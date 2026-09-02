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
    scripts_dir = Path(__file__).resolve().parent.parent
    try:
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        registry = importlib.import_module("check_artifact_surface_preflight").REGISTRY
    except Exception:
        return None
    tree_root = scripts_dir.parent
    for surface in registry:
        if surface.artifact_type == artifact_type and surface.scaffold:
            for candidate in _layout_spellings(surface.scaffold):
                resolved = tree_root / candidate
                if not resolved.is_file():
                    continue
                # RELATIVE only when the reader's cwd can resolve it. In an installed
                # layout `tree_root` is the PLUGIN root, not the consumer's repo, so a
                # bare `skills/<id>/scripts/...` names a file that does not exist from
                # where the reader is standing -- a hint naming an unrunnable command is
                # worse than no hint, which is exactly the bar this arm was added under.
                # Absolute is what `scaffold_artifact_lib.validator_command` already
                # emits for the same reason; the `--repo-root .` the caller appends
                # stays correct either way.
                return candidate if candidate == surface.scaffold else str(resolved)
    return None


def _layout_spellings(scaffold: str) -> tuple[str, ...]:
    """The registry spelling, then the EXPORTED one.

    The export flattens `skills/public/<id>/` to `skills/<id>/`, and the registry only
    ever declares the source spelling. Checking one spelling meant `_scaffold_rel`
    returned None for every artifact type in an installed consumer repo -- so the one
    audience that cannot read this repo's source lost the whole hint, including the
    clause that tells them the ceiling is adapter-configurable and where it is
    forecast. Found by an adversarial installed-layout round.

    Order matters: the source spelling wins where both exist, so a dev checkout keeps
    emitting the path its own operator runs.
    """
    parts = Path(scaffold).parts
    if len(parts) > 2 and parts[0] == "skills" and parts[1] == "public":
        return (scaffold, Path(*parts[:1], *parts[2:]).as_posix())
    return (scaffold,)


def _skill_id(artifact_type: str) -> str | None:
    """The skill that owns an artifact type, DERIVED from its scaffold path.

    `skills/public/<id>/scripts/scaffold_*.py` already declares the owner, so a
    second mapping here would be a registry that rots independently of the one it
    duplicates -- the failure this module's `_scaffold_rel` docstring already
    refuses. Both layout spellings are accepted for the same reason `_scaffold_rel`
    checks both: the export flattens `skills/public/<id>/` to `skills/<id>/`, and
    reading only the source spelling silently dropped the "load the owning skill"
    clause for every installed consumer. Anything not under `skills/` yields no name
    rather than a guessed one.
    """
    scaffold = _scaffold_rel(artifact_type)
    return None if scaffold is None else _skill_id_from_scaffold(scaffold)


def _skill_id_from_scaffold(scaffold: str) -> str | None:
    """The parsing half, split out so BOTH layout spellings can be asserted directly.

    `_skill_id` can only be driven through a registry entry whose file exists, and the
    exported spelling by definition does not exist in a source checkout -- so the arm
    that matters to a consumer was untestable while the rule lived inline.
    """
    parts = Path(scaffold).parts
    # `skills` located rather than assumed at index 0: the installed layout emits an
    # ABSOLUTE path (so the printed command is runnable from the consumer's cwd), and
    # anchoring on position dropped the skill name for exactly that reader.
    if "skills" not in parts:
        return None
    parts = parts[parts.index("skills") :]
    if len(parts) < 3:
        return None
    if parts[1] == "public":
        return f"charness:{parts[2]}"
    # `shared`/`support` sit exactly where a flattened `<id>` sits, so a purely
    # positional read would invite the author to load `charness:shared` -- a skill that
    # does not exist -- at the moment they are already looking at a refusal. The export
    # flattens ONLY `skills/public/`; those two keep their own names under it.
    if parts[1] in {"shared", "support"}:
        return None
    return f"charness:{parts[1]}"


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
    # why an owner must sit ON its entry, and why paraphrasing a second artifact
    # beside an owner still fills the budget. A session that hand-authored an
    # artifact hit exactly those three, because nothing in this refusal pointed
    # at the owning skill.
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
