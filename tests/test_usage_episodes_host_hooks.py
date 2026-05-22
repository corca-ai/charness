from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

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


def _write_adapter(repo: Path, body: str) -> Path:
    adapter = repo / ".agents" / "usage-episodes-adapter.yaml"
    adapter.write_text(body, encoding="utf-8")
    return adapter


def test_resolve_codex_target_defaults_to_toml(fake_home: Path) -> None:
    path, kind = lib.resolve_codex_target(fake_home)
    assert kind == "codex-toml"
    assert path == fake_home / ".codex" / "config.toml"


def test_resolve_codex_target_picks_hooks_json_when_present(fake_home: Path) -> None:
    hooks_json = fake_home / ".codex" / "hooks.json"
    hooks_json.parent.mkdir(parents=True)
    hooks_json.write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "^Bash$", "hooks": [{"type": "command", "command": "ls"}]}]}}), encoding="utf-8")
    path, kind = lib.resolve_codex_target(fake_home)
    assert kind == "codex-json"
    assert path == hooks_json


def test_resolve_codex_target_ignores_empty_hooks_json(fake_home: Path) -> None:
    hooks_json = fake_home / ".codex" / "hooks.json"
    hooks_json.parent.mkdir(parents=True)
    hooks_json.write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    _, kind = lib.resolve_codex_target(fake_home)
    assert kind == "codex-toml"


def test_install_claude_hook_creates_settings_and_records_state(fake_repo: Path, fake_home: Path) -> None:
    result = lib.install_claude_hook(fake_repo, home=fake_home)
    assert result["action"] == "installed"
    settings_path = Path(result["settings_path"])
    assert settings_path.is_file()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    entries = settings["hooks"]["SessionStart"]
    assert len(entries) == 1
    inner = entries[0]["hooks"]
    assert inner[0]["type"] == "command"
    assert inner[0]["command"].endswith("--host claude")
    state = lib.read_state(fake_repo)
    assert state["claude"]["kind"] == "claude-json"
    assert state["claude"]["command"] == inner[0]["command"]


def test_install_claude_hook_is_idempotent(fake_repo: Path, fake_home: Path) -> None:
    first = lib.install_claude_hook(fake_repo, home=fake_home)
    second = lib.install_claude_hook(fake_repo, home=fake_home)
    assert first["action"] == "installed"
    assert second["action"] == "noop"
    settings = json.loads(Path(first["settings_path"]).read_text(encoding="utf-8"))
    assert len(settings["hooks"]["SessionStart"]) == 1


