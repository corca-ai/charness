#!/usr/bin/env python3
"""Materialize identity-checked review bytes for every supported backend."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:
    _scripts_dir = next(
        (
            ancestor / "scripts"
            for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
            if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
        ),
        None,
    )
    if _scripts_dir is None:
        raise
    sys.path.insert(0, str(_scripts_dir))
    from scripts.core.subprocess_guard import run_process

MAX_SEMANTIC_INPUT_BYTES = 1024 * 1024
MAX_PREIMAGE_BYTES = MAX_SEMANTIC_INPUT_BYTES

#: The two framings `scripts/review/reviewed_input_identity.py` binds a deletion under, one per
#: substrate. They are NOT the same, and reading them as one is what broke this file:
#:
#:   working tree  `_recorded_blob_digest`  -> sha256(b"file\0" + mode_tag + blob)
#:   committed ref `_committed_ref_digest`  -> sha256(blob)
#:
#: The mode tag records the exec bit, because `chmod +x` on a reviewed script is
#: review-significant and its bytes do not move. Only the working-tree binder carries it.
#:
#: RESTATED, not imported, and that is the hazard. A critique skill script must stay
#: portable -- nothing under `skills/` imports `scripts/` -- so this lives on both sides of
#: that boundary and drifted: the working-tree binder gained its mode tag while this file
#: still compared raw `sha256(blob)` for BOTH substrates, so every deletion-only
#: working-tree review refused with `preimage-hash-mismatch` while committed ranges passed.
#: `test_the_deleted_preimage_digest_matches_the_binder_across_the_skill_boundary` drives
#: the real binders and pins both; extend it if either framing moves.
_DELETED_BLOB_PREFIX = b"file\0"
_DELETED_BLOB_MODE_TAGS = (b"-\0", b"x\0")


def worktree_deleted_digests(blob: bytes) -> tuple[str, ...]:
    """Every digest the WORKING-TREE binder could have bound for ``blob``, one per mode tag.

    Enumerating the two tags RECOVERS the mode from the hash instead of asking Git for it.
    That is not a weakening: the bound hash covers the (mode, bytes) pair, so a match under
    one tag proves that pair, and it costs no extra `git ls-files`/`ls-tree` on a path Git
    has already been asked about twice.
    """
    return tuple(
        hashlib.sha256(_DELETED_BLOB_PREFIX + tag + blob).hexdigest()
        for tag in _DELETED_BLOB_MODE_TAGS
    )


def committed_deleted_digests(blob: bytes) -> tuple[str, ...]:
    """What the COMMITTED-REF binder bound for ``blob``: raw bytes, no mode.

    A separate one-element function rather than a bare `sha256` call at the callsite, so
    the asymmetry above is named where it is used and the guard test can drive both.
    """
    return (hashlib.sha256(blob).hexdigest(),)


class SemanticInputError(ValueError):
    """A deleted reviewed input cannot be safely carried to the worker."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def semantic_review_paths(packet: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return readable and deleted paths from the verified input identity."""
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return [], []
    raw_paths = identity.get("reviewed_paths")
    raw_content = identity.get("reviewed_content")
    if not isinstance(raw_paths, list) or not isinstance(raw_content, list):
        return [], []
    paths = [path for path in raw_paths if isinstance(path, str) and path]
    deleted = {
        entry.get("path")
        for entry in raw_content
        if isinstance(entry, dict)
        and entry.get("disposition") == "deleted"
        and isinstance(entry.get("path"), str)
    }
    return [path for path in paths if path not in deleted], sorted(deleted)


def _git_bytes(root: Path, *args: str) -> bytes | None:
    result = run_process(["git", *args], cwd=root, timeout_seconds=None)
    return result.stdout.encode("utf-8") if result.returncode == 0 else None


def _preimage_digests(identity: dict[str, Any]):
    """The binder that produced this identity, chosen by the SAME substrate test that
    chooses the pre-image sources below. Read them together: a substrate's sources and its
    framing are one decision, and splitting them is how the two fell out of step."""
    mode = identity.get("substrate_mode") or identity.get("mode")
    changed_ref = identity.get("changed_ref")
    if mode == "committed-ref" and isinstance(changed_ref, str) and changed_ref:
        return committed_deleted_digests
    return worktree_deleted_digests


