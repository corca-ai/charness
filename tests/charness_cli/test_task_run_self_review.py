"""Self-review receipt states and unavailable-review non-claims."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_execution, task_run_runtime, task_run_self_review
from tests.charness_cli.test_task_run_fixtures import _codex


def test_self_review_findings_are_grouped_by_disposition() -> None:
    block = task_run_self_review.self_review_block(
        "findings-received",
        findings=[
            {"summary": "The boundary is covered.", "disposition": "fixed", "evidence": ["src/a.py:2"]},
            {"summary": "The follow-up remains open.", "disposition": "deferred", "evidence": []},
            {"summary": "The reported risk does not apply.", "disposition": "disputed", "evidence": []},
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
        (
            "findings-received",
            [{"summary": "risk", "disposition": "fixed"}],
            "evidence must be a list",
        ),
    ],
)
def test_self_review_rejects_malformed_findings(state: str, findings: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        task_run_self_review.self_review_block(state, findings=findings)


def test_self_review_filters_blank_evidence() -> None:
    block = task_run_self_review.self_review_block(
        "findings-received",
        findings=[{"summary": "Risk", "disposition": "fixed", "evidence": ["path:2", " "]}],
    )

    assert block["findings"]["fixed"][0]["evidence"] == ["path:2"]


def test_self_review_prompt_and_schema_use_list_evidence() -> None:
    schema = task_run_self_review.self_review_schema()
    finding_schema = schema["properties"]["findings"]["items"]

    assert schema["required"] == list(schema["properties"])
    assert schema["properties"]["kind"]["enum"] == ["charness.task_self_review.v1"]
    assert finding_schema["properties"]["evidence"] == {
        "type": "array", "items": {"type": "string"}
    }
    prompt = task_run_self_review.self_review_prompt("Review.", "base", ["file.py"])
    assert finding_schema["required"] == list(finding_schema["properties"])
    assert "minLength" not in json.dumps(schema)
    assert "use [] when there is no evidence" in prompt
    assert "optional string evidence" not in prompt


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
            "candidate": {"changed_paths": ["src/module.py"]},
            "execution_runtime_root": str(tmp_path / "runtime"),
            "worktree_path": str(tmp_path),
        }
    )

    assert block["state"] == "unavailable-skip"
    assert reason_fragment in block["reason"]
    assert "not review-passed" in block["non_claim"]
    assert block["findings"] == {"fixed": [], "deferred": [], "disputed": []}


def test_self_review_normalizes_runtime_failures(tmp_path: Path) -> None:
    blocked_runtime = tmp_path.parent / f"{tmp_path.name}-runtime-file"
    blocked_runtime.write_text("file", encoding="utf-8")
    runtime_failure = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review this candidate.",
            "executor": {"kind": "codex", "command": [sys.executable]},
            "execution_runtime_root": str(blocked_runtime),
            "worktree_path": str(tmp_path),
        }
    )
    assert runtime_failure["state"] == "unavailable-skip"
    assert "reviewer could not run" in runtime_failure["reason"]


def test_self_review_maps_executor_and_invalid_result_failures() -> None:
    failed = task_run_self_review.self_review_result({"exit_code": 2}, "")
    invalid = task_run_self_review.self_review_result(
        {"exit_code": 0},
        '{"kind":"charness.task_self_review.v1","findings":"invalid"}',
    )

    assert failed["state"] == "unavailable-skip"
    assert "exited with code 2" in failed["reason"]
    assert invalid["state"] == "unavailable-skip"
    assert "invalid" in invalid["reason"]


def test_task_status_reads_the_self_review_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = tmp_path / "runtime"
    block = task_run_self_review.self_review_block(
        "unavailable-skip", reason="read-only reviewer is unavailable"
    )
    monkeypatch.setattr(task_run_runtime._git_owner, "_require_git_root", lambda _path: tmp_path)
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _repo: runtime)
    task_run_runtime.write_task_result(
        runtime, {"task_id": "review-consumer", "runner_pid": None, "self_review": block}
    )

    status = task_run_runtime.task_status(tmp_path, "review-consumer")

    assert status["self_review"] == block


def test_run_task_rejects_retired_auto_self_review_policy(tmp_path: Path) -> None:
    result = task_run.run_task(
        tmp_path, scopes=["module.py"], prompt="Review this candidate.", self_review_policy="auto"
    )

    assert result["status"] == "fail"
    assert "self_review_policy must be never or always" in result["error"]


def test_self_review_runs_a_read_only_codex_pass_and_records_findings(tmp_path: Path) -> None:
    executable = _codex(
        tmp_path,
        "cat >/dev/null",
        last_message=(
            '{"kind":"charness.task_self_review.v1",'
            '"findings":[{"summary":"Keep the follow-up visible.",'
            '"disposition":"deferred","evidence":["src/module.py:4"]}]}'
        ),
        record_arguments=True,
    )
    runtime_root = tmp_path.parent / f"{tmp_path.name}-runtime"
    block = task_run_execution.run_self_review(
        {
            "self_review_policy": "always",
            "_self_review_prompt": "Review the lane candidate.",
            "executor": {"kind": "codex", "command": [str(executable)], "timeout_seconds": 30},
            "candidate": {"changed_paths": ["src/module.py"]},
            "base_sha": "base-sha",
            "execution_runtime_root": str(runtime_root),
            "worktree_path": str(tmp_path),
        }
    )

    assert block["state"] == "findings-received"
    assert block["findings"]["deferred"][0]["summary"] == "Keep the follow-up visible."
    arguments = (tmp_path / "args").read_text(encoding="utf-8").splitlines()
    schema_path = Path(arguments[arguments.index("--output-schema") + 1])
    assert schema_path.is_file()
    assert task_run_self_review.self_review_schema() == json.loads(
        schema_path.read_text(encoding="utf-8")
    )
    assert block["findings"]["deferred"][0]["evidence"] == ["src/module.py:4"]


def test_default_policy_skips_gateway_path_and_push_prompt(tmp_path: Path) -> None:
    marker = tmp_path / "review-ran"
    executable = tmp_path / "codex"
    executable.write_text(
        f"#!/bin/sh\ntouch '{marker}'\ncat >/dev/null\nprintf '{{}}\\n'\n", encoding="utf-8"
    )
    executable.chmod(0o755)

    block = task_run_execution.run_self_review(
        {
            "_self_review_prompt": "Push this branch to origin after the change.",
            "executor": {"kind": "codex", "command": [str(executable)], "timeout_seconds": 30},
            "scopes": ["gateway/lease.py"],
            "candidate": {"changed_paths": ["gateway/lease.py"]},
            "persistence": {"findings": [], "blocking": False},
            "base_sha": "base-sha",
            "execution_runtime_root": str(tmp_path / "runtime"),
            "worktree_path": str(tmp_path),
        }
    )

    assert block["state"] == "not-requested"
    assert not marker.exists()


def test_self_review_module_imports_before_execution() -> None:
    """Either import order binds the same runner; no circular-import trap (#886)."""
    repo_root = Path(__file__).resolve().parents[2]
    probe = (
        "from scripts.task_run import task_run_self_review; "
        "from scripts.task_run import task_run_execution; "
        "assert task_run_execution.run_self_review "
        "is task_run_self_review.run_self_review"
    )
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
