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
``git diff --cached --raw``):

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
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from scripts.yaml_output import emit_yaml

try:
    from scripts.core.env_bypass import env_bypass_enabled
except ModuleNotFoundError:
    from env_bypass import env_bypass_enabled

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

_ENV_BYPASS = "CHARNESS_ALLOW_STAGED_REVERSION"
_GITLINK_MODE = "160000"


def _git(repo_root: str, *args: str) -> "subprocess.CompletedProcess[str]":
    """Run a read-only git command in ``repo_root`` and capture text output."""
    return run_process(
        ["git", "-C", repo_root, *args],
        cwd=Path(repo_root),
        timeout_seconds=None,
    )


def _blob_or_none(sha: str) -> str | None:
    """``None`` for the all-zero placeholder ``--raw`` prints for an absent blob."""
    return None if set(sha) == {"0"} else sha


def _staged_raw_diff(repo_root: str) -> list[dict[str, object]]:
    """One ``git diff --cached --raw`` pass over every staged path.

    A ``--raw`` record already carries the old (HEAD) mode/blob and the new
    (index) mode/blob for a path, plus an explicit ``U`` status for an unmerged
    one -- the same three facts a ``--name-only`` scoping diff, a per-path
    ``ls-tree HEAD``, and a per-path ``ls-files --stage`` used to need three
    separate git processes to assemble. ``--no-renames`` keeps one path per
    record; this gate classifies per-path triples and a rename record with two
    paths would need its own decomposition.

    Raises ``RuntimeError`` if git cannot enumerate the index (not a repository,
    dubious ownership, missing git, ...; the exit code is git's and varies by
    subcommand and version, so nothing keys on a specific one). This call
    establishes the gate's entire scope: an empty list from a failed git is
    indistinguishable from "nothing staged", so returning it would render a
    clean verdict over a scope that was never read (mirrors the sibling gate
    ``check_staged_worktree_consistency.py``).
    """
    try:
        # `-c core.abbrev=no`: `--raw` abbreviates object names by default (a
        # short hash git itself may lengthen later as the repo grows), and an
        # abbreviated `head_blob` compared against `_worktree_blob`'s full
        # `hash-object` output never matches even when the content is identical.
        proc = _git(
            repo_root, "-c", "core.abbrev=no", "diff", "--cached", "--raw", "-z", "--no-renames"
        )
    except OSError as exc:  # git absent, repo_root unusable as cwd, ...
        raise RuntimeError(f"git diff --cached failed: {exc}") from exc
    if proc.returncode != 0:
        # First stderr line only: git appends a full usage dump for some
        # failures, which would bury the gate's own message.
        reason = next((ln for ln in proc.stderr.splitlines() if ln.strip()), "")
        raise RuntimeError(reason.strip() or f"git diff --cached --raw exited {proc.returncode}")
    records = [r for r in proc.stdout.split("\0") if r]
    entries: list[dict[str, object]] = []
    index = 0
    while index < len(records):
        meta, path = records[index], records[index + 1]
        index += 2
        # ":<old-mode> <new-mode> <old-sha> <new-sha> <status>"
        old_mode, new_mode, old_sha, new_sha, status = meta.lstrip(":").split()
        entries.append(
            {
                "path": path,
                "head_blob": _blob_or_none(old_sha),
                "index_blob": _blob_or_none(new_sha),
                "unmerged": status.startswith("U"),
                "gitlink": _GITLINK_MODE in (old_mode, new_mode),
            }
        )
    return entries


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


def classify_reversion(
    path: str,
    *,
    head_blob: str | None,
    index_blob: str | None,
    worktree_blob: str | None,
    unmerged: bool = False,
    gitlink: bool = False,
) -> Finding | None:
    """Classify one already-observed HEAD/index/worktree triple.

    Fingerprint: the index diverges from HEAD, yet the worktree agrees with
    HEAD. ``None == None`` is intentional (both absent => the worktree agrees
    with HEAD that the path should not exist). Callers that already have the
    three blobs project from this; they do not re-ask Git.
    """
    if unmerged:
        return None  # conflicted: no stage-0 entry, and git refuses to commit it
    if gitlink:
        return None  # skip submodule gitlinks defensively
    if index_blob != head_blob and worktree_blob == head_blob:
        return Finding(
            path=path,
            case=(
                "staged-deletion-phantom" if index_blob is None else "modified-reversion-phantom"
            ),
            head_blob=head_blob,
            index_blob=index_blob,
            worktree_blob=worktree_blob,
        )
    return None


