from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OBSERVATION = runpy.run_path(
    str(ROOT / "skills/public/issue/scripts/issue_tracker_observation.py")
)


def test_started_and_terminal_observations_are_immutable_and_hash_bound(tmp_path: Path) -> None:
    started = OBSERVATION["begin"](
        repo_root=tmp_path,
        observation_dir=Path("charness-artifacts/goal-runs/724"),
        attempt_id="bootstrap-parent-update-1",
        draft_sha256="a" * 64,
        binding_sha256="b" * 64,
        repo="corca-ai/charness",
        parent_number=724,
        operation="update-body",
        target={"repo": "corca-ai/charness", "number": 724},
        submitted_body_sha256="c" * 64,
        backend={"id": "gh", "binary": "gh"},
    )
    terminal = OBSERVATION["finish"](
        repo_root=tmp_path,
        observation_dir=Path("charness-artifacts/goal-runs/724"),
        attempt_id="bootstrap-parent-update-1",
        started=started,
        result={"ok": True, "outcome": "verified-write", "mutation_invoked": True},
    )

    started_payload = json.loads((tmp_path / started["path"]).read_text(encoding="utf-8"))
    terminal_payload = json.loads((tmp_path / terminal["path"]).read_text(encoding="utf-8"))
    assert started_payload["outcome"] == "started"
    assert terminal_payload["started_sha256"] == started_payload["receipt_sha256"]
    assert len(terminal_payload["receipt_sha256"]) == 64
    with pytest.raises(RuntimeError, match="immutable"):
        OBSERVATION["begin"](
            repo_root=tmp_path,
            observation_dir=Path("charness-artifacts/goal-runs/724"),
            attempt_id="bootstrap-parent-update-1",
            draft_sha256="a" * 64,
            binding_sha256="b" * 64,
            repo="corca-ai/charness",
            parent_number=724,
            operation="update-body",
            target={},
            submitted_body_sha256=None,
            backend={"id": "gh", "binary": "gh"},
        )


def test_observation_directory_cannot_escape_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="inside repo root"):
        OBSERVATION["begin"](
            repo_root=tmp_path,
            observation_dir=Path("../outside"),
            attempt_id="attempt-1",
            draft_sha256="a" * 64,
            binding_sha256="b" * 64,
            repo="corca-ai/charness",
            parent_number=724,
            operation="update-body",
            target={},
            submitted_body_sha256=None,
            backend={"id": "gh", "binary": "gh"},
        )


def test_unverified_create_observation_blocks_same_identity_retry(tmp_path: Path) -> None:
    observation_dir = Path("charness-artifacts/goal-runs/724")
    started = OBSERVATION["begin"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        attempt_id="create-binding-1",
        draft_sha256="a" * 64,
        binding_sha256="b" * 64,
        repo="corca-ai/charness",
        parent_number=724,
        operation="create-child",
        target={"repo": "corca-ai/charness", "work_item_key": "goal-binding-v1"},
        submitted_body_sha256="c" * 64,
        backend={"id": "gh", "binary": "gh"},
    )
    OBSERVATION["finish"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        attempt_id="create-binding-1",
        started=started,
        result={"ok": False, "outcome": "unverified-write", "mutation_invoked": True},
    )

    unresolved = OBSERVATION["find_unresolved_create"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        repo="corca-ai/charness",
        parent_number=724,
        work_item_key="goal-binding-v1",
        submitted_body_sha256="c" * 64,
        exclude_attempt_id="create-binding-2",
    )

    assert unresolved["reason"] == "prior-mutation-outcome-unverified"
    assert unresolved["started_path"].endswith("create-binding-1.started.json")

    changed_body = OBSERVATION["find_unresolved_create"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        repo="corca-ai/charness",
        parent_number=724,
        work_item_key="goal-binding-v1",
        submitted_body_sha256="d" * 64,
        exclude_attempt_id="create-binding-2",
    )
    assert changed_body["reason"] == "prior-mutation-outcome-unverified"
    assert changed_body["submitted_body_changed"] is True
    assert changed_body["prior_submitted_body_sha256"] == "c" * 64
    assert changed_body["requested_submitted_body_sha256"] == "d" * 64


def test_verified_create_observation_does_not_block_retry_scan(tmp_path: Path) -> None:
    observation_dir = Path("observations")
    started = OBSERVATION["begin"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        attempt_id="create-binding-1",
        draft_sha256="a" * 64,
        binding_sha256="b" * 64,
        repo="corca-ai/charness",
        parent_number=724,
        operation="create-child",
        target={"repo": "corca-ai/charness", "work_item_key": "goal-binding-v1"},
        submitted_body_sha256="c" * 64,
        backend={"id": "gh", "binary": "gh"},
    )
    OBSERVATION["finish"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        attempt_id="create-binding-1",
        started=started,
        result={"ok": True, "outcome": "verified-write", "mutation_invoked": True},
    )

    unresolved = OBSERVATION["find_unresolved_create"](
        repo_root=tmp_path,
        observation_dir=observation_dir,
        repo="corca-ai/charness",
        parent_number=724,
        work_item_key="goal-binding-v1",
        submitted_body_sha256="c" * 64,
        exclude_attempt_id="create-binding-2",
    )

    assert unresolved is None
