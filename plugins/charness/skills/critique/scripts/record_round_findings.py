#!/usr/bin/env python3
"""Persist one critique round before its findings leave the parent context.

The writer binds returned findings to the exact reviewer-boundary snapshot and
window id that framed the round. It does not judge whether a finding is
correct, nor whether the boundary snapshot is a good review scope; those are
reviewer and boundary-proof claims owned elsewhere. Its job is to make the
bytes available to the next round instead of relying on closeout transcription.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROUND_DIRECTORY = Path("charness-artifacts/critique/rounds")
WINDOW_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class RoundFindingsError(ValueError):
    """A caller supplied a round record that cannot be durably bound."""


def _emit_yaml(payload: dict[str, Any]) -> None:
    """Use the repo renderer when present, with JSON as valid YAML fallback."""
    for ancestor in Path(__file__).resolve().parents:
        helper = ancestor / "scripts" / "yaml_output.py"
        if not helper.is_file():
            continue
        spec = importlib.util.spec_from_file_location("charness_yaml_output", helper)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.emit_yaml(payload)
        return
    print(json.dumps(payload, ensure_ascii=False, sort_keys=False))


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise RoundFindingsError(f"path must stay under repo root: {path}") from exc


def _read_snapshot(repo_root: Path, snapshot_arg: str, window_id: str) -> tuple[str, str]:
    snapshot_path = Path(snapshot_arg)
    if not snapshot_path.is_absolute():
        snapshot_path = repo_root / snapshot_path
    snapshot_path = snapshot_path.resolve()
    if not snapshot_path.is_file():
        raise RoundFindingsError(f"boundary snapshot not found: {snapshot_path}")
    try:
        raw = snapshot_path.read_bytes()
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RoundFindingsError(f"boundary snapshot is unreadable: {snapshot_path}: {exc}") from exc
    observed_window = payload.get("window") if isinstance(payload, dict) else None
    observed_id = observed_window.get("id") if isinstance(observed_window, dict) else None
    if observed_id != window_id:
        raise RoundFindingsError(
            f"boundary snapshot window id mismatch: expected {window_id!r}, found {observed_id!r}"
        )
    return _repo_relative(repo_root, snapshot_path), hashlib.sha256(raw).hexdigest()


def _read_findings(findings_arg: str | None) -> tuple[str, str]:
    if findings_arg in (None, "-"):
        raw = sys.stdin.buffer.read()
    else:
        try:
            raw = Path(findings_arg).read_bytes()
        except OSError as exc:
            raise RoundFindingsError(f"findings file is unreadable: {findings_arg}: {exc}") from exc
    if not raw.strip():
        raise RoundFindingsError("reviewer findings must not be empty")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RoundFindingsError("reviewer findings must be UTF-8") from exc
    return text.rstrip() + "\n", hashlib.sha256(raw).hexdigest()


def _record_path(repo_root: Path, recorded_date: str, window_id: str) -> Path:
    if not WINDOW_ID_RE.fullmatch(window_id):
        raise RoundFindingsError("window id may contain only letters, digits, '.', '_' and '-'")
    try:
        dt.date.fromisoformat(recorded_date)
    except ValueError as exc:
        raise RoundFindingsError(
            f"recorded date must be ISO-8601 YYYY-MM-DD: {recorded_date!r}"
        ) from exc
    return repo_root / ROUND_DIRECTORY / f"{recorded_date}-{window_id}.md"


def record_round(
    repo_root: Path,
    *,
    round_number: int,
    window_id: str,
    snapshot: str,
    findings: str | None,
    recorded_date: str,
) -> dict[str, Any]:
    """Write one non-overwritable record and return its machine-readable receipt."""
    if round_number < 1:
        raise RoundFindingsError("round must be a positive integer")
    snapshot_path, snapshot_sha256 = _read_snapshot(repo_root, snapshot, window_id)
    findings_text, findings_sha256 = _read_findings(findings)
    output_path = _record_path(repo_root, recorded_date, window_id)
    if output_path.exists():
        raise RoundFindingsError(f"round record already exists; refusing overwrite: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "# Critique Round Findings\n\n"
        f"- Round: {round_number}\n"
        f"- Recorded date: {recorded_date}\n"
        f"- Boundary window id: `{window_id}`\n"
        f"- Boundary snapshot: `{snapshot_path}`\n"
        f"- Boundary snapshot SHA-256: `{snapshot_sha256}`\n"
        f"- Findings SHA-256: `{findings_sha256}`\n\n"
        "## Findings Returned\n\n"
        f"{findings_text}"
    )
    try:
        output_path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise RoundFindingsError(f"could not write round record: {output_path}: {exc}") from exc
    return {
        "ok": True,
        "round": round_number,
        "window_id": window_id,
        "path": _repo_relative(repo_root, output_path),
        "boundary_snapshot": snapshot_path,
        "boundary_snapshot_sha256": snapshot_sha256,
        "findings_sha256": findings_sha256,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--round", type=int, required=True, dest="round_number")
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--boundary-snapshot", required=True)
    parser.add_argument("--findings-file", help="UTF-8 reviewer output; omit or use '-' for stdin")
    parser.add_argument(
        "--recorded-date",
        default=dt.date.today().isoformat(),
        help="ISO date for the record filename (default: today)",
    )
    args = parser.parse_args(argv)
    try:
        receipt = record_round(
            args.repo_root.resolve(),
            round_number=args.round_number,
            window_id=args.window_id,
            snapshot=args.boundary_snapshot,
            findings=args.findings_file,
            recorded_date=args.recorded_date,
        )
    except RoundFindingsError as exc:
        _emit_yaml({"ok": False, "error": str(exc)})
        return 2
    _emit_yaml(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
