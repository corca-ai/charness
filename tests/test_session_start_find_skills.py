from __future__ import annotations

import json
import subprocess
from pathlib import Path

import session_start_find_skills as hook

REPO_ROOT = Path(__file__).resolve().parent.parent

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_find_skills.py"

# The session-start routing trigger is installed at USER level
# (~/.claude/settings.json, ~/.codex/config.toml) pointing at the released
# plugin script, not committed into this repo. These tests pin the script's
# behavior (the portable mechanism); the host wiring is per-machine config.
#
# 2026-07-04 contract inversion: the original #240 fix kept this hook "dumb"
# (it only pointed at `charness:find-skills`, which owned the pickup ->
# handoff decision). That design was replaced by a front-load: the hook now
# carries the routing rule directly, so pickup-drive protection moved INTO
# the directive text itself instead of living solely in the find-skills
# skill. `test_directive_is_dumb_and_points_at_find_skills` below used to
# assert the directive must NOT mention "handoff"/"pickup"; it is inverted
# here to assert the directive DOES name the pickup -> `charness:handoff`
# route, `docs/handoff.md`, `charness:find-skills` for capability discovery,
# and the `charness-artifacts/find-skills/latest.md` capability map. See
# `skills/public/find-skills/references/session-start-routing.md` for the
# full history and the three carried-over #240 protections.


def test_directive_front_loads_pickup_discovery_and_otherwise_routes() -> None:
    """The directive now states the routing rule directly, not just a pointer.

    Carries over the #240 protections: (1) a pickup deterministically drives
    into the handoff-named workflow, (2) capability discovery stays owned by
    `find-skills`, (3) the capability map is named so a missing/stale map or
    an unclear route still falls back to `find-skills`.
    """
    directive = hook.build_additional_context()
    lowered = directive.lower()
    # (1) Pickup route: names the handoff doc, its Workflow Trigger, and the
    # concrete skill to invoke -- this used to live only in find-skills.
    assert "pickup" in lowered
    assert "docs/handoff.md" in directive
    assert "workflow trigger" in lowered
    assert "charness:handoff" in directive
    # (2) Capability-discovery route: still owned by find-skills.
    assert "charness:find-skills" in directive
    assert "capability discovery" in lowered
    # (3) Capability map + fallback: names the map artifact and the
    # missing/stale/unclear conditions that still send it to find-skills.
    assert "charness-artifacts/find-skills/latest.md" in directive
    assert "missing or stale" in lowered
    assert "genuinely unclear" in lowered


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
