"""A pre-bootstrap environment snapshot derives the same runtime root after bootstrap."""

from __future__ import annotations

import tempfile
from pathlib import Path

from scripts.runtime_bootstrap import runtime_root


def test_snapshot_root_ignores_tempfile_redirected_by_bootstrap(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    system_temp = tmp_path / "system-temp"
    snapshot = {"TEMP": str(system_temp), "TMP": str(system_temp)}
    before = runtime_root(repo, snapshot)

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "runtime" / "tmp"))

    assert runtime_root(repo, snapshot) == before
    assert system_temp.resolve() in before.parents
