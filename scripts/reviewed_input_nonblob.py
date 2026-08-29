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
    """None on any failure, INCLUDING a missing working directory.

    `subprocess.run(cwd=...)` raises `FileNotFoundError` when the directory is
    gone, which a function named `_optional` must not do to its caller: a
    submodule deleted from disk while its gitlink stays in the index crashed
    identity construction outright instead of falling through to the pre-image
    that the removed-submodule support exists to bind.
    """
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True)
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _lexical_path(path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root")
    return relative


CURRENT_POINTER_FILENAME = "latest.md"
GitlinkSnapshot = dict[tuple[Path, str, str | None], str | None]
GitObjectSnapshot = dict[tuple[Path, str], bytes | None]


def _object_or_show(
    repo_root: Path, spec: str, snapshot: GitObjectSnapshot | None
) -> bytes | None:
    key = (repo_root.resolve(), spec)
    if snapshot is not None and key in snapshot:
        return snapshot[key]
    return _git_bytes_optional(repo_root, "show", spec)


def _parse_cat_file_batch(
    output: bytes, specs: list[str]
) -> dict[str, bytes | None] | None:
    values: dict[str, bytes | None] = {}
    offset = 0
    for spec in specs:
        header_end = output.find(b"\n", offset)
        if header_end < 0:
            return None
        fields = output[offset:header_end].split()
        offset = header_end + 1
        if len(fields) >= 2 and fields[1] == b"missing":
            values[spec] = None
            continue
        if len(fields) < 3:
            return None
        try:
            size = int(fields[2])
        except ValueError:
            return None
        payload = output[offset : offset + size]
        if len(payload) != size or output[offset + size : offset + size + 1] != b"\n":
            return None
        values[spec] = payload
        offset += size + 1
    return values


def _git_objects_optional(
    repo_root: Path, specs: list[str], snapshot: GitObjectSnapshot | None = None
) -> dict[str, bytes | None]:
    """Read several blob specs in one ``cat-file --batch`` request.

    Missing objects remain ``None`` just like the old per-path ``git show`` calls. The
    fallback is deliberately per-spec: unusual paths that cannot be represented by the
    batch protocol, or a Git without the command, retain the old refusal semantics.
    """
    root = repo_root.resolve()
    cache = snapshot if snapshot is not None else {}
    pending = [spec for spec in dict.fromkeys(specs) if (root, spec) not in cache]
    if pending:
        if any("\n" in spec or "\0" in spec for spec in pending):
            for spec in pending:
                cache[(root, spec)] = _git_bytes_optional(repo_root, "show", spec)
        else:
            try:
                result = subprocess.run(
                    ["git", "cat-file", "--batch"],
                    cwd=repo_root,
                    input=b"".join(
                        spec.encode("utf-8", errors="surrogateescape") + b"\n"
                        for spec in pending
                    ),
                    check=False,
                    capture_output=True,
                )
            except OSError:
                result = None
            if result is None or result.returncode != 0:
                for spec in pending:
                    cache[(root, spec)] = _git_bytes_optional(repo_root, "show", spec)
            else:
                parsed = _parse_cat_file_batch(result.stdout, pending)
                if parsed is None:
                    for spec in pending:
                        cache[(root, spec)] = _git_bytes_optional(repo_root, "show", spec)
                else:
                    for spec, value in parsed.items():
                        cache[(root, spec)] = value
    return {spec: cache[(root, spec)] for spec in specs}


def _gitlink_snapshot_for_paths(
    repo_root: Path, paths: list[str], base_head: str | None
) -> GitlinkSnapshot:
    """Discover gitlinks for several paths with one index/tree listing."""
    snapshot: GitlinkSnapshot = {}
    if not paths:
        return snapshot
    args = (
        ["ls-tree", "-z", base_head, "--", *paths]
        if base_head is not None
        else ["ls-files", "-s", "-z", "--", *paths]
    )
    raw = _git_bytes_optional(repo_root, *args)
    if raw is None:
        return snapshot
    root = repo_root.resolve()
    for path in paths:
        snapshot[(root, path, base_head)] = None
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or not fields or fields[0] != b"160000":
            continue
        path = raw_path.decode("utf-8", errors="surrogateescape")
        if path not in paths:
            continue
        if base_head is not None:
            commit = fields[2].decode("ascii")
        else:
            commit = _gitlink_commit(
                repo_root,
                path,
                None,
                index_commit=fields[1].decode("ascii"),
            )
        snapshot[(root, path, base_head)] = (
            _sha256(b"gitlink\0" + commit.encode("ascii")) if commit is not None else None
        )
    return snapshot


def _prepare_path_snapshots(
    repo_root: Path,
    paths: list[str],
    *,
    base_head: str,
    committed_ref: bool,
    preimage_refs: list[str] | None,
    gitlink_snapshot: GitlinkSnapshot,
    git_object_snapshot: GitObjectSnapshot,
    current_pointer_payload,
    worktree_content_sha256,
) -> None:
    """Populate request-scoped object and gitlink snapshots before path reduction."""
    if not paths:
        return
    if committed_ref:
        target_specs = [f"{base_head}:{path}" for path in paths]
        target_content = _git_objects_optional(
            repo_root, target_specs, git_object_snapshot
        )
        missing_target = [
            path for path, spec in zip(paths, target_specs) if target_content[spec] is None
        ]
        if not missing_target:
            return
        gitlink_snapshot.update(
            _gitlink_snapshot_for_paths(repo_root, missing_target, base_head)
        )
        for preimage_ref in preimage_refs or ():
            gitlink_snapshot.update(
                _gitlink_snapshot_for_paths(repo_root, missing_target, preimage_ref)
            )
            _git_objects_optional(
                repo_root,
                [f"{preimage_ref}:{path}" for path in missing_target],
                git_object_snapshot,
            )
        return
    needs_index = [
        path
        for path in paths
        if current_pointer_payload(repo_root, path) is None
        and worktree_content_sha256(repo_root, path) is None
    ]
    if not needs_index:
        return
    unknown_gitlinks = [
        path
        for path in needs_index
        if (repo_root.resolve(), path, None) not in gitlink_snapshot
    ]
    gitlink_snapshot.update(
        _gitlink_snapshot_for_paths(repo_root, unknown_gitlinks, None)
    )
    needs_staged = [
        path
        for path in needs_index
        if gitlink_snapshot.get((repo_root.resolve(), path, None)) is None
    ]
    staged_specs = [f":{path}" for path in needs_staged]
    staged_content = _git_objects_optional(
        repo_root, staged_specs, git_object_snapshot
    )
    needs_head = [
        path
        for path, spec in zip(needs_staged, staged_specs)
        if staged_content[spec] is None
    ]
    if needs_head:
        gitlink_snapshot.update(
            _gitlink_snapshot_for_paths(repo_root, needs_head, base_head)
        )
        _git_objects_optional(
            repo_root,
            [f"{base_head}:{path}" for path in needs_head],
            git_object_snapshot,
        )


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
def _gitlink_commit(
    repo_root: Path,
    path: str,
    base_head: str | None,
    *,
    index_commit: str | None = None,
) -> str | None:
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
    elif index_commit is None:
        raw = _git_bytes_optional(repo_root, "ls-files", "-s", "--", path)
        object_field = 1
    else:
        raw = None
        object_field = 1
    if index_commit is not None:
        fields = ["160000", index_commit, "0"]
    elif raw:
        fields = raw.decode("utf-8", errors="surrogateescape").split()
    else:
        fields = []
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
    checked_out_snapshot = _git_bytes_optional(
        submodule_root, "rev-parse", "--show-toplevel", "HEAD"
    )
    if checked_out_snapshot is not None:
        snapshot_lines = checked_out_snapshot.decode(
            "utf-8", errors="surrogateescape"
        ).splitlines()
        if len(snapshot_lines) != 2:
            return fields[object_field]
        resolved = Path(snapshot_lines[0].strip())
        if resolved.resolve() == submodule_root.resolve():
            return snapshot_lines[1].strip()
    return fields[object_field]
def _gitlink_sha256(
    repo_root: Path,
    path: str,
    base_head: str | None,
    snapshot: GitlinkSnapshot | None = None,
) -> str | None:
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
    key = (repo_root.resolve(), path, base_head)
    if snapshot is not None and key in snapshot:
        return snapshot[key]
    commit = _gitlink_commit(repo_root, path, base_head)
    if commit is None:
        if snapshot is not None:
            snapshot[key] = None
        return None
    digest = _sha256(b"gitlink\0" + commit.encode("ascii"))
    if snapshot is not None:
        snapshot[key] = digest
    return digest
