"""Post-boot warmup: avoid cold-start on the first user inference."""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image

from .client import server_url, wait_ready_loop
from .config import get_config
from .decide import decide


def _warmup_image() -> Path:
    path = Path(__file__).resolve().parent / "assets" / "warmup.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size < 100:
        Image.new("RGB", (64, 64), (90, 90, 90)).save(path, format="JPEG", quality=70)
    return path


def run(base_url: str | None = None) -> float:
    cfg = get_config()
    url = server_url(base_url, cfg)
    wait_ready_loop(url)
    t0 = time.perf_counter()
    decide(_warmup_image(), base_url=url, config=cfg)
    return round(time.perf_counter() - t0, 2)


def main() -> None:
    sec = run()
    print(f"warmup ok in {sec}s")


if __name__ == "__main__":
    main()
