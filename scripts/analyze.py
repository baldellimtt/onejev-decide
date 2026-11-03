"""Batch labeled → outputs/results.jsonl."""

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
from onejev_decide.evaluate import confusion  # noqa: E402

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def list_labeled(normal: Path, incident: Path) -> list[tuple[Path, str]]:
    rows: list[tuple[Path, str]] = []
    for folder, label in ((normal, "normal"), (incident, "incident")):
        if not folder.exists():
            continue
        for p in sorted(folder.iterdir()):
            if p.is_file() and p.suffix.lower() in EXTS:
                rows.append((p, label))
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--server", default=None)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    cfg = reload_config(args.config)
    server = args.server or cfg["model"]["server_url"]
    out = args.out or Path(cfg["paths"]["outputs"]) / "results.jsonl"
    items = list_labeled(Path(cfg["paths"]["normal"]), Path(cfg["paths"]["incident"]))
    if not items:
        raise SystemExit("no images — run: python scripts/fetch_samples.py")

    try:
        wait_ready(server)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"server unreachable at {server}\n({exc})") from exc

    out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    print(f"images={len(items)} server={server}\n")
    for path, expected in items:
        t0 = time.perf_counter()
        try:
            row = decide(path, base_url=server, config=cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"[error ] {path.name}: {exc}")
            continue
        row["expected"] = expected
        row["seconds"] = round(time.perf_counter() - t0, 2)
        results.append(row)
        a = row["answers"].get("overflow") or {}
        print(f"[{row['status']:7}] {path.name}  overflow={a.get('value')}  {row['seconds']}s  expected={expected}")

    with out.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    if results:
        print("\n", confusion(results))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
