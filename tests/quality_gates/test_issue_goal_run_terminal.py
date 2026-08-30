from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/public/issue/scripts"
REPO = "corca-ai/charness"
DRAFT_SHA = "a" * 64
BINDING_SHA = "b" * 64
COMMENT_SHA = "c" * 64


def _attempt(tmp_path: Path, *, result_operation: str) -> tuple[dict[str, object], dict[str, object]]:
    observation = runpy.run_path(str(SCRIPTS / "issue_tracker_observation.py"))
    started = observation["begin"](
        repo_root=tmp_path,
        observation_dir=Path("observations"),
        attempt_id="close-1",
        draft_sha256=DRAFT_SHA,
        binding_sha256=BINDING_SHA,
        repo=REPO,
        parent_number=724,
        operation="close-goal-run",
        target={"repo": REPO, "number": 724},
        submitted_body_sha256=COMMENT_SHA,
        backend={"id": "gh", "binary": "gh"},
    )
    observation["finish"](
        repo_root=tmp_path,
        observation_dir=Path("observations"),
        attempt_id="close-1",
        started=started,
        result={
            "ok": True,
            "operation": result_operation,
            "outcome": "verified-write",
            "mutation_invoked": True,
            "comment_succeeded": True,
            "close_succeeded": True,
        },
    )
    attempt = observation["read_attempt"](
        repo_root=tmp_path,
        observation_dir=Path("observations"),
        attempt_id="close-1",
    )
    assert attempt is not None
    return observation, attempt


def test_verified_close_receipt_binds_started_and_result_operation(tmp_path: Path) -> None:
    terminal = runpy.run_path(str(SCRIPTS / "issue_goal_run_terminal.py"))
    _, attempt = _attempt(tmp_path, result_operation="different-operation")

    with pytest.raises(RuntimeError, match="completed Goal Run close command"):
        terminal["validate_verified_close_attempt"](
            attempt,
            repo=REPO,
            parent_number=724,
            draft_sha256=DRAFT_SHA,
            binding_sha256=BINDING_SHA,
        )


def test_metadata_receipt_binds_current_comment_bytes(tmp_path: Path) -> None:
    terminal = runpy.run_path(str(SCRIPTS / "issue_goal_run_terminal.py"))
    observation, attempt = _attempt(tmp_path, result_operation="close-goal-run")
    receipt = attempt["terminal"]

    with pytest.raises(RuntimeError, match="verified Goal Run close"):
        terminal["validate_metadata_receipt"](
            repo_root=tmp_path,
            observation_dir=Path("observations"),
            metadata={
                "terminal_observation_path": receipt["path"],
                "terminal_observation_sha256": receipt["payload"]["receipt_sha256"],
            },
            repo=REPO,
            parent_number=724,
            draft_sha256=DRAFT_SHA,
            binding_sha256=BINDING_SHA,
            comment_sha256="d" * 64,
            observation=SimpleNamespace(read_attempt=observation["read_attempt"]),
        )


def test_close_history_matches_repository_identity_case_insensitively(tmp_path: Path) -> None:
    observation, _ = _attempt(tmp_path, result_operation="close-goal-run")

    history = observation["find_close_attempts"](
        repo_root=tmp_path,
        observation_dir=Path("observations"),
        repo="Corca-AI/Charness",
        parent_number=724,
        draft_sha256=DRAFT_SHA,
        binding_sha256=BINDING_SHA,
        exclude_attempt_id="next-attempt",
    )

    assert len(history) == 1


def test_closed_recovery_refuses_an_invalid_prior_terminal_before_new_receipt(
    tmp_path: Path,
) -> None:
    recovery = runpy.run_path(str(SCRIPTS / "issue_goal_run_close_recovery.py"))
    _, attempt = _attempt(tmp_path, result_operation="different-operation")
    observation = SimpleNamespace(
        find_close_attempts=lambda **_kwargs: [attempt],
        begin=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("invalid prior receipt must not create a recovery attempt")
        ),
    )
    terminal = SimpleNamespace(
        validate_recoverable_close_attempt=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("invalid prior close")
        )
    )

    with pytest.raises(RuntimeError, match="unresolved"):
        recovery["plan"](
            repo_root=tmp_path,
            repo=REPO,
            parent_number=724,
            parent={"number": 724, "state": "CLOSED"},
            metadata={},
            proof={
                "attempt_id": "recovery-1",
                "draft_sha256": DRAFT_SHA,
                "binding_sha256": BINDING_SHA,
                "comment_sha256": COMMENT_SHA,
                "observation_dir": "observations",
            },
            backend={"id": "gh", "binary": "gh"},
            observation=observation,
            terminal_contract=terminal,
        )


@pytest.mark.parametrize(
    ("prior", "message"),
    [
        (
            {"started": {"payload": {"submitted_body_sha256": COMMENT_SHA}}, "terminal": None},
            "without a valid terminal observation",
        ),
        (
            {
                "started": {
                    "payload": {
                        "operation": "close-goal-run",
                        "submitted_body_sha256": "d" * 64,
                    }
                },
                "terminal": {
                    "payload": {
                        "mutation_invoked": True,
                        "result": {
                            "operation": "close-goal-run",
                            "comment_succeeded": True,
                            "close_succeeded": False,
                        },
                    }
                },
            },
            "different comment bytes",
        ),
    ],
)
def test_open_retry_refuses_orphaned_or_changed_input_close_history(
    tmp_path: Path, prior: dict[str, object], message: str
) -> None:
    recovery = runpy.run_path(str(SCRIPTS / "issue_goal_run_close_recovery.py"))
    observation = SimpleNamespace(
        find_close_attempts=lambda **_kwargs: [prior],
        begin=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("unsafe history must refuse before a new close start")
        ),
    )

    with pytest.raises(RuntimeError, match=message):
        recovery["plan"](
            repo_root=tmp_path,
            repo=REPO,
            parent_number=724,
            parent={"number": 724, "state": "OPEN"},
            metadata={},
            proof={
                "attempt_id": "retry-1",
                "draft_sha256": DRAFT_SHA,
                "binding_sha256": BINDING_SHA,
                "comment_sha256": COMMENT_SHA,
                "observation_dir": "observations",
            },
            backend={"id": "gh", "binary": "gh"},
            observation=observation,
            terminal_contract=SimpleNamespace(),
        )
