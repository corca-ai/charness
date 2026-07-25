from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module
from scripts.run_standing_pytest import choose_xdist_workers

from .support import (
    ROOT,
    clone_quality_runner_repo,
    run_shell_script,
    write_executable,
)


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


def test_quality_runner_clones_do_not_contaminate_each_other_or_the_module_seed(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    first_clone, _ = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    runner_path = Path("scripts/run-quality.sh")
    first_clone_runner = first_clone / runner_path
    original_runner = first_clone_runner.read_text(encoding="utf-8")
    first_clone_runner.write_text("mutated first clone\n", encoding="utf-8")

    second_root = tmp_path / "second-clone"
    second_root.mkdir()
    second_clone, _ = clone_quality_runner_repo(second_root, seeded_quality_runner_repo)

    assert (second_clone / runner_path).read_text(encoding="utf-8") == original_runner
    assert (seeded_quality_runner_repo / runner_path).read_text(encoding="utf-8") == original_runner


def test_dead_code_advisory_gate_is_default_off(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    # Default-off: a normal run (no opt-in env var, label set that does not name it)
    # must NOT queue the vulture-backed dead-code advisory.
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "dead-code-advisory" not in result.stdout


def test_dead_code_advisory_gate_runs_when_opted_in_via_env(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    # Opt-in via env var runs it regardless of label scoping (mirrors the
    # agent-browser-runtime gate) and it is advisory — the run stays green.
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    env["CHARNESS_QUALITY_DEAD_CODE"] = "1"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS dead-code-advisory" in result.stdout


def test_dead_code_advisory_gate_runs_when_explicitly_labeled(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    # The triage-follow-up entry point: name only this gate to run just it.
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "dead-code-advisory"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS dead-code-advisory" in result.stdout


def test_run_quality_uses_repo_local_pytest_temp_root(tmp_path: Path, seeded_quality_runner_repo: Path) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    real_python = sys.executable
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
    # core-relative: assert the worker count run_standing_pytest actually computes
    # for THIS machine (min(cpu_count, cap)) rather than a hardcoded "16" that only
    # holds on a >=16-core box — CI runners with fewer cores compute a smaller -n
    # and were failing this assertion while the runner behaved correctly.
    assert choose_xdist_workers(env) in payload["args"]
    assert "tests/charness_cli" in payload["args"]
    basetemp = payload["args"][payload["args"].index("--basetemp") + 1]
    assert basetemp.startswith(payload["temproot"] + "/pytest-of-")
    # The leaf must NOT be a "pytest-*" dir: it shares pytest-of-<user> with nested
    # pytest runs whose exit-time cleanup deletes unlocked "pytest-*" dirs, and this
    # explicit basetemp carries no cleanup lock (see test_standing_pytest_runner.py).
    assert Path(basetemp).name.startswith("charness-run-")
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
    assert "Non-claims:" in result.stdout


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
    # A gate wrapped in `bash -c` can still call a repo script, and the pattern above
    # cannot see it -- the specdown step is exactly that shape, and its seeding had to
    # be remembered by hand, which is the forgetting this guard exists to prevent.
    for line in runner.splitlines():
        if "queue_selected" not in line:
            continue
        for path in re.findall(r'([\w$/{}.-]*scripts/[a-z0-9_]+\.py)', line):
            prefix, _, name = path.rpartition("scripts/")
            # Repo-root scripts only. Skill-package gates (skills/public/quality/scripts)
            # come from QUALITY_RUNTIME_STUBS and are seeded elsewhere.
            if prefix in ("", "$REPO_ROOT/"):
                queued.add(name)
    stubbed = {name for _, name in QUALITY_PYTHON_STUBS}
    copied_real_scripts = {"run_standing_pytest.py", "specdown_ephemeral_config.py"}
    missing = sorted(queued - stubbed - copied_real_scripts)
    assert missing == [], (
        "run-quality.sh queues repo-script gates with no seeded harness stub; "
        f"add them to QUALITY_PYTHON_STUBS in tests/quality_gates/support.py: {missing}"
    )


def test_quality_runner_keeps_specdown_reports_out_of_the_worktree() -> None:
    """This test used to grep the runner for `specdown run -jobs 4 -out` and pass --
    while every quality run dirtied the tracked `.charness/specdown/report.json`.
    `-out` redirects only the HTML directory; the JSON reporter's destination lives
    in `specdown.json`, so the flag the test pinned never controlled the file the
    test is named after. Assert the redirect that actually decides it: the runner
    must pass a `-config`, and the config that helper produces must point every
    reporter outside the repo."""
    runner = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    specdown_command = next(line for line in runner.splitlines() if 'queue_selected "specdown"' in line)

    # Unescape the nested `bash -c` quoting so the assertions can bind the flag to
    # the variable. Asserting `-config` is merely PRESENT would still pass if the
    # runner passed the repo's own specdown.json -- the same assert-the-proxy hole
    # this test is being repaired for.
    unescaped = specdown_command.replace("\\", "")
    assert 'queue_selected "specdown" bash -c' in specdown_command
    assert 'specdown_config=$(python3 "$REPO_ROOT/scripts/specdown_ephemeral_config.py"' in unescaped
    assert 'specdown run -config "$specdown_config"' in unescaped
    assert "RUN_QUALITY_TMPDIR/specdown-report" in specdown_command
    # Removed on 2026-07-22 because specdown rejects them; keep them gone.
    assert "-quiet" not in specdown_command
    assert "-no-report" not in specdown_command


def test_specdown_ephemeral_config_redirects_every_reporter_out_of_the_repo(tmp_path: Path) -> None:
    """The behavioural half of the guard above: whatever `specdown.json` declares,
    the generated config must not leave a reporter writing into the repo. Driven off
    the real checked-in config so a newly added reporter is covered without anyone
    remembering to update a fixture."""
    helper = import_repo_module(
        ROOT / "scripts" / "specdown_ephemeral_config.py", "scripts.specdown_ephemeral_config"
    )
    source = json.loads((ROOT / "specdown.json").read_text(encoding="utf-8"))
    assert source.get("reporters"), "fixture assumes the repo config declares reporters"

    config = helper.build_ephemeral_config(source, tmp_path)

    for reporter in config["reporters"]:
        assert "outFile" in reporter, (
            f"reporter {reporter} declares no outFile, so specdown picks the default -- "
            "which may be repo-relative. Decide that destination explicitly."
        )
        out_file = Path(reporter["outFile"])
        assert out_file.is_absolute(), reporter
        assert out_file.is_relative_to(tmp_path), reporter
        assert not out_file.is_relative_to(ROOT), reporter
    # `entry` must stay relative: specdown resolves it against the config file's own
    # directory, so absolutising it would send specdown looking in the wrong place.
    assert config["entry"] == source["entry"]
    assert not Path(config["entry"]).is_absolute()


def test_quality_runner_leaves_no_specdown_state_in_the_worktree(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """The property the two guards above only approximate, observed directly: after a
    real runner invocation the repo must carry neither a rewritten specdown report nor
    a leftover ephemeral config, and the config specdown was actually handed must
    point its reporters outside the repo. A `-config` flag pointing at the repo's own
    specdown.json passes every string assertion and fails this one."""
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    tracked_report = repo / ".charness" / "specdown" / "report.json"
    tracked_report.parent.mkdir(parents=True, exist_ok=True)
    tracked_report.write_text('{"generatedAt": "sentinel"}\n', encoding="utf-8")
    argv_log = tmp_path / "specdown-argv.log"

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--read-only",
        cwd=repo,
        env={**env, "SPECDOWN_ARGV_LOG": str(argv_log)},
    )

    assert result.returncode == 0, result.stdout
    assert tracked_report.read_text(encoding="utf-8") == '{"generatedAt": "sentinel"}\n'
    assert not (repo / ".specdown.ephemeral.json").exists(), "ephemeral config was not cleaned up"

    argv = argv_log.read_text(encoding="utf-8").split()
    config_path = Path(argv[argv.index("-config") + 1])
    assert config_path.name == ".specdown.ephemeral.json"
    handed = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else None
    if handed is None:
        # Cleaned up by the trap, which is the point; reconstruct what it contained.
        helper = import_repo_module(
            ROOT / "scripts" / "specdown_ephemeral_config.py", "scripts.specdown_ephemeral_config"
        )
        source = json.loads((repo / "specdown.json").read_text(encoding="utf-8"))
        handed = helper.build_ephemeral_config(source, tmp_path / "out")
    for reporter in handed["reporters"]:
        assert not Path(reporter["outFile"]).is_relative_to(repo), reporter
