"""Focused execution probes for uncovered merge-train statements.

The injected Git, worktree, and cleanup outcomes below establish fixture-level
behavior only. They do not claim live train landing or release behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.task_run import task_run_train as train
from scripts.task_run import task_run_train_core as train_core
from scripts.task_run import task_run_train_flow as train_flow


@pytest.mark.parametrize("module", [train, train_flow])
def test_train_script_bootstrap_adds_owning_repo_to_sys_path(
    module: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "checkout"
    marker = repo / "scripts" / "adapter_lib.py"
    marker.parent.mkdir(parents=True)
    marker.write_text("", encoding="utf-8")
    script = repo / "scripts" / "task_run" / "train.py"
    script.parent.mkdir()
    monkeypatch.setattr(module, "__file__", str(script))
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(repo)])

    module._load_repo_runtime_bootstrap()  # type: ignore[attr-defined]

    assert sys.path[0] == str(repo)


def test_verify_profile_relative_path_errors_and_invalid_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    valid_profile = {
        "version": 1,
        "commands": [{"id": "smoke", "argv": ["python3", "-c", "pass"]}],
        "known_failures": [],
    }
    loaded_paths: list[Path] = []
    monkeypatch.setattr(
        train._adapter,
        "load_yaml_file",
        lambda path: loaded_paths.append(path) or valid_profile,
    )

    loaded = train.load_verify_profile(repo, Path("relative.yaml"))

    assert loaded == valid_profile
    assert loaded_paths == [repo / "relative.yaml"]

    with monkeypatch.context() as patch:
        def fail_to_load(_path: Path) -> object:
            raise OSError("profile storage unavailable")

        patch.setattr(train._adapter, "load_yaml_file", fail_to_load)
        with pytest.raises(train.TrainError, match="could not load verify profile") as caught:
            train.load_verify_profile(repo, Path("broken.yaml"))
        assert isinstance(caught.value.__cause__, OSError)
        assert str(caught.value.__cause__) == "profile storage unavailable"

    invalid_file = repo / "invalid.yaml"
    with monkeypatch.context() as patch:
        patch.setattr(
            train._adapter,
            "load_yaml_file",
            lambda _path: {"version": 2, "commands": [], "known_failures": []},
        )
        with pytest.raises(train.TrainError, match="invalid verify profile"):
            train.load_verify_profile(repo, invalid_file)


def test_junit_report_missing_and_parse_failure_are_named_errors(
    tmp_path: Path,
) -> None:
    with pytest.raises(train.TrainError, match="did not write its JUnit report"):
        train._junit_failures(tmp_path / "missing.xml")

    malformed = tmp_path / "malformed.xml"
    malformed.write_text("<testsuite><testcase>", encoding="utf-8")
    with pytest.raises(train.TrainError, match="could not read JUnit report") as caught:
        train._junit_failures(malformed)
    assert caught.value.__cause__ is not None
    assert "no element found" in str(caught.value.__cause__)


def test_run_train_refuses_duplicate_resolved_branch_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(train, "_branch_ref", lambda _repo, _branch: "refs/heads/shared")

    result = train.run_train(tmp_path, ["lane/one", "lane/two"])

    assert result["status"] == train.FAIL
    assert result["decision"] == "refused"
    assert result["error"] == "the train queue contains duplicate local branch refs"


@pytest.mark.parametrize(
    ("cleanup_error", "expected_error"),
    [("worktree busy", "worktree busy"), (None, train.FAIL)],
)
def test_run_train_turns_cleanup_failure_after_success_into_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cleanup_error: str | None,
    expected_error: str,
) -> None:
    monkeypatch.setattr(train, "_branch_ref", lambda _repo, branch: f"refs/heads/{branch}")
    monkeypatch.setattr(train, "_local_ref", lambda _repo, _ref: "refs/heads/main")
    monkeypatch.setattr(train, "_sha", lambda *_args: "base")
    monkeypatch.setattr(train, "load_verify_profile", lambda *_args: {})
    monkeypatch.setattr(train, "runtime_root", lambda _repo: tmp_path / "runtime")

    def stage(
        _repo: Path,
        _refs: tuple[str, ...],
        _base: str,
        _root: Path,
        _cache: Path,
        worktrees: list[Path],
    ) -> tuple[Path, list[str]]:
        worktrees.append(tmp_path / "temporary-worktree")
        return tmp_path / "stage", ["base", "tip"]

    monkeypatch.setattr(train, "_stage_train_branches", stage)
    monkeypatch.setattr(
        train,
        "_verify_train_stack",
        lambda *_args: ([], {0: True, 1: True}, "base", {"action": "land"}),
    )
    monkeypatch.setattr(train, "_finalize_train", lambda *_args: {"status": train.PASS})
    monkeypatch.setattr(
        train._cleanup,
        "run_cleanup",
        lambda *_args, **_kwargs: {"status": train.FAIL, "error": cleanup_error},
    )

    result = train.run_train(tmp_path, ["lane/one"])

    assert result["status"] == train.FAIL
    assert result["cleanup_failures"] == [
        {"path": str(tmp_path / "temporary-worktree"), "error": expected_error}
    ]
    assert result["error"] == (
        "train completed but Charness could not remove every temporary worktree"
    )


def test_train_core_rejects_empty_duplicate_and_unbracketed_inputs() -> None:
    with pytest.raises(train_core.TrainError, match="at least one branch"):
        train_core.stack_order([])
    with pytest.raises(train_core.TrainError, match="duplicate branch"):
        train_core.stack_order(["lane/a", "lane/a"])
    with pytest.raises(ValueError, match="0 <= green < red"):
        train_core.next_bisect_prefix(2, 2)
    with pytest.raises(train_core.TrainError, match="no verified green/red bisect bracket"):
        train_core.decide_next_action(
            ["lane/a"], {0: True}, main_at_start="base", main_now="base"
        )


def test_verify_profile_validation_reports_non_mapping_and_fallback_shapes() -> None:
    errors = train_core.validate_verify_profile(
        {
            "version": True,
            "extra": "not allowed",
            "commands": [
                None,
                {"id": "Bad", "argv": ["true"]},
                {"id": "smoke", "argv": ["true"], "unexpected": True},
            ],
            "known_failures": "not a list",
        }
    )

    assert "profile.version must be integer 1" in errors
    assert "profile has unknown keys: extra" in errors
    assert "profile.commands[0] must be a mapping" in errors
    assert any(
        error.startswith("profile.commands[1].id must match ") for error in errors
    )
    assert "profile.commands[2] has unknown keys" in errors
    assert "profile.known_failures must be a list" in errors
    assert train_core.validate_verify_profile(None) == ["profile root must be a mapping"]


@pytest.mark.parametrize(
    ("stderr", "stdout", "expected"),
    [("", "git output", "git output"), ("", "", "git command failed")],
)
def test_git_error_uses_stdout_then_named_fallback(
    monkeypatch: pytest.MonkeyPatch, stderr: str, stdout: str, expected: str
) -> None:
    monkeypatch.setattr(
        train_flow,
        "_run_process",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1, stderr=stderr, stdout=stdout
        ),
    )

    with pytest.raises(train_flow.TrainError, match=expected):
        train_flow._git(Path("/repo"), "status")


def test_ref_helpers_reject_nonlocal_and_invalid_branch_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(train_flow, "_git", lambda *_args, **_kwargs: "refs/tags/v1")
    with pytest.raises(train_flow.TrainError, match="is not a local branch"):
        train_flow._local_ref(Path("/repo"), "v1")

    with pytest.raises(train_flow.TrainError, match="invalid local branch name"):
        train_flow._branch_ref(Path("/repo"), "")
    with pytest.raises(train_flow.TrainError, match="invalid local branch name"):
        train_flow._branch_ref(Path("/repo"), "-force")

    monkeypatch.setattr(
        train_flow,
        "_run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stderr="", stdout=""),
    )
    with pytest.raises(train_flow.TrainError, match="invalid local branch name"):
        train_flow._branch_ref(Path("/repo"), "bad name")


@pytest.mark.parametrize(
    ("error", "expected"),
    [(None, "Charness could not create the train worktree"), ("disk full", "disk full")],
)
def test_worktree_creation_failure_uses_error_or_named_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    error: str | None,
    expected: str,
) -> None:
    monkeypatch.setattr(
        train_flow._worktree,
        "run_create",
        lambda *_args, **_kwargs: {"created": False, "error": error},
    )

    with pytest.raises(train_flow.TrainError, match=expected):
        train_flow._create_worktree(
            tmp_path / "repo", tmp_path / "worktrees" / "stack", "base", tmp_path / "cache"
        )


def test_land_main_refuses_changed_or_dirty_checked_out_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(train_flow, "_checked_out_path", lambda *_args: tmp_path)
    monkeypatch.setattr(train_flow, "_sha", lambda *_args: "moved")
    assert train_flow._land_main(
        tmp_path, "refs/heads/main", "base", "tip"
    ) == (False, "main changed before the train could land")

    monkeypatch.setattr(train_flow, "_sha", lambda *_args: "base")
    monkeypatch.setattr(
        train_flow,
        "_run_process",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=" M tracked.txt", stderr=""
        ),
    )
    assert train_flow._land_main(
        tmp_path, "refs/heads/main", "base", "tip"
    ) == (False, "the main branch worktree is not clean; train was not landed")


def test_land_main_updates_unchecked_out_ref_and_names_git_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(train_flow, "_checked_out_path", lambda *_args: None)
    calls: list[list[str]] = []

    def update_ref(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(train_flow, "_run_process", update_ref)
    assert train_flow._land_main(
        tmp_path, "refs/heads/main", "base", "tip"
    ) == (True, "")
    assert calls[0] == ["git", "update-ref", "refs/heads/main", "tip", "base"]

    monkeypatch.setattr(
        train_flow,
        "_run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout="", stderr=""),
    )
    assert train_flow._land_main(
        tmp_path, "refs/heads/main", "base", "tip"
    ) == (False, "main changed before the train could land")


def test_prefix_bisect_stops_when_prepare_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare_calls = 0
    created: list[Path] = []

    def prepare(*_args: object) -> dict[str, str]:
        nonlocal prepare_calls
        prepare_calls += 1
        return {"status": train.PASS if prepare_calls == 1 else train.FAIL}

    monkeypatch.setattr(train_flow, "_prepare_worktree", prepare)
    monkeypatch.setattr(
        train_flow,
        "_create_worktree",
        lambda _repo, path, *_args: created.append(path) or {"created": True},
    )
    monkeypatch.setattr(train_flow, "_sha", lambda *_args: "base")

    with pytest.raises(train_flow.TrainError, match="bisect verification refused at prefix 1"):
        train_flow._verify_train_stack(
            tmp_path,
            ["lane/a", "lane/b"],
            tmp_path / "worktrees" / "stack",
            ["base", "one", "two"],
            "base",
            "refs/heads/main",
            tmp_path / "train-run",
            tmp_path / "cache",
            [],
            {},
            lambda *_args: (False, []),
        )

    assert created == [tmp_path / "train-run" / "worktrees" / "prefix-1"]


def _finalize_train_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    main_shas: list[str],
    landed: bool = True,
    land_error: str = "",
    outcomes: dict[int, bool] | None = None,
    land_count: int = 1,
) -> dict[str, object]:
    observed_shas = iter(main_shas)
    monkeypatch.setattr(train_flow, "_sha", lambda *_args: next(observed_shas))
    monkeypatch.setattr(
        train_flow, "_land_main", lambda *_args: (landed, land_error)
    )
    monkeypatch.setattr(
        train_flow,
        "_landing_review_trigger",
        lambda *_args: {"status": "fixture-only"},
    )
    return train_flow._finalize_train(
        Path("/repo"),
        ["lane/a"],
        outcomes if outcomes is not None else {0: True, 1: True},
        {"action": "land-prefix", "land_count": land_count},
        "refs/heads/main",
        "base",
        ["base", "tip"],
        [],
        Path("/runtime/train-runs/run"),
        "run",
        "base",
    )


def test_finalize_requeues_when_main_moves_before_landing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _finalize_train_fixture(monkeypatch, main_shas=["moved"])

    assert result["decision"] == "requeue"
    assert result["reason"] == "main-moved"
    assert result["main_sha"] == "moved"


def test_finalize_returns_without_landing_when_green_prefix_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _finalize_train_fixture(
        monkeypatch, main_shas=["base"], outcomes={0: True, 1: False}, land_count=0
    )

    assert result["decision"] == "land-prefix"
    assert result["landed_branches"] == []
    assert result["candidate_sha"] == "base"


def test_finalize_requeues_when_main_moves_after_a_failed_landing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _finalize_train_fixture(
        monkeypatch, main_shas=["base", "moved"], landed=False, land_error="stale ref"
    )

    assert result["decision"] == "requeue"
    assert result["reason"] == "main-moved"
    assert result["main_sha"] == "moved"


def test_finalize_raises_when_landing_fails_without_main_movement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(train_flow.TrainError, match="merge refused"):
        _finalize_train_fixture(
            monkeypatch, main_shas=["base", "base"], landed=False, land_error="merge refused"
        )


def test_finalize_returns_land_raced_payload_when_tip_does_not_match_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _finalize_train_fixture(monkeypatch, main_shas=["base", "other"])

    assert result["status"] == train.FAIL
    assert result["decision"] == "land-raced"
    assert result["error"] == "main changed while the fast-forward was completing"
    assert result["landed_sha"] == "other"
