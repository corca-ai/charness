"""Lane payload phase, timing, and persistence helpers."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_support as _support  # noqa: E402


def _mark_phase(payload: dict[str, Any], phase: str, stamp: str) -> float:
    """Enter a phase: record its UTC start and return the monotonic origin."""
    payload["phase"] = phase
    payload["timestamps"][stamp] = _support.utc_now_iso()
    return time.monotonic()


def _record_timing(payload: dict[str, Any], key: str, origin: float) -> None:
    payload["timings_ms"][key] = int((time.monotonic() - origin) * 1000)


def _persist(payload: dict[str, Any], runtime_path: Path) -> None:
    stamps = payload.setdefault("timestamps", {})
    stamps["updated_at"] = _support.utc_now_iso()
    if payload.get("phase") == "terminal":
        stamps["finished_at"] = stamps["updated_at"]
    _support.write_task_result(runtime_path, payload)


def _persist_completion(payload: dict[str, Any], runtime_path: Path) -> None:
    candidate = payload.get("candidate")
    persist_status = (
        candidate.get("persist", {}).get("status") if isinstance(candidate, dict) else None
    )
    if (
        payload.get("status") == "completed"
        and isinstance(candidate, dict)
        and candidate.get("status") == "validated"
        and persist_status != "committed"
        and not candidate.get("head_is_complete", True)
    ):
        if candidate.get("carrier_kind") == "worktree-only":
            payload["next_step"] = (
                f"Review the complete validated candidate in {payload['worktree_path']}; "
                "no lane commit exists, so lane HEAD is not the complete candidate."
            )
        else:
            payload["next_step"] = (
                f"Review the complete validated candidate in {payload['worktree_path']}; "
                "the lane HEAD commit is a proper subset of the complete candidate. "
                "Carry the committed_paths and dirty_paths before treating it as integrated."
            )
    _persist(payload, runtime_path)
