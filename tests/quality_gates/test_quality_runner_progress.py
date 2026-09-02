from __future__ import annotations

from pathlib import Path

from .support import clone_quality_runner_repo, run_shell_script


def test_run_quality_reports_each_check_as_it_finishes(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    slow = repo / "tools" / "validate_skills.py"
    slow.write_text(
        "import time\ntime.sleep(1)\nprint('slow validator finished')\n",
        encoding="utf-8",
    )
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,validate-quality-reference-catalog"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    fast_position = result.stdout.index("PASS validate-quality-reference-catalog")
    slow_position = result.stdout.index("PASS validate-skills")
    assert fast_position < slow_position, (
        "completion status must follow observed completion, not queue order; otherwise "
        "a finished check remains invisible behind an unrelated slow check"
    )


def test_run_quality_rejects_invalid_heartbeat_interval(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    env["CHARNESS_QUALITY_HEARTBEAT_SECONDS"] = "soon"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 2
    assert "must be a non-negative integer" in result.stderr
