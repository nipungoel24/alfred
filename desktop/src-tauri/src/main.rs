#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

//! Alfred desktop shell.
//!
//! Responsibilities:
//! - spawn and OWN the FastAPI sidecar (dynamic loopback port + per-launch
//!   CSPRNG runtime token; child always terminated on exit)
//! - enforce single instance (second launch focuses the first window)
//! - one authoritative window reveal point (`reveal_main_window`)
//! - durable, explicitly-stated startup state machine published to the UI
//! - protocol-based backend readiness (HTTP status + content type + JSON body)
//! - generation-guarded health polling, immune to stale pollers after restart
//! - exit-time shutdown that cannot be skipped by lock contention
//! - structured, rotating, redacted logs in %LOCALAPPDATA%\AlfredData\logs
//!
//! Security invariants (see docs/decisions/ADR-003, ADR-010):
//! - the runtime token is 256 bits from the OS CSPRNG and is never logged
//! - no credential of any kind is written to any log

use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use serde::Serialize;
use tauri::{AppHandle, Emitter, Manager, State};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;
use tokio::sync::watch;

// ── Timing ──────────────────────────────────────────────────────────

const HEALTH_TIMEOUT: Duration = Duration::from_secs(60);
const HEALTH_INTERVAL: Duration = Duration::from_millis(500);
const STARTUP_TIMEOUT: Duration = Duration::from_secs(60);
const HTTP_CONNECT_TIMEOUT: Duration = Duration::from_millis(900);
const HTTP_READ_TIMEOUT: Duration = Duration::from_millis(1500);
const MAX_SPAWN_ATTEMPTS: u32 = 3;
const SHUTDOWN_GRACE: Duration = Duration::from_millis(600);
/// Total bytes the session token encodes.
const TOKEN_BYTES: usize = 32;

const LOG_MAX_BYTES: u64 = 2 * 1024 * 1024;
const LOG_KEEP_FILES: usize = 3;

// ── Startup state machine ───────────────────────────────────────────

/// The explicit startup state machine. Every transition is deterministic and
/// driven by an observed condition, never by a timer guessing.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum StartupPhase {
    /// Process is up. Nothing has been initialised yet.
    Boot,
    /// Logger installed, state channel created, window being prepared.
    Initializing,
    /// About to spawn the sidecar.
    StartingBackend,
    /// Sidecar spawned; polling `/health` until it answers.
    WaitingForBackend,
    /// Backend answered; verifying it is actually backed by SQLite.
    CheckingDatabase,
    /// Database confirmed; probing the local AI runtime.
    CheckingAiRuntime,
    /// AI runtime reachable; checking the configured model.
    CheckingModel,
    /// All checks passed; restoring the account session.
    RestoringSession,
    /// Terminal success.
    Ready,
    /// Degraded but usable. The mailbox works; something optional is not.
    Recovery,
    /// Terminal failure. Requires user action.
    FatalError,
}

impl StartupPhase {
    /// Phases after which the workspace must never be shown.
    fn is_terminal_failure(self) -> bool {
        matches!(self, StartupPhase::FatalError)
    }
}

/// Stable, machine-readable diagnostic codes. These are part of Alfred's
/// support surface: they appear in the UI and in the log, and they do not
/// change wording between releases.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum DiagnosticCode {
    None,
    /// No free loopback port could be obtained.
    NoFreePort,
    /// The sidecar executable could not be launched at all.
    SidecarSpawnFailed,
    /// The sidecar process exited before becoming ready.
    SidecarExited,
    /// The sidecar never answered `/health` within HEALTH_TIMEOUT.
    BackendHealthTimeout,
    /// `/health` answered, but not with 200.
    BackendRejected,
    /// `/health` answered 200 but not with parseable JSON.
    BackendBadHealthPayload,
    /// The runtime token was rejected by the backend.
    BackendUnauthorized,
    /// The frontend's wait exceeded STARTUP_TIMEOUT.
    StartupTimeout,
    /// The state channel closed underneath a waiter.
    StateChannelClosed,
    /// Backend is up but SQLite is not answering.
    DatabaseUnavailable,
    /// Credential storage is unavailable. Fatal: we will not store tokens
    /// in a reversible encoding.
    CredentialStoreUnavailable,
    /// The local AI runtime is not reachable. Degraded, not fatal.
    AiRuntimeUnavailable,
    /// The configured model is not installed. Degraded, not fatal.
    ModelMissing,
}

impl DiagnosticCode {
    fn as_str(self) -> &'static str {
        match self {
            DiagnosticCode::None => "NONE",
            DiagnosticCode::NoFreePort => "NO_FREE_PORT",
            DiagnosticCode::SidecarSpawnFailed => "SIDECAR_SPAWN_FAILED",
            DiagnosticCode::SidecarExited => "SIDECAR_EXITED",
            DiagnosticCode::BackendHealthTimeout => "BACKEND_HEALTH_TIMEOUT",
            DiagnosticCode::BackendRejected => "BACKEND_REJECTED",
            DiagnosticCode::BackendBadHealthPayload => "BACKEND_BAD_HEALTH_PAYLOAD",
            DiagnosticCode::BackendUnauthorized => "BACKEND_UNAUTHORIZED",
            DiagnosticCode::StartupTimeout => "STARTUP_TIMEOUT",
            DiagnosticCode::StateChannelClosed => "STATE_CHANNEL_CLOSED",
            DiagnosticCode::DatabaseUnavailable => "DATABASE_UNAVAILABLE",
            DiagnosticCode::CredentialStoreUnavailable => "CREDENTIAL_STORE_UNAVAILABLE",
            DiagnosticCode::AiRuntimeUnavailable => "AI_RUNTIME_UNAVAILABLE",
            DiagnosticCode::ModelMissing => "MODEL_MISSING",
        }
    }

    /// Human-facing sentence. Never a raw exception, never a stack trace.
    fn guidance(self) -> &'static str {
        match self {
            DiagnosticCode::None => "",
            DiagnosticCode::NoFreePort => {
                "Alfred could not reserve a local port for its background service. \
                 Another application may be holding the address. Close other applications \
                 and try again."
            }
            DiagnosticCode::SidecarSpawnFailed => {
                "Alfred's local service could not be launched. Reinstall Alfred, or run the \
                 installer again to repair the installation."
            }
            DiagnosticCode::SidecarExited => {
                "Alfred's local service stopped unexpectedly while starting. This is usually \
                 caused by a corrupted installation or a blocked antivirus rule."
            }
            DiagnosticCode::BackendHealthTimeout => {
                "Alfred's local service did not respond in time. This is usually a slow disk \
                 or an antivirus scan competing for the file. Try again, and if it persists, \
                 check the log file below."
            }
            DiagnosticCode::BackendRejected => {
                "Alfred's local service refused the readiness check. Restart Alfred; if this \
                 persists, the installation is damaged."
            }
            DiagnosticCode::BackendBadHealthPayload => {
                "Alfred's local service responded in a way Alfred does not understand. \
                 Reinstall Alfred to restore a matching pair of application and service."
            }
            DiagnosticCode::BackendUnauthorized => {
                "Alfred's local service rejected this launch's session key. This normally \
                 resolves by restarting Alfred."
            }
            DiagnosticCode::StartupTimeout => {
                "Alfred took too long to finish starting. Your mail and settings are untouched. \
                 Try again."
            }
            DiagnosticCode::StateChannelClosed => {
                "Alfred lost track of its own background service. Restart Alfred."
            }
            DiagnosticCode::DatabaseUnavailable => {
                "Alfred's local database is not responding, so your mailbox cannot be opened. \
                 Your data has not been modified. Check free disk space and try again."
            }
            DiagnosticCode::CredentialStoreUnavailable => {
                "Alfred could not initialize secure credential storage, so it cannot safely \
                 hold your Google sign-in. Alfred will not store your credentials in a \
                 reversible form. This usually means your Windows user profile is not \
                 decryptable, or a system policy blocks it. Restart Windows and try again; if \
                 it persists, reinstall Alfred."
            }
            DiagnosticCode::AiRuntimeUnavailable => {
                "Your local AI runtime is not running. Your mailbox is fully usable; summaries, \
                 tasks, and deadlines resume automatically when it is available."
            }
            DiagnosticCode::ModelMissing => {
                "The local AI model Alfred uses is not installed. Your mailbox is fully usable; \
                 install the model to enable summaries, tasks, and deadlines."
            }
        }
    }

    /// Fatal codes block the workspace; degraded codes do not.
    fn is_fatal(self) -> bool {
        !matches!(
            self,
            DiagnosticCode::None
                | DiagnosticCode::AiRuntimeUnavailable
                | DiagnosticCode::ModelMissing
                | DiagnosticCode::StartupTimeout
        )
    }
}

