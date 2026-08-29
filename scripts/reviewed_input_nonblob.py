"""What a path binds when its content is NOT file bytes.

Split from `scripts/reviewed_input_identity.py`, which owns assembling an
identity from a repository. Two path kinds answer "what did I read" with
something other than a blob, and both were unbindable before:

- a SUBMODULE is a commit id, not a tree, so `git show <ref>:<path>` cannot read
  it and "declare the individual files" names files that do not exist;
- a CURRENT POINTER is a selection, so its meaning is the record it names plus
  that record's bytes, not the pointer file itself.

Kept a leaf, and loaded the same deterministic way the verification module
resolves its own sibling: the shipped reviewer runtime loads these files BY PATH,
so "which module is this" must not depend on what a consumer happens to have
importable or on who imported first.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


def _git_bytes_optional(repo_root: Path, *args: str) -> bytes | None:
    result = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _lexical_path(path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root")
    return relative


CURRENT_POINTER_FILENAME = "latest.md"


def _current_pointer_payload(repo_root: Path, path: str) -> str | None:
    """Digest of a current-pointer symlink: its TARGET NAME and that target's bytes.

    Binding the payload rather than dropping the path. An earlier cut excluded the
    pointer from the sweep, which a fresh-eye review blocked on and was right to:
    `auto_excluded_paths` sits in `PROVENANCE_FIELDS` and is never digested, so
    retargeting `latest.md` at a DIFFERENT record left the identity unchanged and
    an approved verdict silently followed the move.

    The TARGET CONTENT is folded in too. Binding only `readlink` caught a
    retarget but not an edit to the record the pointer names -- and a pointer
    whose selected record is rewritten in place selects different bytes for every
    consumer while reading as unchanged. The link is still never followed for
    traversal: the target is resolved lexically inside the repo, and a pointer
    escaping the root refuses rather than binding something outside it.
    """
    if Path(path).name != CURRENT_POINTER_FILENAME:
        return None
    candidate = repo_root / _lexical_path(path)
    if not candidate.is_symlink():
        return None
    target = os.readlink(candidate)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(
            f"reviewed path `{path}` is a current pointer resolving outside repo root"
        ) from exc
    try:
        selected = _sha256(resolved.read_bytes()) if resolved.is_file() else "absent"
    except OSError:
        selected = "unreadable"
    return _sha256(
        b"current-pointer\0" + os.fsencode(target) + b"\0" + selected.encode("ascii")
    )
def _gitlink_commit(repo_root: Path, path: str, base_head: str | None) -> str | None:
    """The submodule commit id recorded for `path`, or None when it is not a gitlink.

    The object-id column differs per command and reading the wrong one is silent:
    `ls-tree` prints `<mode> <type> <object>` while `ls-files -s` prints
    `<mode> <object> <stage>`. Taking field 2 from both bound the STAGE NUMBER --
    the constant `0` -- for every working-tree submodule, so no submodule change
    could ever stale an identity. Caught by a fresh-eye review; the test that
    should have caught it asserted only `captured` and never that the digest
    tracked the commit.
    """
    if base_head is not None:
        raw = _git_bytes_optional(repo_root, "ls-tree", base_head, "--", path)
        object_field = 2
    else:
        raw = _git_bytes_optional(repo_root, "ls-files", "-s", "--", path)
        object_field = 1
    if not raw:
        return None
    fields = raw.decode("utf-8", errors="surrogateescape").split()
    if len(fields) <= object_field or fields[0] != "160000":
        return None
    if base_head is not None:
        return fields[object_field]
    # Working-tree substrate: bind the commit the submodule is CHECKED OUT at,
    # not the one the index records. A reviewer reads the working tree, and
    # moving the submodule's HEAD without staging it left the index entry --
    # and therefore the identity -- unchanged, so a changed reviewed input
    # verified as current.
    #
    # The toplevel is proven to BE this path first. Git repository discovery
    # walks upward, so `git -C <uninitialised-submodule> rev-parse HEAD` returns
    # the SUPERPROJECT's HEAD -- an unrelated commit bound as if it were the
    # submodule's. An uninitialised submodule has nothing checked out to read,
    # which is exactly when the index entry is the honest answer.
    submodule_root = repo_root / _lexical_path(path)
    toplevel = _git_bytes_optional(submodule_root, "rev-parse", "--show-toplevel")
    if toplevel is not None:
        resolved = Path(toplevel.decode("utf-8", errors="surrogateescape").strip())
        if resolved.resolve() == submodule_root.resolve():
            checked_out = _git_bytes_optional(submodule_root, "rev-parse", "HEAD")
            if checked_out is not None:
                return checked_out.decode("utf-8", errors="surrogateescape").strip()
    return fields[object_field]
def _gitlink_sha256(repo_root: Path, path: str, base_head: str | None) -> str | None:
    """Digest of a SUBMODULE pointer (gitlink), or None when the path is not one.

    A submodule bump had no valid declaration in either substrate: committed-ref
    refused with `null-content-hash` because `git show <ref>:<path>` cannot read a
    gitlink, and working-tree refused it as "a directory; declare the individual
    files" -- with no individual files to declare, because a gitlink is a commit
    id, not a tree. Both refusals correct alone, and their intersection made a
    dependency bump unreviewable.

    The commit id IS the content here: bumping a submodule changes exactly that
    one value, and it is what a reviewer judges.
    """
    commit = _gitlink_commit(repo_root, path, base_head)
    if commit is None:
        return None
    return _sha256(b"gitlink\0" + commit.encode("ascii"))
