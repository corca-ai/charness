from __future__ import annotations

import json
import os
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/inventory_sloc.py"


def _path_without_tokei(tmp_path: Path) -> dict[str, str]:
    """Force `shutil.which('tokei')` to miss by pointing PATH at an empty dir while
    keeping the rest of the environment (so the subprocess still starts normally).
    `inventory_sloc.py` returns the degraded payload before any tokei/git subprocess,
    so an empty PATH is safe. Before #368 these tests skipped whenever tokei was on
    PATH — which is always (tokei is installed locally and in CI), so the degraded
    path was never actually exercised."""
    nobin = tmp_path / "nobin"
    nobin.mkdir(exist_ok=True)
    return {**os.environ, "PATH": str(nobin)}


def test_inventory_sloc_reports_degraded_when_tokei_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", env=_path_without_tokei(tmp_path))

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
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCRIPT, "--repo-root", str(repo), env=_path_without_tokei(tmp_path))

    assert result.returncode == 0, result.stderr
    assert "degraded" in result.stdout
