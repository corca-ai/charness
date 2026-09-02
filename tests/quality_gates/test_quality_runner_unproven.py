from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import (
    ROOT,
    assert_quality_receipt,
    clone_quality_runner_repo,
    run_shell_script,
    write_executable,
)


def _assert_external_failure_recovery(repo: Path, label: str) -> None:
    receipt = json.loads((repo / "receipt.json").read_text(encoding="utf-8"))
    recovery = receipt["adverse_subjects"][0]["recovery"]
    assert recovery["status"] == "available"
    path = Path(recovery["path"])
    assert path.is_absolute()
    assert path.name == f"{label}.log"
    assert path.parent.name == "quality-failure-logs"
    assert path.is_file()
    assert not path.is_relative_to(repo)


def _stub_gate(repo: Path, script: str, exit_code: int, message: str) -> None:
    write_executable(
        repo / "tools" / script,
        f"#!/usr/bin/env python3\nimport sys\nprint({message!r})\nsys.exit({exit_code})\n",
    )


def test_exit_four_from_a_gate_that_did_not_opt_in_still_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _stub_gate(repo, "validate_skills.py", 4, "some other tool's exit 4")
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode != 0
    assert "FAIL validate-skills" in result.stdout
    assert "UNPROVEN" not in result.stdout


def test_exit_three_from_a_gate_that_did_not_opt_in_still_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _stub_gate(repo, "validate_skills.py", 3, "INTERNAL ERROR: conftest crashed")
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode != 0
    assert "FAIL validate-skills" in result.stdout
    assert "UNPROVEN" not in result.stdout
    assert_quality_receipt(
        repo, result, status="fail", passed=1, failed=1, adverse_subjects=["validate-skills"]
    )
    _assert_external_failure_recovery(repo, "validate-skills")


def test_the_unproven_column_is_absent_when_every_gate_established_its_scope(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert_quality_receipt(repo, result, status="pass", passed=2, failed=0)
    assert "UNPROVEN" not in result.stdout


def test_the_real_runtime_recorder_accepts_every_status_the_runner_emits() -> None:
    recorder = import_repo_module(
        ROOT / "scripts/record_quality_runtime.py", "scripts.record_quality_runtime"
    )

    assert "unestablished" in recorder.VALID_STATUSES
    for status in ("pass", "fail", "unestablished"):
        parsed = recorder._read_batch_line(
            json.dumps(
                {
                    "label": "x",
                    "elapsed_ms": 1,
                    "status": status,
                    "timestamp": "2026-07-29T00:00:00Z",
                }
            )
        )
        assert parsed["status"] == status
    with pytest.raises(ValueError):
        recorder._read_batch_line(
            json.dumps(
                {
                    "label": "x",
                    "elapsed_ms": 1,
                    "status": "green",
                    "timestamp": "2026-07-29T00:00:00Z",
                }
            )
        )
