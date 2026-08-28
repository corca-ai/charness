#!/usr/bin/env python3
"""Build and package the version-bound Charness native artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path
from typing import Sequence

from runtime_bootstrap import import_repo_module, runtime_root
from yaml_output import emit_yaml

VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
CRATE_RELATIVE_PATH = Path("native") / "repograph"


class BuildError(RuntimeError):
    """Raised when the native artifact cannot be built safely."""


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: Sequence[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command), cwd=cwd, env=env, check=False, capture_output=True, text=True
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BuildError(f"could not run {' '.join(command)}: {exc}") from exc


def _manifest_version(repo_root: Path) -> str:
    path = repo_root / "packaging" / "charness.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"could not read product version from {path}: {exc}") from exc
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise BuildError(f"product version is missing or invalid in {path}")
    return version


def _git_output(repo_root: Path, arguments: Sequence[str]) -> str:
    result = _run(["git", *arguments], cwd=repo_root)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BuildError(f"git {' '.join(arguments)} failed: {detail or result.returncode}")
    return result.stdout.strip()


def _require_clean_tree(repo_root: Path) -> None:
    for arguments in (("diff", "--quiet"), ("diff", "--cached", "--quiet")):
        result = _run(["git", *arguments], cwd=repo_root)
        if result.returncode == 1:
            raise BuildError("refusing native build: git tree is dirty")
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise BuildError(f"git {' '.join(arguments)} failed: {detail or result.returncode}")

    # `--exclude-standard` is intentional: Cargo writes target/ during this
    # operation, and that ignored tree must not turn a clean source checkout
    # into a false dirty-build refusal.
    untracked = _run(
        ["git", "ls-files", "--others", "--exclude-standard", "--directory", "-z"],
        cwd=repo_root,
    )
    if untracked.returncode != 0:
        detail = (untracked.stderr or untracked.stdout).strip()
        raise BuildError(f"git ls-files failed: {detail or untracked.returncode}")
    if untracked.stdout:
        raise BuildError("refusing native build: git tree is dirty (untracked files present)")


def _external_output_dir(repo_root: Path, value: str | None) -> Path:
    if value:
        output = Path(value).expanduser().resolve()
    else:
        try:
            output = runtime_root(repo_root) / "native-artifacts"
        except OSError as exc:
            raise BuildError(f"could not resolve external runtime output root: {exc}") from exc
    try:
        output.relative_to(repo_root.resolve())
    except ValueError:
        return output
    raise BuildError(f"artifact output must be outside the repository: {output}")


def _pinned_toolchain(crate_root: Path) -> str:
    path = crate_root / "rust-toolchain.toml"
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BuildError(f"pinned Rust toolchain is unavailable at {path}: {exc}") from exc
    match = re.search(r"(?m)^\s*channel\s*=\s*[\"']([^\"']+)[\"']\s*$", contents)
    if not match:
        raise BuildError(f"pinned Rust toolchain channel is missing from {path}")
    return match.group(1)


def _build(crate_root: Path, toolchain: str) -> Path:
    environment = os.environ.copy()
    environment["RUSTUP_TOOLCHAIN"] = toolchain
    result = _run(["cargo", "build", "--release", "--locked"], cwd=crate_root, env=environment)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BuildError(f"cargo build --release --locked failed: {detail or result.returncode}")
    binary = crate_root / "target" / "release" / "repograph"
    if not binary.is_file():
        raise BuildError(f"cargo completed without producing {binary}")
    return binary


def _rustc_version(crate_root: Path, toolchain: str) -> str:
    environment = os.environ.copy()
    environment["RUSTUP_TOOLCHAIN"] = toolchain
    result = _run(["rustc", "--version"], cwd=crate_root, env=environment)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BuildError(f"could not read pinned rustc version: {detail or result.returncode}")
    version = result.stdout.strip()
    if not version:
        raise BuildError("pinned rustc returned an empty version")
    return version


def _git_tag(repo_root: Path) -> str | None:
    result = _run(["git", "describe", "--tags", "--exact-match", "HEAD"], cwd=repo_root)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def _write_archive(binary: Path, output_dir: Path, version: str, tuple_name: str) -> Path:
    archive = output_dir / f"repograph-v{version}-{tuple_name}.tar.gz"
    try:
        with tarfile.open(archive, "w:gz") as bundle:
            bundle.add(binary, arcname="repograph", recursive=False)
    except (OSError, tarfile.TarError) as exc:
        raise BuildError(f"could not write {archive}: {exc}") from exc
    return archive


def build_native_artifact(repo_root: Path, *, out_dir: Path | None = None) -> dict[str, object]:
    """Build one native artifact and return its sidecar payload."""
    repo_root = repo_root.resolve()
    version = _manifest_version(repo_root)
    _require_clean_tree(repo_root)
    crate_root = repo_root / CRATE_RELATIVE_PATH
    if not crate_root.is_dir():
        raise BuildError(f"native repograph crate is missing: {crate_root}")
    output_dir = _external_output_dir(repo_root, str(out_dir) if out_dir else None)
    output_dir.mkdir(parents=True, exist_ok=True)
    native_resolution = import_repo_module(__file__, "scripts.native_core_resolution_lib")
    tuple_name = native_resolution.host_tuple()
    toolchain = _pinned_toolchain(crate_root)
    binary = _build(crate_root, toolchain)
    rustc_version = _rustc_version(crate_root, toolchain)
    lockfile = crate_root / "Cargo.lock"
    if not lockfile.is_file():
        raise BuildError(f"Cargo.lock is missing: {lockfile}")
    archive = _write_archive(binary, output_dir, version, tuple_name)
    archive_digest = _digest(archive)
    binary_digest = _digest(binary)
    commit = _git_output(repo_root, ("rev-parse", "HEAD"))
    metadata: dict[str, object] = {
        "product": "charness",
        "version": version,
        "tuple": tuple_name,
        "artifact": archive.name,
        "artifact_sha256": archive_digest,
        "binary": "repograph",
        "binary_sha256": binary_digest,
        "binary_size": binary.stat().st_size,
        "git_tag": _git_tag(repo_root),
        "git_commit": commit,
        "toolchain": toolchain,
        "rustc_version": rustc_version,
        "cargo_lock_sha256": _digest(lockfile),
    }
    (output_dir / "SHA256SUMS").write_text(
        f"{archive_digest}  {archive.name}\n", encoding="utf-8"
    )
    (output_dir / "artifact.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Charness checkout")
    parser.add_argument("--out-dir", type=Path, help="External artifact output directory")
    args = parser.parse_args()
    try:
        metadata = build_native_artifact(args.repo_root, out_dir=args.out_dir)
    except BuildError as exc:
        parser.error(str(exc))
    emit_yaml(metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
