from __future__ import annotations

from typing import Any


def normalize(qspec: dict[str, Any], raw: Any) -> dict[str, Any]:
    qtype = qspec.get("type", "")
    ans = raw if isinstance(raw, dict) else {}
    out: dict[str, Any] = {"type": qtype}

    if qtype == "noul":
        out["value"] = float(ans.get("noul") or 0.0)
    elif qtype == "score":
        score = ans.get("score")
        probs = ans.get("probabilities") or {}
        if score is None and probs:
            vals = list(probs.values()) if isinstance(probs, dict) else list(probs)
            if vals:
                score = sum(i * float(p) for i, p in enumerate(vals))
        score_f = float(score or 0.0)
        criteria = list(qspec.get("criteria") or [])
        idx = min(max(int(round(score_f)), 0), max(len(criteria) - 1, 0)) if criteria else 0
        out["value"] = round(score_f, 4)
        if criteria:
            out["label"] = criteria[idx]
        if probs:
            out["probabilities"] = probs
    elif qtype == "choice":
        out["value"] = ans.get("choice")
        if "probabilities" in ans:
            out["probabilities"] = ans["probabilities"]
    else:
        out["value"] = ans
    return out


def is_alert(answers: dict[str, dict[str, Any]], thresholds: dict[str, Any] | None) -> bool:
    for qname, rules in (thresholds or {}).items():
        if qname not in answers or not isinstance(rules, dict):
            continue
        got = answers[qname]
        qtype, value = got.get("type"), got.get("value")
        if value is None:
            continue
        if qtype == "noul" and "noul" in rules and float(value) >= float(rules["noul"]):
            return True
        if qtype == "score" and "score" in rules and float(value) >= float(rules["score"]):
            return True
        if qtype == "choice" and "choice" in rules and value == rules["choice"]:
            return True
    return False
