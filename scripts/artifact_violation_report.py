#!/usr/bin/env python3

"""How an artifact violation reaches its author, including the scaffold hint.

Split out of `artifact_validator` as one cohesive concern rather than as a spill to
dodge the length cap (D33): every function here answers "what does the author READ
when a rule refuses", none of them decides a verdict, and nothing in the module
imports the rules it reports for. `artifact_validator` re-exports the whole surface,
so callers keep importing it from the one place they always did.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

__all__ = ["scaffold_hint", "report_validation_failure"]


def _scaffold_rel(artifact_type: str) -> str | None:
    """Repo-relative scaffold script that owns an artifact type's shape.

    The owning scaffold is declared once, in
    `check_artifact_surface_preflight.REGISTRY`; read it from there rather than
    re-declaring the mapping here. Imported lazily so a passing run never pays
    for it, and any import failure degrades to "no hint" — a hint must never
    change a verdict. The scaffold must exist in this layout (an installed
    consumer repo may not ship the skill tree), otherwise the command would name
    a file the author cannot run.
    """
    scripts_dir = Path(__file__).resolve().parent
    try:
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        registry = importlib.import_module("check_artifact_surface_preflight").REGISTRY
    except Exception:
        return None
    for surface in registry:
        if surface.artifact_type == artifact_type and surface.scaffold:
            if (scripts_dir.parent / surface.scaffold).is_file():
                return surface.scaffold
    return None


def _skill_id(artifact_type: str) -> str | None:
    """The skill that owns an artifact type, DERIVED from its scaffold path.

    `skills/public/<id>/scripts/scaffold_*.py` already declares the owner, so a
    second mapping here would be a registry that rots independently of the one it
    duplicates -- the failure this module's `_scaffold_rel` docstring already
    refuses. Anything not under `skills/public/` yields no name rather than a
    guessed one.
    """
    scaffold = _scaffold_rel(artifact_type)
    if scaffold is None:
        return None
    parts = Path(scaffold).parts
    if len(parts) < 3 or parts[0] != "skills" or parts[1] != "public":
        return None
    return f"charness:{parts[2]}"


def scaffold_hint(artifact_type: str) -> str | None:
    """One trailing hint line naming the scaffold an author should start from.

    Every artifact rule is a shape the owning scaffold already emits, so a
    violation report that names only WHAT is wrong leaves the author to
    rediscover the contract one failed run at a time. This names the command
    instead. Hint only: no verdict, requirement, or exit code depends on it.
    """
    scaffold = _scaffold_rel(artifact_type)
    if scaffold is None:
        return None
    # The SKILL is named alongside the scaffold, because they teach different
    # halves and an author who follows only the scaffold gets only one. The
    # scaffold emits shape; the skill body holds the disciplines an author
    # otherwise meets one refusal at a time -- what the size budget charges for,
    # why an owner must sit ON its entry, why paraphrasing a second artifact
    # beside an owner still fills the budget. A session that hand-authored a
    # handoff hit exactly those three, in a repo whose skill already documented
    # all of them, because nothing in this refusal pointed at the skill.
    skill = _skill_id(artifact_type)
    invoke = f" Load the `{skill}` skill for the authoring discipline." if skill else ""
    return (
        f"hint: start from the owning scaffold instead of hand-authoring — "
        f'`python3 {scaffold} --repo-root . --title "<title>"` emits a conforming '
        f"stub plus the write path and validator command.{invoke}"
    )


def report_validation_failure(message: str, *, artifact_type: str) -> int:
    """Print a validator's violations, then the scaffold hint ONCE per run.

    Returns the failing exit code so callers can `return`/`raise SystemExit` it.
    """
    print(message, file=sys.stderr)
    hint = scaffold_hint(artifact_type)
    if hint:
        print(hint, file=sys.stderr)
    return 1
