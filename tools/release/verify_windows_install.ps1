<#
Read-only verifier for Alfred's per-user Windows installation.

Run this from a normal PowerShell window after manually installing Alfred as
the real logged-in Windows user. It does not modify files, shortcuts, data, or
processes.
#>

$ErrorActionPreference = "Continue"

function Get-Sha256OrMissing {
  param([Parameter(Mandatory=$true)][string]$Path)
  if (Test-Path -LiteralPath $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
  }
  return "<missing>"
}

function PassFail {
  param([Parameter(Mandatory=$true)][bool]$Condition)
  if ($Condition) { "PASS" } else { "FAIL" }
}

$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$localAppData = [Environment]::GetFolderPath("LocalApplicationData")
$appData = [Environment]::GetFolderPath("ApplicationData")
$installDir = Join-Path $localAppData "Alfred"
$desktopPath = Join-Path $installDir "alfred-desktop.exe"
$backendPath = Join-Path $installDir "alfred-backend.exe"
$shortcutPath = Join-Path $appData "Microsoft\Windows\Start Menu\Programs\Alfred.lnk"

$shortcutTarget = "<missing>"
$shortcutWorkingDirectory = "<missing>"
if (Test-Path -LiteralPath $shortcutPath) {
  $shell = New-Object -ComObject WScript.Shell
  $shortcut = $shell.CreateShortcut($shortcutPath)
  $shortcutTarget = $shortcut.TargetPath
  $shortcutWorkingDirectory = $shortcut.WorkingDirectory
}

$desktopExists = Test-Path -LiteralPath $desktopPath
$backendExists = Test-Path -LiteralPath $backendPath
$shortcutExists = Test-Path -LiteralPath $shortcutPath
$shortcutTargetExists = Test-Path -LiteralPath $shortcutTarget
$targetInCurrentInstall = $shortcutTarget -ieq $desktopPath
$workingDirOk = ($shortcutWorkingDirectory -eq "") -or ($shortcutWorkingDirectory -ieq $installDir)
$alfredProcesses = Get-Process alfred* -ErrorAction SilentlyContinue |
  Select-Object Name, Id, Path, StartTime

$checks = [ordered]@{
  "Desktop exists" = $desktopExists
  "Backend exists" = $backendExists
  "Start Menu shortcut exists" = $shortcutExists
  "Shortcut target exists" = $shortcutTargetExists
  "Shortcut target is current user's install" = $targetInCurrentInstall
  "Shortcut working directory is install dir or empty" = $workingDirOk
}

Write-Host "Alfred Windows Install Verification"
Write-Host "Current Windows user: $currentUser"
Write-Host "Current LOCALAPPDATA: $localAppData"
Write-Host "Expected install directory: $installDir"
Write-Host ""
Write-Host "Installed desktop path: $desktopPath"
Write-Host "Installed desktop exists: $desktopExists"
Write-Host "Installed desktop SHA256: $(Get-Sha256OrMissing -Path $desktopPath)"
Write-Host ""
Write-Host "Installed backend path: $backendPath"
Write-Host "Installed backend exists: $backendExists"
Write-Host "Installed backend SHA256: $(Get-Sha256OrMissing -Path $backendPath)"
Write-Host ""
Write-Host "Start Menu shortcut path: $shortcutPath"
Write-Host "Shortcut target: $shortcutTarget"
Write-Host "Shortcut working directory: $shortcutWorkingDirectory"
Write-Host "Shortcut target exists: $shortcutTargetExists"
Write-Host ""
Write-Host "Checks:"
foreach ($key in $checks.Keys) {
  Write-Host ("  [{0}] {1}" -f (PassFail -Condition $checks[$key]), $key)
}
Write-Host ""
Write-Host "Alfred process status:"
if ($alfredProcesses) {
  $alfredProcesses | Format-Table -AutoSize
} else {
  Write-Host "  No Alfred processes running."
}

if ($checks.Values -contains $false) {
  exit 1
}
exit 0
