from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import yaml

from .test_managed_install import load_charness_module


def _doctor_payload() -> dict[str, object]:
    return {
        "codex_host_guidance": {},
        "claude_host_guidance": {},
        "repo_onboarding": {},
        "next_steps": {},
        "next_action": {},
        "checkout_version": "1.0.9",
        "codex_source_version": "1.0.9",
        "codex_cache_manifest_version": "1.0.9",
        "codex_source_cache_drift": False,
    }


def _runtime_args(home_root: Path, repo_root: Path) -> Namespace:
    return Namespace(
        home_root=home_root,
        repo_root=repo_root,
        target_repo_root=repo_root,
        repo_url="https://example.invalid/charness.git",
        skip_cli_install=True,
        skip_claude_wrapper=True,
        no_pull=True,
        skip_codex_cache_refresh=True,
        scope=None,
    )


def _patch_runtime_dependencies(module, monkeypatch, repo_root: Path, home_root: Path) -> None:
    runtime_paths = (home_root / "plugin", home_root / "marketplace.json", home_root / "claude", home_root / "cli")
    monkeypatch.setattr(module, "resolve_repo_root", lambda *_args: (repo_root, False))
    monkeypatch.setattr(module, "resolve_target_repo_root", lambda *_args: repo_root)
    monkeypatch.setattr(module, "enforce_managed_cli_contract", lambda **_kwargs: None)
    monkeypatch.setattr(module, "resolve_runtime_paths", lambda _args: runtime_paths)
    monkeypatch.setattr(module, "ensure_checkout", lambda *_args, **_kwargs: {"repo_root": str(repo_root)})
    monkeypatch.setattr(module, "install_surface", lambda *_args, **_kwargs: {"next_steps": {}})
    monkeypatch.setattr(module, "reconcile_usage_episodes_host_hooks", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "build_doctor_payload", lambda **_kwargs: _doctor_payload())
    monkeypatch.setattr(module, "maybe_install_codex_host", lambda **_kwargs: {"status": "skipped"})
    monkeypatch.setattr(module, "write_install_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "write_version_state", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(module, "write_host_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "build_version_provenance", lambda **_kwargs: {})
    monkeypatch.setattr(module, "codex_all_plugin_cache_entries", lambda _path: [])
    monkeypatch.setattr(module, "diff_cache_entries", lambda *_args: [])
    monkeypatch.setattr(module, "session_staleness_payload", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "latest_release_for_current_version", lambda *_args: None)
    monkeypatch.setattr(module, "packaging_version", lambda _path: "1.0.9")


