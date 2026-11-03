from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config.yaml"


def _resolve(root: Path, rel: str | Path) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else (root / p)


def _config_path(path: str | None = None) -> Path:
    raw = path or os.environ.get("DECISION_CONFIG")
    cfg = Path(raw) if raw else DEFAULT_CONFIG
    return cfg if cfg.is_absolute() else ROOT / cfg


@lru_cache(maxsize=4)
def load_config(path: str | None = None) -> dict[str, Any]:
    cfg_path = _config_path(path)
    with cfg_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    root = cfg_path.resolve().parent
    paths = data.setdefault("paths", {})
    for key in ("data", "normal", "incident", "outputs"):
        if key in paths:
            paths[key] = str(_resolve(root, paths[key]))
    return data


def get_config(path: str | None = None) -> dict[str, Any]:
    return load_config(path)


def reload_config(path: str | Path | None = None) -> dict[str, Any]:
    load_config.cache_clear()
    return load_config(None if path is None else str(path))


_cfg = load_config()
SERVER_URL = _cfg["model"]["server_url"]
NORMAL_DIR = Path(_cfg["paths"]["normal"])
INCIDENT_DIR = Path(_cfg["paths"]["incident"])
