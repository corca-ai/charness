"""What a completed task RESULT records, and how terminal states reach it.

Split from `test_task_run.py` at its length cap, on the seam the file already
had: everything before it drives the INVOCATION -- argv shapes, lane and worktree
creation, scope and parent-progress refusals -- and everything here reads the
record that invocation leaves behind. The delivery payload is projected, not
interpreted; the terminal states (completed, interrupted, timed-out, non-zero
exit) are each pinned with the WIP candidate they must or must not commit.
"""
from __future__ import annotations

import json
import os
import shlex
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_runtime, task_run_support
from skills.shared.scripts import reviewer_lifecycle

from .test_task_run_fixtures import _codex, _repo, _run


def _with_liveness(payload: dict[str, object]) -> dict[str, object]:
    """`task status` returns the record plus its read-time liveness projection."""
    return {**payload, "liveness": task_run_runtime.runner_liveness(payload)}


def test_task_result_exposes_schema_bearing_delivery_without_interpreting_it(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'schema_version: charness.reviewer_lifecycle.v1\\napproval_eligible: false\\ndelivery_state: findings-received\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="structured-review")

    delivery = payload["result_delivery"]
    assert delivery["structured_status"] == "valid"
    assert delivery["structured"] == {
        "schema_version": "charness.reviewer_lifecycle.v1",
        "approval_eligible": False,
        "delivery_state": "findings-received",
    }
    assert payload["reviewer_lifecycle"] == delivery["structured"]


def test_task_result_reports_malformed_schema_bearing_delivery(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\nprintf 'schema_version: broken\\nvalue: [\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="structured-invalid")

    assert payload["result_delivery"]["structured_status"] == "invalid"
    assert "structured" not in payload["result_delivery"]


def test_task_result_rejects_non_json_yaml_without_breaking_terminal_receipt(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\n"
        "printf 'schema_version: example.v1\\nwhen: 2026-08-28\\n'",
        deliver=False,
    )

    payload = _run(repo, tmp_path, executable, task_id="non-json-yaml")

    assert payload["status"] == "completed", payload
    assert payload["result_delivery"]["structured_status"] == "invalid"
    assert task_run.task_status(repo, "non-json-yaml") == _with_liveness(payload)


def _reviewer_lifecycle_codex(tmp_path: Path, carrier: dict[str, object]) -> Path:
    encoded = shlex.quote(json.dumps(carrier, separators=(",", ":")))
    return _codex(
        tmp_path,
        f"printf '%s\\n' {encoded}\nprintf 'VALUE = 2\\n' > module.py",
        deliver=False,
    )


@pytest.mark.parametrize(
    ("name", "carrier"),
    [
        (
            "preflight-blocked",
            reviewer_lifecycle.build_lifecycle(
                status="runner-invalid",
                error="reviewer boundary unavailable",
                reviewer_started=False,
            ),
        ),
        (
            "started-timed-out",
            reviewer_lifecycle.build_lifecycle(
                status="runner-timeout",
                error="canonical runner timed out",
                returncode=124,
                reviewer_started=True,
            ),
        ),
        (
            "terminal-delivered-block",
            reviewer_lifecycle.build_lifecycle(
                status="runner-completed",
                report={
                    "schema_version": "charness.reviewer_worker_report.v1",
                    "delivery_state": "findings-received",
                    "review_verdict": "block",
                    "classification": "contract",
                    "approval_eligible": False,
                },
                returncode=0,
                reviewer_started=True,
            ),
        ),
    ],
)
def test_task_result_projects_canonical_reviewer_lifecycle_exactly(
    tmp_path: Path, name: str, carrier: dict[str, object]
) -> None:
    repo = _repo(tmp_path)
    executable = _reviewer_lifecycle_codex(tmp_path, carrier)

    payload = _run(repo, tmp_path, executable, task_id=name)
    status = task_run.task_status(repo, name)

    assert payload["result_delivery"]["structured"] == carrier
    assert payload["reviewer_lifecycle"] is payload["result_delivery"]["structured"]
    assert payload["reviewer_lifecycle"] == carrier
    assert status == _with_liveness(payload)


def test_task_result_does_not_project_non_review_schema(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    carrier = {
        "schema_version": "charness.other_result.v1",
        "status": "complete",
        "review_verdict": "block",
    }
    executable = _reviewer_lifecycle_codex(tmp_path, carrier)

    payload = _run(repo, tmp_path, executable, task_id="non-review-schema")

    assert payload["result_delivery"]["structured"] == carrier
    assert "reviewer_lifecycle" not in payload


def test_running_result_is_visible_to_the_child(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result_path = task_run_support.task_runtime_root(repo) / "task-run" / "running-check" / "result.json"
    executable = _codex(
        tmp_path,
        f"grep '\"status\": \"running\"' {shlex.quote(str(result_path))} > running.txt\nprintf 'VALUE = 2\\n' > module.py",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        task_id="running-check",
        scopes=["module.py", "running.txt"],
    )

    assert payload["status"] == "completed", payload
    assert (tmp_path / "lane/running.txt").read_text(encoding="utf-8").strip() == '"status": "running",'


def test_interruption_is_a_distinct_terminal_state(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")
    monkeypatch.setattr(
        task_run,
        "_execute_codex",
        lambda *_args, **_kwargs: {
            "exit_code": None,
            "timed_out": False,
            "interrupted": True,
        },
    )

    payload = _run(repo, tmp_path, executable, require_change=False)

    assert payload["status"] == "interrupted"
    assert payload["execution"]["status"] == "interrupted"
    assert payload["phase"] == "terminal"


def test_a_nonzero_child_exit_commits_a_typed_wip_candidate(tmp_path: Path) -> None:
    """A failed child leaves the same untyped pile a timeout does.

    Timeout was preserved; a non-zero exit was not, so nearly-done work from a lane
    whose child died became an untyped worktree the parent had to triage by hand or
    pay to re-run. The checkpoint is explicitly UNVERIFIED -- it is durability, not
    approval.
    """
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py\nexit 3", deliver=False)

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "failed"
    assert payload["candidate"]["status"] == "wip"
    assert payload["candidate"]["state"] == "interrupted-mid-edit"
    assert payload["candidate"]["state_known"] is False
    assert payload["candidate"]["changed_paths"] == ["module.py"]
    commit = payload["candidate"]["commit"]
    assert commit["status"] == "committed"
    assert commit["correctness_verified"] is False
    # The work is durable, and it is still not approvable.
    assert payload["approval_eligibility"] == "ineligible"


def test_an_interrupted_child_commits_a_typed_wip_candidate(tmp_path: Path) -> None:
    """A signalled child is the shape the issue names beside the timeout."""
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path, "printf 'VALUE = 3\\n' > module.py\nkill -TERM $$", deliver=False
    )

    payload = _run(repo, tmp_path, executable)

    assert payload["candidate"]["status"] == "wip"
    assert payload["candidate"]["state_known"] is False
    assert payload["candidate"]["changed_paths"] == ["module.py"]
    assert payload["candidate"]["commit"]["status"] == "committed"
    assert payload["approval_eligibility"] == "ineligible"


def test_a_clean_normal_exit_still_produces_no_wip_commit(tmp_path: Path) -> None:
    """The control: widening the checkpoint must not mint WIP on an ordinary run."""
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 4\\n' > module.py")

    payload = _run(repo, tmp_path, executable)

    assert payload["status"] == "completed"
    assert payload["candidate"]["status"] == "validated"
    assert "commit" not in payload["candidate"] or payload["candidate"].get("commit") is None


def test_receipt_records_runner_pid_phase_timestamps_and_timings(tmp_path: Path) -> None:
    """#791: prepare and exec are reported separately, and the record says
    which process wrote it, so a reader can tell a live lane from a stale
    record without trusting a status word."""
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable, scopes=["module.py"])

    assert payload["runner_pid"] == os.getpid()
    stamps = payload["timestamps"]
    for key in ("launched_at", "create_started_at", "exec_started_at", "updated_at", "finished_at"):
        assert stamps[key].endswith("Z"), (key, stamps)
    assert set(payload["timings_ms"]) == {"prepare", "exec"}
    assert all(isinstance(value, int) and value >= 0 for value in payload["timings_ms"].values())
    assert payload["codex"]["timeout_scope"] == "codex-exec"


def test_task_status_projects_runner_liveness_against_the_record_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """#791: `task status` says whether the writer is alive and whether that
    agrees with the record; a terminal record with a live writer, or a running
    record with a dead one, is the two-store symptom made visible."""
    dead_pid = 4_000_001

    def kill(pid: int, sig: int) -> None:
        if pid == dead_pid:
            raise ProcessLookupError(pid)

    monkeypatch.setattr(task_run_runtime.os, "kill", kill)

    alive_running = task_run_runtime.runner_liveness({"runner_pid": os.getpid(), "phase": "exec"})
    assert alive_running == {"runner_pid": os.getpid(), "alive": True, "consistent": True}

    alive_terminal = task_run_runtime.runner_liveness(
        {"runner_pid": os.getpid(), "phase": "terminal"}
    )
    assert alive_terminal["alive"] is True and alive_terminal["consistent"] is False

    dead_running = task_run_runtime.runner_liveness({"runner_pid": dead_pid, "phase": "exec"})
    assert dead_running == {"runner_pid": dead_pid, "alive": False, "consistent": False}

    assert task_run_runtime.runner_liveness({"phase": "exec"}) == {
        "runner_pid": None,
        "alive": None,
        "consistent": None,
    }

    repo = _repo(tmp_path)
    runtime_path = task_run_runtime.task_runtime_root(repo)
    record_path = runtime_path / "task-run" / "stale" / "result.json"
    record_path.parent.mkdir(parents=True)
    record_path.write_text(
        json.dumps(
            {"task_id": "stale", "status": "timed-out", "phase": "terminal", "runner_pid": dead_pid}
        ),
        encoding="utf-8",
    )
    listing = task_run.task_status(repo)
    assert [task["liveness"] for task in listing["tasks"] if task["task_id"] == "stale"] == [
        {"runner_pid": dead_pid, "alive": False, "consistent": True}
    ]
    single = task_run.task_status(repo, "stale")
    assert single["liveness"]["alive"] is False
    assert "liveness" not in json.loads(record_path.read_text(encoding="utf-8"))
