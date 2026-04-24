from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .support import ROOT, clone_quality_runner_repo, init_git_repo, run_script, run_shell_script


def test_record_quality_runtime_writes_summary_and_archive(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    first = run_script(
        "scripts/record_quality_runtime.py",
        "--repo-root",
        str(repo),
        "--label",
        "pytest",
        "--elapsed-ms",
        "1234",
        "--status",
        "pass",
        "--timestamp",
        "2026-04-10T09:00:00Z",
        "--runtime-profile",
        "default",
        cwd=ROOT,
    )
    assert first.returncode == 0, first.stderr

    second = run_script(
        "scripts/record_quality_runtime.py",
        "--repo-root",
        str(repo),
        "--label",
        "pytest",
        "--elapsed-ms",
        "2345",
        "--status",
        "fail",
        "--timestamp",
        "2026-04-11T09:00:00Z",
        "--runtime-profile",
        "default",
        cwd=ROOT,
    )
    assert second.returncode == 0, second.stderr

    summary_path = repo / ".charness" / "quality" / "runtime-signals.json"
    smoothing_path = repo / ".charness" / "quality" / "runtime-smoothing.json"
    archive_path = repo / ".charness" / "quality" / "history" / "runtime-signals-2026-04.jsonl"
    assert summary_path.exists()
    assert smoothing_path.exists()
    assert archive_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    pytest_entry = summary["commands"]["pytest"]
    assert pytest_entry["samples"] == 2
    assert pytest_entry["passes"] == 1
    assert pytest_entry["failures"] == 1
    assert pytest_entry["latest"]["elapsed_ms"] == 2345
    assert pytest_entry["median_recent_elapsed_ms"] == 1789

    smoothing = json.loads(smoothing_path.read_text(encoding="utf-8"))
    policy = smoothing["policy"]
    assert policy == {
        "kind": "ewma",
        "advisory": True,
        "alpha_base": 0.35,
        "warmup_n": 5,
    }
    smoothed_pytest = smoothing["commands"]["pytest"]
    assert smoothed_pytest["samples"] == 2
    assert smoothed_pytest["alpha_last"] == 0.14
    assert smoothed_pytest["ewma_elapsed_ms"] == 1389.54
    assert smoothed_pytest["advisory"] is True

    archive_lines = archive_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(archive_lines) == 2
    assert json.loads(archive_lines[-1])["runtime_profile"] == "default"


def test_record_quality_runtime_keeps_named_profiles_separate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    for profile, elapsed in (("local-fast", "1200"), ("ci-slow", "9000")):
        result = run_script(
            "scripts/record_quality_runtime.py",
            "--repo-root",
            str(repo),
            "--label",
            "pytest",
            "--elapsed-ms",
            elapsed,
            "--status",
            "pass",
            "--timestamp",
            "2026-04-10T09:00:00Z",
            "--runtime-profile",
            profile,
            cwd=ROOT,
        )
        assert result.returncode == 0, result.stderr

    summary = json.loads((repo / ".charness" / "quality" / "runtime-signals.json").read_text(encoding="utf-8"))
    assert summary.get("commands", {}) == {}
    assert summary["profiles"]["local-fast"]["commands"]["pytest"]["latest"]["elapsed_ms"] == 1200
    assert summary["profiles"]["ci-slow"]["commands"]["pytest"]["latest"]["elapsed_ms"] == 9000


def test_record_quality_runtime_rotates_old_monthly_archives(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    history_dir = repo / ".charness" / "quality" / "history"
    history_dir.mkdir(parents=True)

    for month in range(1, 14):
        result = run_script(
            "scripts/record_quality_runtime.py",
            "--repo-root",
            str(repo),
            "--label",
            "pytest",
            "--elapsed-ms",
            str(1000 + month),
            "--status",
            "pass",
            "--timestamp",
            f"2025-{month:02d}-01T00:00:00Z" if month <= 12 else "2026-01-01T00:00:00Z",
            cwd=ROOT,
        )
        assert result.returncode == 0, result.stderr

    archives = sorted(path.name for path in history_dir.glob("runtime-signals-*.jsonl"))
    assert len(archives) == 12
    assert "runtime-signals-2025-01.jsonl" not in archives
    assert "runtime-signals-2026-01.jsonl" in archives


def test_run_quality_summarizes_success_without_replaying_logs(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown,pytest,check-coverage"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS validate-skills" in result.stdout
    assert "PASS check-markdown" in result.stdout
    assert "PASS pytest" in result.stdout
    assert "PASS check-coverage" in result.stdout
    assert "validate-profiles" not in result.stdout
    assert "quality success output from validate-skills" not in result.stdout
    assert "quality success output from check-markdown" not in result.stdout
    assert "Quality summary: 4 passed, 0 failed" in result.stdout


def test_run_quality_replays_only_failing_command_logs(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown,pytest,check-coverage"
    env["QUALITY_FAIL_LABEL"] = "check-markdown"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "FAIL check-markdown" in result.stdout
    assert "--- check-markdown output ---" in result.stdout
    assert "quality failure output from check-markdown" in result.stdout
    assert "quality success output from validate-skills" not in result.stdout
    assert "Quality summary: 3 passed, 1 failed" in result.stdout


def test_run_quality_can_select_command_docs_gate(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "check-command-docs"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS check-command-docs" in result.stdout
    assert "quality success output from check-command-docs" not in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_can_select_cautilus_proof_gate(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-cautilus-proof"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS validate-cautilus-proof" in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_skips_check_coverage_without_control_plane_changes(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    init_git_repo(repo)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "codex-test@example.com"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS pytest" in result.stdout
    assert "PASS check-coverage" not in result.stdout


def test_run_quality_verbose_replays_success_logs(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-markdown,pytest,check-coverage"
    env["CHARNESS_QUALITY_VERBOSE"] = "1"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "--- validate-skills output ---" in result.stdout
    assert "quality success output from validate-skills" in result.stdout
    assert "--- check-markdown output ---" in result.stdout
    assert "quality success output from check-markdown" in result.stdout
    assert "--- check-coverage output ---" in result.stdout
    assert "quality success output from check-coverage" in result.stdout


def test_run_quality_review_replays_logs_and_enables_online_links(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,check-links-external"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--review", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "--- validate-skills output ---" in result.stdout
    assert "--- check-links-external output ---" in result.stdout
    assert "quality success output from check-links-external" in result.stdout
    assert "link online=1" in result.stdout
    assert "Quality summary: 2 passed, 0 failed" in result.stdout


def test_install_git_hooks_sets_core_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    hookspath = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert hookspath.stdout.strip() == str((repo / ".githooks").resolve())


def test_validate_maintainer_setup_requires_installed_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "validate_maintainer_setup.py", repo / "scripts" / "validate_maintainer_setup.py")
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    missing = subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 1
    assert "install-git-hooks.sh" in missing.stderr

    install = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    ready = subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ready.returncode == 0, ready.stderr
