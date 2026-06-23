from __future__ import annotations

import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from tests.quality_gates.support import ROOT

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


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
