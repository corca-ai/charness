"""Ingest a repo-declared command-timing log as a runtime sample source.

`render_runtime_summary` / `check_runtime_budget` read precomputed samples from
`.charness/quality/runtime-signals.json`. Many repos already emit their own
structured per-command timing log (e.g. a `command_timing.v1` JSONL written by a
pre-push runner). Without a bridge from that log into `runtime-signals.json`, the
runtime helpers report only "no samples," so the gate-cost hot-spot ranking never
appears as default skill output and the operator has to profile gates by hand.

This module lets a repo declare an existing timing log through a portable adapter
key (`command_timing_log`: a path + a field/schema mapping) so the log lights up
hot spots without each repo hand-rolling a log->signals bridge. It is **inert when
the key is absent** (stack-neutral opt-in) and **fails loud** on a misconfigured
key (the config errors ride `profile_config_errors`, which `check_runtime_budget`
already turns into a non-zero exit).

The output is the same per-label `commands` shape `runtime_budget_lib` consumes
from `runtime-signals.json`:

    {label: {"latest": {"elapsed_ms": int},
             "median_recent_elapsed_ms": int,
             "max_recent_elapsed_ms": int,
             "samples": int}}
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

from runtime_profile_lib import DEFAULT_RUNTIME_PROFILE

DEFAULT_FORMAT = "jsonl"
SUPPORTED_FORMATS = ("jsonl", "json")
DEFAULT_ELAPSED_UNIT = "ms"
# Multiplier from the source unit to milliseconds.
ELAPSED_UNIT_TO_MS: dict[str, float] = {
    "ms": 1.0,
    "millis": 1.0,
    "milliseconds": 1.0,
    "s": 1000.0,
    "sec": 1000.0,
    "secs": 1000.0,
    "seconds": 1000.0,
    "us": 0.001,
    "microseconds": 0.001,
    "ns": 1e-6,
    "nanoseconds": 1e-6,
}
DEFAULT_RECENT_WINDOW = 10


def _inert(configured: bool, errors: list[str] | None = None, path: str | None = None) -> dict[str, Any]:
    return {
        "configured": configured,
        "errors": errors or [],
        "path": path,
        "file_present": False,
        "samples_total": 0,
        "commands": {},
    }


def _validate_config(config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return (parsed, errors). Parsed is only trustworthy when errors is empty."""
    errors: list[str] = []
    path_value = config.get("path")
    if not isinstance(path_value, str) or not path_value:
        errors.append("command_timing_log.path must be a non-empty string")

    fmt = config.get("format", DEFAULT_FORMAT)
    if fmt not in SUPPORTED_FORMATS:
        errors.append(f"command_timing_log.format must be one of {list(SUPPORTED_FORMATS)}")

    field_map = config.get("field_map")
    label_field = elapsed_field = profile_field = None
    if not isinstance(field_map, dict):
        errors.append("command_timing_log.field_map must be a mapping naming at least `label` and `elapsed`")
    else:
        label_field = field_map.get("label")
        elapsed_field = field_map.get("elapsed")
        profile_field = field_map.get("profile")
        if not isinstance(label_field, str) or not label_field:
            errors.append("command_timing_log.field_map.label must name the log's command/label field")
        if not isinstance(elapsed_field, str) or not elapsed_field:
            errors.append("command_timing_log.field_map.elapsed must name the log's elapsed-time field")
        if profile_field is not None and (not isinstance(profile_field, str) or not profile_field):
            errors.append("command_timing_log.field_map.profile, when set, must be a non-empty string")

    unit = config.get("elapsed_unit", DEFAULT_ELAPSED_UNIT)
    if unit not in ELAPSED_UNIT_TO_MS:
        errors.append(f"command_timing_log.elapsed_unit must be one of {sorted(ELAPSED_UNIT_TO_MS)}")

    window = config.get("recent_window", DEFAULT_RECENT_WINDOW)
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        errors.append("command_timing_log.recent_window must be a positive integer")
        window = DEFAULT_RECENT_WINDOW

    parsed = {
        "path": path_value if isinstance(path_value, str) else None,
        "format": fmt,
        "label_field": label_field,
        "elapsed_field": elapsed_field,
        "profile_field": profile_field,
        "unit": unit,
        "window": window,
    }
    return parsed, errors


