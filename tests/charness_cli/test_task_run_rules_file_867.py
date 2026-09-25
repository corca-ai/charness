"""Task-run standing rules by reference and dry-run refusal parity (#867)."""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run, task_run_lane_runner, task_run_state

from .test_task_run_fixtures import _codex, _git, _repo


def _rules_file(tmp_path: Path) -> Path:
    """Standing material naming dozens of repository-shaped paths."""
    paths = [
        "scripts/task_run/task_run.py",
        "scripts/task_run/task_run_scope.py",
        "scripts/hooks/host_hook_registry.py",
        "tests/charness_cli/test_task_run_scope.py",
        "docs/agent-task-runs.md",
        "plugins/charness/skills/issue/SKILL.md",
    ]
    content = "".join(f"see `{path}` before editing\n" for path in paths * 4)
    rules = tmp_path / "lane-rules.md"
    rules.write_text(content, encoding="utf-8")
    return rules


def _dry_run(repo: Path, tmp_path: Path, prompt: str, **kwargs) -> dict:
    executable = _codex(tmp_path, "exit 0")
    return task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/rules-dry-run",
        base="HEAD",
        scopes=["module.py"],
        prompt=prompt,
        codex=str(executable),
        effort="medium",
        dry_run=True,
        **kwargs,
    )


def _exit_code(payload: dict) -> int:
    return task_run_state.exit_code_for_result_kind(
        task_run_state.result_kind_for_receipt(payload)
    )


def test_rules_file_content_stays_outside_scope_evidence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    rules = _rules_file(tmp_path)

    payload = _dry_run(repo, tmp_path, "update the module", rules_files=[rules])

    assert payload["status"] == "pass", payload
    assert payload["scope_preflight"]["would_touch_outside_declared"] == []
    assert payload["rules_files"] == [str(rules.resolve())]
    assert _exit_code(payload) == 0


def test_executor_prompt_lists_rules_paths_not_content(tmp_path: Path) -> None:
    rules = _rules_file(tmp_path)
    content = rules.read_text(encoding="utf-8")

    shaped = task_run_lane_runner.build_lane_prompt(
        "update the module",
        require_change=True,
        scopes=["module.py"],
        rules_files=[str(rules.resolve())],
    )

    assert "Read these in full before any edit; they bind this lane" in shaped
    assert str(rules.resolve()) in shaped
    assert "see `scripts/task_run/task_run.py` before editing" not in shaped
    assert content not in shaped


def test_dry_run_reports_out_of_scope_refusal(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(
        repo, tmp_path, "fix the helper in scripts/task_run/task_run.py"
    )

    outside = payload["scope_preflight"]["would_touch_outside_declared"]
    assert [finding["path"] for finding in outside] == [
        "scripts/task_run/task_run.py"
    ]
    assert payload["status"] == "premise-blocked", payload
    assert "scripts/task_run/task_run.py" in payload["error"]
    assert _exit_code(payload) == 2
    assert not (tmp_path / "lane").exists()


def test_dry_run_clean_prompt_plans_with_zero_exit(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _git(repo, "rev-parse", "HEAD")

    payload = _dry_run(repo, tmp_path, "inspect the selected base")

    assert payload["status"] == "pass", payload
    assert _exit_code(payload) == 0


def test_rules_file_missing_path_is_a_preflight_failure(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    payload = _dry_run(
        repo, tmp_path, "update the module", rules_files=[tmp_path / "absent.md"]
    )

    assert payload["status"] == "fail", payload
    assert "--rules-file is not a file" in payload["error"]
