"""In-process coverage for inventory_doc_duplicates.py error/print branches (#393 class).

The nose Markdown doc-duplicate advisory is exercised mainly via subprocess, so
its error-handling and human-render branches (nose version probe failures, query
timeout / non-zero exit / invalid JSON, and the ``print_human`` status dispatch)
stay uncovered; over a batch range that touched the file those changed lines read
as blocking changed lines — the same #393 recurrence class. These tests import
the module in-process and drive the previously-uncovered branches directly.
Test-only; no production change.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_doc_duplicates.py"


def _load():
    spec = importlib.util.spec_from_file_location("inventory_doc_duplicates_inproc", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dd = _load()


def _completed(stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(["nose"], returncode, stdout, stderr)


# --------------------------------------------------------------------------- #
# version probe
# --------------------------------------------------------------------------- #
def test_parse_nose_version_none() -> None:
    assert dd.parse_nose_version("no version token here") is None


def test_parse_nose_version_ok() -> None:
    assert dd.parse_nose_version("nose 0.13.0") == (0, 13, 0)


def test_nose_version_timeout(monkeypatch) -> None:
    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired("nose", 30)

    monkeypatch.setattr(dd.subprocess, "run", boom)
    assert dd.nose_version("nose") is None


def test_nose_version_oserror(monkeypatch) -> None:
    def boom(*_a, **_k):
        raise OSError("not executable")

    monkeypatch.setattr(dd.subprocess, "run", boom)
    assert dd.nose_version("nose") is None


def test_nose_version_ok(monkeypatch) -> None:
    monkeypatch.setattr(dd.subprocess, "run", lambda *_a, **_k: _completed(stdout="nose 0.13.0"))
    assert dd.nose_version("nose") == (0, 13, 0)


# --------------------------------------------------------------------------- #
# run_query branches
# --------------------------------------------------------------------------- #
def test_run_query_timeout(monkeypatch, tmp_path: Path) -> None:
    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired("nose", dd.NOSE_TIMEOUT_SECONDS)

    monkeypatch.setattr(dd.subprocess, "run", boom)
    result = dd.run_query(tmp_path, ["nose"])
    assert result["status"] == "error"
    assert "timed out" in result["stderr"]


def test_run_query_nonzero_exit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dd.subprocess, "run", lambda *_a, **_k: _completed(returncode=2, stderr="boom"))
    result = dd.run_query(tmp_path, ["nose"])
    assert result["status"] == "error"
    assert result["stderr"] == "boom"


def test_run_query_invalid_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dd.subprocess, "run", lambda *_a, **_k: _completed(stdout="not json"))
    result = dd.run_query(tmp_path, ["nose"])
    assert result["status"] == "error"
    assert "invalid JSON" in result["stderr"]


def test_run_query_ok(monkeypatch, tmp_path: Path) -> None:
    payload = json.dumps({"schema_version": 1, "markdown": [{"members": [{"path": "a.md", "heading": "H"}]}]})
    monkeypatch.setattr(dd.subprocess, "run", lambda *_a, **_k: _completed(stdout=payload))
    result = dd.run_query(tmp_path, ["nose"])
    assert result["status"] == "ok"
    assert len(result["families"]) == 1


# --------------------------------------------------------------------------- #
# print_human status dispatch
# --------------------------------------------------------------------------- #
def test_print_human_missing(capsys) -> None:
    dd.print_human({"status": "missing"})
    assert "nose missing" in capsys.readouterr().out


def test_print_human_version_too_old(capsys) -> None:
    dd.print_human({"status": "version-too-old", "tool_version": "0.10.0"})
    assert "too old" in capsys.readouterr().out


def test_print_human_error(capsys) -> None:
    dd.print_human({"status": "error", "stderr": "boom"})
    out = capsys.readouterr().out
    assert "doc inventory error" in out and "boom" in out


def test_print_human_baseline_written(capsys) -> None:
    dd.print_human({"status": "baseline-written", "baseline": "b.json", "family_count": 3})
    assert "doc baseline written" in capsys.readouterr().out


def test_print_human_findings_full(capsys) -> None:
    payload = {
        "status": "ok",
        "total_family_count": 5,
        "family_count": 1,
        "accepted_count": 4,
        "baseline": "charness-artifacts/quality/doc-nose-baseline.json",
        "families": [
            {
                "tier": "T1",
                "score": 0.9,
                "files": 2,
                "removable": 1,
                "witness": {"a": "a.md:1-2", "b": "b.md:3-4", "matched_lines": 2},
            }
        ],
        "interpretation": dict(dd.INTERPRETATION),
    }
    dd.print_human(payload)
    out = capsys.readouterr().out
    assert "doc-duplicate advisory" in out
    assert "BASELINE: active" in out
    assert "doc family #1" in out
    assert "INTERPRETATION" in out


# --------------------------------------------------------------------------- #
# main: non-json print path + --require-nose fail-closed
# --------------------------------------------------------------------------- #
def test_main_human_path(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(dd, "resolve_nose_bin", lambda: None)
    monkeypatch.setattr(sys, "argv", ["dd", "--repo-root", str(tmp_path)])
    assert dd.main() == 0
    assert "nose missing" in capsys.readouterr().out


def test_main_require_nose_fails_closed(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(dd, "resolve_nose_bin", lambda: None)
    monkeypatch.setattr(sys, "argv", ["dd", "--repo-root", str(tmp_path), "--require-nose"])
    assert dd.main() == 1  # status "missing" + --require-nose -> fail closed
    capsys.readouterr()
