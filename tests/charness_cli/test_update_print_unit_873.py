from __future__ import annotations

import argparse
from pathlib import Path

import scripts.cli.cmd_update as cmd_update
import scripts.cli.tool_update as tool_update


def test_tool_update_lines_support_fallback_and_skip() -> None:
    payload = {
        "results": {
            "alpha": {"support": {"status": "ok"}},
            "beta": "not-a-dict",
            "gamma": {"update": {"status": "updated", "mode": "script"}},
            "delta": {"doctor": {"doctor_status": "healthy"}},
            "epsilon": {},
        }
    }
    lines = tool_update._tool_update_lines(payload)
    assert any(line.startswith("  - alpha: ok") for line in lines)
    assert any(line.startswith("  - gamma: updated") for line in lines)
    assert any(line.startswith("  - delta: healthy") for line in lines)
    assert any(line.startswith("  - epsilon: unknown") for line in lines)
    assert not any("beta" in line for line in lines)
    assert tool_update._tool_update_lines({"results": {}}) == []
    assert tool_update._tool_update_lines({"results": "nope"}) == []


def test_print_tool_human_summary_branches(capsys) -> None:
    payload = {
        "repo_root": "/r",
        "managed_checkout": True,
        "tool_ids": ["alpha"],
        "results": {"alpha": {"update": {"status": "ok"}}},
    }
    tool_update.print_tool_human_summary(payload)
    out = capsys.readouterr().out
    assert "REPO_ROOT: /r" in out
    assert "MANAGED_CHECKOUT: yes" in out
    assert "TOOLS: alpha" in out
    assert "alpha:" in out


def test_print_tool_human_summary_non_dict_results_and_entries(capsys) -> None:
    tool_update.print_tool_human_summary(
        {"repo_root": "/r", "managed_checkout": False, "results": "nope"}
    )
    out = capsys.readouterr().out
    assert "MANAGED_CHECKOUT: no" in out
    tool_update.print_tool_human_summary(
        {
            "repo_root": "/r",
            "managed_checkout": False,
            "tool_ids": "all",
            "results": {"alpha": "not-a-dict"},
        }
    )
    assert "REPO_ROOT: /r" in capsys.readouterr().out


def test_latest_release_for_current_version_shapes() -> None:
    assert cmd_update.latest_release_for_current_version(["x"], "1.0") is None
    payload = cmd_update.latest_release_for_current_version({"latest_version": "9.0.0"}, "1.0")
    assert payload is not None
    assert payload["current_version"] == "1.0"
    assert "update_available" in payload


