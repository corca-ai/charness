from __future__ import annotations

import hashlib
import json
import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROVIDER_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run.py"
CLOSE_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_close.py"
CLOSE_BACKEND_PATH = ROOT / "skills/public/issue/scripts/issue_close.py"
REPO = "corca-ai/charness"


def _provider():
    return runpy.run_path(str(PROVIDER_PATH))


def _operation(tmp_path: Path, operation: str, target: dict[str, object], **extra: object) -> Path:
    path = tmp_path / f"{operation}.json"
    value = {
        "kind": "charness.goal-run-operation/v1",
        "repo": REPO,
        "parent_number": 724,
        "operation": operation,
        "attempt_id": f"attempt-{operation}",
        "draft_sha256": "a" * 64,
        "binding_sha256": "b" * 64,
        "observation_dir": "observations",
        "target": target,
        **extra,
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _close_inputs(
    tmp_path: Path,
    *,
    attempt_id: str = "close-1",
    children: list[int] | None = None,
    index_payload: dict[str, object] | None = None,
    proof_overrides: dict[str, object] | None = None,
) -> Path:
    children = children or [725]
    comment = tmp_path / "close.md"
    comment.write_text("Closes the Goal Run.\n", encoding="utf-8")
    index = tmp_path / "final-proof-index.json"
    index.write_text(
        json.dumps(
            index_payload
            or {
                "kind": "charness.goal-run-final-proof-index/v1",
                "repo": REPO,
                "parent_number": 724,
                "draft_sha256": "a" * 64,
                "binding_sha256": "b" * 64,
                "expected_children": [{"repo": REPO, "number": number} for number in children],
                "parent_obligation": {"repo": REPO, "number": 724},
            }
        ),
        encoding="utf-8",
    )
    proof_payload: dict[str, object] = {
        "kind": "charness.goal-run-close-proof/v1",
        "repo": REPO,
        "parent_number": 724,
        "attempt_id": attempt_id,
        "draft_sha256": "a" * 64,
        "binding_sha256": "b" * 64,
        "observation_dir": "observations",
        "comment_file": "close.md",
        "comment_sha256": hashlib.sha256(comment.read_bytes()).hexdigest(),
        "final_proof_index_file": "final-proof-index.json",
        "final_proof_index_sha256": hashlib.sha256(index.read_bytes()).hexdigest(),
        "whole_system_proof": True,
        "children": [
            {
                "repo": REPO,
                "number": number,
                "evidence": {"kind": "issue-owned-closeout/v1", "identity": "comment"},
            }
            for number in children
        ],
    }
    proof_payload.update(proof_overrides or {})
    proof = tmp_path / "proof.json"
    proof.write_text(json.dumps(proof_payload), encoding="utf-8")
    return proof


def test_goal_run_plan_preflight_is_file_bound_and_typed(tmp_path: Path) -> None:
    module = _provider()
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "kind": "charness.goal-run-plan/v1",
                "repo": REPO,
                "parent_number": 724,
                "operations": ["read-body", "list-children"],
            }
        ),
        encoding="utf-8",
    )
    module["command_preflight"].__globals__["_preflight"] = lambda **kwargs: {
        "ok": True,
        "status": "ready",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "parent": {"number": kwargs["parent_number"], "state": "OPEN"},
    }
    emitted: list[dict[str, object]] = []

    rc = module["command_preflight"](
        Namespace(repo=REPO, number=724, plan_file=plan, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["kind"] == "charness.goal-run-preflight/v1"
    assert emitted[0]["plan"]["sha256"]
    assert emitted[0]["plan"]["operations"] == ["read-body", "list-children"]


def test_goal_run_read_returns_parent_and_real_graph(tmp_path: Path) -> None:
    module = _provider()
    module["command_read"].__globals__["_preflight"] = lambda **_kwargs: (_ for _ in ()).throw(
        AssertionError("ordinary graph reads must not run a duplicate readiness preflight")
    )
    module["command_read"].__globals__["_read_graph"] = lambda *_args, **_kwargs: {
        "ok": True,
        "kind": "charness.goal-run-read/v1",
        "status": "verified-read",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "parent": {"number": 724, "state": "OPEN"},
        "children": [{"number": 725, "state": "OPEN"}],
    }
    emitted: list[dict[str, object]] = []

    rc = module["command_read"](
        Namespace(repo=REPO, number=724, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["children"] == [{"number": 725, "state": "OPEN"}]
    assert emitted[0]["selected_backend"]["id"] == "gh"


def test_goal_run_apply_records_started_and_terminal_for_read(tmp_path: Path) -> None:
    module = _provider()
    module["command_apply"].__globals__["_preflight"] = lambda **_kwargs: (_ for _ in ()).throw(
        AssertionError("ordinary applies must not run a duplicate readiness preflight")
    )
    module["command_apply"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda *_args, **_kwargs: {
            "issue": {
                "number": 724,
                "state": "OPEN",
                "url": "https://github.com/corca-ai/charness/issues/724",
                "body": "body\n",
                "comments": [],
            }
        }
    )
    operation = _operation(tmp_path, "read-body", {"repo": REPO, "number": 724})
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh", "binary": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["outcome"] == "verified-read"
    assert emitted[0]["observation"]["started_path"].endswith(".started.json")
    assert (tmp_path / "observations/attempt-read-body.started.json").is_file()
    assert (tmp_path / "observations/attempt-read-body.terminal.json").is_file()


def test_goal_run_apply_uses_record_operation_without_backend_mutation(tmp_path: Path) -> None:
    module = _provider()
    operation = _operation(
        tmp_path,
        "record-observation",
        {"repo": REPO, "number": 724},
        result={"ok": True, "outcome": "verified-read", "mutation_invoked": False},
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: (_ for _ in ()).throw(
            AssertionError("local observation must not select a provider")
        ),
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["status"] == "local-only"
    assert emitted[0]["outcome"] == "verified-read"
    assert emitted[0]["selected_backend"]["id"] == "local"


def test_goal_run_apply_rejects_missing_operation_identity_before_provider(tmp_path: Path) -> None:
    module = _provider()
    operation = _operation(tmp_path, "read-state", {"repo": REPO})
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: (_ for _ in ()).throw(AssertionError("must not resolve backend")),
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["error_code"] == "schema-invalid"
    assert emitted[0]["mutation_invoked"] is False


def test_goal_run_close_refuses_open_child_before_observation_or_close(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path)
    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda *_args, **_kwargs: {
            "issue": {
                "number": 724,
                "state": "OPEN",
                "body": '<!-- charness-goal-run:v1\n{"draft_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","binding_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}\n-->\n',
            }
        }
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {
            "children": [{"number": 725, "state": "OPEN"}]
        }
    )
    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not close"))
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["status"] == "close-refused"
    assert "not CLOSED" in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()


def test_goal_run_close_reuses_parent_read_for_carrier_preflight(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-2")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": '<!-- charness-goal-run:v1\n{"binding_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","draft_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","initial_graph_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","parent_identity":{"number":724,"repo":"corca-ai/charness"},"progress":{"revision":1}}\n-->\n',
        "comments": [],
    }
    child = {
        "number": 725,
        "state": "CLOSED",
        "comments": [{"url": "comment"}],
    }
    reads: list[int] = []
    updated_parent = dict(parent)

    def read_issue(_repo: str, number: int, **_kwargs: object) -> dict[str, object]:
        reads.append(number)
        return {"issue": updated_parent if number == 724 and len(reads) > 2 else parent if number == 724 else child}

    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=read_issue
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {"children": [{"number": 725, "state": "CLOSED"}]},
        update_issue_body=lambda _repo, _number, body_file, **_kwargs: (
            updated_parent.update(state="CLOSED", body=body_file.read_text(encoding="utf-8"))
            or {
                "ok": True,
                "status": "verified-write",
                "outcome": "verified-write",
                "mutation_invoked": True,
                "body_verified": True,
            }
        ),
    )
    captured: dict[str, object] = {}

    def close_with_comment(*_args: object, **kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {"carrier": "test", "preflight_state": kwargs["preflight_state"]}

    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=close_with_comment
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
            resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert reads == [724, 725, 724]
    assert captured["preflight_state"] == parent
    assert emitted[0]["status"] == "verified-write"
    assert emitted[0]["terminal_metadata"]["readback"]["state"] == "CLOSED"
    metadata = json.loads(updated_parent["body"].split("\n", 2)[1])
    assert metadata["draft_sha256"] == "a" * 64
    assert metadata["binding_sha256"] == "b" * 64
    assert metadata["initial_graph_sha256"] == "c" * 64
    assert metadata["parent_identity"] == {"number": 724, "repo": REPO}
    assert metadata["progress"] == {"revision": 1}
    assert metadata["terminal_observation_path"].endswith("close-2.terminal.json")
    assert metadata["terminal_observation_sha256"] == emitted[0]["observation"]["terminal_sha256"]


@pytest.mark.parametrize("failure", ["malformed", "stale", "mismatched"])
def test_goal_run_close_rejects_bound_final_proof_before_provider(
    tmp_path: Path, failure: str
) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path)
    index = tmp_path / "final-proof-index.json"
    payload = json.loads(proof.read_text(encoding="utf-8"))
    if failure == "malformed":
        index.write_text("{", encoding="utf-8")
        payload["final_proof_index_sha256"] = hashlib.sha256(index.read_bytes()).hexdigest()
    elif failure == "stale":
        index.write_text(index.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    else:
        index_payload = json.loads(index.read_text(encoding="utf-8"))
        index_payload["repo"] = "corca-ai/other"
        index.write_text(json.dumps(index_payload), encoding="utf-8")
        payload["final_proof_index_sha256"] = hashlib.sha256(index.read_bytes()).hexdigest()
    proof.write_text(json.dumps(payload), encoding="utf-8")
    emitted: list[dict[str, object]] = []

    def must_not_select_backend(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("malformed, stale, or mismatched close input must not select a provider")

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=must_not_select_backend,
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["mutation_invoked"] is False
    assert emitted[0]["outcome"] == "refused"
    assert emitted[0]["status"] in {"input-invalid", "input-stale", "parent-mismatch"}
    assert not (tmp_path / "observations").exists()


def test_goal_run_close_reports_metadata_failure_after_verified_close(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-metadata-failure")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": '<!-- charness-goal-run:v1\n{"draft_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","binding_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}\n-->\n',
        "comments": [],
    }
    child = {"number": 725, "state": "CLOSED", "comments": [{"url": "comment"}]}
    reads: list[int] = []

    def read_issue(_repo: str, number: int, **_kwargs: object) -> dict[str, object]:
        reads.append(number)
        return {"issue": parent if number == 724 else child}

    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=read_issue
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {"children": [{"number": 725, "state": "CLOSED"}]},
        update_issue_body=lambda *_args, **_kwargs: {
            "ok": False,
            "status": "unverified-write",
            "outcome": "unverified-write",
            "mutation_invoked": True,
            "error": "provider readback failed",
        },
    )
    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=lambda *_args, **_kwargs: {"verified_state": {"state": "CLOSED"}}
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda _root, **_kwargs: {
            "adapter_ok": True,
            "backend": {"id": "gh"},
        },
        emit=emitted.append,
    )

    assert rc == 2
    assert reads == [724, 725]
    assert emitted[0]["ok"] is False
    assert emitted[0]["outcome"] == "unverified-write"
    assert emitted[0]["mutation_invoked"] is True
    assert "terminal observation exists" in emitted[0]["error"]
    assert (tmp_path / "observations/close-metadata-failure.terminal.json").is_file()


def test_goal_run_close_reports_parent_readback_failure_after_metadata_update(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    proof = _close_inputs(tmp_path, attempt_id="close-readback-failure")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": '<!-- charness-goal-run:v1\n{"draft_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","binding_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}\n-->\n',
        "comments": [],
    }
    child = {"number": 725, "state": "CLOSED", "comments": [{"url": "comment"}]}
    reads: list[int] = []

    def read_issue(_repo: str, number: int, **_kwargs: object) -> dict[str, object]:
        reads.append(number)
        if number == 724 and len(reads) > 2:
            return {"issue": {**parent, "state": "OPEN"}}
        return {"issue": parent if number == 724 else child}

    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=read_issue
    )

    def update_issue_body(_repo: str, _number: int, body_file: Path, **_kwargs: object) -> dict[str, object]:
        parent.update(state="CLOSED", body=body_file.read_text(encoding="utf-8"))
        return {
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "body_verified": True,
        }

    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {"children": [{"number": 725, "state": "CLOSED"}]},
        update_issue_body=update_issue_body,
    )
    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=lambda *_args, **_kwargs: {"verified_state": {"state": "CLOSED"}}
    )
    emitted: list[dict[str, object]] = []

    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 2
    assert reads == [724, 725, 724]
    assert emitted[0]["ok"] is False
    assert emitted[0]["outcome"] == "unverified-write"
    assert emitted[0]["mutation_invoked"] is True
    assert emitted[0]["terminal_metadata"]["ok"] is False
    assert (tmp_path / "observations/close-readback-failure.terminal.json").is_file()


def test_generic_close_refuses_goal_run_carrier_before_backend(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_BACKEND_PATH))
    body = tmp_path / "body.md"
    body.write_text(
        '<!-- charness-goal-run:v1\n{}\n-->\nAI-provenance: authored by an agent.\n',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="goal-run-close-required"):
        module["close_with_comment"](
            REPO,
            724,
            body,
            repo_root=tmp_path,
            classification="feature",
            backend={"id": "gh", "binary": "gh"},
        )


def test_goal_run_close_capability_reports_missing_close_ingress() -> None:
    contract = runpy.run_path(
        str(ROOT / "skills/public/issue/scripts/issue_goal_run_contract.py")
    )
    report = contract["capability_report"](
        {"id": "custom", "binary": "custom", "commands": {"view": ["view", "{repo}", "{number}"]}},
        ["close-goal-run"],
        repo=REPO,
    )

    assert report["ok"] is False
    assert "comment" in report["missing_backend_operations"]
    assert "close-goal-run" in report["missing_operations"]
