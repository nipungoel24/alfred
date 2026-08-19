#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

//! Alfred desktop shell.
//!
//! Responsibilities:
//! - spawn and OWN the FastAPI sidecar (dynamic loopback port + per-launch
//!   runtime token; child killed on exit)
//! - enforce single instance (second launch focuses the first window)
//! - poll backend health before revealing the workspace
//! - graceful shutdown via POST /api/shutdown, then kill
//! - expose `backend_info` / `retry_backend` to the frontend only
//! - safe startup diagnostics in %LOCALAPPDATA%\AlfredData\logs\desktop.log
//!   (ports, PIDs, stages, HTTP status categories — never tokens/secrets)

use std::fs::OpenOptions;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::PathBuf;
use std::sync::Mutex;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use tauri::{AppHandle, Emitter, Manager, State};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

const HEALTH_TIMEOUT: Duration = Duration::from_secs(45);
const HEALTH_INTERVAL: Duration = Duration::from_millis(500);

struct BackendRuntime {
    child: CommandChild,
    port: u16,
    token: String,
}

#[derive(Default)]
struct BackendState(Mutex<Option<BackendRuntime>>);

#[derive(serde::Serialize)]
struct BackendInfo {
    port: u16,
    token: String,
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

/// High-entropy per-launch token (not persisted, never logged).
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

// ── Sidecar lifecycle ──────────────────────────────────────────────

fn spawn_backend(app: &AppHandle, state: &BackendState) -> Result<(), String> {
    let port = pick_free_port().ok_or("no free loopback port")?;
    let token = generate_token();
    startup_log(&format!("spawn port={port}"));

    let mut cmd = app
        .shell()
        .sidecar("alfred-backend")
        .map_err(|e| e.to_string())?;
    cmd = cmd
        .env("ALFRED_HOST", "127.0.0.1")
        .env("ALFRED_PORT", port.to_string())
        .env("ALFRED_RUNTIME_TOKEN", &token);
    // Supported test/alternate data root: pass through when the shell's
    // own environment defines it (used for isolated fresh-profile QA).
    if let Ok(db_path) = std::env::var("ALFRED_DATABASE_PATH") {
        cmd = cmd.env("ALFRED_DATABASE_PATH", db_path);
    }
    let (mut rx, child) = cmd.spawn().map_err(|e| e.to_string())?;
    startup_log(&format!("spawned child_pid={}", child.pid()));

    // Drain sidecar output; keep last lines for diagnostics; log exits.
    let child_pid = child.pid();
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
                    startup_log(&format!("child_error pid={child_pid} error={e}"));
                }
                CommandEvent::Terminated(payload) => {
                    startup_log(&format!(
                        "child_exited pid={child_pid} code={:?}",
                        payload.code
                    ));
                }
                _ => {}
            }
        }
    });

    let mut guard = state.0.lock().unwrap();
    if let Some(prev) = guard.take() {
        startup_log(&format!(
            "replacing previous child pid={}",
            prev.child.pid()
        ));
        let _ = prev.child.kill();
    }
    *guard = Some(BackendRuntime { child, port, token });
    Ok(())
}

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

fn backend_alive(state: &BackendState) -> bool {
    let guard = state.0.lock().unwrap();
    match guard.as_ref() {
        Some(rt) => http_request(rt.port, "GET", "/health", &rt.token),
        None => false,
    }
}

/// Poll health until ready or the timeout elapses, then reveal the window.
fn wait_and_reveal(app: AppHandle, port: u16, token: String) {
    std::thread::spawn(move || {
        let deadline = Instant::now() + HEALTH_TIMEOUT;
        let mut ready = false;
        let mut last_status = String::new();
        while Instant::now() < deadline {
            if http_request(port, "GET", "/health", &token) {
                ready = true;
                break;
            }
            let status = probe_status(port, &token);
            if status != last_status {
                startup_log(&format!("probe port={port} status={status}"));
                last_status = status;
            }
            std::thread::sleep(HEALTH_INTERVAL);
        }
        startup_log(&format!("readiness port={port} ready={ready}"));
        let _ = app.emit("backend-ready", ready);
        if let Some(window) = app.get_webview_window("main") {
            let _ = window.show();
            let _ = window.set_focus();
        }
    });
}

fn shutdown_backend(state: &BackendState) {
    let mut guard = state.0.lock().unwrap();
    if let Some(rt) = guard.take() {
        // Graceful: stop workers + close SQLite, then exit.
        let _ = http_request(rt.port, "POST", "/api/shutdown", &rt.token);
        std::thread::sleep(Duration::from_millis(600));
        let _ = rt.child.kill();
        startup_log(&format!("shutdown port={}", rt.port));
    }
}

// ── Frontend commands ──────────────────────────────────────────────

#[tauri::command]
fn backend_info(state: State<BackendState>) -> Result<BackendInfo, String> {
    let guard = state.0.lock().unwrap();
    match guard.as_ref() {
        Some(rt) => Ok(BackendInfo {
            port: rt.port,
            token: rt.token.clone(),
        }),
        None => Err("backend not started".into()),
    }
}

#[tauri::command]
fn retry_backend(app: AppHandle, state: State<BackendState>) -> Result<(), String> {
    // If the current backend is already healthy, do NOT kill it — just
    // re-run the readiness reveal. Killing a healthy-but-late backend and
    // respawning made every Retry repeat the slow cold-start cycle.
    if backend_alive(&state) {
        startup_log("retry: backend already healthy, re-revealing");
        let (port, token) = {
            let guard = state.0.lock().unwrap();
            let rt = guard.as_ref().ok_or("backend not started")?;
            (rt.port, rt.token.clone())
        };
        let _ = app.emit("backend-ready", true);
        if let Some(window) = app.get_webview_window("main") {
            let _ = window.show();
            let _ = window.set_focus();
        }
        wait_and_reveal(app, port, token);
        return Ok(());
    }

    startup_log("retry: respawning backend");
    {
        let mut guard = state.0.lock().unwrap();
        if let Some(rt) = guard.take() {
            let _ = rt.child.kill();
        }
    }
    spawn_backend(&app, &state)?;
    let (port, token) = {
        let guard = state.0.lock().unwrap();
        let rt = guard.as_ref().ok_or("backend not started")?;
        (rt.port, rt.token.clone())
    };
    wait_and_reveal(app, port, token);
    Ok(())
}

fn main() {
    startup_log(&format!(
        "desktop start version={}",
        env!("CARGO_PKG_VERSION")
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
        .manage(BackendState::default())
        .invoke_handler(tauri::generate_handler![backend_info, retry_backend])
        .setup(|app| {
            let handle = app.handle().clone();
            let state = app.state::<BackendState>();
            spawn_backend(&handle, &state)?;
            let (port, token) = {
                let guard = state.0.lock().unwrap();
                let rt = guard.as_ref().expect("backend just spawned");
                (rt.port, rt.token.clone())
            };
            wait_and_reveal(handle, port, token);
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("failed to build Alfred desktop")
        .run(|app, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                shutdown_backend(&app.state::<BackendState>());
            }
        });
}
