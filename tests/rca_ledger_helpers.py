from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
from pathlib import Path

from scripts import aggregate_rca_ledger, record_rca_event, validate_rca_ledger

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_LEDGER = ROOT / "charness-artifacts" / "metrics" / "rca-ledger.jsonl"
SCRIPT_MAINS = {
    "aggregate_rca_ledger.py": aggregate_rca_ledger.main,
    "record_rca_event.py": record_rca_event.main,
    "validate_rca_ledger.py": validate_rca_ledger.main,
}


def run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    command = ["python3", f"scripts/{script}", *args]
    main = SCRIPT_MAINS.get(script)
    if main is None:
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_cwd = Path.cwd()
    os.chdir(ROOT)
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                returncode = main(list(args))
            except SystemExit as exc:
                returncode = int(exc.code) if isinstance(exc.code, int) else 1
    finally:
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        command,
        returncode,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
    )


def event(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": 1,
        "ts": "2026-05-24T00:00:00Z",
        "source": "debug",
        "event_kind": "bug",
        "converted": True,
        "durable_kind": "gate",
        "class_key": "k",
    }
    record.update(overrides)
    return record


def ts_event(day: int, **overrides: object) -> dict[str, object]:
    return event(ts=f"2026-06-{day:02d}T00:00:00Z", **overrides)


def seed_only_both_outcomes() -> list[dict[str, object]]:
    return [
        event(converted=True, durable_kind="gate", seed=True),
        event(converted=False, durable_kind="none", seed=True),
    ]


def write_ledger(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )


def write_raw(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
