from __future__ import annotations

from typing import Any

from .config import get_config


def build_state(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    t = (cfg or get_config())["task"]
    return {"task": t["name"], "view": t["view"]}


def build_questions(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, spec in ((cfg or get_config()).get("questions") or {}).items():
        q: dict[str, Any] = {"type": spec["type"]}
        if "instructions" in spec:
            q["instructions"] = str(spec["instructions"]).strip()
        if "criteria" in spec:
            q["criteria"] = list(spec["criteria"])
        if "choices" in spec:
            q["choices"] = list(spec["choices"])
        out[name] = q
    return out
