from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .support import (
    ROOT,
    clone_quality_runner_repo,
    init_git_repo,
    run_script,
    run_shell_script,
    write_executable,
)


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


def _commit_quality_runner_repo(repo: Path, *tracked_paths: str) -> None:
    init_git_repo(repo, *tracked_paths)
    subprocess.run(
        ["git", "config", "user.name", "Codex Test"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)


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


def test_run_quality_uses_repo_local_pytest_temp_root(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    real_python = subprocess.run(
        ["python3", "-c", "import sys; print(sys.executable)"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    log_path = repo / "pytest-invocation.json"
    write_executable(
        repo / "bin" / "python3",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "-m" && "${2:-}" == "pytest" ]]; then',
                "  shift 2",
                '  if [[ "${1:-}" == "--version" ]]; then echo "pytest 9.0.2"; exit 0; fi',
                '  if [[ "${1:-}" == "--help" ]]; then echo "  -n numprocesses, --numprocesses=numprocesses"; exit 0; fi',
                f"  {real_python!r} - <<'PY' \"$PYTEST_DEBUG_TEMPROOT\" \"$@\"",
                "import json",
                "import sys",
                "from pathlib import Path",
                f"Path({str(log_path)!r}).write_text(json.dumps({{'temproot': sys.argv[1], 'args': sys.argv[2:]}}, indent=2) + '\\n', encoding='utf-8')",
                "PY",
                "  echo 'quality success output from pytest'",
                "  exit 0",
                "fi",
                f"exec {real_python!r} \"$@\"",
                "",
            ]
        ),
    )
    env["CHARNESS_QUALITY_LABELS"] = "pytest"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert "/charness/pytest-tmp/" in payload["temproot"]
    assert "--basetemp" in payload["args"]
    assert "-n" in payload["args"]
    assert "auto" in payload["args"]
    assert "tests/charness_cli" in payload["args"]
    basetemp = payload["args"][payload["args"].index("--basetemp") + 1]
    assert basetemp.startswith(payload["temproot"] + "/pytest-of-")
    assert Path(basetemp).name.startswith("pytest-")
    assert not basetemp.endswith("/pytest-0")


def test_run_quality_seed_budget_uses_repo_local_pytest_temp_root(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = repo / "seed-budget-temproot.txt"
    write_executable(
        repo / "scripts" / "check_seed_fixture_budget.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "from pathlib import Path",
                f"Path({str(log_path)!r}).write_text(os.environ['PYTEST_DEBUG_TEMPROOT'] + '\\n', encoding='utf-8')",
                "print('quality success output from check-seed-fixture-budget')",
                "",
            ]
        ),
    )
    env["CHARNESS_QUALITY_LABELS"] = "check-seed-fixture-budget"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "/charness/pytest-tmp/" in log_path.read_text(encoding="utf-8")


def test_run_quality_passes_expanded_targets_to_test_completeness(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    log_path = repo / "test-completeness-targets.json"
    write_executable(
        repo / "scripts" / "check_test_completeness.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "from pathlib import Path",
                f"Path({str(log_path)!r}).write_text(json.dumps(sys.argv[1:]) + '\\n', encoding='utf-8')",
                "print('quality success output from check-test-completeness')",
                "",
            ]
        ),
    )
    env["CHARNESS_QUALITY_LABELS"] = "check-test-completeness"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    args = json.loads(log_path.read_text(encoding="utf-8"))
    assert "tests/test_alpha.py" in args
    assert "tests/test_*.py" not in args


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


