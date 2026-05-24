from __future__ import annotations

import getpass
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"
LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "standing_test_economics_lib.py"


def _load_inventory_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("standing_test_economics_lib_for_test", LIB)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standing_test_economics_surfaces_runner_startup_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps({"scripts": {"test:unit": "node --test --import tsx tests/**/*.test.ts"}}),
        encoding="utf-8",
    )
    tests = repo / "tests"
    tests.mkdir()
    for index in range(52):
        (tests / f"case{index}.test.ts").write_text("import { spawnSync } from 'node:child_process';\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["test_file_count"] == 52
    finding_types = {finding["type"] for finding in payload["findings"]}
    assert {
        "many_test_files",
        "node_test_isolation_unknown",
        "transpiler_startup_surface",
        "nested_cli_fanout",
    }.issubset(finding_types)


def test_standing_test_economics_ignores_generated_mutant_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_real.py").write_text("def test_real():\n    assert True\n", encoding="utf-8")
    mutant_tests = repo / "mutants" / "tests"
    mutant_tests.mkdir(parents=True)
    (mutant_tests / "test_generated.py").write_text("def test_generated():\n    assert True\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["test_file_count"] == 1


def test_standing_test_economics_reports_pytest_temp_footprint(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    pytest_root = tmp_path / f"pytest-of-{getpass.getuser()}" / "pytest-0" / "popen-gw0"
    seed = pytest_root / "charness-repo-seed0"
    top_test = pytest_root / "test_expensive0"
    seed.mkdir(parents=True)
    top_test.mkdir()
    (seed / "payload.bin").write_bytes(b"x" * 11)
    (top_test / "payload.bin").write_bytes(b"x" * 13)

    env = {**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = json.loads(result.stdout)
    footprint = payload["pytest_temp_footprint"]

    assert footprint["status"] == "available"
    assert footprint["session_count"] == 1
    assert footprint["worker_dir_count"] == 1
    assert footprint["total_disk_bytes"] >= 24
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["bytes"] >= 11
    assert footprint["seed_totals"]["charness-repo-seed"]["disk_bytes"] >= 11
    assert footprint["top_test_dirs"][0]["bytes"] >= 13
    assert footprint["top_test_dirs"][0]["disk_bytes"] >= 13


def test_standing_test_economics_does_not_double_count_nested_seed_dirs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    pytest_root = tmp_path / f"pytest-of-{getpass.getuser()}" / "pytest-0" / "popen-gw0"
    outer = pytest_root / "charness-repo-seed0"
    nested = outer / "charness-repo-seed-nested"
    nested.mkdir(parents=True)
    (outer / "outer.bin").write_bytes(b"x" * 11)
    (nested / "nested.bin").write_bytes(b"x" * 13)

    env = {**os.environ, "PYTEST_DEBUG_TEMPROOT": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    footprint = json.loads(result.stdout)["pytest_temp_footprint"]

    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["bytes"] >= 24
    assert footprint["seed_totals"]["charness-repo-seed"]["disk_bytes"] >= 24


def test_pytest_temp_footprint_tolerates_disappearing_temp_dirs(tmp_path: Path, monkeypatch) -> None:
    lib = _load_inventory_lib()
    root = tmp_path / f"pytest-of-{getpass.getuser()}"
    session = root / "pytest-0"
    worker = session / "popen-gw0"
    stale = root / "garbage-stale"
    worker.mkdir(parents=True)
    stale.mkdir(parents=True)

    original_iterdir = Path.iterdir

    def racy_iterdir(path: Path):
        if path == root:
            yield session
            raise FileNotFoundError(stale)
        yield from original_iterdir(path)

    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path))
    monkeypatch.setattr(lib, "_du_bytes", lambda *args: None)
    monkeypatch.setattr(Path, "iterdir", racy_iterdir)

    footprint = lib._pytest_temp_footprint()

    assert footprint["status"] == "available"
    assert footprint["session_count"] == 1
    assert footprint["worker_dir_count"] == 1


def test_pytest_temp_iter_helpers_skip_missing_and_stale_children(
    tmp_path: Path,
    monkeypatch,
) -> None:
    lib = _load_inventory_lib()
    root = tmp_path / "root"
    root.mkdir()
    file_path = root / "payload.bin"
    stale_path = root / "stale.bin"
    file_path.write_bytes(b"x")
    stale_path.write_bytes(b"y")

    missing = tmp_path / "missing"
    original_iterdir = Path.iterdir
    original_stat = Path.stat

    def flaky_iterdir(path: Path):
        if path == missing:
            raise FileNotFoundError(path)
        return original_iterdir(path)

    def flaky_stat(path: Path, *args, **kwargs):
        if path == stale_path:
            raise FileNotFoundError(path)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "iterdir", flaky_iterdir)
    monkeypatch.setattr(Path, "stat", flaky_stat)

    assert list(lib._iter_child_stats(missing)) == []
    assert [item.st_size for item in lib._iter_file_stats(root)] == [1]
