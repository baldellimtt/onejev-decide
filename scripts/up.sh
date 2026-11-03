#!/usr/bin/env bash
# Build + start stack, then print where to connect (use this instead of bare docker compose up)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose up -d --build --remove-orphans "$@"

sleep 1
echo ""
docker compose logs ready --no-log-prefix || true
echo ""
