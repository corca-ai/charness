from __future__ import annotations

import hashlib
import json
import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.quality_gates.issue_goal_run_test_support import (
    _fixture_metadata,
    close_inputs,
    parent_body,
)

ROOT = Path(__file__).resolve().parents[2]
PROVIDER_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run.py"
CLOSE_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_close.py"
REPO = "corca-ai/charness"
BINDING_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_binding.py"


def _provider() -> dict[str, object]:
    return runpy.run_path(str(PROVIDER_PATH))


def _bound_operation(
    tmp_path: Path, operation: str, target: dict[str, object], **extra: object
) -> Path:
    fixture = _fixture_metadata(tmp_path)
    path = tmp_path / f"{operation}.json"
    path.write_text(
        json.dumps(
            {
                "kind": "charness.goal-run-operation/v1",
                "repo": REPO,
                "parent_number": 724,
                "operation": operation,
                "attempt_id": f"attempt-{operation}",
                "draft_sha256": fixture["draft_sha256"],
                "binding_sha256": fixture["binding_sha256"],
                "binding_path": "goal.binding.json",
                "observation_dir": "observations",
                "target": target,
                **extra,
            }
        ),
        encoding="utf-8",
    )
    return path


def _apply_without_provider(tmp_path: Path, operation: Path) -> tuple[int, dict[str, object]]:
    emitted: list[dict[str, object]] = []
    rc = _provider()["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
        resolve_backend=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("binding mismatch must refuse before provider selection")
        ),
        emit=emitted.append,
    )
    return rc, emitted[0]


@pytest.mark.parametrize(
    "target",
    [
        {"repo": REPO, "number": 725, "work_item_key": "wrong-key"},
        {"repo": REPO, "number": 726, "work_item_key": "child-725"},
    ],
)
def test_update_refuses_wrong_bound_child_identity_before_provider(
    tmp_path: Path, target: dict[str, object]
) -> None:
    close_inputs(tmp_path)
    (tmp_path / "body.md").write_bytes(b"new child body\n")
    operation = _bound_operation(tmp_path, "update-body", target, body_file="body.md")

    rc, result = _apply_without_provider(tmp_path, operation)

    assert rc == 2
    assert result["error_code"] == "binding-mismatch"
    assert result["mutation_invoked"] is False


def test_update_refuses_changed_submitted_body_before_provider(tmp_path: Path) -> None:
    close_inputs(tmp_path)
    (tmp_path / "body.md").write_bytes(b"changed child body\n")
    operation = _bound_operation(
        tmp_path,
        "update-body",
        {"repo": REPO, "number": 725, "work_item_key": "child-725"},
        body_file="body.md",
    )

    rc, result = _apply_without_provider(tmp_path, operation)

    assert rc == 2
    assert result["error_code"] == "binding-mismatch"
    assert result["mutation_invoked"] is False


@pytest.mark.parametrize("operation", ["add-child", "remove-child"])
def test_relationship_refuses_wrong_work_item_key_before_provider(
    tmp_path: Path, operation: str
) -> None:
    close_inputs(tmp_path)
    operation_file = _bound_operation(
        tmp_path,
        operation,
        {"repo": REPO, "sub_issue_number": 725, "work_item_key": "wrong-key"},
    )

    rc, result = _apply_without_provider(tmp_path, operation_file)

    assert rc == 2
    assert result["error_code"] == "binding-mismatch"
    assert result["mutation_invoked"] is False


def test_list_refuses_expected_child_set_outside_binding_before_provider(tmp_path: Path) -> None:
    close_inputs(tmp_path, children=[726])
    operation = _bound_operation(
        tmp_path,
        "list-children",
        {"repo": REPO, "number": 724},
        expected_child_file="expected-children.json",
    )

    rc, result = _apply_without_provider(tmp_path, operation)

    assert rc == 2
    assert result["error_code"] == "binding-mismatch"
    assert result["mutation_invoked"] is False


def test_created_child_identity_is_bound_by_approved_body_bytes() -> None:
    module = runpy.run_path(str(BINDING_PATH))
    body = "<!-- charness-work-item-key: created-child -->\napproved body\n"
    binding = {
        "parent": {"repo": REPO, "number": 724},
        "approved_work_items": [
            {
                "key": "created-child",
                "intent": "create",
                "issue": None,
                "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            }
        ],
    }

    module["require_expected_children"](
        binding, [{"repo": REPO, "number": 900}], context="created graph"
    )
    module["require_created_children"](binding, [{"number": 900, "body": body}])

    with pytest.raises(RuntimeError, match="does not map to one live child"):
        module["require_created_children"](
            binding, [{"number": 900, "body": body + "drift"}]
        )


@pytest.mark.parametrize("position", ["prefix", "suffix"])
def test_parent_update_preserves_live_human_body_before_provider(
    tmp_path: Path, position: str
) -> None:
    close_inputs(tmp_path)
    current = "original prefix\n" + parent_body(tmp_path) + "original suffix\n"
    desired = (
        "changed prefix\n" + parent_body(tmp_path) + "original suffix\n"
        if position == "prefix"
        else "original prefix\n" + parent_body(tmp_path) + "changed suffix\n"
    )
    (tmp_path / "body.md").write_text(desired, encoding="utf-8")
    module = _provider()
    tracker = module["TRACKER"]
    tracker.VERIFY_CREATE = SimpleNamespace(
        verify_created_issue=lambda *_args, **_kwargs: {
            "body_verified": False,
            "body": current,
            "url": f"https://github.com/{REPO}/issues/724",
        }
    )
    tracker.run_backend = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("human body mismatch must refuse before provider mutation")
    )
    operation = _bound_operation(
        tmp_path, "update-body", {"repo": REPO, "number": 724}, body_file="body.md"
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
        resolve_backend=lambda *_args, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["status"] == "provider-refused"
    assert emitted[0]["mutation_invoked"] is False


def test_close_refuses_final_expected_set_outside_binding_before_graph(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = close_inputs(tmp_path, children=[726])
    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda *_args, **_kwargs: {
            "issue": {"number": 724, "state": "OPEN", "body": parent_body(tmp_path)}
        }
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("binding mismatch must stop before graph verification")
        )
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda *_args, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["status"] == "close-refused"
    assert "immutable Goal Binding" in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()