def test_install_claude_preserves_foreign_hooks(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {"matcher": "startup", "hooks": [{"type": "command", "command": "/usr/local/bin/foreign-hook"}]}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    lib.install_claude_hook(fake_repo, home=fake_home)
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    commands = [
        entry["hooks"][0]["command"]
        for entry in settings["hooks"]["SessionStart"]
        if isinstance(entry.get("hooks"), list) and entry["hooks"]
    ]
    assert "/usr/local/bin/foreign-hook" in commands
    assert any("usage_episode_session_start.py" in cmd for cmd in commands)


def test_uninstall_claude_removes_only_charness_entry(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {"matcher": "startup", "hooks": [{"type": "command", "command": "/usr/local/bin/foreign-hook"}]}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    lib.install_claude_hook(fake_repo, home=fake_home)
    uninstall = lib.uninstall_claude_hook(fake_repo, home=fake_home)
    assert uninstall["action"] == "removed"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    remaining = [
        entry["hooks"][0]["command"]
        for entry in settings["hooks"]["SessionStart"]
    ]
    assert remaining == ["/usr/local/bin/foreign-hook"]
    state = lib.read_state(fake_repo)
    assert "claude" not in state


def test_install_codex_toml_writes_marker_block(fake_repo: Path, fake_home: Path) -> None:
    result = lib.install_codex_hook(fake_repo, home=fake_home)
    assert result["action"] == "installed"
    assert result["kind"] == "codex-toml"
    settings_path = Path(result["settings_path"])
    text = settings_path.read_text(encoding="utf-8")
    assert "# charness:usage-episodes" in text
    assert "[[hooks.SessionStart]]" in text
    assert "--host codex" in text


def test_install_codex_toml_is_idempotent(fake_repo: Path, fake_home: Path) -> None:
    first = lib.install_codex_hook(fake_repo, home=fake_home)
    second = lib.install_codex_hook(fake_repo, home=fake_home)
    assert first["action"] == "installed"
    assert second["action"] == "noop"
    text = Path(first["settings_path"]).read_text(encoding="utf-8")
    assert text.count(f"# {lib.CHARNESS_MARKER}") == 1


def test_install_codex_toml_appends_after_existing_content(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    existing = '[user]\nname = "alice"\n'
    settings_path.write_text(existing, encoding="utf-8")
    lib.install_codex_hook(fake_repo, home=fake_home)
    text = settings_path.read_text(encoding="utf-8")
    assert text.startswith(existing)
    assert "# charness:usage-episodes" in text


def test_uninstall_codex_toml_removes_only_marker_block(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_codex_config_toml_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        '[user]\nname = "alice"\n\n[[hooks.PreToolUse]]\nmatcher = "^Bash$"\n[[hooks.PreToolUse.hooks]]\ntype = "command"\ncommand = "echo other"\n',
        encoding="utf-8",
    )
    lib.install_codex_hook(fake_repo, home=fake_home)
    uninstall = lib.uninstall_codex_hook(fake_repo, home=fake_home)
    assert uninstall["action"] == "removed"
    text = settings_path.read_text(encoding="utf-8")
    assert "# charness:usage-episodes" not in text
    assert "echo other" in text
    state = lib.read_state(fake_repo)
    assert "codex" not in state


def test_install_codex_json_when_hooks_json_present(fake_repo: Path, fake_home: Path) -> None:
    hooks_json = fake_home / ".codex" / "hooks.json"
    hooks_json.parent.mkdir(parents=True)
    hooks_json.write_text(
        json.dumps({"hooks": {"PreToolUse": [{"matcher": "^Bash$", "hooks": [{"type": "command", "command": "echo bash"}]}]}}),
        encoding="utf-8",
    )
    result = lib.install_codex_hook(fake_repo, home=fake_home)
    assert result["kind"] == "codex-json"
    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    assert "SessionStart" in data["hooks"]
    assert any(
        item["command"].endswith("--host codex")
        for entry in data["hooks"]["SessionStart"]
        for item in entry["hooks"]
    )
    assert "echo bash" in json.dumps(data)


def test_reconcile_no_touch_when_host_hooks_disabled(fake_repo: Path, fake_home: Path) -> None:
    actions = lib.reconcile_host_hooks(fake_repo, adapter={"version": 1, "enabled": True}, home=fake_home)
    assert actions["claude"]["intent"] == "disabled"
    assert actions["codex"]["intent"] == "disabled"
    assert not lib.default_claude_settings_path(fake_home).exists()
    assert not lib.default_codex_config_toml_path(fake_home).exists()


def test_reconcile_installs_when_intent_enabled(fake_repo: Path, fake_home: Path) -> None:
    actions = lib.reconcile_host_hooks(
        fake_repo,
        adapter={"version": 1, "enabled": True, "host_hooks": {"claude": "enabled", "codex": "enabled"}},
        home=fake_home,
    )
    assert actions["claude"]["result"]["action"] == "installed"
    assert actions["codex"]["result"]["action"] == "installed"
    assert lib.default_claude_settings_path(fake_home).is_file()
    assert lib.default_codex_config_toml_path(fake_home).is_file()


def test_reconcile_uninstalls_when_intent_flipped(fake_repo: Path, fake_home: Path) -> None:
    lib.reconcile_host_hooks(
        fake_repo,
        adapter={"version": 1, "enabled": True, "host_hooks": {"claude": "enabled", "codex": "enabled"}},
        home=fake_home,
    )
    actions = lib.reconcile_host_hooks(
        fake_repo,
        adapter={"version": 1, "enabled": True, "host_hooks": {"claude": "disabled", "codex": "disabled"}},
        home=fake_home,
    )
    assert actions["claude"]["result"]["action"] == "removed"
    assert actions["codex"]["result"]["action"] == "removed"
    state = lib.read_state(fake_repo)
    assert "claude" not in state and "codex" not in state


def test_status_reports_drift_when_intent_enabled_but_actual_absent(fake_repo: Path, fake_home: Path) -> None:
    status = lib.session_capture_status(
        fake_repo,
        adapter={"version": 1, "enabled": True, "host_hooks": {"claude": "enabled"}},
        home=fake_home,
    )
    assert status["in_sync"] is False
    assert any("claude" in item for item in status["drift"])
    assert status["hosts"]["claude"]["in_sync"] is False
    assert status["hosts"]["codex"]["in_sync"] is True


def test_status_reports_drift_when_intent_disabled_but_actual_present(fake_repo: Path, fake_home: Path) -> None:
    lib.install_claude_hook(fake_repo, home=fake_home)
    status = lib.session_capture_status(
        fake_repo,
        adapter={"version": 1, "enabled": True},
        home=fake_home,
    )
    assert status["in_sync"] is False
    assert any("claude" in item for item in status["drift"])


def test_session_start_script_silent_when_disabled(fake_repo: Path, fake_home: Path) -> None:
    _write_adapter(fake_repo, "version: 1\nenabled: false\n")
    script = REPO_ROOT / "scripts" / "usage_episode_session_start.py"
    payload = {"hook_event_name": "SessionStart", "cwd": str(fake_repo), "model": "test"}
    result = subprocess.run(
        [sys.executable, str(script), "--host", "claude"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"CHARNESS_SESSION_START_DEBUG": "1", "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    assert not (fake_repo / ".charness" / "usage-episodes" / "sessions").exists()


def test_session_start_script_writes_session_when_enabled(fake_repo: Path, fake_home: Path) -> None:
    _write_adapter(fake_repo, "version: 1\nenabled: true\n")
    script = REPO_ROOT / "scripts" / "usage_episode_session_start.py"
    payload = {"hook_event_name": "SessionStart", "cwd": str(fake_repo), "model": "test-model"}
    result = subprocess.run(
        [sys.executable, str(script), "--host", "codex"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    sessions_dir = fake_repo / ".charness" / "usage-episodes" / "sessions"
    assert sessions_dir.is_dir()
    pointer = sessions_dir / "current"
    assert pointer.is_file()
    session_id = pointer.read_text(encoding="utf-8").strip()
    start_record = sessions_dir / session_id / "start.json"
    assert start_record.is_file()
    record = json.loads(start_record.read_text(encoding="utf-8"))
    assert record["session_id"] == session_id
    assert record["host"] == "codex"
    assert record["model"] == "test-model"
    assert "transcript_path" not in record
    assert "last_assistant_message" not in record


def test_session_start_script_no_adapter_exits_silent(fake_repo: Path) -> None:
    script = REPO_ROOT / "scripts" / "usage_episode_session_start.py"
    payload = {"hook_event_name": "SessionStart", "cwd": str(fake_repo), "model": "test"}
    result = subprocess.run(
        [sys.executable, str(script), "--host", "claude"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    assert not (fake_repo / ".charness").exists()


def test_session_capture_cli_install_and_uninstall_round_trip(fake_home: Path) -> None:
    cli = REPO_ROOT / "charness"
    install = subprocess.run(
        [sys.executable, str(cli), "session-capture", "install", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr
    install_payload = json.loads(install.stdout)
    assert install_payload["mode"] == "install"
    claude_settings = fake_home / ".claude" / "settings.json"
    codex_settings = fake_home / ".codex" / "config.toml"
    assert claude_settings.is_file()
    assert codex_settings.is_file()
    status = subprocess.run(
        [sys.executable, str(cli), "session-capture", "status", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT), "--json"],
        capture_output=True,
        text=True,
    )
    status_payload = json.loads(status.stdout)
    assert status_payload["hosts"]["claude"]["actual"]["present"] is True
    assert status_payload["hosts"]["codex"]["actual"]["present"] is True
    uninstall = subprocess.run(
        [sys.executable, str(cli), "session-capture", "uninstall", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
    )
    assert uninstall.returncode == 0, uninstall.stderr
    text = codex_settings.read_text(encoding="utf-8") if codex_settings.is_file() else ""
    assert lib.CHARNESS_MARKER not in text
    if claude_settings.is_file():
        settings = json.loads(claude_settings.read_text(encoding="utf-8"))
        assert "hooks" not in settings or "SessionStart" not in settings.get("hooks", {})


def test_session_capture_cli_status_exit_codes(fake_home: Path) -> None:
    cli = REPO_ROOT / "charness"
    in_sync = subprocess.run(
        [sys.executable, str(cli), "session-capture", "status", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT), "--json"],
        capture_output=True,
        text=True,
    )
    assert in_sync.returncode == 0
    subprocess.run(
        [sys.executable, str(cli), "session-capture", "install", "--host", "claude", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        check=True,
    )
    drift = subprocess.run(
        [sys.executable, str(cli), "session-capture", "status", "--home-root", str(fake_home), "--repo-root", str(REPO_ROOT), "--json"],
        capture_output=True,
        text=True,
    )
    assert drift.returncode == 1
    drift_payload = json.loads(drift.stdout)
    assert drift_payload["in_sync"] is False


def test_reconcile_runner_status_mode_exit_codes(fake_repo: Path, fake_home: Path) -> None:
    _write_adapter(fake_repo, "version: 1\nenabled: true\nhost_hooks:\n  claude: enabled\n")
    runner = REPO_ROOT / "scripts" / "reconcile_usage_episodes_host_hooks.py"
    result = subprocess.run(
        [sys.executable, str(runner), "--repo-root", str(fake_repo), "--home", str(fake_home), "--mode", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["in_sync"] is False

    lib.install_claude_hook(fake_repo, home=fake_home)
    result = subprocess.run(
        [sys.executable, str(runner), "--repo-root", str(fake_repo), "--home", str(fake_home), "--mode", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["in_sync"] is True
