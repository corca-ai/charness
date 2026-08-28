"""Typed native-core locator and doctor projection."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

NativeStatus = Literal[
    "healthy", "missing", "corrupt", "stale", "incompatible",
    "not-distributed", "awaiting-artifact", "offline", "unsupported-tuple",
]


@dataclass(frozen=True, slots=True)
class NativeCoreHealthy:
    status: Literal["healthy"]
    path: Path
    provenance: str
    version: str
    artifact_commit: str | None = None


@dataclass(frozen=True, slots=True)
class NativeCoreUnavailable:
    status: NativeStatus
    provenance: str | None = None
    version: str | None = None
    reason: str | None = None


NativeCoreResult = NativeCoreHealthy | NativeCoreUnavailable


def host_tuple() -> str:
    machine = platform.machine().lower()
    if platform.system().lower() == "linux" and machine in {"x86_64", "amd64"}:
        return "x86_64-unknown-linux-gnu"
    return f"{machine or 'unknown'}-unknown-{platform.system().lower() or 'unknown'}"


def _manifest(repo_root: Path) -> dict[str, Any]:
    try:
        data = json.loads((repo_root / "packaging" / "charness.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_native_declaration(repo_root: Path) -> dict[str, Any] | None:
    value = _manifest(repo_root).get("native_core")
    return value if isinstance(value, dict) else None


def checkout_version(repo_root: Path) -> str | None:
    value = _manifest(repo_root).get("version")
    return value if isinstance(value, str) and value else None


def repository_url(repo_root: Path) -> str | None:
    value = _manifest(repo_root).get("repository")
    return value if isinstance(value, str) else None


def _artifact_table(declaration: dict[str, Any]) -> dict[str, Any]:
    for key in ("artifacts", "releases", "versions"):
        value = declaration.get(key)
        if isinstance(value, dict):
            return value
    return {}


def artifact_declaration(
    declaration: dict[str, Any], version: str, tuple_name: str
) -> dict[str, str] | None:
    version_entry = _artifact_table(declaration).get(version)
    if not isinstance(version_entry, dict):
        return None
    candidate = version_entry.get(tuple_name)
    if not isinstance(candidate, dict) and version_entry.get("tuple") == tuple_name:
        candidate = version_entry
    if not isinstance(candidate, dict):
        return None
    name, digest = candidate.get("name"), candidate.get("sha256")
    if not isinstance(name, str) or not name or not isinstance(digest, str) or len(digest) != 64:
        return None
    return {"name": name, "sha256": digest.lower()}


def validate_state_root(state_root: Path, home_root: Path | None) -> Path:
    root = state_root.expanduser().resolve()
    if home_root is not None:
        try:
            root.relative_to(home_root.expanduser().resolve())
        except ValueError as exc:
            raise ValueError(f"native state root escapes home root: {root}") from exc
    return root


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def pointer(native_root: Path) -> dict[str, Any] | None:
    return read_json(native_root / "current")


def metadata(root: Path) -> dict[str, Any]:
    for path in (root / "artifact.json", *root.rglob("artifact.json")):
        data = read_json(path)
        if data is not None:
            return data
    return {}


def _checkout_head(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, check=False,
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _no_pointer_result(repo_root: Path, native_root: Path, version: str) -> NativeCoreResult:
    last = read_json(native_root / "last-status.json")
    if isinstance(last, dict) and last.get("version") == version and last.get("status") in {"awaiting-artifact", "offline"}:
        return NativeCoreUnavailable(last["status"], version=version, reason=last.get("reason"))
    if os.environ.get("CHARNESS_ALLOW_DEV_NATIVE_CORE") == "1":
        dev = repo_root / "native" / "repograph" / "target" / "release" / "repograph"
        if dev.is_file():
            return NativeCoreHealthy("healthy", dev, "dev-tree-build", version)
    return NativeCoreUnavailable("missing", version=version, reason="native current pointer is absent")


def _pointer_version_status(
    current: dict[str, Any], version: str, tuple_name: str
) -> NativeCoreUnavailable | None:
    if current.get("version") != version:
        previous = current.get("version") if isinstance(current.get("version"), str) else version
        return NativeCoreUnavailable("stale", version=previous, reason="native core version does not match checkout")
    if current.get("tuple") != tuple_name:
        return NativeCoreUnavailable("incompatible", version=version, reason="native core tuple does not match host")
    return None


def _pointer_binary(
    native_root: Path, current: dict[str, Any], *, verify_digest: bool
) -> tuple[Path | None, str | None]:
    if current.get("verified") is not True:
        return None, "current pointer is not marked verified"
    binary_name = current.get("binary")
    if not isinstance(binary_name, str):
        return None, "current pointer has no binary"
    binary = (native_root / binary_name).resolve()
    try:
        binary.relative_to(native_root.resolve())
    except ValueError:
        return None, "current pointer escapes native state root"
    if not binary.is_file():
        return None, "current native binary is absent"
    try:
        stat = binary.stat()
    except OSError as exc:
        return None, str(exc)
    if stat.st_size != current.get("size") or stat.st_mtime_ns != current.get("mtime_ns") or verify_digest:
        recorded = current.get("binary_sha256")
        if not isinstance(recorded, str) or sha256(binary) != recorded:
            return None, "current native binary digest is invalid"
    return binary, None


def _managed_result(
    native_root: Path,
    current: dict[str, Any],
    declaration: dict[str, Any],
    version: str,
    tuple_name: str,
    *,
    verify_digest: bool,
) -> NativeCoreResult:
    version_status = _pointer_version_status(current, version, tuple_name)
    if version_status is not None:
        return version_status
    binary, binary_reason = _pointer_binary(native_root, current, verify_digest=verify_digest)
    if binary is None:
        return NativeCoreUnavailable("corrupt", version=version, reason=binary_reason)
    installed = read_json(binary.parent / "artifact.json") or metadata(binary.parent)
    expected = artifact_declaration(declaration, version, tuple_name)
    if expected is None or installed.get("version") != version or installed.get("tuple") != tuple_name:
        return NativeCoreUnavailable("incompatible", version=version, reason="installed artifact metadata is incompatible")
    if installed.get("artifact_sha256") != expected["sha256"]:
        return NativeCoreUnavailable("corrupt", version=version, reason="installed artifact is not declaration-bound")
    return NativeCoreHealthy("healthy", binary, "managed", version, installed.get("git_commit") or installed.get("commit"))


def native_core_path(
    home_root: Path | None = None,
    repo_root: Path | None = None,
    *,
    state_root: Path | None = None,
    verify_digest: bool = False,
) -> NativeCoreResult:
    home = (home_root or Path.home()).expanduser().resolve()
    repo = (repo_root or Path(os.environ.get("CHARNESS_REPO_ROOT", Path.cwd()))).expanduser().resolve()
    version = checkout_version(repo)
    override = os.environ.get("CHARNESS_NATIVE_CORE", "").strip()
    if override:
        path = Path(override).expanduser().resolve()
        if path.is_file():
            return NativeCoreHealthy("healthy", path, "override", version or "override")
        return NativeCoreUnavailable("corrupt", "override", version, "override path is missing")
    declaration = read_native_declaration(repo)
    tuple_name = host_tuple()
    if declaration is None:
        return NativeCoreUnavailable("not-distributed", version=version, reason="native_core declaration is absent")
    if isinstance(declaration.get("supported_tuples"), list) and tuple_name not in declaration["supported_tuples"]:
        return NativeCoreUnavailable("unsupported-tuple", version=version, reason="host tuple is not supported")
    if not version or artifact_declaration(declaration, version, tuple_name) is None:
        return NativeCoreUnavailable("not-distributed", version=version, reason="checkout version has no native artifact declaration")
    root = (state_root or home / ".local" / "state" / "charness").expanduser().resolve()
    try:
        root = validate_state_root(root, home)
    except ValueError as exc:
        return NativeCoreUnavailable("incompatible", version=version, reason=str(exc))
    native_root = root / "native"
    current = pointer(native_root)
    if current is None:
        return _no_pointer_result(repo, native_root, version)
    return _managed_result(
        native_root, current, declaration, version, tuple_name, verify_digest=verify_digest
    )


def native_core_doctor_payload(
    home_root: Path, repo_root: Path, *, state_root: Path | None = None
) -> dict[str, object]:
    result = native_core_path(home_root, repo_root, state_root=state_root, verify_digest=True)
    payload: dict[str, object] = {
        "status": result.status,
        "provenance": result.provenance,
        "version": result.version,
        "tuple": host_tuple(),
    }
    if isinstance(result, NativeCoreHealthy):
        if result.provenance != "managed":
            payload["status"] = "incompatible"
            payload["reason"] = "explicit native core paths are not managed release artifacts"
            payload["source_drift"] = None
        else:
            payload["path"] = str(result.path)
            head = _checkout_head(repo_root)
            payload["source_drift"] = "in-sync" if not result.artifact_commit or result.artifact_commit == head else "ahead-of-artifact"
    else:
        payload["reason"] = result.reason
        payload["source_drift"] = None
    messages = {
        "not-distributed": "This checkout does not declare a native core; the Python surface remains active.",
        "unsupported-tuple": "This host tuple is unsupported; continue with the Python surface.",
        "awaiting-artifact": "The declared artifact is not published yet; the previous core remains active. Retry `charness update` after publication.",
        "offline": "The native artifact could not be reached; retry `charness update` when online.",
        "missing": "No managed native core is active; run `charness update` when the artifact is available.",
        "stale": "The active native core belongs to another checkout version; run `charness update` to activate the matching version.",
        "corrupt": "The managed native core failed verification; run `charness update` to restore it.",
        "incompatible": "The native core is not a verified managed release artifact; remove the override and run `charness update`.",
        "healthy": "The managed native core is verified and active.",
    }
    payload["message"] = messages.get(payload["status"], "Inspect the native core state and retry the managed update.")
    return payload


__all__ = [
    "NativeCoreHealthy", "NativeCoreResult", "NativeCoreUnavailable",
    "artifact_declaration", "checkout_version", "host_tuple", "metadata", "repository_url",
    "native_core_doctor_payload", "native_core_path", "pointer",
    "read_json", "read_native_declaration", "sha256", "validate_state_root",
]
