"""Edit-time #N-anchor guard: adapter-gated PostToolUse hook + guard script.

The firing mechanism is host-specific and adapter-declared
(`skill_anchor_edit_guard` in the usage-episodes adapter, claude-only); the
scan stays the repo-owned single source. The guard is additive and fail-open:
the commit-time validate_skill_ergonomics sweep stays the backstop, and a repo
or machine without the adapter intent inherits no hook at all.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import host_hook_install_lib as lib
import host_hook_skill_anchor_guard as guard
import pytest

from scripts.post_edit_skill_anchor_guard import main as guard_main


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir()
    return repo


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    return home


def _claude_settings(home: Path) -> dict:
    return json.loads(lib.default_claude_settings_path(home).read_text(encoding="utf-8"))


def test_install_adds_post_tool_use_entry_and_records_state(fake_repo: Path, fake_home: Path) -> None:
    result = guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    assert result["action"] == "installed"
    assert result["event"] == "PostToolUse"
    settings = _claude_settings(fake_home)
    entries = settings["hooks"]["PostToolUse"]
    assert len(entries) == 1
    assert entries[0]["matcher"] == guard.GUARD_MATCHER
    assert "post_edit_skill_anchor_guard.py" in entries[0]["hooks"][0]["command"]
    state = lib.read_state(fake_repo)
    assert "claude:skill_anchor_edit_guard" in state


def test_install_does_not_touch_session_start_entries(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "foreign"}]}]}}),
        encoding="utf-8",
    )

    guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    settings = _claude_settings(fake_home)
    assert len(settings["hooks"]["SessionStart"]) == 1
    assert settings["hooks"]["SessionStart"][0]["hooks"][0]["command"] == "foreign"
    assert len(settings["hooks"]["PostToolUse"]) == 1


def test_uninstall_removes_entry_and_state(fake_repo: Path, fake_home: Path) -> None:
    guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    result = guard.uninstall_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    assert result["action"] == "removed"
    settings = _claude_settings(fake_home)
    assert "PostToolUse" not in settings.get("hooks", {})
    assert "claude:skill_anchor_edit_guard" not in lib.read_state(fake_repo)


def test_reconcile_honors_intent_and_reports_codex_unsupported(fake_repo: Path, fake_home: Path) -> None:
    enabled = {"skill_anchor_edit_guard": {"claude": "enabled"}}
    actions = guard.reconcile_skill_anchor_guard_hooks(fake_repo, adapter=enabled, home=fake_home)
    assert actions["claude"]["result"]["action"] == "installed"
    assert actions["codex"]["intent"] == "disabled"
    assert actions["codex"]["result"]["action"] == "noop"

    actions = guard.reconcile_skill_anchor_guard_hooks(fake_repo, adapter={}, home=fake_home)
    assert actions["claude"]["result"]["action"] in {"removed", "absent", "not_installed"}

    misdeclared = {"skill_anchor_edit_guard": {"claude": "enabled", "codex": "enabled"}}
    actions = guard.reconcile_skill_anchor_guard_hooks(fake_repo, adapter=misdeclared, home=fake_home)
    assert "error" in actions["codex"]


def test_reconcile_host_hooks_carries_anchor_guard_section(fake_repo: Path, fake_home: Path) -> None:
    adapter = {"skill_anchor_edit_guard": {"claude": "enabled"}}
    actions = lib.reconcile_host_hooks(fake_repo, adapter=adapter, home=fake_home)
    assert actions["skill_anchor_edit_guard"]["claude"]["result"]["action"] == "installed"


def test_status_reports_drift_when_enabled_but_absent(fake_repo: Path, fake_home: Path) -> None:
    adapter = {"skill_anchor_edit_guard": {"claude": "enabled"}}
    status = guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)
    assert status["in_sync"] is False

    guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)
    status = guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)
    assert status["in_sync"] is True


def _payload(file_path: str) -> io.StringIO:
    return io.StringIO(json.dumps({"tool_name": "Edit", "tool_input": {"file_path": file_path}}))


def _seed_skill_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "skill-repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo\n\nsee #123 for the recurring trap\n", encoding="utf-8")
    (skill_dir / "CLEAN.md").write_text("# Demo\n\nno anchors here\n", encoding="utf-8")
    return repo


def test_guard_flags_disallowed_anchor_in_edited_skill_file(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    repo = _seed_skill_repo(tmp_path)
    target = repo / "skills" / "public" / "demo" / "SKILL.md"

    code = guard_main(["--repo-root", str(repo)], stdin=_payload(str(target)))

    assert code == 2
    err = capsys.readouterr().err
    assert "skill-issue-anchor-scan: blocked" in err
    assert "SKILL.md:3" in err


def test_guard_passes_clean_skill_file(tmp_path: Path) -> None:
    repo = _seed_skill_repo(tmp_path)
    target = repo / "skills" / "public" / "demo" / "CLEAN.md"

    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(target))) == 0


def test_guard_fail_open_paths(tmp_path: Path) -> None:
    repo = _seed_skill_repo(tmp_path)

    # non-skill file, outside-repo file, missing file, bad payloads: all silent
    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(tmp_path / "other.md"))) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=_payload("README.md")) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(repo / "skills/public/demo/GONE.md"))) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=io.StringIO("not json")) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=io.StringIO("")) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=io.StringIO(json.dumps({"tool_input": {}}))) == 0