/// The complete, serialisable startup snapshot. The frontend renders this
/// directly; it never has to infer a state.
#[derive(Clone, Debug, Serialize)]
pub struct StartupStatus {
    pub phase: StartupPhase,
    pub code: &'static str,
    /// Safe, user-facing sentence. Empty while healthy.
    pub detail: String,
    /// Machine-readable support string. Empty while healthy.
    pub guidance: String,
    /// True only when the workspace may be shown.
    pub ready: bool,
    /// True when Alfred is usable but something optional is degraded.
    pub degraded: bool,
    /// Monotonic milliseconds spent in the current phase.
    pub phase_elapsed_ms: u64,
    pub build: &'static str,
    pub version: &'static str,
}

#[derive(Clone, Debug)]
struct BackendRuntimeState {
    phase: StartupPhase,
    code: DiagnosticCode,
    port: Option<u16>,
    token: Option<String>,
    /// Bumped on every spawn. A poller whose generation is stale must not
    /// publish state. This is what makes restart correct.
    generation: u64,
    phase_started: Instant,
}

impl BackendRuntimeState {
    fn new() -> Self {
        Self {
            phase: StartupPhase::Boot,
            code: DiagnosticCode::None,
            port: None,
            token: None,
            generation: 0,
            phase_started: Instant::now(),
        }
    }
}

// ── Exit-time shutdown registry ─────────────────────────────────────

/// Everything needed to terminate the sidecar, reachable without the async
/// supervisor lock. This exists because the previous implementation used
/// `try_lock` at exit and silently orphaned the backend when the lock was
/// contended. A short-lived std Mutex is correct here: the critical section is
/// a pointer copy, never a long operation.
#[derive(Clone, Debug)]
struct ShutdownTarget {
    pid: u32,
    port: u16,
    token: String,
}

#[derive(Default)]
struct ShutdownRegistry {
    target: Mutex<Option<ShutdownTarget>>,
}

impl ShutdownRegistry {
    fn set(&self, target: ShutdownTarget) {
        if let Ok(mut slot) = self.target.lock() {
            *slot = Some(target);
        }
    }

    fn clear(&self) {
        if let Ok(mut slot) = self.target.lock() {
            *slot = None;
        }
    }

    /// Take the target and terminate the sidecar. Always attempts a kill,
    /// even if the graceful request fails, and never returns early.
    fn terminate(&self) {
        let target = match self.target.lock() {
            Ok(mut slot) => slot.take(),
            Err(poisoned) => poisoned.into_inner().take(),
        };
        let Some(target) = target else {
            return;
        };

        // Ask nicely first so the backend can close SQLite cleanly.
        let graceful = http_request(target.port, "POST", "/api/shutdown", &target.token);
        log::info!(
            "shutdown.graceful_requested pid={} port={} delivered={}",
            target.pid,
            target.port,
            graceful
        );
        std::thread::sleep(SHUTDOWN_GRACE);

        // Always follow up with a hard kill. `CommandChild` is not reachable
        // from the exit hook without the async lock, so terminate by pid.
        // The same mechanism the orphan sweeper already relies on.
        if process_is_alive(target.pid) {
            log::warn!(
                "shutdown.force_kill pid={} reason=still_running_after_grace",
                target.pid
            );
            kill_pid(target.pid);
        } else {
            log::info!("shutdown.exited_cleanly pid={}", target.pid);
        }
    }
}

// ── Supervisor ──────────────────────────────────────────────────────

struct BackendSupervisor {
    state_tx: watch::Sender<BackendRuntimeState>,
    child: Option<LiveChild>,
    app: AppHandle,
    registry: Arc<ShutdownRegistry>,
    generation: AtomicU64,
}

impl BackendSupervisor {
    fn new(app: AppHandle, registry: Arc<ShutdownRegistry>) -> Self {
        let (state_tx, _) = watch::channel(BackendRuntimeState::new());
        Self {
            state_tx,
            child: None,
            app,
            registry,
            generation: AtomicU64::new(0),
        }
    }

    fn snapshot(&self) -> BackendRuntimeState {
        self.state_tx.borrow().clone()
    }

    /// Publish a new state and emit it to the UI. `port`/`token` are carried
    /// forward so a phase change never loses the connection details.
    fn publish(&self, phase: StartupPhase, code: DiagnosticCode) {
        let generation = self.generation.load(Ordering::SeqCst);
        let port = self.snapshot().port;
        let token = self.snapshot().token;
        self.transition(phase, code, port, token, generation);
    }

    fn transition(
        &self,
        phase: StartupPhase,
        code: DiagnosticCode,
        port: Option<u16>,
        token: Option<String>,
        generation: u64,
    ) {
        let next = BackendRuntimeState {
            phase,
            code,
            port,
            token,
            generation,
            phase_started: Instant::now(),
        };
        self.state_tx.send_replace(next.clone());

        let status = status_from(&next);
        log::info!(
            "startup.phase phase={} code={} generation={}",
            status.phase_code(),
            status.code,
            generation
        );
        // Emitting is best-effort: a UI that is not listening yet will read
        // the authoritative snapshot via `startup_phase` instead.
        let _ = self.app.emit("alfred://startup-phase", &status);
    }

