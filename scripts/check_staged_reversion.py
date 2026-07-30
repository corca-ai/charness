#!/usr/bin/env python3
"""Block a *staged reversion* of an already-committed file (#258).

The trap this gate closes: a review/critique subagent running in the parent
session's shared worktree checks out a base-commit version of a source file to
exercise pre-change behavior. That leaves the parent index holding the stale,
pre-change blob as a *staged reversion* while ``HEAD`` and the worktree hold the
correct post-change version. A routine closeout ``git add -A && git commit``
would then silently re-commit the reverted code — undoing the change — with every
gate still green, because the reverted code is internally self-consistent.

Detector (three-way blob-hash comparison, per path in
``git diff --cached --name-only``):

    head_blob     = blob of HEAD:<path>      (None if absent in HEAD)
    index_blob    = blob staged at :<path>   (None if staged for deletion)
    worktree_blob = git hash-object <path>   (None if absent on disk)

    flag iff  index_blob != head_blob  AND  worktree_blob == head_blob

Using blob hashes (not ``git diff HEAD``, which ignores the index) means:

- mode-only staged changes pass (the blob is unchanged, so ``index_blob ==
  head_blob``);
- a legitimate full stage passes (``worktree_blob != head_blob`` — the worktree
  carries the new work);
- a new-file add with a present worktree is not flagged (``worktree_blob``
  carries the new blob, which is not ``head_blob``);
- a genuine staged deletion (worktree also gone) passes;
- a staged deletion of a file the worktree still holds unchanged *is* flagged.

This catches only the *unambiguous* phantom: ``worktree == HEAD`` (the file looks
done/correct) but ``index != HEAD`` (a staged blob present in neither the commit
nor the working copy). The mixed case — HEAD=v1, worktree=v2 (real new work),
index=v0 (base reversion) — is git-state-indistinguishable from a legitimate
partial stage, so this gate does NOT block it; that residual is mitigated by the
``Shared-Tree Git Hygiene`` prevention rule in
``skills/shared/references/fresh-eye-subagent-review.md``, not by this gate. This
rung-1 deterministic floor / rung-2 prevention split mirrors the #253
disposition gate.

Escape (mirrors the ``--allow-unmatched`` / env-bypass pattern in the existing
gate family): pass ``--allow-staged-reversion`` or set the environment variable
``CHARNESS_ALLOW_STAGED_REVERSION`` to a truthy value. The escape exits clean and
prints an explicit ``allowed`` line so an intentional staged reversion is
acknowledged, never hidden behind a silent pass.

If git cannot enumerate the index at all (not a repository, dubious ownership,
missing git), the gate reports ``unestablished`` and exits non-zero: it
never prints a clean verdict over a scope it could not read.

Portable: pure git plumbing, no host-specific assumption. Gitlinks (submodules)
are ignored defensively; this repo has none.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass

_ENV_BYPASS = "CHARNESS_ALLOW_STAGED_REVERSION"
_TRUTHY = {"1", "true", "yes", "on"}
_GITLINK_MODE = "160000"


def _git(repo_root: str, *args: str) -> "subprocess.CompletedProcess[str]":
    """Run a read-only git command in ``repo_root`` and capture text output."""
    return subprocess.run(
        ["git", "-C", repo_root, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _staged_paths(repo_root: str) -> list[str]:
    """Repo-relative paths with staged changes (index vs HEAD), deletions included.

    Raises ``RuntimeError`` if git cannot enumerate the index (not a repository,
    dubious ownership, missing git, ...; the exit code is git's and varies by
    subcommand and version, so nothing keys on a specific one). This call establishes the
    gate's entire scope: an empty list from a failed git is indistinguishable
    from "nothing staged", so returning it would render a clean verdict over a
    scope that was never read (mirrors the sibling gate
    ``check_staged_worktree_consistency.py``).
    """
    try:
        proc = _git(repo_root, "diff", "--cached", "--name-only", "-z")
    except OSError as exc:  # git absent, repo_root unusable as cwd, ...
        raise RuntimeError(f"git diff --cached failed: {exc}") from exc
    if proc.returncode != 0:
        # First stderr line only: git appends a full usage dump for some
        # failures, which would bury the gate's own message.
        reason = next((ln for ln in proc.stderr.splitlines() if ln.strip()), "")
        raise RuntimeError(
            reason.strip() or f"git diff --cached --name-only exited {proc.returncode}"
        )
    return [p for p in proc.stdout.split("\0") if p]


def _head_entry(repo_root: str, path: str) -> tuple[str | None, str | None]:
    """(mode, blob) of HEAD:<path>, or (None, None) if absent in HEAD."""
    proc = _git(repo_root, "ls-tree", "HEAD", "-z", "--", path)
    if proc.returncode != 0 or not proc.stdout:
        return None, None
    record = proc.stdout.split("\0")[0]  # "<mode> <type> <sha>\t<path>"
    meta = record.partition("\t")[0]
    parts = meta.split()
    if len(parts) < 3:
        return None, None
    return parts[0], parts[2]


def _index_entry(repo_root: str, path: str) -> tuple[str | None, str | None, bool]:
    """(mode, blob, unmerged) for :<path>; (None, None, False) when staged for deletion.

    Record [0] of an UNMERGED path is stage 1 -- the merge base, not an index blob.
    Reading it as the staged content made a mid-merge `git checkout --ours` look
    like a modified-reversion phantom (base != HEAD, worktree == HEAD), and reading
    "no stage 0" as a staged deletion turns it into a deletion phantom instead.
    Neither is true, `git commit` refuses a conflicted path anyway, so the caller
    skips it on the third element rather than guessing from the first two.
    """
    proc = _git(repo_root, "ls-files", "--stage", "-z", "--", path)
    if proc.returncode != 0 or not proc.stdout:
        return None, None, False
    records = [record for record in proc.stdout.split("\0") if record]
    for record in records:  # "<mode> <sha> <stage>\t<path>"
        meta = record.partition("\t")[0]
        parts = meta.split()
        if len(parts) < 3 or parts[2] != "0":
            continue
        return parts[0], parts[1], False
    return None, None, bool(records)


def _worktree_blob(repo_root: str, path: str) -> str | None:
    """git hash-object of the worktree file, or None if it is absent on disk.

    `None` is load-bearing in the line-198 fingerprint -- it MEANS "not on disk",
    which is what distinguishes the deletion phantom from the modified one. A file
    that is present but unhashable (unreadable mode, dangling symlink) is not that
    fact, and mapping it to `None` silently dropped a real phantom: `None ==
    head_blob` is False, so the finding vanished and the gate printed clean. That
    is the gate's own class at path granularity, so it raises instead.
    """
    if not os.path.lexists(os.path.join(repo_root, path)):
        return None
    proc = _git(repo_root, "hash-object", "--", path)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(
            f"could not hash the worktree copy of {path}: "
            + (proc.stderr.strip().splitlines() or ["git hash-object failed"])[0]
        )
    return proc.stdout.strip()


def _recovery(case: str, path: str) -> str:
    """Per-case recovery that never tells the operator to re-corrupt the index."""
    if case == "staged-deletion-phantom":
        # `git rm --cached` produces this exact triple deliberately, and it is
        # git-state-indistinguishable from the phantom. Naming only `git add` there
        # tells the operator to undo the commit they meant to make, so the
        # untrack reading gets its own line rather than a footnote at the end.
        return (
            f"index stages a deletion of {path!r}, but HEAD and the worktree both "
            f"hold it unchanged. Recover with: git add -- {path!r} "
            "(re-stage the worktree version, dropping the phantom deletion). "
            f"If you ran `git rm --cached {path}` on purpose, re-run the commit with "
            f"{_ENV_BYPASS}=1 instead."
        )
    return (
        f"index holds a stale blob for {path!r} that matches neither HEAD nor the "
        f"worktree (worktree == HEAD). Recover with: git add -- {path!r} "
        "(re-stage the correct worktree version so index == HEAD)."
    )


@dataclass
class Finding:
    path: str
    case: str
    head_blob: str | None
    index_blob: str | None
    worktree_blob: str | None

    @property
    def recovery(self) -> str:
        return _recovery(self.case, self.path)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "case": self.case,
            "head_blob": self.head_blob,
            "index_blob": self.index_blob,
            "worktree_blob": self.worktree_blob,
            "recovery": self.recovery,
        }


def find_staged_reversions(repo_root: str) -> list[Finding]:
    """Return the unambiguous staged-reversion phantoms among staged paths."""
    findings: list[Finding] = []
    for path in _staged_paths(repo_root):
        head_mode, head_blob = _head_entry(repo_root, path)
        index_mode, index_blob, unmerged = _index_entry(repo_root, path)
        if unmerged:
            continue  # conflicted: no stage-0 entry, and git refuses to commit it
        if _GITLINK_MODE in (head_mode, index_mode):
            continue  # skip submodule gitlinks defensively
        worktree_blob = _worktree_blob(repo_root, path)

        # Fingerprint: the index diverges from HEAD, yet the worktree agrees with
        # HEAD. ``None == None`` is intentional (both absent => the worktree
        # agrees with HEAD that the path should not exist).
        if index_blob != head_blob and worktree_blob == head_blob:
            case = (
                "staged-deletion-phantom"
                if index_blob is None
                else "modified-reversion-phantom"
            )
            findings.append(
                Finding(
                    path=path,
                    case=case,
                    head_blob=head_blob,
                    index_blob=index_blob,
                    worktree_blob=worktree_blob,
                )
            )
    return findings


def _bypassed(args: argparse.Namespace) -> bool:
    if getattr(args, "allow_staged_reversion", False):
        return True
    return os.environ.get(_ENV_BYPASS, "").strip().lower() in _TRUTHY


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Block a staged reversion of an already-committed file: index != "
            "HEAD while worktree == HEAD (#258)."
        )
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument(
        "--allow-staged-reversion",
        action="store_true",
        help=(
            "Acknowledge an intentional staged reversion and exit clean "
            f"(also honored via the {_ENV_BYPASS} env var)."
        ),
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit findings as JSON on stdout."
    )
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)

    if _bypassed(args):
        if args.json:
            print(json.dumps({"state": "allowed", "findings": []}))
        else:
            print(
                "check-staged-reversion: explicitly allowed "
                f"(--allow-staged-reversion / {_ENV_BYPASS})"
            )
        return 0

    try:
        findings = find_staged_reversions(repo_root)
    except RuntimeError as exc:
        # The index could not be read, so nothing was established. Report the
        # unestablished state instead of printing a clean verdict over a scope
        # this gate never saw.
        if args.json:
            print(
                json.dumps(
                    {"state": "unestablished", "findings": [], "error": str(exc)}
                )
            )
        else:
            print(
                "check-staged-reversion: UNESTABLISHED — git could not read the "
                f"index at {repo_root!r}, so no staged path was inspected.\n"
                f"  git: {exc}\n"
                "Fix the repository access (e.g. run from inside the repo, or "
                "`git config --global --add safe.directory <path>` for a "
                "dubious-ownership checkout) and re-run."
            )
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "state": "clean" if not findings else "blocked",
                    "findings": [f.to_dict() for f in findings],
                }
            )
        )
    elif not findings:
        print("check-staged-reversion: clean (no staged reversion of committed files)")
    else:
        print(
            "check-staged-reversion: BLOCKED — staged reversion of "
            f"{len(findings)} already-committed file(s) detected.\n"
            "The index holds a blob that is in neither the commit nor the "
            "working copy; committing now would silently re-introduce removed "
            "code with all gates green (#258).\n"
        )
        for finding in findings:
            print(f"  - {finding.path} [{finding.case}]")
            print(f"      {finding.recovery}")
        print(
            "\nIf this staged reversion is intentional, re-run with "
            f"--allow-staged-reversion or set {_ENV_BYPASS}=1."
        )

    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
