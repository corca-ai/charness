"""Per-lane no-progress budgets for task-run lanes (#835).

Contract-heavy lanes get a visible `--no-progress-seconds` choice recorded in
`progress_guard` instead of an env-only kill; the guard also snapshots the
first scoped diff so a later self-revert stays recoverable.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run_progress as prog
from tests.charness_cli.test_task_run_fixtures import _codex, _git, _repo


def test_no_progress_flag_overrides_env_and_records_source(
    monkeypatch, tmp_path: Path
) -> None:
    """An explicit --no-progress-seconds wins over the env and is recorded (#835)."""
    monkeypatch.setenv(prog.NO_PROGRESS_BUDGET_ENV, "300")
    watch = prog.build_progress_watch(
        require_change=True,
        stdout_log=tmp_path / "o.log",
        stderr_log=tmp_path / "e.log",
        worktree=tmp_path,
        base_sha="deadbeef",
        scope_specs=[],
        budget_override=1200.0,
    )
    assert watch is not None
    receipt = watch.receipt()
    assert receipt["budget_seconds"] == 1200.0
    assert receipt["budget_source"] == "flag"


def test_no_progress_seconds_rejects_nonfinite_and_negative(tmp_path: Path) -> None:
    from scripts.task_run import task_run_plan

    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    import pytest

    # A self-made executable keeps this test off ambient PATH (#825).
    fake_bin = tmp_path / "fakebin"
    fake_bin.mkdir(exist_ok=True)
    executable = _codex(fake_bin, "exit 0")

    for bad in ("nan", "-5", "inf", "not-a-number", object()):
        with pytest.raises(task_run_plan.TaskRunError, match="no-progress-seconds"):
            task_run_plan.resolve_task_inputs(
                repo,
                target_path=tmp_path / "lane",
                branch="lane/bad-budget",
                base=base_sha,
                lane=None,
                scopes=["module.py"],
                prompt="update the module",
                codex=str(executable),
                executor="codex",
                effort="medium",
                task_id="bad-budget",
                prepare=False,
                require_change=True,
                skip_prepare=False,
                allow_no_change=False,
                timeout_seconds=60,
                report_only=False,
                no_progress_seconds=bad,
            )
    for good, expected in (("1200", 1200.0), (0, 0.0), (None, None)):
        resolved = task_run_plan.resolve_task_inputs(
            repo,
            target_path=tmp_path / "lane",
            branch="lane/good-budget",
            base=base_sha,
            lane=None,
            scopes=["module.py"],
            prompt="update the module",
            codex=str(executable),
            executor="codex",
            effort="medium",
            task_id="good-budget",
            prepare=False,
            require_change=True,
            skip_prepare=False,
            allow_no_change=False,
            timeout_seconds=60,
            report_only=False,
            no_progress_seconds=good,
        )
        assert resolved["no_progress_seconds"] == expected


def test_guard_snapshots_first_scoped_diff_once(tmp_path: Path) -> None:
    """The guard keeps the first scoped diff for a later self-revert (#834)."""
    from scripts.task_run import task_run_scope

    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)

    def _watch_for(worktree: Path) -> prog.LaneProgressWatch:
        return prog.LaneProgressWatch(
            stdout_log=tmp_path / "o.log",
            stderr_log=tmp_path / "e.log",
            worktree=worktree,
            base_sha=base_sha,
            scope_specs=specs,
            budget_seconds=300.0,
            poll_seconds=15.0,
        )

    watch = _watch_for(repo)
    watch._maybe_snapshot_scoped_diff(100.0)
    assert watch.receipt()["first_scoped_diff"]["observed"] is False

    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    watch._maybe_snapshot_scoped_diff(101.0)
    snapshot = watch.receipt()["first_scoped_diff"]
    assert snapshot["observed"] is True
    assert snapshot["changed_paths"] == ["module.py"]
    assert "VALUE = 2" in (snapshot["diff"] or "")
    assert snapshot["truncated"] is False

    (repo / "module.py").write_text("VALUE = 3\n", encoding="utf-8")
    watch._maybe_snapshot_scoped_diff(102.0)
    resnapshot = watch.receipt()["first_scoped_diff"]
    assert "VALUE = 3" not in (resnapshot["diff"] or "")

    missing = _watch_for(tmp_path / "no-such-worktree")
    missing._maybe_snapshot_scoped_diff(103.0)
    assert missing.receipt()["first_scoped_diff"]["observed"] is False


def test_guard_snapshot_truncates_large_diffs(tmp_path: Path) -> None:
    from scripts.task_run import task_run_scope

    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    (repo / "module.py").write_text("X = 1\n" * 20000, encoding="utf-8")
    watch = prog.LaneProgressWatch(
        stdout_log=tmp_path / "o.log",
        stderr_log=tmp_path / "e.log",
        worktree=repo,
        base_sha=base_sha,
        scope_specs=specs,
        budget_seconds=300.0,
        poll_seconds=15.0,
    )
    watch._maybe_snapshot_scoped_diff(100.0)
    snapshot = watch.receipt()["first_scoped_diff"]
    assert snapshot["observed"] is True
    assert snapshot["truncated"] is True


def test_bad_budget_reports_itself_without_executables(
    monkeypatch, tmp_path: Path
) -> None:
    """Input validation precedes PATH probing (#825).

    With no executor executable installed, a bad --no-progress-seconds must
    still report itself instead of a "not on PATH" error. Deliberately uses
    the ambient ``codex`` name so the ordering, not a fake, is exercised.
    """
    from scripts.task_run import task_run_plan

    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    import pytest

    with pytest.raises(task_run_plan.TaskRunError, match="no-progress-seconds"):
        task_run_plan.resolve_task_inputs(
            repo,
            target_path=tmp_path / "lane",
            branch="lane/no-exec-budget",
            base=base_sha,
            lane=None,
            scopes=["module.py"],
            prompt="update the module",
            codex="codex",
            executor="codex",
            effort="medium",
            task_id="no-exec-budget",
            prepare=False,
            require_change=True,
            skip_prepare=False,
            allow_no_change=False,
            timeout_seconds=60,
            report_only=False,
            no_progress_seconds="nan",
        )
