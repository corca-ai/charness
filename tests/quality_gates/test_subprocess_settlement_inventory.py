from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"
SURFACE_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "surface_marker_lib.py"


def _load_surface_marker_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("surface_marker_lib_for_settlement_test", SURFACE_LIB)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_inventory_cli(*args: str):
    return run_loaded_script_main(
        "inventory_standing_test_economics.py",
        load_script_module("inventory_standing_test_economics_for_settlement_test", SCRIPT),
        *args,
    )


def test_subprocess_settlement_seams_are_conservative_and_callsite_attributed(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    fixture = tests / "test_settlement.py"
    fixture.write_text(
        "import subprocess\n\n"
        "def test_bounded():\n"
        "    subprocess.run(['probe'], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n\n"
        "def test_unbounded_capture():\n"
        "    subprocess.run(['probe'], capture_output=True)\n\n"
        "def test_mixed_output():\n"
        "    subprocess.run(['probe'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)\n\n"
        "def test_unknown_lifecycle():\n"
        "    subprocess.Popen(['observe'])\n\n"
        "def test_dynamic_timeout():\n"
        "    subprocess.run(['probe'], timeout=maybe_timeout)\n",
        encoding="utf-8",
    )

    assert lib.subprocess_settlement_seams(repo, [fixture]) == [
        {"path": "tests/test_settlement.py", "line": 4, "call": "subprocess.run", "deadline": "present", "lifecycle": "finite", "process_tree_termination": "unknown", "output_bounding": "bounded"},
        {"path": "tests/test_settlement.py", "line": 7, "call": "subprocess.run", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unbounded"},
        {"path": "tests/test_settlement.py", "line": 10, "call": "subprocess.run", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unbounded"},
        {"path": "tests/test_settlement.py", "line": 13, "call": "subprocess.Popen", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
        {"path": "tests/test_settlement.py", "line": 16, "call": "subprocess.run", "deadline": "unknown", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
    ]

    js_fixture = tests / "test_settlement.js"
    js_fixture.write_text(
        "execSync('probe', { timeout: 1000, stdio: 'ignore' });\n"
        "execSync('observe', { timeout: maybeUndefined });\n",
        encoding="utf-8",
    )
    assert lib.subprocess_settlement_seams(repo, [js_fixture]) == [
        {"path": "tests/test_settlement.js", "line": 1, "call": "execSync", "deadline": "present", "lifecycle": "finite", "process_tree_termination": "unknown", "output_bounding": "bounded"},
        {"path": "tests/test_settlement.js", "line": 2, "call": "execSync", "deadline": "unknown", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
    ]


def test_standing_test_economics_hides_settlement_callsite_list_in_summary(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_settlement.py").write_text(
        "import subprocess\nsubprocess.run(['probe'], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n",
        encoding="utf-8",
    )

    summary = _run_inventory_cli("--repo-root", str(repo), "--summary", "--json")
    detail = _run_inventory_cli("--repo-root", str(repo), "--detail", "--json")
    assert summary.returncode == 0, summary.stderr
    assert detail.returncode == 0, detail.stderr
    summary_payload = json.loads(summary.stdout)
    detail_payload = json.loads(detail.stdout)
    assert summary_payload["subprocess_settlement"] == {
        "seam_count": 1,
        "deadline_counts": {"present": 1, "absent": 0, "unknown": 0},
        "lifecycle_counts": {"finite": 1, "until_interrupted": 0, "unknown": 0},
        "process_tree_termination_counts": {"owned": 0, "not_owned": 0, "unknown": 1},
        "output_bounding_counts": {"bounded": 1, "unbounded": 0, "unknown": 0},
    }
    assert "seams" not in summary_payload["subprocess_settlement"]
    assert detail_payload["subprocess_settlement"]["seams"][0]["path"] == "tests/test_settlement.py"
