"""Report-only task runs: inspection lanes without change or writer-conflict gates (#827)."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_completion, task_run_plan

from .test_task_run_fixtures import _codex, _repo, _run

ROOT = Path(__file__).resolve().parent.parent.parent


def test_report_only_completes_with_delivered_report_and_no_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "true")

    payload = _run(repo, tmp_path, executable, require_change=None, report_only=True)

    assert payload["report_only"] is True
    assert payload["require_change"] is False
    assert payload["status"] == "completed", payload
    assert payload["approval_eligibility"] == "eligible", payload
    assert payload["result_delivery"]["status"] == "delivered"
    assert payload["result_delivery"]["text"].strip() != ""
    assert payload["candidate"]["status"] == "absent"
    assert payload["candidate"]["changed_paths"] == []
    assert payload["scope"]["verdict"] == task_run.PASS
    assert "lane stalled" not in payload["next_step"]


def test_report_only_parent_progress_inside_read_scope_is_not_a_writer_conflict(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        f"printf 'parent\\n' > {repo / 'module.py'}\n"
        f"git -C {repo} add module.py\n"
        f"git -C {repo} -c user.email=test@example.com -c user.name=test "
        "commit -m 'parent progress inside the read scope'",
    )

    payload = _run(repo, tmp_path, executable, require_change=None, report_only=True)

    assert payload["status"] == "completed", payload
    assert payload["approval_eligibility"] == "eligible", payload
    progress = payload["parent"]["progress"]
    assert progress["classification"] == "concurrent-parent-progress"
    assert progress["blocking"] is False
    assert progress["overlap_paths"] == ["module.py"]
    assert progress["committed_paths"] == ["module.py"]
    assert progress["before_head"] == payload["base_sha"]
    assert progress["after_head"] != payload["base_sha"]


def test_report_only_executor_failure_is_a_typed_failure(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 3", deliver=False)

    payload = _run(repo, tmp_path, executable, require_change=None, report_only=True)

    assert payload["status"] == "failed", payload
    assert payload["approval_eligibility"] == "ineligible"


def test_report_only_missing_report_is_a_typed_failure(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "true", deliver=False)

    payload = _run(repo, tmp_path, executable, require_change=None, report_only=True)

    assert payload["execution"]["status"] == "non-delivery"
    assert payload["status"] == "failed", payload
    assert payload["approval_eligibility"] == "ineligible"
    assert "no report" in payload["next_step"]


def test_report_only_truncated_delivery_blocks_but_writer_delivery_does_not() -> None:
    truncated = {"status": "delivered", "text": "partial", "truncated": True, "bytes": 7}
    scope = {"verdict": task_run.PASS, "reason": "all candidate changes are within scope"}
    parent = {"blocking": False}

    report_blockers = task_run_completion._completion_blockers(
        execution_status="completed",
        scope=scope,
        parent_progress=parent,
        pass_value=task_run.PASS,
        delivery=truncated,
        report_only=True,
    )
    writer_blockers = task_run_completion._completion_blockers(
        execution_status="completed",
        scope=scope,
        parent_progress=parent,
        pass_value=task_run.PASS,
        delivery=truncated,
        report_only=False,
    )

    assert any("truncat" in blocker for blocker in report_blockers)
    assert writer_blockers == []


def test_report_only_rejects_require_change_and_forces_no_change(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    def resolve(**overrides):
        options = {
            "target_path": tmp_path / "lane",
            "branch": "lane/report",
            "base": "HEAD",
            "lane": None,
            "scopes": ["module.py"],
            "prompt": "inspect and report",
            "codex": "python3",
            "effort": "medium",
            "task_id": None,
            "prepare": None,
            "require_change": None,
            "skip_prepare": False,
            "allow_no_change": False,
            "timeout_seconds": 60,
            "report_only": False,
        }
        options.update(overrides)
        return task_run_plan.resolve_task_inputs(repo, **options)

    with pytest.raises(task_run.TaskRunError, match="--report-only"):
        resolve(require_change=True, report_only=True)
    resolved = resolve(report_only=True)
    assert resolved["report_only"] is True
    assert resolved["require_change"] is False


def test_writer_require_change_contract_is_retained(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "true")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "failed", payload
    assert payload["scope"]["reason"] == "the task required a change but the worktree is unchanged"


def test_task_run_help_names_report_only(capsys: pytest.CaptureFixture[str]) -> None:
    namespace = runpy.run_path(str(ROOT / "charness"))

    with pytest.raises(SystemExit) as exc:
        namespace["build_parser"]().parse_args(["task", "run", "--help"])

    assert exc.value.code == 0
    assert "--report-only" in capsys.readouterr().out