def _read_records(log_path: Path, fmt: str) -> list[dict[str, Any]]:
    text = log_path.read_text(encoding="utf-8")
    records: list[dict[str, Any]] = []
    if fmt == "json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return []
        if isinstance(payload, list):
            records = [item for item in payload if isinstance(item, dict)]
        return records
    # jsonl: one JSON object per line; skip blank or malformed lines so a partial
    # trailing write never crashes the ingest.
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            item = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def _coerce_elapsed_ms(value: Any, unit_multiplier: float) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value < 0:
        return None
    return int(round(value * unit_multiplier))


def _aggregate(samples_by_label: dict[str, list[int]], window: int) -> dict[str, Any]:
    commands: dict[str, Any] = {}
    for label, samples in samples_by_label.items():
        if not samples:
            continue
        recent = samples[-window:]
        commands[label] = {
            "latest": {"elapsed_ms": samples[-1]},
            "median_recent_elapsed_ms": int(round(median(recent))),
            "max_recent_elapsed_ms": max(recent),
            "samples": len(samples),
        }
    return commands


def evaluate_timing_log(
    repo_root: Path,
    adapter_data: dict[str, Any],
    selected_profile: str,
) -> dict[str, Any]:
    """Derive a `commands`-shaped sample source from a repo-declared timing log.

    Inert ({} commands, no errors) when `command_timing_log` is absent/empty.

    Two failure boundaries, deliberately split:
    - **config-shape** problems (bad path/field_map/elapsed_unit/recent_window)
      are returned as `errors` so the caller can fail loud (they ride
      `profile_config_errors` → `check_runtime_budget` exits non-zero).
    - **data-shape** problems are soft (no samples, no error), mirroring an absent
      `runtime-signals.json`: a configured-but-missing log file, a malformed/non-list
      `json` payload, malformed `jsonl` lines, and records with a missing/non-string
      label or missing/negative/non-numeric elapsed are dropped rather than failing
      the run. The log may simply not have been written yet or carry a partial trailing
      write; the render layer reports "no usable samples" so a green run is not silently
      treated as a clean cost signal.
    """
    config = adapter_data.get("command_timing_log")
    if not config:
        return _inert(configured=False)
    if not isinstance(config, dict):
        return _inert(configured=True, errors=["command_timing_log must be a mapping"])

    parsed, errors = _validate_config(config)
    if errors:
        return _inert(configured=True, errors=errors, path=parsed.get("path"))

    rel_path = parsed["path"]
    log_path = repo_root / rel_path
    if not log_path.is_file():
        result = _inert(configured=True, path=rel_path)
        return result

    records = _read_records(log_path, parsed["format"])
    unit_multiplier = ELAPSED_UNIT_TO_MS[parsed["unit"]]
    label_field = parsed["label_field"]
    elapsed_field = parsed["elapsed_field"]
    profile_field = parsed["profile_field"]

    samples_by_label: dict[str, list[int]] = {}
    samples_total = 0
    for record in records:
        # When a profile field is declared, only entries for the selected profile
        # count (a multi-runner log). The literal "default" machine-auto profile
        # is not a stored profile value, so it matches all entries.
        if profile_field and selected_profile != DEFAULT_RUNTIME_PROFILE:
            if str(record.get(profile_field)) != selected_profile:
                continue
        label = record.get(label_field)
        if not isinstance(label, str) or not label:
            continue
        elapsed_ms = _coerce_elapsed_ms(record.get(elapsed_field), unit_multiplier)
        if elapsed_ms is None:
            continue
        samples_by_label.setdefault(label, []).append(elapsed_ms)
        samples_total += 1

    commands = _aggregate(samples_by_label, parsed["window"])
    return {
        "configured": True,
        "errors": [],
        "path": rel_path,
        "file_present": True,
        "samples_total": samples_total,
        "recent_window": parsed["window"],
        "commands": commands,
    }
