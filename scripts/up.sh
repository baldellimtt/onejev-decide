#!/usr/bin/env bash
# Build + start stack, then print where to connect
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose up -d --build "$@"

PORT="${PORT:-8000}"
UI_PORT="${UI_PORT:-7860}"

echo ""
echo "========================================"
echo " onejev-decide ready"
echo "   API   http://127.0.0.1:${PORT}"
echo "   UI    http://127.0.0.1:${UI_PORT}"
echo "   infer docker compose run --rm infer data/incident/incident_01.jpg --pretty"
echo "========================================"
echo ""
