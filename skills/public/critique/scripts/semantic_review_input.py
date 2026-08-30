#!/usr/bin/env python3
"""Materialize verified deleted review inputs for a bounded worker."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

MAX_PREIMAGE_BYTES = 1024 * 1024


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
    result = subprocess.run(["git", *args], cwd=root, check=False, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def _preimage_sources(root: Path, identity: dict[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    mode = identity.get("substrate_mode") or identity.get("mode")
    changed_ref = identity.get("changed_ref")
    if mode == "committed-ref" and isinstance(changed_ref, str) and changed_ref:
        resolved = identity.get("resolved_changed_ref")
        refs = [ref for ref in resolved if isinstance(ref, str) and ref] if isinstance(resolved, list) else []
        if len(refs) >= 2:
            return [(f"{refs[0]}:{{path}}", ("show", f"{refs[0]}:{{path}}"))]
        target = refs[-1] if refs else changed_ref
        parents = _git_bytes(root, "rev-list", "--parents", "-n", "1", target)
        parent_refs = parents.decode("utf-8", errors="surrogateescape").split()[1:] if parents else []
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
        if hashlib.sha256(content).hexdigest() == expected_sha256:
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


def materialize_semantic_input(
    root: Path, packet: dict[str, Any], run_dir: Path
) -> dict[str, Any]:
    """Carry deleted pre-images into a hash-checked read-only worker input."""
    identity = packet.get("reviewed_input_identity")
    if not isinstance(identity, dict):
        return {"entries": [], "manifest": None}
    _, deleted_paths = semantic_review_paths(packet)
    if not deleted_paths:
        return {"entries": [], "manifest": None}
    try:
        run_dir.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise SemanticInputError(
            "carrier-path-invalid", "semantic input carrier escaped the repository root"
        ) from exc
    content_by_path = {
        entry.get("path"): entry
        for entry in identity.get("reviewed_content", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    staged: list[tuple[str, bytes, str, str]] = []
    for path in deleted_paths:
        entry = content_by_path.get(path, {})
        expected = entry.get("content_sha256")
        if not isinstance(expected, str):
            raise SemanticInputError(
                "preimage-hash-invalid",
                f"deleted reviewed path `{path}` has no bound pre-image hash",
                details={"path": path},
            )
        content, source = _read_deleted_preimage(root, identity, path, expected)
        staged.append((path, content, source, expected))

    carrier_dir = run_dir / "semantic-input"
    carrier_dir.mkdir(parents=True, exist_ok=False)
    entries: list[dict[str, Any]] = []
    for index, (path, content, source, expected) in enumerate(staged):
        carrier = carrier_dir / f"{index:04d}-preimage.bin"
        carrier.write_bytes(content)
        carrier.chmod(0o444)
        if hashlib.sha256(carrier.read_bytes()).hexdigest() != expected:
            raise SemanticInputError(
                "preimage-carrier-mismatch",
                f"materialized pre-image carrier for `{path}` failed its bound hash check",
                details={"path": path, "carrier": carrier.as_posix(), "expected_sha256": expected},
            )
        entries.append(
            {
                "path": path,
                "carrier_path": carrier.relative_to(root).as_posix(),
                "content_sha256": expected,
                "source": source,
                "size_bytes": len(content),
            }
        )
    manifest = carrier_dir / "manifest.json"
    manifest.write_text(
        json.dumps({"kind": "charness.semantic_input_carrier.v1", "entries": entries}, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest.chmod(0o444)
    carrier_dir.chmod(0o555)
    return {"entries": entries, "manifest": manifest.relative_to(root).as_posix()}
