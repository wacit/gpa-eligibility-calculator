# GPA & Athletic Eligibility Calculator — Portable PowerShell launcher
# Right-click -> Run with PowerShell, or run from a terminal.
$here = Split-Path -Parent $PSCommandPath
$index = Join-Path $here 'app\index.html'
if (Test-Path $index) {
    Start-Process $index
} else {
    Write-Error "index.html not found at $index"
    Read-Host "Press Enter to exit"
}
