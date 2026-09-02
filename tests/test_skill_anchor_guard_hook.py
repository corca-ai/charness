"""Edit-time #N-anchor guard: adapter-gated PostToolUse hook + guard script.

The firing mechanism is host-specific and adapter-declared
(`skill_anchor_edit_guard` in a host-hook adapter, claude-only); the
scan stays the repo-owned single source. The guard is additive and fail-open:
the commit-time validate_skill_ergonomics sweep stays the backstop, and a repo
or machine without the adapter intent inherits no hook at all.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import host_hook_install_lib as lib
import host_hook_skill_anchor_guard as guard
import pytest

import scripts.gates_support.skill_issue_anchor_scan as anchor_scan
from scripts.post_edit_skill_anchor_guard import main as guard_main

ROOT = Path(__file__).resolve().parents[1]


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


def test_install_does_not_touch_foreign_post_tool_use_entries(fake_repo: Path, fake_home: Path) -> None:
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps({"hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "foreign"}]}]}}),
        encoding="utf-8",
    )

    guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    settings = _claude_settings(fake_home)
    entries = settings["hooks"]["PostToolUse"]
    assert len(entries) == 2
    assert entries[0]["hooks"][0]["command"] == "foreign"


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


def test_reconcile_surfaces_host_hook_error(fake_repo: Path, fake_home: Path) -> None:
    # A corrupt settings file raises HostHookError; reconcile reports it per
    # host instead of aborting the chain.
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text("not json", encoding="utf-8")

    actions = guard.reconcile_skill_anchor_guard_hooks(
        fake_repo, adapter={"skill_anchor_edit_guard": {"claude": "enabled"}}, home=fake_home
    )

    assert "error" in actions["claude"]
    assert "result" not in actions["claude"]


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


def _write_guard_entry_with_matcher(fake_repo: Path, fake_home: Path, matcher: str) -> Path:
    """Seed a PostToolUse entry carrying the expected guard command but a
    drifted matcher, i.e. a hook that can never see an Edit/Write."""
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    command = guard._command(fake_repo, "claude")
    settings_path.write_text(
        json.dumps({"hooks": {guard.GUARD_EVENT: [{"matcher": matcher, "hooks": [{"type": "command", "command": command}]}]}}),
        encoding="utf-8",
    )
    return settings_path


def test_status_reports_drift_when_matcher_cannot_fire(fake_repo: Path, fake_home: Path) -> None:
    """A guard entry under a non-edit matcher is inert; status must not call it healthy."""
    _write_guard_entry_with_matcher(fake_repo, fake_home, "Bash")
    adapter = {"skill_anchor_edit_guard": {"claude": "enabled"}}

    status = guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)

    assert status["hosts"]["claude"]["actual"]["present"] is False
    assert status["in_sync"] is False


def test_reconcile_repairs_drifted_matcher_in_place(fake_repo: Path, fake_home: Path) -> None:
    settings_path = _write_guard_entry_with_matcher(fake_repo, fake_home, "Bash")
    adapter = {"skill_anchor_edit_guard": {"claude": "enabled"}}

    result = guard.reconcile_skill_anchor_guard_hooks(fake_repo, adapter=adapter, home=fake_home)["claude"]["result"]

    assert result["action"] == "installed"
    assert result["repaired_matcher"] is True
    entries = json.loads(settings_path.read_text(encoding="utf-8"))["hooks"][guard.GUARD_EVENT]
    assert len(entries) == 1
    assert entries[0]["matcher"] == guard.GUARD_MATCHER
    assert guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)["in_sync"] is True


def test_install_is_noop_when_matcher_already_correct(fake_repo: Path, fake_home: Path) -> None:
    _write_guard_entry_with_matcher(fake_repo, fake_home, guard.GUARD_MATCHER)

    result = guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    assert result["action"] == "noop"
    assert result["repaired_matcher"] is False


@pytest.mark.parametrize(
    "matcher",
    ["Edit|Write|MultiEdit|NotebookEdit", "Write|Edit|MultiEdit", "", None, "*", ".*", "Edit.*|Write|MultiEdit"],
    ids=["widened", "reordered", "empty-matches-all", "absent-matches-all", "star", "regex-any", "regex-prefix"],
)
def test_a_matcher_that_still_fires_is_present_and_is_never_rewritten(
    fake_repo: Path, fake_home: Path, matcher: str | None
) -> None:
    """Matcher identity is COVERAGE, not string equality.

    The first cut of the matcher fix used `entry["matcher"] != expected`, which
    reported an operator-widened matcher absent (it fires for every guard event)
    and then "repaired" it back to the charness string — deleting the operator's
    extra NotebookEdit coverage. A verdict that calls a live hook missing, and a
    repair that silently narrows real coverage, are both worse than the drift.

    The second cut read the matcher as a literal `|`-separated set, which put every
    REGEX spelling (`*`, `.*`, `Edit.*|...`) back in the same trap: a live catch-all
    classified inert and rewritten. A matcher we cannot bound is left alone.
    """
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    command = guard._command(fake_repo, "claude")
    entry: dict[str, object] = {"hooks": [{"type": "command", "command": command}]}
    if matcher is not None:
        entry["matcher"] = matcher
    settings_path.write_text(json.dumps({"hooks": {guard.GUARD_EVENT: [entry]}}), encoding="utf-8")
    adapter = {"skill_anchor_edit_guard": {"claude": "enabled"}}

    status = guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)
    assert status["hosts"]["claude"]["actual"]["present"] is True
    assert status["in_sync"] is True

    result = guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)
    assert result["action"] == "noop"
    assert result["repaired_matcher"] is False
    assert json.loads(settings_path.read_text(encoding="utf-8"))["hooks"][guard.GUARD_EVENT] == [entry]


def test_install_refuses_to_rewrite_a_matcher_shared_with_a_foreign_command(
    fake_repo: Path, fake_home: Path
) -> None:
    """A settings entry groups several commands under ONE matcher — that is the shape
    the host's own hooks UI produces — so the matcher is shared state. Repairing it
    would change when the operator's unrelated hook fires, which this installer's
    own contract forbids. Refuse and name the entry instead.
    """
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    command = guard._command(fake_repo, "claude")
    shared = {
        "matcher": "Bash",
        "hooks": [
            {"type": "command", "command": "/home/op/my-own-hook.sh"},
            {"type": "command", "command": command},
        ],
    }
    settings_path.write_text(json.dumps({"hooks": {guard.GUARD_EVENT: [shared]}}), encoding="utf-8")

    with pytest.raises(lib.HostHookError) as excinfo:
        guard.install_skill_anchor_guard_claude_hook(fake_repo, home=fake_home)

    assert "non-charness command" in str(excinfo.value)
    # ...and the operator's file is untouched by the refusal.
    assert json.loads(settings_path.read_text(encoding="utf-8"))["hooks"][guard.GUARD_EVENT] == [shared]


def test_an_unreadable_settings_file_is_drift_for_a_disabled_intent(
    fake_repo: Path, fake_home: Path
) -> None:
    """`present: False` over a file nobody could parse agrees with a disabled intent
    by accident. That agreement is a verdict rendered over an unread scope, and it is
    the direction no other assertion covers: for an ENABLED intent the same False
    already fails closed.
    """
    settings_path = lib.default_claude_settings_path(fake_home)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text('{"hooks": {"PostToolUse": [},}', encoding="utf-8")  # trailing comma
    adapter = {"skill_anchor_edit_guard": {"claude": "disabled"}}

    status = guard.skill_anchor_guard_status(fake_repo, adapter=adapter, home=fake_home)

    assert status["hosts"]["claude"]["actual"]["settings_readable"] is False
    assert status["in_sync"] is False
    assert any("unreadable" in line for line in status["drift"])


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
    assert guard_main(["--repo-root", str(repo)], stdin=io.StringIO("[]")) == 0
    assert guard_main(["--repo-root", str(repo)], stdin=io.StringIO(json.dumps({"tool_input": {}}))) == 0


def test_guard_reports_unestablished_when_rule_library_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    # A bundle whose skill_text_quality_lib rule library is absent cannot render
    # any anchor verdict. The guard must not exit 0 like a clean scan: it stays
    # non-blocking (exit 1, not 2) but names the unestablished scope on stderr.
    repo = _seed_skill_repo(tmp_path)
    monkeypatch.setattr(anchor_scan, "LIB_ROOT", tmp_path / "bundle-without-rule-library")

    dirty = repo / "skills" / "public" / "demo" / "SKILL.md"
    clean = repo / "skills" / "public" / "demo" / "CLEAN.md"
    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(dirty))) == 1
    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(clean))) == 1

    err = capsys.readouterr().err
    assert "unestablished" in err
    assert "skill_text_quality_lib" in err


def test_guard_still_scans_when_rule_library_is_present(tmp_path: Path) -> None:
    # Discriminating control for the test above: same files, real rule library.
    repo = _seed_skill_repo(tmp_path)
    dirty = repo / "skills" / "public" / "demo" / "SKILL.md"
    clean = repo / "skills" / "public" / "demo" / "CLEAN.md"

    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(dirty))) == 2
    assert guard_main(["--repo-root", str(repo)], stdin=_payload(str(clean))) == 0


@pytest.mark.boundary_contract(
    reason="the post-edit guard's exact exit code and stderr are the hook contract"
)
def test_guard_process_contract_exit_codes(tmp_path: Path) -> None:
    # The host invokes the guard as a subprocess with the hook payload on
    # stdin and branches on exit 0 (silent) vs 2 (surface findings) — that IS
    # the contract, so one boundary-level proof runs the real process
    # (ratchet-exempted); all logic tests above stay in-process.
    repo = _seed_skill_repo(tmp_path)
    target = repo / "skills" / "public" / "demo" / "SKILL.md"

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "post_edit_skill_anchor_guard.py"), "--repo-root", str(repo)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(target)}}),
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 2
    assert "skill-issue-anchor-scan: blocked" in proc.stderr