def test_codex_all_plugin_cache_entries_delegates(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def _fake(cache_root: Path, *, plugin_glob: str):
        seen["root"] = cache_root
        seen["glob"] = plugin_glob
        return [{"plugin": "p"}]

    monkeypatch.setattr(cmd_update, "_codex_cache_entries", _fake)
    assert cmd_update.codex_all_plugin_cache_entries(tmp_path) == [{"plugin": "p"}]
    assert seen == {"root": tmp_path, "glob": "*"}


def test_diff_cache_entries_removed_rotated_added(tmp_path: Path) -> None:
    before = [
        {
            "marketplace": "m",
            "plugin": "gone",
            "version": "1",
            "version_dir": str(tmp_path / "missing-a"),
        },
        {
            "marketplace": "m",
            "plugin": "moved",
            "version": "1",
            "version_dir": str(tmp_path / "missing-b"),
        },
        {
            "marketplace": "m",
            "plugin": "stale",
            "version": "1",
            "version_dir": str(tmp_path / "missing-c"),
        },
    ]
    after = [
        {
            "marketplace": "m",
            "plugin": "moved",
            "version": "2",
            "version_dir": str(tmp_path / "missing-d"),
        },
        {
            "marketplace": "m",
            "plugin": "fresh",
            "version": "1",
            "version_dir": str(tmp_path / "missing-e"),
        },
    ]
    diff = cmd_update.diff_cache_entries(before, after)
    assert any(r["plugin"] == "gone" for r in diff["removed"])
    assert any(r["plugin"] == "stale" for r in diff["removed"])
    assert [r["plugin"] for r in diff["rotated"]] == ["moved"]
    assert [r["plugin"] for r in diff["added"]] == ["moved", "fresh"]
    live = tmp_path / "live"
    live.mkdir()
    kept = [
        {
            "marketplace": "m",
            "plugin": "kept",
            "version": "1",
            "version_dir": str(live),
        }
    ]
    assert cmd_update.diff_cache_entries(kept, []) == {
        "rotated": [],
        "removed": [],
        "added": [],
    }


def test_print_next_actions_preamble_and_dedup(capsys) -> None:
    payload = {
        "plugin_preamble": {"root_install_surface": {"ok": True}},
        "next_action": {"message": "do this", "host": "codex"},
        "codex_host_guidance": {"message": "do this"},
        "claude_host_guidance": {"message": "other"},
        "repo_onboarding": {"message": "third", "source": "x"},
    }
    cmd_update._print_next_actions(payload)
    out = capsys.readouterr().out
    assert "INSTALL_SURFACE: ok" in out
    assert out.count("do this") == 1
    assert "NEXT:" in out
    cmd_update._print_next_actions({})
    assert capsys.readouterr().out == ""
    cmd_update._print_next_actions(
        {"next_action": {"message": "repo thing", "source": "repo_onboarding"}}
    )
    assert "repo: repo thing" in capsys.readouterr().out


def _human_summary_payload() -> dict[str, object]:
    return {
        "package_id": "charness",
        "checkout_present": True,
        "repo_root": "/r",
        "checkout_version": "1.0",
        "checkout_git_head": "abc",
        "version_provenance": {"invocation_kind": "cli", "install_method": "clone"},
        "latest_release_check": {"status": "ok", "latest_tag": "v9"},
        "plugin_root_present": True,
        "plugin_root": "/p",
        "codex_source_version": "2.0",
    }


def test_print_human_summary_branches(monkeypatch, capsys) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        cmd_update, "_print_latest_release", lambda payload: calls.append("release")
    )
    monkeypatch.setattr(
        cmd_update, "_print_codex_marketplace", lambda payload: calls.append("market")
    )
    monkeypatch.setattr(cmd_update, "_print_codex_cache", lambda payload: calls.append("cache"))
    monkeypatch.setattr(cmd_update, "_print_codex_config", lambda payload: calls.append("config"))
    monkeypatch.setattr(
        cmd_update,
        "_print_claude_install_surface",
        lambda payload: calls.append("claude"),
    )
    cmd_update.print_human_summary(_human_summary_payload())
    out = capsys.readouterr().out
    assert "PACKAGE: charness" in out
    assert "CHECKOUT: present /r" in out
    assert "VERSION: 1.0" in out
    assert "GIT_HEAD: abc" in out
    assert "VERSION_PROVENANCE: cli clone" in out
    assert "PLUGIN_ROOT: present /p" in out
    assert "CODEX_SOURCE_VERSION: 2.0" in out
    assert calls == ["release", "market", "cache", "config", "claude"]


def _patch_update_printers(monkeypatch) -> None:
    monkeypatch.setattr(cmd_update, "_print_latest_release", lambda payload: None)
    monkeypatch.setattr(cmd_update, "_print_session_staleness", lambda payload: None)
    monkeypatch.setattr(cmd_update, "_print_next_actions", lambda payload: None)


def test_print_update_human_summary_version_branches(monkeypatch, capsys) -> None:
    _patch_update_printers(monkeypatch)
    monkeypatch.setattr(cmd_update, "_tool_update_lines", lambda payload: ["  - t: ok"])
    base: dict[str, object] = {
        "package_id": "charness",
        "checkout_git_head": "abc",
        "scope": "all",
        "completed_actions": ["did"],
        "checkout": {"pulled": True, "repo_root": "/r"},
        "tool_update": {"results": {"t": {}}},
    }
    changed = {**base, "previous_checkout_version": "1.0", "checkout_version": "2.0"}
    cmd_update.print_update_human_summary(changed)
    out = capsys.readouterr().out
    assert "VERSION: 1.0 -> 2.0" in out
    assert "GIT_HEAD: abc" in out
    assert "SCOPE: all" in out
    assert "TOOLS:" in out
    current_only = {"package_id": "charness", "checkout_version": "2.0"}
    cmd_update.print_update_human_summary(current_only)
    assert "VERSION: 2.0" in capsys.readouterr().out


