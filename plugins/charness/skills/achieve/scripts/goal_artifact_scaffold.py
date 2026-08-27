"""The single planning-record renderer used by ``upsert_goal.py``."""
from __future__ import annotations

from pathlib import Path

TEMPLATE = (Path(__file__).resolve().parent / "goal_artifact_template.md").read_text(
    encoding="utf-8"
)


def render_goal_template(
    template: str,
    *,
    title: str,
    date: str,
    goal_rel_path: str,
    goal_body: str,
) -> str:
    return template.format(
        title=title,
        date=date,
        goal_rel=goal_rel_path,
        goal_body=goal_body.strip(),
    )
