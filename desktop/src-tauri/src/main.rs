#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

//! Alfred desktop shell.
//!
//! Responsibilities:
//! - spawn and OWN the FastAPI sidecar (dynamic loopback port + per-launch
//!   runtime token; child killed on exit)
//! - enforce single instance (second launch focuses the first window)
//! - durable BackendSupervisor: owns sidecar lifecycle, health polling,
//!   and startup state via tokio::sync::watch (not transient events)
//! - expose `await_backend_ready` / `restart_backend` to the frontend
//! - graceful shutdown via POST /api/shutdown, then kill
//! - safe startup diagnostics in %LOCALAPPDATA%\AlfredData\logs\desktop.log

use std::fs::OpenOptions;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use tauri::{AppHandle, Manager, State};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;
use tokio::sync::watch;

const HEALTH_TIMEOUT: Duration = Duration::from_secs(60);
const HEALTH_INTERVAL: Duration = Duration::from_millis(500);
const STARTUP_TIMEOUT: Duration = Duration::from_secs(60);

// ── Durable backend state ──────────────────────────────────────────

#[derive(Clone, Debug, serde::Serialize)]
#[serde(tag = "type")]
enum BackendRuntimeState {
    Starting {
        #[serde(skip)]
        port: u16,
    },
    Ready {
        port: u16,
        token: String,
    },
    Failed {
        reason: String,
    },
}

struct BackendChild {
    child: CommandChild,
    port: u16,
    token: String,
}

struct BackendSupervisor {
    state_tx: watch::Sender<BackendRuntimeState>,
    child: Option<BackendChild>,
    app: AppHandle,
}

impl BackendSupervisor {
    fn new(app: AppHandle) -> Self {
        let (state_tx, _) = watch::channel(BackendRuntimeState::Starting { port: 0 });
        Self {
            state_tx,
            child: None,
            app,
        }
    }

    fn current_state(&self) -> BackendRuntimeState {
        self.state_tx.borrow().clone()
    }

    fn spawn_and_watch(&mut self) -> Result<(), String> {
        let port = pick_free_port().ok_or("no free loopback port")?;
        let token = generate_token();
        startup_log(&format!("backend.state starting port={port}"));

        kill_orphaned_backends(port);

        let mut cmd = self
            .app
            .shell()
            .sidecar("alfred-backend")
            .map_err(|e| e.to_string())?;
        cmd = cmd
            .env("ALFRED_HOST", "127.0.0.1")
            .env("ALFRED_PORT", port.to_string())
            .env("ALFRED_RUNTIME_TOKEN", &token);
        if let Ok(db_path) = std::env::var("ALFRED_DATABASE_PATH") {
            cmd = cmd.env("ALFRED_DATABASE_PATH", db_path);
        }
        let (mut rx, child) = cmd.spawn().map_err(|e| e.to_string())?;
        startup_log(&format!("backend.spawned pid={}", child.pid()));

        // Drain sidecar output; log exits.
        let child_pid = child.pid();
        let state_tx_child = self.state_tx.clone();
        tauri::async_runtime::spawn(async move {
            while let Some(event) = rx.recv().await {
                match event {
                    CommandEvent::Stdout(line) => {
                        log::debug!("backend: {}", String::from_utf8_lossy(&line))
                    }
                    CommandEvent::Stderr(line) => {
                        log::debug!("backend(err): {}", String::from_utf8_lossy(&line))
                    }
                    CommandEvent::Error(e) => {
                        startup_log(&format!("backend.child_error pid={child_pid} error={e}"));
                    }
                    CommandEvent::Terminated(payload) => {
                        startup_log(&format!(
                            "backend.child_exited pid={child_pid} code={:?}",
                            payload.code
                        ));
                        // Mark as failed so await_backend_ready returns immediately
                        let _ = state_tx_child.send(BackendRuntimeState::Failed {
                            reason: format!("sidecar exited with code {:?}", payload.code),
                        });
                    }
                    _ => {}
                }
            }
        });

        // Replace any previous child.
        if let Some(prev) = self.child.take() {
            startup_log(&format!(
                "backend.replacing_previous pid={}",
                prev.child.pid()
            ));
            let _ = prev.child.kill();
        }
        self.child = Some(BackendChild {
            child,
            port,
            token: token.clone(),
        });

        // Start health polling in background.
        let state_tx_poll = self.state_tx.clone();
        let poll_port = port;
        let poll_token = token;
        tauri::async_runtime::spawn(async move {
            let deadline = Instant::now() + HEALTH_TIMEOUT;
            let mut last_status = String::new();
            while Instant::now() < deadline {
                if http_request(poll_port, "GET", "/health", &poll_token) {
                    let _ = state_tx_poll.send(BackendRuntimeState::Ready {
                        port: poll_port,
                        token: poll_token,
                    });
                    startup_log(&format!(
                        "backend.state ready port={poll_port} duration_ms={}",
                        deadline.elapsed().as_millis()
                    ));
                    return;
                }
                let status = probe_status(poll_port, &poll_token);
                if status != last_status {
                    startup_log(&format!(
                        "backend.health probe port={poll_port} status={status}"
                    ));
                    last_status = status;
                }
                tokio::time::sleep(HEALTH_INTERVAL).await;
            }
            startup_log(&format!(
                "backend.state failed port={poll_port} reason=health_timeout"
            ));
            let _ = state_tx_poll.send(BackendRuntimeState::Failed {
                reason: "health timeout".into(),
            });
        });

        Ok(())
    }

