"""Typed failure terminals of `run_task` the standing suite never executed.

Issue #825: the scheduled mutation run kept a 100% score but failed on its
blocking signal, 67 sampled mutants whose lines the mapped tests never
execute. The changed-line gate was clean, so the repair is coverage, not
sampling. The arms live here instead of `test_task_run.py` because that
module is at the test-file length cap: creation-failure handlers, the
failed-WIP-checkpoint terminal, the persisted-for-review completion
branches, and the flat-layout import fallback.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_execution, task_run_runtime
from tests.module_eviction import evict_module, evict_new_modules
from tests.script_loader import load_script_module

from .test_task_run_fixtures import _codex, _repo, _run


def _with_liveness(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "liveness": task_run_runtime.runner_liveness(payload)}


def test_worktree_create_keyboard_interrupt_persists_interrupted_result(
    tmp_path: Path, monkeypatch
) -> None:
    """An interrupt during worktree creation is a typed interrupt, not a crash."""
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    def interrupt_create(*_args, **_kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(task_run._worktree, "run_create", interrupt_create)
    payload = _run(repo, tmp_path, executable, task_id="create-interrupt")

    assert payload["status"] == "interrupted"
    assert payload["phase"] == "terminal"
    assert payload["next_step"] == (
        "Task creation was interrupted; inspect the target path before retrying with a fresh path."
    )
    assert task_run.task_status(repo, "create-interrupt") == _with_liveness(payload)


@pytest.mark.parametrize(
    "error_type", [OSError, RuntimeError, subprocess.SubprocessError]
)
def test_worktree_create_error_persists_failed_result(
    tmp_path: Path, monkeypatch, error_type
) -> None:
    """Every creation-error shape the handler names reaches the same terminal."""
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    def fail_create(*_args, **_kwargs):
        raise error_type("disk gone")

    monkeypatch.setattr(task_run._worktree, "run_create", fail_create)
    payload = _run(repo, tmp_path, executable, task_id="create-error")

    assert payload["status"] == "failed"
    assert payload["phase"] == "terminal"
    assert payload["error"] == "disk gone"
    assert payload["next_step"] == (
        "Task worktree creation failed; inspect the error and retry with a fresh path."
    )
    assert task_run.task_status(repo, "create-error") == _with_liveness(payload)


def test_worktree_create_refusal_uses_the_default_next_step(
    tmp_path: Path, monkeypatch
) -> None:
    """A refusal without its own next step still tells the operator what to fix."""
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    monkeypatch.setattr(
        task_run._worktree, "run_create", lambda *args, **kwargs: {"created": False}
    )
    payload = _run(repo, tmp_path, executable, task_id="create-refusal")

    assert payload["status"] == "failed"
    assert payload["phase"] == "terminal"
    assert payload["next_step"] == "Fix worktree creation/doctor, then rerun task run."
    assert task_run.task_status(repo, "create-refusal") == _with_liveness(payload)


@pytest.mark.parametrize(
    "error",
    [
        OSError("disk gone"),
        RuntimeError("boom"),
        TypeError("bad type"),
        task_run.TaskRunError("checkpoint refused"),
        subprocess.SubprocessError("proc failed"),
    ],
)
def test_failed_wip_checkpoint_persists_unknown_mid_edit_candidate(
    tmp_path: Path, monkeypatch, error
) -> None:
    """A checkpoint that cannot commit leaves an explicitly unknown WIP candidate.

    Each named error shape takes the same arm, so the stranded worktree reads as
    `interrupted-mid-edit` with a failed commit rather than as a silent loss.
    """
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")
    execution = {"timed_out": True, "interrupted": False, "exit_code": None}

    monkeypatch.setattr(
        task_run._progress,
        "_execute_watched_lane",
        lambda *args, **kwargs: dict(execution),
    )

    def fail_checkpoint(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(
        task_run._lane_runner, "_checkpoint_interrupted_lane", fail_checkpoint
    )
    payload = _run(repo, tmp_path, executable, task_id="wip-checkpoint-failure")

    assert payload["status"] == "timed-out"
    assert payload["phase"] == "terminal"
    assert payload["execution"] == {**execution, "status": "timed-out"}
    assert payload["candidate"] == {
        "status": "wip",
        "useful": False,
        "changed_paths": [],
        "state": "interrupted-mid-edit",
        "state_known": False,
        "commit": {
            "status": "failed",
            "error": str(error),
            "correctness_verified": False,
        },
    }
    assert payload["error"] == f"timed-out WIP candidate commit failed: {error}"
    assert payload["next_step"] == (
        "The timed-out WIP checkpoint could not be committed; inspect and "
        "recover the retained worktree manually."
    )
    assert task_run.task_status(repo, "wip-checkpoint-failure") == _with_liveness(payload)


def _completion_payload(carrier_kind: str | None) -> dict[str, object]:
    candidate: dict[str, object] = {
        "status": "validated",
        "persist": {"status": "persisted"},
        "head_is_complete": False,
    }
    if carrier_kind is not None:
        candidate["carrier_kind"] = carrier_kind
    return {
        "task_id": "persist-completion",
        "status": "completed",
        "phase": "running",
        "timestamps": {},
        "timings_ms": {},
        "worktree_path": "/tmp/lane",
        "candidate": candidate,
    }


def test_persist_completion_names_the_worktree_only_carrier(tmp_path: Path) -> None:
    """A persisted worktree-only candidate says no lane commit holds it."""
    payload = _completion_payload("worktree-only")

    task_run._persist_completion(payload, tmp_path / "runtime")

    assert payload["next_step"] == (
        "Review the complete validated candidate in /tmp/lane; "
        "no lane commit exists, so lane HEAD is not the complete candidate."
    )


def test_persist_completion_names_the_subset_lane_head(tmp_path: Path) -> None:
    """Any other carrier says the lane HEAD is a proper subset of the candidate."""
    payload = _completion_payload("lane")

    task_run._persist_completion(payload, tmp_path / "runtime")

    assert payload["next_step"] == (
        "Review the complete validated candidate in /tmp/lane; "
        "the lane HEAD commit is a proper subset of the complete candidate. "
        "Carry the committed_paths and dirty_paths before treating it as integrated."
    )


class _RefuseSubprocessGuardOnce:
    """Refuses the first `scripts.core.subprocess_guard` import, then stands down."""

    def __init__(self) -> None:
        self.fired = False

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts.core.subprocess_guard" and not self.fired:
            self.fired = True
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_task_run_execution_binds_its_owners_without_the_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The flat-layout fallback still binds the real subprocess guard.

    `task_run_execution` is imported both as `scripts.task_run...` and by path
    from a host that cannot resolve the `scripts` package for one import. The
    fallback arm re-roots on the file location and binds the same owners, and
    it leaves `sys.path` alone when the root is already present.
    """
    root = Path(__file__).resolve().parents[2]
    refuser = _RefuseSubprocessGuardOnce()
    monkeypatch.setattr(sys, "meta_path", [refuser] + sys.meta_path)
    evict_module(monkeypatch, "scripts.core.subprocess_guard")
    before_path = list(sys.path)
    before = set(sys.modules)
    try:
        module = load_script_module(
            "task_run_execution_flat_825",
            root / "scripts/task_run/task_run_execution.py",
        )

        assert refuser.fired
        assert module.render_display.__module__ == "scripts.core.subprocess_guard"
        assert module.run_monitored_phase.__module__ == "scripts.core.subprocess_guard"
        assert list(sys.path) == before_path
    finally:
        evict_new_modules(before)


def test_task_run_execution_module_is_mapped_for_mutation_sampling() -> None:
    """The sampled module stays referenced so the sampler keeps mapping this file."""
    assert task_run_execution._DESCENDANT_CLEANUP_SHELL.startswith("printf")
