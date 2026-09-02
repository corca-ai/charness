#!/usr/bin/env python3
"""Pre-commit gate: a staged file must not also carry unstaged worktree edits.

Many pre-commit gates (check-markdown, check_doc_links,
...) validate the WORKING TREE, not the staged index blob. If a file is staged and
then edited again, those gates validate the on-disk version while git commits the
stale staged blob -- a gate can pass on content that is not what lands. Observed:
a document once committed past its cap because the validator read the worktree
while the index still held a different blob.

This gate fails when a staged path also has unstaged worktree modifications, so
"what the gates validate" == "what is committed". Set CHARNESS_ALLOW_PARTIAL_STAGE=1
to allow a deliberate partial (`git add -p`) commit.

It also fails on the UNTRACK shape: a path staged for deletion that is still on
disk (`git rm --cached x`, or `git rm --cached x` followed by editing x). That
one is invisible to the intersection below -- see `find_stale_staged` -- and it
is the same defect, at full strength: every worktree-walking gate validates the
on-disk copy and prints `ok`, and the commit removes the file from the tree.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

if __package__ in (None, ""):  # `python3 scripts/<name>.py`, not `-m scripts.<name>`
    # That argv puts `<repo>/scripts` on `sys.path` and NOT the repo root, so
    # `from scripts.… import …` raised `ModuleNotFoundError: No module named
    # 'scripts'` and this gate could not run through its own scheduled
    # invocation (`staged_commit_gate_plan_helpers.py:115`) at all.
    #
    # The repo root goes on the path rather than each import gaining a bare-name
    # fallback, because the failure is not local: `git_status_snapshot` imports
    # `scripts.git_checkout` in turn, so a per-import dual-path here fixes only
    # the first link and dies on the next one down.
    #
    # No test could observe this. Every test reaches these gates IN-PROCESS,
    # where `pyproject.toml` `pythonpath = [".", "scripts"]` supplies both
    # spellings at once.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_bootstrap import import_repo_module
from scripts.env_bypass import env_bypass_enabled
from scripts.git_status_snapshot import (
    GitStatusError,
    GitStatusSnapshot,
)
from scripts.git_status_snapshot import parse as parse_git_status
from scripts.git_status_snapshot import status_args as git_status_args

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

ALLOW_ENV = "CHARNESS_ALLOW_PARTIAL_STAGE"
_STATUS_CODES = frozenset(".MTADRCU")
_STAGED_STATUS_ARGS = git_status_args(branch=False, untracked="no", no_renames=True)
# No --diff-filter. The first cut used ACM, which hid a path staged and then
# DELETED on disk -- exactly the case worktree-walking validators skip entirely,
# so the staged blob shipped unchecked. Widening it to ACMRD fixed that one letter
# and left T (typechange: file <-> symlink) and U (unmerged) hidden by the same
# mechanism. An allowlist of status letters is the wrong shape for a gate whose
# question is "does this path appear on BOTH sides": every letter git can report
# is a real difference, so the intersection is the filter.


def allow_partial_stage() -> bool:
    """True only for an explicit truthy spelling of the bypass env var."""
    return env_bypass_enabled(ALLOW_ENV)


def _index_sides(snapshot: GitStatusSnapshot) -> tuple[set[str], set[str], set[str]]:
    """Project staged, unstaged, and post-index tracked paths from one snapshot."""
    staged: set[str] = set()
    unstaged: set[str] = set()
    tracked: set[str] = set()
    for record in snapshot.records:
        if record.kind == "rename":
            raise RuntimeError("git status reported a rename despite --no-renames")
        if record.kind in {"untracked", "ignored"}:
            raise RuntimeError(
                "git status enumerated untracked or ignored paths despite --untracked-files=no"
            )
        xy = record.xy
        if (
            len(xy) != 2
            or any(status not in _STATUS_CODES for status in xy)
            or xy == ".."
            or not record.path
        ):
            raise RuntimeError("git status returned malformed path state")
        x, y = xy[0], xy[1]
        if x != ".":
            staged.add(record.path)
        if y != ".":
            unstaged.add(record.path)
        if record.kind == "unmerged" or x != "D":
            tracked.add(record.path)
    return staged, unstaged, tracked


def _status_paths(repo_root: Path) -> tuple[set[str], set[str], set[str]]:
    """Return staged, unstaged, and post-index tracked paths from one status read."""
    try:
        result = run_process(
            ["git", *_STAGED_STATUS_ARGS],
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError as exc:  # git absent, cwd unusable
        raise RuntimeError(f"git status: {exc}") from exc
    if result.returncode != 0:
        message = result.stderr.strip()
        raise RuntimeError(message or "git status failed")
    try:
        # The guard decodes child output with surrogateescape; encoding the same way
        # hands the byte parser the exact bytes git emitted, so a non-UTF-8 path survives.
        snapshot = parse_git_status(result.stdout.encode("utf-8", errors="surrogateescape"))
    except GitStatusError as exc:
        raise RuntimeError(str(exc)) from exc
    return _index_sides(snapshot)


def _on_disk(repo_root: Path, path: str) -> bool:
    """Whether a worktree walker would still find something at ``path``.

    ``lexists``, not ``exists``: a dangling symlink is still an entry a walker
    trips over, and mapping it to "gone" is how a real finding vanished in the
    sibling gate. Any OSError (name too long, unrepresentable byte sequence,
    permission on a parent) is reported as PRESENT, because this predicate only
    ever adds a refusal -- guessing "absent" would fail open.
    """
    try:
        return (repo_root / path).is_symlink() or (repo_root / path).exists()
    except OSError:
        return True


# floor-addition-restraint: recorded call, not an assertion of compliance.
# Q1 (closeout-contract weight): no -- this widens an existing gate's predicate and
# adds no new required field, section, or form.
# Q2 (is advisory enough?): no, but NOT on a recurrence count -- there is no honest
# one. This exact shape was adjudicated once, as F8 in
# charness-artifacts/critique/2026-07-27-a3-staged-scope.md, at
# `valid-but-defer / action: document`, and carried on the work item since. This
# slice promotes that documented deferral to a floor, on the ground that the
# failure is a commit that removes a file from the tree with every doc gate green
# -- the #258 class the sibling gate refuses outright -- and an advisory does not
# stop it. Calling that a "recurrence" would be manufacturing evidence.
# Q3 (can the describe-first preflight absorb it?): no -- the condition is a
# runtime property of the index, not a static artifact shape, so this is a `keep`.
# Control: no new env var. `CHARNESS_ALLOW_PARTIAL_STAGE` is reused, and because
# its NAME does not describe an untrack, the untrack branch of the message names
# the deliberate case in words the way check_staged_reversion does (that gate's
# own F4 fix). An operator untracking on purpose is a legitimate workflow, not a
# mistake; the gate refuses only because the assurance the other gates printed was
# over the wrong tree, and the message says so.
def find_stale_staged(repo_root: Path) -> list[str]:
    """Paths whose committed blob is not what the worktree-walking gates read."""
    edited, orphaned = _classify_stale(repo_root)
    return sorted(edited | orphaned)


def classify_stale(
    staged: set[str],
    unstaged: set[str],
    tracked: set[str],
    *,
    present: Callable[[str], bool],
) -> tuple[set[str], set[str]]:
    """Classify stale paths from one already-observed index/worktree snapshot.

    Returns ``(edited, orphaned)``:

    * ``edited`` -- staged AND further edited on disk. The original intersection.
    * ``orphaned`` -- staged such that the path has NO index entry afterwards,
      yet something is still on disk at that name (`git rm --cached x`, or the
      source half of a rename whose old name was recreated). The intersection is
      structurally blind to this: removing a path from the index removes its index
      ENTRY, so `git diff --name-only` (worktree vs index) can no longer name it --
      git reports it as untracked. The intersection went empty and the gate passed
      while the file the doc gates walked was exactly the file the commit deletes.

    Porcelain v2 exposes both sides as XY in one coherent observation. Rename
    detection stays disabled so a deleted source and added destination remain
    independently classifiable. Untracked enumeration is disabled: a staged
    deletion remains a ``D.`` record, and ``present`` owns presence detection.
    """
    # A case-only rename (`Foo.md` -> `foo.md`) on a case-insensitive filesystem
    # stages a deletion of the old spelling while `lexists` resolves it to the NEW
    # file, which would be a false refusal on macOS and Windows -- and both remedies
    # would be actively harmful there.
    #
    # Folded over `staged & tracked`, NOT over `tracked`. A case-only rename always
    # STAGES the new spelling, so that is the evidence of a re-spelling; folding
    # over the whole tracked set makes the exemption fire on coincidence instead.
    # Measured: with `Foo.md` and `foo.md` both tracked (legal on Linux, where this
    # hook runs), `git rm --cached Foo.md` with the file still on disk returned
    # `[]` -- a fail-open in the repaired predicate, in the exact class this slice
    # closes, found by the round that read the repair.
    folded = {path.casefold() for path in staged & tracked}
    orphaned = {
        path for path in staged - tracked if path.casefold() not in folded and present(path)
    }
    return staged & unstaged, orphaned


def _classify_stale(repo_root: Path) -> tuple[set[str], set[str]]:
    staged, unstaged, tracked = _status_paths(repo_root)
    return classify_stale(staged, unstaged, tracked, present=lambda path: _on_disk(repo_root, path))


def _remedy_lines(paths: list[str], render, *, cap: int = 10) -> str:
    """Rendered remedies, capped. `git rm -r --cached <dir>` can orphan thousands
    of paths, and an uncapped enumeration buries the bypass line printed after it.
    """
    shown = paths[:cap]
    text = "".join(line + "\n" for path in shown for line in render(path))
    if len(paths) > cap:
        text += f"  ... and {len(paths) - cap} more path(s) in the same state\n"
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if allow_partial_stage():
        # Announced, not silent — the sibling gate at this boundary prints its own
        # `allowed` line so a deliberate bypass is acknowledged rather than hidden
        # behind a pass that looks identical to a clean run.
        sys.stderr.write(f"staged-worktree-consistency: explicitly allowed ({ALLOW_ENV})\n")
        return 0

    try:
        edited_set, orphaned = _classify_stale(repo_root)
    except RuntimeError as exc:
        # The sibling gate at this boundary (check_staged_reversion) reports an
        # explicit UNESTABLISHED verdict with a remedy; a bare traceback blocks
        # the same commit while telling the operator nothing.
        sys.stderr.write(
            f"UNESTABLISHED: could not read the index/worktree diff: {exc}\n"
            "This gate reports no verdict rather than a clean one. If this is a\n"
            "dubious-ownership checkout, run:\n"
            f"  git config --global --add safe.directory {repo_root}\n"
        )
        return 1
    if not edited_set and not orphaned:
        return 0

    # One classification, one index read. The first cut re-queried git to split the
    # remedies, so a concurrent `git add` between the two reads could file a path
    # under the wrong remedy -- and a failure of that second read silently offered
    # `git add` for a path staged for deletion, the one remedy the split exists to
    # forbid.
    sys.stderr.write(
        "the committed blob is NOT what the pre-commit gates validated; those\n"
        "gates walk the working tree, and for these paths the working tree and\n"
        "the index disagree about what lands.\n"
    )
    if edited_set:
        sys.stderr.write(
            "\nstaged, then edited again on disk -- re-stage so what is validated\n"
            "is what commits:\n"
            + _remedy_lines(sorted(edited_set), lambda path: [f"  git add {path}"])
        )
    if orphaned:
        # `git rm <path>` is NOT offered: these paths have no index entry, so it
        # exits 128 with `pathspec ... did not match any files`. Handing an operator
        # a command that errors, on a gate that just blocked their commit, is worse
        # than saying nothing. Verified 2026-07-31.
        sys.stderr.write(
            "\nstaged for removal from the tree but still on disk (`git rm --cached`,\n"
            "or a rename whose old name was recreated). Untracking on purpose is a\n"
            "legitimate thing to do -- the problem is only that the gates above\n"
            "printed PASS after walking the on-disk copy, which this commit removes\n"
            "from the tree. If you meant it, that is what the bypass is for:\n"
            f"  {ALLOW_ENV}=1 git commit ...   # deliberate untrack; gates re-read nothing\n"
            "Otherwise (`git reset` restores the old name's entry; after a rename\n"
            "that leaves BOTH names in the commit, so prefer `rm` there):\n"
            + _remedy_lines(
                sorted(orphaned),
                lambda path: [
                    f"  rm {path}                 # remove it on disk too, then re-run",
                    f"  git reset -- {path}       # restore this path's HEAD entry",
                ],
            )
        )
    sys.stderr.write(f"\n({ALLOW_ENV}=1 also allows a deliberate partial (`git add -p`) commit.)\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