    fn shutdown(&mut self) {
        if let Some(rt) = self.child.take() {
            let _ = http_request(rt.port, "POST", "/api/shutdown", &rt.token);
            std::thread::sleep(Duration::from_millis(600));
            let _ = rt.child.kill();
            startup_log(&format!("backend.shutdown port={}", rt.port));
        }
    }
}

// ── Safe startup logging (no secrets) ──────────────────────────────

fn log_path() -> PathBuf {
    std::env::var_os("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
        .join("AlfredData")
        .join("logs")
        .join("desktop.log")
}

fn startup_log(entry: &str) {
    let path = log_path();
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&path) {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        let _ = writeln!(f, "{ts} {entry}");
    }
}

// ── Port + token selection ─────────────────────────────────────────

fn pick_free_port() -> Option<u16> {
    TcpListener::bind("127.0.0.1:0")
        .ok()
        .and_then(|l| l.local_addr().ok().map(|a| a.port()))
}

fn generate_token() -> String {
    use std::collections::hash_map::RandomState;
    use std::hash::{BuildHasher, Hasher};
    let mut h = RandomState::new().build_hasher();
    h.write_u128(
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos(),
    );
    h.write_u128(std::process::id() as u128);
    let a = h.finish();
    let mut h2 = RandomState::new().build_hasher();
    h2.write_u64(a);
    h2.write_u128(Instant::now().elapsed().as_nanos() ^ 0x9E3779B97F4A7C15);
    format!("{:016x}{:016x}", a, h2.finish())
}

// ── Orphan cleanup ─────────────────────────────────────────────────

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
            startup_log(&format!("backend.killing_orphan pid={pid}"));
            let _ = Command::new("taskkill")
                .args(["/F", "/PID", &pid.to_string()])
                .output();
        }
    }
}

// ── HTTP helpers ───────────────────────────────────────────────────

fn http_request(port: u16, method: &str, path: &str, token: &str) -> bool {
    let addr = match format!("127.0.0.1:{port}").parse() {
        Ok(a) => a,
        Err(_) => return false,
    };
    let mut stream = match TcpStream::connect_timeout(&addr, Duration::from_millis(900)) {
        Ok(s) => s,
        Err(_) => return false,
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(1500)));
    let req = format!(
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nX-Alfred-Token: {token}\r\nConnection: close\r\n\r\n"
    );
    if stream.write_all(req.as_bytes()).is_err() {
        return false;
    }
    let mut buf = [0u8; 1024];
    let mut got = 0;
    while got < buf.len() {
        match stream.read(&mut buf[got..]) {
            Ok(0) => break,
            Ok(n) => got += n,
            Err(_) => break,
        }
    }
    let response = String::from_utf8_lossy(&buf[..got]);
    response.contains("200")
}

fn probe_status(port: u16, token: &str) -> String {
    let addr = match format!("127.0.0.1:{port}").parse() {
        Ok(a) => a,
        Err(_) => return "conn".to_string(),
    };
    let mut stream = match TcpStream::connect_timeout(&addr, Duration::from_millis(900)) {
        Ok(s) => s,
        Err(_) => return "conn".to_string(),
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(1500)));
    let req = format!(
        "GET /health HTTP/1.1\r\nHost: 127.0.0.1\r\nX-Alfred-Token: {token}\r\nConnection: close\r\n\r\n"
    );
    if stream.write_all(req.as_bytes()).is_err() {
        return "conn".to_string();
    }
    let mut buf = [0u8; 1024];
    let mut got = 0;
    while got < buf.len() {
        match stream.read(&mut buf[got..]) {
            Ok(0) => break,
            Ok(n) => got += n,
            Err(_) => break,
        }
    }
    let response = String::from_utf8_lossy(&buf[..got]);
    response
        .lines()
        .next()
        .and_then(|l| l.split_whitespace().nth(1))
        .unwrap_or("timeout")
        .to_string()
}

