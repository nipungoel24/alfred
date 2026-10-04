use std::path::{Path, PathBuf};
use std::process::Command;

/// Where the repository's git directory lives, following the `gitdir:` pointer
/// that worktrees and submodules use.
fn git_dir() -> Option<PathBuf> {
    let dot_git = Path::new("../../.git");
    if dot_git.is_dir() {
        return Some(dot_git.to_path_buf());
    }
    if dot_git.is_file() {
        let contents = std::fs::read_to_string(dot_git).ok()?;
        let target = contents.strip_prefix("gitdir:")?.trim();
        let base = dot_git.parent()?;
        return Some(base.join(target));
    }
    None
}

/// The ref file HEAD currently points at, if HEAD is a symbolic ref.
fn head_ref(git: &Path) -> Option<PathBuf> {
    let head = std::fs::read_to_string(git.join("HEAD")).ok()?;
    let reference = head.strip_prefix("ref:")?.trim();
    if reference.is_empty() {
        return None;
    }
    Some(git.join(reference))
}

fn main() {
    // The build script's only input is the repository HEAD, so watch exactly
    // that and nothing else.
    //
    // Without these directives Cargo falls back to "re-run when any file in the
    // package changes". A commit that touches only `docs/` or `tools/` therefore
    // left the *previous* commit compiled into `ALFRED_GIT_COMMIT`, and the
    // shell logged a build identity that did not match the artifact it was
    // running in. That field is a support surface: it appears in `desktop.log`
    // and in `startup_diagnostics()`.
    if let Some(git) = git_dir() {
        println!("cargo:rerun-if-changed={}", git.join("HEAD").display());
        if let Some(reference) = head_ref(&git) {
            println!("cargo:rerun-if-changed={}", reference.display());
        }
    }

    let git_commit = Command::new("git")
        .args(["rev-parse", "--short=12", "HEAD"])
        .output()
        .ok()
        .filter(|output| output.status.success())
        .and_then(|output| String::from_utf8(output.stdout).ok())
        .map(|sha| sha.trim().to_string())
        .filter(|sha| !sha.is_empty())
        .unwrap_or_else(|| "unknown".to_string());

    println!("cargo:rustc-env=ALFRED_GIT_COMMIT={git_commit}");
    tauri_build::build()
}
