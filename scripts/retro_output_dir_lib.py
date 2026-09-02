#!/usr/bin/env python3
"""Which directory a repo keeps its retros in.

One concept, and it renders no verdict on any artifact: this answers "where are THIS
repo's retros", which stopped being a literal and became a layout search, an adapter
read, and a fallback whose two rejected alternatives are the interesting part.

The directory helper lives here so bootstrap and validation use one adapter-derived
owner. It returns a path, while `retro_artifact_prefix` remains the validator's
string-prefix projection.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from runtime_bootstrap import load_path_module, repo_root_from_script, skill_script

#: The prefix used when this repo's retro adapter cannot be read at all. NOT the
#: prefix a run uses -- `retro_artifact_prefix` is. It was a bare constant in the
#: validator while the retro PLANNER's path was adapter-declared, so a consumer whose
#: adapter names another `output_dir` got `Validated 0 retro artifact(s).` and exit 0
#: from a `--paths`-scoped run: the candidate filter dropped every path it was handed,
#: and `owned_prefix` owned a directory that repo does not write to. A validator that
#: reports zero and exits clean over artifacts it was explicitly given is the
#: fail-quiet shape the debug sibling's adapter-derived prefix already closed.
DEFAULT_RETRO_ARTIFACT_PREFIX = "charness-artifacts/retro/"


#: This script's OWN tree, which for a consumer is the installed plugin.
_SCRIPT_REPO_ROOT = repo_root_from_script(__file__)


def _retro_resolver_path(repo_root: Path) -> Path | None:
    """Retro's adapter resolver for ``repo_root``, or ``None`` when none is reachable.

    Two roots, and the second is not optional. The target repo comes first, because a
    repo that vendors its own retro skill must be read by that copy. But the ordinary
    consumer has only `.agents/retro-adapter.yaml` and gets the skill from the
    installed plugin -- searching the target repo alone found nothing there and fell
    back to the DEFAULT prefix, which is the very fail-quiet this module exists to
    close, reproduced inside its own fix. A test asserting the scaffold and the
    validator name one directory is what caught it; the single-root version passed
    every test that only called this function.

    `skill_script` is the shared owner of the dev-tree-vs-export layout search.
    `None` rather than the raise, because a repo with no retro skill reachable at all
    is not an error for a validator whose whole job may legitimately be a no-op.
    """
    for root in (repo_root, _SCRIPT_REPO_ROOT):
        try:
            return skill_script(root, "retro", "resolve_adapter.py")
        except FileNotFoundError:
            continue
    return None


def load_retro_adapter(repo_root: Path) -> dict:
    """The retro adapter payload for ``repo_root``, read through the repo's OWN resolver.

    Exposed so the validator's version preflight asks the same resolver
    `retro_artifact_prefix` asks. Reading it a second way is how a prefix and a verdict
    about that prefix come to disagree about one adapter. Raises when no resolver is
    reachable or the resolver itself fails; the caller decides whether that is fatal --
    `unspeakable_version_message` treats it as "not a version refusal", which is right,
    because a repo with no retro skill reachable is not an error for this validator.
    """
    resolver_path = _retro_resolver_path(repo_root)
    if resolver_path is None:
        raise FileNotFoundError("no retro resolve_adapter.py reachable")
    return load_path_module("retro_validator_resolve_adapter", resolver_path).load_adapter(
        repo_root
    )


def retro_artifact_prefix(repo_root: Path) -> str:
    """The retro output directory THIS repo declares, as a trailing-slash prefix.

    Read the same way the retro skill reads it, so the validator and the planner
    cannot disagree about which directory holds a repo's retros. The value is
    canonicalised by retro's `resolve_adapter` -- one owner, because a raw-string
    producer and a `Path`-normalising consumer disagreed silently for every untidy
    `output_dir` -- so this only appends the separator.

    Falls back to `DEFAULT_RETRO_ARTIFACT_PREFIX` rather than to `None` or `""`,
    and the two rejected alternatives are why: `None` would make `candidate_paths`
    unable to glob anything, and an empty prefix would make EVERY named path look
    owned -- the opposite failure, refusing paths that belong to no retro family at
    all.

    The `except Exception` is not defensive padding. This executes the resolver of
    the repo UNDER VALIDATION, whose module body itself runs a bootstrap search: a
    partial install, an exported layout missing `skill_runtime_bootstrap.py`, or a
    syntax error in a consumer's own copy all raise, and an uncaught one is a
    traceback out of a surface whose entire job is to render a verdict. The
    docstring used to claim an unreadable adapter kept today's behaviour while only
    a MISSING one did; this makes the claim true.
    """
    output_dir: object = None
    resolver_path = _retro_resolver_path(repo_root)
    if resolver_path is not None:
        try:
            module = load_path_module("retro_validator_resolve_adapter", resolver_path)
            output_dir = module.load_adapter(repo_root).get("data", {}).get("output_dir")
        except Exception:  # noqa: BLE001 - see docstring: a verdict, never a traceback
            output_dir = None
    if not isinstance(output_dir, str) or not output_dir.strip():
        return DEFAULT_RETRO_ARTIFACT_PREFIX
    normalized = PurePosixPath(output_dir.strip()).as_posix().rstrip("/")
    # An absolute or repo-escaping value cannot name a directory inside the tree being
    # validated. The adapter refuses it; if one arrives anyway (an older adapter, a
    # consumer resolver that skips validation), owning nothing is the fail-quiet this
    # module exists to close, so fall back to the declared default instead.
    if not normalized or normalized.startswith(("/", "..")):
        return DEFAULT_RETRO_ARTIFACT_PREFIX
    return f"{normalized}/"


def retro_output_dir(repo_root: Path) -> Path:
    """Return the adapter-declared retro directory for a repository."""
    return repo_root.resolve() / PurePosixPath(retro_artifact_prefix(repo_root).rstrip("/"))


def retro_summary_path(repo_root: Path) -> Path | None:
    """Return the adapter-declared summary path, preserving an explicit opt-out."""
    try:
        data = load_retro_adapter(repo_root).get("data", {})
    except (FileNotFoundError, OSError, ValueError, KeyError, TypeError):
        data = {}
    summary = data.get("summary_path")
    if summary is None and "summary_path" in data:
        return None
    if isinstance(summary, str) and summary.strip():
        candidate = PurePosixPath(summary.strip())
        if not candidate.is_absolute() and ".." not in candidate.parts:
            return repo_root.resolve() / candidate
    return retro_output_dir(repo_root) / "recent-lessons.md"
