from __future__ import annotations

import json
from pathlib import Path

from runtime_bootstrap import import_repo_module

from .support import ROOT

_native_gate = import_repo_module(ROOT / "scripts/native_gate_lib.py", "scripts.native_gate_lib")


def _fake_binary(monkeypatch, tmp_path: Path, payload: dict[str, object], exit_code: int) -> Path:
    binary = tmp_path / "fake-repograph"
    binary.write_text(
        "#!/usr/bin/env python3\n"
        "import os\n"
        "print(os.environ['FAKE_REPOGRAPH_PAYLOAD'])\n"
        "raise SystemExit(int(os.environ['FAKE_REPOGRAPH_EXIT']))\n",
        encoding="utf-8",
    )
    binary.chmod(0o755)
    monkeypatch.setenv("FAKE_REPOGRAPH_PAYLOAD", json.dumps(payload))
    monkeypatch.setenv("FAKE_REPOGRAPH_EXIT", str(exit_code))
    return binary


def _run_gate(monkeypatch, capfd, tmp_path: Path, payload: dict[str, object], exit_code: int):
    binary = _fake_binary(monkeypatch, tmp_path, payload, exit_code)
    monkeypatch.setenv("CHARNESS_NATIVE_CORE", str(binary))

    return_code = _native_gate.main(
        [
            "--repo-root",
            str(tmp_path),
            "plugin-refs",
            "--repo-root",
            str(tmp_path),
        ]
    )
    captured = capfd.readouterr()
    return return_code, json.loads(captured.out)


def test_plugin_refs_findings_exit_propagates_through_the_native_gate(monkeypatch, capfd, tmp_path: Path) -> None:
    payload = {
        "schema": "repograph.plugin_refs.v1",
        "findings": [{"path": "docs/guide.md", "classification": "missing"}],
    }

    return_code, report = _run_gate(monkeypatch, capfd, tmp_path, payload, 1)

    assert return_code == 1
    assert report == payload


def test_plugin_refs_unestablished_exit_propagates_through_the_native_gate(monkeypatch, capfd, tmp_path: Path) -> None:
    payload = {
        "schema": "repograph.plugin_refs.v1",
        "unestablished": [{"path": "<inventory>", "status": "inventory"}],
    }

    return_code, report = _run_gate(monkeypatch, capfd, tmp_path, payload, 3)

    assert return_code == 3
    assert report == payload


def test_plugin_refs_clean_exit_propagates_through_the_native_gate(monkeypatch, capfd, tmp_path: Path) -> None:
    payload = {
        "schema": "repograph.plugin_refs.v1",
        "findings": [],
        "scope_note": "validated package set: charness",
    }

    return_code, report = _run_gate(monkeypatch, capfd, tmp_path, payload, 0)

    assert return_code == 0
    assert report == payload
