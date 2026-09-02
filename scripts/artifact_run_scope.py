#!/usr/bin/env python3
"""Which artifacts a validation run is about, and how it decides that.

Split from `artifact_validator.py` along a real seam: that module owns what a
VALID artifact looks like (headings, order, length, dates), while this one owns
WHICH artifacts a run covers — changed-path discovery, the shared selection
flags, and the judgement separating a legitimately empty scope from one the
caller asserted that resolved to nothing.

The two answer to different failures. A shape rule is wrong when it accepts a
malformed artifact; a scope rule is wrong when it reports a verdict over inputs
it never established — the class `tests/quality_gates/test_empty_scope_refusals.py`
pins.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

from runtime_bootstrap import import_repo_module
from scripts.core.git_status_snapshot import GitStatusError
from scripts.worktree.checkout_view import GitCheckout

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process


class ValidationError(Exception):
    pass


def safe_repo_relative_path(raw: str) -> str | None:
    """Return a normalized repo-relative path, or refuse an escaping one.

    Git emits slash-separated relative paths. An absolute path, Windows drive,
    backslash, or ``..`` component is a malformed ``--paths`` assertion, not an
    empty artifact scope; refusing it prevents readers from escaping their owner.
    """

    value = str(raw)
    candidate = Path(value)
    if (
        not value
        or candidate.is_absolute()
        or PureWindowsPath(value).is_absolute()
        or "\\" in value
        or ".." in candidate.parts
    ):
        return None
    return candidate.as_posix()


def _git_paths(repo_root: Path, args: list[str], *, artifact_label: str) -> list[str]:
    command = ["git", *args]
    result = run_process(
        command,
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        message = (
            f"{artifact_label} artifact changed-path discovery failed; "
            f"command: {' '.join(command)}; exit_code: {result.returncode}"
        )
        if detail:
            message = f"{message}; output: {detail}"
        raise ValidationError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def git_changed_paths(repo_root: Path, *, artifact_label: str) -> list[str]:
    """Dirty worktree paths vs HEAD: one status observation, not diff+ls-files."""
    try:
        return sorted(GitCheckout(repo_root).status().dirty_destination_paths())
    except (GitStatusError, OSError) as exc:
        detail = str(exc).strip()
        message = f"{artifact_label} artifact changed-path discovery failed"
        if detail:
            message = f"{message}; output: {detail}"
        raise ValidationError(message) from exc


def add_changed_artifact_args(parser, *, default_repo_root: Path, all_help: str) -> None:
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument(
        "--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths."
    )
    parser.add_argument("--all", action="store_true", help=all_help)


def add_one_pass_args(parser, *, fail_fast_help: str) -> None:
    """The one-pass control, declared once for every artifact validator.

    `--fail-fast` is the only knob: one-pass is the default across the family.
    Declaring it here rather than per validator is what stops the D28 polarity split (opposite
    defaults AND opposite flag names across sibling validators) from re-forming:
    a new artifact family cannot pick its own polarity without editing this.
    """
    parser.add_argument("--fail-fast", action="store_true", help=fail_fast_help)


def add_artifact_path_arg(parser, *, surface: str) -> None:
    """The draft-override knob for an ADAPTER-SCOPED validator, declared once.

    An adapter-scoped validator resolves its artifact from the adapter (a pointer),
    so without this it can only ever judge the pointer's target. That made the
    author-time preflight print a verdict about a DIFFERENT file than the draft the
    author was holding — a plain wrong PASS for a directory-prefixed surface.

    Declared here for the same reason `add_one_pass_args` is: a shared helper keeps
    adapter-scoped validators from drifting in wording and behavior.
    """
    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=None,
        help=(
            f"Validate this {surface} artifact instead of the adapter-resolved one. Lets a "
            "caller check a candidate draft without moving the live pointer."
        ),
    )


def resolve_artifact_override(args, repo_root: Path, adapter_relative: str) -> Path:
    """The `--artifact-path` override, or the adapter-resolved default.

    Accepts an absolute path so a draft outside the tree (a temp dir) can be checked.
    """
    override = getattr(args, "artifact_path", None)
    if override is None:
        return repo_root / adapter_relative
    return override if override.is_absolute() else repo_root / override


def selected_changed_paths(
    args, repo_root: Path, *, changed_paths_fn: Callable[[Path], list[str]]
) -> list[str]:
    return [] if args.all else args.paths if args.paths is not None else changed_paths_fn(repo_root)


@dataclass(frozen=True)
class ChangedArtifactRun:
    """Resolved CLI state for one changed-path artifact validator run.

    Passed to `validate_factory` (and `artifacts_fn`) so a validator that needs
    more than `collect_all` — critique keys `require_tier_evidence` off which
    paths were selected and whether they were explicit — can single-source
    through the shared runner instead of forking its own `main()`.
    """

    args: Any
    repo_root: Path
    collect_all: bool
    selected_paths: list[str]
    explicit_paths: bool


def unresolvable_named_paths(
    repo_root: Path, named: Sequence[str], *, owned_prefix: str | None = None
) -> list[str]:
    """Named paths this validator owns that resolve to nothing at all.

    Two exclusions keep this off the normal flows, and both are load-bearing
    because `--paths` is fed by TOOLS as often as by people — the surface
    preflight and the closeout sweep pass a slice of the changed set:

    - **Not owned.** A changed path outside this validator's artifact directory
      is the tool saying "none of what changed is yours", which is the common
      case and must stay a pass. Without an `owned_prefix` nothing is owned, so
      a validator that does not declare one keeps its previous behavior.
    - **Deleted on purpose.** A path that is gone *because this change deleted
      it* is a real thing the caller named; a path that never existed is a typo.

    A git failure yields no known deletions, so the check falls back to on-disk
    existence rather than to a blanket pass. That covers git RETURNING nonzero and git
    being ABSENT: `check=False` suppresses only the first, and a missing binary raises
    `FileNotFoundError` straight out of `subprocess.run`. The distinction was dead code
    until a validator declared an `owned_prefix`; the first one that did made an
    uncaught traceback reachable from a surface whose whole job is to render a verdict,
    on any image that ships a lint stage without git.
    """
    if owned_prefix is None:
        return []
    owned = [str(path) for path in named if str(path).startswith(owned_prefix)]
    unsafe = [path for path in owned if safe_repo_relative_path(path) is None]
    missing = [path for path in owned if path not in unsafe and not (repo_root / path).is_file()]
    if not unsafe and not missing:
        return []
    deleted: set[str] = set()
    for args in (
        ["ls-files", "--deleted", "-z"],
        ["diff", "--cached", "--name-only", "--diff-filter=D", "-z"],
    ):
        try:
            result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
        except OSError:
            # No git binary, or it cannot be executed here. Same disposition as a git
            # that ran and failed: no KNOWN deletions, so a named path that is missing
            # on disk stays refused. Refusing is the safe direction -- the alternative
            # is passing a run that validated nothing.
            continue
        if result.returncode == 0:
            deleted.update(entry for entry in result.stdout.split("\0") if entry)
    return unsafe + [path for path in missing if path not in deleted]
