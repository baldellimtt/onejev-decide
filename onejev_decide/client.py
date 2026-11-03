"""Persistent HTTP client to qev."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .config import SERVER_URL, get_config

_client: httpx.Client | None = None


def _http() -> httpx.Client:
    global _client
    if _client is None:
        timeout = float(get_config()["model"].get("timeout_s", 60))
        _client = httpx.Client(timeout=timeout)
    return _client


def server_url(base_url: str | None = None, cfg: dict[str, Any] | None = None) -> str:
    c = cfg or get_config()
    return (
        base_url
        or os.environ.get("DECISION_SERVER_URL")
        or c["model"].get("server_url")
        or SERVER_URL
    )


def post_systemone(
    payload: dict[str, Any],
    *,
    base_url: str,
    retries: int = 1,
    debias: int | None = None,
) -> dict[str, Any]:
    if debias is None:
        debias = int((get_config().get("inference") or {}).get("debias", 0))
    url = f"{base_url.rstrip('/')}/v1/systemone?debias={debias}"
    last_exc: Exception | None = None
    for _ in range(max(1, retries)):
        try:
            r = _http().post(url, json=payload)
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException as exc:
            last_exc = exc
    assert last_exc is not None
    raise last_exc


def wait_ready(base_url: str, timeout_s: float = 5.0) -> None:
    httpx.get(f"{base_url.rstrip('/')}/v1/models", timeout=timeout_s)


def wait_ready_loop(base_url: str, attempts: int = 90, delay_s: float = 2.0) -> None:
    import time

    last: Exception | None = None
    for _ in range(attempts):
        try:
            wait_ready(base_url, timeout_s=3.0)
            return
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(delay_s)
    raise RuntimeError(f"server not ready at {base_url}: {last}")
