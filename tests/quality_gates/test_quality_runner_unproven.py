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

_UNPROVEN_LABEL = "check-changed-line-mutation-coverage"
_UNPROVEN_GATE_SCRIPT = "prepush_focused_changed_line_coverage.py"


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
        repo / "scripts" / script,
        f"#!/usr/bin/env python3\nimport sys\nprint({message!r})\nsys.exit({exit_code})\n",
    )


def test_release_only_mutation_gate_can_be_unestablished(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _stub_gate(repo, _UNPROVEN_GATE_SCRIPT, 3, "this run analyzed nothing")
    env["CHARNESS_QUALITY_LABELS"] = f"{_UNPROVEN_LABEL},check-markdown"

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env
    )

    assert result.returncode == 0, result.stderr
    assert_quality_receipt(
        repo,
        result,
        status="unestablished",
        passed=1,
        failed=0,
        unproven_subjects=[_UNPROVEN_LABEL],
    )
    assert "this run analyzed nothing" in result.stdout


def test_release_only_mutation_gate_reports_partial_scope_as_unproven(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _stub_gate(repo, _UNPROVEN_GATE_SCRIPT, 4, "analyzed only 1 of 2 changed files")
    env["CHARNESS_QUALITY_LABELS"] = f"{_UNPROVEN_LABEL},check-markdown"

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env
    )

    assert result.returncode == 0, result.stderr
    assert f"UNPROVEN {_UNPROVEN_LABEL}" in result.stdout
    assert f"FAIL {_UNPROVEN_LABEL}" not in result.stdout
    assert f"PASS {_UNPROVEN_LABEL}" not in result.stdout
    assert "analyzed only 1 of 2 changed files" in result.stdout
    assert_quality_receipt(
        repo,
        result,
        status="unestablished",
        passed=1,
        failed=0,
        unproven_subjects=[_UNPROVEN_LABEL],
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


def test_a_real_failure_is_still_a_failure_next_to_an_unproven_gate(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _stub_gate(repo, _UNPROVEN_GATE_SCRIPT, 3, "this run analyzed nothing")
    _stub_gate(repo, "check_doc_links.py", 1, "broken link")
    env["CHARNESS_QUALITY_LABELS"] = f"{_UNPROVEN_LABEL},check-doc-links"

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env
    )

    assert result.returncode != 0
    assert_quality_receipt(
        repo,
        result,
        status="fail",
        passed=0,
        failed=1,
        adverse_subjects=["check-doc-links"],
        unproven_subjects=[_UNPROVEN_LABEL],
    )
    _assert_external_failure_recovery(repo, "check-doc-links")


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


def test_release_arms_mutation_refusal_but_full_does_not(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    argv_log = repo / "argv.log"
    write_executable(
        repo / "scripts" / _UNPROVEN_GATE_SCRIPT,
        "#!/usr/bin/env python3\nimport sys\n"
        f"open({str(argv_log)!r}, 'a').write(' '.join(sys.argv[1:]) + chr(10))\n",
    )
    env["CHARNESS_QUALITY_LABELS"] = _UNPROVEN_LABEL

    ordinary = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--full", "--read-only", cwd=repo, env=env
    )
    assert ordinary.returncode == 2
    assert not argv_log.exists()

    release = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env
    )
    assert release.returncode == 0
    assert "--refuse-unestablished" in argv_log.read_text(encoding="utf-8")
