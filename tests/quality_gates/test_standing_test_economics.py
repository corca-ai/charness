from __future__ import annotations

import json
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
