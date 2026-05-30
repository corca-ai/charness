from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import session_start_find_skills as hook  # noqa: E402

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_find_skills.py"

# The find-skills SessionStart trigger is installed at USER level
# (~/.claude/settings.json, ~/.codex/config.toml) pointing at the released
# plugin script, not committed into this repo. These tests pin the script's
# behavior (the portable mechanism); the host wiring is per-machine config.


def test_directive_is_dumb_and_points_at_find_skills() -> None:
    """The directive triggers find-skills and defers ALL routing to that skill.

    It must not re-encode routing rules: find-skills owns the pickup -> handoff
    decision (see find-skills/references/session-start-routing.md), so the hook
    text stays fully decoupled from `handoff` and the handoff doc.
    """
    directive = hook.build_additional_context()
    # Triggers find-skills.
    assert "charness:find-skills" in directive
    # Stays dumb: the routing decision lives in the skill, not the hook text.
    assert "routing decision lives in that skill" in directive
    # Decoupled: the hook must not name handoff, pickup, or the handoff doc —
    # that routing lives entirely in find-skills.
    lowered = directive.lower()
    assert "handoff" not in lowered
    assert "pickup" not in lowered
    assert "docs/handoff" not in lowered


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
