# Build + start stack, then print where to connect
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

docker compose up -d --build @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$port = if ($env:PORT) { $env:PORT } else { "8000" }
$ui = if ($env:UI_PORT) { $env:UI_PORT } else { "7860" }

Write-Host ""
Write-Host "========================================"
Write-Host " onejev-decide ready"
Write-Host "   API   http://127.0.0.1:$port"
Write-Host "   UI    http://127.0.0.1:$ui"
Write-Host "   infer docker compose run --rm infer data/incident/incident_01.jpg --pretty"
Write-Host "========================================"
Write-Host ""
