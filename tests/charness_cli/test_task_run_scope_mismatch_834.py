"""Preserve scope mismatch facts without inferring edits from phase declarations."""

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


def test_declared_editing_without_a_diff_does_not_prove_candidate_reversal(tmp_path) -> None:
    from tests.charness_cli.test_task_run_fixtures import _codex, _repo, _run

    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        'echo "CONTRACT-READ"\necho "EDITING"\necho "TESTING"\n'
        'echo "BLOCKED: scope mismatch - real owner other.py is outside declared scope"',
    )
    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "failed"
    assert payload["scope"]["changed_paths"] == []
    assert "required a change" in payload["scope"]["reason"]
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ", "EDITING", "TESTING"]
    assert "scope mismatch" in payload["lane_progress"]["blocker"]
    assert "candidate_self_reverted" not in payload
    assert "self_reverted" not in payload["candidate"]
    assert "recovered_scoped_snapshot" not in payload
