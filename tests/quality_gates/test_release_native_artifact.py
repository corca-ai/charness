from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.native_core_resolution_lib import canonical_artifact_name, host_tuple

from .release_publish_fixtures import (
    _release_env,
    _run_publish,
    _seed_publish_release_repo,
    _simulate_partial_publish,
)
from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
NATIVE_PATH = ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_native_artifact.py"
FAKE_GH_PATH = ROOT / "tests" / "quality_gates" / "fixtures" / "release_publish_fake_gh.py"
NATIVE = load_module("publish_release_native_artifact_tests", NATIVE_PATH)
HELPERS = load_module("publish_release_helpers_native_artifact_tests", ROOT / "skills/public/release/scripts/publish_release_helpers.py")


def _write_manifest(
    repo: Path,
    version: str = "8.0.0",
    *,
    native_core: dict | None = None,
) -> None:
    (repo / "packaging").mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"version": version}
    if native_core is not None:
        manifest["native_core"] = native_core
    (repo / "packaging" / "charness.json").write_text(
        json.dumps(manifest) + "\n", encoding="utf-8"
    )


def _native_core(version: str, *, name: str | None = None, digest: str = "a" * 64) -> dict:
    tuple_name = host_tuple()
    return {
        "supported_tuples": [tuple_name],
        "artifacts": {
            version: {
                tuple_name: {
                    "name": canonical_artifact_name(version, tuple_name) if name is None else name,
                    "sha256": digest,
                }
            }
        },
    }


def _declared_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: bytes = b"archive") -> tuple[Path, str]:
    repo = tmp_path / "repo"
    digest = hashlib.sha256(content).hexdigest()
    version = "8.0.0"
    asset = canonical_artifact_name(version, host_tuple())
    _write_manifest(repo, version, native_core=_native_core(version, digest=digest))
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime))
    archive = runtime / "native-artifacts" / asset
    archive.parent.mkdir(parents=True)
    archive.write_bytes(content)
    return repo, asset


def test_canonical_artifact_name_is_shared_by_version_and_tuple() -> None:
    assert canonical_artifact_name("8.0.0", "x86_64-unknown-linux-gnu") == (
        "repograph-v8.0.0-x86_64-unknown-linux-gnu.tar.gz"
    )


def test_preflight_absent_declaration_stops_before_other_resolution(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest(repo)

    def unexpected(*_args, **_kwargs):
        raise AssertionError("native declaration no-op must not resolve anything else")

    monkeypatch.setattr(NATIVE, "checkout_version", unexpected)
    monkeypatch.setattr(NATIVE, "host_tuple", unexpected)
    monkeypatch.setattr(NATIVE, "runtime_root", unexpected)

    assert NATIVE.native_artifact_preflight(repo) == {
        "status": "not-applicable",
        "asset": None,
        "reason": "native_core declaration is absent",
    }


def test_upload_absent_declaration_stops_before_backend_or_path_work(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest(repo)

    def unexpected(*_args, **_kwargs):
        raise AssertionError("native declaration no-op must not upload")

    monkeypatch.setattr(NATIVE, "native_artifact_preflight", unexpected)
    result = NATIVE.upload_native_artifact(
        repo,
        backend={"id": "gh", "commands": None},
        tag_name="v8.0.0",
        backend_command=unexpected,
        run=unexpected,
    )
    assert result["status"] == "not-applicable"


@pytest.mark.parametrize(
    ("native_core", "field"),
    [
        (_native_core("8.0.0", name=""), "name"),
        (_native_core("8.0.0", digest="short"), "sha256"),
    ],
)
def test_preflight_refuses_a_malformed_declared_table_entry(
    tmp_path: Path, native_core: dict, field: str
) -> None:
    repo = tmp_path / "repo"
    _write_manifest(repo, native_core=native_core)

    with pytest.raises(SystemExit, match=field):
        NATIVE.native_artifact_preflight(repo)


def test_preflight_treats_a_missing_version_or_tuple_entry_as_not_applicable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_manifest(repo, native_core={"artifacts": {}})

    assert NATIVE.native_artifact_preflight(repo) == {
        "status": "not-applicable",
        "asset": None,
        "reason": "checkout version has no native artifact declaration",
    }


def test_preflight_names_the_resolved_archive_and_build_command_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    version = "8.0.0"
    _write_manifest(repo, native_core=_native_core(version))
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime))
    expected = runtime / "native-artifacts" / canonical_artifact_name(version, host_tuple())

    with pytest.raises(SystemExit) as error:
        NATIVE.native_artifact_preflight(repo)

    message = str(error.value)
    assert str(expected) in message
    assert "python3 scripts/build_native_artifact.py --repo-root" in message


