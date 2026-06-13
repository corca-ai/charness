#!/usr/bin/env python3
"""Closeout-telemetry emitter (spec achieve-efficiency-improvements, direction E1).

Persist the OBJECTIVE operational-waste signals the slice closeout already
computes into a durable, accumulating, per-repo stream — a *sibling* of the
usage-episode stream (``scripts/slice_closeout_usage_episode.py``), NOT the
product-success episode. Keeping the two streams separate keeps the #184
product-review consumers clean: usage episodes answer "did the user get value",
this stream answers "did the run waste effort" (slow-by-design gates,
over-slicing churn). The weekly retro miner
(``skills/public/retro/scripts/mine_closeout_telemetry.py``, direction E2a)
reads the same default path.

Signals are REUSED, not recomputed: ``gate_runtime`` is C's
``gate_runtime_advisory`` verdict taken straight off the closeout payload, and
``over_slice`` calls ``slice_closeout_advisories.over_slice_run`` — the same one
computation B's advisory prints. ``slice_churn`` is the only new signal.

Robustness mirrors the usage-episode emitter: NEVER block or fail closeout
(degrade silently), suppress under ``CHARNESS_QUALITY_MODE`` so a closeout
spawned inside a quality/verification run cannot race the test suite (the #194
state-bleed class), and write only under the gitignored ``.charness/`` tree.

Unlike usage episodes (opt-in via an adapter), this stream is ON by default:
the Problem-5 fix is precisely that operational waste must accumulate WITHOUT a
human first noticing and opting in. Set ``CHARNESS_CLOSEOUT_TELEMETRY=off`` to
disable; ``CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB`` tunes rotation (default 5).
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from runtime_bootstrap import import_repo_module

# Sibling of .charness/usage-episodes/usage_episode.jsonl; the whole
# .charness/usage-episodes/ tree is already gitignored, so the stream is
# per-repo local. Keep this literal in sync with the retro miner default.
CLOSEOUT_TELEMETRY_DEFAULT_PATH = Path(".charness/usage-episodes/closeout_telemetry.jsonl")
TELEMETRY_DISABLE_VALUES = {"0", "off", "false", "no"}
DEFAULT_TELEMETRY_MAX_MB = 5
SLICE_CHURN_BASE = "origin/main"


def _telemetry_disabled() -> bool:
    raw = os.environ.get("CHARNESS_CLOSEOUT_TELEMETRY")
    return raw is not None and raw.strip().lower() in TELEMETRY_DISABLE_VALUES


def _resolve_max_mb() -> int:
    raw = os.environ.get("CHARNESS_CLOSEOUT_TELEMETRY_MAX_MB")
    if raw is None:
        return DEFAULT_TELEMETRY_MAX_MB
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_TELEMETRY_MAX_MB


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _slice_commit_path_lists(repo_root: Path, base: str = SLICE_CHURN_BASE) -> list[list[str]]:
    """Per-commit changed-path lists for the current slice (the unpushed
    ``base..HEAD`` range), most-recent-first. Degrades to ``[]`` when the base ref
    does not resolve (no upstream) or any git command fails. Mirrors the
    returncode-only guard of ``slice_closeout_advisories._recent_commit_path_lists``
    (the closeout context is always a real git repo)."""
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base],
        cwd=repo_root,
        capture_output=True,
    )
    if probe.returncode != 0:
        return []
    log = subprocess.run(
        ["git", "log", f"{base}..HEAD", "--format=%H"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if log.returncode != 0:
        return []
    result: list[list[str]] = []
    for sha in log.stdout.split():
        show = subprocess.run(
            ["git", "show", "--pretty=format:", "--name-only", sha],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if show.returncode != 0:
            break
        result.append([line for line in show.stdout.splitlines() if line.strip()])
    return result


def _slice_churn(repo_root: Path) -> dict[str, object]:
    """Commit churn over the current slice (unpushed ``origin/main..HEAD``): how
    many commits it spans, how many are ``charness-artifacts/``-only, and the
    ratio. A high artifact-only ratio is the over-slicing signal B flags, recorded
    here as a continuous number rather than a single fired/silent advisory. Uses
    the same artifact-only predicate as B; degrades to zeros when no slice range
    resolves.

    Window note: this is the FULL unbounded slice range, deliberately distinct
    from the sibling ``over_slice`` field, which reuses B's bounded trailing run
    (capped at ``threshold + 1`` commits). So ``over_slice.trailing_artifact_only_run``
    can read smaller than ``slice_churn.commits`` on a long slice — two different
    questions (is-this-churn-now vs how-big-is-the-slice), not a drift."""
    lists = _slice_commit_path_lists(repo_root)
    commits = len(lists)
    artifact_only = sum(
        1
        for paths in lists
        if paths and all(p.startswith("charness-artifacts/") for p in paths)
    )
    ratio = round(artifact_only / commits, 3) if commits else 0.0
    return {
        "base": SLICE_CHURN_BASE,
        "commits": commits,
        "artifact_only_commits": artifact_only,
        "artifact_only_ratio": ratio,
    }


def build_closeout_telemetry_record(repo_root: Path, payload: dict[str, object]) -> dict[str, object]:
    """The durable telemetry record for one closeout. ``gate_runtime`` and
    ``over_slice`` reuse C's and B's existing computations so the stream cannot
    drift from what the advisories reported; ``slice_churn`` is the new signal.
    Fields are always present (empty/zero, never absent) so the weekly miner can
    aggregate without per-record key guards."""
    advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
    gate_runtime = payload.get("gate_runtime_advisory") or {"budget_seconds": None, "over_budget": []}
    run, threshold = advisories.over_slice_run(repo_root)
    return {
        "schema_version": 1,
        "event_type": "closeout_telemetry",
        "timestamp": _timestamp(),
        "status": str(payload.get("status") or "unknown"),
        "gate_runtime": gate_runtime,
        "over_slice": {
            "trailing_artifact_only_run": run,
            "threshold": threshold,
            "over": run >= threshold,
        },
        "slice_churn": _slice_churn(repo_root),
    }


def _rotate(records_path: Path, pending_bytes: int) -> None:
    """Single-backup size rotation reusing the usage-episode rotation helper so
    the stream stays bounded without an adapter file (telemetry is on by
    default)."""
    if not records_path.exists():
        return
    usage = import_repo_module(__file__, "scripts.slice_closeout_usage_episode")
    usage._rotate_usage_episode_records(
        records_path,
        {"max_size_mb": _resolve_max_mb(), "max_files": 2},
        pending_bytes,
    )


def emit_closeout_telemetry_for_slice(repo_root: Path, payload: dict[str, object]) -> dict[str, object]:
    """Append one closeout-telemetry record. Returns a status dict (mirrors the
    usage-episode emitter) and never raises — closeout must not fail on telemetry.
    Suppressed under CHARNESS_QUALITY_MODE and the disable knob; writes only under
    the gitignored .charness/ tree."""
    import json

    quality_mode = os.environ.get("CHARNESS_QUALITY_MODE")
    if quality_mode:
        return {"status": "readonly_quality_run", "emitted": False, "quality_mode": quality_mode}
    if _telemetry_disabled():
        return {"status": "disabled", "emitted": False}

    records_path = (repo_root / CLOSEOUT_TELEMETRY_DEFAULT_PATH).resolve()
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        return {
            "status": "invalid_records_path",
            "emitted": False,
            "records_path": _portable_path(repo_root, records_path),
        }

    try:
        record = build_closeout_telemetry_record(repo_root, payload)
        serialized = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        records_path.parent.mkdir(parents=True, exist_ok=True)
        _rotate(records_path, len(serialized.encode("utf-8")))
        with records_path.open("a", encoding="utf-8") as handle:
            handle.write(serialized)
    except Exception as exc:  # pragma: no cover - exercised through CLI behavior
        return {
            "status": "emit_failed",
            "emitted": False,
            "records_path": _portable_path(repo_root, records_path),
            "error": f"closeout telemetry emission failed: {exc.__class__.__name__}",
        }

    return {
        "status": "emitted",
        "emitted": True,
        "records_path": _portable_path(repo_root, records_path),
        "record": record,
    }
