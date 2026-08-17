# Derive Alfred web/PWA brand assets from the approved source icon.
#
# Prerequisites:
#   - frontend/public/alfred-icon.png  (the generated symbol-only mark)
#   - frontend/public/alfred-wordmark.png (optional horizontal lockup)
#
# This script does NOT generate the source artwork — it only derives the
# standard sizes Alfred references (favicon, 192, 512) and establishes the
# future Tauri icon source at desktop/branding/alfred-icon.png.
#
# Usage:  powershell -File frontend/scripts/derive-brand-assets.ps1
param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

$publicDir = Join-Path $RepoRoot 'frontend\public'
$source = Join-Path $publicDir 'alfred-icon.png'
$brandingDir = Join-Path $RepoRoot 'desktop\branding'

if (-not (Test-Path $source)) {
  Write-Output "SKIP: source asset not found at frontend\public\alfred-icon.png"
  Write-Output "      Copy the generated symbol-only Alfred icon there first."
  exit 0
}

Add-Type -AssemblyName System.Drawing

function Resize-Png([string]$src, [string]$dst, [int]$size) {
  $img = [System.Drawing.Image]::FromFile($src)
  $bmp = New-Object System.Drawing.Bitmap($size, $size)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $g.DrawImage($img, 0, 0, $size, $size)
  $bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $img.Dispose()
}

# favicon: 32x32
Resize-Png $source (Join-Path $publicDir 'favicon.png') 32
# PWA icons
Resize-Png $source (Join-Path $publicDir 'icon-192.png') 192
Resize-Png $source (Join-Path $publicDir 'icon-512.png') 512

# Future Tauri icon source (approved source asset, no Rust tooling needed)
if (-not (Test-Path $brandingDir)) {
  New-Item -ItemType Directory -Path $brandingDir | Out-Null
}
Copy-Item $source (Join-Path $brandingDir 'alfred-icon.png') -Force
$wordmark = Join-Path $publicDir 'alfred-wordmark.png'
if (Test-Path $wordmark) {
  Copy-Item $wordmark (Join-Path $brandingDir 'alfred-wordmark.png') -Force
}

Write-Output "Derived: favicon.png (32), icon-192.png, icon-512.png"
Write-Output "Tauri source staged at: desktop\branding\alfred-icon.png"
