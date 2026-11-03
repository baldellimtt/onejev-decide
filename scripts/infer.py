"""CLI: one image → JSON."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from onejev_decide import decide, reload_config  # noqa: E402
from onejev_decide.client import wait_ready  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="onejev-decide — single image")
    p.add_argument("image", type=Path)
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--server", default=None)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    if not args.image.is_file():
        raise SystemExit(f"image not found: {args.image}")

    cfg = reload_config(args.config)
    server = args.server or cfg["model"]["server_url"]
    try:
        wait_ready(server)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"server unreachable at {server}\n({exc})") from exc

    t0 = time.perf_counter()
    row = decide(args.image.resolve(), base_url=server, config=cfg)
    row["seconds"] = round(time.perf_counter() - t0, 2)
    print(json.dumps(row, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
