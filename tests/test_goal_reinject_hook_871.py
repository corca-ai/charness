"""Goal Run re-injection hook: pointer after compaction (#871)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts import host_goal_reinject_hook as hook
from scripts.hooks import host_hook_goal_reinject_install as install
from scripts.hooks import host_hook_registry


def _checkout(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo


def _payload(repo: Path, source: str = "compact") -> dict:
    return {"source": source, "cwd": str(repo)}


def test_compaction_inside_checkout_prints_pointer(tmp_path: Path) -> None:
    repo = _checkout(tmp_path)
    install.record_active_goal_run(
        repo, number=12, ledger_path="charness-artifacts/goals/ledger.md"
    )

    code, message = hook.decide(_payload(repo))

    assert code == 0
    assert message == (
        "/goal #12\nledger: charness-artifacts/goals/ledger.md\nstatus: charness task status"
    )


def test_other_sources_outside_and_missing_run_print_nothing(tmp_path: Path) -> None:
    repo = _checkout(tmp_path)
    install.record_active_goal_run(repo, number=3, ledger_path="ledger.md")

    assert hook.decide(_payload(repo, source="startup")) == (0, "")
    assert hook.decide(_payload(repo, source="resume")) == (0, "")
    assert hook.decide(_payload(tmp_path / "elsewhere")) == (0, "")
    assert hook.decide(None) == (0, "")
    assert hook.decide({"source": "compact", "cwd": None}) == (0, "")

    install.clear_active_goal_run(repo)
    assert hook.decide(_payload(repo)) == (0, "")


def test_malformed_state_fails_open(tmp_path: Path, monkeypatch) -> None:
    repo = _checkout(tmp_path)
    state = repo / ".charness" / "host-hooks" / "state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text("{oops", encoding="utf-8")
    assert hook.decide(_payload(repo)) == (0, "")
    state.write_text(json.dumps({"goal-reinject:active": {"number": "x"}}), encoding="utf-8")
    assert hook.decide(_payload(repo)) == (0, "")
    monkeypatch.setattr(hook, "pointer_for", lambda *a, **k: 1 / 0)
    assert hook.decide(_payload(repo)) == (0, "")


def test_record_validates_and_roundtrips(tmp_path: Path) -> None:
    repo = _checkout(tmp_path)
    entry = install.record_active_goal_run(repo, number=7, ledger_path="  log.md  ")

    assert entry == {
        "number": 7,
        "ledger_path": "log.md",
        "status_command": "charness task status",
    }
    assert hook.pointer_for(repo) == "/goal #7\nledger: log.md\nstatus: charness task status"
    install.clear_active_goal_run(repo)
    assert hook.pointer_for(repo) is None
    for bad in (
        {"number": 0, "ledger_path": "log.md"},
        {"number": True, "ledger_path": "log.md"},
        {"number": 7, "ledger_path": ""},
        {"number": 7, "ledger_path": "log.md", "status_command": ""},
    ):
        try:
            install.record_active_goal_run(repo, **bad)
        except ValueError:
            continue
        raise AssertionError(f"record accepted {bad}")


def test_reconcile_installs_and_status_reports(tmp_path: Path) -> None:
    repo = _checkout(tmp_path)
    home = tmp_path / "home"
    adapter = {"goal_reinject": {"claude": "enabled"}}

    actions = host_hook_registry.reconcile_sibling_hooks(repo, adapter=adapter, home=home)
    assert actions["goal_reinject"]["claude"]["result"]["action"] in {
        "installed",
        "noop",
    }
    statuses = host_hook_registry.sibling_hook_statuses(repo, adapter=adapter, home=home)
    assert statuses["goal_reinject"]["in_sync"] is True

    removed = host_hook_registry.reconcile_sibling_hooks(repo, adapter={}, home=home)
    assert removed["goal_reinject"]["claude"]["result"]["action"] in {
        "removed",
        "absent",
        "not_installed",
    }
    assert (
        host_hook_registry.sibling_hook_statuses(repo, adapter={}, home=home)["goal_reinject"][
            "in_sync"
        ]
        is True
    )


def test_registry_carries_five_intents() -> None:
    keys = [intent.key for intent in host_hook_registry.SIBLING_HOOK_INTENTS]
    assert keys == [
        "skill_anchor_edit_guard",
        "command_guard_parallel_window",
        "command_guard_verdict_channel",
        "command_guard_discard_worktree",
        "goal_reinject",
    ]


def test_fresh_import_executes_reinject_bootstrap() -> None:
    import importlib.util

    from tests.module_eviction import evict_new_modules

    root = Path(__file__).resolve().parents[1]
    for relative, name in (
        ("scripts/host_goal_reinject_hook.py", "fresh_reinject_hook"),
        (
            "scripts/hooks/host_hook_goal_reinject_install.py",
            "fresh_reinject_install",
        ),
    ):
        spec = importlib.util.spec_from_file_location(name, root / relative)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        saved = sys.path[:]
        sys.path[:] = [
            entry
            for entry in saved
            if entry not in ("", str(root)) and __import__("os").path.abspath(entry) != str(root)
        ]
        before = set(sys.modules)
        try:
            sys.modules[name] = module
            spec.loader.exec_module(module)
        finally:
            sys.path[:] = saved
            evict_new_modules(before)
    assert module.ACTIVE_STATE_KEY == "goal-reinject:active"