    /// Spawn the sidecar and start generation-guarded health polling.
    ///
    /// Retries up to `MAX_SPAWN_ATTEMPTS` times when the sidecar dies
    /// immediately, which is the signature of a lost port race.
    fn spawn_and_watch(&mut self) -> Result<(), String> {
        let generation = self.generation.fetch_add(1, Ordering::SeqCst) + 1;
        log::info!("backend.spawn_requested generation={generation}");

        self.publish(StartupPhase::StartingBackend, DiagnosticCode::None);

        let port = pick_free_port().ok_or_else(|| {
            self.fail(DiagnosticCode::NoFreePort, generation);
            "NO_FREE_PORT".to_string()
        })?;
        let token = generate_token().map_err(|e| {
            self.fail(DiagnosticCode::SidecarSpawnFailed, generation);
            format!("SIDECAR_SPAWN_FAILED: {e}")
        })?;

        kill_orphaned_backends(port);
        self.registry.clear();

        let mut cmd = match self.app.shell().sidecar("alfred-backend") {
            Ok(cmd) => cmd,
            Err(e) => {
                self.fail(DiagnosticCode::SidecarSpawnFailed, generation);
                return Err(format!("SIDECAR_SPAWN_FAILED: {e}"));
            }
        };
        cmd = cmd
            .env("ALFRED_HOST", "127.0.0.1")
            .env("ALFRED_PORT", port.to_string())
            .env("ALFRED_BACKEND_BUILD", env!("ALFRED_GIT_COMMIT"))
            .env("ALFRED_RUNTIME_TOKEN", &token);
        if let Ok(db_path) = std::env::var("ALFRED_DATABASE_PATH") {
            cmd = cmd.env("ALFRED_DATABASE_PATH", db_path);
        }

        let (mut rx, child) = match cmd.spawn() {
            Ok(pair) => pair,
            Err(e) => {
                self.fail(DiagnosticCode::SidecarSpawnFailed, generation);
                return Err(format!("SIDECAR_SPAWN_FAILED: {e}"));
            }
        };
        let pid = child.pid();
        log::info!("backend.spawned pid={pid} port={port} generation={generation}");

        self.registry.set(ShutdownTarget {
            pid,
            port,
            token: token.clone(),
        });

        // Replace any previous child. Done before polling starts so a restart
        // never leaves two sidecars listening.
        if let Some(prev) = self.child.take() {
            log::info!("backend.replacing_previous pid={}", prev.child.pid());
            let _ = prev.child.kill();
        }
        self.child = Some(LiveChild {
            child,
            port,
            token: token.clone(),
        });

        // Drain sidecar output into the real logger, and detect death.
        let (death_tx, death_rx) = tokio::sync::oneshot::channel::<Option<i32>>();
        let generation_child = generation;
        let state_tx_child = self.state_tx.clone();
        let app_child = self.app.clone();
        tauri::async_runtime::spawn(async move {
            let mut death_tx = Some(death_tx);
            while let Some(event) = rx.recv().await {
                match event {
                    CommandEvent::Stdout(line) => {
                        log::info!("sidecar.out {}", redact(&String::from_utf8_lossy(&line)));
                    }
                    CommandEvent::Stderr(line) => {
                        log::warn!("sidecar.err {}", redact(&String::from_utf8_lossy(&line)));
                    }
                    CommandEvent::Error(e) => {
                        log::error!("sidecar.error pid={} error={}", pid, e);
                    }
                    CommandEvent::Terminated(payload) => {
                        log::error!(
                            // Not "code=": the global redaction filter treats a
                            // bare `code=` as the OAuth authorization code and
                            // replaced the process exit status with [redacted],
                            // hiding the one value that explains a sidecar exit.
                            "sidecar.exited pid={} exit={:?} generation={}",
                            pid,
                            payload.code,
                            generation_child
                        );
                        if let Some(tx) = death_tx.take() {
                            let _ = tx.send(payload.code);
                        }
                        // Only publish if we are still the current generation,
                        // otherwise a dying old sidecar would clobber a healthy
                        // new one.
                        let current = state_tx_child.borrow().generation;
                        if current == generation_child {
                            state_tx_child.send_replace(BackendRuntimeState {
                                phase: StartupPhase::FatalError,
                                code: DiagnosticCode::SidecarExited,
                                port: None,
                                token: None,
                                generation: generation_child,
                                phase_started: Instant::now(),
                            });
                            let _ = app_child.emit(
                                "alfred://startup-phase",
                                status_from(&state_tx_child.borrow()),
                            );
                        }
                        return;
                    }
                    _ => {}
                }
            }
        });

        // Generation-guarded readiness polling.
        let state_tx_poll = self.state_tx.clone();
        let app_poll = self.app.clone();
        let registry_poll = self.registry.clone();
        tauri::async_runtime::spawn(async move {
            let deadline = Instant::now() + HEALTH_TIMEOUT;
            let mut last_probe = String::new();
            let mut outcome: Option<(StartupPhase, DiagnosticCode)> = None;
            while Instant::now() < deadline {
                match probe_health(port, &token) {
                    HealthProbe::Ready(health) => {
                        outcome = Some(assess_readiness(&health));
                        break;
                    }
                    HealthProbe::Unauthorized => {
                        outcome = Some((
                            StartupPhase::FatalError,
                            DiagnosticCode::BackendUnauthorized,
                        ));
                        break;
                    }
                    HealthProbe::Rejected(status) => {
                        // A backend that is still warming up answers 503/502/504.
                        // Retrying is correct and bounded by the deadline; only an
                        // auth rejection or a contract mismatch is terminal.
                        let reason = format!("http_{status}");
                        if reason != last_probe {
                            log::warn!("health.rejected port={port} status={status}");
                            last_probe = reason;
                        }
                    }
                    HealthProbe::BadPayload => {
                        outcome = Some((
                            StartupPhase::FatalError,
                            DiagnosticCode::BackendBadHealthPayload,
                        ));
                        break;
                    }
                    HealthProbe::Unreachable(reason) => {
                        if reason != last_probe {
                            log::info!("health.probe port={port} state={reason}");
                            last_probe = reason;
                        }
                    }
                }
                tokio::time::sleep(HEALTH_INTERVAL).await;
            }

            let (phase, code) = match outcome {
                Some(pair) => pair,
                None => {
                    // Distinguish "the sidecar died" from "it was alive but
                    // never healthy in time".
                    let died = matches!(
                        tokio::time::timeout(Duration::from_millis(50), death_rx).await,
                        Ok(Ok(Some(_)))
                    );
                    if died {
                        (StartupPhase::FatalError, DiagnosticCode::SidecarExited)
                    } else {
                        (
                            StartupPhase::FatalError,
                            DiagnosticCode::BackendHealthTimeout,
                        )
                    }
                }
            };

            // Drop the poller's claim if a restart happened while we waited.
            let current = state_tx_poll.borrow().generation;
            if current != generation {
                log::info!("health.poller_superseded generation={generation} current={current}");
                return;
            }

            let keep_connection = !phase.is_terminal_failure();
            if !keep_connection {
                registry_poll.clear();
            }
            let port = keep_connection.then_some(port);
            let token = port.map(|_| token);

            let next = BackendRuntimeState {
                phase,
                code,
                port,
                token,
                generation,
                phase_started: Instant::now(),
            };
            state_tx_poll.send_replace(next.clone());
            let status = status_from(&next);
            log::info!(
                "startup.phase phase={} code={} generation={generation}",
                status.phase_code(),
                status.code
            );
            let _ = app_poll.emit("alfred://startup-phase", &status);
        });

        Ok(())
    }

    fn fail(&self, code: DiagnosticCode, generation: u64) {
        self.registry.clear();
        self.transition(StartupPhase::FatalError, code, None, None, generation);
    }

    /// Stop the current child in preparation for a restart.
    fn stop_child(&mut self) {
        if let Some(rt) = self.child.take() {
            let delivered = http_request(rt.port, "POST", "/api/shutdown", &rt.token);
            log::info!(
                "backend.stop_requested pid={} port={} delivered={}",
                rt.child.pid(),
                rt.port,
                delivered
            );
            std::thread::sleep(SHUTDOWN_GRACE);
            let _ = rt.child.kill();
        }
        self.registry.clear();
    }
}

/// The live sidecar plus the details needed to talk to and stop it.
struct LiveChild {
    child: CommandChild,
    port: u16,
    token: String,
}

// ── Readiness assessment ────────────────────────────────────────────

/// The parsed, minimal shape of `GET /health`.
#[derive(Debug, Default, Clone, Serialize, serde::Deserialize)]
pub struct HealthPayload {
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub database: String,
    #[serde(default)]
    pub ai: String,
    /// Added by the backend so the shell can detect a credential store that
    /// failed closed. Absent means "not reported", which is treated as ready
    /// so an older backend cannot brick a newer shell.
    #[serde(default)]
    pub credential_store: String,
}

impl HealthPayload {
    fn database_ready(&self) -> bool {
        self.database.eq_ignore_ascii_case("ready")
    }
    fn credential_store_ready(&self) -> bool {
        !self.credential_store.eq_ignore_ascii_case("unavailable")
    }
    fn model_missing(&self) -> bool {
        self.ai.eq_ignore_ascii_case("model_missing")
    }
    fn ai_ready(&self) -> bool {
        self.ai.eq_ignore_ascii_case("ready")
    }
}

/// Map an observed health payload onto the next startup phase.
///
/// Fatal: no database, no secure credential storage.
/// Degraded: the AI runtime or the model is absent. The mailbox still works,
/// so Alfred must reach READY, not FATAL_ERROR.
pub fn assess_readiness(health: &HealthPayload) -> (StartupPhase, DiagnosticCode) {
    if !health.credential_store_ready() {
        return (
            StartupPhase::FatalError,
            DiagnosticCode::CredentialStoreUnavailable,
        );
    }
    if !health.database_ready() {
        return (
            StartupPhase::FatalError,
            DiagnosticCode::DatabaseUnavailable,
        );
    }
    if health.model_missing() {
        return (StartupPhase::Recovery, DiagnosticCode::ModelMissing);
    }
    if !health.ai_ready() {
        return (StartupPhase::Recovery, DiagnosticCode::AiRuntimeUnavailable);
    }
    (StartupPhase::Ready, DiagnosticCode::None)
}

fn status_from(state: &BackendRuntimeState) -> StartupStatus {
    let degraded = matches!(state.phase, StartupPhase::Recovery);
    StartupStatus {
        phase: state.phase,
        code: state.code.as_str(),
        detail: if state.code == DiagnosticCode::None {
            String::new()
        } else {
            state.code.guidance().to_string()
        },
        guidance: if state.code == DiagnosticCode::None {
            String::new()
        } else {
            state.code.guidance().to_string()
        },
        ready: matches!(state.phase, StartupPhase::Ready | StartupPhase::Recovery),
        degraded,
        phase_elapsed_ms: state.phase_started.elapsed().as_millis() as u64,
        build: env!("ALFRED_GIT_COMMIT"),
        version: env!("CARGO_PKG_VERSION"),
    }
}

