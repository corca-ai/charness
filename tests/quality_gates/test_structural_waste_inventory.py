from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_structural_waste.py"
LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "structural_waste_lib.py"


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_json(repo: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_structural_waste_reports_duplicate_pytest_collection(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(
        repo / ".githooks" / "pre-push",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only",
                "python3 -m pytest --collect-only -q tests",
            ]
        )
        + "\n",
    )
    _write(repo / "scripts" / "run_standing_pytest.py", "print('runner')\n")

    payload = _run_json(repo)

    assert payload["duplicate_discovery_candidates"][0]["type"] == "pytest_collect_only_duplicate"
    assert payload["duplicate_discovery_candidates"][0]["canonical_runner_count"] >= 1
    assert payload["findings"][0]["severity"] == "advisory"
    assert "file-level target coverage" in payload["findings"][0]["recommended_action"]


def test_structural_waste_does_not_call_collection_duplicate_without_canonical_runner(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(
        repo / ".githooks" / "pre-push",
        "python3 -m pytest --collect-only -q tests\n",
    )

    payload = _run_json(repo)

    candidate = payload["duplicate_discovery_candidates"][0]
    assert candidate["type"] == "pytest_collect_only_broad_collection"
    assert candidate["canonical_runner_count"] == 0
    assert "Name the canonical runner" in candidate["recommended_action"]
    assert payload["findings"][0]["type"] == "broad_collection_review"
    assert "do not call this duplicate proof" in payload["findings"][0]["recommended_action"]


def test_structural_waste_reports_broad_parser_without_prefilter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(
        repo / "scripts" / "scan_everything.py",
        "\n".join(
            [
                "from pathlib import Path",
                "import ast",
                "for path in Path('.').rglob('*.py'):",
                "    ast.parse(path.read_text())",
            ]
        )
        + "\n",
    )

    payload = _run_json(repo)

    candidates = payload["broad_scanner_candidates"]
    assert candidates == [
        {
            "line": 4,
            "parser_token": "ast.parse",
            "path": "scripts/scan_everything.py",
            "recommended_action": "Add a cheap path/text candidate prefilter before parser work, or record why full parsing is the correctness boundary.",
            "type": "broad_parser_without_visible_prefilter",
        }
    ]
    assert payload["findings"][0]["type"] == "broad_scanner_prefilter"


def test_structural_waste_does_not_flag_visible_prefilter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(
        repo / "scripts" / "scan_candidates.py",
        "\n".join(
            [
                "from pathlib import Path",
                "import ast",
                "for path in Path('.').rglob('*.py'):",
                "    text = path.read_text()",
                "    if 'needle' not in text:",
                "        continue",
                "    ast.parse(text)",
            ]
        )
        + "\n",
    )

    payload = _run_json(repo)

    assert payload["broad_scanner_candidates"] == []
    assert payload["findings"] == []


def test_structural_waste_text_output_carries_interpretation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Structural waste inventory" in result.stdout
    assert "advisory structural signal, not a refactor mandate" in result.stdout
    assert "Answer first:" in result.stdout


def test_structural_waste_text_output_prints_findings_and_candidates(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(
        repo / ".githooks" / "pre-push",
        "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only\n"
        "python3 -m pytest --collect-only -q tests\n",
    )
    _write(repo / "scripts" / "run_standing_pytest.py", "print('runner')\n")
    _write(
        repo / "scripts" / "scan_everything.py",
        "from pathlib import Path\nimport ast\nfor path in Path('.').rglob('*.py'):\n    ast.parse(path.read_text())\n",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "ADVISORY duplicate_discovery" in result.stdout
    assert "  duplicate .githooks/pre-push::git_hook" in result.stdout
    assert "  scanner scripts/scan_everything.py:4" in result.stdout


def test_structural_waste_bootstrap_reports_missing_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(SCRIPT, "inventory_structural_waste_for_missing_runtime_test")
    fake_resolved = SimpleNamespace(parents=[ROOT / "does-not-contain-bootstrap"])
    monkeypatch.setattr(module, "Path", lambda _value: SimpleNamespace(resolve=lambda: fake_resolved))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()


def test_structural_waste_discovery_loader_reports_missing_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lib = _load_module(LIB, "structural_waste_lib_missing_helper_test")
    monkeypatch.setattr(lib.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)

    with pytest.raises(ImportError, match="Unable to load"):
        lib._load_discovery_lib()


def test_structural_waste_helper_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lib = _load_module(LIB, "structural_waste_lib_edges_test")
    repo = tmp_path / "repo"
    repo.mkdir()
    tracked = SimpleNamespace(returncode=0, stdout=b"scripts/a.py\0")
    monkeypatch.setattr(lib.subprocess, "run", lambda *_args, **_kwargs: tracked)
    _write(repo / "scripts" / "a.py", "print('a')\n")

    assert lib._tracked_files(repo) == [repo / "scripts" / "a.py"]

    monkeypatch.setattr(lib, "_tracked_files", lambda _repo: [tmp_path / "outside.py"])
    assert lib._python_sources(repo) == []

    assert lib._duplicate_discovery_candidates(
        [{"path": "x", "origin": "test", "snippet": "python3 -m pytest -q"}],
        [],
    ) == []

    bad = repo / "scripts" / "bad.py"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_bytes(b"\xff")
    no_parser = repo / "scripts" / "no_parser.py"
    no_parser.write_text("from pathlib import Path\nfor path in Path('.').rglob('*.py'):\n    print(path)\n", encoding="utf-8")
    monkeypatch.setattr(lib, "_python_sources", lambda _repo: [bad, no_parser])

    assert lib._broad_scanner_candidates(repo) == []
