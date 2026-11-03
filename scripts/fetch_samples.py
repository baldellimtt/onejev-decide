"""Scarica foto sample normal vs overflowing (Wikimedia thumbnails)."""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from onejev_decide.config import INCIDENT_DIR, NORMAL_DIR  # noqa: E402

UA = "onejev-decide/0.1 (local research)"

NORMAL = [
    "Street waste container in Roncesvalles Village, August 2025 - back.jpg",
    "A very superior litter bin - geograph.org.uk - 3716714.jpg",
]

INCIDENT = [
    "Overflowing Hamburg street garbage bin.jpg",
    "Full trash bin 0001.jpg",
    "Bin overflowing with Starbucks paper cups.jpg",
    "Dont think this bin will take any more ! (6861377341).jpg",
    # pieno al limite (prima scaricato per errore come normal_02)
    "Public Litter Bin (0923) - Railway Street, Gillingham, Medway.jpg",
]


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def wiki_thumb(title: str, width: int = 1280) -> str | None:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    data = json.loads(http_get(f"https://commons.wikimedia.org/w/api.php?{params}"))
    for page in data.get("query", {}).get("pages", {}).values():
        infos = page.get("imageinfo") or []
        if infos:
            return infos[0].get("thumburl") or infos[0].get("url")
    return None


def save(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 5000:
        print(f"skip {dest.name}")
        return True
    try:
        blob = http_get(url)
        if len(blob) < 1000:
            print(f"fail {dest.name}: too small")
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        print(f"ok   {dest.name} ({len(blob) // 1024} KB)")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"fail {dest.name}: {exc}")
        return False


def pull(titles: list[str], out_dir: Path, prefix: str) -> int:
    n = 0
    for i, title in enumerate(titles, 1):
        dest = out_dir / f"{prefix}_{i:02d}.jpg"
        try:
            url = wiki_thumb(title)
            time.sleep(1.0)
        except Exception as exc:  # noqa: BLE001
            print(f"fail API {title}: {exc}")
            continue
        if not url:
            print(f"fail missing {title}")
            continue
        if save(url, dest):
            n += 1
        time.sleep(0.8)
    return n


def main() -> None:
    ok = pull(NORMAL, NORMAL_DIR, "normal") + pull(INCIDENT, INCIDENT_DIR, "incident")
    print(f"done: {ok} images")
    if ok == 0:
        raise SystemExit("Nessuna immagine. Metti JPG in data/normal e data/incident.")


if __name__ == "__main__":
    main()