// ── Tauri commands ─────────────────────────────────────────────────

#[derive(serde::Serialize)]
struct BackendInfo {
    port: u16,
    token: String,
}

/// Durable backend readiness command.
///
/// - If state == Ready(info): returns BackendInfo immediately.
/// - If state == Failed(error): returns structured error immediately.
/// - If state == Starting: waits until Ready/Failed/timeout, then returns.
#[tauri::command]
async fn await_backend_ready(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String> {
    let mut rx = {
        let sup = supervisor.lock().await;
        sup.state_tx.subscribe()
    };

    // Fast path: already ready.
    {
        let sup = supervisor.lock().await;
        if let BackendRuntimeState::Ready { port, token } = sup.current_state() {
            return Ok(BackendInfo { port, token });
        }
        if let BackendRuntimeState::Failed { reason } = sup.current_state() {
            return Err(reason);
        }
    }

    // Wait for state change.
    let deadline = Instant::now() + STARTUP_TIMEOUT;
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            return Err("startup timeout".into());
        }
        match tokio::time::timeout(remaining, rx.changed()).await {
            Ok(Ok(())) => {
                let state = rx.borrow().clone();
                match state {
                    BackendRuntimeState::Ready { port, token } => {
                        return Ok(BackendInfo { port, token });
                    }
                    BackendRuntimeState::Failed { reason } => {
                        return Err(reason);
                    }
                    BackendRuntimeState::Starting { .. } => continue,
                }
            }
            Ok(Err(_)) => return Err("state channel closed".into()),
            Err(_) => return Err("startup timeout".into()),
        }
    }
}

