#!/usr/bin/env python3
"""Verbatim-named public-skill recommendations for the task-text route.

Without this, the task-text recommendation payload was structurally blind to
the public-skill layer: only support skills, integrations, and the two
hardcoded worktree workflows could ever match, so an agent that named a public
skill verbatim still saw an empty result and drifted to a tool or raw shell
(#220).
"""
from __future__ import annotations

import re
from typing import Any


def _task_text_token_matches(task_text: str, candidate: str) -> bool:
    """Token-bounded match for public-skill trigger phrases.

    Public-skill names are short and collision-prone as raw substrings (`impl`
    inside `simple`/`implement`, `spec` inside `respect`/`specs`). A Unicode word
    boundary keeps the "named verbatim" signal high precision and avoids the
    broad-match over-trigger that #108/#139 fought. `\b` (not ASCII-only
    lookarounds) is required so a CJK letter glued to the name — e.g. `hitl스킬`
    — is treated as a non-boundary and does not false-match, since Korean is a
    first-class trigger language here.
    """

    normalized = candidate.casefold().strip()
    if not normalized:
        return False
    pattern = rf"\b{re.escape(normalized)}\b"
    return re.search(pattern, task_text.casefold()) is not None


def public_skill_recommendations_for_task(
    task_text: str,
    *,
    public_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for entry in public_entries:
        triggers = [t for t in entry.get("trigger_phrases", []) if isinstance(t, str) and t]
        matched = [trigger for trigger in triggers if _task_text_token_matches(task_text, trigger)]
        if not matched:
            continue
        recommendations.append(
            {
                "id": entry["id"],
                "layer": entry["layer"],
                "path": entry.get("canonical_path") or entry.get("path"),
                "summary": entry["summary"],
                "matched_triggers": matched,
                "referenced_paths": entry.get("referenced_paths", []),
                "next_step": (
                    f"Invoke the `{entry['id']}` public skill (the task names it verbatim) "
                    "before routing to an external tool or raw shell."
                ),
            }
        )
    return recommendations
