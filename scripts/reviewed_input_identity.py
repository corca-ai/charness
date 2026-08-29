"""Deterministic binding between a critique verdict and its declared inputs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import date
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
ARTIFACT_HEADING = "## Reviewed Input Identity"
# floor-addition-restraint: keep — this typed form is consumed at release/closeout,
# where silently reusing a stale verdict can escape an irreversible boundary;
# enforcement is limited to packet-bound critiques and grandfathered by date.
ARTIFACT_REQUIRED_FIELDS = ("packet path", "packet sha256", "identity sha256")
ARTIFACT_BINDING_RULE_DATE = date(2026, 7, 20)
LEGACY_UNDATED_ARTIFACTS = frozenset({"release-0-55-1-critique.md"})


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


def artifact_binding_required(path_name: str, observed_date: date | None, packet_consumed: bool) -> bool:
    if not packet_consumed:
        return False
    if observed_date is not None:
        return observed_date >= ARTIFACT_BINDING_RULE_DATE
    return path_name not in LEGACY_UNDATED_ARTIFACTS


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


def _auto_paths(repo_root: Path, changed_ref: str | None) -> list[str]:
    if changed_ref and ".." in changed_ref:
        raw = _git_bytes(repo_root, "diff", "--name-only", "-z", changed_ref)
    elif changed_ref:
        raw = _git_bytes(
            repo_root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "-r",
            "-z",
            changed_ref,
        )
    else:
        raw = _git_bytes(repo_root, "diff", "--name-only", "-z", "HEAD")
        raw += _git_bytes(repo_root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted({path.decode("utf-8", errors="surrogateescape") for path in raw.split(b"\0") if path})


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
        candidate = _checked_path(repo_root, path)
        if candidate.is_symlink():
            return _sha256(b"symlink\0" + os.fsencode(os.readlink(candidate)))
        if not candidate.is_file():
            return None
        # The exec bit belongs in the content digest: otherwise `chmod +x` on a
        # reviewed script would pass as unchanged because its bytes are identical.
        mode_tag = b"x\0" if candidate.stat().st_mode & 0o111 else b"-\0"
        return _sha256(b"file\0" + mode_tag + candidate.read_bytes())
    except OSError:
        return None


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
        if not changed_ref:
            # A DECLARED symlink still refuses, deliberately -- `_checked_path`
            # owns that boundary and its test names the remedy. But the auto
            # sweep is not a declaration, and this repo's own artifact
            # convention puts a `latest.md` symlink in every family. Refreshing
            # one -- the documented step after filing any record -- put a
            # modified symlink in the change set and made `build_packet` refuse
            # outright, so every session that filed a record could not be
            # reviewed until it committed. Dropping it from the SWEEP keeps the
            # boundary and removes the self-inflicted refusal; the path is
            # reported in `auto_excluded_paths`, so it is never silent.
            kept = {path for path in kept if not (repo_root / _lexical_path(path)).is_symlink()}
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
        candidate = _checked_path(repo_root, path)
        if candidate.is_dir() and not candidate.is_symlink():
            raise ValueError(
                f"reviewed path `{path}` is a directory; declare the individual files "
                "that were reviewed, since a directory binds no content"
            )
    return paths, auto_excluded


def _patch_components(
    repo_root: Path, paths: list[str], changed_ref: str | None, mode: str
) -> tuple[list[str], str, bytes, bytes, bytes]:
    path_args = ["--", *paths]
    if mode == SUBSTRATE_COMMITTED_REF:
        if ".." in changed_ref:
            start_ref, target_ref = changed_ref.split("..", 1)
            start_head = _git_bytes(repo_root, "rev-parse", start_ref).decode().strip()
            target_head = _git_bytes(repo_root, "rev-parse", target_ref).decode().strip()
            resolved_ref = [start_head, target_head]
        else:
            target_head = _git_bytes(repo_root, "rev-parse", changed_ref).decode().strip()
            resolved_ref = [target_head]
        base_head = target_head
        reviewed_patch = (
            b""
            if not paths
            else _git_bytes(repo_root, "diff", "--binary", changed_ref, *path_args)
            if ".." in changed_ref
            else _git_bytes(repo_root, "show", "--format=", "--binary", changed_ref, *path_args)
        )
        return resolved_ref, base_head, reviewed_patch, b"", b""
    base_head = _git_bytes(repo_root, "rev-parse", "HEAD").decode().strip()
    staged_patch = _git_bytes(repo_root, "diff", "--cached", "--binary", *path_args) if paths else b""
    unstaged_patch = _git_bytes(repo_root, "diff", "--binary", *path_args) if paths else b""
    return [], base_head, b"", staged_patch, unstaged_patch


def _preimage_ref(changed_ref: str | None) -> str | None:
    """The ref a path existed at BEFORE the reviewed range, or None outside ref mode.

    A range `a..b` has its pre-image at `a`. A single commit `c` has it at `c^`;
    a root commit has no parent, but a root commit deletes nothing, so the
    lookup that follows simply finds no pre-image and the refusal stands.
    """
    if not changed_ref:
        return None
    if ".." in changed_ref:
        return changed_ref.split("..", 1)[0]
    return f"{changed_ref}^"


def _content_components(
    repo_root: Path, paths: list[str], base_head: str, mode: str, preimage_ref: str | None = None
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
        deleted = False
        if mode == SUBSTRATE_COMMITTED_REF:
            content = _git_bytes_optional(repo_root, "show", f"{base_head}:{path}")
            digest = _sha256(content) if content is not None else None
            # A path absent at the range's target was DELETED by the range. The
            # working-tree substrate below has always bound such a path to its
            # pre-change bytes; ref mode did not, so `git diff --name-only`
            # (which lists deletions) produced a manifest that always refused,
            # while `--diff-filter=d` produced one that no longer matched the
            # range. Between them a removal slice had no valid declaration at
            # all -- exactly the change class a fresh-eye review is worth most.
            if digest is None and preimage_ref is not None:
                previous = _git_bytes_optional(repo_root, "show", f"{preimage_ref}:{path}")
                if previous is not None:
                    digest = _sha256(previous)
                    deleted = True
        else:
            digest = _worktree_content_sha256(repo_root, path)
            # A deletion is still a reviewed input: bind its pre-change bytes
            # from the working-tree base instead of treating the missing path
            # as an unreviewable null. This keeps destructive migrations
            # auditable without resurrecting the file in the worktree.
            if digest is None:
                previous = _git_bytes_optional(repo_root, "show", f"{base_head}:{path}")
                digest = _sha256(previous) if previous is not None else None
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
        repo_root, paths, base_head, mode, _preimage_ref(changed_ref)
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


def verify_reviewed_input_identity(repo_root: Path, identity: dict[str, Any]) -> tuple[bool, str]:
    if identity.get("status") != "captured":
        return False, "reviewed input identity was unavailable when the packet was produced"
    if identity.get("algorithm") != ALGORITHM:
        return False, f"reviewed input identity must use `{ALGORITHM}`"
    if "reviewed_paths" not in identity or identity.get("reviewed_paths") is None:
        return False, "declared reviewed inputs cover zero paths"
    if not isinstance(identity.get("reviewed_paths"), list):
        return False, "cannot reconstruct reviewed input identity: reviewed_paths must be a list"
    if not identity.get("reviewed_paths"):
        # An empty path set digests to the same constant in every repo forever, so
        # it would verify as `current` while proving nothing. Reject it as a
        # binding rather than let a zero-input verdict read as a checked one.
        return False, "declared reviewed inputs cover zero paths"
    mode = identity.get("substrate_mode") or identity.get("mode")
    mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(mode, mode)
    if mode not in SUBSTRATE_MODES or identity.get("mode") != mode:
        return False, "reviewed input identity has an invalid or missing substrate mode"
    if (mode == SUBSTRATE_COMMITTED_REF) != bool(identity.get("changed_ref")):
        return False, "reviewed input identity substrate mode does not match changed_ref"
    try:
        current = build_reviewed_input_identity(
            repo_root=repo_root,
            reviewed_paths=list(identity["reviewed_paths"]),
            changed_ref=identity.get("changed_ref"),
            substrate_mode=mode,
        )
    except ReviewedInputError as exc:
        return False, f"{exc.code}: {exc}"
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"cannot reconstruct reviewed input identity: {exc}"
    for item in current.get("reviewed_content", []):
        if not isinstance(item, dict) or not _SHA256_RE.fullmatch(str(item.get("content_sha256", ""))):
            return False, "reviewed input identity contains a null or invalid content hash"
    for field in ("reviewed_patch_sha256", "staged_patch_sha256", "unstaged_patch_sha256"):
        if not _SHA256_RE.fullmatch(str(current.get(field, ""))):
            return False, f"reviewed input identity contains a null or invalid {field}"
    if current["identity_sha256"] != identity.get("identity_sha256"):
        return False, "declared reviewed inputs are stale"
    return True, "current"


def packet_file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _canonical_packet_path(repo_root: Path, packet_path: str) -> tuple[Path | None, str | None]:
    raw = Path(packet_path)
    if raw.is_absolute() or ".." in raw.parts:
        return None, "reviewed packet path resolves outside repo root"
    lexical = repo_root / raw
    if lexical.is_symlink():
        return None, "reviewed packet path must not be a symlink"
    candidate = lexical.resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return None, "reviewed packet path resolves outside repo root"
    return candidate, None


def verify_packet_binding(
    *,
    repo_root: Path,
    packet_path: str,
    packet_sha256: str,
    identity_sha256: str,
    expected_kind: str,
    check_current: bool = True,
) -> tuple[bool, str]:
    candidate, path_error = _canonical_packet_path(repo_root, packet_path)
    if path_error is not None or candidate is None:
        return False, path_error or "reviewed packet path is invalid"
    if not candidate.is_file():
        return False, f"reviewed packet does not exist: {packet_path}"
    packet_bytes = candidate.read_bytes()
    if not _SHA256_RE.fullmatch(str(packet_sha256)):
        return False, "packet sha256 is null or invalid"
    if _sha256(packet_bytes) != packet_sha256:
        return False, "reviewed packet bytes are stale or tampered"
    try:
        packet = json.loads(packet_bytes)
    except json.JSONDecodeError:
        return False, "reviewed packet is not valid JSON"
    if packet.get("kind") != expected_kind:
        return False, "reviewed packet has the wrong kind"
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return False, "reviewed packet has no reviewed input identity"
    if identity.get("identity_sha256") != identity_sha256:
        return False, "artifact identity does not match the reviewed packet"
    if not _SHA256_RE.fullmatch(str(identity_sha256)):
        return False, "identity sha256 is null or invalid"
    packet_mode = packet.get("substrate_mode")
    packet_mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(packet_mode, packet_mode)
    identity_mode = identity.get("substrate_mode") or identity.get("mode")
    identity_has_mode = identity_mode is not None
    identity_mode = _LEGACY_SUBSTRATE_MODE_ALIASES.get(identity_mode, identity_mode)
    legacy_packet = packet_mode is None
    if identity_mode is None:
        identity_mode = SUBSTRATE_COMMITTED_REF if packet.get("changed_ref") else SUBSTRATE_WORKING_TREE
    # Historical v1 packets carried the mode only inside the reviewed-input
    # identity.  Preserve that immutable evidence while requiring all newly
    # produced packets to emit the top-level field.
    if packet_mode is None:
        packet_mode = identity_mode
    if packet_mode not in SUBSTRATE_MODES or identity_mode != packet_mode:
        return False, "packet and reviewed input identity substrate modes do not match"
    if packet.get("changed_ref") != identity.get("changed_ref"):
        return False, "packet and reviewed input identity changed_ref values do not match"
    if check_current and identity_has_mode:
        return verify_reviewed_input_identity(repo_root, identity)
    return True, "legacy-packet-integrity-only" if legacy_packet else "packet-integrity-only"


def verify_artifact_binding(
    artifact_path: Path,
    fields: dict[str, str],
    *,
    expected_kind: str,
    check_current: bool = True,
    repo_root: Path | None = None,
) -> tuple[bool, str]:
    resolved_root = repo_root.resolve() if repo_root is not None else None
    if resolved_root is None:
        # Prefer the known artifact layout before scanning ancestors. A nested
        # test checkout can live below an unrelated `.git` directory (for
        # example a shared temp root); selecting that first makes a valid
        # packet look like a wrong-path/missing-file failure.
        if len(artifact_path.resolve().parents) >= 3:
            layout_root = artifact_path.resolve().parents[2]
            if (layout_root / fields.get("packet path", "")).is_file():
                resolved_root = layout_root
        if resolved_root is None:
            resolved_root = next(
                (parent for parent in artifact_path.resolve().parents if (parent / ".git").exists()),
                None,
            )
        # Artifacts produced under the canonical `charness-artifacts/<kind>/`
        # layout still need a deterministic root when a fixture has no `.git`
        # directory. Keep the layout fallback even when the packet is missing:
        # the caller should receive the typed missing-packet refusal, not a
        # misleading repository-root discovery failure.
        if resolved_root is None and len(artifact_path.resolve().parents) >= 3:
            resolved_root = artifact_path.resolve().parents[2]
    if resolved_root is None:
        return False, "cannot resolve repository root for reviewed input binding"
    return verify_packet_binding(
        repo_root=resolved_root,
        packet_path=fields["packet path"],
        packet_sha256=fields["packet sha256"],
        identity_sha256=fields["identity sha256"],
        expected_kind=expected_kind,
        check_current=check_current,
    )


def verify_declared_binding(
    artifact_path: Path,
    fields: dict[str, str],
    *,
    required: bool,
    required_fields: tuple[str, ...],
    expected_kind: str,
    check_current: bool = True,
    repo_root: Path | None = None,
) -> tuple[bool, str]:
    if not fields:
        if required:
            return False, f"packet-bound critique must declare fields {list(required_fields)}"
        return True, "not-declared"
    missing = [field for field in required_fields if not fields.get(field)]
    if missing:
        return False, f"reviewed input identity missing fields: {missing}"
    return verify_artifact_binding(
        artifact_path,
        fields,
        expected_kind=expected_kind,
        check_current=check_current,
        repo_root=repo_root,
    )
