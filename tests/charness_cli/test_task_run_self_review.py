"""Self-review receipt states and unavailable-review non-claims."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_execution, task_run_runtime, task_run_state


def test_self_review_findings_are_grouped_by_disposition() -> None:
    block = task_run_state.self_review_block(
        "findings-received",
        findings=[
            {"id": "f-1", "summary": "The boundary is covered.", "disposition": "fixed"},
            {"summary": "The follow-up remains open.", "disposition": "deferred"},
            {"summary": "The reported risk does not apply.", "disposition": "disputed"},
        ],
    )

    assert block["kind"] == "charness.task_self_review.v1"
    assert [item["summary"] for item in block["findings"]["fixed"]] == [
        "The boundary is covered."
    ]
    assert [item["disposition"] for item in block["findings"]["deferred"]] == [
        "deferred"
    ]
    assert [item["disposition"] for item in block["findings"]["disputed"]] == [
        "disputed"
    ]
    assert "independent review" in block["non_claim"]


@pytest.mark.parametrize(
    ("state", "findings", "message"),
    [
        ("passed", [], "unknown self-review state"),
        ("findings-received", "invalid", "must be a list"),
        ("findings-received", [{"summary": "risk", "disposition": "open"}], "needs"),
        ("findings-received", [{"summary": " ", "disposition": "fixed"}], "non-empty"),
        (
            "findings-received",
            [{"summary": "risk", "disposition": "fixed", "evidence": ["file.py", 3]}],
            "evidence must be a list",
        ),
    ],
)
def test_self_review_rejects_malformed_findings(state: str, findings: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        task_run_state.self_review_block(state, findings=findings)


def test_self_review_filters_blank_evidence() -> None:
    block = task_run_state.self_review_block(
        "findings-received",
        findings=[{"summary": "Risk", "disposition": "fixed", "evidence": ["path:2", " "]}],
    )

    assert block["findings"]["fixed"][0]["evidence"] == ["path:2"]


@pytest.mark.parametrize(
    ("executor", "command", "reason_fragment"),
    [
        ("muse", ["/not-used/muse"], "read-only Codex reviewer is unavailable"),
        ("codex", None, "reviewer command is unavailable"),
        ("codex", ["/not-installed/codex"], "reviewer executable is unavailable"),
    ],
)
def test_unavailable_self_review_is_a_reasoned_non_claim(
    tmp_path: Path,
    executor: str,
    command: list[str] | None,
    reason_fragment: str,
) -> None:
    block = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review this candidate.",
            "executor": {"kind": executor, "command": command},
            "scopes": ["src/module.py"],
            "candidate": {"changed_paths": ["src/module.py"]},
            "persistence": {"findings": [], "blocking": False},
            "execution_runtime_root": str(tmp_path / "runtime"),
            "worktree_path": str(tmp_path),
        }
    )

    assert block["state"] == "unavailable-skip"
    assert reason_fragment in block["reason"]
    assert "not review-passed" in block["non_claim"]
    assert block["findings"] == {"fixed": [], "deferred": [], "disputed": []}


def test_self_review_normalizes_bad_scopes_and_runtime_failures(tmp_path: Path) -> None:
    unavailable_executor = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review this candidate.",
            "executor": {"kind": "muse", "command": ["muse"]},
            "scopes": "not-a-list",
        }
    )
    assert unavailable_executor["state"] == "unavailable-skip"

    blocked_runtime = tmp_path.parent / f"{tmp_path.name}-runtime-file"
    blocked_runtime.write_text("file", encoding="utf-8")
    runtime_failure = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review this candidate.",
            "executor": {"kind": "codex", "command": [sys.executable]},
            "scopes": [],
            "execution_runtime_root": str(blocked_runtime),
            "worktree_path": str(tmp_path),
        }
    )
    assert runtime_failure["state"] == "unavailable-skip"
    assert "reviewer could not run" in runtime_failure["reason"]


def test_self_review_maps_executor_and_invalid_result_failures() -> None:
    failed = task_run_state.self_review_result({"exit_code": 2}, "")
    invalid = task_run_state.self_review_result(
        {"exit_code": 0},
        '{"kind":"charness.task_self_review.v1","findings":"invalid"}',
    )

    assert failed["state"] == "unavailable-skip"
    assert "exited with code 2" in failed["reason"]
    assert invalid["state"] == "unavailable-skip"
    assert "invalid" in invalid["reason"]


def test_task_status_reads_the_self_review_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = tmp_path / "runtime"
    block = task_run_state.self_review_block(
        "unavailable-skip", reason="read-only reviewer is unavailable"
    )
    monkeypatch.setattr(task_run_runtime._git_owner, "_require_git_root", lambda _path: tmp_path)
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _repo: runtime)
    task_run_runtime.write_task_result(
        runtime, {"task_id": "review-consumer", "runner_pid": None, "self_review": block}
    )

    status = task_run_runtime.task_status(tmp_path, "review-consumer")

    assert status["self_review"] == block


def test_run_task_rejects_unknown_self_review_policy(tmp_path: Path) -> None:
    result = task_run.run_task(
        tmp_path, scopes=["module.py"], prompt="Review this candidate.", self_review_policy="disabled"
    )

    assert result["status"] == "fail"
    assert "self_review_policy must be auto or always" in result["error"]


def test_self_review_runs_a_read_only_codex_pass_and_records_findings(tmp_path: Path) -> None:
    executable = tmp_path / "codex"
    runtime_root = tmp_path.parent / f"{tmp_path.name}-runtime"
    executable.write_text(
        "#!/bin/sh\ncat >/dev/null\n"
        "printf '%s\\n' '{\"kind\":\"charness.task_self_review.v1\","
        "\"findings\":[{\"summary\":\"Keep the follow-up visible.\","
        "\"disposition\":\"deferred\"}]}'\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    block = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review the lane candidate.",
            "executor": {"kind": "codex", "command": [str(executable)], "timeout_seconds": 30},
            "scopes": ["src/module.py"],
            "candidate": {"changed_paths": ["src/module.py"]},
            "persistence": {"findings": [], "blocking": False},
            "base_sha": "base-sha",
            "execution_runtime_root": str(runtime_root),
            "worktree_path": str(tmp_path),
        }
    )

    assert block["state"] == "findings-received"
    assert block["findings"]["deferred"][0]["summary"] == "Keep the follow-up visible."


def test_auto_policy_runs_for_boundary_signals_and_stays_off_for_ordinary_lanes() -> None:
    no_persistence_risk = {"findings": [], "blocking": False}

    assert not task_run_state.self_review_requested(
        "auto", "Update a local helper.", ["src/helper.py"], ["src/helper.py"], no_persistence_risk
    )
    assert task_run_state.self_review_requested(
        "auto", "Push this branch to origin after the change.", ["src/helper.py"],
        ["src/helper.py"], no_persistence_risk
    )
    assert task_run_state.self_review_requested(
        "auto", "Update a local helper.", ["src/store.py"], ["src/store.py"],
        {"findings": [{"shape": "unscoped-delete"}], "blocking": True}
    )
