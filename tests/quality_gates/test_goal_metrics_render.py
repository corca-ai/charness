from __future__ import annotations

from scripts import goal_metrics_render_lib as render


def _payload_with_window_audit(*, status: str, scope_key: str) -> dict:
    audit = {
        "measured": {
            "token_count_snapshots": 5,
            "function_calls": 12,
            "custom_tool_calls": 3,
            "patch_applications": 4,
            "context_compactions": 1,
            "subagent": {"spawn": 2, "wait": 2, "close": 2},
        },
        "proxy": {
            "repeated_broad_gates": {"pytest": 4},
            "repeated_vcs_commands": {"git diff": 6, "git status": 3},
        },
        "window_filter": {"status": "applied", "included_records": 9, "total_records": 20},
    }
    return {
        "goal_metric_window": {
            "status": status,
            "started_at": "2026-06-03T00:00:00Z",
            "completed_at": "2026-06-03T03:42:00Z",
        },
        "hosts": {"codex": {scope_key: audit}, "claude": {}},
    }


def test_render_block_uses_goal_window_scope_when_parsed() -> None:
    payload = _payload_with_window_audit(status="parsed", scope_key="goal_window_audit")
    block = render.render_goal_metrics_block(payload)

    assert "## Goal Closeout Metrics" in block
    assert "Goal metric window: parsed — applied" in block
    assert "2026-06-03T00:00:00Z -> 2026-06-03T03:42:00Z" in block
    # measured and proxy are rendered as separate sections
    assert "### Measured (goal-window scope)" in block
    assert "function calls: 12" in block
    assert "subagent spawn/wait/close: spawn=2, wait=2, close=2" in block
    assert "### Proxy (activity shape, not measured cost)" in block
    assert "repeated broad gates: pytest=4" in block
    assert "repeated VCS commands: git diff=6, git status=3" in block


def test_render_block_surfaces_absent_window_and_falls_back_to_thread_wide() -> None:
    payload = _payload_with_window_audit(status="absent", scope_key="session_audit")
    block = render.render_goal_metrics_block(payload)

    # an absent window must not masquerade as a per-goal total
    assert "Goal metric window: absent — ABSENT" in block
    assert "thread-wide pressure, not a per-goal total" in block
    assert "### Measured (thread-wide scope)" in block


def test_render_block_marks_codex_unavailable_when_no_audit() -> None:
    payload = {
        "goal_metric_window": {"status": "not_requested"},
        "hosts": {"codex": {}, "claude": {"metrics": {"token_count": {"status": "available", "detail": "usage fields present"}}}},
    }
    block = render.render_goal_metrics_block(payload)

    assert "unavailable: no Codex or Claude session audit for this run" in block
    assert "### Token availability (Claude host)" in block
    assert "available: usage fields present" in block


def test_render_block_is_provider_safe_and_records_results_not_commands() -> None:
    payload = _payload_with_window_audit(status="parsed", scope_key="goal_window_audit")
    attestations = [{"gate": "final-quality", "outcome": "PASS", "state_ref": "abc1234 (tree-clean)"}]
    block = render.render_goal_metrics_block(payload, attestations=attestations)

    assert "### Broad-gate attestation (results, not commands)" in block
    assert "final-quality: PASS @ abc1234 (tree-clean)" in block
    # the renderer never emits provider CLI verification command strings
    lowered = block.lower()
    for provider_token in ("gh issue", "gh pr", "ceal github", "gh auth"):
        assert provider_token not in lowered


def test_broad_gate_attestation_flattens_pasted_command_blocks() -> None:
    # Even if a caller passes a multi-line command-looking blob, it is flattened
    # to a single result line — the structure has no command field to honor.
    attestations = [{"gate": "g", "outcome": "PASS\n$ gh issue close 1", "state_ref": "deadbee"}]
    rendered = render.render_broad_gate_attestation(attestations)

    assert rendered.count("\n- ") == 1  # one result line, no embedded command block
    assert "\n$ " not in rendered


def test_render_block_handles_non_ascii() -> None:
    payload = {
        "goal_metric_window": {"status": "absent"},
        "hosts": {"codex": {}, "claude": {}},
    }
    block = render.render_goal_metrics_block(payload)
    # rendering is pure-string and never raises on default content
    assert block.endswith("\n")


def _claude_audit(*, last_event_at: str | None = "2026-06-10T09:00:00Z") -> dict:
    return {
        "source": {"kind": "session-jsonl", "host": "claude", "path": "/home/u/.claude/projects/p/s.jsonl"},
        "measured": {
            "token_count_snapshots": 7,
            "function_calls": 21,
            "custom_tool_calls": 1,
            "patch_applications": 6,
            "context_compactions": 0,
            "subagent": {"spawn": 2},
        },
        "proxy": {"repeated_broad_gates": {}, "repeated_vcs_commands": {}},
        "window_filter": {"status": "applied", "included_records": 30, "total_records": 40},
        "last_event_at": last_event_at,
    }


def _codex_audit(*, last_event_at: str | None = "2026-06-05T16:00:00Z") -> dict:
    return {
        "source": {"kind": "session-jsonl", "path": "/home/u/.codex/sessions/r.jsonl"},
        "measured": {
            "token_count_snapshots": 434,
            "function_calls": 429,
            "custom_tool_calls": 149,
            "patch_applications": 139,
            "context_compactions": 4,
            "subagent": {"spawn": 4, "wait": 3, "close": 3},
        },
        "proxy": {"repeated_broad_gates": {}, "repeated_vcs_commands": {}},
        "window_filter": {},
        "last_event_at": last_event_at,
    }


def test_render_block_scopes_to_claude_goal_window_audit_with_provenance() -> None:
    payload = {
        "goal_metric_window": {
            "status": "parsed",
            "started_at": "2026-06-10T08:50:14Z",
            "completed_at": "2026-06-10T12:50:14Z",
        },
        "hosts": {"codex": {"session_audit": _codex_audit()}, "claude": {"goal_window_audit": _claude_audit()}},
    }
    block = render.render_goal_metrics_block(payload)

    assert "### Measured (goal-window, claude session scope)" in block
    assert "- session: /home/u/.claude/projects/p/s.jsonl" in block
    assert "function calls: 21" in block
    # the stale codex audit must not be presented as the measured block
    assert "function calls: 429" not in block


def test_render_block_prefers_freshest_session_audit_over_stale_cross_host() -> None:
    payload = {
        "goal_metric_window": {"status": "not_requested"},
        "hosts": {
            "codex": {"session_audit": _codex_audit(last_event_at="2026-06-05T16:00:00Z")},
            "claude": {"session_audit": _claude_audit(last_event_at="2026-06-10T09:00:00Z")},
        },
    }
    block = render.render_goal_metrics_block(payload)

    assert "### Measured (thread-wide, claude session scope)" in block
    assert "function calls: 21" in block
    assert "function calls: 429" not in block


def test_render_block_keeps_codex_audit_when_codex_is_fresher_or_tied() -> None:
    payload = {
        "goal_metric_window": {"status": "not_requested"},
        "hosts": {
            "codex": {"session_audit": _codex_audit(last_event_at="2026-06-10T09:00:00Z")},
            "claude": {"session_audit": _claude_audit(last_event_at="2026-06-10T09:00:00Z")},
        },
    }
    block = render.render_goal_metrics_block(payload)

    assert "### Measured (thread-wide scope)" in block
    assert "function calls: 429" in block
    # codex-sourced output carries no claude provenance line
    assert "- session:" not in block
