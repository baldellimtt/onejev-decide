"""Playground: upload → decide."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from onejev_decide import decide, get_config, reload_config  # noqa: E402

UI_DIR = ROOT / "ui"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def create_app() -> FastAPI:
    app = FastAPI(title="onejev-decide")
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")

    @app.get("/")
    def index():
        return FileResponse(UI_DIR / "index.html")

    @app.get("/api/config")
    def api_config():
        cfg = get_config()
        samples = []
        for key, folder in (("normal", Path(cfg["paths"]["normal"])), ("incident", Path(cfg["paths"]["incident"]))):
            if not folder.exists():
                continue
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix.lower() in EXTS:
                    samples.append(
                        {"label": f"{key}/{p.name}", "name": p.name, "url": f"/api/sample/{key}/{p.name}"}
                    )
        return {
            "task": cfg.get("task"),
            "questions": cfg.get("questions"),
            "thresholds": cfg.get("thresholds"),
            "samples": samples,
        }

    @app.get("/api/sample/{split}/{name}")
    def api_sample(split: str, name: str):
        cfg = get_config()
        base = {"normal": Path(cfg["paths"]["normal"]), "incident": Path(cfg["paths"]["incident"])}.get(split)
        if base is None:
            return JSONResponse({"detail": "unknown split"}, status_code=404)
        path = (base / name).resolve()
        if not str(path).startswith(str(base.resolve())) or not path.is_file():
            return JSONResponse({"detail": "not found"}, status_code=404)
        return FileResponse(path)

    @app.post("/api/decide")
    async def api_decide(image: UploadFile = File(...), task: str = Form(""), questions: str = Form("")):
        cfg = dict(get_config())
        if task.strip():
            cfg = {**cfg, "task": {**cfg.get("task", {}), "name": task.strip()}}
        if questions.strip():
            try:
                cfg = {**cfg, "questions": json.loads(questions)}
            except json.JSONDecodeError as exc:
                return JSONResponse({"detail": f"questions JSON: {exc}"}, status_code=400)

        suffix = Path(image.filename or "upload.jpg").suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await image.read())
            tmp_path = Path(tmp.name)

        t0 = time.perf_counter()
        try:
            row = decide(tmp_path, config=cfg)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if "Connection refused" in msg or "111" in msg:
                msg += " — server not ready"
            return JSONResponse({"detail": msg}, status_code=502)
        finally:
            tmp_path.unlink(missing_ok=True)

        row["seconds"] = round(time.perf_counter() - t0, 2)
        row["file"] = image.filename or row["file"]
        return row

    return app


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7860)
    args = p.parse_args()
    cfg = reload_config(args.config)
    server = os.environ.get("DECISION_SERVER_URL") or cfg["model"]["server_url"]
    browse = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    print("")
    print("========================================")
    print(f" UI     http://{browse}:{args.port}")
    print(f" API    {server}")
    print("========================================")
    print("")
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
