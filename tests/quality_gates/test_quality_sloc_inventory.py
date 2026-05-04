from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from .support import run_script

SCRIPT = "skills/public/quality/scripts/inventory_sloc.py"


def test_inventory_sloc_reports_degraded_when_tokei_missing(tmp_path: Path) -> None:
    if shutil.which("tokei") is not None:
        pytest.skip("tokei is installed; degraded path is not exercised in this env")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["engine"] == "tokei"
    assert payload["tokei_version"] is None
    assert "tokei" in payload["reason"].lower()
    assert payload["totals"] == {"code": 0, "comments": 0, "blanks": 0, "files": 0}
    assert payload["languages"] == {}
    assert payload["advisory_notes"]


def test_inventory_sloc_human_output_marks_degraded(tmp_path: Path) -> None:
    if shutil.which("tokei") is not None:
        pytest.skip("tokei is installed; degraded path is not exercised in this env")
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCRIPT, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "degraded" in result.stdout