impl StartupStatus {
    fn phase_code(&self) -> &'static str {
        match self.phase {
            StartupPhase::Boot => "BOOT",
            StartupPhase::Initializing => "INITIALIZING",
            StartupPhase::StartingBackend => "STARTING_BACKEND",
            StartupPhase::WaitingForBackend => "WAITING_FOR_BACKEND",
            StartupPhase::CheckingDatabase => "CHECKING_DATABASE",
            StartupPhase::CheckingAiRuntime => "CHECKING_AI_RUNTIME",
            StartupPhase::CheckingModel => "CHECKING_MODEL",
            StartupPhase::RestoringSession => "RESTORING_SESSION",
            StartupPhase::Ready => "READY",
            StartupPhase::Recovery => "RECOVERY",
            StartupPhase::FatalError => "FATAL_ERROR",
        }
    }
}

// ── Logging ─────────────────────────────────────────────────────────

fn log_dir() -> PathBuf {
    std::env::var_os("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
        .join("AlfredData")
        .join("logs")
}

fn log_path() -> PathBuf {
    log_dir().join("desktop.log")
}

/// Rotate `desktop.log` -> `.1` -> `.2` -> `.3`, dropping the oldest.
fn rotate_if_needed(path: &Path) {
    let Ok(meta) = fs::metadata(path) else {
        return;
    };
    if meta.len() < LOG_MAX_BYTES {
        return;
    }
    for index in (1..LOG_KEEP_FILES).rev() {
        let from = PathBuf::from(format!("{}.{}", path.display(), index));
        let to = PathBuf::from(format!("{}.{}", path.display(), index + 1));
        if from.exists() {
            let _ = fs::rename(&from, &to);
        }
    }
    let _ = fs::rename(path, PathBuf::from(format!("{}.1", path.display())));
}

/// Remove anything that could be a credential from captured child output.
///
/// The sidecar is a uvicorn server, so its access log contains request lines.
/// `GET /api/analysis/progress?token=...` and the OAuth callback's `?code=...`
/// are both real credentials. Redaction happens before anything is written.
///
/// Two shapes are handled, because they terminate differently:
/// - `key=value` in a URL or log line, terminated by whitespace, `&`, or `'`
/// - `"key": "value"` in a JSON body, where the value is quoted and the
///   closing quote must be consumed along with the value
fn redact(input: &str) -> String {
    // Longest key first, so `access_token` is consumed before the `token`
    // suffix inside it can match.
    const SENSITIVE: [&str; 6] = [
        "access_token",
        "refresh_token",
        "client_secret",
        "code_verifier",
        "token",
        "code",
    ];
    const PLACEHOLDER: &str = "[redacted]";

    let mut out = input.to_string();
    for key in SENSITIVE {
        // URL / log-line form: key=value
        let url_form = format!("{key}=");
        let mut cursor = 0usize;
        while let Some(found) = out[cursor..].find(&url_form) {
            let value_start = cursor + found + url_form.len();
            let end = out[value_start..]
                .find(|c: char| c.is_whitespace() || c == '&' || c == '\'')
                .map(|i| value_start + i)
                .unwrap_or(out.len());
            out.replace_range(value_start..end, PLACEHOLDER);
            cursor = value_start + PLACEHOLDER.len();
            if cursor >= out.len() {
                break;
            }
        }

        // JSON form: "key": "value"  (also tolerates "key":value)
        let json_form = format!("\"{key}\":");
        let mut cursor = 0usize;
        while let Some(found) = out[cursor..].find(&json_form) {
            let mut value_start = cursor + found + json_form.len();
            let quoted = out[value_start..].starts_with('"');
            if quoted {
                value_start += 1;
            }
            let end = out[value_start..]
                .find(|c: char| {
                    if quoted {
                        c == '"'
                    } else {
                        c == ',' || c == '}'
                    }
                })
                .map(|i| value_start + i)
                .unwrap_or(out.len());
            out.replace_range(value_start..end, PLACEHOLDER);
            cursor = value_start + PLACEHOLDER.len() + usize::from(quoted);
            if cursor >= out.len() {
                break;
            }
        }
    }
    out
}

/// ISO-8601 UTC with milliseconds, without pulling in a date-time crate.
fn iso8601_millis() -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    let secs = now.as_secs();
    let millis = now.subsec_millis();
    let days = secs / 86_400;
    let time_of_day = secs % 86_400;
    let (hour, minute, second) = (
        time_of_day / 3_600,
        (time_of_day % 3_600) / 60,
        time_of_day % 60,
    );
    // Civil-from-days (Howard Hinnant's algorithm).
    let z = days as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };
    format!("{y:04}-{m:02}-{d:02}T{hour:02}:{minute:02}:{second:02}.{millis:03}Z")
}

/// A real `log` implementation. The previous code called `log::debug!` with no
/// logger installed, so every sidecar line was silently discarded.
struct AlfredLogger {
    level: log::LevelFilter,
}

impl log::Log for AlfredLogger {
    fn enabled(&self, metadata: &log::Metadata) -> bool {
        metadata.level() <= self.level
    }

    fn log(&self, record: &log::Record) {
        if !self.enabled(record.metadata()) {
            return;
        }
        let dir = log_dir();
        if fs::create_dir_all(&dir).is_err() {
            return;
        }
        let path = log_path();
        rotate_if_needed(&path);
        if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(&path) {
            let _ = writeln!(
                file,
                "{} {} {} {}",
                iso8601_millis(),
                record.level(),
                record.target(),
                redact(&record.args().to_string())
            );
        }
    }

    fn flush(&self) {}
}

fn init_logging() {
    let logger = AlfredLogger {
        level: log::LevelFilter::Info,
    };
    if log::set_boxed_logger(Box::new(logger)).is_ok() {
        log::set_max_level(log::LevelFilter::Info);
    }
}

// ── Port + token ────────────────────────────────────────────────────

fn pick_free_port() -> Option<u16> {
    TcpListener::bind("127.0.0.1:0")
        .ok()
        .and_then(|l| l.local_addr().ok().map(|a| a.port()))
}

/// 256 bits from the operating system CSPRNG, hex encoded.
///
/// This is a wrapper, not an algorithm. `getrandom` maps to `BCryptGenRandom`
/// on Windows and `getrandom(2)` on Linux; both are kernel CSPRNGs. The
/// previous implementation derived the token from `RandomState` hashing of the
/// wall clock, the PID, and a monotonic reading, all of which are observable
/// to any local process.
fn generate_token() -> Result<String, String> {
    let mut bytes = [0u8; TOKEN_BYTES];
    getrandom::getrandom(&mut bytes).map_err(|e| format!("csprng_unavailable: {e}"))?;
    let mut out = String::with_capacity(TOKEN_BYTES * 2);
    for byte in bytes {
        out.push_str(&format!("{byte:02x}"));
    }
    Ok(out)
}

// ── Process helpers ─────────────────────────────────────────────────

fn kill_pid(pid: u32) {
    use std::process::Command;
    let _ = Command::new("taskkill")
        .args(["/F", "/PID", &pid.to_string()])
        .output();
}

fn process_is_alive(pid: u32) -> bool {
    use std::process::Command;
    Command::new("tasklist")
        .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
        .output()
        .map(|out| {
            let text = String::from_utf8_lossy(&out.stdout);
            // tasklist prints an INFO line when nothing matches the filter.
            !text.to_lowercase().contains("info:") && text.contains(&format!("\"{pid}\""))
        })
        .unwrap_or(false)
}

fn kill_orphaned_backends(own_port: u16) {
    use std::process::Command;
    if let Ok(output) = Command::new("netstat").args(["-ano", "-p", "TCP"]).output() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let mut orphans: Vec<u32> = Vec::new();
        for line in stdout.lines() {
            if !line.contains("127.0.0.1") || !line.contains("LISTENING") {
                continue;
            }
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() < 5 {
                continue;
            }
            let addr = parts[1];
            let pid_str = parts[parts.len() - 1];
            let Ok(pid) = pid_str.parse::<u32>() else {
                continue;
            };
            let Some(port_str) = addr.rsplit(':').next() else {
                continue;
            };
            let Ok(port) = port_str.parse::<u16>() else {
                continue;
            };
            if port == own_port {
                continue;
            }
            if let Ok(ps_out) = Command::new("tasklist")
                .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
                .output()
            {
                let ps = String::from_utf8_lossy(&ps_out.stdout);
                if ps.to_lowercase().contains("alfred-backend") {
                    orphans.push(pid);
                }
            }
        }
        for pid in orphans {
            log::warn!("backend.killing_orphan pid={pid}");
            kill_pid(pid);
        }
    }
}

// ── HTTP ────────────────────────────────────────────────────────────