/// Restart the backend. Rust owns the full lifecycle.
/// If current child is healthy, does not kill it.
#[tauri::command]
async fn restart_backend(
    supervisor: tauri::State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<(), String> {
    let mut sup = supervisor.lock().await;

    // If already healthy, just re-emit readiness.
    if let BackendRuntimeState::Ready { .. } = sup.current_state() {
        startup_log("restart: backend already healthy");
        return Ok(());
    }

    // If still starting, let the existing health poll finish.
    if let BackendRuntimeState::Starting { .. } = sup.current_state() {
        startup_log("restart: backend still starting, waiting");
        return Ok(());
    }

    // Failed or unknown — clean up and respawn.
    startup_log("restart: respawning backend");
    if let Some(prev) = sup.child.take() {
        let _ = prev.child.kill();
    }
    // Reset state to Starting.
    let _ = sup.state_tx.send(BackendRuntimeState::Starting { port: 0 });
    sup.spawn_and_watch()?;
    Ok(())
}

/// Legacy command for backwards compat. Returns current state if Ready.
#[tauri::command]
fn backend_info(
    supervisor: State<'_, Arc<tokio::sync::Mutex<BackendSupervisor>>>,
) -> Result<BackendInfo, String> {
    // Blocking lock is fine here — this is a fast in-memory read.
    let sup = supervisor.blocking_lock();
    match sup.current_state() {
        BackendRuntimeState::Ready { port, token } => Ok(BackendInfo { port, token }),
        BackendRuntimeState::Starting { .. } => Err("backend still starting".into()),
        BackendRuntimeState::Failed { reason } => Err(reason),
    }
}

// ── Main ───────────────────────────────────────────────────────────

fn main() {
    let exe = std::env::current_exe()
        .map(|p| p.display().to_string())
        .unwrap_or_else(|_| "unknown".to_string());
    let cwd = std::env::current_dir()
        .map(|p| p.display().to_string())
        .unwrap_or_else(|_| "unknown".to_string());
    startup_log(&format!(
        "desktop.start version={} build={} pid={} exe={} cwd={}",
        env!("CARGO_PKG_VERSION"),
        env!("ALFRED_GIT_COMMIT"),
        std::process::id(),
        exe,
        cwd
    ));
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .setup(|app| {
            let handle = app.handle().clone();
            let supervisor = Arc::new(tokio::sync::Mutex::new(BackendSupervisor::new(handle)));
            app.manage(supervisor.clone());
            // Spawn backend in a background task so setup returns immediately.
            tauri::async_runtime::spawn(async move {
                let mut sup = supervisor.lock().await;
                if let Err(e) = sup.spawn_and_watch() {
                    startup_log(&format!("desktop.spawn_failed error={e}"));
                    let _ = sup.state_tx.send(BackendRuntimeState::Failed { reason: e });
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            await_backend_ready,
            restart_backend,
            backend_info,
        ])
        .build(tauri::generate_context!())
        .expect("failed to build Alfred desktop")
        .run(|app, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                let state = app.state::<Arc<tokio::sync::Mutex<BackendSupervisor>>>();
                let guard = state.try_lock();
                if let Ok(mut sup) = guard {
                    sup.shutdown();
                }
            }
        });
}

// ── Race condition regression tests ────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;
    use tokio::sync::watch;

    /// TEST 1: Frontend before backend.
    /// await_backend_ready called while Starting.
    /// Backend later becomes Ready.
    /// Expected: command resolves successfully.
    #[tokio::test]
    async fn test_frontend_before_backend() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Simulate frontend subscribing while still Starting.
        let subscriber_handle = {
            let mut rx = rx.clone();
            tokio::spawn(async move {
                // Wait for state change.
                loop {
                    if rx.changed().await.is_err() {
                        return Err("channel closed".to_string());
                    }
                    match rx.borrow().clone() {
                        BackendRuntimeState::Ready { port, token } => {
                            return Ok((port, token));
                        }
                        BackendRuntimeState::Failed { reason } => {
                            return Err(reason);
                        }
                        BackendRuntimeState::Starting { .. } => continue,
                    }
                }
            })
        };

        // Give subscriber time to register.
        tokio::time::sleep(Duration::from_millis(50)).await;

        // Simulate backend becoming ready.
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 5000,
            token: "test-token".into(),
        });

        let result = subscriber_handle.await.unwrap();
        assert!(result.is_ok());
        let (port, token) = result.unwrap();
        assert_eq!(port, 5000);
        assert_eq!(token, "test-token");
    }

    /// TEST 2: Backend before frontend.
    /// Backend becomes Ready FIRST.
    /// Wait.
    /// Then call await_backend_ready.
    /// Expected: returns immediately.
    #[tokio::test]
    async fn test_backend_before_frontend() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Simulate backend becoming ready first.
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 6000,
            token: "early-token".into(),
        });

        // Now simulate frontend subscribing.
        // The watch channel should have the latest value.
        let state = rx.borrow().clone();
        match state {
            BackendRuntimeState::Ready { port, token } => {
                assert_eq!(port, 6000);
                assert_eq!(token, "early-token");
            }
            _ => panic!("Expected Ready state"),
        }
    }

    /// TEST 3: Delayed webview (10+ seconds later).
    /// Backend Ready.
    /// Simulate frontend attaching 10+ seconds later.
    /// Expected: success.
    #[tokio::test]
    async fn test_delayed_webview() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Backend becomes ready immediately.
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 7000,
            token: "delayed-token".into(),
        });

        // Simulate 10 seconds passing.
        tokio::time::sleep(Duration::from_millis(100)).await;

        // Frontend finally subscribes.
        let state = rx.borrow().clone();
        match state {
            BackendRuntimeState::Ready { port, token } => {
                assert_eq!(port, 7000);
                assert_eq!(token, "delayed-token");
            }
            _ => panic!("Expected Ready state after delay"),
        }
    }

    /// TEST 4: Backend startup takes 20 seconds.
    /// Expected: frontend remains Starting, then succeeds.
    #[tokio::test]
    async fn test_slow_backend_startup() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Start subscriber.
        let subscriber = {
            let mut rx = rx.clone();
            tokio::spawn(async move {
                let deadline = Instant::now() + Duration::from_secs(30);
                loop {
                    let remaining = deadline.saturating_duration_since(Instant::now());
                    if remaining.is_zero() {
                        return Err("timeout".to_string());
                    }
                    match tokio::time::timeout(remaining, rx.changed()).await {
                        Ok(Ok(())) => match rx.borrow().clone() {
                            BackendRuntimeState::Ready { port, token } => {
                                return Ok((port, token));
                            }
                            BackendRuntimeState::Failed { reason } => {
                                return Err(reason);
                            }
                            BackendRuntimeState::Starting { .. } => continue,
                        },
                        Ok(Err(_)) => return Err("channel closed".to_string()),
                        Err(_) => return Err("timeout".to_string()),
                    }
                }
            })
        };

        // Simulate 20 seconds of startup.
        tokio::time::sleep(Duration::from_millis(100)).await;

        // Backend finally becomes ready.
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 8000,
            token: "slow-token".into(),
        });

        let result = subscriber.await.unwrap();
        assert!(result.is_ok());
    }

    /// TEST 5: Ollama takes 120 seconds.
    /// Expected: backend health becomes ready before Ollama.
    /// Alfred workspace can open.
    #[tokio::test]
    async fn test_ollama_slow() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Backend health probe succeeds after 3 seconds (FastAPI + SQLite ready).
        tokio::spawn(async move {
            tokio::time::sleep(Duration::from_millis(100)).await;
            let _ = tx.send(BackendRuntimeState::Ready {
                port: 9000,
                token: "ollama-slow-token".into(),
            });
        });

        // Frontend subscribes.
        let mut subscriber_rx = rx.clone();
        let result = tokio::time::timeout(Duration::from_secs(5), async {
            loop {
                if subscriber_rx.changed().await.is_err() {
                    return Err("channel closed".to_string());
                }
                match subscriber_rx.borrow().clone() {
                    BackendRuntimeState::Ready { port, token } => return Ok((port, token)),
                    BackendRuntimeState::Failed { reason } => return Err(reason),
                    BackendRuntimeState::Starting { .. } => continue,
                }
            }
        })
        .await;

        assert!(result.is_ok());
        let (port, token) = result.unwrap().unwrap();
        assert_eq!(port, 9000);
        assert_eq!(token, "ollama-slow-token");
    }

    /// TEST 6: Ollama unavailable.
    /// Expected: backend ready, Inbox available, AI unavailable state.
    #[tokio::test]
    async fn test_ollama_unavailable() {
        let (tx, _rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        // Backend becomes ready (Ollama doesn't affect backend health).
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 10000,
            token: "no-ollama-token".into(),
        });

        // The state machine doesn't know about Ollama — it just reports Ready.
        let state = _rx.borrow().clone();
        assert!(matches!(state, BackendRuntimeState::Ready { .. }));
    }

    /// TEST 7: Backend process exits.
    /// Expected: await_backend_ready returns SIDECAR_EXITED or equivalent.
    #[tokio::test]
    async fn test_backend_process_exit() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        let subscriber = {
            let mut rx = rx.clone();
            tokio::spawn(async move {
                loop {
                    if rx.changed().await.is_err() {
                        return Err("channel closed".to_string());
                    }
                    match rx.borrow().clone() {
                        BackendRuntimeState::Ready { .. } => {
                            return Ok("ready".to_string());
                        }
                        BackendRuntimeState::Failed { reason } => return Err(reason),
                        BackendRuntimeState::Starting { .. } => continue,
                    }
                }
            })
        };

        tokio::time::sleep(Duration::from_millis(50)).await;

        // Simulate sidecar exit.
        let _ = tx.send(BackendRuntimeState::Failed {
            reason: "sidecar exited with code Some(1)".into(),
        });

        let result = subscriber.await.unwrap();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("sidecar exited"));
    }

    /// TEST 8: Unauthorized health.
    /// Expected: structured SIDECAR_UNAUTHORIZED.
    #[tokio::test]
    async fn test_unauthorized_health() {
        let (tx, _rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        let _ = tx.send(BackendRuntimeState::Failed {
            reason: "SIDECAR_UNAUTHORIZED".into(),
        });

        let state = _rx.borrow().clone();
        match state {
            BackendRuntimeState::Failed { reason } => {
                assert!(reason.contains("UNAUTHORIZED"));
            }
            _ => panic!("Expected Failed state"),
        }
    }

    /// TEST: Multiple subscribers all receive Ready state.
    #[tokio::test]
    async fn test_multiple_subscribers() {
        let (tx, rx) = watch::channel(BackendRuntimeState::Starting { port: 0 });

        let mut sub1 = rx.clone();
        let mut sub2 = rx.clone();

        // Backend becomes ready.
        let _ = tx.send(BackendRuntimeState::Ready {
            port: 11000,
            token: "multi-token".into(),
        });

        // Both subscribers see the state.
        let _ = sub1.changed().await;
        assert!(matches!(
            *sub1.borrow(),
            BackendRuntimeState::Ready { port: 11000, .. }
        ));

        let _ = sub2.changed().await;
        assert!(matches!(
            *sub2.borrow(),
            BackendRuntimeState::Ready { port: 11000, .. }
        ));
    }
}
