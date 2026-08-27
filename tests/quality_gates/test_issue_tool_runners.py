from __future__ import annotations

import json
import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from tests.quality_gates.support import ROOT

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
PLAN_SCRIPT = "skills/public/issue/scripts/issue_plan.py"


def test_backend_command_runner_reports_runtime_error(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_backend_command"]
    runner.__globals__["_resolve_backend"] = lambda _repo_root, _target_repo=None: {
        "adapter_ok": True,
        "backend": {"id": "fake-gh"},
    }
    runner.__globals__["emit"] = emitted.append

    def fail(_resolved: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("provider refused")

    rc = runner(Namespace(repo_root=tmp_path), fail, lambda _result: 0)

    assert rc == 2
    assert emitted == [
        {
            "ok": False,
            "error": "provider refused",
            "selected_backend": {"id": "fake-gh"},
        }
    ]


def test_backend_command_runner_reports_invalid_adapter(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_backend_command"]
    runner.__globals__["_resolve_backend"] = lambda _repo_root, _target_repo=None: {
        "adapter_ok": False,
        "adapter": {"valid": False, "errors": ["missing adapter"]},
    }
    runner.__globals__["emit"] = emitted.append

    rc = runner(Namespace(repo_root=tmp_path), lambda _resolved: {"ok": True}, lambda _result: 0)

    assert rc == 1
    assert emitted == [{"ok": False, "adapter": {"valid": False, "errors": ["missing adapter"]}}]


def test_backend_command_runner_attaches_backend_before_exit_code(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_backend_command"]
    runner.__globals__["_resolve_backend"] = lambda _repo_root, _target_repo=None: {
        "adapter_ok": True,
        "backend": {"id": "fake-gh"},
    }
    runner.__globals__["emit"] = emitted.append

    rc = runner(
        Namespace(repo_root=tmp_path),
        lambda _resolved: {"ok": False},
        lambda result: 7 if result["selected_backend"]["id"] == "fake-gh" else 9,
    )

    assert rc == 7
    assert emitted == [{"ok": False, "selected_backend": {"id": "fake-gh"}}]


def test_tracker_runner_persists_started_and_terminal_around_mutation(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_tracker_backend_command"]
    runner.__globals__["_resolve_backend"] = lambda _repo_root, _target_repo=None: {
        "adapter_ok": True,
        "backend": {"id": "gh", "binary": "gh", "commands": None},
    }
    runner.__globals__["emit"] = emitted.append
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    args = Namespace(
        repo_root=tmp_path,
        repo="corca-ai/charness",
        number=724,
        goal_run_parent=724,
        work_item_key="goal-run-parent",
        body_file=body,
        attempt_id="update-parent-1",
        draft_sha256="a" * 64,
        binding_sha256="b" * 64,
        observation_dir=Path("observations"),
    )

    rc = runner(
        args,
        "update-body",
        lambda _resolved: {
            "ok": True,
            "outcome": "verified-write",
            "mutation_invoked": True,
        },
    )

    assert rc == 0
    assert (tmp_path / "observations/update-parent-1.started.json").is_file()
    assert (tmp_path / "observations/update-parent-1.terminal.json").is_file()
    assert emitted[0]["observation"]["terminal_path"].endswith(".terminal.json")


def test_changed_body_cannot_reinvoke_ambiguous_create_for_same_work_item(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    create_calls = 0
    module["command_create_or_reuse_child"].__globals__["_resolve_backend"] = (
        lambda _repo_root, _target_repo=None: {
            "adapter_ok": True,
            "backend": {"id": "gh", "binary": "gh", "commands": None},
        }
    )
    module["command_create_or_reuse_child"].__globals__["emit"] = emitted.append

    tracker_module = module["TRACKER"]
    original_create = tracker_module.create_or_reuse_child

    def ambiguous_or_refuse(*_args, prior_unresolved_observation=None, **_kwargs):
        nonlocal create_calls
        if prior_unresolved_observation is not None:
            raise RuntimeError("prior matching provider attempt remains unresolved")
        create_calls += 1
        return {
            "ok": False,
            "status": "unverified-write",
            "outcome": "unverified-write",
            "mutation_invoked": True,
        }

    tracker_module.create_or_reuse_child = ambiguous_or_refuse
    try:
        common = {
            "repo_root": tmp_path,
            "repo": "corca-ai/charness",
            "parent_number": 724,
            "goal_run_parent": None,
            "number": None,
            "sub_issue_number": None,
            "work_item_key": "goal-binding-v1",
            "title": "Binding",
            "draft_sha256": "a" * 64,
            "binding_sha256": "b" * 64,
            "observation_dir": Path("observations"),
        }
        first_body = tmp_path / "first.md"
        first_body.write_text(
            "<!-- charness-work-item-key: goal-binding-v1 -->\nfirst\n",
            encoding="utf-8",
        )
        second_body = tmp_path / "second.md"
        second_body.write_text(
            "<!-- charness-work-item-key: goal-binding-v1 -->\nchanged\n",
            encoding="utf-8",
        )

        first_rc = module["command_create_or_reuse_child"](
            Namespace(**common, attempt_id="create-1", body_file=first_body)
        )
        second_rc = module["command_create_or_reuse_child"](
            Namespace(**common, attempt_id="create-2", body_file=second_body)
        )
    finally:
        tracker_module.create_or_reuse_child = original_create

    assert first_rc == 2
    assert second_rc == 2
    assert create_calls == 1
    assert emitted[1]["mutation_invoked"] is False
    assert "prior matching provider attempt" in emitted[1]["error"]


def test_tracker_preflight_combines_backend_capabilities_and_exact_parent(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    command = module["command_tracker_preflight"]
    command.__globals__["_resolve_backend"] = lambda _repo_root, _target_repo=None: {
        "adapter_ok": True,
        "adapter": {"valid": True},
        "backend": {"id": "gh", "binary": "gh", "commands": None},
    }
    command.__globals__["BACKEND"] = SimpleNamespace(
        build_preflight_payload=lambda _resolved: {
            "ok": True,
            "selected_backend": {
                "id": "gh",
                "binary": "gh",
                "found": True,
                "auth_status": {"exit_code": 0},
                "version": None,
            },
        }
    )
    command.__globals__["TRACKER"] = SimpleNamespace(
        tracker_capability_report=lambda _backend, **_kwargs: {
            "ok": True,
            "operations": {"create": True, "view": True, "update": True},
            "missing_operations": [],
        }
    )
    command.__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda _repo, _number, backend: {
            "issue": {
                "number": 724,
                "state": "OPEN",
                "url": "https://github.com/corca-ai/charness/issues/724",
                "updatedAt": "2026-08-26T00:00:00Z",
            }
        }
    )
    command.__globals__["emit"] = emitted.append

    rc = command(
        Namespace(repo_root=tmp_path, repo="corca-ai/charness", number=724)
    )

    assert rc == 0
    assert emitted[0]["kind"] == "charness.goal-run-bootstrap-preflight/v1"
    assert emitted[0]["status"] == "ready"
    assert emitted[0]["backend_readiness"]["auth_verified"] is True
    assert emitted[0]["parent"]["number"] == 724


def test_explicit_empty_expected_child_file_detects_unexpected_child(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    manifest = tmp_path / "children.json"
    manifest.write_text(
        json.dumps(
            {
                "kind": "charness.expected-sub-issue-set/v1",
                "repo": "corca-ai/charness",
                "parent_number": 724,
                "children": [],
            }
        ),
        encoding="utf-8",
    )
    command = module["command_list_sub_issues"]
    command.__globals__["_run_tracker_read_command"] = lambda args, build: build(
        {"backend": {"id": "gh"}}
    )
    command.__globals__["TRACKER"] = SimpleNamespace(
        load_expected_child_set=module["TRACKER"].load_expected_child_set,
        list_sub_issues=lambda *_args, **_kwargs: {
            "ok": True,
            "status": "verified-read",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "open": 1,
            "children": [{"number": 725}],
        },
    )

    result = command(
        Namespace(
            repo="corca-ai/charness",
            number=724,
            expect_child_file=manifest,
            expect_child=None,
            expect_all_closed=False,
        )
    )

    assert result["ok"] is False
    assert result["status"] == "graph-mismatch"
    assert result["expected_children"] == []
    assert result["unexpected_children"] == [725]


def test_tracker_bootstrap_commands_parse_with_complete_required_flags(tmp_path: Path) -> None:
    parser = runpy.run_path(str(ROOT / SCRIPT))["build_parser"]()
    common = [
        "--repo-root", str(tmp_path),
        "--attempt-id", "attempt-1",
        "--draft-sha256", "a" * 64,
        "--binding-sha256", "b" * 64,
        "--observation-dir", "observations",
    ]
    body = tmp_path / "body.md"

    create = parser.parse_args(
        [
            "create-or-reuse-child", "--repo", "corca-ai/charness",
            "--parent-number", "724", "--work-item-key", "goal-binding-v1",
            "--title", "Binding", "--body-file", str(body), *common,
        ]
    )
    update = parser.parse_args(
        [
            "update", "--repo", "corca-ai/charness", "--number", "724",
            "--goal-run-parent", "724", "--work-item-key", "goal-parent-v1",
            "--body-file", str(body), *common,
        ]
    )
    add = parser.parse_args(
        [
            "add-sub-issue", "--repo", "corca-ai/charness", "--number", "724",
            "--sub-issue-number", "725", "--work-item-key", "goal-binding-v1", *common,
        ]
    )

    assert create.func.__name__ == "command_create_or_reuse_child"
    assert update.func.__name__ == "command_update"
    assert add.func.__name__ == "command_add_sub_issue"


def test_adapter_payload_runner_reports_invalid_adapter(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_adapter_payload"]
    runner.__globals__["emit"] = emitted.append
    runner.__globals__["ADAPTER"] = SimpleNamespace(
        load_adapter=lambda _repo_root: {"valid": False, "errors": ["missing target"]}
    )

    rc = runner(Namespace(repo_root=tmp_path), lambda _adapter: {"ok": True})

    assert rc == 1
    assert emitted == [{"ok": False, "adapter": {"valid": False, "errors": ["missing target"]}}]


def test_adapter_payload_runner_reports_value_error(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    runner = module["_run_adapter_payload"]
    runner.__globals__["emit"] = emitted.append
    runner.__globals__["ADAPTER"] = SimpleNamespace(
        load_adapter=lambda _repo_root: {"valid": True, "data": {}}
    )

    def fail(_adapter: dict[str, object]) -> dict[str, object]:
        raise ValueError("bad selector")

    rc = runner(Namespace(repo_root=tmp_path), fail)

    assert rc == 2
    assert emitted == [{"ok": False, "error": "bad selector", "adapter": {"valid": True, "data": {}}}]


def test_resolve_target_command_uses_adapter_payload_runner(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    emitted: list[dict[str, object]] = []
    command = module["command_resolve_target"]
    command.__globals__["emit"] = emitted.append
    command.__globals__["ADAPTER"] = SimpleNamespace(
        load_adapter=lambda _repo_root: {"valid": True, "data": {"default_org": "corca-ai"}}
    )
    command.__globals__["RUNTIME"] = SimpleNamespace(
        resolve_target=lambda _repo_root, target, _adapter_data: {
            "full_name": f"corca-ai/{target}",
            "source": "test",
        }
    )

    rc = command(Namespace(repo_root=tmp_path, target="demo"))

    assert rc == 0
    assert emitted == [
        {
            "ok": True,
            "target": {"full_name": "corca-ai/demo", "source": "test"},
            "adapter": {"valid": True, "data": {"default_org": "corca-ai"}},
        }
    ]


def test_verify_closeout_command_delegates_to_backend_runner(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / SCRIPT))
    calls: list[str] = []
    command = module["command_verify_closeout"]
    command.__globals__["_run_backend_command"] = lambda _args, _call, _exit_code: calls.append("called") or 0

    rc = command(
        Namespace(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            number=[42],
            classification="bug",
            carrier="pr-body",
            commit_ref=None,
            pr_url=None,
            body_file=None,
            manual_fallback_reason=None,
            expect_state=None,
        )
    )

    assert rc == 0
    assert calls == ["called"]


def test_issue_plan_new_command_builds_new_plan(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / PLAN_SCRIPT))
    emitted: list[dict[str, object]] = []

    rc = module["command_plan"](
        Namespace(repo_root=tmp_path, intent="new", target="demo", values=[]),
        adapter_module=SimpleNamespace(
            load_adapter=lambda _repo_root: {
                "valid": True,
                "path": ".agents/issue-adapter.yaml",
                "data": {"feature_brief_pause": "on-open-decisions"},
            },
            DEFAULT_FEATURE_BRIEF_PAUSE="on-open-decisions",
        ),
        runtime_module=SimpleNamespace(
            resolve_target=lambda _repo_root, target, _adapter_data: {
                "full_name": f"corca-ai/{target}",
                "source": "test",
            }
        ),
        brief_module=SimpleNamespace(),
        backend_module=SimpleNamespace(
            build_preflight_payload=lambda _resolved: {
                "ok": True,
                "selected_backend": {
                    "id": "gh",
                    "found": True,
                    "authenticated": True,
                    "commands": ["gh issue create"],
                },
            }
        ),
        resolve_backend=lambda _repo_root: {"adapter_ok": True},
        emit=emitted.append,
    )

    assert rc == 0
    assert emitted[0]["intent"] == "new"
    assert emitted[0]["ok"] is True
    assert emitted[0]["target"]["full_name"] == "corca-ai/demo"
    assert emitted[0]["adapter"]["feature_brief_pause"] == "on-open-decisions"
    assert emitted[0]["required_reads"][0]["path"] == "references/issue-shaping.md"


def test_issue_plan_resolve_target_rejection_precedes_backend_preflight(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / PLAN_SCRIPT))
    emitted: list[dict[str, object]] = []

    def unexpected(_repo_root: Path) -> object:
        raise AssertionError("backend resolution should not run for an ignored resolve target")

    def unexpected_preflight(_resolved: object) -> object:
        raise AssertionError("backend preflight should not run for an ignored resolve target")

    def unexpected_invocation(*_args: object) -> object:
        raise AssertionError("resolve invocation should not run for an ignored target")

    rc = module["command_plan"](
        Namespace(repo_root=tmp_path, intent="resolve", target="corca-ai/other", values=["42"]),
        adapter_module=SimpleNamespace(
            load_adapter=lambda _repo_root: {
                "valid": True,
                "path": ".agents/issue-adapter.yaml",
                "data": {},
            },
            DEFAULT_FEATURE_BRIEF_PAUSE="on-open-decisions",
        ),
        runtime_module=SimpleNamespace(),
        brief_module=SimpleNamespace(build_invocation_payload=unexpected_invocation),
        backend_module=SimpleNamespace(build_preflight_payload=unexpected_preflight),
        resolve_backend=unexpected,
        emit=emitted.append,
    )

    assert rc == 2
    assert emitted == [
        {
            "ok": False,
            "error": "`--target` is only valid with `--intent new`; pass resolve repo/selector as positional values",
            "adapter": {
                "valid": True,
                "path": ".agents/issue-adapter.yaml",
                "data": {},
            },
        }
    ]
