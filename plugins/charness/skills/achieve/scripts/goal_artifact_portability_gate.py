"""Apply the goal-path portability verdict at both achieve read boundaries."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside goal_artifact_portability_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_markdown = _load_sibling("goal_artifact_markdown")
_portability = _load_sibling("goal_path_portability")


def check(text: str) -> dict[str, Any]:
    """Read portability from the same fence-masked artifact view as other floors."""
    return _portability.check_goal_path_portability(_markdown.mask_fences(text))


def apply_pursue_floor(report: dict[str, Any], text: str) -> dict[str, Any]:
    """Make pursue readiness fail closed while preserving every existing reason."""
    portability = check(text)
    report["path_portability"] = portability
    if portability["ok"]:
        return report
    was_ready = report["pursue_ready"]
    report["pursue_ready"] = False
    report["activation_ready"] = False
    clause = "path portability floor — " + "; ".join(portability["issues"])
    report["reason"] = clause if was_ready else report["reason"] + "; " + clause
    return report


def check_issue(path_portability: dict[str, Any]) -> str | None:
    """Render the one issue line owned by the shared portability floor."""
    if path_portability["ok"]:
        return None
    return "path portability floor — " + "; ".join(path_portability["issues"])


__all__ = ["apply_pursue_floor", "check", "check_issue"]
