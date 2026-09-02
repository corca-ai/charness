from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from .support import (
    CLI,
    ROOT,
    build_test_path,
    clone_seeded_managed_home,
    make_fake_claude,
    pin_state_home,
    run_cli,
    run_cli_path,
)


@pytest.mark.release_only
def test_charness_doctor_selects_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(
        tmp_path, seeded_managed_home["home_root"], share_source_checkout=True
    )
    doctor_result = run_cli("doctor", "--home-root", str(home_root), env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = yaml.safe_load(doctor_result.stdout)
    assert payload["next_action"]["kind"] == "restart"
    assert payload["next_action"]["host"] == "claude"
    assert payload["next_action"]["message"] == payload["claude_host_guidance"]["message"]


@pytest.mark.release_only
def test_charness_doctor_prints_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(
        tmp_path, seeded_managed_home["home_root"], share_source_checkout=True
    )
    doctor_result = run_cli("doctor", "--home-root", str(home_root), env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = yaml.safe_load(doctor_result.stdout)
    assert payload["next_action"]["host"] == "claude"
    assert payload["next_action"]["message"] == "Claude host install markers are present. Restart Claude Code to load or refresh charness."


@pytest.mark.release_only
def test_charness_doctor_next_action_flag_prints_only_message(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(
        tmp_path, seeded_managed_home["home_root"], share_source_checkout=True
    )
    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--next-action", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    assert yaml.safe_load(doctor_result.stdout) == {
        "next_action": "Claude host install markers are present. Restart Claude Code to load or refresh charness."
    }


def test_charness_doctor_next_action_without_source_uses_manual_guidance(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True, exist_ok=True)
    installed_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    installed_cli.chmod(0o755)

    doctor_result = run_cli_path(
        installed_cli,
        "doctor",
        "--home-root",
        str(home_root),
        cwd=tmp_path,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = yaml.safe_load(doctor_result.stdout)
    assert payload["next_action"]["kind"] == "manual"
    assert payload["next_action"]["host"] == "claude"
    assert payload["next_action"]["message"] == payload["claude_host_guidance"]["message"]


@pytest.mark.release_only
def test_charness_doctor_can_surface_repo_onboarding_as_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(
        tmp_path, seeded_managed_home["home_root"], share_source_checkout=True
    )
    env["PATH"] = build_test_path()
    consumer_repo = tmp_path / "consumer-repo"
    consumer_repo.mkdir()
    (consumer_repo / "README.md").write_text("# Demo\n", encoding="utf-8")

    doctor_result = run_cli_path(
        CLI,
        "doctor",
        "--home-root",
        str(home_root),
        "--target-repo-root",
        str(consumer_repo),
        cwd=ROOT,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = yaml.safe_load(doctor_result.stdout)
    assert payload["repo_onboarding"]["status"] == "required"
    assert payload["next_action"]["kind"] == "repo-init"
    assert payload["next_action"]["source"] == "repo_onboarding"
    assert "setup" in payload["next_action"]["message"]
