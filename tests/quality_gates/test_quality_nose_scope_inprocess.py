"""In-process coverage for the nose inventory scope and receipt branches."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    return load_module(f"{name}_scope_inproc", SCRIPT_DIR / f"{name}.py")


inv = _load("inventory_nose_clones")
scope = inv.nose_scope


def _args(tmp_path: Path, **overrides) -> SimpleNamespace:
    base = {
        "repo_root": tmp_path,
        "path": [],
        "exclude": [],
        "ignore_file": None,
        "write_baseline": False,
        "baseline": None,
        "mode": "syntax,semantic,near",
        "min_size": 24,
        "top": 20,
        "sort": "extractability",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _baseline() -> SimpleNamespace:
    return SimpleNamespace(resolve_baseline=lambda **_kwargs: "baseline.json")


def _report(collected: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        build_query_command=lambda *_args, **_kwargs: ["nose", "query"],
        resolve_tool_version=lambda _nose: "0.13.3",
        collect_families=lambda *_args, **_kwargs: collected or {"status": "clean", "families": []},
    )


def _payload(
    tmp_path: Path,
    *,
    args: SimpleNamespace,
    adapter_loader,
    report: SimpleNamespace,
    nose_bin: str | None = "nose",
) -> dict:
    return scope.payload_for_args(
        args,
        baseline=_baseline(),
        report=report,
        fingerprint=SimpleNamespace(),
        load_repo_module=adapter_loader,
        script_path="adapter.py",
        resolve_nose_bin=lambda: nose_bin,
        interpretation={},
    )


@pytest.mark.parametrize("failure", [ImportError("missing"), RuntimeError("broken"), OSError("unreadable")])
def test_adapter_scope_loader_falls_back_on_loader_failures(tmp_path: Path, failure: Exception) -> None:
    def load(_path: str, _name: str):
        raise failure

    configured, errors, notes = scope._adapter_inventory_paths(tmp_path, load, "adapter.py")

    assert configured is None
    assert errors == []
    assert "using defaults" in notes[0]


def test_adapter_scope_loader_reports_invalid_payload(tmp_path: Path) -> None:
    def load(_path: str, _name: str):
        return SimpleNamespace(load_quality_adapter_permissive=lambda _repo: [])

    configured, errors, notes = scope._adapter_inventory_paths(tmp_path, load, "adapter.py")

    assert configured is None
    assert errors == []
    assert notes == ["quality adapter scope unavailable; using defaults: invalid payload"]


def test_invalid_adapter_scope_returns_error_without_querying(tmp_path: Path) -> None:
    def load(_path: str, _name: str):
        return SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {"errors": ["bad scope"], "data": {}}
        )

    payload = _payload(
        tmp_path,
        args=_args(tmp_path),
        adapter_loader=load,
        report=_report(),
    )

    assert payload["status"] == "error"
    assert payload["exit_code"] == 1
    assert payload["scope_status"] == "error"
    assert payload["families"] == []


def test_partial_scope_refuses_baseline_write(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    args = _args(tmp_path, path=["src", "worker"], write_baseline=True)
    payload = _payload(
        tmp_path,
        args=args,
        adapter_loader=lambda *_args: SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {"errors": [], "data": {}}
        ),
        report=_report(),
    )

    assert payload["status"] == "error"
    assert payload["scope_status"] == "partial"
    assert "baseline not written" in payload["notes"][0]


def test_query_error_refuses_baseline_write(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    args = _args(tmp_path, path=["src"], write_baseline=True)
    payload = _payload(
        tmp_path,
        args=args,
        adapter_loader=lambda *_args: SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {"errors": [], "data": {}}
        ),
        report=_report({"status": "error", "exit_code": 2, "stderr": "query boom", "families": []}),
    )

    assert payload["status"] == "error"
    assert payload["exit_code"] == 2
    assert payload["stderr"] == "query boom"
    assert "baseline not written" in payload["notes"][0]


def test_non_scan_and_partial_human_receipts_are_rendered(capsys) -> None:
    assert inv._print_non_scan({"status": "inapplicable", "missing_paths": ["src", "worker"]})
    assert "missing_paths=src, worker" in capsys.readouterr().out

    inv.print_human(
        {
            "status": "clean",
            "tool_version": "0.13.3",
            "family_count": 0,
            "total_dup_lines": 0,
            "families": [],
            "scope_status": "partial",
            "scanned_paths": ["src"],
            "missing_paths": ["worker"],
        }
    )
    assert "partial scan" in capsys.readouterr().out


def test_error_exit_code_is_nonzero() -> None:
    assert scope.cli_exit_code_for_payload({"status": "error"}) == 1
