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

import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    pass


def _git_paths(repo_root: Path, args: list[str], *, artifact_label: str) -> list[str]:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
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
    paths = set(_git_paths(repo_root, ["diff", "--name-only", "HEAD", "--"], artifact_label=artifact_label))
    paths.update(_git_paths(repo_root, ["ls-files", "--others", "--exclude-standard"], artifact_label=artifact_label))
    return sorted(paths)


REPORT_ALL_DEPRECATED_HELP = (
    "Deprecated no-op: reporting every violation in one pass is now the default. "
    "Use --fail-fast to stop at the first violation."
)


def add_changed_artifact_args(parser, *, default_repo_root: Path, all_help: str) -> None:
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help=all_help)


def add_one_pass_args(parser, *, fail_fast_help: str) -> None:
    """The one-pass control, declared once for every artifact validator.

    `--fail-fast` is the ONLY knob: one-pass is the default across the family, and
    `--report-all` stays accepted as a no-op so existing callers, docs, and
    checked-in artifact commands do not break on the flip. Declaring both here —
    rather than per validator — is what stops the D28 polarity split (opposite
    defaults AND opposite flag names across sibling validators) from re-forming:
    a new artifact family cannot pick its own polarity without editing this.
    """
    parser.add_argument("--fail-fast", action="store_true", help=fail_fast_help)
    parser.add_argument("--report-all", action="store_true", help=REPORT_ALL_DEPRECATED_HELP)


def selected_changed_paths(args, repo_root: Path, *, changed_paths_fn: Callable[[Path], list[str]]) -> list[str]:
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
    existence rather than to a blanket pass.
    """
    if owned_prefix is None:
        return []
    owned = [str(path) for path in named if str(path).startswith(owned_prefix)]
    missing = [path for path in owned if not (repo_root / path).is_file()]
    if not missing:
        return []
    deleted: set[str] = set()
    for args in (["ls-files", "--deleted", "-z"], ["diff", "--cached", "--name-only", "--diff-filter=D", "-z"]):
        result = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True)
        if result.returncode == 0:
            deleted.update(
                entry for entry in result.stdout.decode("utf-8", errors="surrogateescape").split("\0") if entry
            )
    return [path for path in missing if path not in deleted]


