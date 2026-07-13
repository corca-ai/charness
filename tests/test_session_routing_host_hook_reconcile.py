from __future__ import annotations

import json
from pathlib import Path

import host_hook_codex_toml_lib as toml
import host_hook_install_lib as lib
import host_hook_session_routing as routing
import pytest


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


def test_session_routing_prefers_canonical_intent_section() -> None:
    assert routing._routing_intent({"session_routing": {"codex": "enabled"}}, "codex") == "enabled"


@pytest.mark.parametrize("host", ["claude", "codex"])
@pytest.mark.parametrize("operation", ["install", "uninstall"])
def test_session_routing_reconcile_removes_retired_state_only_entry(
    fake_repo: Path,
    fake_home: Path,
    host: str,
    operation: str,
) -> None:
    other_host = "codex" if host == "claude" else "claude"
    other_canonical_key = routing._state_key(other_host)
    other_canonical = {"sentinel": "canonical-survives"}
    foreign_state = {"sentinel": "foreign-survives"}
    lib.write_state(
        fake_repo,
        {
            "schema_version": lib.STATE_SCHEMA_VERSION,
            routing._retired_state_key(host): {"sentinel": "delete-only"},
            other_canonical_key: other_canonical,
            "foreign:state": foreign_state,
        },
    )

    reconcile = getattr(routing, f"{operation}_session_routing_{host}_hook")
    result = reconcile(fake_repo, home=fake_home)

    cleanup = result["retired_state_cleanup"]
    assert any(
        item == {
            "action": "removed",
            "kind": "retired-state-ledger-entry",
            "state_key": routing._retired_state_key(host),
        }
        for item in cleanup
    )
    state = lib.read_state(fake_repo)
    assert routing._retired_state_key(host) not in state
    assert state[other_canonical_key] == other_canonical
    assert state["foreign:state"] == foreign_state
    if operation == "install":
        assert routing._state_key(host) in state


def test_session_routing_claude_install_reports_retired_state_cleanup(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    retired_command = routing._retired_command(fake_repo, "claude")
    settings_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": retired_command}]}]}}),
        encoding="utf-8",
    )

    result = routing.install_session_routing_claude_hook(fake_repo, home=fake_home)

    assert result["retired_state_cleanup"][0]["action"] == "removed"
    entries = json.loads(settings_path.read_text(encoding="utf-8"))["hooks"]["SessionStart"]
    assert entries[0]["hooks"][0]["command"] == routing._command(fake_repo, "claude")