def _preimage_sources(root: Path, identity: dict[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    mode = identity.get("substrate_mode") or identity.get("mode")
    changed_ref = identity.get("changed_ref")
    if mode == "committed-ref" and isinstance(changed_ref, str) and changed_ref:
        resolved = identity.get("resolved_changed_ref")
        refs = (
            [ref for ref in resolved if isinstance(ref, str) and ref]
            if isinstance(resolved, list)
            else []
        )
        if len(refs) >= 2:
            return [(f"{refs[0]}:{{path}}", ("show", f"{refs[0]}:{{path}}"))]
        target = refs[-1] if refs else changed_ref
        parents = _git_bytes(root, "rev-list", "--parents", "-n", "1", target)
        parent_refs = (
            parents.decode("utf-8", errors="surrogateescape").split()[1:] if parents else []
        )
        return [(f"{parent}:{{path}}", ("show", f"{parent}:{{path}}")) for parent in parent_refs]
    return [
        ("index:{path}", ("show", ":{path}")),
        ("HEAD:{path}", ("show", "HEAD:{path}")),
    ]


def _read_deleted_preimage(
    root: Path, identity: dict[str, Any], path: str, expected_sha256: str
) -> tuple[bytes, str]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise SemanticInputError(
            "preimage-hash-invalid",
            f"deleted reviewed path `{path}` has no valid pre-image hash",
            details={"path": path},
        )
    candidates = _preimage_sources(root, identity)
    digests_for = _preimage_digests(identity)
    mismatches: list[str] = []
    oversized: list[str] = []
    for source_template, command_template in candidates:
        source = source_template.format(path=path)
        command = tuple(argument.format(path=path) for argument in command_template)
        content = _git_bytes(root, *command)
        if content is None:
            continue
        if len(content) > MAX_PREIMAGE_BYTES:
            oversized.append(source)
            continue
        if expected_sha256 in digests_for(content):
            return content, source
        mismatches.append(source)
    if oversized:
        raise SemanticInputError(
            "preimage-too-large",
            f"deleted reviewed path `{path}` pre-image exceeds the {MAX_PREIMAGE_BYTES}-byte semantic input limit",
            details={"path": path, "sources": oversized, "max_bytes": MAX_PREIMAGE_BYTES},
        )
    if mismatches:
        raise SemanticInputError(
            "preimage-hash-mismatch",
            f"deleted reviewed path `{path}` pre-image does not match its bound hash",
            details={"path": path, "sources": mismatches, "expected_sha256": expected_sha256},
        )
    raise SemanticInputError(
        "preimage-unavailable",
        f"deleted reviewed path `{path}` has no readable bound pre-image",
        details={"path": path, "sources": [source for source, _ in candidates]},
    )


def _expected_content(identity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        entry.get("path"): entry
        for entry in identity.get("reviewed_content", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }


def _read_present_content(
    root: Path, identity: dict[str, Any], path: str, expected_sha256: str
) -> tuple[bytes, str]:
    mode = identity.get("substrate_mode") or identity.get("mode")
    if mode == "committed-ref":
        target = identity.get("base_head")
        if not isinstance(target, str) or not target:
            raise SemanticInputError(
                "semantic-source-invalid",
                f"reviewed path `{path}` has no bound committed-ref target",
                details={"path": path},
            )
        content = _git_bytes(root, "show", f"{target}:{path}")
        source = f"{target}:{path}"
        actual = hashlib.sha256(content).hexdigest() if content is not None else None
    elif mode == "working-tree":
        candidate = root / path
        try:
            candidate.resolve().relative_to(root.resolve())
        except (OSError, ValueError) as exc:
            raise SemanticInputError(
                "semantic-source-invalid",
                f"reviewed path `{path}` escapes the repository root",
                details={"path": path},
            ) from exc
        if candidate.is_symlink() or not candidate.is_file():
            content = None
            actual = None
        else:
            content = candidate.read_bytes()
            mode_tag = b"x\0" if candidate.stat().st_mode & 0o111 else b"-\0"
            actual = hashlib.sha256(b"file\0" + mode_tag + content).hexdigest()
        source = f"working-tree:{path}"
    else:
        raise SemanticInputError(
            "semantic-source-invalid",
            f"reviewed path `{path}` has unsupported substrate mode `{mode}`",
            details={"path": path, "substrate_mode": mode},
        )
    if content is None:
        raise SemanticInputError(
            "semantic-source-unavailable",
            f"reviewed path `{path}` has no readable regular-file bytes at its bound source",
            details={"path": path, "source": source},
        )
    if actual != expected_sha256:
        raise SemanticInputError(
            "semantic-source-hash-mismatch",
            f"reviewed path `{path}` bytes do not match its bound identity",
            details={
                "path": path,
                "source": source,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual,
            },
        )
    return content, source


def _prompt_content(content: bytes) -> tuple[str, str]:
    try:
        return "utf-8", content.decode("utf-8")
    except UnicodeDecodeError:
        return "base64", base64.b64encode(content).decode("ascii")


def materialize_semantic_input(root: Path, packet: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    """Carry all reviewed bytes into backend-independent semantic input."""
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return {"entries": [], "manifest": None}
    readable_paths, deleted_paths = semantic_review_paths(packet)
    try:
        run_dir.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise SemanticInputError(
            "carrier-path-invalid", "semantic input carrier escaped the repository root"
        ) from exc
    content_by_path = _expected_content(identity)
    staged: list[tuple[str, bytes, str, str, str]] = []
    for path in readable_paths + deleted_paths:
        entry = content_by_path.get(path, {})
        expected = entry.get("content_sha256")
        if not isinstance(expected, str):
            raise SemanticInputError(
                "preimage-hash-invalid",
                f"reviewed path `{path}` has no bound content hash",
                details={"path": path},
            )
        if path in deleted_paths:
            content, source = _read_deleted_preimage(root, identity, path, expected)
            disposition = "deleted-preimage"
        else:
            content, source = _read_present_content(root, identity, path, expected)
            disposition = "present"
        staged.append((path, content, source, expected, disposition))

    total_bytes = sum(len(content) for _, content, _, _, _ in staged)
    if total_bytes > MAX_SEMANTIC_INPUT_BYTES:
        raise SemanticInputError(
            "semantic-input-too-large",
            "reviewed semantic input exceeds the bounded worker input limit",
            details={
                "size_bytes": total_bytes,
                "max_bytes": MAX_SEMANTIC_INPUT_BYTES,
                "paths": [path for path, _, _, _, _ in staged],
            },
        )

    carrier_dir = run_dir / "semantic-input"
    carrier_dir.mkdir(parents=True, exist_ok=False)
    entries: list[dict[str, Any]] = []
    for index, (path, content, source, expected, disposition) in enumerate(staged):
        carrier = carrier_dir / f"{index:04d}-content.bin"
        carrier.write_bytes(content)
        carrier.chmod(0o444)
        carrier_sha256 = hashlib.sha256(content).hexdigest()
        if carrier.read_bytes() != content:
            raise SemanticInputError(
                "semantic-carrier-mismatch",
                f"materialized semantic carrier for `{path}` changed after writing",
                details={"path": path, "carrier": carrier.as_posix()},
            )
        encoding, prompt_content = _prompt_content(content)
        entries.append(
            {
                "path": path,
                "disposition": disposition,
                "carrier_path": carrier.relative_to(root).as_posix(),
                "content_sha256": expected,
                "carrier_sha256": carrier_sha256,
                "source": source,
                "size_bytes": len(content),
                "prompt_encoding": encoding,
                "prompt_content": prompt_content,
            }
        )
    manifest = carrier_dir / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "kind": "charness.semantic_input_carrier.v1",
                "entries": [
                    {key: value for key, value in entry.items() if key != "prompt_content"}
                    for entry in entries
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest.chmod(0o444)
    carrier_dir.chmod(0o555)
    return {
        "entries": entries,
        "manifest": manifest.relative_to(root).as_posix(),
        "size_bytes": total_bytes,
    }
