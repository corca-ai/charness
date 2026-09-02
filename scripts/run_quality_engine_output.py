#!/usr/bin/env python3
"""Shell-compatible gate status, output surfacing, and receipt ledger."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from run_quality_engine_phase import GateResult

_ATTENTION = re.compile(r"(^|: |- |[\"'])(WARNING|WARN|WEAK|ADVISORY)(:|\s)")


def format_elapsed(elapsed_ms: int) -> str:
    if elapsed_ms >= 1000:
        return f"{elapsed_ms // 1000}.{(elapsed_ms % 1000) // 100}s"
    return f"{elapsed_ms}ms"


@dataclass
class Ledger:
    passed: int = 0
    failed: int = 0
    unestablished: list[str] = field(default_factory=list)
    measured_scope: list[str] = field(default_factory=list)
    adverse_subjects: list[str] = field(default_factory=list)
    recoveries: list[str] = field(default_factory=list)


def consume_result(result: GateResult, *, verbose: bool, failure_dir: Path, ledger: Ledger) -> None:
    print(
        f"{result.status.upper().replace('UNESTABLISHED', 'UNPROVEN')} {result.gate.label:<24} {format_elapsed(result.elapsed_ms)}"
    )
    attention = bool(result.log and _ATTENTION.search(result.log))
    if result.status in {"fail", "unestablished"} or verbose or attention:
        print(f"--- {result.gate.label} output ---")
        print(result.log, end="" if result.log.endswith("\n") else "\n") if result.log else print(
            "(no output)"
        )
    if result.status == "pass":
        ledger.passed += 1
        ledger.measured_scope.append(result.gate.label)
        return
    if result.status == "unestablished":
        ledger.unestablished.append(result.gate.label)
        return
    ledger.failed += 1
    ledger.adverse_subjects.append(result.gate.label)
    target = failure_dir / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', result.gate.label)}.log"
    try:
        failure_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(result.log, encoding="utf-8")
        ledger.recoveries.append(f"available:{target}")
    except OSError:
        print(
            f"WARN: could not save full output for {result.gate.label} to {target}; its log is NOT available.",
            file=sys.stderr,
        )
        ledger.recoveries.append("unavailable:full output could not be copied")


def add_filter_failure(ledger: Ledger) -> None:
    ledger.failed += 1
    ledger.adverse_subjects.append("explicit label filter")
    ledger.recoveries.append("unavailable:no phase matched the explicit filter")
