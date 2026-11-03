# OneJev GGUF — reads model/port/ctx from config.yaml
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")
if (-not $env:DECISION_CONFIG) {
    $env:DECISION_CONFIG = Join-Path $Root "config.yaml"
}
$env:QEV_DEBIAS = if ($env:QEV_DEBIAS) { $env:QEV_DEBIAS } else { "0" }

if (-not (Get-Command llama-server -ErrorAction SilentlyContinue)) {
    Write-Host "llama-server not found. Install: winget install ggml.llamacpp"
    exit 1
}

$meta = & .\.venv\Scripts\python.exe -c @"
from onejev_decide.config import get_config
m=get_config()['model']
print(m['gguf'])
print(m['port'])
print(m.get('max_branch_tokens', 2048))
print(m.get('max_request_tokens', 4096))
"@
$gguf, $port, $branch, $req = ($meta -split "`n") | ForEach-Object { $_.Trim() } | Where-Object { $_ }

Write-Host "Serving $gguf on :$port (ctx=$branch, debias=$env:QEV_DEBIAS) ..."
& .\.venv\Scripts\qev.exe serve --gguf $gguf --port ([int]$port) `
  --max-branch-tokens ([int]$branch) --max-request-tokens ([int]$req)
