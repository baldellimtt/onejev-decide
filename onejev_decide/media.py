from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

from .config import get_config


def _prep_image(path: Path) -> bytes:
    inf = get_config().get("inference") or {}
    max_side = int(inf.get("max_image_side", 320))
    quality = int(inf.get("jpeg_quality", 75))

    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BILINEAR)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def media_item(path: Path) -> dict:
    return {
        "type": "image",
        "data": f"data:image/jpeg;base64,{base64.b64encode(_prep_image(path)).decode('ascii')}",
    }
