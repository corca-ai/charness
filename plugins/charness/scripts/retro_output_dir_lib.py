#!/usr/bin/env python3
"""Which directory a repo keeps its retros in.

Split from `validate_retro_artifact` at its length cap. One concept, not a spill
(D33): this answers "where are THIS repo's retros" and renders no verdict on any
artifact. It became a job worth its own module the moment the directory stopped
being a literal -- resolving it now carries a layout search, an adapter read, and a
fallback whose two rejected alternatives are the interesting part.

`validate_retro_artifact` re-exports both public names, so its importers keep one
import site.
"""

from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import load_path_module, skill_script

#: The prefix used when this repo's retro adapter cannot be read at all. NOT the
#: prefix a run uses -- `retro_artifact_prefix` is. It was a bare constant in the
#: validator while the retro PLANNER's path was adapter-declared, so a consumer whose
#: adapter names another `output_dir` got `Validated 0 retro artifact(s).` and exit 0
#: from a `--paths`-scoped run: the candidate filter dropped every path it was handed,
#: and `owned_prefix` owned a directory that repo does not write to. A validator that
#: reports zero and exits clean over artifacts it was explicitly given is the
#: fail-quiet shape the debug sibling's adapter-derived prefix already closed.
DEFAULT_RETRO_ARTIFACT_PREFIX = "charness-artifacts/retro/"


def _retro_resolver_path(repo_root: Path) -> Path | None:
    """Retro's own adapter resolver, or ``None`` when this repo has no retro skill.

    `skill_script` is the shared owner of the dev-tree-vs-export layout search; the
    sibling validators that predate it still each carry their own copy. `None`
    rather than the raise, because a repo without the retro skill installed is not
    an error for a validator whose whole job may legitimately be a no-op.
    """
    try:
        return skill_script(repo_root, "retro", "resolve_adapter.py")
    except FileNotFoundError:
        return None


def retro_artifact_prefix(repo_root: Path) -> str:
    """The retro output directory THIS repo declares, as a trailing-slash prefix.

    Read the same way the retro skill reads it, so the validator and the planner
    cannot disagree about which directory holds a repo's retros.

    Falls back to `DEFAULT_RETRO_ARTIFACT_PREFIX` rather than to `None` or `""`,
    and the two rejected alternatives are why: `None` would make `candidate_paths`
    unable to glob anything, and an empty prefix would make EVERY named path look
    owned -- the opposite failure, refusing paths that belong to no retro family at
    all. An unreadable adapter therefore keeps today's behaviour instead of
    inventing a new one.
    """
    resolver_path = _retro_resolver_path(repo_root)
    output_dir: object = None
    if resolver_path is not None:
        module = load_path_module("retro_validator_resolve_adapter", resolver_path)
        output_dir = module.load_adapter(repo_root).get("data", {}).get("output_dir")
    if not isinstance(output_dir, str) or not output_dir.strip():
        return DEFAULT_RETRO_ARTIFACT_PREFIX
    return f"{Path(output_dir).as_posix().rstrip('/')}/"
