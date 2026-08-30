"""Deterministic binding between a critique verdict and its declared inputs."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ALGORITHM = "sha256-v2"
SUBSTRATE_WORKING_TREE = "working-tree"
SUBSTRATE_COMMITTED_REF = "committed-ref"
SUBSTRATE_MODES = frozenset({SUBSTRATE_WORKING_TREE, SUBSTRATE_COMMITTED_REF})
_LEGACY_SUBSTRATE_MODE_ALIASES = {
    "changed-ref": SUBSTRATE_COMMITTED_REF,
    "committed": SUBSTRATE_COMMITTED_REF,
    "worktree": SUBSTRATE_WORKING_TREE,
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
# Owned by `scripts/artifact_naming_lib.py`, restated rather than imported. The
# shipped reviewer runtime loads this file BY PATH (`spec_from_file_location`),
# with no package context, so a sibling import would not resolve there.
# `validate_quality_artifact.py` restates it the same way; a test asserts the two
# agree, so the copy cannot drift silently.
CURRENT_POINTER_FILENAME = "latest.md"
# The identity ignores the index/worktree split and untracked-set membership,
# so a plain `git add` of an unchanged reviewed path does not stale-flag a
# binding that was current a second earlier. In working-tree mode the bytes the
# reviewers actually read are already covered by `reviewed_content`, so v2 keeps these
# fields as provenance and drops them from the digest.
WORKING_TREE_PROVENANCE_FIELDS = (
    "base_head",
    "staged_patch_sha256",
    "unstaged_patch_sha256",
    "declared_untracked",
)
# Never digested: what the auto sweep dropped is a report about the selection,
# not an input, and `reviewed_paths` is the binding record of what was selected.
PROVENANCE_FIELDS = ("auto_excluded_paths",)


class ReviewedInputError(ValueError):
    """Typed refusal while constructing or validating a review substrate."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _fail(code: str, message: str) -> None:
    raise ReviewedInputError(code, message)


def _substrate_mode(changed_ref: str | None, substrate_mode: str | None) -> str:
    inferred = SUBSTRATE_COMMITTED_REF if changed_ref else SUBSTRATE_WORKING_TREE
    mode = substrate_mode or inferred
    if mode not in SUBSTRATE_MODES:
        _fail(
            "invalid-substrate-mode",
            f"substrate mode must be `{SUBSTRATE_WORKING_TREE}` or `{SUBSTRATE_COMMITTED_REF}`",
        )
    if mode == SUBSTRATE_WORKING_TREE and changed_ref:
        _fail("substrate-ref-mismatch", "working-tree substrate cannot declare changed_ref")
    if mode == SUBSTRATE_COMMITTED_REF and not changed_ref:
        _fail("substrate-ref-missing", "committed-ref substrate requires changed_ref")
    return mode




def _git_bytes(repo_root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True)
    if result.returncode != 0:
        raise ValueError(
            f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}"
        )
    return result.stdout


def _git_bytes_optional(repo_root: Path, *args: str) -> bytes | None:
    result = subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_changed_path_owner():
    """Load the adjacent surface module even when this file is loaded by path."""
    sibling = Path(__file__).resolve().with_name("surfaces_lib.py")
    canonical = "scripts.surfaces_lib"
    loaded = sys.modules.get(canonical)
    if loaded is not None and Path(getattr(loaded, "__file__", "")).resolve() == sibling:
        return loaded
    try:
        spec = importlib.util.find_spec(canonical)
    except (ImportError, ValueError):
        spec = None
    if spec is not None and spec.origin and Path(spec.origin).resolve() == sibling:
        return importlib.import_module(canonical)
    spec = importlib.util.spec_from_file_location("charness_surfaces_lib", sibling)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load changed-path owner from {sibling}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_changed_path_owner = _load_changed_path_owner()