def test_preflight_refuses_a_digest_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _asset = _declared_archive(tmp_path, monkeypatch, content=b"actual")
    manifest = json.loads((repo / "packaging" / "charness.json").read_text(encoding="utf-8"))
    manifest["native_core"]["artifacts"]["8.0.0"][host_tuple()]["sha256"] = "b" * 64
    (repo / "packaging" / "charness.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SystemExit, match="sha256 mismatch"):
        NATIVE.native_artifact_preflight(repo)


def test_upload_uses_distinct_asset_read_and_upload_ops_and_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, asset = _declared_archive(tmp_path, monkeypatch)
    preflight = NATIVE.native_artifact_preflight(repo)
    commands: list[list[str]] = []

    def run(command, *, cwd, check=True):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="", args=command)

    uploaded = NATIVE.upload_native_artifact(
        repo,
        backend={"id": "gh", "commands": None},
        tag_name="v8.0.0",
        preflight=preflight,
        backend_command=HELPERS.backend_command,
        run=run,
    )
    assert uploaded == {
        "status": "uploaded",
        "asset": asset,
        "reason": "native artifact uploaded to the release",
    }
    assert commands == [
        ["gh", "release", "view", "v8.0.0", "--json", "assets", "--jq", ".assets[].name"],
        ["gh", "release", "upload", "v8.0.0", str(preflight["path"])],
    ]
    assert "--clobber" not in commands[-1]

    commands.clear()

    def already_present(command, *, cwd, check=True):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=f"{asset}\n", stderr="", args=command)

    present = NATIVE.upload_native_artifact(
        repo,
        backend={"id": "gh", "commands": None},
        tag_name="v8.0.0",
        preflight=preflight,
        backend_command=HELPERS.backend_command,
        run=already_present,
    )
    assert present["status"] == "already-present"
    assert commands == [["gh", "release", "view", "v8.0.0", "--json", "assets", "--jq", ".assets[].name"]]


def test_non_gh_backend_without_new_asset_ops_refuses_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _asset = _declared_archive(tmp_path, monkeypatch)
    with pytest.raises(SystemExit, match="release_assets"):
        NATIVE.upload_native_artifact(
            repo,
            backend={"id": "acme", "commands": None},
            tag_name="v8.0.0",
            preflight=NATIVE.native_artifact_preflight(repo),
            backend_command=HELPERS.backend_command,
            run=lambda *_args, **_kwargs: pytest.fail("backend refusal must precede execution"),
        )


def test_fake_gh_rejects_malformed_native_asset_commands_and_records_names(tmp_path: Path) -> None:
    log = tmp_path / "gh-log.json"
    release_state = tmp_path / "release-state.json"
    asset_state = tmp_path / "release-assets.json"
    environment = {
        **os.environ,
        "FAKE_GH_LOG": str(log),
        "FAKE_GH_RELEASE_STATE": str(release_state),
        "FAKE_GH_RELEASE_ASSET_STATE": str(asset_state),
    }

    malformed_upload = subprocess.run(
        [sys.executable, str(FAKE_GH_PATH), "release", "upload", "v8.0.0", "/tmp/a", "extra"],
        check=False, capture_output=True, text=True, env=environment,
    )
    assert malformed_upload.returncode == 2

    uploaded = subprocess.run(
        [sys.executable, str(FAKE_GH_PATH), "release", "upload", "v8.0.0", "/tmp/native.tar.gz"],
        check=False, capture_output=True, text=True, env=environment,
    )
    assert uploaded.returncode == 0

    malformed_view = subprocess.run(
        [sys.executable, str(FAKE_GH_PATH), "release", "view", "v8.0.0", "--bad"],
        check=False, capture_output=True, text=True, env=environment,
    )
    assert malformed_view.returncode == 2
    assets = subprocess.run(
        [sys.executable, str(FAKE_GH_PATH), "release", "view", "v8.0.0", "--json", "assets", "--jq", ".assets[].name"],
        check=False, capture_output=True, text=True, env=environment,
    )
    assert assets.returncode == 0
    assert assets.stdout.strip() == "native.tar.gz"


def _add_native_archive(repo: Path, runtime: Path, version: str = "0.0.0") -> tuple[Path, str]:
    content = b"native fixture archive"
    digest = hashlib.sha256(content).hexdigest()
    asset = canonical_artifact_name(version, host_tuple())
    manifest_path = repo / "packaging" / "demo.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["native_core"] = _native_core(version, name=asset, digest=digest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (repo / "packaging" / "charness.json").write_text(
        json.dumps({"version": version, "native_core": manifest["native_core"]}) + "\n",
        encoding="utf-8",
    )
    archive = runtime / "native-artifacts" / asset
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(content)
    return archive, asset


@pytest.mark.release_only
def test_resume_uploads_native_asset_after_create(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    runtime = tmp_path / "runtime"
    env = _release_env(tmp_path, bin_dir)
    env["CHARNESS_RUNTIME_ROOT"] = str(runtime)
    archive, asset = _add_native_archive(repo, runtime)
    _simulate_partial_publish(repo)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["native_artifact_upload"]["status"] == "uploaded"
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["release", "view", "v0.0.0", "--json", "assets", "--jq", ".assets[].name"] in gh_log
    assert ["release", "upload", "v0.0.0", str(archive)] in gh_log
    assert payload["native_artifact_upload"]["asset"] == asset


@pytest.mark.release_only
def test_resume_repairs_existing_release_without_recreating_it(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    runtime = tmp_path / "runtime"
    env = _release_env(tmp_path, bin_dir)
    env["CHARNESS_RUNTIME_ROOT"] = str(runtime)
    archive, asset = _add_native_archive(repo, runtime)
    _simulate_partial_publish(repo)
    Path(env["FAKE_GH_RELEASE_STATE"]).write_text(json.dumps(["v0.0.0"]) + "\n", encoding="utf-8")

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["native_artifact_upload"]["status"] == "uploaded"
    assert payload["native_artifact_upload"]["asset"] == asset
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)
    assert ["release", "upload", "v0.0.0", str(archive)] in gh_log