def test_print_session_staleness_shapes(capsys) -> None:
    cmd_update._print_session_staleness("nope")
    assert capsys.readouterr().out == ""
    cmd_update._print_session_staleness({"affected": [], "message": "m"})
    assert capsys.readouterr().out == ""
    cmd_update._print_session_staleness({"affected": ["m/p 1 -> 2"], "message": "restart"})
    out = capsys.readouterr().out
    assert "SESSION_STALENESS" in out
    assert "m/p 1 -> 2" in out
    assert "restart" in out


def _doctor_payload() -> dict[str, object]:
    return {
        "codex_host_guidance": {"status": "installed"},
        "claude_host_guidance": {},
        "repo_onboarding": {},
        "host_next_steps": {},
        "next_action": {"message": "m"},
        "checkout_version": "2.0",
        "codex_source_version": "2.0",
        "codex_cache_manifest_version": "2.0",
        "codex_cache_manifest_status": "valid",
        "codex_source_cache_drift": None,
    }


def _patch_finish_update_common(monkeypatch, tmp_path: Path, seen: dict[str, object]):
    home_root = tmp_path / "home"
    repo_root = tmp_path / "repo"
    home_root.mkdir()
    repo_root.mkdir()
    monkeypatch.setattr(
        cmd_update,
        "install_surface",
        lambda *a, **k: {
            "package_id": "charness",
            "host_next_steps": {},
        },
    )
    monkeypatch.setattr(cmd_update, "build_doctor_payload", lambda **k: _doctor_payload())
    monkeypatch.setattr(cmd_update, "_record_post_delivery_readback", lambda *a, **k: None)
    monkeypatch.setattr(cmd_update, "build_version_provenance", lambda **k: {})
    monkeypatch.setattr(cmd_update, "write_host_state", lambda *a, **k: None)
    monkeypatch.setattr(cmd_update, "emit_progress", lambda *a, **k: None)

    def _emit(args, payload, *, event, projector) -> None:
        seen["payload"] = payload
        seen["event"] = event

    monkeypatch.setattr(cmd_update, "emit_operational_response", _emit)
    monkeypatch.setattr(cmd_update, "_mark_host_delivery_failure", lambda *a, **k: None)
    args = argparse.Namespace(
        skip_claude_wrapper=True,
        skip_cli_install=True,
        skip_codex_cache_refresh=True,
        scope="self",
    )
    paths = {
        "home_root": home_root,
        "target_repo_root": repo_root,
        "plugin_root": repo_root,
        "codex_marketplace_path": repo_root / "market",
        "claude_wrapper_path": repo_root / "wrapper",
        "cli_path": repo_root / "cli",
        "checkout": {"repo_root": str(repo_root)},
    }
    return args, paths


def test_finish_update_install_action_managed_tool_failure(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}
    args, paths = _patch_finish_update_common(monkeypatch, tmp_path, seen)
    args.scope = "all"
    monkeypatch.setattr(cmd_update, "codex_all_plugin_cache_entries", lambda root: [])
    monkeypatch.setattr(
        cmd_update,
        "maybe_install_codex_host",
        lambda **k: {"status": "attempted", "action": "install", "delivery_verified": True},
    )
    monkeypatch.setattr(cmd_update, "write_version_state", lambda *a, **k: {})
    monkeypatch.setattr(cmd_update, "write_install_state", lambda *a, **k: None)
    monkeypatch.setattr(
        cmd_update,
        "run_tool_update_flow",
        lambda **k: ({"results": {"t": {"update": {"status": "failed"}}}}, True),
    )
    rc = cmd_update.finish_update(
        args,
        home_root=paths["home_root"],
        managed_checkout=True,
        target_repo_root=paths["target_repo_root"],
        include_repo_onboarding=False,
        previous_checkout_version="1.0",
        plugin_root=paths["plugin_root"],
        codex_marketplace_path=paths["codex_marketplace_path"],
        claude_wrapper_path=paths["claude_wrapper_path"],
        cli_path=paths["cli_path"],
        checkout=paths["checkout"],
        cli_reexec_state=None,
    )
    assert rc == 1
    payload = seen["payload"]
    assert isinstance(payload, dict)
    assert "codex_host_installed" in payload["completed_actions"]
    assert payload["tool_update"]["status"] == "failed"


