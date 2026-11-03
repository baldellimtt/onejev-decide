#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export DECISION_CONFIG="${DECISION_CONFIG:-$ROOT/config.yaml}"
export QEV_DEBIAS="${QEV_DEBIAS:-0}"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
  QEV="$ROOT/.venv/bin/qev"
else
  PY=python3
  QEV=qev
fi

read -r GGUF PORT BRANCH REQ < <("$PY" - <<'PY'
from onejev_decide.config import get_config
m = get_config()["model"]
print(m["gguf"], m["port"], m.get("max_branch_tokens", 2048), m.get("max_request_tokens", 4096))
PY
)

if ! command -v llama-server >/dev/null 2>&1; then
  echo "llama-server not found in PATH"
  exit 1
fi

echo "Serving $GGUF on :${PORT} (ctx=${BRANCH}, debias=${QEV_DEBIAS}) ..."
exec "$QEV" serve --gguf "$GGUF" --port "$PORT" --host 0.0.0.0 \
  --max-branch-tokens "$BRANCH" --max-request-tokens "$REQ"
