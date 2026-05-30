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
    """Repo-relative paths with staged changes (index vs HEAD), deletions included."""
    proc = _git(repo_root, "diff", "--cached", "--name-only", "-z")
    if proc.returncode != 0:
        return []
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


def _index_entry(repo_root: str, path: str) -> tuple[str | None, str | None]:
    """(mode, blob) staged at :<path>, or (None, None) if staged for deletion."""
    proc = _git(repo_root, "ls-files", "--stage", "-z", "--", path)
    if proc.returncode != 0 or not proc.stdout:
        return None, None
    record = proc.stdout.split("\0")[0]  # "<mode> <sha> <stage>\t<path>"
    meta = record.partition("\t")[0]
    parts = meta.split()
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1]


def _worktree_blob(repo_root: str, path: str) -> str | None:
    """git hash-object of the worktree file, or None if it is absent on disk."""
    if not os.path.lexists(os.path.join(repo_root, path)):
        return None
    proc = _git(repo_root, "hash-object", "--", path)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.strip()


def _recovery(case: str, path: str) -> str:
    """Per-case recovery that never tells the operator to re-corrupt the index."""
    if case == "staged-deletion-phantom":
        return (
            f"index stages a deletion of {path!r}, but HEAD and the worktree both "
            f"hold it unchanged. Recover with: git add -- {path!r} "
            "(re-stage the worktree version, dropping the phantom deletion)."
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
        index_mode, index_blob = _index_entry(repo_root, path)
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

    findings = find_staged_reversions(repo_root)

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
