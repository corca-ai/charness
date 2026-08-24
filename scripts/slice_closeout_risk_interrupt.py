#!/usr/bin/env python3
"""Closeout policy for interpreting a path-bound risk-interrupt plan."""

from __future__ import annotations


def initial_paths(
    repo_root,
    *,
    campaign_base_sha,
    base,
    collect_live,
    collect_since_base,
    collect_since_resolved_base,
) -> list[str]:
    """Select Git-observed risk provenance without consulting caller --paths."""
    if campaign_base_sha:
        return collect_since_resolved_base(repo_root, campaign_base_sha)
    if base is not None:
        return collect_since_base(repo_root, base)
    return collect_live(repo_root)


def observe_initial_paths(*, observation_error, **kwargs) -> dict[str, object]:
    """Keep Git-observation failure distinct from an observed empty path set."""
    try:
        paths = initial_paths(**kwargs)
    except observation_error as exc:
        return {"status": "unavailable", "paths": None, "reason": str(exc)}
    return {"status": "observed", "paths": paths, "reason": None}


def observe_final_paths(
    repo_root,
    *,
    initial_observation: dict[str, object],
    collect_live,
    observation_error,
) -> dict[str, object]:
    """Re-observe after closeout mutations; unavailable means global/fail-closed."""
    try:
        live_paths = collect_live(repo_root)
    except observation_error as exc:
        return {"status": "unavailable", "paths": None, "reason": str(exc)}
    initial_paths_value = initial_observation.get("paths")
    initial = initial_paths_value if isinstance(initial_paths_value, list) else []
    paths = sorted(dict.fromkeys([*initial, *live_paths]))
    return {"status": "observed", "paths": paths, "reason": None}


def block_reason(plan: object) -> str | None:
    if not isinstance(plan, dict):
        return "risk interrupt planner returned malformed output"
    if plan.get("status") == "not-applicable" and plan.get("required") is False:
        return None
    if (
        plan.get("status") == "handoff-recorded"
        and plan.get("required") is True
        and plan.get("impl_status") == "allowed"
        and plan.get("chosen_next_step") == "impl"
    ):
        return None
    if plan.get("status") == "not-applicable":
        return "risk interrupt planner returned not-applicable without required:false"
    if plan.get("status") == "handoff-recorded":
        return "risk interrupt planner returned a handoff without a valid impl permission"
    return f"risk interrupt planner returned unknown or blocked status={plan.get('status')!r}"
