from __future__ import annotations

from pathlib import Path
from typing import Any

from .answers import is_alert, normalize
from .client import post_systemone, server_url
from .config import get_config
from .media import media_item
from .questions import build_questions, build_state


def decide(
    image_path: Path,
    base_url: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = config or get_config()
    model = cfg["model"]
    raw = post_systemone(
        {
            "state": build_state(cfg),
            "media": [media_item(image_path)],
            "questions": build_questions(cfg),
        },
        base_url=server_url(base_url, cfg),
        retries=int(model.get("retries", 1)),
    )
    raw_answers = raw.get("answers") or {}
    answers = {
        name: normalize(spec, raw_answers.get(name))
        for name, spec in (cfg.get("questions") or {}).items()
    }
    out: dict[str, Any] = {
        "file": str(image_path),
        "stato": "allarme" if is_alert(answers, cfg.get("thresholds")) else "ok",
        "answers": answers,
    }
    if (cfg.get("inference") or {}).get("include_raw"):
        out["raw_answers"] = raw_answers
    return out
