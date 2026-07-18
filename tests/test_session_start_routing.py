from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path

import session_start_routing as hook

REPO_ROOT = Path(__file__).resolve().parent.parent

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_routing.py"

# The session-start routing trigger is installed at USER level
# (~/.claude/settings.json, ~/.codex/config.toml) pointing at the released
# plugin script, not committed into this repo. These tests pin the script's
# behavior (the portable mechanism); the host wiring is per-machine config.
#
# The hook carries contextual pickup guidance and points at the deterministic
# catalog only for hidden inventory facts. It does not classify tasks or invoke
# a public semantic-routing skill; ordinary workflow choice remains owned by
# installed metadata and model judgment.


def test_directive_front_loads_pickup_inventory_and_otherwise_routes() -> None:
    """The directive now states the routing rule directly, not just a pointer.

    Carries over the #240 protections: (1) a pickup deterministically drives
    into the handoff-named workflow and (2) hidden capability inventory stays
    a deterministic catalog lookup rather than semantic routing.
    """
    directive = hook.build_additional_context()
    lowered = directive.lower()
    # (1) Pickup route: names the handoff doc, its Workflow Trigger, and the
    # concrete skill to invoke.
    assert "pickup" in lowered
    assert "docs/handoff.md" in directive
    assert "workflow trigger" in lowered
    assert "charness:handoff" in directive
    # (2) Hidden inventory route: deterministic catalog facts only.
    assert "charness catalog list" in directive
    assert "--summary" in directive
    assert "--json" not in directive
    assert "hidden support/integration" in lowered
    assert "treat its facts only as inventory" in lowered
    assert "start the matching workflow directly" in directive
    assert "if the command returns nonzero" in directive


def test_render_output_claude_emits_session_start_additional_context() -> None:
    payload = json.loads(hook.render_output("claude"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness catalog list" in inner["additionalContext"]


def test_render_output_codex_emits_session_start_additional_context() -> None:
    # Codex confirmed 2026-05-29 to support hookSpecificOutput.additionalContext.
    payload = json.loads(hook.render_output("codex"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness catalog list" in inner["additionalContext"]


def test_render_output_unknown_emits_plain_directive() -> None:
    out = hook.render_output("unknown")
    # Plain text fallback, not the structured JSON wrapper.
    assert "hookSpecificOutput" not in out
    assert "charness catalog list" in out


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
    assert "charness catalog list" in emitted["hookSpecificOutput"]["additionalContext"]


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
    assert "charness catalog list" in result.stdout


def test_read_payload_reports_oserror_in_debug_mode(monkeypatch, capsys) -> None:
    class BrokenStream:
        def read(self) -> str:
            raise OSError("stdin unavailable")

    monkeypatch.setenv("CHARNESS_SESSION_START_DEBUG", "1")

    assert hook._read_payload(BrokenStream()) == {}
    assert "session_start_routing: stdin read failed: stdin unavailable" in capsys.readouterr().err


def test_read_payload_empty_input_returns_empty_mapping() -> None:
    assert hook._read_payload(io.StringIO("  \n")) == {}
