from __future__ import annotations

from pathlib import Path

import yaml

from .support import ROOT, run_script


def test_strict_fails_for_an_unreferenced_python_script(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "used.py").write_text("VALUE = 1\n", encoding="utf-8")
    (scripts / "orphan.py").write_text("VALUE = 2\n", encoding="utf-8")
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_used.py").write_text(
        "from scripts import used\n\nassert used.VALUE == 1\n", encoding="utf-8"
    )

    result = run_script(
        "scripts/check_unreferenced_scripts.py",
        "--repo-root",
        str(repo),
        "--strict",
        cwd=ROOT,
        real_process=True,
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["unreferenced"] == ["scripts/orphan.py"]
    assert payload["verdict"] == "fail"
    assert "ERROR: 1 unreferenced script file(s)" in result.stderr


def test_empty_script_universe_refuses(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# no scripts\n", encoding="utf-8")

    result = run_script(
        "scripts/check_unreferenced_scripts.py",
        "--repo-root",
        str(tmp_path),
        cwd=ROOT,
        real_process=True,
    )

    assert result.returncode == 1
    assert "refusing empty matched script universe" in result.stderr
    assert "scripts/**" in result.stderr
