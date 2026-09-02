from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

_MODULE = load_script_module(
    "check_unreferenced_scripts", ROOT / "tools" / "check_unreferenced_scripts.py"
)


def _run(*args: str) -> SimpleNamespace:
    return run_loaded_script_main("check_unreferenced_scripts.py", _MODULE, *args)


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

    result = _run("--repo-root", str(repo), "--strict")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["unreferenced"] == ["scripts/orphan.py"]
    assert payload["verdict"] == "fail"
    assert "ERROR: 1 unreferenced script file(s)" in result.stderr


def test_empty_script_universe_refuses(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# no scripts\n", encoding="utf-8")

    result = _run("--repo-root", str(tmp_path))

    assert result.returncode == 1
    assert "refusing empty matched script universe" in result.stderr
    assert "scripts/**" in result.stderr


def test_strict_keeps_a_nested_dotted_import_reachable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "scripts" / "pkg"
    nested.mkdir(parents=True)
    (nested / "__init__.py").write_text('"""Package marker."""\n', encoding="utf-8")
    (nested / "entry.py").write_text("VALUE = 1\n", encoding="utf-8")
    (nested / "consumer.py").write_text(
        "from scripts.pkg.entry import VALUE\nassert VALUE == 1\n", encoding="utf-8"
    )
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_consumer.py").write_text(
        "from scripts.pkg.consumer import VALUE\nassert VALUE == 1\n", encoding="utf-8"
    )

    result = _run("--repo-root", str(repo), "--strict")

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert "scripts/pkg/entry.py" not in payload["unreferenced"]
    assert "scripts/pkg/consumer.py" not in payload["unreferenced"]
    assert "scripts/pkg/__init__.py" not in payload["unreferenced"]
    assert payload["verdict"] == "ok"


def test_strict_keeps_a_subpackage_name_import_reachable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "scripts" / "pkg"
    nested.mkdir(parents=True)
    (nested / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
    (nested / "entry.py").write_text("VALUE = 1\n", encoding="utf-8")
    (nested / "consumer.py").write_text(
        "from scripts.pkg import entry\nassert entry.VALUE == 1\n", encoding="utf-8"
    )
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_consumer.py").write_text(
        "from scripts.pkg import consumer\nassert consumer.entry.VALUE == 1\n",
        encoding="utf-8",
    )

    result = _run("--repo-root", str(repo), "--strict")

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert "scripts/pkg/entry.py" not in payload["unreferenced"]
    assert payload["verdict"] == "ok"
