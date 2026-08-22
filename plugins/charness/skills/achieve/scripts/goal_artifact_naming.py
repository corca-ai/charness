"""Where a goal artifact lives, what it is called, and what values it accepts.

One concept -- naming and location -- lifted out of `goal_artifact_lib` when that
file crossed its code-line cap. The contract here is to separate a cohesive
concept rather than shave lines, and this group is cohesive on its own terms:
every function answers "what filename, and is this value safe to write into one".

The markdown facts it needs (fence balance, fence masking) are INJECTED rather
than imported, so this module stays free of the artifact-reading layer that
imports it.
"""

from __future__ import annotations

import re
from pathlib import Path

GOAL_DIR = "charness-artifacts/goals"
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")

#: What `slugify` returns when the input contained nothing usable. Named because it is
#: the TOTAL-LOSS signature callers refuse on -- not merely "was coerced", which is
#: normal and global.
SLUG_FALLBACK = "goal"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or SLUG_FALLBACK


def normalize_goal_text(value: str) -> str:
    """Normalize line endings before a value is checked or rendered."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def validate_goal_values(title: str, goal_body: str, *, fences_balanced, mask_fences) -> tuple[str, str]:
    """Return canonical goal values or reject shapes that change on readback."""
    title = normalize_goal_text(title)
    goal_body = normalize_goal_text(goal_body)
    if "\n" in title:
        raise ValueError(
            "goal `title` must be single-line; it is rendered as one `# Achieve Goal:` heading"
        )
    if not fences_balanced(goal_body):
        raise ValueError(
            "goal `goal-body` leaves a code fence unclosed (odd number of ``` / ~~~ markers). "
            "Every heading check reads the body with fences masked, and an unbalanced body has "
            "two irreconcilable readings, so this refuses rather than guessing. Close the fence."
        )
    if re.search(r"^#{1,6} ", mask_fences(goal_body), re.MULTILINE):
        raise ValueError(
            "goal `goal-body` contains an unfenced markdown heading line (`# `..`###### `). "
            "The body is written under `## Goal`; a heading there would silently end that "
            "section and be read back as a real one. Use bold or list text, or put the line "
            "inside a fenced code block."
        )
    return title, goal_body


def resolve_supplied_slug(slug: str) -> str:
    """Resolve a caller-supplied slug while refusing total loss to the fallback."""
    resolved = slugify(slug)
    if resolved == SLUG_FALLBACK and slug.strip().lower() != SLUG_FALLBACK:
        raise ValueError(
            f"--slug {slug!r} contains nothing usable and would be written as "
            f"{resolved!r} -- a filename you did not ask for. An argument that survives "
            f"as nothing is what a failed shell substitution looks like, so this refuses "
            f"rather than creating <date>-{resolved}.md."
        )
    return resolved


def goal_path(repo_root: Path, date: str, slug: str) -> Path:
    if not _DATE.match(date):
        raise ValueError(f"invalid date {date!r}; expected YYYY-MM-DD")
    return repo_root / GOAL_DIR / f"{date}-{slugify(slug)}.md"


def goal_rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()
