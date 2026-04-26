from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from .support import CLI, clone_seeded_managed_home, make_release_fixture

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
CURRENT_RELEASE_TAG = f"v{CURRENT_VERSION}"
NEWER_RELEASE_TAG = "v9.9.9"
NEWER_PRERELEASE_TAG = "v9.9.9-rc.1"
OLDER_RELEASE_TAG = "v0.0.0"
pytestmark = pytest.mark.ci_only


def test_charness_version_can_refresh_latest_release_and_record_provenance(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path, charness_tag=NEWER_RELEASE_TAG)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    version_result = subprocess.run(
        [sys.executable, str(installed_cli), "version", "--home-root", str(home_root), "--json", "--check"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["current_version"] == CURRENT_VERSION
    assert payload["version_provenance"]["invocation_kind"] == "installed-cli"
    assert payload["version_provenance"]["install_method"] == "managed-local-cli"
    assert payload["latest_release_check"]["latest_tag"] == NEWER_RELEASE_TAG
    assert payload["latest_release_check"]["update_available"] is True
    assert payload["update_notice"] == (
        f"charness update available: `{CURRENT_VERSION}` -> `{NEWER_RELEASE_TAG}`. "
        f"Run `charness update`. https://github.com/corca-ai/charness/releases/tag/{NEWER_RELEASE_TAG}"
    )
    version_state = json.loads(
        (home_root / ".local" / "state" / "charness" / "version-state.json").read_text(encoding="utf-8")
    )
    assert version_state["version_provenance"]["invocation_kind"] == "installed-cli"
    assert version_state["latest_release"]["latest_tag"] == NEWER_RELEASE_TAG
    assert version_state["latest_release"]["current_version"] == CURRENT_VERSION


def test_charness_version_skips_notice_when_latest_release_matches_current(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path, charness_tag=CURRENT_RELEASE_TAG)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    version_result = subprocess.run(
        [sys.executable, str(installed_cli), "version", "--home-root", str(home_root), "--json", "--check"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["latest_release_check"]["latest_tag"] == CURRENT_RELEASE_TAG
    assert payload["latest_release_check"]["update_available"] is False
    assert payload["update_notice"] is None


def test_charness_version_skips_notice_when_latest_release_is_older(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path, charness_tag=OLDER_RELEASE_TAG)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    version_result = subprocess.run(
        [sys.executable, str(installed_cli), "version", "--home-root", str(home_root), "--json", "--check"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["latest_release_check"]["latest_tag"] == OLDER_RELEASE_TAG
    assert payload["latest_release_check"]["update_available"] is False
    assert payload["update_notice"] is None


def test_installed_cli_can_emit_auto_update_notice_for_newer_release(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path, charness_tag=NEWER_RELEASE_TAG)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_FORCE_UPDATE_CHECK"] = "1"

    installed_cli = home_root / ".local" / "bin" / "charness"
    doctor_result = subprocess.run(
        [sys.executable, str(installed_cli), "doctor", "--home-root", str(home_root)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    assert f"charness update available: `{CURRENT_VERSION}` -> `{NEWER_RELEASE_TAG}`." in doctor_result.stderr


def test_charness_version_preserves_prerelease_tag_in_update_notice(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path, charness_tag=NEWER_PRERELEASE_TAG)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    version_result = subprocess.run(
        [sys.executable, str(installed_cli), "version", "--home-root", str(home_root), "--json", "--check"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["latest_release_check"]["latest_tag"] == NEWER_PRERELEASE_TAG
    assert payload["latest_release_check"]["latest_version"] == "9.9.9-rc.1"
    assert payload["latest_release_check"]["update_available"] is True
    assert payload["update_notice"] == (
        f"charness update available: `{CURRENT_VERSION}` -> `{NEWER_PRERELEASE_TAG}`. "
        f"Run `charness update`. https://github.com/corca-ai/charness/releases/tag/{NEWER_PRERELEASE_TAG}"
    )


def test_charness_version_degrades_when_state_cache_is_unwritable(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    home_root.mkdir()
    (home_root / ".local").write_text("not a directory\n", encoding="utf-8")

    version_result = subprocess.run(
        [sys.executable, str(CLI), "version", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["current_version"] == CURRENT_VERSION
    assert payload["version_state_path"] == str(home_root / ".local" / "state" / "charness" / "version-state.json")
    assert (home_root / ".local").is_file()
