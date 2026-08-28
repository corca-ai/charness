from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest

from scripts import native_core_lib
from scripts.native_core_resolution_lib import native_core_doctor_payload, native_core_path

from .support import CLI, build_test_path, make_fake_claude, make_support_sync_fixture, run_cli

TUPLE = "x86_64-unknown-linux-gnu"


def _native_env(home: Path, store: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["CHARNESS_STATE_HOME"] = str(home / ".local" / "state")
    if store is None:
        env.pop("CHARNESS_NATIVE_ARTIFACT_STORE", None)
    else:
        env["CHARNESS_NATIVE_ARTIFACT_STORE"] = str(store)
    return env


def _set_env(monkeypatch: pytest.MonkeyPatch, env: dict[str, str]) -> None:
    for key in ("CHARNESS_STATE_HOME", "CHARNESS_NATIVE_ARTIFACT_STORE"):
        value = env.get(key)
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)


def _write_artifact(store: Path, version: str, *, content: str = "ok") -> str:
    store.mkdir(parents=True, exist_ok=True)
    name = f"repograph-v{version}-{TUPLE}.tar.gz"
    binary = store / f"{name}.binary"
    binary.write_text(f"#!/bin/sh\n[ \"$1\" = parse-corpus ] && exit 0\nexit 1\n{content}\n", encoding="utf-8")
    binary.chmod(0o755)
    archive = store / name
    with tarfile.open(archive, "w:gz") as bundle:
        bundle.add(binary, arcname="repograph")
        metadata = store / f"{name}.artifact.json"
        metadata.write_text(json.dumps({"version": version, "tuple": TUPLE, "git_commit": "fixture"}) + "\n", encoding="utf-8")
        bundle.add(metadata, arcname="artifact.json")
    binary.unlink()
    metadata.unlink()
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def _repo(tmp_path: Path, version: str, declaration: dict[str, object] | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    manifest: dict[str, object] = {
        "version": version,
        "repository": "https://github.com/corca-ai/charness",
    }
    if declaration is not None:
        manifest["native_core"] = declaration
    (repo / "packaging" / "charness.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _declaration(version: str, digest: str, *, source: str = "fixture/source") -> dict[str, object]:
    name = f"repograph-v{version}-{TUPLE}.tar.gz"
    return {
        "source": source,
        "supported_tuples": [TUPLE],
        "artifacts": {version: {TUPLE: {"name": name, "sha256": digest}}},
    }


def test_clean_first_install_and_already_current_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    digest = _write_artifact(store, "1.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", digest))
    env = _native_env(home, store)
    _set_env(monkeypatch, env)
    first = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    second = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    assert first["status"] == "activated"
    assert second["status"] == "no-op"
    assert native_core_path(home, repo, state_root=home / ".local/state/charness").provenance == "managed"


def test_clean_first_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    digest = _write_artifact(store, "1.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", digest))
    _set_env(monkeypatch, _native_env(home, store))
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    assert result["status"] == "activated"


def test_version_transition_retains_previous_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    d1, d2 = _write_artifact(store, "1.0.0"), _write_artifact(store, "2.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", d1))
    _set_env(monkeypatch, _native_env(home, store))
    native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    manifest = json.loads((repo / "packaging/charness.json").read_text())
    manifest["version"] = "2.0.0"
    manifest["native_core"] = _declaration("2.0.0", d2)
    (repo / "packaging/charness.json").write_text(json.dumps(manifest))
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    versions = {path.name for path in (home / ".local/state/charness/native/versions").iterdir()}
    assert result["status"] == "activated"
    assert versions == {f"1.0.0-{TUPLE}", f"2.0.0-{TUPLE}"}


def test_unsupported_tuple_does_not_create_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = tmp_path / "store"
    digest = _write_artifact(store, "1.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", digest))
    home = tmp_path / "home"
    _set_env(monkeypatch, _native_env(home, store))
    monkeypatch.setattr(native_core_lib, "host_tuple", lambda: "aarch64-unknown-linux-gnu")
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    assert result["status"] == "unsupported-tuple"
    assert not (home / ".local/state/charness/native").exists()


def test_checksum_failure_leaves_current_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = tmp_path / "store"
    _write_artifact(store, "1.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", "0" * 64))
    home = tmp_path / "home"
    _set_env(monkeypatch, _native_env(home, store))
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness")
    assert result["status"] == "checksum-failure"
    assert not (home / ".local/state/charness/native/current").exists()


