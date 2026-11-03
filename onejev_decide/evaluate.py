from __future__ import annotations

from typing import Iterable


def confusion(rows: Iterable[dict]) -> dict[str, int]:
    tp = fp = tn = fn = 0
    for r in rows:
        pred = r.get("status") == "alarm"
        truth = r.get("expected") == "incident"
        if pred and truth:
            tp += 1
        elif pred and not truth:
            fp += 1
        elif not pred and not truth:
            tn += 1
        else:
            fn += 1
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn}
