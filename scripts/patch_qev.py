"""Patch qev: Q8 mmproj, low vision tokens, flash-attn, -ngl, max_pixels."""
from __future__ import annotations

import sys
from importlib.util import find_spec
from pathlib import Path


def main() -> None:
    spec = find_spec("qev.llamacpp")
    if spec is None or not spec.origin:
        raise SystemExit("qev.llamacpp not installed")
    path = Path(spec.origin)
    text = path.read_text(encoding="utf-8")

    old_proj = (
        'proj = next((f for f in projs if "f16" in f.lower()), projs[0] if projs else None)'
    )
    new_proj = (
        'proj = next((f for f in projs if "q8" in f.lower()), None) '
        'or next((f for f in projs if "f16" in f.lower()), projs[0] if projs else None)'
    )
    if old_proj in text:
        text = text.replace(old_proj, new_proj)

    text = text.replace('"--image-max-tokens", "16384"', '"--image-max-tokens", "128"')
    text = text.replace('"--image-max-tokens", "192"', '"--image-max-tokens", "128"')

    needle = "cmd += list(extra or [])"
    inject = (
        'cmd += ["-ngl", "99", "-fa", "on", '
        '"--mtmd-batch-max-tokens", "128"]\n'
        "        cmd += list(extra or [])"
    )
    if needle not in text:
        raise SystemExit(f"pattern extra args not found in {path}")
    if '"-fa", "on"' not in text:
        text = text.replace(needle, inject, 1)
    else:
        text = text.replace('"--mtmd-batch-max-tokens", "192"', '"--mtmd-batch-max-tokens", "128"')

    for old, new in (
        (
            "self.max_pixels = int(size.get(\"longest_edge\", 16777216))",
            "self.max_pixels = min(int(size.get(\"longest_edge\", 16777216)), 102400)",
        ),
        (
            "self.max_pixels = min(int(size.get(\"longest_edge\", 16777216)), 147456)",
            "self.max_pixels = min(int(size.get(\"longest_edge\", 16777216)), 102400)",
        ),
    ):
        if old in text:
            text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


if __name__ == "__main__":
    main()
    sys.exit(0)