def find_staged_reversions(
    repo_root: str,
    *,
    triples: list[dict[str, object]] | None = None,
) -> list[Finding]:
    """Return the unambiguous staged-reversion phantoms among staged paths.

    ``triples`` is already-observed HEAD/index/worktree facts. The Git adapter
    below obtains them; classifiers do not.
    """
    if triples is not None:
        findings: list[Finding] = []
        for triple in triples:
            head_blob = triple.get("head_blob")
            index_blob = triple.get("index_blob")
            worktree_blob = triple.get("worktree_blob")
            finding = classify_reversion(
                str(triple["path"]),
                head_blob=None if head_blob is None else str(head_blob),
                index_blob=None if index_blob is None else str(index_blob),
                worktree_blob=None if worktree_blob is None else str(worktree_blob),
                unmerged=bool(triple.get("unmerged", False)),
                gitlink=bool(triple.get("gitlink", False)),
            )
            if finding is not None:
                findings.append(finding)
        return findings
    findings = []
    for entry in _staged_raw_diff(repo_root):
        unmerged = bool(entry["unmerged"])
        path = str(entry["path"])
        worktree_blob = None if unmerged else _worktree_blob(repo_root, path)
        finding = classify_reversion(
            path,
            head_blob=entry["head_blob"],  # type: ignore[arg-type]
            index_blob=entry["index_blob"],  # type: ignore[arg-type]
            worktree_blob=worktree_blob,
            unmerged=unmerged,
            gitlink=bool(entry["gitlink"]),
        )
        if finding is not None:
            findings.append(finding)
    return findings


def _bypassed(args: argparse.Namespace) -> bool:
    if getattr(args, "allow_staged_reversion", False):
        return True
    return env_bypass_enabled(_ENV_BYPASS)


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
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)

    if _bypassed(args):
        emit_yaml(
            {
                "state": "allowed",
                "findings": [],
                # The escape must stay acknowledged rather than hidden behind a
                # silent pass (module docstring); with output unconditionally
                # YAML, the acknowledgement has to be a payload field.
                "detail": (
                    "explicitly allowed (--allow-staged-reversion / "
                    f"{_ENV_BYPASS}); no staged path was inspected"
                ),
            }
        )
        return 0

    try:
        findings = find_staged_reversions(repo_root)
    except RuntimeError as exc:
        # The index could not be read, so nothing was established. Report the
        # unestablished state instead of printing a clean verdict over a scope
        # this gate never saw.
        emit_yaml(
            {
                "state": "unestablished",
                "findings": [],
                "error": str(exc),
                # Folded in from the deleted human renderer: the raw git error
                # alone never said that NOTHING was inspected, nor how to make the
                # index readable again.
                "detail": (
                    f"git could not read the index at {repo_root!r}, so no staged path "
                    "was inspected."
                ),
                "remediation": (
                    "Fix the repository access (e.g. run from inside the repo, or "
                    "`git config --global --add safe.directory <path>` for a "
                    "dubious-ownership checkout) and re-run."
                ),
            }
        )
        return 1

    payload: dict = {
        "state": "clean" if not findings else "blocked",
        "findings": [f.to_dict() for f in findings],
    }
    if not findings:
        payload["detail"] = "no staged reversion of committed files"
    else:
        # Per-path recovery already rides on each finding; what only the deleted
        # renderer carried is WHY this blocks (a commit now silently re-introduces
        # removed code with every gate green) and the acknowledged escape.
        payload["detail"] = (
            f"staged reversion of {len(findings)} already-committed file(s) detected. "
            "The index holds a blob that is in neither the commit nor the working copy; "
            "committing now would silently re-introduce removed code with all gates "
            "green (#258)."
        )
        payload["escape"] = (
            "If this staged reversion is intentional, re-run with "
            f"--allow-staged-reversion or set {_ENV_BYPASS}=1."
        )
    emit_yaml(payload)
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
