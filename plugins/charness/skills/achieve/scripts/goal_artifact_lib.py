"""Conservative markdown helpers for achieve goal artifacts.

A goal artifact lives at ``charness-artifacts/goals/<yyyy-mm-dd-slug>.md`` and is
the living scratchpad for one autonomous goal run. These helpers scaffold the
artifact, append slice reports, and check the artifact shape without churning
manual content.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

GOAL_DIR = "charness-artifacts/goals"
VALID_STATUSES = ("draft", "active", "blocked", "complete")

# H2 sections every goal artifact must keep so a compacted run can be audited
# from one file.
REQUIRED_SECTIONS = (
    "Goal",
    "Non-Goals",
    "Boundaries",
    "User Acceptance",
    "Agent Verification Plan",
    "Slice Plan",
    "Slice Log",
    "Off-Goal Findings",
    "Final Verification",
    "User Verification Instructions",
    "Auto-Retro",
)

_SLICE_HEADING = re.compile(r"^### Slice (\d+):", re.MULTILINE)
_STATUS_LINE = re.compile(r"^Status:\s*(.+?)\s*$", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)\s*$", re.MULTILINE)

_TEMPLATE = """# Achieve Goal: {title}

Status: {status}
Created: {date}
Activation: `/goal @{goal_rel}`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

{goal_body}

## Non-Goals

## Boundaries

## User Acceptance

What the user can do to verify completion directly.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Slice Log

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "goal"


def goal_path(repo_root: Path, date: str, slug: str) -> Path:
    return repo_root / GOAL_DIR / f"{date}-{slugify(slug)}.md"


def goal_rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def render_template(*, title: str, date: str, status: str, goal_rel_path: str, goal_body: str) -> str:
    return _TEMPLATE.format(
        title=title,
        date=date,
        status=status,
        goal_rel=goal_rel_path,
        goal_body=goal_body.strip() or "_State the desired outcome before activation._",
    )


def set_status(text: str, status: str) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}; expected one of {VALID_STATUSES}")
    if not _STATUS_LINE.search(text):
        raise ValueError("artifact has no `Status:` line to update")
    return _STATUS_LINE.sub(f"Status: {status}", text, count=1)


def read_status(text: str) -> str | None:
    match = _STATUS_LINE.search(text)
    return match.group(1).strip() if match else None


def upsert_goal(
    repo_root: Path,
    *,
    date: str,
    slug: str,
    title: str,
    status: str = "draft",
    goal_body: str = "",
) -> dict[str, Any]:
    """Create the goal artifact when missing, else update only its status.

    Returns a structured result. An existing artifact is never overwritten; only
    the ``Status:`` line is touched, and only when the value actually changes.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}; expected one of {VALID_STATUSES}")
    path = goal_path(repo_root, date, slug)
    rel = goal_rel(repo_root, path)
    if path.exists():
        original = path.read_text(encoding="utf-8")
        updated = set_status(original, status)
        changed = updated != original
        if changed:
            path.write_text(updated, encoding="utf-8")
        return {"action": "updated" if changed else "unchanged", "path": rel, "status": status}
    path.parent.mkdir(parents=True, exist_ok=True)
    body = render_template(
        title=title,
        date=date,
        status=status,
        goal_rel_path=rel,
        goal_body=goal_body,
    )
    path.write_text(body, encoding="utf-8")
    return {"action": "created", "path": rel, "status": status}


def next_slice_number(text: str) -> int:
    numbers = [int(match.group(1)) for match in _SLICE_HEADING.finditer(text)]
    return (max(numbers) + 1) if numbers else 1


def render_slice_block(number: int, name: str, fields: dict[str, str]) -> str:
    lines = [f"### Slice {number}: {name}", ""]
    for label in (
        "Objective",
        "Why this approach",
        "Commits",
        "What changed",
        "Alternatives rejected",
        "Targeted verification",
        "Critique",
        "Off-goal findings",
        "Lessons carried forward",
        "Metrics",
    ):
        value = fields.get(label, "").strip()
        lines.append(f"- {label}: {value}" if value else f"- {label}:")
    return "\n".join(lines) + "\n"


def append_slice(text: str, slice_block: str) -> str:
    """Insert a slice block at the end of the ``## Slice Log`` section."""
    headings = list(_H2.finditer(text))
    for index, match in enumerate(headings):
        if match.group(1).strip() != "Slice Log":
            continue
        newline = text.find("\n", match.start())
        heading_line_end = len(text) if newline == -1 else newline + 1
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        existing = text[heading_line_end:section_end].strip("\n")
        block = slice_block.strip("\n")
        body = f"{existing}\n\n{block}" if existing else block
        suffix = "\n" if section_end == len(text) else f"\n\n{text[section_end:]}"
        return f"{text[:heading_line_end]}\n{body}{suffix}"
    raise ValueError("artifact has no `## Slice Log` section")


def check_goal(text: str) -> dict[str, Any]:
    present = {match.group(1).strip() for match in _H2.finditer(text)}
    missing = [section for section in REQUIRED_SECTIONS if section not in present]
    status = read_status(text)
    issues: list[str] = []
    if status is None:
        issues.append("missing `Status:` line")
    elif status not in VALID_STATUSES:
        issues.append(f"status {status!r} is not one of {VALID_STATUSES}")
    if "Activation:" not in text:
        issues.append("missing `Activation:` line")
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    return {"ok": not issues, "status": status, "missing_sections": missing, "issues": issues}
