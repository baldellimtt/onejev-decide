#!/usr/bin/env bash
set -euo pipefail
cd /app

read -r GGUF PORT BRANCH REQ WARM < <(python3 - <<'PY'
from onejev_decide.config import get_config
c = get_config()
m, i = c["model"], c.get("inference") or {}
print(
    m["gguf"],
    m["port"],
    m.get("max_branch_tokens", 1536),
    m.get("max_request_tokens", 3072),
    1 if i.get("warmup", True) else 0,
)
PY
)

export QEV_DEBIAS="${QEV_DEBIAS:-0}"

_banner() {
  echo ""
  echo "========================================"
  echo " onejev-decide ready"
  echo "   API   http://127.0.0.1:${PORT}"
  echo "   UI    http://127.0.0.1:7860"
  echo "   infer docker compose run --rm infer data/incident/incident_01.jpg --pretty"
  echo "========================================"
  echo ""
}

case "${1:-serve}" in
  serve)
    shift || true
    qev serve \
      --gguf "$GGUF" \
      --port "$PORT" \
      --host 0.0.0.0 \
      --max-branch-tokens "$BRANCH" \
      --max-request-tokens "$REQ" \
      "$@" &
    pid=$!
    if [[ "$WARM" == "1" ]]; then
      python3 -m onejev_decide.warmup || echo "warmup skipped"
    fi
    _banner
    wait "$pid"
    ;;
  infer)
    shift
    exec python3 scripts/infer.py "$@"
    ;;
  analyze)
    shift || true
    exec python3 scripts/analyze.py "$@"
    ;;
  ui)
    shift || true
    exec python3 scripts/ui.py --host 0.0.0.0 "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
