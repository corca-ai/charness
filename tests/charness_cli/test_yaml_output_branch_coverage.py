from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .test_managed_install import load_charness_module


def _doctor_payload() -> dict[str, object]:
    return {
        "codex_host_guidance": {},
        "claude_host_guidance": {},
        "grok_host_guidance": {},
        "repo_onboarding": {},
        "host_next_steps": {},
        "next_action": {},
        "checkout_version": "1.0.9",
        "codex_source_version": "1.0.9",
        "codex_cache_manifest_version": "1.0.9",
        "codex_source_cache_drift": False,
        "raw_probe_dump": "full host probe evidence",
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
        detail=False,
    )


def _patch_runtime_dependencies(module, monkeypatch, repo_root: Path, home_root: Path) -> None:
    runtime_paths = (home_root / "plugin", home_root / "marketplace.json", home_root / "claude", home_root / "cli")
    monkeypatch.setattr(module, "resolve_repo_root", lambda *_args: (repo_root, False))
    monkeypatch.setattr(module, "resolve_target_repo_root", lambda *_args: repo_root)
    monkeypatch.setattr(module, "enforce_managed_cli_contract", lambda **_kwargs: None)
    monkeypatch.setattr(module, "resolve_runtime_paths", lambda _args: runtime_paths)
    monkeypatch.setattr(module, "ensure_checkout", lambda *_args, **_kwargs: {"repo_root": str(repo_root)})
    monkeypatch.setattr(
        module, "maybe_reexec_refreshed_cli", lambda *_args, **_kwargs: {"status": "reexecuted", "checkout_cli": "checkout/charness"}
    )
    monkeypatch.setattr(module, "install_surface", lambda *_args, **_kwargs: {"host_next_steps": {}, "raw_install_trace": "verbose installer evidence"})
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
    init_output = yaml.safe_load(capsys.readouterr().out)
    assert init_output["response_level"] == "summary"
    assert init_output["checkout"]["repo_root"] == str(repo_root)
    assert init_output["cli_reexec"]["status"] == "reexecuted"
    assert "raw_install_trace" not in init_output

    args.detail = True
    assert module.cmd_init(args) == 0
    init_detail = yaml.safe_load(capsys.readouterr().out)
    assert init_detail["response_level"] == "detail"
    assert init_detail["raw_install_trace"] == "verbose installer evidence"
    args.detail = False

    assert module.cmd_update(args) == 0
    update_output = capsys.readouterr()
    assert yaml.safe_load(update_output.out)["response_level"] == "summary"
    assert yaml.safe_load(update_output.out)["scope"] == "self"
    assert yaml.safe_load(update_output.out)["cli_reexec"]["status"] == "reexecuted"
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
        detail=False,
    )
    assert module.cmd_doctor(doctor_args) == 0
    assert yaml.safe_load(capsys.readouterr().out)["next_action"] == "No manual host action is currently required."

    doctor_args.next_action = False
    assert module.cmd_doctor(doctor_args) == 0
    doctor_summary = yaml.safe_load(capsys.readouterr().out)
    assert doctor_summary["response_level"] == "summary"
    assert doctor_summary["checkout_version"] == "1.0.9"
    assert "raw_probe_dump" not in doctor_summary

    doctor_args.detail = True
    assert module.cmd_doctor(doctor_args) == 0
    doctor_detail = yaml.safe_load(capsys.readouterr().out)
    assert doctor_detail["response_level"] == "detail"
    assert doctor_detail["raw_probe_dump"] == "full host probe evidence"


def test_init_and_update_fail_on_explicit_host_delivery_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_host_delivery_exit_under_test")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _patch_runtime_dependencies(module, monkeypatch, repo_root, tmp_path / "home")
    monkeypatch.setattr(module, "maybe_install_codex_host", lambda **_kwargs: {"status": "failed", "reason": "post-readback"})
    args = _runtime_args(tmp_path / "home", repo_root)

    assert module.cmd_init(args) == 1
    init_payload = yaml.safe_load(capsys.readouterr().out)
    assert init_payload["codex_host_install"]["status"] == "failed"

    assert module.cmd_update(args) == 1
    update_payload = yaml.safe_load(capsys.readouterr().out)
    assert update_payload["codex_cache_refresh"]["status"] == "failed"