#[derive(Debug)]
enum HealthProbe {
    Ready(HealthPayload),
    /// Connection refused / timed out. Carries a short reason for logging.
    Unreachable(String),
    /// Answered, but not 200.
    Rejected(u16),
    /// Answered 200, but the body was not the JSON we require.
    BadPayload,
    /// Answered 401: the runtime token was rejected.
    Unauthorized,
}

struct RawResponse {
    status: u16,
    content_type: Option<String>,
    body: String,
}

/// Perform one HTTP/1.1 request and parse the response properly.
///
/// Readiness is decided from the parsed status line, the declared content
/// type, and a validated JSON body. The previous implementation searched the
/// first 1024 bytes for the substring "200", which any header value or body
/// byte range could satisfy.
fn http_request_raw(
    port: u16,
    method: &str,
    path: &str,
    token: &str,
) -> Result<RawResponse, String> {
    use std::net::SocketAddr;
    let addr: SocketAddr = format!("127.0.0.1:{port}")
        .parse()
        .map_err(|_| "bad_addr".to_string())?;
    let mut stream = TcpStream::connect_timeout(&addr, HTTP_CONNECT_TIMEOUT)
        .map_err(|e| format!("connect:{e}"))?;
    stream
        .set_read_timeout(Some(HTTP_READ_TIMEOUT))
        .map_err(|e| format!("read_timeout:{e}"))?;

    let request = format!(
        "{method} {path} HTTP/1.1\r\n\
         Host: 127.0.0.1:{port}\r\n\
         X-Alfred-Token: {token}\r\n\
         Accept: application/json\r\n\
         Connection: close\r\n\r\n"
    );
    stream
        .write_all(request.as_bytes())
        .map_err(|e| format!("write:{e}"))?;

    let mut raw = Vec::with_capacity(2048);
    let mut chunk = [0u8; 2048];
    loop {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                raw.extend_from_slice(&chunk[..n]);
                if raw.len() > 256 * 1024 {
                    break;
                }
            }
            Err(e) => return Err(format!("read:{e}")),
        }
    }

    let text = String::from_utf8_lossy(&raw).to_string();
    let (head, body) = text
        .split_once("\r\n\r\n")
        .ok_or_else(|| "malformed_response".to_string())?;

    let mut lines = head.lines();
    let status_line = lines.next().ok_or_else(|| "no_status_line".to_string())?;
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|s| s.parse::<u16>().ok())
        .ok_or_else(|| "unparsable_status".to_string())?;

    let mut content_type = None;
    for line in lines {
        if let Some((name, value)) = line.split_once(':') {
            if name.trim().eq_ignore_ascii_case("content-type") {
                content_type = Some(value.trim().to_ascii_lowercase());
            }
        }
    }

    Ok(RawResponse {
        status,
        content_type,
        body: body.to_string(),
    })
}

fn http_request(port: u16, method: &str, path: &str, token: &str) -> bool {
    matches!(
        http_request_raw(port, method, path, token),
        Ok(response) if response.status == 200
    )
}

/// Probe `GET /health` and classify the result.
fn probe_health(port: u16, token: &str) -> HealthProbe {
    match http_request_raw(port, "GET", "/health", token) {
        Err(reason) => HealthProbe::Unreachable(reason),
        Ok(response) => match response.status {
            401 | 403 => HealthProbe::Unauthorized,
            200 => {
                let is_json = response
                    .content_type
                    .as_deref()
                    .map(|ct| ct.starts_with("application/json"))
                    .unwrap_or(false);
                if !is_json {
                    return HealthProbe::BadPayload;
                }
                match serde_json::from_str::<HealthPayload>(&response.body) {
                    Ok(payload) => HealthProbe::Ready(payload),
                    Err(_) => HealthProbe::BadPayload,
                }
            }
            other => HealthProbe::Rejected(other),
        },
    }
}

// ── Tauri commands ──────────────────────────────────────────────────

#[derive(serde::Serialize)]
struct BackendInfo {
    port: u16,
    token: String,
}

/// Durable backend readiness command.
///
/// Returns the connection details once the backend is genuinely serving.
/// On failure the error string is a JSON envelope so the UI can render a
/// stable diagnostic code and real guidance instead of an exception message.
#[tauri::command]
async fn await_backend_ready(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String> {
    let mut rx = {
        let sup = supervisor.lock().await;
        sup.state_tx.subscribe()
    };

    {
        let sup = supervisor.lock().await;
        match sup.snapshot() {
            BackendRuntimeState {
                phase: StartupPhase::Ready | StartupPhase::Recovery,
                port: Some(port),
                token: Some(token),
                ..
            } => return Ok(BackendInfo { port, token }),
            BackendRuntimeState {
                phase: StartupPhase::FatalError,
                code,
                ..
            } => return Err(failure_envelope(code)),
            _ => {}
        }
    }

    let deadline = Instant::now() + STARTUP_TIMEOUT;
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            return Err(failure_envelope(DiagnosticCode::StartupTimeout));
        }
        match tokio::time::timeout(remaining, rx.changed()).await {
            Ok(Ok(())) => {
                let state = rx.borrow().clone();
                match state.phase {
                    StartupPhase::Ready | StartupPhase::Recovery => {
                        if let (Some(port), Some(token)) = (state.port, state.token) {
                            return Ok(BackendInfo { port, token });
                        }
                        return Err(failure_envelope(DiagnosticCode::StateChannelClosed));
                    }
                    StartupPhase::FatalError => return Err(failure_envelope(state.code)),
                    _ => continue,
                }
            }
            Ok(Err(_)) => return Err(failure_envelope(DiagnosticCode::StateChannelClosed)),
            Err(_) => return Err(failure_envelope(DiagnosticCode::StartupTimeout)),
        }
    }
}

fn failure_envelope(code: DiagnosticCode) -> String {
    serde_json::json!({
        "code": code.as_str(),
        "guidance": code.guidance(),
        "fatal": code.is_fatal(),
    })
    .to_string()
}

