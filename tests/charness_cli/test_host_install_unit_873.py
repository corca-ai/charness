"""Direct unit tests for host/install/process/common/rpc/doctor branches (#873)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.cli.common as common
import scripts.cli.doctor_payload as dp
import scripts.cli.host_claude as hc
import scripts.cli.host_codex_rpc as rpc
import scripts.cli.install_delivery as delivery
import scripts.cli.process as proc
import scripts.runtime_bootstrap as rb


def _result(returncode: int = 0, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_write_claude_wrapper_materializes_script(tmp_path: Path) -> None:
    wrapper = tmp_path / "bin" / "claude-charness"
    hc.write_claude_wrapper(wrapper, tmp_path / "plugin")
    text = wrapper.read_text(encoding="utf-8")
    assert "exec claude --plugin-dir" in text
    assert str(tmp_path / "plugin") in text


def test_install_cli_binary_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(hc.CharnessError):
        hc.install_cli_binary(tmp_path / "charness", source_path=tmp_path / "absent")


def test_install_cli_binary_copies_new_target(tmp_path: Path) -> None:
    source = tmp_path / "charness-src"
    source.write_text("#!/bin/sh\n", encoding="utf-8")
    target = tmp_path / "bin" / "charness"
    hc.install_cli_binary(target, source_path=source)
    assert target.read_text(encoding="utf-8") == "#!/bin/sh\n"


def test_claude_installed_plugin_rejects_non_dict_plugins(tmp_path: Path) -> None:
    path = tmp_path / "installed_plugins.json"
    path.write_text(json.dumps({"plugins": ["x"]}), encoding="utf-8")
    assert hc.claude_installed_plugin(path, "charness@mkt") is None


def test_claude_enabled_status_returns_none_without_cli(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert hc.claude_enabled_status(tmp_path, home_root=tmp_path) is None


def test_claude_enabled_status_reports_failed_probe(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/claude")
    monkeypatch.setattr(
        hc, "run_claude", lambda *args, **kwargs: _result(returncode=1, stdout="o", stderr="e")
    )
    status = hc.claude_enabled_status(tmp_path, home_root=tmp_path)
    assert status == {"ok": False, "raw": "oe"}


def test_ensure_claude_marketplace_reports_configured(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/claude")
    monkeypatch.setattr(hc, "claude_marketplace_name", lambda repo_root: "mkt")
    monkeypatch.setattr(
        hc, "claude_known_marketplace", lambda path, name: {"source": {"path": str(tmp_path)}}
    )
    actions, message = hc.ensure_claude_marketplace(tmp_path, home_root=tmp_path)
    assert actions == []
    assert "already configured" in message


def test_ensure_claude_plugin_skips_without_cli(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    actions, message = hc.ensure_claude_plugin(tmp_path, home_root=tmp_path, update=False)
    assert actions == []
    assert "skipped" in message


def _packaging_repo(root: Path) -> Path:
    (root / "packaging").mkdir(parents=True, exist_ok=True)
    (root / "packaging" / "charness.json").write_text(
        json.dumps({"claude": {"marketplace": {"name": "mkt"}}}), encoding="utf-8"
    )
    return root


def test_build_claude_host_guidance_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    guidance = hc.build_claude_host_guidance(
        repo_root=Path("/r"),
        home_root=Path("/h"),
        source_manifest_present=True,
        marketplace_entry={},
        installed_entry={},
        enabled_status={},
    )
    assert guidance["status"] == "unavailable"


def test_build_claude_host_guidance_needs_marketplace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/claude")
    repo = _packaging_repo(tmp_path / "repo")
    guidance = hc.build_claude_host_guidance(
        repo_root=repo,
        home_root=tmp_path,
        source_manifest_present=True,
        marketplace_entry=None,
        installed_entry=None,
        enabled_status=None,
    )
    assert guidance["status"] == "needs-marketplace"


def test_build_claude_host_guidance_needs_install(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/claude")
    repo = _packaging_repo(tmp_path / "repo")
    guidance = hc.build_claude_host_guidance(
        repo_root=repo,
        home_root=tmp_path,
        source_manifest_present=True,
        marketplace_entry={},
        installed_entry=None,
        enabled_status=None,
    )
    assert guidance["status"] == "needs-install"


def test_looks_like_repo_root_rejects_missing_path(tmp_path: Path) -> None:
    assert delivery.looks_like_repo_root(tmp_path / "absent") is False


def test_write_install_state_round_trips(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_STATE_HOME", str(tmp_path / "state"))
    delivery.write_install_state(tmp_path, repo_root=tmp_path / "repo", managed_checkout=True)
    payload = json.loads(delivery.default_install_state_path(tmp_path).read_text(encoding="utf-8"))
    assert payload["managed_checkout"] is True


def test_read_host_state_handles_bad_payloads(tmp_path: Path) -> None:
    path = common.default_host_state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    assert delivery.read_host_state(tmp_path) == {"state_version": 1}
    path.write_text(json.dumps([1]), encoding="utf-8")
    assert delivery.read_host_state(tmp_path) == {"state_version": 1}


def test_compact_session_staleness_counts_affected() -> None:
    compact = delivery._compact_session_staleness(
        {"status": "stale", "message": "m", "affected": ["a", "b"]}
    )
    assert compact == {"status": "stale", "message": "m", "affected_count": 2}


def test_runtime_root_for_repo_raises_without_owner(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(proc, "_runtime_bootstrap_module", lambda repo_root: None)
    with pytest.raises(proc.CharnessError):
        proc._runtime_root_for_repo(tmp_path)


def test_invoke_repo_script_supports_tools_module_path(tmp_path: Path, monkeypatch) -> None:
    seen: list[list[str]] = []

    def _fake_run(command: list[str], **kwargs) -> SimpleNamespace:
        seen.append(command)
        return _result(stdout="ok\n")

    monkeypatch.setattr(proc, "resolve_repo_python", lambda repo_root: "py")
    monkeypatch.setattr(proc, "run", _fake_run)
    assert proc.invoke_repo_script(tmp_path, "tools/foo/bar.py") == "ok"
    assert seen[0][:3] == ["py", "-m", "tools.foo.bar"]


def test_resolve_repo_python_rejects_empty_bootstrap_output(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(proc, "_configure_runtime_for_repo", lambda repo_root: True)
    monkeypatch.setattr(proc, "bootstrap_runtime_fast_path", lambda repo_root: None)
    monkeypatch.setattr(proc, "run", lambda *args, **kwargs: _result(stdout="  \n"))
    with pytest.raises(proc.CharnessError):
        proc.resolve_repo_python(tmp_path)


def test_invoke_repo_json_script_failure_modes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(proc, "resolve_repo_python", lambda repo_root: "py")
    monkeypatch.setattr(
        proc, "run", lambda *args, **kwargs: _result(returncode=1, stdout='{"a": 1}\n')
    )
    with pytest.raises(proc.CharnessError):
        proc.invoke_repo_json_script(tmp_path, "scripts/x.py")
    monkeypatch.setattr(proc, "run", lambda *args, **kwargs: _result(returncode=1, stdout=""))
    with pytest.raises(proc.CharnessError):
        proc.invoke_repo_json_script(tmp_path, "scripts/x.py", allow_failure=True)
    monkeypatch.setattr(proc, "run", lambda *args, **kwargs: _result(stdout="  \n"))
    assert proc.invoke_repo_json_script(tmp_path, "scripts/x.py") is None


def test_load_worktree_audit_lib_inserts_lib_root(tmp_path: Path, monkeypatch) -> None:
    lib = tmp_path / "audit-lib"
    lib.mkdir()
    assert str(lib) not in sys.path
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda args: lib)
    args = argparse.Namespace()
    assert proc._load_worktree_audit_lib(args).__name__ == "scripts.worktree.worktree_audit_lib"
    sys.path.remove(str(lib))


def test_load_worktree_cleanup_lib_reuses_path_entry(tmp_path: Path, monkeypatch) -> None:
    lib = tmp_path / "cleanup-lib"
    lib.mkdir()
    monkeypatch.syspath_prepend(str(lib))
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda args: lib)
    args = argparse.Namespace()
    assert proc._load_worktree_cleanup_lib(args).__name__ == "scripts.worktree.worktree_cleanup_lib"


def test_load_worktree_create_lib_inserts_lib_root(tmp_path: Path, monkeypatch) -> None:
    lib = tmp_path / "create-lib"
    lib.mkdir()
    assert str(lib) not in sys.path
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda args: lib)
    args = argparse.Namespace()
    assert proc._load_worktree_create_lib(args).__name__ == "scripts.worktree.worktree_create_lib"
    sys.path.remove(str(lib))


def test_load_task_run_lib_inserts_lib_root(tmp_path: Path, monkeypatch) -> None:
    lib = tmp_path / "task-lib"
    lib.mkdir()
    assert str(lib) not in sys.path
    monkeypatch.setattr(proc, "_resolve_worktree_lib_root", lambda args: lib)
    args = argparse.Namespace()
    assert proc._load_task_run_lib(args).__name__ == "scripts.task_run.task_run"
    sys.path.remove(str(lib))


def test_resolve_config_home_shapes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_CONFIG_HOME", str(tmp_path / "cfg"))
    assert common.resolve_config_home(tmp_path) == (tmp_path / "cfg").resolve()
    monkeypatch.delenv("CHARNESS_CONFIG_HOME", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert common.resolve_config_home(tmp_path) == (tmp_path / "xdg").resolve()
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert common.resolve_config_home(tmp_path) == tmp_path / ".config"
    assert common.default_config_root(tmp_path) == tmp_path / ".config" / "charness"


def test_send_jsonrpc_message_rejects_missing_stdin() -> None:
    with pytest.raises(rpc.CharnessError):
        rpc.send_jsonrpc_message(SimpleNamespace(stdin=None), {"jsonrpc": "2.0"})


def test_refresh_codex_cache_skips_without_cli_or_marketplace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    skipped = rpc.refresh_codex_cache_via_app_server(
        home_root=tmp_path,
        codex_marketplace_path=tmp_path / "market.json",
        plugin_name="charness",
    )
    assert skipped["status"] == "skipped"
    assert skipped["reason"] == "codex-cli-missing"
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/codex")
    skipped_marketplace = rpc.refresh_codex_cache_via_app_server(
        home_root=tmp_path,
        codex_marketplace_path=tmp_path / "absent.json",
        plugin_name="charness",
    )
    assert skipped_marketplace["reason"] == "missing-marketplace"


class _FakeStdin:
    def write(self, data: str) -> None:
        return None

    def flush(self) -> None:
        return None

    def close(self) -> None:
        return None


class _FakeAppServer:
    def __init__(self) -> None:
        self.stdin: object = _FakeStdin()
        self.stdout: object = object()
        self.stderr: object = object()
        self.terminated = False
        self.killed = False
        self._waits = 0

    def poll(self) -> None:
        return None

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        self._waits += 1
        if self._waits == 1:
            raise subprocess.TimeoutExpired("codex", timeout)
        return 0


def test_refresh_codex_cache_kills_hung_app_server(tmp_path: Path, monkeypatch) -> None:
    marketplace = tmp_path / "market.json"
    marketplace.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/codex")
    server = _FakeAppServer()
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: server)
    calls = [{"result": {}}, {"result": {"installed": True}}]

    def _fake_wait(stream: object, *, expected_id: int, deadline: float) -> dict[str, object]:
        return calls.pop(0)

    monkeypatch.setattr(rpc, "wait_for_jsonrpc_response", _fake_wait)
    outcome = rpc.refresh_codex_cache_via_app_server(
        home_root=tmp_path, codex_marketplace_path=marketplace, plugin_name="charness"
    )
    assert outcome["status"] == "attempted"
    assert server.terminated is True
    assert server.killed is True


def test_build_doctor_next_action_handles_unknown_and_repo_guidance() -> None:
    payload = {
        "codex_host_guidance": {"message": "m", "status": 7},
        "claude_host_guidance": {"message": "c", "status": "needs-install"},
        "repo_onboarding": {
            "message": "r",
            "status": "required",
            "manual_action_required": True,
        },
    }
    action = dp.build_doctor_next_action(payload)
    assert action["kind"] == "repo-init"
    codex_only = {"codex_host_guidance": {"message": "m", "status": 7}}
    assert dp.build_doctor_next_action(codex_only)["status"] == "unknown"


def test_install_surface_records_synced_support_and_paths(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    cli_path = tmp_path / "bin" / "charness"
    wrapper_path = tmp_path / "wrap"
    monkeypatch.setattr(dp, "invoke_repo_script", lambda *args, **kwargs: '{"host_next_steps": {}}')
    monkeypatch.setattr(
        dp, "invoke_repo_json_script", lambda *args, **kwargs: [{"status": "synced"}]
    )
    monkeypatch.setattr(dp, "install_cli_binary", lambda target, **kwargs: None)
    monkeypatch.setattr(dp, "write_claude_wrapper", lambda path, root: None)
    monkeypatch.setattr(dp, "ensure_claude_marketplace", lambda *args, **kwargs: (["m"], "mkt"))
    monkeypatch.setattr(dp, "ensure_claude_plugin", lambda *args, **kwargs: (["p"], "plug"))
    monkeypatch.setattr(dp, "ensure_grok_plugin", lambda *args, **kwargs: (["g"], "grok"))
    payload = dp.install_surface(
        repo,
        home_root=tmp_path,
        plugin_root=tmp_path / "plugin",
        codex_marketplace_path=tmp_path / "market.json",
        claude_wrapper_path=wrapper_path,
        cli_path=cli_path,
        update=False,
    )
    assert "upstream_support_skills_synced" in payload["completed_actions"]
    assert payload["cli_path"] == str(cli_path)
    assert payload["claude_wrapper_path"] == str(wrapper_path)
    assert payload["host_next_steps"]["claude"] == "plug"
    assert payload["host_next_steps"]["grok"] == "grok"


def test_package_import_context_reports_package_caller(monkeypatch) -> None:
    def _boom(depth: int) -> object:
        raise ValueError("shallow")

    monkeypatch.setattr(sys, "_getframe", _boom)
    assert rb._package_import_context() is False

    inner = SimpleNamespace(f_globals={"__name__": "scripts.runtime_bootstrap"}, f_back=None)
    outer = SimpleNamespace(f_globals={"__name__": "scripts.foo"}, f_back=None)
    inner.f_back = outer
    monkeypatch.setattr(sys, "_getframe", lambda depth: inner)
    assert rb._package_import_context() is True
    lone = SimpleNamespace(f_globals={"__name__": "scripts.runtime_bootstrap"}, f_back=None)
    monkeypatch.setattr(sys, "_getframe", lambda depth: lone)
    assert rb._package_import_context() is False
