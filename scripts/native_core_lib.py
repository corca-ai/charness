"""Version-bound native-core installation and lookup.

The lifecycle is deliberately kept out of the top-level ``charness`` script.
The manifest declaration is the feature switch: an absent declaration returns
before the native state root is created and before a release probe can run.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Any, Callable

from scripts.current_pointer_writer_lib import CurrentPointerWriteError, write_current_pointer_json
from scripts.native_core_resolution_lib import (
    artifact_declaration,
    checkout_version,
    host_tuple,
    pointer,
    read_json,
    read_native_declaration,
    repository_url,
    sha256,
    validate_state_root,
)
from scripts.native_core_resolution_lib import (
    metadata as read_metadata,
)

PHASE_STATUSES = frozenset(
    {
        "activated",
        "reactivated",
        "no-op",
        "not-distributed",
        "unsupported-tuple",
        "awaiting-artifact",
        "offline",
        "foreign-origin",
        "checksum-failure",
        "verification-failure",
        "activation-failed",
        "state-write-skipped",
    }
)


ReleaseProbe = Callable[..., dict[str, object]]


def _write_status(native_root: Path, result: dict[str, object]) -> None:
    try:
        native_root.mkdir(parents=True, exist_ok=True)
        path = native_root / "last-status.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return


def _result(status: str, *, version: str | None, tuple_name: str, reason: str, **extra: object) -> dict[str, object]:
    return {"status": status, "version": version, "tuple": tuple_name, "reason": reason, **extra}


def _safe_member_path(root: Path, member: tarfile.TarInfo) -> Path:
    target = (root / member.name).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"artifact contains unsafe path `{member.name}`") from exc
    return target


def _extract_artifact(archive: Path, destination: Path) -> None:
    payload = destination / "payload"
    payload.mkdir(parents=True, exist_ok=True)
    if not tarfile.is_tarfile(archive):
        binary = payload / "repograph"
        shutil.copy2(archive, binary)
        return
    with tarfile.open(archive, "r:*") as bundle:
        for member in bundle.getmembers():
            if member.issym() or member.islnk():
                raise ValueError(f"artifact contains a link `{member.name}`")
            _safe_member_path(payload, member)
        bundle.extractall(payload)


def _find_binary(root: Path) -> Path | None:
    exact = [path for path in root.rglob("repograph") if path.is_file()]
    if exact:
        return sorted(exact)[0]
    candidates = [path for path in root.rglob("*") if path.is_file() and path.name.startswith("repograph")]
    return sorted(candidates)[0] if candidates else None


def _smoke(binary: Path) -> tuple[bool, str | None]:
    try:
        completed = subprocess.run(
            [str(binary), "parse-corpus", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    return completed.returncode == 0, (completed.stderr or completed.stdout).strip() or None


def _verify_version_dir(
    version_dir: Path, expected: dict[str, str], *, tuple_name: str, version: str, full_digest: bool
) -> tuple[Path | None, dict[str, Any], str | None]:
    if not version_dir.is_dir():
        return None, {}, "version directory is missing"
    metadata = read_metadata(version_dir)
    binary = version_dir / "repograph"
    if not binary.is_file():
        binary = _find_binary(version_dir) or binary
    if not binary.is_file():
        return None, metadata, "repograph binary is missing"
    if metadata.get("version") != version or metadata.get("tuple") != tuple_name:
        return None, metadata, "artifact metadata does not match the checkout"
    if metadata.get("artifact_sha256") != expected["sha256"]:
        return None, metadata, "artifact checksum declaration does not match installed metadata"
    try:
        stat = binary.stat()
    except OSError as exc:
        return None, metadata, str(exc)
    recorded_size = metadata.get("binary_size")
    recorded_mtime = metadata.get("binary_mtime_ns")
    recorded_digest = metadata.get("binary_sha256")
    if full_digest or recorded_size != stat.st_size or recorded_mtime != stat.st_mtime_ns:
        if not isinstance(recorded_digest, str) or sha256(binary) != recorded_digest:
            return None, metadata, "installed binary digest is corrupt"
    return binary, metadata, None


def _repo_slug(value: str) -> str | None:
    text = value.strip().removesuffix(".git")
    if text.startswith("git@") and ":" in text:
        text = text.split(":", 1)[1]
    elif "://" in text:
        text = text.split("://", 1)[1].split("/", 1)[1]
    if text.count("/") == 1 and not text.startswith("/"):
        return text
    return None


def _origin(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _foreign_origin(repo_root: Path, declaration: dict[str, Any]) -> str | None:
    expected = declaration.get("source") or repository_url(repo_root)
    actual = _origin(repo_root)
    expected_slug = _repo_slug(expected) if isinstance(expected, str) else None
    actual_slug = _repo_slug(actual) if actual else None
    if expected_slug and actual_slug and expected_slug != actual_slug:
        return f"origin `{actual}` does not match declared source `{expected}`"
    return None


def _local_artifact(store: str, name: str) -> Path | None:
    root = Path(store).expanduser().resolve()
    direct = root / name
    if direct.is_file():
        return direct
    if root.is_dir():
        for path in root.rglob(name):
            if path.is_file():
                return path
    return None


def _download_artifact(release: dict[str, object], name: str, destination: Path) -> tuple[Path | None, str | None]:
    import urllib.error
    import urllib.request

    urls = release.get("asset_urls")
    url = urls.get(name) if isinstance(urls, dict) else None
    if not isinstance(url, str):
        repo = release.get("repo")
        tag = release.get("latest_tag")
        html_url = release.get("html_url")
        if isinstance(repo, str) and isinstance(tag, str):
            url = f"https://github.com/{repo}/releases/download/{tag}/{name}"
        elif isinstance(html_url, str) and isinstance(tag, str):
            url = html_url.replace("/releases/tag/", "/releases/download/").rstrip("/") + f"/{name}"
    if not isinstance(url, str):
        return None, "release did not provide a downloadable asset URL"
    try:
        with urllib.request.urlopen(url, timeout=30) as response, destination.open("wb") as output:
            shutil.copyfileobj(response, output)
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        return None, str(exc)
    return destination, None


def _resolve_artifact(
    repo_root: Path,
    declaration: dict[str, Any],
    expected: dict[str, str],
    staging: Path,
    release_probe: ReleaseProbe | None,
) -> tuple[Path | None, str, str | None]:
    store = os.environ.get("CHARNESS_NATIVE_ARTIFACT_STORE", "").strip()
    if store:
        artifact = _local_artifact(store, expected["name"])
        sidecar = None
        if artifact is not None:
            for candidate in (
                artifact.parent / "artifact.json",
                artifact.with_name(f"{expected['name']}.artifact.json"),
            ):
                if candidate.is_file():
                    sidecar = candidate
                    break
        sidecar = sidecar or _local_artifact(store, "artifact.json") or _local_artifact(
            store, f"{expected['name']}.artifact.json"
        )
        if sidecar is not None:
            staging.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sidecar, staging / "artifact.json")
        return artifact, "local-store", None if artifact else "artifact is absent from local store"
    foreign = _foreign_origin(repo_root, declaration)
    if foreign:
        return None, "release", f"foreign-origin: {foreign}"
    if release_probe is None:
        return None, "release", "no release probe is configured"
    try:
        origin = _repo_slug(_origin(repo_root) or "")
        release = release_probe(origin) if origin else release_probe()
    except (OSError, TimeoutError) as exc:
        return None, "release", f"offline: {exc}"
    status = release.get("status")
    if status in {"error", "offline", "network-error"}:
        return None, "release", f"offline: {release.get('error') or status}"
    assets = release.get("asset_names")
    if not isinstance(assets, list) or expected["name"] not in assets:
        return None, "release", "awaiting-artifact: declared asset is not published yet"
    artifact, error = _download_artifact(release, expected["name"], staging / expected["name"])
    if artifact is not None and "artifact.json" in assets:
        _, sidecar_error = _download_artifact(release, "artifact.json", staging / "artifact.json")
        if sidecar_error:
            return None, "release", f"offline: {sidecar_error}"
    return artifact, "release", f"offline: {error}" if error else None


def _prepare_activation(
    archive: Path,
    stage: Path,
    expected: dict[str, str],
    *,
    version: str,
    tuple_name: str,
) -> tuple[Path | None, str | None]:
    if sha256(archive) != expected["sha256"]:
        return None, "downloaded artifact checksum does not match declaration"
    stage.mkdir(parents=True, exist_ok=True)
    _extract_artifact(archive, stage)
    binary = _find_binary(stage / "payload")
    if binary is None:
        return None, "artifact does not contain a repograph binary"
    metadata = read_metadata(stage / "payload")
    if not metadata:
        adjacent = read_json(archive.parent / "artifact.json")
        metadata = adjacent or {}
    if metadata and (metadata.get("version") != version or metadata.get("tuple") != tuple_name):
        return None, "artifact metadata does not match declaration"
    metadata = {
        **metadata,
        "version": version,
        "tuple": tuple_name,
        "artifact_sha256": expected["sha256"],
    }
    target = stage / "repograph"
    shutil.copy2(binary, target)
    target.chmod(target.stat().st_mode | 0o111)
    metadata["binary_sha256"] = sha256(target)
    stat = target.stat()
    metadata["binary_size"] = stat.st_size
    metadata["binary_mtime_ns"] = stat.st_mtime_ns
    (stage / "artifact.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    ok, detail = _smoke(target)
    return target if ok else None, None if ok else f"native smoke check failed: {detail or 'exit status was non-zero'}"


def _phase_locked(
    repo_root: Path,
    declaration: dict[str, Any],
    expected: dict[str, str],
    native_root: Path,
    versions: Path,
    staging_root: Path,
    version: str,
    tuple_name: str,
    release_probe: ReleaseProbe | None,
) -> dict[str, object]:
    base = {"changed": False}
    current = pointer(native_root)
    wanted = versions / f"{version}-{tuple_name}"
    binary, metadata, _ = _verify_version_dir(
        wanted, expected, tuple_name=tuple_name, version=version, full_digest=True
    )
    if binary is not None and current and current.get("version") == version and current.get("tuple") == tuple_name:
        return _result("no-op", version=version, tuple_name=tuple_name, reason="current pointer is already verified", **base)
    if binary is not None:
        pointer_payload = _make_pointer(
            native_root, binary, metadata, version, tuple_name,
            predecessor=_pointer_identity(current),
        )
        try:
            write_current_pointer_json(native_root / "current", pointer_payload)
        except (CurrentPointerWriteError, OSError, ValueError) as exc:
            return _result("activation-failed", version=version, tuple_name=tuple_name, reason=str(exc), **base)
        _prune_versions(versions, wanted, current)
        result = _result(
            "reactivated", version=version, tuple_name=tuple_name,
            reason="verified version was re-activated from disk", changed=True,
        )
        _write_status(native_root, result)
        return result
    stage_id = f"{version}-{tuple_name}"
    stage = staging_root / stage_id
    if stage.exists():
        shutil.rmtree(stage)
    download_dir = staging_root / f".{stage_id}.download"
    download_dir.mkdir(parents=True, exist_ok=True)
    archive, source, error = _resolve_artifact(
        repo_root, declaration, expected, download_dir, release_probe
    )
    if archive is None:
        status = "foreign-origin" if error and error.startswith("foreign-origin:") else "offline" if error and error.startswith("offline:") else "awaiting-artifact"
        result = _result(
            status, version=version, tuple_name=tuple_name,
            reason=error or "artifact is unavailable", source=source, **base,
        )
        _write_status(native_root, result)
        return result
    try:
        prepared, error = _prepare_activation(
            archive, stage, expected, version=version, tuple_name=tuple_name
        )
    except (OSError, ValueError, tarfile.TarError) as exc:
        prepared, error = None, str(exc)
    if prepared is None:
        result = _result(
            "checksum-failure" if error and "checksum" in error else "verification-failure",
            version=version, tuple_name=tuple_name,
            reason=error or "artifact verification failed", source=source, **base,
        )
        _write_status(native_root, result)
        return result
    previous = _pointer_identity(current)
    if wanted.exists():
        shutil.rmtree(wanted)
    os.replace(stage, wanted)
    metadata = read_json(wanted / "artifact.json") or {}
    pointer_payload = _make_pointer(
        native_root, wanted / "repograph", metadata, version, tuple_name, predecessor=previous
    )
    try:
        write_current_pointer_json(native_root / "current", pointer_payload)
    except (CurrentPointerWriteError, OSError, ValueError) as exc:
        result = _result(
            "activation-failed", version=version, tuple_name=tuple_name,
            reason=str(exc), source=source, **base,
        )
        _write_status(native_root, result)
        return result
    _prune_versions(versions, wanted, current)
    result = _result(
        "activated", version=version, tuple_name=tuple_name,
        reason="artifact verified and atomically activated", source=source, changed=True,
    )
    _write_status(native_root, result)
    return result


def run_native_core_phase(
    repo_root: Path,
    *,
    home_root: Path,
    state_root: Path,
    release_probe: ReleaseProbe | None = None,
) -> dict[str, object]:
    tuple_name = host_tuple()
    version = checkout_version(repo_root)
    declaration = read_native_declaration(repo_root)
    base = {"changed": False}
    if declaration is None:
        return _result("not-distributed", version=version, tuple_name=tuple_name, reason="native_core declaration is absent", **base)
    supported = declaration.get("supported_tuples")
    if isinstance(supported, list) and tuple_name not in supported:
        return _result("unsupported-tuple", version=version, tuple_name=tuple_name, reason="host tuple is not supported", **base)
    if not version:
        return _result("not-distributed", version=None, tuple_name=tuple_name, reason="checkout version is unavailable", **base)
    expected = artifact_declaration(declaration, version, tuple_name)
    if expected is None:
        return _result("not-distributed", version=version, tuple_name=tuple_name, reason="checkout version has no native artifact declaration", **base)
    try:
        root = validate_state_root(state_root, home_root)
        native_root = root / "native"
        native_root.mkdir(parents=True, exist_ok=True)
        with (native_root / ".lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            versions = native_root / "versions"
            staging_root = native_root / "staging"
            versions.mkdir(exist_ok=True)
            staging_root.mkdir(exist_ok=True)
            return _phase_locked(
                repo_root, declaration, expected, native_root, versions, staging_root,
                version, tuple_name, release_probe,
            )
    except ValueError as exc:
        return _result("state-write-skipped", version=version, tuple_name=tuple_name, reason=str(exc), **base)
    except OSError as exc:
        return _result("state-write-skipped", version=version, tuple_name=tuple_name, reason=f"native state is not writable: {exc}", **base)


def _make_pointer(
    native_root: Path,
    binary: Path,
    metadata: dict[str, Any],
    version: str,
    tuple_name: str,
    *,
    predecessor: str | None = None,
) -> dict[str, object]:
    relative = binary.resolve().relative_to(native_root.resolve()).as_posix()
    stat = binary.stat()
    pointer: dict[str, object] = {
        "version": version,
        "tuple": tuple_name,
        "binary": relative,
        "artifact_sha256": metadata.get("artifact_sha256"),
        "binary_sha256": metadata.get("binary_sha256") or sha256(binary),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "verified": True,
    }
    if predecessor:
        pointer["predecessor"] = predecessor
    return pointer


def _pointer_identity(value: dict[str, Any] | None) -> str | None:
    if not isinstance(value, dict):
        return None
    version, tuple_name = value.get("version"), value.get("tuple")
    if isinstance(version, str) and isinstance(tuple_name, str):
        return f"{version}-{tuple_name}"
    return None


def _prune_versions(versions: Path, current: Path, old_pointer: dict[str, Any] | None) -> None:
    keep = {current.name}
    if isinstance(old_pointer, dict):
        old_version, old_tuple = old_pointer.get("version"), old_pointer.get("tuple")
        if isinstance(old_version, str) and isinstance(old_tuple, str):
            keep.add(f"{old_version}-{old_tuple}")
    for path in versions.iterdir():
        if path.is_dir() and path.name not in keep:
            shutil.rmtree(path)


__all__ = [
    "run_native_core_phase",
]
