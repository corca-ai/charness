"""Deterministic binding between a critique verdict and its declared inputs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

ALGORITHM = "sha256-v2"
SUPPORTED_ALGORITHMS = ("sha256-v1", "sha256-v2")
# v2 answers #460: v1 folded the index/worktree split and the untracked-set membership
# into the digest, so a plain `git add` of an unchanged reviewed path stale-flagged a
# binding that was current a second earlier. In working-tree mode the bytes the
# reviewers actually read are already covered by `reviewed_content`, so v2 keeps these
# fields as provenance and drops them from the digest.
WORKING_TREE_PROVENANCE_FIELDS = (
    "base_head",
    "staged_patch_sha256",
    "unstaged_patch_sha256",
    "declared_untracked",
)
# Never digested in v2: what the auto sweep dropped is a report about the selection,
# not an input, and `reviewed_paths` is the binding record of what was selected.
PROVENANCE_FIELDS = ("auto_excluded_paths",)
ARTIFACT_HEADING = "## Reviewed Input Identity"
# floor-addition-restraint: keep — this typed form is consumed at release/closeout,
# where silently reusing a stale verdict can escape an irreversible boundary;
# enforcement is limited to packet-bound critiques and grandfathered by date.
ARTIFACT_REQUIRED_FIELDS = ("packet path", "packet sha256", "identity sha256")
ARTIFACT_BINDING_RULE_DATE = date(2026, 7, 20)
LEGACY_UNDATED_ARTIFACTS = frozenset({"release-0-55-1-critique.md"})


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
    resolved_for_boundary = candidate.parent.resolve() if candidate.is_symlink() else candidate.resolve()
    try:
        resolved_for_boundary.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root") from exc
    return candidate


def _worktree_content_sha256(repo_root: Path, path: str, algorithm: str = ALGORITHM) -> str | None:
    try:
        candidate = _checked_path(repo_root, path)
        if candidate.is_symlink():
            return _sha256(b"symlink\0" + os.fsencode(os.readlink(candidate)))
        if not candidate.is_file():
            return None
        if algorithm == "sha256-v1":
            return _sha256(b"file\0" + candidate.read_bytes())
        # v2 folds the exec bit into the content digest. v1 caught a mode-only
        # change through the (then-digested) unstaged patch bytes; dropping those
        # from the digest would otherwise let `chmod +x` on a reviewed script pass
        # as unchanged, since its bytes are identical.
        mode_tag = b"x\0" if candidate.stat().st_mode & 0o111 else b"-\0"
        return _sha256(b"file\0" + mode_tag + candidate.read_bytes())
    except OSError:
        return None


def _unavailable(
    reviewed_paths: list[str] | None, changed_ref: str | None, reason: str, algorithm: str = ALGORITHM
) -> dict[str, Any]:
    components = {
        "algorithm": algorithm,
        "status": "unavailable",
        "reason": reason,
        "reviewed_paths": sorted(set(reviewed_paths or [])),
        "changed_ref": changed_ref,
    }
    return _with_identity_digest(components)


def _with_identity_digest(components: dict[str, Any]) -> dict[str, Any]:
    digest_components = dict(components)
    provenance_only = components.get("base_head_role") == "provenance-only"
    if components.get("algorithm") == "sha256-v2":
        for field in PROVENANCE_FIELDS + (WORKING_TREE_PROVENANCE_FIELDS if provenance_only else ()):
            digest_components.pop(field, None)
    elif provenance_only:
        digest_components.pop("base_head", None)
    canonical = json.dumps(digest_components, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {**components, "identity_sha256": _sha256(canonical.encode("utf-8"))}


def build_reviewed_input_identity(
    *,
    repo_root: Path,
    reviewed_paths: list[str] | None = None,
    changed_ref: str | None = None,
    excluded_paths: list[str] | None = None,
    excluded_prefixes: list[str] | None = None,
    algorithm: str = ALGORITHM,
) -> dict[str, Any]:
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"unsupported reviewed input identity algorithm `{algorithm}`")
    try:
        _git_bytes(repo_root, "rev-parse", "--is-inside-work-tree")
    except ValueError as exc:
        return _unavailable(reviewed_paths, changed_ref, str(exc), algorithm)

    auto_excluded: list[str] = []
    if reviewed_paths is None:
        # Exclusions apply to the auto sweep ONLY: an explicit `--reviewed-path` is a
        # declaration of what was read and is never silently dropped.
        swept = set(_auto_paths(repo_root, changed_ref))
        prefixes = tuple(excluded_prefixes or ())
        kept = swept - set(excluded_paths or [])
        auto_excluded = sorted(swept - {path for path in kept if not path.startswith(prefixes)})
        paths = sorted(path for path in kept if not path.startswith(prefixes))
    else:
        paths = sorted(set(reviewed_paths))
    for path in paths:
        if changed_ref:
            _lexical_path(path)
            continue
        candidate = _checked_path(repo_root, path)
        # A directory binds NOTHING in working-tree mode: its content digest is
        # `null` and stays `null` however its files change. v1 accidentally
        # covered it through the digested patch bytes (a directory pathspec
        # sweeps everything beneath it); v2 must reject it outright rather than
        # issue a binding that can never go stale.
        if candidate.is_dir() and not candidate.is_symlink():
            raise ValueError(
                f"reviewed path `{path}` is a directory; declare the individual files "
                "that were reviewed, since a directory binds no content"
            )

    path_args = ["--", *paths]
    if changed_ref:
        resolved_ref = _git_bytes(repo_root, "rev-parse", changed_ref).decode().splitlines()
        base_head = resolved_ref[0]
        if not paths:
            reviewed_patch = b""
        elif ".." in changed_ref:
            reviewed_patch = _git_bytes(repo_root, "diff", "--binary", changed_ref, *path_args)
        else:
            reviewed_patch = _git_bytes(repo_root, "show", "--format=", "--binary", changed_ref, *path_args)
        staged_patch = unstaged_patch = b""
    else:
        resolved_ref = []
        base_head = _git_bytes(repo_root, "rev-parse", "HEAD").decode().strip()
        reviewed_patch = b""
        staged_patch = _git_bytes(repo_root, "diff", "--cached", "--binary", *path_args) if paths else b""
        unstaged_patch = _git_bytes(repo_root, "diff", "--binary", *path_args) if paths else b""

    untracked: set[str] = set()
    if paths and not changed_ref:
        raw_untracked = _git_bytes(
            repo_root, "ls-files", "--others", "--exclude-standard", "-z", *path_args
        )
        untracked = set(raw_untracked.decode("utf-8", errors="surrogateescape").split("\0"))

    reviewed_content = []
    declared_untracked = []
    for path in paths:
        if changed_ref:
            content = _git_bytes_optional(repo_root, "show", f"{base_head}:{path}")
            digest = _sha256(content) if content is not None else None
        else:
            digest = _worktree_content_sha256(repo_root, path, algorithm)
        entry = {"path": path, "content_sha256": digest}
        reviewed_content.append(entry)
        if path in untracked:
            declared_untracked.append(entry)

    captured: dict[str, Any] = {
        "algorithm": algorithm,
        "status": "captured",
        "mode": "changed-ref" if changed_ref else "working-tree",
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
    if algorithm == "sha256-v2":
        captured["auto_excluded_paths"] = auto_excluded
    return _with_identity_digest(captured)


def verify_reviewed_input_identity(repo_root: Path, identity: dict[str, Any]) -> tuple[bool, str]:
    if identity.get("status") != "captured":
        return False, "reviewed input identity was unavailable when the packet was produced"
    if not identity.get("reviewed_paths"):
        # An empty path set digests to the same constant in every repo forever, so
        # it would verify as `current` while proving nothing. Reject it as a
        # binding rather than let a zero-input verdict read as a checked one.
        return False, "declared reviewed inputs cover zero paths"
    try:
        current = build_reviewed_input_identity(
            repo_root=repo_root,
            reviewed_paths=list(identity["reviewed_paths"]),
            changed_ref=identity.get("changed_ref"),
            # Recompute under the algorithm the packet was produced with, so a digest
            # rule change does not retroactively stale every binding already written.
            algorithm=identity.get("algorithm", "sha256-v1"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"cannot reconstruct reviewed input identity: {exc}"
    if current["identity_sha256"] != identity.get("identity_sha256"):
        return False, "declared reviewed inputs are stale"
    return True, "current"


def packet_file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def verify_packet_binding(
    *,
    repo_root: Path,
    packet_path: str,
    packet_sha256: str,
    identity_sha256: str,
    expected_kind: str,
    check_current: bool = True,
) -> tuple[bool, str]:
    candidate = (repo_root / packet_path).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return False, "reviewed packet path resolves outside repo root"
    if not candidate.is_file():
        return False, f"reviewed packet does not exist: {packet_path}"
    packet_bytes = candidate.read_bytes()
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
    if check_current:
        return verify_reviewed_input_identity(repo_root, identity)
    return True, "packet-integrity-only"


def verify_artifact_binding(
    artifact_path: Path,
    fields: dict[str, str],
    *,
    expected_kind: str,
    check_current: bool = True,
) -> tuple[bool, str]:
    repo_root = next(
        (parent for parent in artifact_path.resolve().parents if (parent / ".git").exists()),
        None,
    )
    if repo_root is None and len(artifact_path.parents) >= 3:
        repo_root = artifact_path.parents[2]
    if repo_root is None:
        return False, "cannot resolve repository root for reviewed input binding"
    return verify_packet_binding(
        repo_root=repo_root,
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
    )
