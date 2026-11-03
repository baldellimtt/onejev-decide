# Native Windows setup: uv + qev + llama-server
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}

uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
uv pip install --python .\.venv\Scripts\python.exe "git+https://github.com/OmniJev/OneJev.git"

if (-not (Get-Command llama-server -ErrorAction SilentlyContinue)) {
    Write-Host "Installing llama.cpp (winget)..."
    winget install --id ggml.llamacpp -e --accept-package-agreements --accept-source-agreements
}

Write-Host ""
Write-Host "OK. Next:"
Write-Host "  1) .\scripts\serve.ps1"
Write-Host "  2) .\.venv\Scripts\python.exe scripts\ui.py"
Write-Host "     or: .\.venv\Scripts\python.exe scripts\infer.py data\incident\incident_01.jpg --pretty"
