"""Unit coverage for quality-engine gap lines (#824).

The mutation sample flagged uncovered lines in the engine's preflight,
recovery probe, docs-only listing, label-filter exit, and the output
ledger writer. These tests execute each line with assertions that
distinguish the sampled operators.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts import run_quality_engine as _ENGINE
from scripts import run_quality_engine_output as _OUTPUT


def _context(tmp_path: Path, **overrides: Any) -> SimpleNamespace:
    values: dict[str, Any] = {
        "repo_root": tmp_path,
        "environment": {},
        "failure_log_dir": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _gate(**overrides: Any) -> SimpleNamespace:
    values: dict[str, Any] = {"label": "demo", "native_preflight": None}
    values.update(overrides)
    return SimpleNamespace(**values)


def test_native_preflight_skips_gates_without_probe() -> None:
    assert _ENGINE._native_preflight(_context(Path("/tmp")), [_gate()]) == 0


def test_native_preflight_reports_probe_failure(monkeypatch, tmp_path: Path) -> None:
    def failing(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=1, stdout="", stderr="")

    def passing(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(_ENGINE, "run_process", failing)
    assert _ENGINE._native_preflight(_context(tmp_path), [_gate(native_preflight="export-safe")]) == 1
    monkeypatch.setattr(_ENGINE, "run_process", passing)
    assert _ENGINE._native_preflight(_context(tmp_path), [_gate(native_preflight="export-safe")]) == 0


def test_mutation_recovery_pending_reads_both_markers(tmp_path: Path) -> None:
    context = _context(tmp_path)
    assert _ENGINE._mutation_recovery_pending(context) is False
    marker = tmp_path / ".charness" / "mutation-recovery"
    marker.parent.mkdir(parents=True)
    marker.write_text("pending", encoding="utf-8")
    assert _ENGINE._mutation_recovery_pending(context) is True


def test_mutation_recovery_pending_reads_git_dir_marker(
    tmp_path: Path, monkeypatch
) -> None:
    def git_dir_ok(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=".git\n", stderr="")

    def git_dir_missing(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=1, stdout="", stderr="not a repo")

    context = _context(tmp_path)
    monkeypatch.setattr(_ENGINE, "run_process", git_dir_missing)
    assert _ENGINE._mutation_recovery_pending(context) is False
    monkeypatch.setattr(_ENGINE, "run_process", git_dir_ok)
    assert _ENGINE._mutation_recovery_pending(context) is False
    recovery = tmp_path / ".git" / "charness-mutation-recovery"
    recovery.parent.mkdir(parents=True)
    recovery.write_text("pending", encoding="utf-8")
    assert _ENGINE._mutation_recovery_pending(context) is True


def test_consume_result_writes_failure_log_verbatim(tmp_path: Path, capsys) -> None:
    from run_quality_engine_phase import GateResult

    failure_dir = tmp_path / "failures"
    ledger = _OUTPUT.Ledger()
    result = GateResult(
        gate=SimpleNamespace(label="demo-gate"),
        command=("demo",),
        returncode=1,
        stdout="traceback line\n",
        stderr="",
        elapsed_ms=1500,
        status="fail",
    )
    _OUTPUT.consume_result(result, verbose=False, failure_dir=failure_dir, ledger=ledger)
    target = failure_dir / "demo-gate.log"
    assert target.read_text(encoding="utf-8") == "traceback line\n"
    assert ledger.failed == 1
    assert ledger.adverse_subjects == ["demo-gate"]
    assert ledger.recoveries == [f"available:{target}"]
    out = capsys.readouterr().out
    assert "FAIL demo-gate" in out
    assert "1.5s" in out


def test_consume_result_counts_pass_without_writing(tmp_path: Path, capsys) -> None:
    from run_quality_engine_phase import GateResult

    failure_dir = tmp_path / "failures"
    ledger = _OUTPUT.Ledger()
    result = GateResult(
        gate=SimpleNamespace(label="ok-gate"),
        command=("ok",),
        returncode=0,
        stdout="",
        stderr="",
        elapsed_ms=999,
        status="pass",
    )
    _OUTPUT.consume_result(result, verbose=False, failure_dir=failure_dir, ledger=ledger)
    assert ledger.passed == 1
    assert ledger.measured_scope == ["ok-gate"]
    assert not failure_dir.exists()
    assert "999ms" in capsys.readouterr().out