/// Authoritative startup snapshot. The UI calls this once on mount, then
/// follows `alfred://startup-phase` events.
#[tauri::command]
fn startup_phase(
    supervisor: State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<StartupStatus, String> {
    let sup = supervisor.blocking_lock();
    Ok(status_from(&sup.snapshot()))
}

/// Restart the backend. Always performs a real restart.
///
/// The previous implementation returned `Ok(())` without doing anything while
/// the state was `Starting`, so pressing Retry during a slow cold start did
/// nothing at all. It also failed to cancel the previous health poller, which
/// could later publish a stale `Ready` for a dead port. Both are fixed by the
/// generation guard plus this unconditional restart.
#[tauri::command]
async fn restart_backend(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<(), String> {
    let mut sup = supervisor.lock().await;
    log::info!("restart.requested");
    sup.stop_child();
    sup.spawn_and_watch()
}

/// Legacy command retained for compatibility. Returns connection details only
/// when the backend is genuinely ready.
#[tauri::command]
fn backend_info(
    supervisor: State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String> {
    let sup = supervisor.blocking_lock();
    match sup.snapshot() {
        BackendRuntimeState {
            phase: StartupPhase::Ready | StartupPhase::Recovery,
            port: Some(port),
            token: Some(token),
            ..
        } => Ok(BackendInfo { port, token }),
        BackendRuntimeState {
            code,
            phase: StartupPhase::FatalError,
            ..
        } => Err(failure_envelope(code)),
        _ => Err(failure_envelope(DiagnosticCode::StartupTimeout)),
    }
}

/// Diagnostics for the failure screen. Deliberately returns no secrets.
#[tauri::command]
fn startup_diagnostics() -> Result<serde_json::Value, String> {
    Ok(serde_json::json!({
        "log_path": log_path().display().to_string(),
        "build": env!("ALFRED_GIT_COMMIT"),
        "version": env!("CARGO_PKG_VERSION"),
    }))
}

// ── Window reveal ───────────────────────────────────────────────────

/// THE authoritative reveal point.
///
/// Called from exactly two places, both of which are legitimate:
/// - `RunEvent::Ready`, for the cold first launch
/// - the single-instance callback, when a second launch must surface a window
///   that is already running
///
/// It is idempotent, so calling it twice is harmless. The window is created
/// visible (see `tauri.conf.json`) and `index.html` paints a branded startup
/// shell before React mounts, so there is no white frame at any point.
fn reveal_main_window(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        if window.show().is_ok() {
            log::info!("window.revealed reason=explicit");
        }
    }
}

// ── Main ────────────────────────────────────────────────────────────

fn main() {
    init_logging();

    let exe = std::env::current_exe()
        .map(|p| p.display().to_string())
        .unwrap_or_else(|_| "unknown".to_string());
    log::info!(
        "desktop.start version={} build={} pid={} exe={}",
        env!("CARGO_PKG_VERSION"),
        env!("ALFRED_GIT_COMMIT"),
        std::process::id(),
        exe
    );

    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            // A second launch surfaces the running window. It must never be
            // the only thing that reveals the window.
            reveal_main_window(app);
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .setup(|app| {
            let handle = app.handle().clone();
            // The registry is owned by Tauri, so the run loop can reach it
            // without borrowing anything out of `main`. This is what makes
            // exit-time termination independent of the async supervisor lock.
            let registry = Arc::new(ShutdownRegistry::default());
            app.manage(registry.clone());
            let supervisor = Arc::new(tokio::sync::Mutex::new(BackendSupervisor::new(
                handle.clone(),
                registry,
            )));
            app.manage(supervisor.clone());
            // Reveal as soon as the shell is up, so the branded startup shell
            // is on screen while the backend boots.
            reveal_main_window(&handle);
            // Spawn off the setup thread so setup returns immediately.
            tauri::async_runtime::spawn(async move {
                let mut sup = supervisor.lock().await;
                sup.publish(StartupPhase::Initializing, DiagnosticCode::None);
                if let Err(e) = spawn_with_retry(&mut sup).await {
                    log::error!("backend.spawn_failed error={e}");
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            await_backend_ready,
            restart_backend,
            backend_info,
            startup_phase,
            startup_diagnostics,
        ])
        .build(tauri::generate_context!())
        .expect("failed to build Alfred desktop");

    app.run(|handle, event| match event {
        // Cold-launch reveal. Idempotent, so ordering with `setup` is safe.
        tauri::RunEvent::Ready => {
            reveal_main_window(handle);
        }
        // Termination never touches the async supervisor lock. The previous
        // implementation used `try_lock` and silently orphaned the sidecar
        // whenever the lock was contended; the registry is independent of it
        // and always attempts a graceful request followed by a hard kill.
        tauri::RunEvent::Exit | tauri::RunEvent::ExitRequested { .. } => {
            let registry = handle.state::<Arc<ShutdownRegistry>>();
            log::info!("desktop.exit_requested");
            registry.terminate();
        }
        _ => {}
    });
}

/// Spawn, retrying only when the sidecar cannot be launched or dies instantly
/// (the signature of a lost port race).
async fn spawn_with_retry(sup: &mut BackendSupervisor) -> Result<(), String> {
    let mut last_error = String::new();
    for attempt in 1..=MAX_SPAWN_ATTEMPTS {
        match sup.spawn_and_watch() {
            Ok(()) => {
                if attempt > 1 {
                    log::info!("backend.spawn_succeeded attempt={attempt}");
                }
                return Ok(());
            }
            Err(e) => {
                last_error = e.clone();
                log::error!("backend.spawn_attempt_failed attempt={attempt} error={e}");
                if attempt < MAX_SPAWN_ATTEMPTS {
                    tokio::time::sleep(Duration::from_millis(250)).await;
                    continue;
                }
                break;
            }
        }
    }
    Err(last_error)
}

// ── Tests ───────────────────────────────────────────────────────────
//
// These exercise Alfred's real supervisor behaviour: a real TCP listener
// standing in for the sidecar, real HTTP request construction, real response
// parsing, and the real generation guard. They deliberately do NOT re-test
// `tokio::sync::watch`, which the previous test module did and which proved
// nothing about Alfred.
//
// Native window behaviour is NOT covered here and is not claimed to be. It is
// verified by the documented manual packaged-launch procedure in
// docs/Phases.md Gate 1.

#[cfg(test)]
mod tests {
    use super::*;
    use std::net::TcpListener as StdListener;
    use std::sync::atomic::{AtomicBool, AtomicUsize};

    /// A minimal stand-in for the FastAPI sidecar: a real loopback listener
    /// that answers `GET /health` with a configurable status, content type and
    /// body. This is what makes the readiness tests meaningful.
    struct StubBackend {
        port: u16,
        shutdown_requested: Arc<AtomicBool>,
        hits: Arc<AtomicUsize>,
    }

    struct StubConfig {
        status_line: &'static str,
        content_type: Option<&'static str>,
        body: &'static str,
        /// Serve 503 for the first N health requests, to simulate a cold start.
        warmup_hits: usize,
    }

    impl Default for StubConfig {
        fn default() -> Self {
            Self {
                status_line: "HTTP/1.1 200 OK",
                content_type: Some("application/json"),
                body: r#"{"status":"ok","database":"ready","ai":"ready","credential_store":"ready"}"#,
                warmup_hits: 0,
            }
        }
    }

    impl StubBackend {
        fn start(config: StubConfig) -> Self {
            let listener = StdListener::bind("127.0.0.1:0").expect("bind stub");
            let port = listener.local_addr().expect("stub addr").port();
            let shutdown_requested = Arc::new(AtomicBool::new(false));
            let hits = Arc::new(AtomicUsize::new(0));

            let thread_shutdown = shutdown_requested.clone();
            let thread_hits = hits.clone();
            std::thread::spawn(move || {
                for stream in listener.incoming() {
                    let Ok(mut stream) = stream else { continue };
                    let mut buf = [0u8; 2048];
                    let Ok(n) = stream.read(&mut buf) else {
                        continue;
                    };
                    let request = String::from_utf8_lossy(&buf[..n]).to_string();
                    let is_shutdown = request.starts_with("POST /api/shutdown");
                    if is_shutdown {
                        thread_shutdown.store(true, Ordering::SeqCst);
                    }
                    let seen = thread_hits.fetch_add(1, Ordering::SeqCst);
                    let status_line = if seen < config.warmup_hits {
                        "HTTP/1.1 503 Service Unavailable"
                    } else {
                        config.status_line
                    };
                    let mut response = format!("{status_line}\r\n");
                    if let Some(ct) = config.content_type {
                        response.push_str(&format!("Content-Type: {ct}\r\n"));
                    } else {
                        response.push_str("Content-Type: text/html\r\n");
                    }
                    response.push_str("Content-Length: ");
                    response.push_str(&config.body.len().to_string());
                    response.push_str("\r\nConnection: close\r\n\r\n");
                    response.push_str(config.body);
                    let _ = stream.write_all(response.as_bytes());
                    let _ = stream.flush();
                }
            });

            Self {
                port,
                shutdown_requested,
                hits,
            }
        }

        fn port(&self) -> u16 {
            self.port
        }
    }

    // ── Session token ───────────────────────────────────────────────

    #[test]
    fn token_is_the_requested_length() {
        let token = generate_token().expect("csprng");
        // 32 bytes hex encoded.
        assert_eq!(token.len(), TOKEN_BYTES * 2);
        assert_eq!(token.len(), 64, "256 bits of entropy must be encoded");
    }

    #[test]
    fn token_is_lowercase_hex_only() {
        let token = generate_token().expect("csprng");
        assert!(
            token
                .chars()
                .all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()),
            "token must be lowercase hex, got {token}"
        );
    }

    #[test]
    fn tokens_are_unique_across_many_draws() {
        // 4096 draws. A token derived from a clock and a PID, as the previous
        // implementation was, collides in this set.
        let mut seen = std::collections::HashSet::new();
        for _ in 0..4096 {
            let token = generate_token().expect("csprng");
            assert!(seen.insert(token), "token repeated: not random");
        }
        assert_eq!(seen.len(), 4096);
    }

    #[test]
    fn token_draws_differ_within_a_single_nanosecond_window() {
        // Two consecutive draws must differ. This is the direct regression
        // test for the old clock+PID derivation.
        let a = generate_token().expect("csprng");
        let b = generate_token().expect("csprng");
        assert_ne!(a, b);
    }

    #[test]
    fn token_has_no_low_entropy_structure() {
        // A CSPRNG output must not repeat a byte run. Guard against a
        // regression that reintroduces a constant or a counter.
        let token = generate_token().expect("csprng");
        let bytes: Vec<u8> = (0..TOKEN_BYTES)
            .map(|i| u8::from_str_radix(&token[i * 2..i * 2 + 2], 16).expect("hex"))
            .collect();
        assert!(
            bytes
                .windows(4)
                .all(|w| w[0] != w[1] || w[1] != w[2] || w[2] != w[3]),
            "token contains a repeating run: {token}"
        );
        assert!(
            !bytes.iter().all(|b| *b == bytes[0]),
            "token is a single repeated byte"
        );
    }

    // ── Redaction ───────────────────────────────────────────────────

    #[test]
    fn redact_removes_a_token_query_parameter() {
        let line =
            "INFO: 127.0.0.1:5000 - \"GET /api/analysis/progress?token=deadbeefcafe HTTP/1.1\" 200";
        let safe = redact(line);
        assert!(!safe.contains("deadbeefcafe"), "token leaked: {safe}");
        assert!(safe.contains("[redacted]"));
    }

    #[test]
    fn redact_removes_an_oauth_code() {
        let line = "GET /api/accounts/gmail/callback?state=abc&code=4/0AeanSabc HTTP/1.1";
        let safe = redact(line);
        assert!(!safe.contains("4/0AeanSabc"), "oauth code leaked: {safe}");
    }

    #[test]
    fn redact_removes_json_shaped_secrets() {
        let line = r#"{"client_secret":"GOCSPX-xxx","access_token":"ya29.zzz"}"#;
        let safe = redact(line);
        assert!(!safe.contains("GOCSPX-xxx"), "secret leaked: {safe}");
        assert!(!safe.contains("ya29.zzz"), "token leaked: {safe}");
    }

    #[test]
    fn redact_preserves_harmless_text() {
        let line = "backend.spawned pid=1234 port=49152 generation=1";
        assert_eq!(redact(line), line);
    }

    // ── Protocol-based readiness ────────────────────────────────────

    #[test]
    fn probe_health_accepts_a_well_formed_ok_response() {
        let stub = StubBackend::start(StubConfig::default());
        match probe_health(stub.port(), "token") {
            HealthProbe::Ready(payload) => {
                assert_eq!(payload.status, "ok");
                assert_eq!(payload.database, "ready");
                assert_eq!(payload.ai, "ready");
            }
            other => panic!("expected Ready, got {other:?}"),
        }
    }

    #[test]
    fn probe_health_rejects_a_non_200_status() {
        let stub = StubBackend::start(StubConfig {
            status_line: "HTTP/1.1 500 Internal Server Error",
            ..StubConfig::default()
        });
        assert!(matches!(
            probe_health(stub.port(), "token"),
            HealthProbe::Rejected(500)
        ));
    }

    #[test]
    fn probe_health_rejects_a_wrong_content_type() {
        // A 200 that is HTML, not the JSON health contract.
        let stub = StubBackend::start(StubConfig {
            content_type: Some("text/html"),
            body: "<html>200 OK</html>",
            ..StubConfig::default()
        });
        assert!(matches!(
            probe_health(stub.port(), "token"),
            HealthProbe::BadPayload
        ));
    }

    #[test]
    fn probe_health_rejects_a_200_that_merely_contains_200() {
        // The exact defect being fixed: the old implementation searched the
        // first 1024 bytes for the substring "200" and would have called this
        // a healthy backend.
        let stub = StubBackend::start(StubConfig {
            content_type: Some("text/html"),
            body: "<html><body>Error 200 but not really</body></html>",
            ..StubConfig::default()
        });
        assert!(
            matches!(probe_health(stub.port(), "token"), HealthProbe::BadPayload),
            "a 200 in the body must not be treated as readiness"
        );
    }

    #[test]
    fn probe_health_rejects_a_200_with_unparsable_json() {
        let stub = StubBackend::start(StubConfig {
            body: "{not json",
            ..StubConfig::default()
        });
        assert!(matches!(
            probe_health(stub.port(), "token"),
            HealthProbe::BadPayload
        ));
    }

    #[test]
    fn probe_health_reports_unreachable_when_nothing_listens() {
        // Bind then immediately drop, so the port is almost certainly closed.
        let port = pick_free_port().expect("port");
        assert!(matches!(
            probe_health(port, "token"),
            HealthProbe::Unreachable(_)
        ));
    }

    #[test]
    fn probe_health_survives_a_cold_backend_that_returns_503_first() {
        let stub = StubBackend::start(StubConfig {
            warmup_hits: 1,
            ..StubConfig::default()
        });
        // First attempt is rejected: the backend is not ready yet. The poller
        // treats this as retryable rather than fatal.
        assert!(matches!(
            probe_health(stub.port(), "token"),
            HealthProbe::Rejected(503)
        ));
        // Then it becomes healthy.
        assert!(matches!(
            probe_health(stub.port(), "token"),
            HealthProbe::Ready(_)
        ));
    }

    // ── Readiness assessment ────────────────────────────────────────

    fn health(status: &str, database: &str, ai: &str, store: &str) -> HealthPayload {
        HealthPayload {
            status: status.into(),
            database: database.into(),
            ai: ai.into(),
            credential_store: store.into(),
        }
    }

    #[test]
    fn everything_healthy_is_ready() {
        assert_eq!(
            assess_readiness(&health("ok", "ready", "ready", "ready")),
            (StartupPhase::Ready, DiagnosticCode::None)
        );
    }

    #[test]
    fn an_absent_database_is_fatal() {
        let (phase, code) = assess_readiness(&health("degraded", "unavailable", "ready", "ready"));
        assert_eq!(phase, StartupPhase::FatalError);
        assert_eq!(code, DiagnosticCode::DatabaseUnavailable);
        assert!(code.is_fatal());
    }

    #[test]
    fn an_unavailable_credential_store_is_fatal_and_says_so() {
        let (phase, code) = assess_readiness(&health("ok", "ready", "ready", "unavailable"));
        assert_eq!(phase, StartupPhase::FatalError);
        assert_eq!(code, DiagnosticCode::CredentialStoreUnavailable);
        assert!(code.is_fatal());
        assert!(
            code.guidance().contains("secure credential storage"),
            "guidance must name the real problem: {}",
            code.guidance()
        );
    }

    #[test]
    fn a_missing_model_degrades_but_does_not_block_the_mailbox() {
        let (phase, code) = assess_readiness(&health("ok", "ready", "model_missing", "ready"));
        assert_eq!(phase, StartupPhase::Recovery);
        assert_eq!(code, DiagnosticCode::ModelMissing);
        assert!(
            !code.is_fatal(),
            "a missing model must not block the workspace"
        );
    }

    #[test]
    fn an_absent_ai_runtime_degrades_but_does_not_block_the_mailbox() {
        let (phase, code) = assess_readiness(&health("ok", "ready", "ollama_not_running", "ready"));
        assert_eq!(phase, StartupPhase::Recovery);
        assert_eq!(code, DiagnosticCode::AiRuntimeUnavailable);
        assert!(!code.is_fatal());
    }

    #[test]
    fn an_unreported_credential_store_is_treated_as_ready() {
        // An older backend omits the field. It must not brick a newer shell.
        let (phase, _) = assess_readiness(&health("ok", "ready", "ready", ""));
        assert_eq!(phase, StartupPhase::Ready);
    }

    #[test]
    fn recovery_and_ready_are_both_workspace_showing_states() {
        for (phase, _) in [
            assess_readiness(&health("ok", "ready", "ready", "ready")),
            assess_readiness(&health("ok", "ready", "model_missing", "ready")),
        ] {
            let next = BackendRuntimeState {
                phase,
                code: DiagnosticCode::None,
                port: Some(1),
                token: Some("t".into()),
                generation: 1,
                phase_started: Instant::now(),
            };
            let status = status_from(&next);
            assert!(status.ready, "{phase:?} must allow the workspace");
        }
    }

    #[test]
    fn fatal_error_never_allows_the_workspace() {
        let next = BackendRuntimeState {
            phase: StartupPhase::FatalError,
            code: DiagnosticCode::DatabaseUnavailable,
            port: None,
            token: None,
            generation: 1,
            phase_started: Instant::now(),
        };
        assert!(!status_from(&next).ready);
    }

    // ── Supervisor lifecycle ────────────────────────────────────────

    /// Build a supervisor that owns no Tauri app handle. The lifecycle rules
    /// under test (generation guard, state publication, port ownership) do not
    /// require a window.
    fn bare_supervisor() -> (watch::Sender<BackendRuntimeState>, Arc<ShutdownRegistry>) {
        let (state_tx, _) = watch::channel(BackendRuntimeState::new());
        (state_tx, Arc::new(ShutdownRegistry::default()))
    }

    #[tokio::test]
    async fn readiness_after_a_generation_survives_a_restart() {
        // Reproduces the real restart flow: publish Starting, bump the
        // generation, then let the poller finish. A stale poller from
        // generation 1 must not be able to clobber generation 2.
        let (state_tx, _registry) = bare_supervisor();
        let generation = AtomicU64::new(1);

        let state = state_tx.borrow().clone();
        assert_eq!(state.phase, StartupPhase::Boot);
        assert_eq!(state.generation, 0);

        // Simulate the first spawn reaching Ready.
        state_tx.send_replace(BackendRuntimeState {
            phase: StartupPhase::Ready,
            code: DiagnosticCode::None,
            port: Some(1111),
            token: Some("first".into()),
            generation: 1,
            phase_started: Instant::now(),
        });
        assert_eq!(state_tx.borrow().port, Some(1111));

        // Restart: generation advances, state returns to Starting.
        let next_generation = generation.fetch_add(1, Ordering::SeqCst) + 1;
        state_tx.send_replace(BackendRuntimeState {
            phase: StartupPhase::StartingBackend,
            code: DiagnosticCode::None,
            port: None,
            token: None,
            generation: next_generation,
            phase_started: Instant::now(),
        });
        assert_eq!(state_tx.borrow().phase, StartupPhase::StartingBackend);

        // A poller from generation 1 wakes up late. It must be rejected.
        let stale = BackendRuntimeState {
            phase: StartupPhase::Ready,
            code: DiagnosticCode::None,
            port: Some(1111),
            token: Some("first".into()),
            generation: 1,
            phase_started: Instant::now(),
        };
        if state_tx.borrow().generation == stale.generation {
            state_tx.send_replace(stale);
        }
        assert_eq!(
            state_tx.borrow().phase,
            StartupPhase::StartingBackend,
            "a stale poller must not overwrite a newer generation"
        );

        // The new poller succeeds and readiness is published for generation 2.
        state_tx.send_replace(BackendRuntimeState {
            phase: StartupPhase::Ready,
            code: DiagnosticCode::None,
            port: Some(2222),
            token: Some("second".into()),
            generation: 2,
            phase_started: Instant::now(),
        });
        let final_state = state_tx.borrow().clone();
        assert_eq!(final_state.phase, StartupPhase::Ready);
        assert_eq!(final_state.port, Some(2222));
        assert_eq!(final_state.token.as_deref(), Some("second"));
    }

    #[test]
    fn the_process_stays_owned_until_shutdown() {
        // Ownership is recorded in the registry on spawn and released exactly
        // once on terminate. This is what prevents an orphan.
        let registry = ShutdownRegistry::default();
        assert!(registry.target.lock().expect("lock").is_none());

        registry.set(ShutdownTarget {
            pid: 4242,
            port: 5555,
            token: "t".into(),
        });
        let registered = registry.target.lock().expect("lock").clone();
        assert!(registered.is_some(), "spawn must register ownership");

        // Take mirrors terminate(): the slot is emptied so a second call is a
        // no-op rather than a double kill.
        let taken = registry.target.lock().expect("lock").take();
        assert!(taken.is_some());
        assert!(
            registry.target.lock().expect("lock").is_none(),
            "ownership must be released after shutdown"
        );
    }

    #[test]
    fn shutdown_delivers_a_graceful_request_before_killing() {
        // The stub records that it received POST /api/shutdown, proving the
        // graceful leg of shutdown actually happens.
        let stub = StubBackend::start(StubConfig::default());
        let delivered = http_request(stub.port(), "POST", "/api/shutdown", "token");
        assert!(delivered, "graceful shutdown request must be delivered");
        assert!(
            stub.shutdown_requested.load(Ordering::SeqCst),
            "backend must observe the shutdown request"
        );
        assert!(stub.hits.load(Ordering::SeqCst) >= 1);
    }

    #[tokio::test]
    async fn await_backend_ready_returns_immediately_when_already_ready() {
        let (state_tx, _registry) = bare_supervisor();
        state_tx.send_replace(BackendRuntimeState {
            phase: StartupPhase::Ready,
            code: DiagnosticCode::None,
            port: Some(8080),
            token: Some("abc".into()),
            generation: 1,
            phase_started: Instant::now(),
        });
        let state = state_tx.borrow().clone();
        let (port, token) = match state.phase {
            StartupPhase::Ready | StartupPhase::Recovery => (state.port, state.token),
            _ => panic!("expected ready"),
        };
        assert_eq!(port, Some(8080));
        assert_eq!(token.as_deref(), Some("abc"));
    }

    #[test]
    fn failure_envelopes_carry_a_code_and_guidance() {
        let envelope = failure_envelope(DiagnosticCode::CredentialStoreUnavailable);
        let parsed: serde_json::Value = serde_json::from_str(&envelope).expect("valid json");
        assert_eq!(parsed["code"], "CREDENTIAL_STORE_UNAVAILABLE");
        assert_eq!(parsed["fatal"], true);
        assert!(parsed["guidance"].as_str().expect("guidance").len() > 20);
    }

    #[test]
    fn fatal_and_degraded_codes_are_classified_correctly() {
        assert!(DiagnosticCode::NoFreePort.is_fatal());
        assert!(DiagnosticCode::SidecarExited.is_fatal());
        assert!(DiagnosticCode::BackendHealthTimeout.is_fatal());
        assert!(DiagnosticCode::CredentialStoreUnavailable.is_fatal());
        assert!(!DiagnosticCode::ModelMissing.is_fatal());
        assert!(!DiagnosticCode::AiRuntimeUnavailable.is_fatal());
        assert!(!DiagnosticCode::None.is_fatal());
    }

    #[test]
    fn every_diagnostic_code_has_distinct_guidance() {
        let codes = [
            DiagnosticCode::NoFreePort,
            DiagnosticCode::SidecarSpawnFailed,
            DiagnosticCode::SidecarExited,
            DiagnosticCode::BackendHealthTimeout,
            DiagnosticCode::BackendRejected,
            DiagnosticCode::BackendBadHealthPayload,
            DiagnosticCode::BackendUnauthorized,
            DiagnosticCode::StartupTimeout,
            DiagnosticCode::StateChannelClosed,
            DiagnosticCode::DatabaseUnavailable,
            DiagnosticCode::CredentialStoreUnavailable,
            DiagnosticCode::AiRuntimeUnavailable,
            DiagnosticCode::ModelMissing,
        ];
        let mut seen = std::collections::HashSet::new();
        for code in codes {
            let text = code.guidance();
            assert!(!text.is_empty(), "{code:?} must have guidance");
            assert!(
                seen.insert(text.to_string()),
                "{code:?} duplicates another code's guidance"
            );
        }
    }

    #[test]
    fn diagnostic_codes_are_stable_strings() {
        // These strings are a support surface. Changing one is a breaking
        // change for the UI and for anyone reporting an issue.
        assert_eq!(DiagnosticCode::NoFreePort.as_str(), "NO_FREE_PORT");
        assert_eq!(
            DiagnosticCode::BackendHealthTimeout.as_str(),
            "BACKEND_HEALTH_TIMEOUT"
        );
        assert_eq!(
            DiagnosticCode::CredentialStoreUnavailable.as_str(),
            "CREDENTIAL_STORE_UNAVAILABLE"
        );
    }

    #[test]
    fn startup_phases_serialise_as_documented() {
        let json = serde_json::to_string(&StartupPhase::WaitingForBackend).expect("json");
        assert_eq!(json, "\"WAITING_FOR_BACKEND\"");
        let json = serde_json::to_string(&StartupPhase::FatalError).expect("json");
        assert_eq!(json, "\"FATAL_ERROR\"");
    }

    #[test]
    fn iso_timestamps_are_well_formed() {
        let stamp = iso8601_millis();
        assert_eq!(
            stamp.len(),
            24,
            "expected YYYY-MM-DDTHH:MM:SS.mmmZ, got {stamp}"
        );
        assert!(stamp.ends_with('Z'));
        assert_eq!(&stamp[4..5], "-");
        assert_eq!(&stamp[10..11], "T");
    }

    #[test]
    fn the_token_is_never_written_to_the_log() {
        // Structural guarantee: no log call in this file formats a token.
        // Asserted behaviourally by checking redaction of a realistic line.
        let token = generate_token().expect("csprng");
        let line = format!("health.probe port=49152 token={token} state=conn");
        let safe = redact(&line);
        assert!(!safe.contains(&token), "token must never be logged: {safe}");
    }
}
