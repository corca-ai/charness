#!/usr/bin/env python3
"""Bind the retro trigger probe to the planner's actual change basis."""

from __future__ import annotations

from typing import Any


def auto_trigger_scope(work_paths: list[str], source: str) -> tuple[list[str], dict[str, Any]]:
    """Return probe arguments and receipt fields for one planner change basis.

    A clean post-commit tree has no working-tree diff, so a bare trigger command
    loses the slice exactly at closeout. The recent-commit fallback is narrowed
    to the latest committed range; explicit and working-tree inputs carry paths.
    An empty input stays basis-less and fail-closed.
    """
    if source == "recent_commits":
        return ["--base-ref", "HEAD^", "--head-ref", "HEAD"], {
            "trigger_scope": "HEAD^..HEAD",
            "trigger_scope_source": source,
        }
    if work_paths:
        return ["--paths", *work_paths], {
            "trigger_scope": list(work_paths),
            "trigger_scope_source": source,
        }
    return [], {
        "trigger_scope": [],
        "trigger_scope_source": source,
        "trigger_scope_status": "not-established",
    }
