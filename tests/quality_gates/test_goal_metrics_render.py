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

    assert "unavailable: no Codex session audit for this run" in block
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
