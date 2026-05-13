"""Regression tests for scripts/run_cautilus_eval.py.

The wrapper enforces the planner-consult contract from
skills/public/quality/references/cautilus-on-demand.md: bare `cautilus evaluate`
must not run without either (a) a non-`none` planner next_action or (b) an
operator-supplied --justification-log pointing at a real failing-log file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_cautilus_eval.py"


def _run(*extra: str, justification_log: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--mode", "fixture", "--dry-run"]
    if justification_log is not None:
        cmd += ["--justification-log", str(justification_log)]
    cmd += list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=ROOT)


def test_refuses_when_planner_says_next_action_none(tmp_path: Path) -> None:
    # No justification-log → planner default refusal must fire.
    result = _run("--paths")
    assert result.returncode == 2, result.stdout
    assert "next_action=\"none\"" in result.stderr
    assert "cautilus-on-demand.md" in result.stderr


def test_refuses_when_justification_log_missing(tmp_path: Path) -> None:
    missing = tmp_path / "no-such-log.txt"
    result = _run("--paths", justification_log=missing)
    assert result.returncode == 2, result.stdout
    assert "is missing" in result.stderr


def test_refuses_when_justification_log_empty(tmp_path: Path) -> None:
    empty = tmp_path / "empty-log.txt"
    empty.write_text("", encoding="utf-8")
    result = _run("--paths", justification_log=empty)
    assert result.returncode == 2, result.stdout
    assert "is empty" in result.stderr


def test_refuses_when_justification_log_below_min_bytes(tmp_path: Path) -> None:
    tiny = tmp_path / "tiny-log.txt"
    tiny.write_text("failing-prompt\n", encoding="utf-8")  # marker present but only 15 bytes
    result = _run("--paths", justification_log=tiny)
    assert result.returncode == 2, result.stdout
    assert "bytes" in result.stderr
    assert "behavior proof" in result.stderr


def test_refuses_when_justification_log_lacks_source_kind_line(tmp_path: Path) -> None:
    no_marker = tmp_path / "no-marker.txt"
    no_marker.write_text(
        "This is a long-enough log file that says nothing structured.\n",
        encoding="utf-8",
    )
    result = _run("--paths", justification_log=no_marker)
    assert result.returncode == 2, result.stdout
    assert "no `- source-kind:" in result.stderr


def test_refuses_when_source_kind_is_unrecognized(tmp_path: Path) -> None:
    weird = tmp_path / "weird-kind.txt"
    weird.write_text(
        "- source-kind: vibes\nA long-enough body to clear the 32-byte minimum.\n",
        encoding="utf-8",
    )
    result = _run("--paths", justification_log=weird)
    assert result.returncode == 2, result.stdout
    assert "supported kinds are" in result.stderr


def test_refuses_when_marker_only_appears_as_substring(tmp_path: Path) -> None:
    # The pre-tighten wrapper would accept this; the line-shape check rejects it.
    substring_only = tmp_path / "substring-only.txt"
    substring_only.write_text(
        "Conversational note about a failing-prompt encountered earlier today.\n",
        encoding="utf-8",
    )
    result = _run("--paths", justification_log=substring_only)
    assert result.returncode == 2, result.stdout
    assert "no `- source-kind:" in result.stderr


def test_forwards_when_justification_log_has_marker_and_minimum_size(tmp_path: Path) -> None:
    log = tmp_path / "failing-prompt.txt"
    log.write_text(
        "- source-kind: failing-prompt\nA real failing prompt body goes here.\n",
        encoding="utf-8",
    )
    result = _run("--paths", "--", "--fixture", "demo.json", justification_log=log)
    assert result.returncode == 0, result.stderr
    assert "would run:" in result.stdout
    assert "cautilus evaluate fixture" in result.stdout
    assert "--fixture demo.json" in result.stdout


def test_strips_double_dash_separator(tmp_path: Path) -> None:
    log = tmp_path / "log.txt"
    log.write_text(
        "- source-kind: regression-log\nA long-enough log line satisfying the size minimum.\n",
        encoding="utf-8",
    )
    result = _run("--paths", "--", "--alpha", "beta", justification_log=log)
    assert result.returncode == 0, result.stderr
    assert "cautilus evaluate fixture --alpha beta" in result.stdout
    assert " -- " not in result.stdout
