from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import build_native_artifact as build_module
from scripts.build_native_artifact import BuildError, _require_clean_tree
from scripts.native_core_resolution_lib import host_tuple

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_native_artifact.py"
FIXTURES = ROOT / "tests" / "charness_cli" / "fixtures"


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _seed_repo(tmp_path: Path, *, version: object = "1.2.3") -> Path:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "native" / "repograph").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps({"version": version}) + "\n", encoding="utf-8"
    )
    (repo / "native" / "repograph" / "Cargo.lock").write_text("fake lock\n", encoding="utf-8")
    (repo / "native" / "repograph" / "rust-toolchain.toml").write_text(
        '[toolchain]\nchannel = "1.96.0"\n', encoding="utf-8"
    )
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    (repo / ".gitignore").write_text(
        "target/\nignored-only/*\nmixed/ignored.txt\n", encoding="utf-8"
    )
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "seed fixture")
    _git(repo, "tag", "v1.2.3")
    return repo


def _fake_tool_path(tmp_path: Path, name: str) -> Path:
    directory = tmp_path / "bin"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    shutil.copy2(FIXTURES / f"fake_{name}.py", target)
    target.chmod(0o755)
    return directory


def _run_build(repo: Path, out_dir: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    cargo_bin = _fake_tool_path(tmp_path, "cargo")
    rustc_bin = _fake_tool_path(tmp_path, "rustc")
    log = tmp_path / "cargo.log"
    environment = {
        **os.environ,
        "PATH": str(cargo_bin) + ":" + str(rustc_bin) + ":" + os.environ["PATH"],
        "FAKE_CARGO_LOG": str(log),
    }
    return subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--repo-root", str(repo), "--out-dir", str(out_dir)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def test_build_packages_binary_checksums_and_metadata_with_fake_cargo(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    output = tmp_path / "artifacts"

    result = _run_build(repo, output, tmp_path)

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["version"] == "1.2.3"
    tuple_name = host_tuple()
    archive = output / f"repograph-v1.2.3-{tuple_name}.tar.gz"
    assert archive.is_file()
    with tarfile.open(archive, "r:gz") as bundle:
        assert bundle.getnames() == ["repograph"]
        assert bundle.extractfile("repograph").read() == b"#!/bin/sh\nprintf '%s\\n' fake-repograph\n"

    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = (output / "SHA256SUMS").read_text(encoding="utf-8").split()
    assert sums == [archive_digest, archive.name]
    metadata = json.loads((output / "artifact.json").read_text(encoding="utf-8"))
    assert metadata["product"] == "charness"
    assert metadata["version"] == "1.2.3"
    assert metadata["tuple"] == tuple_name
    assert metadata["artifact"] == archive.name
    assert metadata["artifact_sha256"] == archive_digest
    assert metadata["git_tag"] == "v1.2.3"
    assert metadata["git_commit"] == _git(repo, "rev-parse", "HEAD")
    assert metadata["toolchain"] == "1.96.0"
    assert metadata["rustc_version"] == "rustc 1.96.0 (fake-toolchain)"
    assert metadata["cargo_lock_sha256"] == hashlib.sha256(
        (repo / "native" / "repograph" / "Cargo.lock").read_bytes()
    ).hexdigest()
    assert (output / "artifact.json").is_file()
    assert not (repo / "repograph-v1.2.3.tar.gz").exists()
    assert (tmp_path / "cargo.log").read_text(encoding="utf-8").splitlines() == [
        "build --release --locked",
        "1.96.0",
    ]


def test_build_allows_ignored_cargo_target_and_default_output_is_external(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _seed_repo(tmp_path)
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)
    cargo_bin = _fake_tool_path(tmp_path, "cargo")
    rustc_bin = _fake_tool_path(tmp_path, "rustc")
    environment = {
        **os.environ,
        "PATH": str(cargo_bin) + ":" + str(rustc_bin) + ":" + os.environ["PATH"],
        "FAKE_CARGO_LOG": str(tmp_path / "cargo.log"),
    }
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 0, result.stderr
    assert (runtime / "native-artifacts" / "artifact.json").is_file()
    assert not (repo / "native-artifacts").exists()
    assert not subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_build_refuses_dirty_tree_before_invoking_cargo(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")
    output = tmp_path / "artifacts"

    result = _run_build(repo, output, tmp_path)

    assert result.returncode != 0
    assert "git tree is dirty" in result.stderr
    assert not (tmp_path / "cargo.log").exists()
    assert not output.exists()


def test_clean_tree_ignores_directories_with_only_ignored_contents(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    ignored_directory = repo / "ignored-only"
    ignored_directory.mkdir()
    (ignored_directory / "cargo-output").write_text("ignored\n", encoding="utf-8")

    _require_clean_tree(repo)


@pytest.mark.parametrize("relative", ["untracked.txt", "mixed/untracked.txt"])
def test_clean_tree_still_refuses_genuinely_untracked_files(tmp_path: Path, relative: str) -> None:
    repo = _seed_repo(tmp_path)
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("untracked\n", encoding="utf-8")

    with pytest.raises(BuildError, match="untracked files present"):
        _require_clean_tree(repo)


def test_builder_uses_the_shared_canonical_name_owner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _seed_repo(tmp_path)
    binary = repo / "native" / "repograph" / "target" / "release" / "repograph"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"fake binary\n")
    resolution = SimpleNamespace(
        host_tuple=lambda: "fixture-tuple",
        canonical_artifact_name=lambda _version, _tuple: "owned-by-resolution.tar.gz",
    )
    monkeypatch.setattr(build_module, "import_repo_module", lambda *_args: resolution)
    monkeypatch.setattr(build_module, "_build", lambda *_args: binary)
    monkeypatch.setattr(build_module, "_rustc_version", lambda *_args: "rustc fixture")

    metadata = build_module.build_native_artifact(repo, out_dir=tmp_path / "artifacts")

    assert metadata["artifact"] == "owned-by-resolution.tar.gz"
    assert (tmp_path / "artifacts" / "owned-by-resolution.tar.gz").is_file()


@pytest.mark.parametrize("bad_manifest", [{}, {"version": "not-a-version"}, "not an object"])
def test_build_refuses_when_product_version_cannot_be_read(
    tmp_path: Path, bad_manifest: object
) -> None:
    repo = _seed_repo(tmp_path)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps(bad_manifest) + "\n", encoding="utf-8"
    )

    result = _run_build(repo, tmp_path / "artifacts", tmp_path)

    assert result.returncode != 0
    assert "product version is missing or invalid" in result.stderr
    assert not (tmp_path / "cargo.log").exists()
