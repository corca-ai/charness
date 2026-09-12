"""Bind reusable follow-up findings to their retained reviewer attempt."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def _retained_source(root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    lexical = root / candidate
    if lexical.is_symlink() or not lexical.is_file():
        return None
    try:
        lexical.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return lexical


def _json_objects(raw: bytes) -> list[dict[str, Any]]:
    text = raw.decode("utf-8", errors="replace")
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _end = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def _source_contains_result(source: Path, raw: dict[str, Any]) -> bool:
    """Prove the selected partial result was emitted by its retained log."""
    return any(candidate == raw for candidate in _json_objects(source.read_bytes()))


def verify_result_carrier(  # noqa: C901, PLR0915
    *,
    root: Path,
    source: Path,
    raw: dict[str, Any],
    plan: dict[str, Any],
    identity: dict[str, Any],
    load_mapping: Callable[[Path], dict[str, Any]],
    sha256: Callable[[Path], str],
    error: Callable[..., Exception],
) -> dict[str, Any]:
    """Bind reusable findings to the retained attempt that owns the packet."""
    run_dir = source.parent
    manifest_path = run_dir / "attempt-manifest.json"
    receipt_path = run_dir / "receipt.json"
    delivery_path = run_dir / "delivery.json"
    report_path = run_dir / "worker-report.yaml"
    result_path = run_dir / "result.json"
    required = (manifest_path, receipt_path, delivery_path, report_path)
    if any(not path.is_file() or path.is_symlink() for path in required):
        raise error(
            "prior-result-unbound",
            "prior result is missing the retained attempt provenance chain",
        )

    manifest = load_mapping(manifest_path)
    receipt = load_mapping(receipt_path)
    delivery = load_mapping(delivery_path)
    report = load_mapping(report_path)
    result = load_mapping(result_path) if result_path.is_file() and not result_path.is_symlink() else None
    attempt = manifest.get("attempt_id")
    if not isinstance(attempt, str) or not attempt:
        raise error("prior-result-unbound", "retained attempt manifest has no attempt_id")
    packet_sha = plan.get("packet_sha256")
    input_sha = plan.get("reviewed_input_identity_sha256")
    if not isinstance(packet_sha, str) or not isinstance(input_sha, str):
        raise error("prior-result-unbound", "retained run plan has no packet/input identities")
    if identity.get("identity_sha256") != input_sha:
        raise error("prior-result-unbound", "retained packet identity is not bound to the run plan")
    if raw.get("packet_sha256") != packet_sha or raw.get("reviewed_input_identity_sha256") != input_sha:
        raise error(
            "prior-result-unbound",
            "prior result carrier identities do not match the retained run plan",
        )

    identity_pairs = (
        ("attempt_id", attempt),
        ("packet_identity", packet_sha),
        ("reviewed_input_identity", input_sha),
    )
    for name, expected in identity_pairs:
        actuals = {
            "manifest": manifest.get(name),
            "receipt": receipt.get(name),
            "report": report.get(name),
            "result": result.get(name) if isinstance(result, dict) else None,
            "plan": plan.get(name),
        }
        if name == "attempt_id" and actuals["result"] is None:
            actuals.pop("result")
        if any(value is not None and value != expected for value in actuals.values()):
            raise error(
                "prior-result-unbound",
                f"retained prior result `{name}` identity does not match the attempt",
                details={"expected": expected, "actual": actuals},
            )

    descriptor = manifest.get("partial_result")
    partial_relative = source.relative_to(root).as_posix()
    source_digest = sha256(source)
    manifest_files = manifest.get("files")
    if not isinstance(descriptor, dict) or descriptor.get("path") != partial_relative:
        raise error(
            "prior-result-unbound",
            "prior result is not the partial-result carrier recorded by its attempt manifest",
        )
    if descriptor.get("sha256") != source_digest or descriptor.get("bytes") != source.stat().st_size:
        raise error(
            "prior-result-tampered",
            "prior result bytes do not match the retained attempt descriptor",
        )
    if not isinstance(manifest_files, dict) or manifest_files.get("partial-result.json") != partial_relative:
        raise error(
            "prior-result-unbound",
            "retained attempt manifest does not expose the supplied result carrier",
        )
    source_path = _retained_source(root, descriptor.get("source"))
    source_relative_value = descriptor.get("source")
    if source_path is None or not isinstance(source_relative_value, str):
        raise error(
            "prior-result-unbound",
            "prior result has no safe retained backend source",
        )
    backend_relative = source_path.relative_to(root).as_posix()
    if backend_relative != source_relative_value:
        raise error("prior-result-unbound", "prior backend source path is not repository-relative")
    if backend_relative not in {
        value for value in manifest_files.values() if isinstance(value, str)
    }:
        raise error(
            "prior-result-unbound",
            "prior result backend source is not exposed by the attempt manifest",
        )
    logs = manifest.get("logs")
    log_descriptor = next(
        (
            value
            for value in logs.values()
            if isinstance(value, dict) and value.get("path") == backend_relative
        ),
        None,
    ) if isinstance(logs, dict) else None
    if not isinstance(log_descriptor, dict):
        raise error("prior-result-unbound", "prior backend source has no retained log descriptor")
    retained_bytes = source_path.stat().st_size
    expected_bytes = log_descriptor.get("retained_bytes") if log_descriptor.get("truncated") else log_descriptor.get("bytes")
    if expected_bytes != retained_bytes:
        raise error("prior-result-tampered", "retained backend source byte count changed")
    if not log_descriptor.get("truncated") and log_descriptor.get("sha256") != sha256(source_path):
        raise error("prior-result-tampered", "retained backend source digest changed")
    if not _source_contains_result(source_path, raw):
        raise error(
            "prior-result-tampered",
            "partial result is not present in its retained backend source",
        )
    if isinstance(result, dict):
        if not all(result.get(key) == value for key, value in raw.items()):
            raise error(
                "prior-result-unbound",
                "partial result is not a projection of the receipt-bound result carrier",
            )
    else:
        retained_partial = receipt.get("retained_partial_output")
        if not isinstance(retained_partial, dict):
            raise error(
                "prior-result-unbound",
                "partial-only result has no receipt-bound retained descriptor",
            )
        if (
            retained_partial.get("path") != partial_relative
            or retained_partial.get("bytes") != source.stat().st_size
            or retained_partial.get("sha256") != source_digest
        ):
            raise error(
                "prior-result-tampered",
                "partial-only result does not match the receipt-bound retained descriptor",
            )
    if report.get("receipt_path") != receipt_path.relative_to(root).as_posix():
        raise error("prior-result-unbound", "prior report receipt path is not retained")
    if report.get("ledger_path") != delivery_path.relative_to(root).as_posix():
        raise error("prior-result-unbound", "prior report delivery path is not retained")
    producer = report.get("producer_binding")
    producer_output = producer.get("output_file") if isinstance(producer, dict) else None
    receipt_output = receipt.get("output_file")
    if not isinstance(producer, dict):
        raise error(
            "prior-result-unbound",
            "prior report is not bound to its result file",
            details={
                "producer_output_file": producer_output,
                "expected_output_file": result_path.relative_to(root).as_posix(),
                "result_present": isinstance(result, dict),
            },
        )
    if isinstance(result, dict):
        if producer_output != result_path.relative_to(root).as_posix() or receipt_output != result_path.relative_to(root).as_posix():
            raise error(
                "prior-result-unbound",
                "prior report is not bound to its result file",
                details={
                    "producer_output_file": producer_output,
                    "receipt_output_file": receipt_output,
                    "expected_output_file": result_path.relative_to(root).as_posix(),
                    "result_present": True,
                },
            )
    elif producer_output != receipt_output or not isinstance(producer_output, str) or Path(producer_output).name != "result.json":
        raise error(
            "prior-result-unbound",
            "partial-only report and receipt do not share the producer output binding",
            details={
                "producer_output_file": producer_output,
                "receipt_output_file": receipt_output,
                "result_present": False,
            },
        )

    result_digest = sha256(result_path) if isinstance(result, dict) else None
    if isinstance(result, dict) and (
        receipt.get("output_sha256") != result_digest
        or report.get("receipt_output_sha256") != result_digest
    ):
        raise error("prior-result-unbound", "prior result digest is not bound by receipt/report")
    attempts = delivery.get("attempts") if isinstance(delivery, dict) else None
    delivery_attempt = next(
        (item for item in attempts or [] if isinstance(item, dict) and item.get("attempt_id") == attempt),
        None,
    )
    if not isinstance(delivery_attempt, dict) or any(
        delivery_attempt.get(key) != expected
        for key, expected in (
            ("packet_identity", packet_sha),
            ("reviewed_input_identity", input_sha),
            ("parent_receipt_identity", plan.get("parent_receipt_identity")),
        )
    ):
        raise error("prior-result-unbound", "prior delivery ledger does not bind the result attempt")
    return {
        "status": "verified",
        "attempt_id": attempt,
        "partial_result_sha256": source_digest,
        "result_sha256": result_digest,
        "source_path": backend_relative,
    }
