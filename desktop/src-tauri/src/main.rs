#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use tauri_plugin_shell::ShellExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // The executable is built by `python backend/build_sidecar.py`. Tauri's
            // sidecar resolver selects the Windows target-suffixed binary at bundle time.
            let (_events, child) = app.shell().sidecar("alfred-backend")?.spawn()?;
            app.manage(child);
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("failed to run Alfred desktop");
}