def _auto_paths(repo_root: Path, changed_ref: str | None) -> list[str]:
    """Delegate changed-path selection to the surface module's single owner."""
    try:
        if changed_ref:
            return _changed_path_owner.collect_changed_paths_for_ref(repo_root, changed_ref)
        return _changed_path_owner.collect_changed_paths(repo_root)
    except _changed_path_owner.SurfaceError as exc:
        raise ValueError(str(exc)) from exc


def _lexical_path(path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root")
    return relative


def _checked_path(repo_root: Path, path: str) -> Path:
    relative = _lexical_path(path)
    candidate = repo_root.resolve() / relative
    if candidate.is_symlink():
        raise ValueError(
            f"reviewed path `{path}` is a symlink; declare the target file explicitly"
        )
    resolved_for_boundary = candidate.resolve()
    try:
        resolved_for_boundary.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root") from exc
    return candidate


def _worktree_content_sha256(repo_root: Path, path: str) -> str | None:
    try:
        # No symlink arm: `_checked_path` above refuses symlinks (f7a09d672), so
        # the link-payload branch that used to sit here was unreachable from the
        # moment that approval boundary landed, and the public contract went on
        # describing it. Removed rather than left as decoration.
        candidate = _checked_path(repo_root, path)
        if not candidate.is_file():
            return None
        # The exec bit belongs in the content digest: otherwise `chmod +x` on a
        # reviewed script would pass as unchanged because its bytes are identical.
        mode_tag = b"x\0" if candidate.stat().st_mode & 0o111 else b"-\0"
        return _sha256(b"file\0" + mode_tag + candidate.read_bytes())
    except OSError:
        return None


def _load_nonblob():
    """The adjacent non-blob binder, resolved the same deterministic way the
    verification module resolves this file.

    Order is load-bearing: preferring the package import would let any
    already-importable module of that name win, and falling back to a by-path
    load whenever the canonical name is unbound would make the object depend on
    who imported first. Both were real defects here, one found by a fresh-eye
    review and one by the full suite.
    """
    sibling = Path(__file__).resolve().with_name("reviewed_input_nonblob.py")
    canonical = "scripts.reviewed_input_nonblob"
    loaded = sys.modules.get(canonical)
    loaded_file = getattr(loaded, "__file__", None)
    if loaded_file is not None and Path(loaded_file).resolve() == sibling:
        return loaded
    if sibling.is_file():
        try:
            spec = importlib.util.find_spec(canonical)
        except (ImportError, ValueError):
            spec = None
        if spec is not None and spec.origin and Path(spec.origin).resolve() == sibling:
            return importlib.import_module(canonical)
        spec = importlib.util.spec_from_file_location("charness_reviewed_input_nonblob", sibling)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    from scripts import reviewed_input_nonblob as module  # noqa: PLC0415

    return module


_nonblob = _load_nonblob()
_current_pointer_payload = _nonblob._current_pointer_payload
_gitlink_sha256 = _nonblob._gitlink_sha256


def _unavailable(
    reviewed_paths: list[str] | None,
    changed_ref: str | None,
    substrate_mode: str,
    reason: str,
) -> dict[str, Any]:
    components = {
        "algorithm": ALGORITHM,
        "status": "unavailable",
        "reason": reason,
        "reviewed_paths": sorted(set(reviewed_paths or [])),
        "changed_ref": changed_ref,
        "substrate_mode": substrate_mode,
        "mode": substrate_mode,
    }
    return _with_identity_digest(components)


def _with_identity_digest(components: dict[str, Any]) -> dict[str, Any]:
    digest_components = dict(components)
    provenance_only = components.get("base_head_role") == "provenance-only"
    for field in PROVENANCE_FIELDS + (WORKING_TREE_PROVENANCE_FIELDS if provenance_only else ()):
        digest_components.pop(field, None)
    canonical = json.dumps(digest_components, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {**components, "identity_sha256": _sha256(canonical.encode("utf-8"))}








def _review_paths(
    repo_root: Path,
    reviewed_paths: list[str] | None,
    changed_ref: str | None,
    mode: str,
    excluded_paths: list[str] | None,
    excluded_prefixes: list[str] | None,
) -> tuple[list[str], list[str]]:
    auto_excluded: list[str] = []
    if reviewed_paths is None:
        # Exclusions apply to the auto sweep ONLY: an explicit --reviewed-path
        # declaration is what was read and is never silently dropped.
        swept = set(_auto_paths(repo_root, changed_ref))
        prefixes = tuple(excluded_prefixes or ())
        kept = swept - set(excluded_paths or [])
        auto_excluded = sorted(swept - {path for path in kept if not path.startswith(prefixes)})
        paths = sorted(path for path in kept if not path.startswith(prefixes))
    else:
        paths = sorted(set(reviewed_paths))
    if mode == SUBSTRATE_COMMITTED_REF:
        try:
            expected_paths = set(_auto_paths(repo_root, changed_ref))
        except ValueError as exc:
            _fail("changed-ref-unavailable", str(exc))
        if set(paths) != expected_paths:
            _fail(
                "changed-ref-path-mismatch",
                "declared reviewed paths do not exactly match the changed-ref path set "
                f"(declared={sorted(paths)!r}, changed_ref={sorted(expected_paths)!r})",
            )
    for path in paths:
        if changed_ref:
            _lexical_path(path)
            continue
        if _current_pointer_payload(repo_root, path) is not None:
            # Bound by link payload below; `_checked_path` would refuse it as a
            # symlink and the round-trip through `verify` would never close.
            continue
        if _gitlink_sha256(repo_root, path, None) is not None:
            # A gitlink LOOKS like a directory on disk but binds a commit id, so
            # "declare the individual files" names files that do not exist.
            continue
        candidate = _checked_path(repo_root, path)
        if candidate.is_dir() and not candidate.is_symlink():
            raise ValueError(
                f"reviewed path `{path}` is a directory; declare the individual files "
                "that were reviewed, since a directory binds no content"
            )
    return paths, auto_excluded


def _is_range(changed_ref: str) -> bool:
    return ".." in changed_ref


def _range_endpoints(repo_root: Path, changed_ref: str) -> tuple[str | None, str]:
    """(start, target) for a range, or (None, commit) for a single commit.

    ONE owner for what a range means. There used to be two readings of the same
    string in this file: `_auto_paths` handed it to git untouched, so `a...b`
    worked, while `_patch_components` did `changed_ref.split("..", 1)` and turned
    `main...feature` into `("main", ".feature")` -- then `rev-parse .feature`
    raised a bare ValueError and the CLI died with a traceback instead of a typed
    refusal. Two functions in one module disagreeing about their own input is the
    same shape as the cross-module disagreements this class keeps producing.

    `a...b` is git's SYMMETRIC form: `git diff a...b` reports b against the
    merge-base, not against a. Resolving the start to that merge-base is what
    makes the recorded endpoints describe the diff that was actually taken.
    """
    if "..." in changed_ref:
        left_raw, right_raw = changed_ref.split("...", 1)
        left = left_raw or "HEAD"
        right = right_raw or "HEAD"
        merge_base = _git_bytes_optional(repo_root, "merge-base", left, right)
        if merge_base is None:
            _fail(
                "unresolvable-range",
                f"changed ref `{changed_ref}` has no merge base for `{left}` and `{right}`",
            )
        return merge_base.decode().strip(), right
    if ".." in changed_ref:
        left, right = changed_ref.split("..", 1)
        return (left or "HEAD"), (right or "HEAD")
    return None, changed_ref


def _patch_components(
    repo_root: Path, paths: list[str], changed_ref: str | None, mode: str
) -> tuple[list[str], str, bytes, bytes, bytes]:
    path_args = ["--", *paths]
    if mode == SUBSTRATE_COMMITTED_REF:
        start_ref, target_ref = _range_endpoints(repo_root, changed_ref)
        target_head = _git_bytes(repo_root, "rev-parse", target_ref).decode().strip()
        if start_ref is None:
            resolved_ref = [target_head]
        else:
            start_head = _git_bytes(repo_root, "rev-parse", start_ref).decode().strip()
            resolved_ref = [start_head, target_head]
        base_head = target_head
        reviewed_patch = (
            b""
            if not paths
            else _git_bytes(repo_root, "diff", "--binary", changed_ref, *path_args)
            if _is_range(changed_ref)
            else _git_bytes(repo_root, "show", "--format=", "--binary", changed_ref, *path_args)
        )
        return resolved_ref, base_head, reviewed_patch, b"", b""
    base_head = _git_bytes(repo_root, "rev-parse", "HEAD").decode().strip()
    staged_patch = _git_bytes(repo_root, "diff", "--cached", "--binary", *path_args) if paths else b""
    unstaged_patch = _git_bytes(repo_root, "diff", "--binary", *path_args) if paths else b""
    return [], base_head, b"", staged_patch, unstaged_patch


def _preimage_refs(repo_root: Path, changed_ref: str | None) -> list[str]:
    """Every ref a path could have existed at BEFORE the reviewed change.

    A LIST, matching how the paths were enumerated. `_auto_paths` passes `-m` to
    `diff-tree`, so a merge contributes the union of its parent-relative changes;
    resolving the pre-image at `<merge>^` alone then covered only the FIRST
    parent, and a path deleted relative to the second — absent from the merge
    result and from the first parent both — refused with `null-content-hash`.
    Reproduced on this repo's own history at 225d4b152. Enumerating across all
    parents while resolving against one is the same two-halves-disagreeing shape
    these repairs keep closing.

    A range resolves to its single start (the merge base for `a...b`). A root
    commit has no parent, but a root commit deletes nothing, so an empty list
    simply finds no pre-image and the refusal stands.
    """
    if not changed_ref:
        return []
    start_ref, target_ref = _range_endpoints(repo_root, changed_ref)
    if start_ref is not None:
        return [start_ref]
    raw = _git_bytes_optional(repo_root, "rev-list", "--parents", "-n", "1", target_ref)
    if not raw:
        return []
    return raw.decode("utf-8", errors="surrogateescape").split()[1:]


def _committed_ref_digest(
    repo_root: Path, path: str, base_head: str, preimage_refs: list[str] | None
) -> tuple[str | None, bool]:
    """(digest, was_deleted) for one path at a committed ref.

    A path absent at the range's target was DELETED by the range. Ref mode used
    to have no pre-image fallback at all, so `git diff --name-only` (which lists
    deletions) produced a manifest that always refused, while `--diff-filter=d`
    produced one that no longer matched the range -- between them a removal slice
    had no valid declaration.
    """
    content = _git_bytes_optional(repo_root, "show", f"{base_head}:{path}")
    if content is not None:
        return _sha256(content), False
    gitlink = _gitlink_sha256(repo_root, path, base_head)
    if gitlink is not None:
        return gitlink, False
    for preimage_ref in preimage_refs or ():
        previous = _git_bytes_optional(repo_root, "show", f"{preimage_ref}:{path}")
        if previous is not None:
            return _sha256(previous), True
        # `git show <ref>:<path>` cannot read a gitlink, so a REMOVED submodule
        # fell through both the deletion fallback and the gitlink binder.
        removed_gitlink = _gitlink_sha256(repo_root, path, preimage_ref)
        if removed_gitlink is not None:
            return removed_gitlink, True
    return None, False


def _working_tree_digest(repo_root: Path, path: str, base_head: str) -> tuple[str | None, bool]:
    """(digest, was_deleted) for one path in the working tree.

    A deletion is still a reviewed input: bind its pre-change bytes rather than
    treating the missing path as an unreviewable null. The INDEX is consulted
    before HEAD, because a path can be staged and then removed from disk --
    absent from the worktree, absent from HEAD because it is new, present only as
    a staged blob, which IS the reviewed input there.
    """
    digest = _current_pointer_payload(repo_root, path)
    if digest is not None:
        return digest, False
    digest = _worktree_content_sha256(repo_root, path)
    if digest is not None:
        return digest, False
    gitlink = _gitlink_sha256(repo_root, path, None)
    if gitlink is not None:
        return gitlink, False
    staged = _git_bytes_optional(repo_root, "show", f":{path}")
    if staged is not None:
        return _sha256(staged), True
    previous = _git_bytes_optional(repo_root, "show", f"{base_head}:{path}")
    if previous is not None:
        return _sha256(previous), True
    # Same gitlink gap on this side: a submodule removed from index and disk is
    # unreadable by `git show`.
    return _gitlink_sha256(repo_root, path, base_head), True


def _content_components(
    repo_root: Path, paths: list[str], base_head: str, mode: str, preimage_refs: list[str] | None = None
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    untracked: set[str] = set()
    path_args = ["--", *paths]
    if paths and mode == SUBSTRATE_WORKING_TREE:
        raw_untracked = _git_bytes(
            repo_root, "ls-files", "--others", "--exclude-standard", "-z", *path_args
        )
        untracked = set(raw_untracked.decode("utf-8", errors="surrogateescape").split("\0"))
    reviewed_content: list[dict[str, str]] = []
    declared_untracked: list[dict[str, str]] = []
    for path in paths:
        if mode == SUBSTRATE_COMMITTED_REF:
            digest, deleted = _committed_ref_digest(repo_root, path, base_head, preimage_refs)
        else:
            digest, deleted = _working_tree_digest(repo_root, path, base_head)
        if digest is None:
            _fail(
                "null-content-hash",
                f"reviewed path `{path}` has no content hash in the {mode} substrate",
            )
        entry: dict[str, str] = {"path": path, "content_sha256": digest}
        if deleted:
            # Marked ONLY on deletions, deliberately. Stamping every entry with a
            # disposition would change the digest of every identity ever captured
            # and read as "stale" across the whole corpus; a deleted entry could
            # not exist before this change, so no prior identity moves.
            #
            # The hash is the PRE-IMAGE, so it answers "what was removed", and the
            # marker is what stops that from reading as "this file is present with
            # these bytes" -- the two facts a reviewer needs to judge a removal.
            entry["disposition"] = "deleted"
        reviewed_content.append(entry)
        if path in untracked:
            declared_untracked.append(entry)
    return reviewed_content, declared_untracked


def build_reviewed_input_identity(
    *,
    repo_root: Path,
    reviewed_paths: list[str] | None = None,
    changed_ref: str | None = None,
    substrate_mode: str | None = None,
    excluded_paths: list[str] | None = None,
    excluded_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    mode = _substrate_mode(changed_ref, substrate_mode)
    try:
        _git_bytes(repo_root, "rev-parse", "--is-inside-work-tree")
    except ValueError as exc:
        return _unavailable(reviewed_paths, changed_ref, mode, str(exc))

    paths, auto_excluded = _review_paths(
        repo_root,
        reviewed_paths,
        changed_ref,
        mode,
        excluded_paths,
        excluded_prefixes,
    )
    resolved_ref, base_head, reviewed_patch, staged_patch, unstaged_patch = _patch_components(
        repo_root, paths, changed_ref, mode
    )
    reviewed_content, declared_untracked = _content_components(
        repo_root, paths, base_head, mode, _preimage_refs(repo_root, changed_ref)
    )

    captured: dict[str, Any] = {
        "algorithm": ALGORITHM,
        "status": "captured",
        "mode": mode,
        "substrate_mode": mode,
        "changed_ref": changed_ref,
        "resolved_changed_ref": resolved_ref,
        "base_head": base_head,
        "base_head_role": "target" if changed_ref else "provenance-only",
        "reviewed_paths": paths,
        "reviewed_content": reviewed_content,
        "reviewed_patch_sha256": _sha256(reviewed_patch),
        "staged_patch_sha256": _sha256(staged_patch),
        "unstaged_patch_sha256": _sha256(unstaged_patch),
        "declared_untracked": declared_untracked,
    }
    captured["auto_excluded_paths"] = auto_excluded
    return _with_identity_digest(captured)
