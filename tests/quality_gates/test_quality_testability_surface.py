from __future__ import annotations

import json
from pathlib import Path

from .support import run_script, write_executable

SCRIPT = "skills/public/quality/scripts/inventory_testability_surface.py"

STUB_MAP_JSON = json.dumps(
    {
        "corpus": "stub",
        "note": "risk ranking, not a bug list",
        "findings": [
            {
                "class": "welded",
                "col": 12,
                "demand": True,
                "file": "runner.mjs",
                "kind": "subprocess",
                "line": 42,
                "reason": "exe-inline",
            },
            {
                "class": "welded",
                "col": 2,
                "demand": False,
                "file": "runner.mjs",
                "kind": "fileio",
                "line": 7,
                "reason": "fs-global",
            },
        ],
        "summary": {
            "files_scanned": 1,
            "welded": 2,
            "seamed": 0,
            "substitution_demand_subset": {"total": 1, "welded": 1, "seamed": 0},
        },
    }
)


def _write_pry_stub(path: Path) -> None:
    write_executable(
        path,
        "\n".join(
            [
                "#!/usr/bin/env bash",
                'if [[ "${1:-}" == "--version" ]]; then',
                '  echo "pry 9.9.9"',
                "  exit 0",
                "fi",
                'if [[ "${1:-}" == "map" ]]; then',
                f"  cat <<'JSON'\n{STUB_MAP_JSON}\nJSON",
                "  exit 0",
                "fi",
                "exit 2",
                "",
            ]
        ),
    )


def test_testability_surface_reports_degraded_when_pry_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--json",
        env={"PRY_BIN": str(tmp_path / "no-such-pry"), "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["engine"] == "pry"
    assert payload["pry_version"] is None
    assert "pry" in payload["reason"].lower()
    assert payload["demand_backlog"] == []
    assert payload["advisory_notes"]


def test_testability_surface_parses_welded_at_demand_backlog(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    stub = tmp_path / "pry-stub"
    _write_pry_stub(stub)

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--path",
        ".",
        "--json",
        env={"PRY_BIN": str(stub), "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["pry_version"] == "pry 9.9.9"
    assert payload["totals"] == {
        "files_scanned": 1,
        "welded": 2,
        "seamed": 0,
        "demand_total": 1,
    }
    assert payload["demand_backlog"] == [
        {
            "path": ".",
            "file": "runner.mjs",
            "line": 42,
            "col": 12,
            "kind": "subprocess",
            "reason": "exe-inline",
            "class": "welded",
        }
    ]


def test_testability_surface_human_output_lists_backlog(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    stub = tmp_path / "pry-stub"
    _write_pry_stub(stub)

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--path",
        ".",
        env={"PRY_BIN": str(stub), "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 0, result.stderr
    assert "welded-at-demand backlog" in result.stdout
    assert "runner.mjs:42 subprocess (exe-inline)" in result.stdout
