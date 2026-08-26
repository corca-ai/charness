"""Strict JSON and pagination decoding for issue-provider reads."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_json_pages_backend")
run_backend = BACKEND.run_backend


def _run_json(argv: list[str], *, context: str) -> Any:
    result = run_backend(argv)
    if result.returncode != 0:
        raise RuntimeError(
            f"{context} failed: exit={result.returncode} stderr={result.stderr.strip()!r}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{context} returned invalid JSON: {exc}") from exc


def _flatten_pages(payload: Any) -> list[Any]:
    if not isinstance(payload, list):
        raise RuntimeError("sub-issue readback returned a non-list JSON payload")
    if payload and all(isinstance(page, list) for page in payload):
        return [item for page in payload for item in page]
    return payload


run_json = _run_json
flatten_pages = _flatten_pages