def test_run_quality_replays_passing_attention_logs(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    attention_tokens = ("WARNING", "WARN", "WEAK", "ADVISORY")
    for attention_token in attention_tokens:
        repo, env = clone_quality_runner_repo(tmp_path / attention_token.lower(), seeded_quality_runner_repo)
        warning_script = repo / "scripts" / "validate_skill_ergonomics.py"
        warning_script.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "print('quality success output from validate-skill-ergonomics')",
                    f"print('{attention_token}: skill_ergonomics_gate_rules is empty; no skill structure heuristics are enforced.')",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        warning_script.chmod(0o755)
        env["CHARNESS_QUALITY_LABELS"] = "validate-skill-ergonomics"

        result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

        assert result.returncode == 0, result.stderr
        assert "PASS validate-skill-ergonomics" in result.stdout
        assert "--- validate-skill-ergonomics output ---" in result.stdout
        assert f"{attention_token}: skill_ergonomics_gate_rules is empty" in result.stdout
        assert "quality success output from validate-skill-ergonomics" in result.stdout
        assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_surfaces_usage_episode_report(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    report_script = repo / "scripts" / "report_usage_episodes.py"
    report_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "print('ADVISORY: usage episode report is an engineering signal, not product-success proof.')",
                "print('Usage episodes: 4 record(s) across 3 session group(s).')",
                "print('Capture gaps: ungrouped=2, missing_feedback=1, single_entry_point_only=True, explicit_request_only=True.')",
                "print('Non-claims:')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    report_script.chmod(0o755)
    env["CHARNESS_QUALITY_LABELS"] = "report-usage-episodes"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS report-usage-episodes" in result.stdout
    assert "--- report-usage-episodes output ---" in result.stdout
    assert "Usage episodes: 4 record(s) across 3 session group(s)." in result.stdout
    assert "Capture gaps: ungrouped=2" in result.stdout
    assert "not product-success proof" in result.stdout


def test_run_quality_keeps_passing_non_attention_logs_quiet(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    warning_script = repo / "scripts" / "validate_skill_ergonomics.py"
    warning_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "print('quality success output from validate-skill-ergonomics')",
                "print('NOTE: skill_ergonomics_gate_rules is empty; this is an ordinary note.')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    warning_script.chmod(0o755)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skill-ergonomics"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS validate-skill-ergonomics" in result.stdout
    assert "--- validate-skill-ergonomics output ---" not in result.stdout
    assert "NOTE: skill_ergonomics_gate_rules is empty" not in result.stdout
    assert "quality success output from validate-skill-ergonomics" not in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_can_select_cautilus_proof_gate(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-cautilus-proof"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS validate-cautilus-proof" in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_can_select_agent_browser_runtime_hygiene(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "agent-browser-runtime-baseline,agent-browser-runtime-hygiene"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS agent-browser-runtime-baseline" in result.stdout
    assert "PASS agent-browser-runtime-hygiene" in result.stdout
    assert "Quality summary: 2 passed, 0 failed" in result.stdout


def test_run_quality_skips_agent_browser_runtime_hygiene_by_default(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "agent-browser-runtime-baseline" not in result.stdout
    assert "agent-browser-runtime-hygiene" not in result.stdout
    assert "PASS validate-skills" in result.stdout


def test_run_quality_default_full_skips_agent_browser_runtime_hygiene(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "agent-browser-runtime-baseline" not in result.stdout
    assert "agent-browser-runtime-hygiene" not in result.stdout


def test_run_quality_runtime_hygiene_env_forces_agent_browser_gate(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    env["CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE"] = "1"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS agent-browser-runtime-baseline" in result.stdout
    assert "PASS agent-browser-runtime-hygiene" in result.stdout
    assert "PASS validate-skills" in result.stdout


def test_run_quality_stops_when_agent_browser_runtime_baseline_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "agent-browser-runtime-baseline,validate-skills"
    env["QUALITY_FAIL_LABEL"] = "agent-browser-runtime-baseline"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "FAIL agent-browser-runtime-baseline" in result.stdout
    assert "validate-skills" not in result.stdout
    assert "Quality summary: 0 passed, 1 failed" in result.stdout
    assert "agent-browser runtime baseline failed" in result.stderr


def test_run_quality_runtime_barriers_ignore_orphan_waiver_env(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "agent-browser-runtime-baseline,agent-browser-runtime-hygiene"
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"
    env["QUALITY_REQUIRE_STRICT_ORPHANS_LABEL"] = "agent-browser-runtime-hygiene"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS agent-browser-runtime-baseline" in result.stdout
    assert "PASS agent-browser-runtime-hygiene" in result.stdout


def test_run_quality_cleans_agent_browser_runtime_after_hygiene_failure(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    cleanup_log = repo / "cleanup.log"
    guard = repo / "scripts" / "agent_browser_runtime_guard.py"
    guard.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "import sys",
                "from pathlib import Path",
                "args = sys.argv[1:]",
                f"cleanup_log = Path({str(cleanup_log)!r})",
                "if '--cleanup-orphans' in args and '--execute' in args:",
                "    cleanup_log.write_text('cleanup executed\\n', encoding='utf-8')",
                "    sys.exit(0)",
                "if os.environ.get('QUALITY_FAIL_LABEL') == 'agent-browser-runtime-hygiene':",
                "    print('quality failure output from agent-browser-runtime-hygiene')",
                "    sys.exit(1)",
                "print('quality success output from agent-browser-runtime-hygiene')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    guard.chmod(0o755)
    env["CHARNESS_QUALITY_LABELS"] = "agent-browser-runtime-hygiene"
    env["QUALITY_FAIL_LABEL"] = "agent-browser-runtime-hygiene"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "FAIL agent-browser-runtime-hygiene" in result.stdout
    assert "quality failure output from agent-browser-runtime-hygiene" in result.stdout
    assert cleanup_log.read_text(encoding="utf-8") == "cleanup executed\n"


def test_run_quality_enforces_ci_local_gate_parity_inventory(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    inventory_script = repo / "skills" / "public" / "quality" / "scripts" / "inventory_ci_local_gate_parity.py"
    inventory_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if '--require-empty-parity-issues' not in sys.argv:",
                "    print('missing --require-empty-parity-issues')",
                "    sys.exit(1)",
                "print('quality success output from inventory-ci-local-gate-parity')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    inventory_script.chmod(0o755)
    env["CHARNESS_QUALITY_LABELS"] = "inventory-ci-local-gate-parity"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS inventory-ci-local-gate-parity" in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_enforces_gitignore_scan_hygiene_inventory(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    inventory_script = (
        repo / "skills" / "public" / "quality" / "scripts" / "inventory_gitignore_scan_hygiene.py"
    )
    inventory_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if '--require-empty' not in sys.argv:",
                "    print('missing --require-empty')",
                "    sys.exit(1)",
                "print('quality success output from inventory-gitignore-scan-hygiene')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    inventory_script.chmod(0o755)
    env["CHARNESS_QUALITY_LABELS"] = "inventory-gitignore-scan-hygiene"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS inventory-gitignore-scan-hygiene" in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_enforces_current_pointer_write_scan(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "check-current-pointer-writes"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "PASS check-current-pointer-writes" in result.stdout
    assert "Quality summary: 1 passed, 0 failed" in result.stdout


def test_run_quality_read_only_skips_check_coverage_without_control_plane_changes(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    (repo / "README.md").write_text("# demo\n\nnon coverage change\n", encoding="utf-8")

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

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

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

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

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

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


def test_run_quality_full_surfaces_planted_check_coverage_regression(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    _commit_quality_runner_repo(repo)
    env["QUALITY_FAIL_LABEL"] = "check-coverage"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)
    assert result.returncode != 0
    assert "FAIL check-coverage" in result.stdout
    assert "quality failure output from check-coverage" in result.stdout


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
    shutil.copy2(ROOT / ".githooks" / "pre-commit", repo / ".githooks" / "pre-commit")
    shutil.copy2(ROOT / ".githooks" / "commit-msg", repo / ".githooks" / "commit-msg")
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


def test_install_git_hooks_materializes_consumer_commit_msg_hook(tmp_path: Path) -> None:
    source = tmp_path / "source"
    consumer = tmp_path / "consumer"
    (source / "scripts").mkdir(parents=True)
    (consumer / ".git").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", source / "scripts" / "install-git-hooks.sh")
    checker = source / "scripts" / "check_issue_closeout_commit_msg.py"
    checker.write_text("#!/usr/bin/env python3\nprint('checker')\n", encoding="utf-8")
    checker.chmod(0o755)
    subprocess.run(["git", "init"], cwd=consumer, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["bash", str(source / "scripts" / "install-git-hooks.sh"), "--repo-root", str(consumer)],
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    hook = consumer / ".githooks" / "commit-msg"
    assert hook.is_file()
    assert str(checker) in hook.read_text(encoding="utf-8")
    hookspath = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=consumer,
        check=True,
        capture_output=True,
        text=True,
    )
    assert hookspath.stdout.strip() == str((consumer / ".githooks").resolve())


def test_validate_maintainer_setup_requires_installed_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "validate_maintainer_setup.py", repo / "scripts" / "validate_maintainer_setup.py")
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-commit", repo / ".githooks" / "pre-commit")
    shutil.copy2(ROOT / ".githooks" / "commit-msg", repo / ".githooks" / "commit-msg")
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


def test_every_queued_repo_script_gate_has_a_seeded_harness_stub() -> None:
    """Drift guard: a gate queued in run-quality.sh must exist in the seeded
    harness repo, or four runner tests fail at the broad boundary instead of
    the slice loop (the failure class this pins)."""
    import re

    from .support import QUALITY_PYTHON_STUBS

    runner = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    queued = set(re.findall(r'queue_selected "[^"]+" python3 scripts/([a-z0-9_]+\.py)', runner))
    stubbed = {name for _, name in QUALITY_PYTHON_STUBS}
    copied_real_scripts = {"run_standing_pytest.py"}
    missing = sorted(queued - stubbed - copied_real_scripts)
    assert missing == [], (
        "run-quality.sh queues repo-script gates with no seeded harness stub; "
        f"add them to QUALITY_PYTHON_STUBS in tests/quality_gates/support.py: {missing}"
    )