def test_update_all_failure_preserves_scope_in_recovery_action(tmp_path: Path, monkeypatch, capsys) -> None:
    module = load_charness_module("charness_update_all_failure_scope_under_test")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _patch_runtime_dependencies(module, monkeypatch, repo_root, tmp_path / "home")
    monkeypatch.setattr(
        module,
        "run_tool_update_flow",
        lambda **_kwargs: (
            {"results": {"nose": {"update": {"status": "failed"}}}},
            True,
        ),
    )
    args = _runtime_args(tmp_path / "home", repo_root)
    args.scope = "all"

    assert module.cmd_update(args) == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["scope"] == "all"
    assert payload["tool_update"]["status"] == "failed"
    assert payload["tool_update"]["failure_scope"] == "all"
    assert payload["tool_update"]["failed_tool_ids"] == ["nose"]
    assert payload["next_action"]["recovery_command"] == "charness update all --detail"
    assert "charness update all --detail" in payload["next_action"]["message"]
    assert "charness update all --detail" in payload["host_next_steps"]["external-tools"]


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
        detail=False,
    )

    assert module.cmd_tool_doctor(base_args) == 0
    doctor_output = yaml.safe_load(capsys.readouterr().out)
    assert doctor_output["response_level"] == "summary"
    assert doctor_output["results"] == {}

    base_args.tool_ids = ["unsupported-tool"]
    assert module.cmd_tool_repair(base_args) == 1
    repair_output = yaml.safe_load(capsys.readouterr().out)
    assert repair_output["response_level"] == "summary"
    assert "unsupported-tool" in repair_output["results"]

    base_args.tool_ids = []
    assert module.cmd_tool_sync_support(base_args) == 0
    sync_output = yaml.safe_load(capsys.readouterr().out)
    assert sync_output["response_level"] == "summary"
    assert sync_output["tool_ids"] == []

    assert module.cmd_tool_install(base_args) == 0
    install_output = yaml.safe_load(capsys.readouterr().out)
    assert install_output["response_level"] == "summary"
    assert install_output["results"] == {}

    monkeypatch.setattr(module, "run_tool_update_flow", lambda **_kwargs: ({"results": {}}, False))
    assert module.cmd_tool_update(base_args) == 0
    update_output = yaml.safe_load(capsys.readouterr().out)
    assert update_output["response_level"] == "summary"
    assert update_output["results"] == {}


def test_operational_response_detail_preserves_the_full_payload(capsys) -> None:
    module = load_charness_module("charness_yaml_detail_output_under_test")
    raw_payload = {
        "repo_root": "/tmp/charness",
        "results": {
            "demo": {
                "update": {"status": "updated", "commands": [{"command": "demo update"}]},
                "next_step": "No action required.",
            }
        },
    }

    module.emit_operational_response(
        Namespace(detail=False),
        raw_payload,
        event="tool-update",
        projector=lambda data: module.project_tool_response(data, event="tool-update"),
    )
    summary = yaml.safe_load(capsys.readouterr().out)
    assert summary["response_level"] == "summary"
    assert "commands" not in summary["results"]["demo"]["update"]

    module.emit_operational_response(
        Namespace(detail=True),
        raw_payload,
        event="tool-update",
        projector=lambda data: module.project_tool_response(data, event="tool-update"),
    )
    detail = yaml.safe_load(capsys.readouterr().out)
    assert detail["response_level"] == "detail"
    assert detail["results"]["demo"]["update"]["commands"] == [{"command": "demo update"}]


def test_doctor_rejects_conflicting_detail_and_next_action_flags() -> None:
    module = load_charness_module("charness_yaml_doctor_output_flags_under_test")

    with pytest.raises(SystemExit):
        module.build_parser().parse_args(["doctor", "--detail", "--next-action"])


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


def test_build_host_next_steps_includes_repo_onboarding_message() -> None:
    module = load_charness_module("charness_host_next_steps_repo_under_test")
    steps = module.build_host_next_steps(
        {
            "codex_host_guidance": {"message": "restart codex"},
            "claude_host_guidance": {},
            "repo_onboarding": {"message": "run `charness setup` in this repo"},
        }
    )
    assert steps == {"codex": "restart codex", "repo": "run `charness setup` in this repo"}


def test_install_surface_records_claude_plugin_message_in_host_next_steps(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_install_surface_claude_under_test")
    monkeypatch.setattr(module, "invoke_repo_script", lambda *args, **kwargs: '{"host_next_steps": {}}')
    monkeypatch.setattr(module, "invoke_repo_json_script", lambda *args, **kwargs: [])
    monkeypatch.setattr(module, "ensure_claude_marketplace", lambda *args, **kwargs: ([], "marketplace ready"))
    monkeypatch.setattr(
        module, "ensure_claude_plugin", lambda *args, **kwargs: (["claude_plugin_installed"], "Restart Claude Code to load charness.")
    )
    payload = module.install_surface(
        tmp_path / "repo",
        home_root=tmp_path / "home",
        plugin_root=tmp_path / "home" / "plugins" / "charness",
        codex_marketplace_path=tmp_path / "home" / ".codex" / "marketplace.json",
        claude_wrapper_path=None,
        cli_path=None,
        update=False,
    )
    assert payload["host_next_steps"]["claude"] == "Restart Claude Code to load charness."
    assert "claude_plugin_installed" in payload["completed_actions"]
