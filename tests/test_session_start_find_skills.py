from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import session_start_find_skills as hook  # noqa: E402

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_find_skills.py"
CLAUDE_SETTINGS = REPO_ROOT / ".claude" / "settings.json"
CODEX_CONFIG = REPO_ROOT / ".codex" / "config.toml"


def test_directive_is_dumb_and_points_at_find_skills() -> None:
    """The directive triggers find-skills and defers routing to that skill."""
    directive = hook.build_additional_context()
    # Triggers find-skills.
    assert "charness:find-skills" in directive
    # Names the pickup -> handoff example without re-encoding routing rules.
    assert "charness:handoff" in directive
    assert "pickup" in directive
    # Stays dumb: the routing decision lives in the skill, not the hook text.
    assert "routing decision lives in that skill" in directive


def test_render_output_claude_emits_session_start_additional_context() -> None:
    payload = json.loads(hook.render_output("claude"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness:find-skills" in inner["additionalContext"]


def test_render_output_codex_emits_session_start_additional_context() -> None:
    # Codex confirmed 2026-05-29 to support hookSpecificOutput.additionalContext.
    payload = json.loads(hook.render_output("codex"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness:find-skills" in inner["additionalContext"]


def test_render_output_unknown_emits_plain_directive() -> None:
    out = hook.render_output("unknown")
    # Plain text fallback, not the structured JSON wrapper.
    assert "hookSpecificOutput" not in out
    assert "charness:find-skills" in out


def test_hook_runs_end_to_end_and_injects_directive() -> None:
    """Simulate the host firing the hook: SessionStart payload on stdin."""
    payload = json.dumps(
        {
            "hook_event_name": "SessionStart",
            "source": "startup",
            "cwd": str(REPO_ROOT),
            "session_id": "test",
        }
    )
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    assert emitted["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "charness:find-skills" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_is_silent_failing_on_garbage_stdin() -> None:
    """A hook script error must never break the host session (exit 0)."""
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input="not json at all {{{",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    # Still emits the directive even when the stdin payload is unparseable.
    assert "charness:find-skills" in result.stdout


def test_repo_claude_settings_wires_session_start_hook() -> None:
    """Slice-2 acceptance: the hook is visible in the repo's .claude/settings.json."""
    settings = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
    entries = settings["hooks"]["SessionStart"]
    assert isinstance(entries, list) and entries
    commands = [
        inner.get("command", "")
        for entry in entries
        for inner in entry.get("hooks", [])
    ]
    assert any("session_start_find_skills.py" in cmd and "--host claude" in cmd for cmd in commands)
    # Fires on a fresh open and on resume/clear; NOT on mid-session compaction.
    matchers = [entry.get("matcher", "") for entry in entries]
    joined = " ".join(matchers)
    assert "startup" in joined and "resume" in joined
    assert "compact" not in joined


def test_repo_codex_config_wires_session_start_hook() -> None:
    """Slice-3 acceptance: Codex parity is visible in the repo's .codex/config.toml."""
    config = tomllib.loads(CODEX_CONFIG.read_text(encoding="utf-8"))
    entries = config["hooks"]["SessionStart"]
    assert isinstance(entries, list) and entries
    commands = [
        inner.get("command", "")
        for entry in entries
        for inner in entry.get("hooks", [])
    ]
    assert any("session_start_find_skills.py" in cmd and "--host codex" in cmd for cmd in commands)
    # Repo-local hooks resolve from the git root (Codex may start in a subdir).
    assert any("git rev-parse --show-toplevel" in cmd for cmd in commands)
    matchers = [entry.get("matcher", "") for entry in entries]
    joined = " ".join(matchers)
    assert "startup" in joined and "resume" in joined
    assert "compact" not in joined