def test_session_routing_claude_uninstall_reports_retired_state_cleanup(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    current_command = routing._command(fake_repo, "claude")
    retired_command = routing._retired_command(fake_repo, "claude")
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {"hooks": [{"type": "command", "command": current_command}]},
                        {"hooks": [{"type": "command", "command": retired_command}]},
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    result = routing.uninstall_session_routing_claude_hook(fake_repo, home=fake_home)

    assert result["action"] == "removed"
    assert result["retired_state_cleanup"][0]["action"] == "removed"
    assert "hooks" not in json.loads(settings_path.read_text(encoding="utf-8"))


def test_session_routing_codex_reconcile_removes_retired_duplicate_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = routing._retired_command(fake_repo, "codex")
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
    adapter = {"version": 1, "enabled": True, "session_routing": {"codex": "enabled"}}
    actions = lib.reconcile_host_hooks(fake_repo, adapter=adapter, home=fake_home)
    result = actions["session_routing"]["codex"]["result"]
    assert result["action"] in {"installed", "updated"}
    assert result["retired_state_cleanup"][0]["action"] == "removed"
    text = settings_path.read_text(encoding="utf-8")
    assert "find-skills session-start routing trigger (#240)" not in text
    assert text.count("# charness:session-routing") == 1
    assert text.count("[[hooks.SessionStart]]") == 1
    assert text.count("session_start_routing.py") == 1
    assert 'matcher = "startup|resume|clear"' in text


def test_session_routing_codex_reconcile_replaces_retired_only_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = routing._retired_command(fake_repo, "codex")
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
    adapter = {"version": 1, "enabled": True, "session_routing": {"codex": "enabled"}}
    result = lib.reconcile_host_hooks(fake_repo, adapter=adapter, home=fake_home)["session_routing"]["codex"]["result"]
    assert result["action"] == "installed"
    assert result["retired_state_cleanup"][0]["action"] == "removed"
    text = settings_path.read_text(encoding="utf-8")
    assert "find-skills session-start routing trigger (#240)" not in text
    assert text.count("# charness:session-routing") == 1
    assert text.count("[[hooks.SessionStart]]") == 1
    assert 'matcher = "startup|resume|clear"' in text


def test_session_routing_codex_update_preserves_following_foreign_sessionstart(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = routing._command(fake_repo, "codex")
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
    result = routing.install_session_routing_codex_hook(fake_repo, home=fake_home)
    assert result["action"] in {"installed", "updated"}
    text = settings_path.read_text(encoding="utf-8")
    assert text.count("[[hooks.SessionStart]]") == 2
    assert text.count("session_start_routing.py") == 1
    assert 'command = "python3 /opt/foreign/session_start.py"' in text
    assert 'matcher = "startup|resume|clear"' in text


def test_session_routing_codex_disabled_removes_retired_only_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    command = routing._command(fake_repo, "codex")
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
    status = lib.session_routing_status(fake_repo, adapter={"version": 1}, home=fake_home)
    assert status["in_sync"] is False
    assert "retired_toml_markers_present" in status["hosts"]["codex"]["actual"]
    actions = lib.reconcile_host_hooks(fake_repo, adapter={"version": 1}, home=fake_home)
    result = actions["session_routing"]["codex"]["result"]
    assert result["retired_state_cleanup"][0]["action"] == "removed"
    assert "session_start_find_skills.py" not in settings_path.read_text(encoding="utf-8")


def test_session_routing_codex_json_install_removes_retired_toml_owned_blocks(fake_repo: Path, fake_home: Path) -> None:
    hooks_json = lib.default_codex_hooks_json_path(fake_home)
    hooks_json.parent.mkdir(parents=True)
    retired_command = routing._retired_command(fake_repo, "codex")
    hooks_json.write_text(
        json.dumps({"hooks": {
            "PreToolUse": [{"matcher": "^Bash$", "hooks": [{"type": "command", "command": "echo bash"}]}],
            "SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": retired_command}]}],
        }}),
        encoding="utf-8",
    )
    config_toml = lib.default_codex_config_toml_path(fake_home)
    command = routing._command(fake_repo, "codex")
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
    result = routing.install_session_routing_codex_hook(fake_repo, home=fake_home)
    assert result["kind"] == "codex-json"
    assert result["retired_state_cleanup"]
    assert "session_start_find_skills.py" not in config_toml.read_text(encoding="utf-8")
    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    assert data["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "echo bash"
    session_start = data["hooks"]["SessionStart"]
    assert len(session_start) == 1
    assert session_start[0]["matcher"] == "startup|resume|clear"


def test_codex_toml_matching_existing_command_returns_none_for_foreign_command(fake_repo: Path) -> None:
    command = routing._command(fake_repo, "codex")

    assert toml._matching_existing_command('command = "python3 /opt/foreign/session_start.py"', command) is None


def test_session_routing_codex_json_uninstall_cleans_retired_toml_markers(fake_repo: Path, fake_home: Path) -> None:
    hooks_json = lib.default_codex_hooks_json_path(fake_home)
    hooks_json.parent.mkdir(parents=True)
    command = routing._command(fake_repo, "codex")
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

    result = routing.uninstall_session_routing_codex_hook(fake_repo, home=fake_home)

    assert result["kind"] == "codex-json"
    assert result["action"] == "removed"
    assert result["retired_state_cleanup"][0]["action"] == "removed"
    assert "find-skills session-start routing trigger (#240)" not in config_toml.read_text(encoding="utf-8")
