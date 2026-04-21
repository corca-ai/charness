from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .support import (
    CLI,
    ROOT,
    build_test_path,
    clone_seeded_managed_home,
    make_fake_claude,
    run_cli,
)


def test_charness_doctor_selects_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["next_action"]["kind"] == "restart"
    assert payload["next_action"]["host"] == "claude"
    assert payload["next_action"]["message"] == payload["claude_host_guidance"]["message"]


def test_charness_doctor_prints_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    doctor_result = run_cli("doctor", "--home-root", str(home_root), env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    assert (
        "NEXT_ACTION: claude: Claude host install markers are present. Restart Claude Code to load or refresh charness."
        in doctor_result.stdout
    )


def test_charness_doctor_next_action_reports_missing_source(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True, exist_ok=True)
    installed_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    installed_cli.chmod(0o755)

    doctor_result = subprocess.run(
        [sys.executable, str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["next_action"]["kind"] == "manual"
    assert payload["next_action"]["host"] == "claude"
    assert payload["next_action"]["message"] == payload["claude_host_guidance"]["message"]


def test_charness_doctor_can_surface_repo_onboarding_as_primary_next_action(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    env["PATH"] = build_test_path()
    consumer_repo = tmp_path / "consumer-repo"
    consumer_repo.mkdir()
    (consumer_repo / "README.md").write_text("# Demo\n", encoding="utf-8")

    doctor_result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "doctor",
            "--home-root",
            str(home_root),
            "--json",
            "--target-repo-root",
            str(consumer_repo),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["repo_onboarding"]["status"] == "required"
    assert payload["next_action"]["kind"] == "repo-init"
    assert payload["next_action"]["source"] == "repo_onboarding"
    assert "init-repo" in payload["next_action"]["message"]
