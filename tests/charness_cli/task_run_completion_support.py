"""Shared real-Git fixture for task completion tests."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts.task_run import task_run_carrier, task_run_completion, task_run_git, task_run_scope
from tests.quality_gates.repo_shapes import install_committed_repo


def _prepare_mixed_merge_delete_candidate(target: Path) -> None:
    def checked_git(*args: str) -> None:
        result = task_run_git._git(target, *args)
        if result.returncode != 0:
            raise AssertionError(result.stderr)

    checked_git("checkout", "-b", "lane-work")
    checked_git("checkout", "main")
    (target / "pkg").mkdir()
    (target / "pkg" / "item.py").write_text("VALUE = 1\n", encoding="utf-8")
    task_run_git._commit_lane_snapshot(target, message="target adds item")
    checked_git("checkout", "lane-work")
    checked_git(
        "-c",
        "user.email=charness-task-run@localhost",
        "-c",
        "user.name=charness task run",
        "merge",
        "--no-ff",
        "--no-edit",
        "main",
    )
    removed = task_run_git._git(target, "rm", "--", "pkg/item.py")
    if removed.returncode != 0:
        raise AssertionError(removed.stderr)
    task_run_git._commit_lane_snapshot(target, message="lane deletes item")
    (target / "module.py").write_text("VALUE = 2\n", encoding="utf-8")


def _fixture_completion_evidence(
    *,
    candidate_kind: str,
    candidate: dict[str, Any],
    carrier: dict[str, Any],
    target: Path,
    base_sha: str,
    scope_specs: list[dict[str, Any]],
    scope_verdict: str,
    parent_progress: dict[str, Any],
    require_change: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if candidate_kind == "mixed-merge-delete":
        scope = task_run_scope._scope_result(
            target, base_sha, scope_specs, require_change
        )
        candidate["disallowed_paths"] = scope["disallowed_paths"]
    else:
        scope = {
            "verdict": scope_verdict,
            "reason": "scope drifted",
            "changed_paths": carrier["changed_paths"],
            "candidate_carrier": carrier,
        }
    evidence = {"populations": {}, "scope": scope}
    return evidence, scope, parent_progress


def _complete(
    tmp_path: Path,
    *,
    candidate_kind: str = "clean",
    result_state: str | None = None,
    scope_verdict: str = "pass",
    changed_line_gate: Any = None,
    execution_state: str = "completed",
    parent_blocking: bool = False,
    git: Any = None,
    persist_events: list[str] | None = None,
    carrier_override: dict[str, Any] | None = None,
    scope_specs_override: list[dict[str, Any]] | None = None,
    prelaunch_plan_override: dict[str, Any] | None = None,
    extra_files: dict[str, str] | None = None,
    delete_path: str | None = None,
) -> dict[str, Any]:
    mapped_suite = "tests/test_completion_scope.py"
    surface_manifest = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "completion-fixture",
                    "description": "Fixture verifier mapping for task completion tests.",
                    "source_paths": ["module.py"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": [f"python3 -m pytest -q {mapped_suite}"],
                    "notes": [],
                }
            ],
        }
    )
    files = {
        "module.py": "VALUE = 1\n",
        ".agents/surfaces.json": surface_manifest,
        mapped_suite: "def test_completion_scope():\n    assert True\n",
        **(extra_files or {}),
    }
    target = install_committed_repo(
        tmp_path / "worktree",
        files,
    )
    base_sha = task_run_git._git_output(target, "rev-parse", "HEAD").strip()
    if candidate_kind == "clean":
        (target / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
        task_run_git._commit_lane_snapshot(target, message="test candidate")
    elif candidate_kind == "dirty":
        (target / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    elif candidate_kind == "delete":
        if not delete_path:
            raise AssertionError("delete candidates need a path")
        removed = task_run_git._git(target, "rm", "--", delete_path)
        if removed.returncode != 0:
            raise AssertionError(removed.stderr)
        task_run_git._commit_lane_snapshot(target, message="delete mapped file")
    elif candidate_kind == "mixed-merge-delete":
        _prepare_mixed_merge_delete_candidate(target)
    elif candidate_kind != "absent":
        raise AssertionError(f"unknown candidate fixture: {candidate_kind}")
    branch = task_run_git._git_output(target, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
    carrier = task_run_carrier._candidate_carrier(target, base_sha, branch=branch)
    if carrier_override is not None:
        carrier = {**carrier, **carrier_override}
    useful = candidate_kind != "absent"
    candidate = {
        "status": "validated" if useful else "absent",
        "useful": useful,
        **carrier,
        # Production candidates always carry the verdict's denied set (possibly
        # empty); the fixture states it explicitly so the persist path classifies
        # exactly what production classifies.
        "disallowed_paths": [],
    }
    if result_state is None:
        result_state = "validated-partial-result" if parent_blocking else "completed"
    prelaunch_plan = prelaunch_plan_override if prelaunch_plan_override is not None else {
        "scope_preflight": {"required_scope_paths": []},
        "scope_verifiers": {
            "status": "configured",
            "bundle_status": "repo-owned-bundle",
            "scope_paths": ["module.py"],
            "unmatched_paths": [],
            "mapped_suites": [mapped_suite],
        },
    }
    parent_progress = {
        "blocking": parent_blocking,
        "classification": "writer-conflict" if parent_blocking else "no-parent-progress",
    }

    def default_git(cwd: Path, *args: str) -> Any:
        if args[:2] == ("worktree", "remove"):
            return SimpleNamespace(returncode=1, stdout="", stderr="not removing the unit fixture")
        if persist_events is not None and "commit" in args:
            persist_events.append("persist-commit")
        return task_run_git._git(cwd, *args)

    return task_run_completion.complete_task(
        {
            "task_id": "lane-1",
            "target_branch": branch,
            "base_sha": base_sha,
            "prelaunch_plan": prelaunch_plan,
        },
        runtime_path=tmp_path / "runtime",
        resolved_target=target,
        resolved_repo=target,
        before_exec={},
        base_sha=base_sha,
        scope_specs=scope_specs_override or [],
        require_change=False,
        parent_before={},
        parent_before_head=base_sha,
        stdout_log=tmp_path / "stdout.log",
        execution={},
        started_at=0.0,
        persist=lambda _payload, _path: None,
        result_delivery=lambda _log: {"status": "delivered"},
        completion_evidence=lambda **kwargs: _fixture_completion_evidence(
            candidate_kind=candidate_kind,
            candidate=candidate,
            carrier=carrier,
            target=target,
            base_sha=base_sha,
            scope_specs=scope_specs_override or [],
            scope_verdict=scope_verdict,
            parent_progress=parent_progress,
            require_change=kwargs["require_change"],
        ),
        execution_state=lambda _execution, _delivery: execution_state,
        candidate_result_state=lambda **_kwargs: (candidate, result_state),
        candidate_commit=None,
        git=git or default_git,
        git_output=task_run_git._git_output,
        pass_value="pass",
        changed_line_gate=changed_line_gate,
    )
