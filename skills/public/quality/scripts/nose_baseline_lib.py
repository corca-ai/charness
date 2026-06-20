#!/usr/bin/env python3
"""Id-set drift baseline I/O for the nose clone advisory.

Split out of `inventory_nose_clones.py` so that entrypoint stays under its length
cap: accepting the intentional/portability clone mass so the advisory reports only
new/changed drift is its own concern.

nose 0.13.3 removed `nose scan`; the advisory now runs `nose query` (see
`nose_report_lib`). nose's native `--baseline`/`--write-baseline` is unusable for a
multi-root scope: `query` takes one path root per call and `--write-baseline`
CLOBBERS the target file on each run (so the three scope roots cannot share one
baseline), and it keys on the churn-prone cluster `key`, not the content-hash
`family_id`. (The advisory uses `family_id` for those plumbing reasons, NOT for
churn-stability: `family_id` also rotates an unchanged copy's id whenever any member
is edited — demonstrated for content/line-offset/file-path shifts, and by construction
for a membership change — so it is not "stable across sibling churn" either. The advisory is non-blocking, so a rotated id only adds
advisory drift, never a hard block; the blocking dup-ratchet gate owns the re-baseline
discipline. See `dup_ratchet_lib`.) So the
advisory keeps its own id-set drift baseline here — a sorted `code_family_ids`
snapshot, symmetric with the dup-ratchet gate baseline and the doc signature
baseline — and filters via a pure set-diff in `inventory_nose_clones`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

# Canonical standing baseline of already-accepted (intentional/portability) clone
# family_ids. When present, the advisory reads it by default so it surfaces only
# NEW/changed duplication (drift) rather than re-flagging deliberate per-skill
# bootstrap boilerplate every run. Re-baseline per scanner version with
# --write-baseline (see the advisory-interpretation contract).
DEFAULT_BASELINE_REL = "charness-artifacts/quality/nose-baseline.json"
BASELINE_SCHEMA_VERSION = "charness.quality.nose_baseline.v2"
BASELINE_NOTE = (
    "Accepted (intentional/portability) code clone family_ids so the advisory "
    "reports only new/changed drift. Keyed by nose family_id (16-hex content hash) "
    "from a full `nose query` over the scanned roots — NOT nose's cluster key/--baseline "
    "(plumbing reasons; see nose_baseline_lib docstring). family_id is NOT churn-stable: "
    "any member edit (content, line offset, file path — and, by construction, membership) "
    "rotates it. The "
    "advisory is non-blocking, so re-baseline per scanner version (and when ids rotate) "
    "with --write-baseline; never treat the accepted count as a reduction target (see item 5 review). "
    "The baseline stamps the producing nose tool_version; the read path warns when the live "
    "scanner version differs so a silent bump reads as re-baseline, not a flood of false drift."
)


def resolve_baseline(*, write_baseline: bool, baseline: str | None, repo_root: Path) -> str | None:
    """Resolve the baseline path (relative to repo root).

    Write mode falls back to the canonical default so re-baselining is a flagless
    `--write-baseline`. Read mode uses an explicit `--baseline`, else the canonical
    default only when it already exists (so a fresh repo stays un-baselined rather
    than erroring on a missing file).
    """
    if write_baseline:
        return baseline or DEFAULT_BASELINE_REL
    if baseline:
        return baseline
    if (repo_root / DEFAULT_BASELINE_REL).is_file():
        return DEFAULT_BASELINE_REL
    return None


def load_baseline_ids(repo_root: Path, baseline_rel: str | None) -> set[str] | None:
    """Accepted family_id set, or ``None`` when the baseline is absent / unreadable
    / not an id-set (the advisory then reports all families as drift). A legacy
    cluster-key baseline (pre-migration ``[{key, ...}]``) carries no
    ``code_family_ids`` and so reads as ``None`` — everything is drift until
    re-seeded, an honest "re-baseline needed" signal rather than a silent all-clear.
    """
    if not baseline_rel:
        return None
    path = repo_root / baseline_rel
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    ids = data.get("code_family_ids")
    if not isinstance(ids, list):
        return None
    return {str(fid) for fid in ids if isinstance(fid, str) and fid}


def load_baseline_tool_version(repo_root: Path, baseline_rel: str | None) -> str:
    """The nose version stamped into the baseline on its last ``--write-baseline``,
    or ``""`` when absent/legacy/unreadable. The advisory compares it against the
    live scanner version (``nose_report.tool_version_skew``) so a silent version bump
    surfaces as "re-baseline" instead of a wall of false drift."""
    if not baseline_rel:
        return ""
    try:
        data = json.loads((repo_root / baseline_rel).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    version = data.get("tool_version") if isinstance(data, dict) else None
    return version if isinstance(version, str) else ""


def build_baseline(
    code_family_ids: Iterable[str], *, tool_version: str = "", note: str = BASELINE_NOTE
) -> dict[str, Any]:
    ids = sorted({str(fid) for fid in code_family_ids if fid})
    baseline: dict[str, Any] = {"schemaVersion": BASELINE_SCHEMA_VERSION, "note": note, "code_family_ids": ids}
    # Stamp only when known: a legacy/unknown write stays unstamped (the read path
    # treats a missing stamp as "unknown", never a false skew warning), not ``""``.
    if tool_version:
        baseline["tool_version"] = str(tool_version)
    return baseline


def write_baseline_payload(
    repo_root: Path, baseline_rel: str | None, code_family_ids: Iterable[str], roots: list[str],
    *, tool_version: str = "",
) -> dict[str, Any]:
    rel = baseline_rel or DEFAULT_BASELINE_REL
    baseline = build_baseline(code_family_ids, tool_version=tool_version)
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "status": "baseline-written",
        "advisory": True,
        "repo_root": str(repo_root),
        "paths": roots,
        "baseline": rel,
        "tool_version": tool_version,
        "code_family_count": len(baseline["code_family_ids"]),
        "notes": [
            "Baseline accepts today's intentional/portability code clone family_ids so the advisory reports only new/changed drift.",
            "Re-baseline per scanner version; never treat the accepted count as a reduction target.",
        ],
    }