def test_init_update_and_doctor_emit_yaml_on_all_public_paths(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_yaml_runtime_output_under_test")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _patch_runtime_dependencies(module, monkeypatch, repo_root, tmp_path / "home")
    args = _runtime_args(tmp_path / "home", repo_root)

    assert module.cmd_init(args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["checkout"]["repo_root"] == str(repo_root)

    assert module.cmd_update(args) == 0
    update_output = capsys.readouterr()
    assert yaml.safe_load(update_output.out)["scope"] == "self"
    assert "STEP: refreshing source checkout" in update_output.err
    assert "DONE: update complete" in update_output.err

    doctor_args = Namespace(
        home_root=tmp_path / "home",
        repo_root=repo_root,
        target_repo_root=repo_root,
        plugin_root=None,
        codex_marketplace_path=None,
        claude_wrapper_path=None,
        cli_path=None,
        next_action=True,
        write_state=False,
    )
    assert module.cmd_doctor(doctor_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["next_action"] == "No manual host action is currently required."

    doctor_args.next_action = False
    assert module.cmd_doctor(doctor_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["checkout_version"] == "1.0.9"


def test_task_and_uninstall_paths_emit_yaml(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_yaml_task_uninstall_under_test")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    task = {"task_id": "slice-1", "status": "claimed", "agent_id": "agent-a"}
    monkeypatch.setattr(module, "resolve_task_repo_root", lambda _args: repo_root)
    monkeypatch.setattr(module, "read_task", lambda *_args: task)

    assert module.cmd_task_claim(Namespace(task_id="slice-1", agent="agent-a", summary="")) == 0
    assert yaml.safe_load(capsys.readouterr().out)["event"] == "claim-existing"

    home_root = tmp_path / "home"
    _patch_runtime_dependencies(module, monkeypatch, repo_root, home_root)
    monkeypatch.setattr(module, "has_source_manifest", lambda _path: False)
    monkeypatch.setattr(module, "remove_codex_marketplace_entry", lambda _path: False)
    monkeypatch.setattr(module, "remove_codex_config_entries", lambda _path: [])
    uninstall_args = Namespace(
        home_root=home_root,
        repo_root=repo_root,
        plugin_root=None,
        codex_marketplace_path=None,
        claude_wrapper_path=None,
        cli_path=None,
        delete_checkout=False,
        delete_cli=False,
    )

    assert module.cmd_uninstall(uninstall_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["package_id"] == "charness"


def test_tool_command_outputs_are_routed_through_yaml(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_yaml_tool_output_under_test")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr(module, "resolve_tool_repo_root", lambda _args: (repo_root, False))
    monkeypatch.setattr(module, "default_plugin_root", lambda _path: tmp_path / "plugin")
    monkeypatch.setattr(module, "invoke_repo_json_script", lambda *_args, **_kwargs: [])
    base_args = Namespace(
        home_root=tmp_path / "home",
        repo_root=repo_root,
        plugin_root=None,
        tool_ids=[],
        no_write_locks=True,
        execute=False,
        upstream_checkout=[],
        dry_run=True,
        skip_sync_support=True,
        recommend_for_skill=None,
        recommendation_role=None,
        next_skill_id="quality",
    )

    assert module.cmd_tool_doctor(base_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["results"] == {}

    base_args.tool_ids = ["unsupported-tool"]
    assert module.cmd_tool_repair(base_args) == 1
    assert "unsupported-tool" in yaml.safe_load(capsys.readouterr().out)["results"]

    base_args.tool_ids = []
    assert module.cmd_tool_sync_support(base_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["tool_ids"] == []

    assert module.cmd_tool_install(base_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["results"] == {}

    monkeypatch.setattr(module, "run_tool_update_flow", lambda **_kwargs: ({"results": {}}, False))
    assert module.cmd_tool_update(base_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["results"] == {}


def test_worktree_and_goal_helper_fallback_keep_stdout_yaml(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_yaml_worktree_goal_output_under_test")

    class WorktreeAudit:
        PASS = "pass"
        WARN = "warn"
        FAIL = "fail"

        @staticmethod
        def run_audit(*_args, **_kwargs):
            return {"status": WorktreeAudit.PASS}

        @staticmethod
        def run_prune(*_args, **_kwargs):
            return {"status": WorktreeAudit.PASS, "remaining_after_prune": {"prunable": 0, "stale": 0}}

    class WorktreeCleanup:
        PASS = "pass"

        @staticmethod
        def run_cleanup(*_args, **_kwargs):
            return {"status": WorktreeCleanup.PASS}

    monkeypatch.setattr(module, "_load_worktree_audit_lib", lambda _args: WorktreeAudit)
    monkeypatch.setattr(module, "_load_worktree_cleanup_lib", lambda _args: WorktreeCleanup)
    monkeypatch.setattr(module, "_resolve_worktree_target", lambda _args: tmp_path)

    assert module.cmd_worktree_audit(Namespace(stale_days=30, doctor=False, prune=True)) == 0
    audit_output = yaml.safe_load(capsys.readouterr().out)
    assert audit_output["audit"]["status"] == "pass"
    assert audit_output["prune"]["status"] == "pass"

    cleanup_args = Namespace(path=None, delete_merged_branch=False, branch_base="main", yes=False, force=False)
    assert module.cmd_worktree_cleanup(cleanup_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "pass"

    monkeypatch.setattr(module, "_resolve_goal_helper_repo_root", lambda _args: tmp_path)
    monkeypatch.setattr(module, "_goal_check_script_args", lambda _args, _repo: [])
    monkeypatch.setattr(module, "resolve_repo_python", lambda _path: sys.executable)
    monkeypatch.setattr(
        module,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout="not json\n", stderr="helper warning\n", returncode=0),
    )

    assert module.cmd_goal_check(Namespace(repo_root=tmp_path)) == 0
    goal_output = capsys.readouterr()
    assert yaml.safe_load(goal_output.out) == {"helper_stdout": "not json"}
    assert goal_output.err == "helper warning\n"
