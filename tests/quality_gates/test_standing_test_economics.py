from __future__ import annotations

import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"


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
    assert footprint["seed_totals"]["charness-repo-seed"]["count"] == 1
    assert footprint["seed_totals"]["charness-repo-seed"]["bytes"] >= 11
    assert footprint["top_test_dirs"][0]["bytes"] >= 13


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
