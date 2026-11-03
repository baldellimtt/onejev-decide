#!/usr/bin/env bash
# Native Ubuntu setup: uv + qev + llama-server
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python "git+https://github.com/OmniJev/OneJev.git"

if ! command -v llama-server >/dev/null 2>&1; then
  echo "llama-server not found in PATH."
  echo "Download a binary from https://github.com/ggml-org/llama.cpp/releases"
  exit 1
fi

echo ""
echo "OK. Next:"
echo "  1) ./scripts/serve.sh"
echo "  2) ./.venv/bin/python scripts/ui.py"
echo "     or: ./.venv/bin/python scripts/infer.py data/incident/incident_01.jpg --pretty"
