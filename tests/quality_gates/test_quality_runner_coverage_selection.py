from __future__ import annotations

import subprocess
from pathlib import Path

from .support import clone_quality_runner_repo, init_git_repo, run_shell_script, write_executable


def _commit_quality_runner_repo(repo: Path, *tracked_paths: str) -> None:
    init_git_repo(repo, *tracked_paths)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)


def test_run_quality_read_only_skips_check_coverage_without_control_plane_changes(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    (repo / "README.md").write_text("# demo\n\nnon coverage change\n", encoding="utf-8")

    # Coverage selection is a broad-lane contract; the default implementation
    # lane intentionally does not discover or run this expensive check.
    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", "--read-only", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS pytest" in result.stdout
    assert "PASS check-coverage" not in result.stdout


def test_run_quality_read_only_runs_check_coverage_for_relevant_changes(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _commit_quality_runner_repo(repo)
    (repo / "scripts" / "check_coverage.py").write_text(
        "#!/usr/bin/env python3\nprint('quality success output from check-coverage')\n",
        encoding="utf-8",
    )

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", "--read-only", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS check-coverage" in result.stdout


def test_run_quality_read_only_runs_check_coverage_when_changed_path_discovery_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    write_executable(
        repo / "bin" / "git",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "$1" == "rev-parse" && "${2:-}" == "--is-inside-work-tree" ]]; then',
                "  echo true",
                "  exit 0",
                "fi",
                'if [[ "$1" == "rev-parse" && "${2:-}" == "--abbrev-ref" ]]; then',
                '  echo "fatal: no upstream configured for branch" >&2',
                "  exit 128",
                "fi",
                'if [[ "$1" == "diff" && "${2:-}" == "--name-only" && "$#" -eq 2 ]]; then',
                '  echo "forced changed-path failure" >&2',
                "  exit 42",
                "fi",
                'if [[ "$1" == "diff" && "${2:-}" == "--name-only" && "${3:-}" == "--cached" ]]; then',
                "  exit 0",
                "fi",
                'if [[ "$1" == "ls-files" && "${2:-}" == "--others" ]]; then',
                "  exit 0",
                "fi",
                'echo "unexpected git invocation: $*" >&2',
                "exit 99",
                "",
            ]
        ),
    )
    env["QUALITY_FAIL_LABEL"] = "check-coverage"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", "--read-only", cwd=repo, env=env)

    assert result.returncode == 1
    assert "run-quality: changed-path discovery command failed (unstaged-diff)" in result.stderr
    assert "command: git diff --name-only" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced changed-path failure" in result.stderr
    assert "run-quality: changed-path discovery failed; running check-coverage fail-closed." in result.stderr
    assert "FAIL check-coverage" in result.stdout
    assert "quality failure output from check-coverage" in result.stdout


def test_run_quality_full_runs_check_coverage_without_control_plane_changes(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS check-coverage" in result.stdout


def test_release_read_only_keeps_check_coverage_outside_the_mutation_nonclaim(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--release",
        "--read-only",
        "--non-claim=release-changed-line-coverage",
        cwd=repo,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS check-coverage" in result.stdout


def test_release_read_only_surfaces_check_coverage_failure_despite_mutation_nonclaim(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    env["QUALITY_FAIL_LABEL"] = "check-coverage"

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--release",
        "--read-only",
        "--non-claim=release-changed-line-coverage",
        cwd=repo,
        env=env,
    )

    assert result.returncode != 0
    assert "FAIL check-coverage" in result.stdout
    assert "quality failure output from check-coverage" in result.stdout


def test_run_quality_full_surfaces_planted_check_coverage_regression(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    env["QUALITY_FAIL_LABEL"] = "check-coverage"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)
    assert result.returncode != 0
    assert "FAIL check-coverage" in result.stdout
    assert "quality failure output from check-coverage" in result.stdout
