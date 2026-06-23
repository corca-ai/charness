from __future__ import annotations

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
    runner.__globals__["_resolve_backend"] = lambda _repo_root: {
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
    runner.__globals__["_resolve_backend"] = lambda _repo_root: {
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
    runner.__globals__["_resolve_backend"] = lambda _repo_root: {
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
