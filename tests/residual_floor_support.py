"""Actionable diagnostics for the live evidence-residual floor.

Unlike the retired inventory probe-drift message, this helper has live callers:
the residual gate pins a current invariant and must tell an operator whether the
invariant, the rule, or the recorded file itself is wrong.
"""
from __future__ import annotations

RESIDUAL_PROBE = "charness-artifacts/probe/2026-08-01-evidence-residual-floor.json"
RESIDUAL_COMMAND = "python3 scripts/gates/measure_evidence_residual.py --repo-root ."
RESIDUAL_RECORD_COMMAND = (
    f"{RESIDUAL_COMMAND}"
    " | python3 -c 'import json,sys,yaml; json.dump(yaml.safe_load(sys.stdin), sys.stdout,"
    " indent=2, sort_keys=True); print()'"
    f" > {RESIDUAL_PROBE}"
)
RESIDUAL_MEASURE_SCRIPT = "scripts/gates/measure_evidence_residual.py"
RESIDUAL_FLOOR_HOME = "scripts/gates/check_prescribed_skill_executed_lib.py"
RESIDUAL_FLOOR_SYMBOL = "MIN_BOUND_RESIDUAL_CHARS"
RESIDUAL_FLOOR_MIRROR = "plugins/charness/scripts/check_prescribed_skill_executed_lib.py"
MIRROR_SYNC_COMMAND = "python3 scripts/plugin_export/sync_root_plugin_manifests.py"

RESIDUAL_UPDATE_SURFACES: tuple[tuple[str, str | None], ...] = (
    (
        f"{RESIDUAL_PROBE} — the whole file; it has NO `_provenance`. The command output is YAML,"
        " so use RESIDUAL_RECORD_COMMAND rather than a straight redirect into this JSON file",
        RESIDUAL_RECORD_COMMAND,
    ),
    (
        f"{RESIDUAL_FLOOR_HOME} — the floor rationale transcribes the per-kind minimums and counts",
        None,
    ),
    (
        f"{RESIDUAL_FLOOR_MIRROR} — the GENERATED mirror; regenerate rather than hand-editing",
        MIRROR_SYNC_COMMAND,
    ),
)


def _render_surfaces(surfaces: tuple[tuple[str, str | None], ...]) -> list[str]:
    lines: list[str] = []
    for surface, command in surfaces:
        lines.append(f"  - {surface}")
        lines.append(f"      run: {command}" if command is not None else "      edit by hand")
    return lines


def residual_floor_message(
    key: str, *, kind: str | None = None, recorded_only: bool = False
) -> str:
    """Explain a residual-floor failure without laundering it as probe drift."""
    where = f"`{key}` for kind `{kind}`" if kind else f"`{key}`"
    which_kind = f"for the kind `{kind}`" if kind else "for each kind"
    if recorded_only:
        return "\n".join(
            [
                f"{where} is inconsistent WITHIN the recorded probe {RESIDUAL_PROBE}.",
                "",
                "Both sides come from the checked-in file. Nothing live took part, so this is",
                "not drift and rerunning the measurement will not explain the inconsistency.",
                "Do not re-record over it; determine whether it was hand-edited or captured an",
                f"already-broken invariant, then use `{RESIDUAL_COMMAND}` deliberately.",
            ]
        )
    return "\n".join(
        [
            f"{where} no longer matches the recorded measurement in {RESIDUAL_PROBE}.",
            "",
            "This site does NOT pin counts, so this is not the usual re-record.",
            "",
            "1. THE INVARIANT BROKE — a measured minimum is no longer strictly above the floor.",
            "   This is a finding. Do NOT lower the floor and do NOT re-record. Run",
            f"   `{RESIDUAL_COMMAND}` and read `min_residual_path` {which_kind}.",
            "   Also check `corpus_established`; an empty corpus proves nothing.",
            "",
            "2. THE FLOOR MOVED — the recorded floor no longer equals the live rule.",
            f"   `{RESIDUAL_FLOOR_SYMBOL}` lives in {RESIDUAL_FLOOR_HOME}, NOT in",
            f"   `{RESIDUAL_MEASURE_SCRIPT}`. Establish the new rule before recording it.",
            "",
            "Per-kind `kinds[*].files` counts are deliberately not pinned; corpus growth is normal.",
            "To re-record case 2, update every figure-bearing surface:",
            *_render_surfaces(RESIDUAL_UPDATE_SURFACES),
        ]
    )
