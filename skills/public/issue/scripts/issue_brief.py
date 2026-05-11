"""Pre-mutation resolution brief helpers (step 6 of `issue resolve`).

The brief contract lives in `references/resolution-brief.md`; this module
owns the runtime helpers `issue_tool.py` uses to wire it up.
"""
from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path
from typing import Any


def _load_runtime():
    path = Path(__file__).resolve().parent / "issue_runtime.py"
    spec = importlib.util.spec_from_file_location("issue_runtime", path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

BRIEF_PAUSE_VALUES = ("on-open-decisions", "always", "never")
DEFAULT_BRIEF_PAUSE = "on-open-decisions"
INVOCATION_FLAG_TO_PAUSE = {"--auto": "never", "--pause": "always"}


def extract_invocation_flags(values: list[str]) -> tuple[list[str], dict[str, Any]]:
    positional: list[str] = []
    override: str | None = None
    for value in values:
        if value in INVOCATION_FLAG_TO_PAUSE:
            mapped = INVOCATION_FLAG_TO_PAUSE[value]
            if override is not None and override != mapped:
                raise ValueError("--auto and --pause cannot be combined in one invocation")
            override = mapped
        elif value.startswith("--"):
            raise ValueError(f"unknown issue resolve flag: {value}")
        else:
            positional.append(value)
    return positional, {"brief_pause": override}


def effective_brief_pause(adapter_value: str | None, flag_override: str | None) -> str:
    for value in (flag_override, adapter_value):
        if value is None:
            continue
        if value not in BRIEF_PAUSE_VALUES:
            raise ValueError(f"feature_brief_pause must be one of: {', '.join(BRIEF_PAUSE_VALUES)}")
        return value
    return DEFAULT_BRIEF_PAUSE


def brief_artifact_relpath(issue_number: int, when: date | None = None) -> str:
    if issue_number <= 0:
        raise ValueError("issue_number must be a positive integer")
    stamp = (when or date.today()).isoformat()
    return f"charness-artifacts/issue/{stamp}-issue-{issue_number}-brief.md"


def build_brief_path_payload(repo_root: Path, issue_number: int, date_arg: str | None) -> dict[str, Any]:
    when = date.fromisoformat(date_arg) if date_arg else date.today()
    relpath = brief_artifact_relpath(issue_number, when)
    absolute = (repo_root / relpath).resolve()
    return {
        "ok": True, "issue_number": issue_number, "date": when.isoformat(),
        "relpath": relpath, "absolute": str(absolute), "exists": absolute.exists(),
    }


def build_invocation_payload(
    repo_root: Path, values: list[str], adapter: dict[str, Any], default_pause: str,
) -> dict[str, Any]:
    runtime = _load_runtime()
    positional, flags = extract_invocation_flags(values)
    target_arg, selector = runtime.split_resolve_args(positional)
    target = runtime.resolve_target(repo_root, target_arg, adapter["data"])
    numbers = runtime.parse_selector(selector)
    adapter_pause = adapter["data"].get("feature_brief_pause", default_pause)
    brief_pause = effective_brief_pause(adapter_pause, flags.get("brief_pause"))
    return {
        "ok": True, "target": target, "selector": selector, "numbers": numbers,
        "selector_source": "github-newest-open" if numbers is None else "argument",
        "invocation_flags": flags,
        "brief_pause": {
            "adapter": adapter_pause, "flag_override": flags.get("brief_pause"),
            "effective": brief_pause,
        },
        "adapter": adapter,
    }
