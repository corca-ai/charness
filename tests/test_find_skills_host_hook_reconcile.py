from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import host_hook_codex_toml_lib as toml  # noqa: E402
import host_hook_find_skills as fs  # noqa: E402
import host_hook_install_lib as lib  # noqa: E402


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".agents").mkdir()
    (repo / "scripts").mkdir()
    return repo


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    return home


def test_find_skills_codex_reconcile_removes_legacy_duplicate_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = fs._command(fake_repo, "codex")
    settings_path.write_text(
        "\n".join(
            [
                "# charness:find-skills session-start routing trigger (#240)",
                "[[hooks.SessionStart]]",
                'matcher = "startup|resume|clear"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
                "# charness:find-skills-routing",
                "[[hooks.SessionStart]]",
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    adapter = {"version": 1, "enabled": True, "find_skills_routing": {"codex": "enabled"}}
    actions = lib.reconcile_host_hooks(fake_repo, adapter=adapter, home=fake_home)
    result = actions["find_skills_routing"]["codex"]["result"]
    assert result["action"] == "updated"
    assert result["legacy_cleanup"][0]["action"] == "removed"
    text = settings_path.read_text(encoding="utf-8")
    assert "find-skills session-start routing trigger (#240)" not in text
    assert text.count("# charness:find-skills-routing") == 1
    assert text.count("[[hooks.SessionStart]]") == 1
    assert text.count("session_start_find_skills.py") == 1
    assert 'matcher = "startup|resume|clear"' in text


def test_find_skills_codex_reconcile_migrates_legacy_only_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = fs._command(fake_repo, "codex")
    settings_path.write_text(
        "\n".join(
            [
                "# charness:find-skills session-start routing trigger (#240)",
                "[[hooks.SessionStart]]",
                'matcher = "startup|resume|clear"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    adapter = {"version": 1, "enabled": True, "find_skills_routing": {"codex": "enabled"}}
    result = lib.reconcile_host_hooks(fake_repo, adapter=adapter, home=fake_home)["find_skills_routing"]["codex"]["result"]
    assert result["action"] == "installed"
    assert result["legacy_cleanup"][0]["action"] == "removed"
    text = settings_path.read_text(encoding="utf-8")
    assert "find-skills session-start routing trigger (#240)" not in text
    assert text.count("# charness:find-skills-routing") == 1
    assert text.count("[[hooks.SessionStart]]") == 1
    assert 'matcher = "startup|resume|clear"' in text


def test_find_skills_codex_update_preserves_following_foreign_sessionstart(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = fs._command(fake_repo, "codex")
    settings_path.write_text(
        "\n".join(
            [
                "# charness:find-skills-routing",
                "[[hooks.SessionStart]]",
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
                "[[hooks.SessionStart]]",
                'matcher = "startup"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                'command = "python3 /opt/foreign/session_start.py"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = fs.install_find_skills_codex_hook(fake_repo, home=fake_home)
    assert result["action"] == "updated"
    text = settings_path.read_text(encoding="utf-8")
    assert text.count("[[hooks.SessionStart]]") == 2
    assert text.count("session_start_find_skills.py") == 1
    assert 'command = "python3 /opt/foreign/session_start.py"' in text
    assert 'matcher = "startup|resume|clear"' in text


def test_find_skills_codex_disabled_removes_legacy_only_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = fs._command(fake_repo, "codex")
    settings_path.write_text(
        "\n".join(
            [
                "# charness:find-skills session-start routing trigger (#240)",
                "[[hooks.SessionStart]]",
                'matcher = "startup|resume|clear"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    status = lib.find_skills_routing_status(fake_repo, adapter={"version": 1}, home=fake_home)
    assert status["in_sync"] is False
    assert "legacy_toml_markers_present" in status["hosts"]["codex"]["actual"]
    actions = lib.reconcile_host_hooks(fake_repo, adapter={"version": 1}, home=fake_home)
    result = actions["find_skills_routing"]["codex"]["result"]
    assert result["legacy_cleanup"][0]["action"] == "removed"
    assert "session_start_find_skills.py" not in settings_path.read_text(encoding="utf-8")


def test_find_skills_codex_json_install_removes_toml_owned_blocks(fake_repo: Path, fake_home: Path) -> None:
    hooks_json = lib.default_codex_hooks_json_path(fake_home)
    hooks_json.parent.mkdir(parents=True)
    hooks_json.write_text(
        json.dumps({"hooks": {"PreToolUse": [{"matcher": "^Bash$", "hooks": [{"type": "command", "command": "echo bash"}]}]}}),
        encoding="utf-8",
    )
    config_toml = lib.default_codex_config_toml_path(fake_home)
    command = fs._command(fake_repo, "codex")
    config_toml.write_text(
        "\n".join(
            [
                "# charness:find-skills-routing",
                "[[hooks.SessionStart]]",
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
                "# charness:find-skills session-start routing trigger (#240)",
                "[[hooks.SessionStart]]",
                'matcher = "startup|resume|clear"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = fs.install_find_skills_codex_hook(fake_repo, home=fake_home)
    assert result["kind"] == "codex-json"
    assert result["legacy_cleanup"]
    assert "session_start_find_skills.py" not in config_toml.read_text(encoding="utf-8")
    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    assert data["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "echo bash"
    session_start = data["hooks"]["SessionStart"]
    assert len(session_start) == 1
    assert session_start[0]["matcher"] == "startup|resume|clear"


def test_codex_toml_matching_existing_command_returns_none_for_foreign_command(fake_repo: Path) -> None:
    command = fs._command(fake_repo, "codex")

    assert toml._matching_existing_command('command = "python3 /opt/foreign/session_start.py"', command) is None


def test_find_skills_codex_json_uninstall_cleans_legacy_toml_markers(fake_repo: Path, fake_home: Path) -> None:
    hooks_json = lib.default_codex_hooks_json_path(fake_home)
    hooks_json.parent.mkdir(parents=True)
    command = fs._command(fake_repo, "codex")
    hooks_json.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "startup|resume|clear",
                            "hooks": [{"type": "command", "command": command}],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    config_toml = lib.default_codex_config_toml_path(fake_home)
    config_toml.write_text(
        "\n".join(
            [
                "# charness:find-skills session-start routing trigger (#240)",
                "[[hooks.SessionStart]]",
                'matcher = "startup|resume|clear"',
                "[[hooks.SessionStart.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = fs.uninstall_find_skills_codex_hook(fake_repo, home=fake_home)

    assert result["kind"] == "codex-json"
    assert result["action"] == "removed"
    assert result["legacy_cleanup"][0]["action"] == "removed"
    assert "find-skills session-start routing trigger (#240)" not in config_toml.read_text(encoding="utf-8")
