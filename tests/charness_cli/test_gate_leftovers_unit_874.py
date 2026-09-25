"""Leftover changed-line coverage for the release gate (#874).

Minimal in-process unit tests hitting the exact lines listed by the
changed-line gate. Conventions: plain pytest, tmp_path/monkeypatch, no
network, no real HOME writes. Wall-clock dates are computed relative to
now, never hardcoded.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# --- scripts/cli/bootstrap.py: 259, 291 ---


def test_default_bootstrap_repo_url_returns_configured() -> None:
    from scripts.cli import bootstrap

    assert (
        bootstrap.default_bootstrap_repo_url(Path("/tmp/home"), "https://example.invalid/r")
        == "https://example.invalid/r"
    )


def test_ensure_checkout_rejects_tracked_changes(tmp_path: Path, monkeypatch) -> None:
    from scripts.cli import bootstrap

    monkeypatch.setattr(bootstrap, "has_source_manifest", lambda _path: True)
    monkeypatch.setattr(bootstrap, "is_git_checkout", lambda _path: True)
    monkeypatch.setattr(bootstrap, "git_has_tracked_changes", lambda _path: True)
    with pytest.raises(bootstrap.CharnessError, match="tracked local changes"):
        bootstrap.ensure_checkout(
            tmp_path,
            managed=True,
            repo_url="https://example.invalid/r",
            allow_clone=False,
            allow_pull=True,
        )


# --- scripts/cli/bootstrap_state.py: 278, 285, 305, 382 ---


def test_should_auto_refresh_disabled_by_env(monkeypatch) -> None:
    import scripts.cli.bootstrap_state as bs

    monkeypatch.setenv("CHARNESS_NO_UPDATE_CHECK", "1")
    args = argparse.Namespace(command="doctor", check=False)
    assert (
        bs.should_auto_refresh_self_release(args, {"eligible_for_auto_update_check": True}) is False
    )


def test_should_auto_refresh_tty_fallback(monkeypatch) -> None:
    import scripts.cli.bootstrap_state as bs

    for var in ("CHARNESS_NO_UPDATE_CHECK", "CHARNESS_FORCE_UPDATE_CHECK", "CI"):
        monkeypatch.delenv(var, raising=False)
    stub = SimpleNamespace(
        stdout=SimpleNamespace(isatty=lambda: True),
        stderr=SimpleNamespace(isatty=lambda: True),
    )
    monkeypatch.setattr(bs, "sys", stub)
    args = argparse.Namespace(command="doctor", check=False)
    assert (
        bs.should_auto_refresh_self_release(args, {"eligible_for_auto_update_check": True}) is True
    )


def test_maybe_record_self_version_state_skips_update(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.bootstrap_state as bs

    monkeypatch.setattr(bs, "resolve_repo_root", lambda _home, _explicit: (tmp_path, False))
    monkeypatch.setattr(
        bs, "build_version_provenance", lambda **_kwargs: {"current_version": "1.0.0"}
    )
    monkeypatch.setattr(bs, "write_version_state", lambda _home, **_kwargs: {"latest_release": {}})

    def _must_not_refresh(_args, _provenance):
        raise AssertionError("should not refresh for the update command")

    monkeypatch.setattr(bs, "should_auto_refresh_self_release", _must_not_refresh)
    args = argparse.Namespace(command="update", home_root=tmp_path, repo_root=None, cli_path=None)
    bs.maybe_record_self_version_state(args)


def test_source_checkout_under_work_none_repo_root() -> None:
    import scripts.cli.bootstrap_state as bs

    assert bs._source_checkout_under_work(SimpleNamespace(repo_root=None)) is None


# --- scripts/cli/capability_support.py: 53, 97 ---


def test_read_json_mapping_returns_default_for_non_dict(tmp_path: Path) -> None:
    import scripts.cli.capability_support as cap

    path = tmp_path / "capability.json"
    path.write_text("[1, 2]", encoding="utf-8")
    assert cap.read_json_mapping(path, default={"a": 1}) == {"a": 1}


def test_load_repo_capability_config_rejects_bad_access_mode(tmp_path: Path) -> None:
    import scripts.cli.capability_support as cap

    path = tmp_path / ".charness" / "local" / "capability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "bindings": {},
                "profiles": {"p": {"provider": "g", "access_mode_preference": "direct"}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(cap.CharnessError, match="access_mode_preference"):
        cap.load_repo_capability_config(tmp_path)


# --- scripts/cli/cmd_capability.py: 194, 369 ---


def test_explain_announcement_notes_missing_delivery_capability(
    tmp_path: Path, monkeypatch
) -> None:
    import scripts.cli.cmd_capability as cc

    monkeypatch.setattr(
        cc,
        "load_skill_capability_needs",
        lambda _root, _skill: {"path": "p", "capability_needs": [], "notes": ["n0"]},
    )
    monkeypatch.setattr(
        cc,
        "invoke_repo_json_script",
        lambda *args, **kwargs: {
            "data": {"delivery_kind": "human-backend", "delivery_capability": ""},
            "delivery_contract": {"status": "executable", "blocking_issues": []},
        },
    )
    response = cc.explain_skill_capabilities(
        charness_repo_root=tmp_path, target_repo_root=tmp_path, skill_id="announcement"
    )
    assert any("delivery_capability" in note for note in response["notes"])


def test_capability_env_raises_on_missing_source_env(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.cmd_capability as cc

    monkeypatch.setattr(cc, "_resolve_charness_repo_root", lambda _args: tmp_path)
    monkeypatch.setattr(cc, "resolve_target_repo_root", lambda _path: tmp_path)
    monkeypatch.setattr(
        cc,
        "resolve_capability",
        lambda **_kwargs: {
            "profile_id": "p",
            "env_bindings": {"OUT_VAR": "SRC_VAR"},
            "env_binding_status": {"OUT_VAR": {"source_env": "SRC_VAR", "present": False}},
        },
    )
    args = argparse.Namespace(target_repo_root=tmp_path, logical_id="llm")
    with pytest.raises(cc.CharnessError, match="missing source env"):
        cc.cmd_capability_env(args)


# --- scripts/cli/cmd_goal.py: 101 ---


def test_cmd_goal_run_emits_dict_payload(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.cmd_goal as goal

    monkeypatch.setattr(goal, "_resolve_goal_run_helper_repo_root", lambda _args: tmp_path)
    monkeypatch.setattr(goal, "resolve_repo_python", lambda _root: sys.executable)
    monkeypatch.setattr(
        goal,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout='{"status": "ok"}', stderr="", returncode=0),
    )
    seen: list[object] = []
    monkeypatch.setattr(goal, "emit_yaml", seen.append)
    args = argparse.Namespace(repo_root=tmp_path, objective="demo")
    assert goal.cmd_goal_run(args) == 0
    assert seen == [{"status": "ok"}]


# --- scripts/cli/cmd_meta.py: 165 ---


def test_remove_claude_marketplace_no_cli_returns_false(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.cmd_meta as meta

    monkeypatch.setattr(meta.shutil, "which", lambda _cmd: None)
    assert meta.remove_claude_marketplace(tmp_path, home_root=tmp_path) is False


def test_remove_claude_marketplace_success_via_host_module(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.cmd_meta as meta
    import scripts.cli.host_claude as host_claude

    monkeypatch.setattr(meta.shutil, "which", lambda _cmd: "/usr/bin/claude")
    calls: list[list[str]] = []

    def _fake_run_claude(command: list[str], *, cwd: Path, home_root: Path):
        calls.append(command)
        return SimpleNamespace(stdout="removed", stderr="", returncode=0)

    monkeypatch.setattr(host_claude, "run_claude", _fake_run_claude)
    monkeypatch.setattr(meta, "remove_claude_marketplace_entry", lambda _path, _name: False)
    assert meta.remove_claude_marketplace(REPO_ROOT, home_root=tmp_path) is True
    assert calls and calls[0][:4] == ["claude", "plugins", "marketplace", "remove"]


# --- scripts/cli/doctor_payload.py: 188, 487 ---


def test_build_doctor_next_action_falls_back_to_none() -> None:
    from scripts.cli import doctor_payload as dp

    assert dp.build_doctor_next_action({})["kind"] == "none"
    unavailable = {
        f"{host}_host_guidance": {
            "status": "unavailable",
            "manual_action_required": False,
            "message": f"{host} missing",
        }
        for host in ("codex", "claude", "grok")
    }
    assert dp.build_doctor_next_action(unavailable)["kind"] == "none"


def test_build_doctor_payload_skips_repo_onboarding(tmp_path: Path, monkeypatch) -> None:
    from scripts.cli import bootstrap as _bootstrap_module
    from scripts.cli import doctor_payload as dp

    # Bare pytest never sets the CLI entry point; provenance only resolves it.
    monkeypatch.setattr(_bootstrap_module, "SCRIPT_PATH", REPO_ROOT / "charness")
    payload = dp.build_doctor_payload(
        home_root=tmp_path / "home",
        repo_root=REPO_ROOT,
        managed_checkout=False,
        target_repo_root=REPO_ROOT,
        plugin_root=tmp_path / "plugin",
        codex_marketplace_path=tmp_path / "marketplace.json",
        cli_path=tmp_path / "charness",
        claude_wrapper_path=tmp_path / "claude-charness",
        include_repo_onboarding=False,
        include_latest_host_operation=False,
    )
    assert payload["repo_onboarding"]["status"] == "skipped"


# --- scripts/cli/host_claude.py: 118, 153, 335 ---


def test_claude_installed_plugin_empty_entries_returns_none(tmp_path: Path) -> None:
    import scripts.cli.host_claude as hc

    path = tmp_path / "installed.json"
    path.write_text(json.dumps({"plugins": {"ref": []}}), encoding="utf-8")
    assert hc.claude_installed_plugin(path, "ref") is None


def test_ensure_claude_marketplace_skips_without_cli(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.host_claude as hc

    monkeypatch.setenv("PATH", str(tmp_path))
    actions, message = hc.ensure_claude_marketplace(tmp_path, home_root=tmp_path)
    assert actions == []
    assert "skipped" in message.lower()


def test_build_claude_host_guidance_needs_enable(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.host_claude as hc

    monkeypatch.setattr(hc.shutil, "which", lambda _cmd: "/usr/bin/claude")
    guidance = hc.build_claude_host_guidance(
        repo_root=REPO_ROOT,
        home_root=tmp_path,
        source_manifest_present=True,
        marketplace_entry={"source": {}},
        installed_entry={"version": "local"},
        enabled_status={"present": True, "enabled": False},
    )
    assert guidance["status"] == "needs-enable"


# --- scripts/cli/process.py: 73, 253, 273 ---


def test_resolve_repo_python_returns_cached(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.process as proc

    monkeypatch.setattr(proc, "_configure_runtime_for_repo", lambda _repo: None)
    resolved = str(tmp_path.resolve())
    monkeypatch.setitem(proc._BOOTSTRAP_PYTHON_CACHE, resolved, "/cached/python")
    assert proc.resolve_repo_python(tmp_path) == "/cached/python"


def _symlinked_repo_root(tmp_path: Path) -> Path:
    link = tmp_path / "repo-link"
    if not link.exists():
        link.symlink_to(REPO_ROOT, target_is_directory=True)
    return link


def test_load_worktree_cleanup_lib_inserts_new_lib_root(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.process as proc

    link = _symlinked_repo_root(tmp_path)
    assert str(link) not in sys.path
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda _args: link)
    try:
        assert proc._load_worktree_cleanup_lib(SimpleNamespace()) is not None
        assert str(link) in sys.path
    finally:
        while str(link) in sys.path:
            sys.path.remove(str(link))


def test_load_worktree_exec_lib_inserts_new_lib_root(tmp_path: Path, monkeypatch) -> None:
    import scripts.cli.process as proc

    link = _symlinked_repo_root(tmp_path)
    assert str(link) not in sys.path
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda _args: link)
    monkeypatch.setattr(proc, "_resolve_worktree_target", lambda _args: tmp_path)
    monkeypatch.setattr(proc, "_configure_runtime_for_repo", lambda _repo: None)
    try:
        assert proc._load_worktree_exec_lib(SimpleNamespace()) is not None
        assert str(link) in sys.path
    finally:
        while str(link) in sys.path:
            sys.path.remove(str(link))


# --- scripts/task_run/task_run_status_report.py: 218, 280 ---


def test_friction_section_reports_skipped_lines() -> None:
    from scripts.task_run import task_run_status_report as sr

    section = sr._friction_section([], skipped=2)
    assert "2 unreadable line(s) skipped." in section


def test_decisions_section_reports_skipped_lines() -> None:
    from scripts.task_run import task_run_status_report as sr

    section = sr._decisions_section([], skipped=1, friction=[])
    assert "1 unreadable line(s) skipped" in section


# --- scripts/task_run/task_run_train_core.py: 363 ---


def test_validate_loosening_rejects_non_numeric_bound() -> None:
    from scripts.task_run.task_run_train_core import _validate_loosening

    errors: list[str] = []
    _validate_loosening({"min_lands": "lots"}, errors)
    assert any("must be a number" in error for error in errors)


# --- scripts/task_run/task_run_train_stats.py ---


def test_load_repo_runtime_bootstrap_reinserts_root() -> None:
    import scripts.task_run.task_run_train_stats as ts

    root = next(
        p
        for p in Path(ts.__file__).resolve().parents
        if (p / "scripts" / "adapter_lib.py").is_file()
    )
    assert str(root) in sys.path
    while str(root) in sys.path:
        sys.path.remove(str(root))
    try:
        ts._load_repo_runtime_bootstrap()
        assert str(root) in sys.path
    finally:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))


def test_parse_time_branches() -> None:
    import scripts.task_run.task_run_train_stats as ts

    assert ts._parse_time(123) is None
    assert ts._parse_time("  ") is None
    assert ts._parse_time("not-a-date") is None
    assert ts._parse_time("2026-01-01T00:00:00") is None
    moment = datetime.now(timezone.utc)
    assert ts._parse_time(moment.isoformat()) is not None


def test_record_landing_fail_open_on_os_error(tmp_path: Path, monkeypatch) -> None:
    import scripts.task_run.task_run_train_stats as ts

    def _boom(_repo_root: Path):
        raise OSError("disk gone")

    monkeypatch.setattr(ts, "task_runtime_root", _boom)
    assert (
        ts.record_landing_for_repo(
            tmp_path, base_sha="a", landed_sha="b", branches=["main"], run_id="r1"
        )
        is None
    )


def test_read_landings_skips_blank_and_malformed(tmp_path: Path) -> None:
    import scripts.task_run.task_run_train_stats as ts

    runtime_path = tmp_path / "runtime"
    path = ts.landing_path(runtime_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    record = {"occurred_at": stamp, "branches": ["main"]}
    path.write_text(f"\n{json.dumps(record)}\n{{bad json\n\n", encoding="utf-8")
    assert ts.read_landings(runtime_path) == [record]


def test_iter_lane_results_skips_bad_payloads(tmp_path: Path) -> None:
    import scripts.task_run.task_run_train_stats as ts

    runtime_path = tmp_path / "runtime"
    bad = runtime_path / "task-run" / "a" / "result.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{not json", encoding="utf-8")
    non_dict = runtime_path / "task-run" / "b" / "result.json"
    non_dict.parent.mkdir(parents=True, exist_ok=True)
    non_dict.write_text("[1, 2]", encoding="utf-8")
    good = runtime_path / "task-run" / "c" / "result.json"
    good.parent.mkdir(parents=True, exist_ok=True)
    good.write_text(json.dumps({"status": "ok", "task_id": "t"}), encoding="utf-8")
    found = ts.iter_lane_results(runtime_path)
    assert [payload for _, payload in found] == [{"status": "ok", "task_id": "t"}]


def test_iter_lane_results_skips_stat_failures(tmp_path: Path, monkeypatch) -> None:
    import scripts.task_run.task_run_train_stats as ts

    runtime_path = tmp_path / "runtime"
    good = runtime_path / "task-run" / "c" / "result.json"
    good.parent.mkdir(parents=True, exist_ok=True)
    good.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    original_stat = Path.stat
    seen: dict[str, int] = {}

    def _flaky_stat(self: Path):
        # `glob` stats each candidate once during traversal; fail only the
        # explicit `path.stat()` read so line 155-156 is the one exercised.
        key = str(self)
        seen[key] = seen.get(key, 0) + 1
        if self.name == "result.json" and seen[key] >= 2:
            raise OSError("stat gone")
        return original_stat(self)

    monkeypatch.setattr(Path, "stat", _flaky_stat)
    assert ts.iter_lane_results(runtime_path) == []


def test_evaluate_loosening_rate_wait_and_waste_branches() -> None:
    import scripts.task_run.task_run_train_stats as ts

    base = {
        "lands_in_window": 0,
        "landings_per_hour": 0.0,
        "median_queue_wait_minutes": None,
        "wasted": 0,
    }
    slow = ts.evaluate_loosening(base, {"min_lands": 2, "min_landings_per_hour": 5.0})
    assert slow["ok"] is False
    assert any("below" in reason for reason in slow["reasons"])
    assert any("only 0 lands" in reason for reason in slow["reasons"])
    no_wait = ts.evaluate_loosening({**base, "lands_in_window": 3}, {"max_queue_wait_minutes": 10})
    assert any("no landed lane" in reason for reason in no_wait["reasons"])
    over_wait = ts.evaluate_loosening(
        {**base, "lands_in_window": 3, "median_queue_wait_minutes": 30.0},
        {"max_queue_wait_minutes": 10},
    )
    assert any("above" in reason for reason in over_wait["reasons"])
    waste = ts.evaluate_loosening({**base, "wasted": 1}, {"require_no_waste": True})
    assert any("wasted" in reason for reason in waste["reasons"])


def test_train_stats_skips_branchless_and_stale_lanes(tmp_path: Path) -> None:
    import scripts.task_run.task_run_train_stats as ts

    now = datetime.now(timezone.utc)
    runtime_path = ts.task_runtime_root(tmp_path.resolve())
    branchless = runtime_path / "task-run" / "lane1" / "result.json"
    branchless.parent.mkdir(parents=True, exist_ok=True)
    branchless.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    stale = runtime_path / "task-run" / "lane2" / "result.json"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text(
        json.dumps({"status": "ok", "branch": "main", "task_id": "t1"}), encoding="utf-8"
    )
    old = now - timedelta(hours=3)
    os.utime(stale, (old.timestamp(), old.timestamp()))
    stats = ts.train_stats_for_repo(tmp_path, window_hours=1.0, now=now)
    assert stats["launched"] == 2
    assert stats["lanes_waiting"] == []
    assert stats["wasted"] == 0
