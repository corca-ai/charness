"""Preflight and attach the locally-built native artifact for a release."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from scripts.native_core_resolution_lib import (
    canonical_artifact_name,
    checkout_version,
    host_tuple,
    read_native_declaration,
    sha256,
)
from scripts.runtime_bootstrap import runtime_root

_SHA256_RE = re.compile(r"[0-9a-fA-F]{64}")


def _not_applicable(reason: str) -> dict[str, Any]:
    return {"status": "not-applicable", "asset": None, "reason": reason}


def _artifact_table(declaration: dict[str, Any]) -> dict[str, Any]:
    for key in ("artifacts", "releases", "versions"):
        value = declaration.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _artifact_candidate(
    declaration: dict[str, Any], version: str, tuple_name: str
) -> dict[str, Any] | None:
    table = _artifact_table(declaration)
    if version not in table:
        return None
    version_entry = table[version]
    if not isinstance(version_entry, dict):
        raise SystemExit(
            f"native artifact declaration for {version} has malformed version entry"
        )
    if tuple_name in version_entry:
        candidate = version_entry[tuple_name]
        if not isinstance(candidate, dict):
            raise SystemExit(
                f"native artifact declaration for {version}/{tuple_name} has malformed tuple entry"
            )
        return candidate
    if version_entry.get("tuple") == tuple_name:
        return version_entry
    return None


def _validated_artifact(
    declaration: dict[str, Any], version: str, tuple_name: str
) -> tuple[str, str] | None:
    candidate = _artifact_candidate(declaration, version, tuple_name)
    if candidate is None:
        return None
    name = candidate.get("name")
    if not isinstance(name, str) or not name:
        raise SystemExit(
            f"native artifact declaration for {version}/{tuple_name} has malformed `name` field"
        )
    digest = candidate.get("sha256")
    if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
        raise SystemExit(
            f"native artifact declaration for {version}/{tuple_name} has malformed `sha256` field"
        )
    expected_name = canonical_artifact_name(version, tuple_name)
    if name != expected_name:
        raise SystemExit(
            f"native artifact declaration must use {expected_name}; malformed `name` field: {name}"
        )
    return name, digest.lower()


def native_artifact_preflight(repo_root: Path) -> dict[str, Any]:
    """Validate the declared native archive and return its local path."""
    if (declaration := read_native_declaration(repo_root)) is None:
        return _not_applicable("native_core declaration is absent")
    version = checkout_version(repo_root)
    if version is None:
        raise SystemExit("product version cannot be read from packaging/charness.json")
    tuple_name = host_tuple()
    artifact = _validated_artifact(declaration, version, tuple_name)
    if artifact is None:
        return _not_applicable("checkout version has no native artifact declaration")
    asset, expected_digest = artifact
    archive = runtime_root(repo_root) / "native-artifacts" / asset
    if not archive.is_file():
        raise SystemExit(
            f"native artifact archive is missing: expected {archive}\n"
            "build it with: "
            f"python3 scripts/build_native_artifact.py --repo-root {repo_root}"
        )
    try:
        actual_digest = sha256(archive)
    except OSError as exc:
        raise SystemExit(f"could not read native artifact archive {archive}: {exc}") from exc
    if actual_digest.lower() != expected_digest:
        raise SystemExit(
            f"native artifact sha256 mismatch for {asset}: expected {expected_digest}, "
            f"got {actual_digest} ({archive})"
        )
    return {
        "status": "ready",
        "asset": asset,
        "path": archive,
        "reason": "native artifact preflight passed",
    }


def _command_failure(command: list[str], result: Any) -> SystemExit:
    return SystemExit(
        f"command failed: {' '.join(command)}\n"
        f"exit_code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def upload_native_artifact(
    repo_root: Path,
    *,
    backend: dict[str, Any],
    tag_name: str,
    preflight: dict[str, Any] | None = None,
    backend_command: Callable[..., list[str]],
    run: Callable[..., Any],
) -> dict[str, Any]:
    """Attach the preflighted archive, treating a present asset as idempotent."""
    if read_native_declaration(repo_root) is None:
        return _not_applicable("native_core declaration is absent")
    preflight = preflight or native_artifact_preflight(repo_root)
    if preflight.get("status") == "not-applicable":
        return _not_applicable(str(preflight.get("reason") or "native artifact is not declared"))
    asset = preflight.get("asset")
    archive = preflight.get("path")
    if not isinstance(asset, str) or not isinstance(archive, (Path, str)):
        raise SystemExit("native artifact upload received an invalid preflight result")
    asset_path = Path(archive)
    assets_command = backend_command(
        backend,
        "release_assets",
        [
            "gh", "release", "view", "{tag}", "--json", "assets", "--jq", ".assets[].name",
        ],
        tag=tag_name,
    )
    assets_result = run(assets_command, cwd=repo_root, check=False)
    if assets_result.returncode != 0:
        raise _command_failure(assets_command, assets_result)
    if asset in {line.strip() for line in assets_result.stdout.splitlines() if line.strip()}:
        return {
            "status": "already-present",
            "asset": asset,
            "reason": "native artifact is already present on the release",
        }
    upload_command = backend_command(
        backend,
        "release_upload",
        ["gh", "release", "upload", "{tag}", "{asset}"],
        tag=tag_name,
        asset=str(asset_path),
    )
    run(upload_command, cwd=repo_root)
    return {
        "status": "uploaded",
        "asset": asset,
        "reason": "native artifact uploaded to the release",
    }


def attempt_native_artifact_upload(
    repo_root: Path,
    *,
    backend: dict[str, Any],
    tag_name: str,
    preflight: dict[str, Any],
    backend_command: Callable[..., list[str]],
    run: Callable[..., Any],
) -> tuple[dict[str, Any] | None, BaseException | None]:
    try:
        return upload_native_artifact(
            repo_root,
            backend=backend,
            tag_name=tag_name,
            preflight=preflight,
            backend_command=backend_command,
            run=run,
        ), None
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, GeneratorExit)):
            raise
        return None, exc


def record_native_artifact_upload(
    payload: dict[str, Any], result: dict[str, Any] | None, failure: BaseException | None
) -> None:
    if failure is None:
        payload["native_artifact_upload"] = result
    else:
        # The native-artifact result vocabulary intentionally has no misleading `failed`
        # status; the existing release-verification field records the failed publication.
        payload["public_release_verification"] = "failed"


__all__ = [
    "attempt_native_artifact_upload", "native_artifact_preflight",
    "record_native_artifact_upload", "upload_native_artifact",
]
