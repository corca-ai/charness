"""Atomic storage helpers for durable critique-review carriers."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

DURABLE_WORKER_REPORTS = Path("charness-artifacts") / "critique" / "workers"
PROMOTED_METADATA = (
    "worker-report.yaml",
    "review-prompt.md",
    "run-plan.json",
    "bounded-review-result.schema.json",
    "capability.json",
    "lifecycle.yaml",
    "receipt.json",
    "delivery.json",
    "result.json",
)
SOURCE_KEYS = {
    "review-prompt.md": "prompt",
    "run-plan.json": "plan",
    "bounded-review-result.schema.json": "schema",
    "capability.json": "capability",
    "lifecycle.yaml": "summary",
    "receipt.json": "receipt",
    "delivery.json": "ledger",
    "result.json": "output",
}
# A reviewer can emit diagnostics before its final JSON.  Scan a bounded
# head/tail window rather than assuming the result is an early one-line record.
# The durable typed result is still much smaller than the log cap below.
PARTIAL_SCAN_LIMIT = 64 * 1024 * 1024
MAX_DURABLE_LOG_BYTES = 4 * 1024 * 1024
LOG_SOURCE_KEYS = {
    "runner.stdout": "runner_stdout",
    "runner.stderr": "runner_stderr",
    "backend.stdout": "backend_stdout",
    "backend.stderr": "backend_stderr",
}


def _support() -> Any:
    for name in ("charness_run_review_support", "run_review_support"):
        module = sys.modules.get(name)
        if module is not None:
            return module
    path = Path(__file__).with_name("run_review_support.py")
    spec = importlib.util.spec_from_file_location("charness_run_review_support", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load run_review_support: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["charness_run_review_support"] = module
    spec.loader.exec_module(module)
    return module


_REVIEWER_CONTRACT: Any | None = None


def _bounded_result_shape(payload: dict[str, Any]) -> str:
    """Load the shared result contract in both source and flat plugin layouts."""
    global _REVIEWER_CONTRACT
    if _REVIEWER_CONTRACT is None:
        here = Path(__file__).resolve()
        candidates = [
            ancestor / "skills" / "shared" / "scripts" / "reviewer_result_contract.py"
            for ancestor in (here.parent, *here.parents)
        ]
        candidates.extend(
            ancestor / "shared" / "scripts" / "reviewer_result_contract.py"
            for ancestor in (here.parent, *here.parents)
        )
        contract_path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if contract_path is None:
            raise ImportError("shared reviewer_result_contract.py is unavailable")
        spec = importlib.util.spec_from_file_location(
            "charness_reviewer_result_contract", contract_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load reviewer result contract: {contract_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _REVIEWER_CONTRACT = module
    return _REVIEWER_CONTRACT.bounded_result_shape(payload)


def _copy_atomically(source: Path, destination: Path) -> None:
    """Copy a bounded carrier without exposing a half-written durable file."""
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary)
    try:
        with source.open("rb") as source_handle, os.fdopen(fd, "wb") as destination_handle:
            shutil.copyfileobj(source_handle, destination_handle)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def copy_or_verify(source: Path, destination: Path) -> None:
    """Copy a durable input, or accept an identical prior promotion."""
    write_or_verify(destination, source.read_bytes())


def write_or_verify(destination: Path, payload: bytes) -> None:
    """Write durable bytes once, or accept an identical prior promotion."""
    if destination.is_symlink():
        raise _support().RunReviewError(
            "stale-artifact-refused",
            f"refusing to overwrite durable reviewer metadata: {destination}",
        )
    if destination.exists():
        if not destination.is_file() or destination.read_bytes() != payload:
            raise _support().RunReviewError(
                "stale-artifact-refused",
                f"refusing to overwrite durable reviewer metadata: {destination}",
            )
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomically(destination, payload)


def promote_worker_report(root: Path, attempt: str, runtime_report: Path) -> Path | None:
    """Copy the combined report into visible knowledge for older callers."""
    if not runtime_report.is_file():
        return None
    lexical_dest_dir = root / DURABLE_WORKER_REPORTS / attempt
    if lexical_dest_dir.is_symlink():
        raise _support().RunReviewError(
            "stale-artifact-refused",
            f"refusing to write through durable worker directory symlink: {lexical_dest_dir}",
        )
    dest_dir = lexical_dest_dir.resolve()
    try:
        dest_dir.relative_to(root.resolve())
    except ValueError as exc:
        raise _support().RunReviewError(
            "path-invalid", "durable worker report directory escaped repository root"
        ) from exc
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "worker-report.yaml"
    if dest.exists() or dest.is_symlink():
        raise _support().RunReviewError(
            "stale-artifact-refused",
            f"refusing to overwrite existing durable worker report: {dest}",
        )
    _copy_atomically(runtime_report, dest)
    return dest


def promote_semantic_inputs(
    root: Path, paths: dict[str, Path], dest_dir: Path
) -> dict[str, str]:
    """Retain backend-independent semantic bytes after scratch cleanup."""
    run_dir = paths.get("run_dir")
    source_dir = run_dir / "semantic-input" if run_dir is not None else None
    if source_dir is None or not source_dir.is_dir():
        return {}
    promoted: dict[str, str] = {}
    for source in sorted(source_dir.rglob("*")):
        if not source.is_file() or source.is_symlink():
            continue
        relative = source.relative_to(source_dir)
        destination = dest_dir / "semantic-input" / relative
        payload = source.read_bytes()
        if relative.as_posix() == "manifest.json":
            replacements = {
                _support().relative(root, source_dir / Path(key.removeprefix("semantic-input/"))): value
                for key, value in promoted.items()
                if key.startswith("semantic-input/") and key != "semantic-input/manifest.json"
            }
            payload = rewrite_path_references(payload, replacements)
        write_or_verify(destination, payload)
        source_mode = source.stat().st_mode & 0o777
        if destination.stat().st_mode & 0o777 != source_mode:
            if destination.exists() and destination.read_bytes() == payload:
                destination.chmod(source_mode)
            else:
                raise _support().RunReviewError(
                    "stale-artifact-refused",
                    f"durable semantic input mode changed: {destination}",
                )
        promoted[f"semantic-input/{relative.as_posix()}"] = _support().relative(root, destination)
    return promoted


def rewrite_path_references(payload: bytes, replacements: dict[str, str]) -> bytes:
    rewritten = payload
    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        rewritten = rewritten.replace(old.encode("utf-8"), new.encode("utf-8"))
    return rewritten


def report_path_replacements(
    paths: dict[str, Path], promoted: dict[str, str]
) -> dict[str, str]:
    """Rebind worker-report references from scratch bytes to durable carriers."""
    replacements: dict[str, str] = {}
    for name, source_key in SOURCE_KEYS.items():
        source = paths.get(source_key)
        durable = promoted.get(name)
        if source is not None and durable is not None:
            replacements[str(source)] = durable
    report_source = paths.get("report")
    durable_report = promoted.get("worker-report.yaml")
    if report_source is not None and durable_report is not None:
        replacements[str(report_source)] = durable_report
    return replacements


def semantic_path_replacements(
    root: Path, paths: dict[str, Path], promoted: dict[str, str]
) -> dict[str, str]:
    """Map materialized semantic-input paths to their durable copies."""
    run_dir = paths.get("run_dir")
    source_dir = run_dir / "semantic-input" if run_dir is not None else None
    if source_dir is None or not source_dir.is_dir():
        return {}
    replacements: dict[str, str] = {}
    for source in source_dir.rglob("*"):
        if not source.is_file() or source.is_symlink():
            continue
        relative = source.relative_to(source_dir)
        promoted_key = f"semantic-input/{relative.as_posix()}"
        durable = promoted.get(promoted_key)
        if durable is not None:
            replacements[_support().relative(root, source)] = durable
    return replacements


def write_json_atomically(destination: Path, payload: object) -> None:
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def write_bytes_atomically(destination: Path, payload: bytes) -> None:
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def promote_log(root: Path, source: Path, destination: Path) -> dict[str, Any]:
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    retained = raw
    truncated = False
    if len(raw) > MAX_DURABLE_LOG_BYTES:
        half = (MAX_DURABLE_LOG_BYTES - 96) // 2
        marker = b"\n[Charness durable log truncated; see source hash in manifest]\n"
        retained = raw[:half] + marker + raw[-half:]
        truncated = True
    if destination.is_symlink():
        raise _support().RunReviewError(
            "stale-artifact-refused",
            f"refusing to overwrite durable reviewer log: {destination}",
        )
    if destination.exists():
        if not destination.is_file() or destination.read_bytes() != retained:
            raise _support().RunReviewError(
                "stale-artifact-refused",
                f"refusing to overwrite durable reviewer log: {destination}",
            )
    else:
        write_bytes_atomically(destination, retained)
    return {
        "path": _support().relative(root, destination),
        "source": _support().relative(root, source),
        "bytes": len(raw),
        "retained_bytes": len(retained),
        "sha256": digest,
        "truncated": truncated,
    }


def _nested_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _nested_dicts(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _nested_dicts(nested)


def _json_values(raw: bytes):
    """Yield JSON values from noisy, line-delimited, or pretty-printed output."""
    if len(raw) > PARTIAL_SCAN_LIMIT:
        half = PARTIAL_SCAN_LIMIT // 2
        raw = raw[:half] + b"\n[Charness partial scan window]\n" + raw[-half:]
    text = raw.decode("utf-8", errors="replace")
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{":
            continue
        try:
            value, _end = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            continue
        yield from _nested_dicts(value)


def extract_partial_review(
    paths: dict[str, Path],
    report: dict[str, Any] | None,
    diagnostics: dict[str, Any] | None = None,
    *,
    expected_identities: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], Path, str] | None:
    """Find a matching bounded-review object in preserved runner logs.

    The result may be late, pretty-printed, wrapped by a backend envelope, or
    interleaved with ordinary log text.  Identity matching remains mandatory.
    """
    info = diagnostics if diagnostics is not None else {}
    info.update({"status": "unavailable", "scan_limit_bytes": PARTIAL_SCAN_LIMIT, "sources": []})
    expected = expected_identities or {}
    expected_packet = (
        expected.get("packet_sha256")
        or (report.get("packet_identity") if report else None)
        or (report.get("packet_sha256") if report else None)
    )
    expected_input = (
        expected.get("reviewed_input_identity_sha256")
        or (report.get("reviewed_input_identity") if report else None)
        or (report.get("reviewed_input_identity_sha256") if report else None)
    )
    expected_parent = expected.get("parent_receipt_identity") or (
        report.get("parent_receipt_identity") if report else None
    )
    if expected_packet is None or expected_input is None:
        info["reason"] = "worker report has no packet and reviewed-input identities"
        return None
    for key in LOG_SOURCE_KEYS:
        source = paths.get(LOG_SOURCE_KEYS[key])
        if source is None or not source.is_file():
            continue
        try:
            raw = source.read_bytes()
        except OSError:
            continue
        info["sources"].append(
            {
                "key": key,
                "path": str(source),
                "bytes": len(raw),
                "scanned_bytes": min(len(raw), PARTIAL_SCAN_LIMIT),
                "windowed": len(raw) > PARTIAL_SCAN_LIMIT,
            }
        )
        for candidate in _json_values(raw):
            if not isinstance(candidate, dict) or candidate.get("kind") != "charness.bounded_review.v1":
                continue
            if candidate.get("packet_sha256") != expected_packet:
                continue
            if candidate.get("reviewed_input_identity_sha256") != expected_input:
                continue
            if (
                expected_parent is not None
                and candidate.get("parent_receipt_identity") not in {None, expected_parent}
            ):
                continue
            validation = _bounded_result_shape(candidate)
            info.update({"status": "preserved", "reason": "matching identity-bound JSON found"})
            return candidate, source, validation
    info["reason"] = "no identity-matching bounded-review object was found in the bounded log windows"
    return None