def test_finish_update_failed_readback_branch(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}
    args, paths = _patch_finish_update_common(monkeypatch, tmp_path, seen)
    monkeypatch.setattr(cmd_update, "codex_all_plugin_cache_entries", lambda root: [])
    monkeypatch.setattr(
        cmd_update,
        "maybe_install_codex_host",
        lambda **k: {"status": "attempted", "action": "install"},
    )
    states = [
        {"latest_release": {"status": "ok", "latest_tag": "v9.0.0", "latest_version": "9.0.0"}}
    ]
    monkeypatch.setattr(
        cmd_update, "write_version_state", lambda *a, **k: states.pop() if states else {}
    )
    rc = cmd_update.finish_update(
        args,
        home_root=paths["home_root"],
        managed_checkout=False,
        target_repo_root=paths["target_repo_root"],
        include_repo_onboarding=False,
        previous_checkout_version="1.0",
        plugin_root=paths["plugin_root"],
        codex_marketplace_path=paths["codex_marketplace_path"],
        claude_wrapper_path=paths["claude_wrapper_path"],
        cli_path=paths["cli_path"],
        checkout=paths["checkout"],
        cli_reexec_state=None,
    )
    assert rc == 1
    payload = seen["payload"]
    assert isinstance(payload, dict)
    assert payload["codex_cache_refresh"]["status"] == "failed"
    assert payload["codex_cache_refresh"]["reason"] == "install-incomplete"
    assert "error" in payload["codex_cache_refresh"]
    assert payload["latest_release_check"]["latest_tag"] == "v9.0.0"


def test_finish_update_success_refresh_and_tool_block(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}
    args, paths = _patch_finish_update_common(monkeypatch, tmp_path, seen)
    args.scope = "all"
    before = [
        {
            "marketplace": "m",
            "plugin": "p",
            "version": "1",
            "version_dir": str(tmp_path / "v1"),
        }
    ]
    after = [
        {
            "marketplace": "m",
            "plugin": "p",
            "version": "2",
            "version_dir": str(tmp_path / "v2"),
        }
    ]
    entries = [before, after]
    monkeypatch.setattr(cmd_update, "codex_all_plugin_cache_entries", lambda root: entries.pop(0))
    monkeypatch.setattr(
        cmd_update,
        "maybe_install_codex_host",
        lambda **k: {"status": "attempted", "action": "refresh", "delivery_verified": True},
    )
    monkeypatch.setattr(
        cmd_update,
        "write_version_state",
        lambda *a, **k: (
            {"latest_release": {"status": "ok", "latest_tag": "v9", "latest_version": "9.0.0"}}
            if "latest_release" not in k
            else {}
        ),
    )
    monkeypatch.setattr(
        cmd_update,
        "run_tool_update_flow",
        lambda **k: ({"results": {"t": {"update": {"status": "ok"}}}}, False),
    )
    rc = cmd_update.finish_update(
        args,
        home_root=paths["home_root"],
        managed_checkout=False,
        target_repo_root=paths["target_repo_root"],
        include_repo_onboarding=False,
        previous_checkout_version="1.0",
        plugin_root=paths["plugin_root"],
        codex_marketplace_path=paths["codex_marketplace_path"],
        claude_wrapper_path=paths["claude_wrapper_path"],
        cli_path=paths["cli_path"],
        checkout=paths["checkout"],
        cli_reexec_state={"reexec": True},
    )
    assert rc == 0
    payload = seen["payload"]
    assert isinstance(payload, dict)
    assert payload["codex_cache_refresh"]["status"] == "refreshed"
    assert "codex_cache_refreshed" in payload["completed_actions"]
    assert "session_staleness" in payload
    assert "external_tools_updated" in payload["completed_actions"]
    assert payload["latest_release_check"]["latest_tag"] == "v9"
