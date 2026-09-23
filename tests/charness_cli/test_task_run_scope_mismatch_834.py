"""Post-edit scope-mismatch handling for task-run lanes (#834).

After EDITING the worker must keep its candidate and emit the typed scope-
extension request instead of restoring scoped files; a lane that emitted
EDITING and ends BLOCKED with an unchanged worktree is recorded as
`candidate-self-reverted` with the guard snapshot as recovery pointer.
"""

from __future__ import annotations

from scripts.task_run import task_run_lane_runner as lane_runner


def test_post_edit_scope_mismatch_keeps_candidate_and_types_request() -> None:
    """After EDITING the worker must not restore scoped files (#834)."""
    shaped = lane_runner.build_lane_prompt(
        "Fix the lease delta.",
        require_change=True,
        scopes=["gateway/lease.py"],
    )
    assert "After the first scoped edit has landed" in shaped
    assert "never run git restore" in shaped
    assert "Keep the candidate as it is" in shaped
    assert "BLOCKED: scope mismatch - real owner <path> is outside declared scope" in shaped
    assert "scope_extension_request" in shaped


def test_self_revert_backstop_flags_editing_blocked_unchanged() -> None:
    from scripts.task_run import task_run_completion

    payload = {
        "lane_progress": {
            "phases": ["CONTRACT-READ", "EDITING", "TESTING"],
            "blocker": "scope mismatch - real owner other.py is outside declared scope",
        },
        "candidate": {"status": "absent"},
        "target_sha": "base-sha",
        "progress_guard": {"first_scoped_diff": {"observed": False}},
    }
    scope = {"changed_paths": [], "disallowed_paths": []}
    blockers: list[str] = []
    assert (
        task_run_completion._apply_self_revert_backstop(
            payload, scope, blockers, base_sha="base-sha", require_change=True
        )
        is True
    )
    assert payload["candidate_self_reverted"] is True
    assert payload["candidate"]["self_reverted"] is True
    assert any("self-reverted" in blocker for blocker in blockers)
    assert payload["recovered_scoped_snapshot"]["unobserved"] is True

    observed = {
        "lane_progress": {
            "phases": ["EDITING"],
            "blocker": "scope mismatch - real owner other.py is outside declared scope",
        },
        "candidate": {"status": "absent"},
        "target_sha": "base-sha",
        "progress_guard": {
            "first_scoped_diff": {
                "observed": True,
                "changed_paths": ["module.py"],
                "diff": "diff --git a/module.py",
                "truncated": False,
            }
        },
    }
    observed_blockers: list[str] = []
    assert (
        task_run_completion._apply_self_revert_backstop(
            observed, scope, observed_blockers, base_sha="base-sha", require_change=True
        )
        is True
    )
    snapshot = observed["recovered_scoped_snapshot"]
    assert snapshot["changed_paths"] == ["module.py"]
    assert snapshot["diff_ref"] == "progress_guard.first_scoped_diff.diff"
    assert "diff" not in snapshot

    pre_edit = {
        "lane_progress": {"phases": ["CONTRACT-READ"], "blocker": "premise/scope mismatch"},
        "candidate": {"status": "absent"},
        "target_sha": "base-sha",
    }
    assert (
        task_run_completion._apply_self_revert_backstop(
            pre_edit, scope, [], base_sha="base-sha", require_change=True
        )
        is False
    )
    assert "candidate_self_reverted" not in pre_edit
