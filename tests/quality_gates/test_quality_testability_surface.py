from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT, run_script, write_executable

SCRIPT = "skills/public/quality/scripts/inventory_testability_surface.py"

# Import the module in-process so coverage instrumentation tracks it; the
# subprocess tests below prove the real CLI, but the changed-line coverage gate
# only sees in-process execution.
_SPEC = importlib.util.spec_from_file_location("inventory_testability_surface_mod", ROOT / SCRIPT)
mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mod)

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
            {
                # demand=true but already seamed -> testable, must NOT be backlog
                "class": "seamed",
                "col": 17,
                "demand": True,
                "file": "runner.mjs",
                "kind": "subprocess",
                "line": 99,
                "reason": "callee-param-injected",
            },
        ],
        "summary": {
            "files_scanned": 1,
            "welded": 2,
            "seamed": 1,
            "substitution_demand_subset": {"total": 2, "welded": 1, "seamed": 1},
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
        "seamed": 1,
        "demand_total": 2,
        "welded_at_demand": 1,
    }
    # demand_total counts both demand findings, but the backlog excludes the
    # already-seamed one (line 99) — only the welded-at-demand finding remains.
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
    # A non-empty backlog leads with ADVISORY so run-quality.sh surfaces it.
    assert result.stdout.startswith("ADVISORY: ")
    assert "welded-at-demand backlog" in result.stdout
    assert "runner.mjs:42 subprocess (exe-inline)" in result.stdout
    # The already-seamed demand finding (line 99) is testable, not backlog.
    assert "runner.mjs:99" not in result.stdout


# --- In-process tests (coverage-visible) ---


def _stub_report() -> dict:
    return json.loads(STUB_MAP_JSON)


class _FakeCompleted:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_in_process_ok_aggregates_across_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "_pry_binary", lambda: "pry")
    monkeypatch.setattr(mod, "_pry_version", lambda binary: "pry 9.9.9")
    monkeypatch.setattr(mod, "_run_pry_map", lambda binary, repo_root, path: _stub_report())

    payload = mod.inventory_testability_surface(tmp_path, paths=["a", "b"])

    assert payload["status"] == "ok"
    assert payload["pry_version"] == "pry 9.9.9"
    # One welded-at-demand finding per path; the seamed-demand finding is excluded.
    assert payload["totals"]["welded_at_demand"] == 2
    assert payload["totals"]["demand_total"] == 4
    assert len(payload["demand_backlog"]) == 2
    assert all(entry["class"] == "welded" for entry in payload["demand_backlog"])


def test_in_process_degraded_when_binary_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "_pry_binary", lambda: None)

    payload = mod.inventory_testability_surface(tmp_path, paths=["."])

    assert payload["status"] == "degraded"
    assert payload["pry_version"] is None
    assert payload["demand_backlog"] == []
    assert payload["totals"]["welded_at_demand"] == 0


def test_in_process_degraded_when_all_paths_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "_pry_binary", lambda: "pry")
    monkeypatch.setattr(mod, "_pry_version", lambda binary: "pry 9.9.9")

    def boom(binary, repo_root, path):
        raise RuntimeError(f"pry map {path} exploded")

    monkeypatch.setattr(mod, "_run_pry_map", boom)

    payload = mod.inventory_testability_surface(tmp_path, paths=["x"])

    assert payload["status"] == "degraded"
    assert "exploded" in payload["reason"]


def test_pry_binary_resolution(monkeypatch, tmp_path: Path) -> None:
    real = tmp_path / "pry"
    real.write_text("", encoding="utf-8")
    monkeypatch.setenv("PRY_BIN", str(real))
    assert mod._pry_binary() == str(real)

    monkeypatch.setenv("PRY_BIN", str(tmp_path / "absent"))
    assert mod._pry_binary() is None

    monkeypatch.delenv("PRY_BIN", raising=False)
    monkeypatch.setattr(mod.shutil, "which", lambda name: "/usr/bin/pry")
    assert mod._pry_binary() == "/usr/bin/pry"


def test_pry_version_paths(monkeypatch) -> None:
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _FakeCompleted(0, "pry 1.2.3\n"))
    assert mod._pry_version("pry") == "pry 1.2.3"

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _FakeCompleted(1, ""))
    assert mod._pry_version("pry") is None

    def raise_os(*a, **k):
        raise OSError("not executable")

    monkeypatch.setattr(mod.subprocess, "run", raise_os)
    assert mod._pry_version("pry") is None


def test_run_pry_map_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _FakeCompleted(0, STUB_MAP_JSON))
    report = mod._run_pry_map("pry", tmp_path, ".")
    assert report["summary"]["files_scanned"] == 1

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _FakeCompleted(2, "", "bad path"))
    with pytest.raises(RuntimeError):
        mod._run_pry_map("pry", tmp_path, ".")

    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="pry", timeout=1)

    monkeypatch.setattr(mod.subprocess, "run", raise_timeout)
    with pytest.raises(RuntimeError):
        mod._run_pry_map("pry", tmp_path, ".")


def test_main_in_process(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(mod, "_pry_binary", lambda: "pry")
    monkeypatch.setattr(mod, "_pry_version", lambda binary: "pry 9.9.9")
    monkeypatch.setattr(mod, "_run_pry_map", lambda binary, repo_root, path: _stub_report())

    out = tmp_path / "out.json"
    monkeypatch.setattr(
        sys, "argv", ["prog", "--repo-root", str(tmp_path), "--path", ".", "--json", "--output", str(out)]
    )
    assert mod.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ok"
    assert out.exists()

    monkeypatch.setattr(sys, "argv", ["prog", "--repo-root", str(tmp_path), "--path", "."])
    assert mod.main() == 0
    assert capsys.readouterr().out.startswith("ADVISORY: ")

    monkeypatch.setattr(mod, "_pry_binary", lambda: None)
    monkeypatch.setattr(sys, "argv", ["prog", "--repo-root", str(tmp_path)])
    assert mod.main() == 0
    assert "degraded" in capsys.readouterr().out
