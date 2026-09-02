from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.adapters.control_plane_lib as control_plane_lib
from scripts.update_tools import previous_observed_version


def _relax_lock_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(control_plane_lib, "load_lock_schema", lambda *args, **kwargs: {"type": "object"})


def _seed_locks_dir(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "integrations" / "locks").mkdir(parents=True)
    return repo


def test_previous_observed_version_returns_none_without_lock_file(tmp_path: Path) -> None:
    repo = _seed_locks_dir(tmp_path)

    assert previous_observed_version(repo, "demo") is None


def test_previous_observed_version_returns_none_for_corrupt_lock_file(tmp_path: Path) -> None:
    repo = _seed_locks_dir(tmp_path)
    (repo / "integrations" / "locks" / "demo.json").write_text('{"not json', encoding="utf-8")

    assert previous_observed_version(repo, "demo") is None


def test_previous_observed_version_prefers_doctor_observed_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _seed_locks_dir(tmp_path)
    _relax_lock_schema(monkeypatch)
    (repo / "integrations" / "locks" / "demo.json").write_text(
        json.dumps({"doctor": {"version": {"observed_version": "1.2.3"}}}),
        encoding="utf-8",
    )

    assert previous_observed_version(repo, "demo") == "1.2.3"


def test_previous_observed_version_falls_back_to_update_detect(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _seed_locks_dir(tmp_path)
    _relax_lock_schema(monkeypatch)
    (repo / "integrations" / "locks" / "demo.json").write_text(
        json.dumps({"update": {"detect": {"results": [{"stdout": "demo 2.0.0"}]}}}),
        encoding="utf-8",
    )

    assert previous_observed_version(repo, "demo") == "2.0.0"


def test_previous_observed_version_returns_none_without_doctor_or_update(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _seed_locks_dir(tmp_path)
    _relax_lock_schema(monkeypatch)
    (repo / "integrations" / "locks" / "demo.json").write_text(
        json.dumps({"schema_version": "1", "tool_id": "demo", "manifest_path": "integrations/tools/demo.json"}),
        encoding="utf-8",
    )

    assert previous_observed_version(repo, "demo") is None
