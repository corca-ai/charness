from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_charness_module(module_name: str = "charness_update_flow_unit_under_test"):
    loader = importlib.machinery.SourceFileLoader(module_name, str(ROOT / "charness"))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        json_mode=True,
        precomputed_support_results=support_results,
    )

    assert failed is False
    assert calls == ["scripts/update_tools.py", "scripts/doctor.py"]
    assert payload["results"]["demo"]["support"] == support_results[0]
