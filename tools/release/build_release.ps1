# Canonical release build.

# `cargo tauri build` copies whatever is already in
# desktop/src-tauri/binaries/ - it never rebuilds the backend. Running it
# without rebuilding the sidecar first packages the PREVIOUS Python backend,
# which is how a release shipped a sidecar predating secure_store.py and how
# stale extraction rules kept running. The order below is mandatory.
#
#   1. build the sidecar from the current backend source
#   2. prove it is newer than every backend source
#   3. build the bundle, which embeds the frontend and packages that sidecar
#   4. re-check freshness, then scan the result for credentials
#
# Usage (from the repository root):
#   pwsh -File tools/release/build_release.ps1
#   pwsh -File tools/release/build_release.ps1 -SkipSidecar   # only if you know why

[CmdletBinding()]
param(
    [switch]$SkipSidecar
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Push-Location $root

function Step($n) { Write-Host "`n[$n]" -ForegroundColor Cyan }

try {
    Step '1/4  backend sidecar'
    if ($SkipSidecar) {
        Write-Warning 'SkipSidecar: the packaged sidecar will NOT be rebuilt."
        Write-Warning 'Use only when you have already run build_sidecar.py yourself.'
    }
    else {
        # build_sidecar.py refuses to run when GMAIL_CLIENT_SECRET is set
        # (ADR-010). It reloads that variable from backend/.env via
        # load_dotenv, so clearing it in this shell is not enough - the key has
        # to be PRESENT but empty, which makes load_dotenv skip it while the
        # guard's truthiness check passes. Windows PowerShell 5.1 cannot express
        # that ($env:X = '' removes the key), so a two-line launcher sets it in
        # Python instead. backend/.env is never read, moved or modified, and no
        # credential is embedded or logged.
        $launcher = Join-Path $env:TEMP 'alfred-sidecar-build.py'
        $body = @(
            'import os, runpy, sys',
            'os.environ["GMAIL_CLIENT_SECRET"] = ""',
            'os.environ["GOOGLE_CLIENT_SECRET"] = ""',
            'sys.argv = ["backend/build_sidecar.py"]',
            'runpy.run_path("backend/build_sidecar.py", run_name="__main__")'
        ) -join "`n"
        # UTF-8 without a BOM: a BOM in a .py file is exactly the corruption
        # this repository has to guard against, so do not add one here.
        [System.IO.File]::WriteAllText($launcher, $body, (New-Object System.Text.UTF8Encoding($false)))
        & py -3.12 $launcher
        if ($LASTEXITCODE -ne 0) { throw "build_sidecar.py failed ($LASTEXITCODE)" }
    }

    Step '2/4  sidecar freshness'
    & py -3.12 tools\release\check_sidecar_freshness.py
    if ($LASTEXITCODE -ne 0) { throw "sidecar is stale - refusing to package" }

    Step '3/4  tauri bundle (embeds the frontend, packages the sidecar)'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    Push-Location desktop
    try { & cargo tauri build } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw "cargo tauri build failed ($LASTEXITCODE)" }

    Step '4/4  post-build checks'
    & py -3.12 tools\release\check_sidecar_freshness.py
    if ($LASTEXITCODE -ne 0) { throw "sidecar went stale during the build" }
    & py -3.12 tools\release\scan_release_secrets.py
    if ($LASTEXITCODE -ne 0) { throw "secret scan failed" }

    $installer = 'desktop\src-tauri\target\release\bundle\nsis\Alfred_0.1.0_x64-setup.exe'
    if (Test-Path $installer) {
        $item = Get-Item $installer
        Write-Host "`nBuilt $($item.FullName)  ($([math]::Round($item.Length/1MB,1)) MB)" -ForegroundColor Green
    }
    Write-Host 'Release build complete.' -ForegroundColor Green
}
finally {
    Pop-Location
}
