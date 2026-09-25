"""Bootstrap preamble: reinsert a missing repo root on import (#873 split).

Every `scripts/cli/*` module self-roots at import so a copied CLI still finds
its tree. The suite always runs with the root on `sys.path`, so the insert
branch needs a test that removes the root first.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from tests.module_eviction import evict_module
from tests.repo_copy import ROOT

MODULES = [
    "scripts.cli.bootstrap",
    "scripts.cli.bootstrap_probe",
    "scripts.cli.bootstrap_state",
    "scripts.cli.capability_support",
    "scripts.cli.cmd_capability",
    "scripts.cli.cmd_catalog",
    "scripts.cli.cmd_doctor",
    "scripts.cli.cmd_goal",
    "scripts.cli.cmd_hooks",
    "scripts.cli.cmd_init",
    "scripts.cli.cmd_meta",
    "scripts.cli.cmd_task",
    "scripts.cli.cmd_train",
    "scripts.cli.cmd_update",
    "scripts.cli.cmd_worktree",
    "scripts.cli.common",
    "scripts.cli.doctor_payload",
    "scripts.cli.host_claude",
    "scripts.cli.host_codex",
    "scripts.cli.host_codex_rpc",
    "scripts.cli.install_delivery",
    "scripts.cli.process",
    "scripts.cli.tool_commands",
    "scripts.cli.tool_response",
    "scripts.cli.tool_update",
    "scripts.task_run.task_run_status_report",
]


def _without_repo_root() -> list[str]:
    return [
        entry
        for entry in sys.path
        if Path(entry or ".").resolve() != ROOT.resolve()
    ]


@pytest.mark.parametrize("module_name", MODULES)
def test_preamble_reinserts_missing_repo_root(monkeypatch, module_name: str) -> None:
    evict_module(monkeypatch, module_name)
    stripped = _without_repo_root()
    assert len(stripped) < len(sys.path)
    monkeypatch.setattr(sys, "path", stripped)
    module = importlib.import_module(module_name)
    assert module.__name__ == module_name
    assert sys.path[0] == str(ROOT.resolve())
