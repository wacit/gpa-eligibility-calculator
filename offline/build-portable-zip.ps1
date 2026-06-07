# Builds the portable offline ZIP for the GPA & Athletic Eligibility Calculator.
# Run from the offline/ folder, or pass the script path explicitly.
$ErrorActionPreference = 'Stop'
$here   = Split-Path -Parent $PSCommandPath
$root   = Resolve-Path (Join-Path $here '..')
$staging = Join-Path $here '_staging'
$appdir  = Join-Path $staging 'app'
$zipOut  = Join-Path $root 'gpatelca-offline.zip'

# Clean
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $appdir | Out-Null

# Files to ship inside app/
$appFiles = @(
  'index.html', 'athletics.json',
  'favicon.ico','favicon-16.png','favicon-32.png','favicon-48.png',
  'apple-touch-icon.png','icon-512.png',
  'gpa_template.csv'
)
foreach ($f in $appFiles) {
  $src = Join-Path $root $f
  if (Test-Path $src) { Copy-Item $src (Join-Path $appdir $f) }
  else { Write-Warning "Missing: $f" }
}

# Launchers + readme go at the zip root
foreach ($f in @('Launch.cmd','Launch.ps1','Launch.command','README.txt')) {
  Copy-Item (Join-Path $here $f) (Join-Path $staging $f)
}

# Build the zip
if (Test-Path $zipOut) { Remove-Item $zipOut -Force }
Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zipOut -CompressionLevel Optimal

# Clean staging
Remove-Item $staging -Recurse -Force

$size = [math]::Round((Get-Item $zipOut).Length / 1KB, 1)
Write-Output "Built: $zipOut  ($size KB)"
