"""Milestone assignment policy: select existing titles and never invent one."""

from __future__ import annotations

from typing import Any


def resolve(requested: str | None, existing: list[str]) -> dict[str, Any]:
    """Resolve a requested milestone against the repo's existing milestone titles.

    The skill must never invent a milestone. This guard assigns only when the
    requested title exactly matches one the repository already has; otherwise it
    leaves the issue unassigned and says so, so the agent cannot silently create
    a fake milestone.
    """
    existing_titles = [title for title in existing if title]
    requested_title = (requested or "").strip()
    if not requested_title:
        return {
            "ok": True,
            "assignable": False,
            "milestone": None,
            "action": "leave-unassigned",
            "reason": "no milestone requested",
            "existing": existing_titles,
        }
    if requested_title in existing_titles:
        return {
            "ok": True,
            "assignable": True,
            "milestone": requested_title,
            "action": "assign",
            "reason": f"`{requested_title}` is an existing repository milestone",
            "existing": existing_titles,
        }
    return {
        "ok": True,
        "assignable": False,
        "milestone": None,
        "action": "leave-unassigned",
        "reason": (
            f"no existing repository milestone titled `{requested_title}`; "
            "not creating a new one — state this explicitly to the operator"
        ),
        "existing": existing_titles,
    }
