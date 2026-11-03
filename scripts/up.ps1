# Build + start stack, then print where to connect (use this instead of bare docker compose up)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

docker compose up -d --build --remove-orphans @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Start-Sleep -Seconds 1
Write-Host ""
docker compose logs ready --no-log-prefix
Write-Host ""