def test_interrupted_activation_keeps_previous_current(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    d1, d2 = _write_artifact(store, "1.0.0"), _write_artifact(store, "2.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", d1))
    _set_env(monkeypatch, _native_env(home, store))
    state = home / ".local/state/charness"
    native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    manifest = json.loads((repo / "packaging/charness.json").read_text())
    manifest.update({"version": "2.0.0", "native_core": _declaration("2.0.0", d2)})
    (repo / "packaging/charness.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(native_core_lib, "write_current_pointer_json", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("interrupted")))
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    current = json.loads((state / "native/current").read_text())
    assert result["status"] == "activation-failed"
    assert current["version"] == "1.0.0"


def test_checkout_rollback_reactivates_verified_disk_without_probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    d1, d2 = _write_artifact(store, "1.0.0"), _write_artifact(store, "2.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", d1))
    _set_env(monkeypatch, _native_env(home, store))
    state = home / ".local/state/charness"
    native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    manifest = json.loads((repo / "packaging/charness.json").read_text())
    manifest.update({"version": "2.0.0", "native_core": _declaration("2.0.0", d2)})
    (repo / "packaging/charness.json").write_text(json.dumps(manifest))
    native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    manifest.update({"version": "1.0.0", "native_core": _declaration("1.0.0", d1)})
    (repo / "packaging/charness.json").write_text(json.dumps(manifest))
    monkeypatch.delenv("CHARNESS_NATIVE_ARTIFACT_STORE", raising=False)
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    assert result["status"] == "reactivated"
    assert json.loads((state / "native/current").read_text())["version"] == "1.0.0"


def test_awaiting_artifact_and_offline_are_typed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", "1" * 64))
    home = tmp_path / "home"
    _set_env(monkeypatch, _native_env(home))
    awaiting = native_core_lib.run_native_core_phase(
        repo, home_root=home, state_root=home / ".local/state/charness",
        release_probe=lambda: {"status": "ok", "asset_names": []},
    )
    assert awaiting["status"] == "awaiting-artifact"
    offline = native_core_lib.run_native_core_phase(
        repo, home_root=home, state_root=home / ".local/state/charness",
        release_probe=lambda: {"status": "error", "error": "network unavailable"},
    )
    assert offline["status"] == "offline"


def test_foreign_origin_refuses_release_probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", "1" * 64, source="corca-ai/charness"))
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/other/project.git"], cwd=repo, check=True)
    home = tmp_path / "home"
    _set_env(monkeypatch, _native_env(home))
    called = False

    def probe():
        nonlocal called
        called = True
        return {"status": "ok", "asset_names": []}

    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness", release_probe=probe)
    assert result["status"] == "foreign-origin"
    assert called is False


def test_not_distributed_is_inert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path, "1.0.0")
    home = tmp_path / "home"
    env = _native_env(home)
    _set_env(monkeypatch, env)
    result = native_core_lib.run_native_core_phase(repo, home_root=home, state_root=home / ".local/state/charness", release_probe=lambda: pytest.fail("probe called"))
    assert result["status"] == "not-distributed"
    assert not (home / ".local/state/charness/native").exists()
    locator = native_core_path(home, repo, state_root=home / ".local/state/charness")
    assert locator.status == "not-distributed"
    assert not hasattr(locator, "path")


def test_pointer_checkout_skew_is_stale_with_remediation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home, store = tmp_path / "home", tmp_path / "store"
    d1, d2 = _write_artifact(store, "1.0.0"), _write_artifact(store, "2.0.0")
    repo = _repo(tmp_path, "1.0.0", _declaration("1.0.0", d1))
    _set_env(monkeypatch, _native_env(home, store))
    state = home / ".local/state/charness"
    native_core_lib.run_native_core_phase(repo, home_root=home, state_root=state)
    manifest = json.loads((repo / "packaging/charness.json").read_text())
    manifest.update({"version": "2.0.0", "native_core": _declaration("2.0.0", d2)})
    (repo / "packaging/charness.json").write_text(json.dumps(manifest))
    doctor = native_core_doctor_payload(home, repo, state_root=state)
    assert doctor["status"] == "stale"
    assert "charness update" in doctor["message"]


def test_uninstall_removes_native_state_and_reports_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home = tmp_path / "home"
    native = home / ".local/state/charness/native/versions/fixture"
    native.mkdir(parents=True)
    env = _native_env(home)
    env["PATH"] = "/usr/bin:/bin"
    result = subprocess.run(
        [os.environ.get("PYTHON", "python3"), str(CLI), "uninstall", "--home-root", str(home)],
        cwd=CLI.parent,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "removed_native_core: true" in result.stdout.lower()
    assert not (home / ".local/state/charness/native").exists()


def test_main_state_behavior_is_inert_when_declaration_is_absent(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(
        CLI.parent,
        repo,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "charness-artifacts", ".pytest_cache", "__pycache__", ".ruff_cache"),
    )
    home = tmp_path / "home"
    env = _native_env(home)
    env["PATH"] = build_test_path(make_fake_claude(tmp_path).parent)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(make_support_sync_fixture(tmp_path))
    result = run_cli(
        "init", "--repo-root", str(repo), "--home-root", str(home),
        "--skip-cli-install", "--skip-claude-wrapper", "--detail", env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "status: not-distributed" in result.stdout
    assert not (home / ".local/state/charness/native").exists()
