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


def _amendment_authorization(tmp_path: Path, current: str, desired: str) -> Path:
    metadata = _fixture_metadata(tmp_path)
    payload = {
        "kind": "charness.goal-run-parent-amendment/v1",
        "parent": {
            "repo": REPO,
            "number": 724,
            "url": f"https://github.com/{REPO}/issues/724",
        },
        "binding_sha256": metadata["binding_sha256"],
        "current_body_sha256": hashlib.sha256(current.encode("utf-8")).hexdigest(),
        "desired_body_sha256": hashlib.sha256(desired.encode("utf-8")).hexdigest(),
        "approval": {
            "response": "approved",
            "session_id": "amendment-session",
            "observed_at": "2026-08-31T00:00:00+09:00",
        },
        "reason": "Keep the parent narrative current after the approved execution change.",
    }
    path = tmp_path / "amendment.json"
    path.write_bytes(
        (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    )
    return path


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


def test_created_child_identity_is_its_marker_not_its_prose() -> None:
    module = runpy.run_path(str(BINDING_PATH))
    body = "<!-- charness-work-item-key: created-child -->\napproved body\n"
    binding = {
        "parent": {"repo": REPO, "number": 724},
        "approved_work_items": [
            {
                "key": "created-child",
                "intent": "create",
                "issue": None,
                "rank": 1,
                "dependencies": [],
                "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            }
        ],
    }

    module["require_expected_children"](
        binding, [{"repo": REPO, "number": 900}], context="created graph"
    )
    module["require_created_children"](binding, [{"number": 900, "body": body}])
    # prose may be corrected after creation; the marker is the identity
    module["require_created_children"](binding, [{"number": 900, "body": body + "corrected scope\n"}])

    with pytest.raises(RuntimeError, match="does not map to one live child"):
        module["require_created_children"](binding, [{"number": 900, "body": "no marker\n"}])


def test_amended_work_item_joins_the_graph_by_number() -> None:
    module = runpy.run_path(str(BINDING_PATH))
    binding = {
        "parent": {"repo": REPO, "number": 724},
        "approved_work_items": [
            {"key": "first", "intent": "create", "issue": None, "rank": 1, "dependencies": [],
             "body_sha256": hashlib.sha256(b"x").hexdigest()},
        ],
    }
    metadata = {
        "parent_identity": {"repo": REPO, "number": 724, "url": f"https://github.com/{REPO}/issues/724"},
        "amendments": [{
            "key": "late", "repo": REPO, "number": 901, "url": f"https://github.com/{REPO}/issues/901",
            "rank": 2, "dependencies": ["first"], "reason": "added after binding",
            "approval": {"response": "approve", "session_id": "s", "observed_at": "t"},
        }],
    }
    first = {"number": 900, "body": "<!-- charness-work-item-key: first -->\n"}
    late = {"number": 901, "body": "no marker needed; identity is the amendment number\n"}
    module["require_expected_children"](
        binding, [{"repo": REPO, "number": 900}, {"repo": REPO, "number": 901}],
        context="amended graph", metadata=metadata,
    )
    module["require_created_children"](binding, [first, late], metadata)
    assert module["work_item_for_target"](binding, "late", number=901, metadata=metadata)["intent"] == "amended"
    with pytest.raises(RuntimeError, match="not an approved Work Item"):
        module["work_item_for_target"](binding, "late")
    with pytest.raises(RuntimeError, match="differ from the Goal Run's approved Work Items"):
        module["require_expected_children"](
            binding, [{"repo": REPO, "number": 900}], context="amended graph", metadata=metadata
        )


@pytest.mark.parametrize("position", ["prefix", "suffix"])
def test_parent_update_allows_human_body_amendment_with_verified_provider_readback(
    tmp_path: Path, position: str
) -> None:
    close_inputs(tmp_path)
    current = "original prefix\n" + parent_body(tmp_path) + "original suffix\n"
    desired = (
        "changed prefix\n" + parent_body(tmp_path) + "original suffix\n"
        if position == "prefix"
        else "original prefix\n" + parent_body(tmp_path) + "changed suffix\n"
    )
    _amendment_authorization(tmp_path, current, desired)
    (tmp_path / "body.md").write_text(desired, encoding="utf-8")
    module = _provider()
    tracker = module["TRACKER"]
    readbacks = iter(
        [
            {
                "body_verified": False,
                "body": current,
                "url": f"https://github.com/{REPO}/issues/724",
            },
            {
                "body_verified": True,
                "url": f"https://github.com/{REPO}/issues/724",
            },
        ]
    )
    tracker.VERIFY_CREATE = SimpleNamespace(
        verify_created_issue=lambda *_args, **_kwargs: next(readbacks)
    )
    provider_calls: list[list[str]] = []
    tracker.resolve_op = lambda *_args, **_kwargs: ["update"]
    tracker.run_backend = lambda argv: (
        provider_calls.append(argv) or SimpleNamespace(returncode=0, stderr="")
    )
    operation = _bound_operation(
        tmp_path,
        "update-body",
        {"repo": REPO, "number": 724},
        body_file="body.md",
        amendment_authorization_file="amendment.json",
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
        resolve_backend=lambda *_args, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["status"] == "verified-write"
    assert emitted[0]["outcome"] == "verified-write"
    assert emitted[0]["mutation_invoked"] is True
    assert emitted[0]["body_verified"] is True
    assert provider_calls == [["update"]]


def test_parent_human_body_may_change_without_an_authorization_receipt(
    tmp_path: Path,
) -> None:
    """Prose on the parent is reversible and provider-logged; only the metadata block is bound."""
    close_inputs(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    binding = module["load_binding"](
        tmp_path, "goal.binding.json", repo=REPO, parent_number=724,
        draft_sha256=_fixture_metadata(tmp_path)["draft_sha256"],
        binding_sha256=_fixture_metadata(tmp_path)["binding_sha256"],
    )
    guard = runpy.run_path(str(ROOT / "skills/public/issue/scripts/issue_goal_run_guard.py"))
    current = "original prefix\n" + parent_body(tmp_path) + "original suffix\n"
    desired = "changed prefix\n" + parent_body(tmp_path) + "original suffix\n"
    module["validate_parent_body_update"](
        current, desired, binding=binding, repo=REPO, parent_number=724,
        parent_url=f"https://github.com/{REPO}/issues/724", guard=SimpleNamespace(**guard),
    )


@pytest.mark.parametrize(
    ("case", "error"),
    [
        ("parent", "parent differs"),
        ("binding", "binding differs"),
        ("current", "current_body_sha256"),
        ("desired", "desired_body_sha256"),
        ("approval", "approval fields must be non-empty"),
    ],
)
def test_parent_update_refuses_authorization_not_bound_to_exact_amendment(
    tmp_path: Path, case: str, error: str
) -> None:
    close_inputs(tmp_path)
    current = "original prefix\n" + parent_body(tmp_path) + "original suffix\n"
    desired = "changed prefix\n" + parent_body(tmp_path) + "original suffix\n"
    authorization = _amendment_authorization(tmp_path, current, desired)
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if case == "parent":
        payload["parent"]["number"] = 725
    elif case == "binding":
        payload["binding_sha256"] = "f" * 64
    elif case == "current":
        payload["current_body_sha256"] = "f" * 64
    elif case == "desired":
        payload["desired_body_sha256"] = "f" * 64
    else:
        payload["approval"]["session_id"] = ""
    authorization.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
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
        AssertionError("invalid amendment authorization must not write")
    )
    operation = _bound_operation(
        tmp_path,
        "update-body",
        {"repo": REPO, "number": 724},
        body_file="body.md",
        amendment_authorization_file="amendment.json",
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
    assert error in emitted[0]["error"]


def test_initial_parent_metadata_append_cannot_overwrite_live_human_body(
    tmp_path: Path,
) -> None:
    close_inputs(tmp_path)
    current = "original human body\n"
    desired = parent_body(tmp_path)
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
    tracker.resolve_op = lambda *_args, **_kwargs: ["update"]
    tracker.run_backend = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("initial metadata append must refuse before provider mutation")
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
    assert "not replace it" in emitted[0]["error"]


def test_parent_metadata_identity_mutation_still_refuses_before_provider(
    tmp_path: Path,
) -> None:
    close_inputs(tmp_path)
    current = parent_body(tmp_path)
    metadata = _fixture_metadata(tmp_path)
    metadata["binding_sha256"] = "f" * 64
    desired = (
        "amended human body\n<!-- charness-goal-run:v1\n"
        + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        + "\n-->\n"
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
        AssertionError("identity mutation must refuse before provider mutation")
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
    assert "immutable Goal Run identity" in emitted[0]["error"]


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
    assert "approved Work Items" in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()
