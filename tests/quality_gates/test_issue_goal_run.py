from __future__ import annotations

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


def _ready_provider(module: dict[str, object]) -> None:
    module["command_apply"].__globals__["_preflight"] = lambda **_kwargs: {
        "ok": True,
        "status": "ready",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "parent": {"number": 724, "state": "OPEN"},
    }


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
        resolve_backend=lambda _root: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["kind"] == "charness.goal-run-preflight/v1"
    assert emitted[0]["plan"]["sha256"]
    assert emitted[0]["plan"]["operations"] == ["read-body", "list-children"]


def test_goal_run_read_returns_parent_and_real_graph(tmp_path: Path) -> None:
    module = _provider()
    _ready_provider(module)
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
        resolve_backend=lambda _root: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["children"] == [{"number": 725, "state": "OPEN"}]
    assert emitted[0]["selected_backend"]["id"] == "gh"


def test_goal_run_apply_records_started_and_terminal_for_read(tmp_path: Path) -> None:
    module = _provider()
    _ready_provider(module)
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
        resolve_backend=lambda _root: {"adapter_ok": True, "backend": {"id": "gh", "binary": "gh"}},
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
        resolve_backend=lambda _root: {"adapter_ok": True, "backend": {"id": "unused"}},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["status"] == "local-only"
    assert emitted[0]["outcome"] == "verified-read"


def test_goal_run_apply_rejects_missing_operation_identity_before_provider(tmp_path: Path) -> None:
    module = _provider()
    operation = _operation(tmp_path, "read-state", {"repo": REPO})
    emitted: list[dict[str, object]] = []

    rc = module["command_apply"](
        Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
        resolve_backend=lambda _root: (_ for _ in ()).throw(AssertionError("must not resolve backend")),
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["error_code"] == "schema-invalid"
    assert emitted[0]["mutation_invoked"] is False


def test_goal_run_close_refuses_open_child_before_observation_or_close(tmp_path: Path) -> None:
    module = runpy.run_path(str(CLOSE_PATH))
    comment = tmp_path / "close.md"
    comment.write_text("Closes the Goal Run.\n", encoding="utf-8")
    proof = tmp_path / "proof.json"
    proof.write_text(
        json.dumps(
            {
                "kind": "charness.goal-run-close-proof/v1",
                "repo": REPO,
                "parent_number": 724,
                "attempt_id": "close-1",
                "draft_sha256": "a" * 64,
                "binding_sha256": "b" * 64,
                "observation_dir": "observations",
                "comment_file": "close.md",
                "whole_system_proof": True,
                "children": [
                    {
                        "repo": REPO,
                        "number": 725,
                        "evidence": {"kind": "issue-owned-closeout/v1", "identity": "comment"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    module["command_close"].__globals__["PROVIDER"]._preflight = lambda **_kwargs: {
        "ok": True,
        "parent": {
            "number": 724,
            "state": "OPEN",
            "body": '<!-- charness-goal-run:v1\n{"draft_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","binding_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}\n-->\n',
        },
    }
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
        resolve_backend=lambda _root: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted[0]["status"] == "close-refused"
    assert "not CLOSED" in emitted[0]["error"]
    assert not (tmp_path / "observations").exists()


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
    )

    assert report["ok"] is False
    assert "comment" in report["missing_backend_operations"]
    assert "close-goal-run" in report["missing_operations"]
