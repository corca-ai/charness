from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.native_core_resolution_lib import host_tuple

ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = ROOT / "scripts" / "check_native_release_asset.py"


def _repo(tmp_path: Path, *, declared: bool) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    version = "8.0.0"
    tuple_name = host_tuple()
    manifest: dict[str, object] = {
        "version": version,
        "repository": "https://github.com/corca-ai/charness",
    }
    if declared:
        manifest["native_core"] = {
            "source": "corca-ai/charness",
            "supported_tuples": [tuple_name],
            "artifacts": {
                version: {
                    tuple_name: {
                        "name": f"repograph-v{version}-{tuple_name}.tar.gz",
                        "sha256": "a" * 64,
                    }
                }
            },
        }
    (repo / "packaging" / "charness.json").write_text(
        json.dumps(manifest) + "\n", encoding="utf-8"
    )
    return repo, f"repograph-v{version}-{tuple_name}.tar.gz"


def _run_check(repo: Path, fixture: Path) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "CHARNESS_RELEASE_PROBE_FIXTURES": str(fixture)}
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def _fixture(path: Path, asset_names: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "tag_name": "v8.0.0",
                    "assets": [{"name": name} for name in asset_names],
                }
            }
        ),
        encoding="utf-8",
    )


def test_declared_native_asset_present_passes_from_release_fixture(tmp_path: Path) -> None:
    repo, asset = _repo(tmp_path, declared=True)
    fixture = tmp_path / "release.json"
    _fixture(fixture, [asset])

    result = _run_check(repo, fixture)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "pass"
    assert payload["asset"] == asset


def test_declared_native_asset_missing_fails_from_release_fixture(tmp_path: Path) -> None:
    repo, asset = _repo(tmp_path, declared=True)
    fixture = tmp_path / "release.json"
    _fixture(fixture, ["other-asset.tar.gz"])

    result = _run_check(repo, fixture)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "fail"
    assert payload["asset"] == asset


def test_undeclared_version_is_typed_not_applicable_without_release_probe(tmp_path: Path) -> None:
    repo, _asset = _repo(tmp_path, declared=False)
    missing_fixture = tmp_path / "fixture-does-not-exist.json"
    environment = {**os.environ, "CHARNESS_RELEASE_PROBE_FIXTURES": str(missing_fixture)}

    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "not-applicable"
