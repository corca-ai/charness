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
from pathlib import Path
from typing import Any

import yaml

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


def _load_goal_lineage(repo_root: Path, path_value: str | None) -> dict[str, Any]:
    candidates = [repo_root / "scripts" / "goal_lineage.py"]
    here = Path(__file__).resolve()
    candidates.extend(ancestor / "scripts" / "goal_lineage.py" for ancestor in (here, *here.parents))
    lineage_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if lineage_path is None:
        raise RoundFindingsError("scripts/goal_lineage.py is not available")
    spec = importlib.util.spec_from_file_location("charness_round_goal_lineage", lineage_path)
    if spec is None or spec.loader is None:
        raise RoundFindingsError(f"cannot load goal lineage helper: {lineage_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        if path_value is None:
            return module.not_goal_bound_lineage(
                "critique round was recorded without a Goal Run Work Item identity"
            )
        loaded = module.load_goal_lineage_file(repo_root, Path(path_value))
        return module.require_goal_execution_identity(loaded)
    except module.LineageError as exc:
        raise RoundFindingsError(str(exc)) from exc


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


def _load_worker_support():
    """Load the adjacent source or exported shared worker-chain owner."""
    here = Path(__file__).resolve()
    candidates = (
        ancestor / "shared/scripts/reviewer_worker_carrier_support.py"
        for ancestor in (here.parent, *here.parents)
    )
    support_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if support_path is None:
        raise RoundFindingsError("shared reviewer worker carrier support is unavailable")
    spec = importlib.util.spec_from_file_location(
        "charness_round_worker_carrier_support", support_path
    )
    if spec is None or spec.loader is None:
        raise RoundFindingsError(f"cannot load worker carrier support: {support_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RoundFindingsError(f"cannot load worker carrier support: {exc}") from exc
    return module


def _normalize_worker_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize reports written before ``boundary_mode`` became explicit.

    The generic delivery proof still requires a concrete boundary mode. Older
    reports already carry a non-empty boundary fingerprint, which identifies
    the only compatible mode without inventing new evidence. Keep this
    compatibility at the critique-recording boundary; reports without either
    field remain rejected by the generic carrier validator.
    """
    if payload.get("boundary_mode") is not None:
        return payload
    fingerprint = payload.get("boundary_fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint.strip():
        return payload
    normalized = dict(payload)
    normalized["boundary_mode"] = "shared-tree-fingerprint"
    provenance = payload.get("provenance")
    if isinstance(provenance, dict) and provenance.get("boundary_mode") is None:
        normalized["provenance"] = {
            **provenance,
            "boundary_mode": "shared-tree-fingerprint",
        }
    return normalized


def _read_worker_report(
    repo_root: Path, report_arg: str
) -> tuple[str, str, dict[str, Any]]:
    support = _load_worker_support()
    try:
        report_path = support._report_path(repo_root, report_arg)
        raw = report_path.read_bytes()
        payload = yaml.safe_load(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError, support.WorkerCarrierError) as exc:
        raise RoundFindingsError(f"worker report is unreadable or unsafe: {exc}") from exc
    if not isinstance(payload, dict):
        raise RoundFindingsError("worker report must contain a mapping")
    return (
        _repo_relative(repo_root, report_path),
        hashlib.sha256(raw).hexdigest(),
        _normalize_worker_report(payload),
    )


def _read_typed_findings(
    repo_root: Path, receipt: dict[str, Any], result_sha256: str
) -> tuple[str, str]:
    support = _load_worker_support()
    output_value = receipt.get("output_file")
    if not isinstance(output_value, str):
        raise RoundFindingsError("worker receipt has no typed result path")
    try:
        result_path = support._report_path(repo_root, output_value)
        raw = result_path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError, support.WorkerCarrierError) as exc:
        raise RoundFindingsError(f"typed worker result is unreadable: {exc}") from exc
    if not raw.strip():
        raise RoundFindingsError("typed worker result must not be empty")
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if observed_sha256 != result_sha256:
        raise RoundFindingsError("typed worker result changed after delivery-chain validation")
    return _repo_relative(repo_root, result_path), text if text.endswith("\n") else text + "\n"


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
    worker_report: str,
    recorded_date: str,
    goal_lineage_file: str | None = None,
) -> dict[str, Any]:
    """Write one non-overwritable record and return its machine-readable receipt."""
    if round_number < 1:
        raise RoundFindingsError("round must be a positive integer")
    goal_lineage = _load_goal_lineage(repo_root, goal_lineage_file)
    snapshot_path, snapshot_sha256 = _read_snapshot(repo_root, snapshot, window_id)
    report_path, report_sha256, report = _read_worker_report(repo_root, worker_report)
    if report.get("boundary_fingerprint") != snapshot_sha256:
        raise RoundFindingsError(
            "worker report boundary fingerprint does not match the supplied boundary snapshot"
        )
    support = _load_worker_support()
    try:
        receipt, result, findings_sha256 = support.validate_delivered_worker_report(
            repo_root=repo_root, report=report
        )
    except Exception as exc:
        raise RoundFindingsError(f"worker report delivery is not a typed result: {exc}") from exc
    result_path, findings_text = _read_typed_findings(repo_root, receipt, findings_sha256)
    execution_identity = {
        "attempt_id": report["attempt_id"],
        "backend": report.get("backend"),
        "boundary_fingerprint": report["boundary_fingerprint"],
        "execution_mode": report["execution_mode"],
        "packet_identity": report["packet_identity"],
        "parent_receipt_identity": report["parent_receipt_identity"],
        "producer_run_id": report["producer_run_id"],
        "reviewed_input_identity": report["reviewed_input_identity"],
        "scope": report["scope"],
    }
    execution_identity_canonical = json.dumps(
        execution_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    execution_identity_sha256 = hashlib.sha256(
        execution_identity_canonical.encode("utf-8")
    ).hexdigest()
    output_path = _record_path(repo_root, recorded_date, window_id)
    if output_path.exists():
        raise RoundFindingsError(f"round record already exists; refusing overwrite: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lineage_canonical = json.dumps(
        goal_lineage, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "\n"
    lineage_sha256 = hashlib.sha256(lineage_canonical.encode("utf-8")).hexdigest()
    lineage_pretty = json.dumps(goal_lineage, ensure_ascii=False, indent=2, sort_keys=True)
    content = (
        "# Critique Round Findings\n\n"
        f"- Round: {round_number}\n"
        f"- Recorded date: {recorded_date}\n"
        f"- Boundary window id: `{window_id}`\n"
        f"- Boundary snapshot: `{snapshot_path}`\n"
        f"- Boundary snapshot SHA-256: `{snapshot_sha256}`\n"
        f"- Findings SHA-256: `{findings_sha256}`\n\n"
        "## Reviewer Provenance\n\n"
        f"- Worker report: `{report_path}`\n"
        f"- Worker report SHA-256: `{report_sha256}`\n"
        f"- Worker result: `{result_path}`\n"
        f"- Worker result SHA-256: `{findings_sha256}`\n"
        f"- Reviewer execution identity: `attempt_id={report['attempt_id']}; producer_run_id={report['producer_run_id']}; execution_mode={report['execution_mode']}`\n"
        f"- Reviewer execution identity SHA-256: `{execution_identity_sha256}`\n"
        f"- Scope: `{report['scope']}`\n"
        f"- Backend: `{report.get('backend')}`\n"
        f"- Packet identity SHA-256: `{report['packet_identity']}`\n"
        f"- Reviewed input identity SHA-256: `{report['reviewed_input_identity']}`\n"
        f"- Parent receipt identity: `{report['parent_receipt_identity']}`\n"
        f"- Delivery state: `{report['delivery_state']}`\n"
        f"- Typed verdict: `{result['verdict']}`\n\n"
        "## Goal Evidence Lineage\n\n"
        f"- Lineage SHA-256: `{lineage_sha256}`\n\n"
        "```json\n"
        f"{lineage_pretty}\n"
        "```\n\n"
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
        "worker_report": report_path,
        "worker_report_sha256": report_sha256,
        "worker_result": result_path,
        "worker_result_sha256": findings_sha256,
        "reviewer_execution_identity_sha256": execution_identity_sha256,
        "review_verdict": result["verdict"],
        "goal_lineage": goal_lineage,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--round", type=int, required=True, dest="round_number")
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--boundary-snapshot", required=True)
    parser.add_argument(
        "--worker-report",
        required=True,
        help="Repo-relative or in-repo path to the typed delivered worker report YAML",
    )
    parser.add_argument("--goal-lineage-file", help="Repo-relative full Goal Run evidence-lineage JSON")
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
            worker_report=args.worker_report,
            recorded_date=args.recorded_date,
            goal_lineage_file=args.goal_lineage_file,
        )
    except RoundFindingsError as exc:
        _emit_yaml({"ok": False, "error": str(exc)})
        return 2
    _emit_yaml(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
