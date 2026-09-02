from __future__ import annotations

from pathlib import Path

from .support import load_cli_module

ROOT = Path(__file__).resolve().parents[2]


def load_charness_module(module_name: str = "charness_update_flow_unit_under_test"):
    return load_cli_module(module_name, ROOT / "charness")


def test_update_all_flow_reuses_precomputed_support_results(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module()
    calls: list[str] = []

    def fake_invoke(_repo_root: Path, relative_script: str, *args: str, allow_failure: bool = False) -> object:
        calls.append(relative_script)
        assert allow_failure is True
        assert "scripts/sync_support.py" not in relative_script
        if relative_script == "scripts/update_tools.py":
            return [{"tool_id": "demo", "status": "updated"}]
        if relative_script == "scripts/doctor.py":
            return [{"tool_id": "demo", "doctor_status": "ok", "doctor_disposition": "ok"}]
        raise AssertionError(f"unexpected script: {relative_script}")

    monkeypatch.setattr(module, "invoke_repo_json_script", fake_invoke)
    support_results = [{"tool_id": "demo", "status": "synced"}]

    payload, failed = module.run_tool_update_flow(
        repo_root=tmp_path,
        managed_checkout=True,
        plugin_root=tmp_path / "plugin",
        tool_ids=[],
        dry_run=False,
        skip_sync_support=False,
        upstream_checkouts=[],
        precomputed_support_results=support_results,
    )

    assert failed is False
    assert calls == ["scripts/update_tools.py", "scripts/doctor.py"]
    assert payload["results"]["demo"]["support"] == support_results[0]


def test_update_flow_syncs_support_when_reuse_is_not_available(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_update_flow_unit_sync_under_test")
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_invoke(_repo_root: Path, relative_script: str, *args: str, allow_failure: bool = False) -> object:
        calls.append((relative_script, args))
        assert allow_failure is True
        if relative_script == "scripts/update_tools.py":
            return [{"tool_id": "demo", "status": "updated"}]
        if relative_script == "scripts/sync_support.py":
            return [{"tool_id": "demo", "status": "synced"}]
        if relative_script == "scripts/doctor.py":
            return [{"tool_id": "demo", "doctor_status": "ok", "doctor_disposition": "ok"}]
        raise AssertionError(f"unexpected script: {relative_script}")

    monkeypatch.setattr(module, "invoke_repo_json_script", fake_invoke)

    payload, failed = module.run_tool_update_flow(
        repo_root=tmp_path,
        managed_checkout=False,
        plugin_root=tmp_path / "plugin",
        tool_ids=["demo"],
        dry_run=False,
        skip_sync_support=False,
        upstream_checkouts=["../upstream"],
        precomputed_support_results=[{"tool_id": "demo", "status": "old"}],
    )

    support_call = next(args for script, args in calls if script == "scripts/sync_support.py")
    assert "--tool-id" in support_call
    assert "--upstream-checkout" in support_call
    assert "--execute" in support_call
    assert failed is False
    assert payload["results"]["demo"]["support"]["status"] == "synced"


def test_update_all_flow_treats_refreshed_not_ready_as_failure(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_update_flow_unit_refreshed_failure_under_test")

    def fake_invoke(_repo_root: Path, relative_script: str, *args: str, allow_failure: bool = False) -> object:
        assert allow_failure is True
        if relative_script == "scripts/update_tools.py":
            return [{"tool_id": "demo", "status": "refreshed-not-ready"}]
        if relative_script == "scripts/doctor.py":
            return [{"tool_id": "demo", "doctor_status": "ok", "doctor_disposition": "ok"}]
        raise AssertionError(f"unexpected script: {relative_script}")

    monkeypatch.setattr(module, "invoke_repo_json_script", fake_invoke)

    payload, failed = module.run_tool_update_flow(
        repo_root=tmp_path,
        managed_checkout=True,
        plugin_root=tmp_path / "plugin",
        tool_ids=[],
        dry_run=False,
        skip_sync_support=True,
        upstream_checkouts=[],
    )

    assert failed is True
    assert payload["results"]["demo"]["update"]["status"] == "refreshed-not-ready"


def test_update_all_flow_propagates_blocking_doctor_and_support_failures(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_update_flow_unit_phase_failure_under_test")

    def fake_invoke(_repo_root: Path, relative_script: str, *args: str, allow_failure: bool = False) -> object:
        assert allow_failure is True
        if relative_script == "scripts/update_tools.py":
            return [{"tool_id": "doctor-blocked", "status": "updated"}, {"tool_id": "support-broken", "status": "updated"}]
        if relative_script == "scripts/sync_support.py":
            return [{"tool_id": "support-broken", "status": "failed"}]
        if relative_script == "scripts/doctor.py":
            return [
                {"tool_id": "doctor-blocked", "doctor_status": "failed", "doctor_disposition": "blocking-failure"},
                {"tool_id": "support-broken", "doctor_status": "ok", "doctor_disposition": "ok"},
            ]
        raise AssertionError(f"unexpected script: {relative_script}")

    monkeypatch.setattr(module, "invoke_repo_json_script", fake_invoke)

    payload, failed = module.run_tool_update_flow(
        repo_root=tmp_path,
        managed_checkout=True,
        plugin_root=tmp_path / "plugin",
        tool_ids=[],
        dry_run=False,
        skip_sync_support=False,
        upstream_checkouts=[],
    )

    assert failed is True
    assert payload["failed_tool_ids"] == ["doctor-blocked", "support-broken"]
    assert payload["failure_phases"] == {
        "doctor-blocked": ["doctor"],
        "support-broken": ["support"],
    }


def _seed_checkout(tmp_path: Path, body: str) -> Path:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (checkout / "charness").write_text(body, encoding="utf-8")
    return checkout


def test_reexec_noops_when_running_cli_matches_checkout(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_reexec_match_under_test")
    monkeypatch.delenv(module._CLI_REEXEC_GUARD_ENV, raising=False)
    checkout = _seed_checkout(tmp_path, "#!/usr/bin/env python3\nprint('cli')\n")
    same_bytes_copy = tmp_path / "installed-charness"
    same_bytes_copy.write_text("#!/usr/bin/env python3\nprint('cli')\n", encoding="utf-8")

    assert module.maybe_reexec_refreshed_cli(checkout, running_cli=checkout / "charness") is None
    assert module.maybe_reexec_refreshed_cli(checkout, running_cli=same_bytes_copy) is None
    assert module.maybe_reexec_refreshed_cli(tmp_path / "no-checkout", running_cli=same_bytes_copy) is None
    # An unreadable comparison (here: the running CLI resolves to a directory)
    # must fail safe into the no-reexec path instead of crashing the command.
    unreadable = tmp_path / "cli-as-dir"
    unreadable.mkdir()
    assert module.maybe_reexec_refreshed_cli(checkout, running_cli=unreadable) is None


def test_reexec_replaces_process_when_checkout_is_newer(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_reexec_fire_under_test")
    monkeypatch.delenv(module._CLI_REEXEC_GUARD_ENV, raising=False)
    checkout = _seed_checkout(tmp_path, "print('new cli')\n")
    stale_cli = tmp_path / "installed-charness"
    stale_cli.write_text("print('old cli')\n", encoding="utf-8")
    recorded: dict[str, object] = {}

    def fake_execve(executable: str, argv: list[str], env: dict[str, str]) -> None:
        recorded["executable"] = executable
        recorded["argv"] = argv
        recorded["env_guard"] = env.get(module._CLI_REEXEC_GUARD_ENV)

    result = module.maybe_reexec_refreshed_cli(checkout, running_cli=stale_cli, execve=fake_execve)

    assert result is None
    assert recorded["executable"] == module.sys.executable
    assert recorded["argv"][:2] == [module.sys.executable, str(checkout / "charness")]
    assert recorded["argv"][2:] == module.sys.argv[1:]
    assert recorded["env_guard"] == str(module.os.getpid())


def test_reexec_guard_reports_child_and_blocks_loops(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_reexec_guard_under_test")
    monkeypatch.setenv(module._CLI_REEXEC_GUARD_ENV, str(module.os.getpid()))
    checkout = _seed_checkout(tmp_path, "print('new cli')\n")

    child_view = module.maybe_reexec_refreshed_cli(checkout, running_cli=checkout / "charness")
    assert child_view == {"status": "reexecuted", "checkout_cli": str(checkout / "charness")}

    still_stale = tmp_path / "installed-charness"
    still_stale.write_text("print('old cli')\n", encoding="utf-8")
    skipped = module.maybe_reexec_refreshed_cli(
        checkout, running_cli=still_stale, execve=lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not re-exec"))
    )
    assert skipped is not None and skipped["status"] == "skipped"


def test_reexec_ignores_foreign_guard_value_and_survives_execve_failure(monkeypatch, tmp_path: Path) -> None:
    module = load_charness_module("charness_reexec_foreign_guard_under_test")
    # A stale/foreign guard (a "1" or another process's pid inherited from an
    # unrelated environment) must not suppress the self-heal.
    monkeypatch.setenv(module._CLI_REEXEC_GUARD_ENV, "1")
    checkout = _seed_checkout(tmp_path, "print('new cli')\n")
    stale_cli = tmp_path / "installed-charness"
    stale_cli.write_text("print('old cli')\n", encoding="utf-8")
    fired: dict[str, object] = {}

    def fake_execve(executable: str, argv: list[str], env: dict[str, str]) -> None:
        fired["env_guard"] = env.get(module._CLI_REEXEC_GUARD_ENV)

    assert module.maybe_reexec_refreshed_cli(checkout, running_cli=stale_cli, execve=fake_execve) is None
    assert fired["env_guard"] == str(module.os.getpid())

    def broken_execve(*_args: object) -> None:
        raise OSError("exec format error")

    fallback = module.maybe_reexec_refreshed_cli(checkout, running_cli=stale_cli, execve=broken_execve)
    assert fallback is not None and fallback["status"] == "failed"
    assert "re-exec failed" in fallback["reason"]
