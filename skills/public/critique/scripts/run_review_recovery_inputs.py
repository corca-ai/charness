"""Validate the immutable inputs of a retained critique reviewer attempt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def parent_receipt_identity(plan: dict[str, Any]) -> str:
    unsigned = dict(plan)
    unsigned.pop("parent_receipt_identity", None)
    encoded = (json.dumps(unsigned, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    return "parent-" + hashlib.sha256(encoded).hexdigest()[:48]


def non_approval_carrier(reason: str) -> dict[str, Any]:
    return {
        "approval_eligible": False,
        "identity_check": {"matches": False, "reason": reason},
        "runner_stream": {"consistent": False, "reason": reason},
    }


def validate_retained_inputs(  # noqa: C901, PLR0915
    root: Path,
    plan: dict[str, Any],
    packet: Path,
    paths: dict[str, Path],
    *,
    attempt: str,
    owner_receipt: Path,
    package: dict[str, Path],
    support: Any,
    packet_module: Any,
    identity_verification: Any,
) -> dict[str, Any]:
    """Rebind retained bytes before allowing a recovery carrier to approve."""
    checks: dict[str, Any] = {}

    def invalid(reason: str, **details: Any) -> dict[str, Any]:
        return {"status": "invalid", "ok": False, "reason": reason, "checks": checks, **details}

    if plan.get("attempt_id") != attempt:
        return invalid(
            "retained run plan attempt_id does not match the requested attempt",
            expected_attempt=attempt,
            actual_attempt=plan.get("attempt_id"),
        )
    owner = support.load_mapping(owner_receipt)
    if not isinstance(owner, dict):
        return invalid("retained owner receipt is missing or unreadable")
    checks["owner_receipt"] = {
        "attempt_id": {"expected": attempt, "actual": owner.get("attempt_id")},
        "packet_identity": {
            "expected": plan.get("packet_sha256"),
            "actual": owner.get("packet_identity"),
        },
        "reviewed_input_identity": {
            "expected": plan.get("reviewed_input_identity_sha256"),
            "actual": owner.get("reviewed_input_identity"),
        },
        "parent_receipt_identity": {
            "expected": plan.get("parent_receipt_identity"),
            "actual": owner.get("parent_receipt_identity"),
        },
    }
    if any(
        (
            owner.get("attempt_id") != attempt,
            owner.get("packet_identity") != plan.get("packet_sha256"),
            owner.get("reviewed_input_identity") != plan.get("reviewed_input_identity_sha256"),
            owner.get("parent_receipt_identity") != plan.get("parent_receipt_identity"),
        )
    ):
        return invalid("retained owner receipt does not bind the requested attempt")
    actual_plan = support.sha256(paths["plan"]) if paths["plan"].is_file() else None
    checks["plan_sha256"] = {"expected": owner.get("plan_sha256"), "actual": actual_plan}
    if not isinstance(owner.get("plan_sha256"), str) or owner.get("plan_sha256") != actual_plan:
        return invalid("retained run plan bytes do not match the owner receipt")

    retained_paths = {
        "receipt": "receipt",
        "delivery": "ledger",
        "result": "output",
        "report": "report",
        "summary": "summary",
    }
    for label, key in retained_paths.items():
        path = paths.get(key)
        actual = support.sha256(path) if path is not None and path.is_file() else None
        expected = owner.get(f"{label}_sha256")
        checks[f"{label}_sha256"] = {"expected": expected, "actual": actual}
        if not isinstance(expected, str) or actual != expected:
            return invalid(f"retained {label} bytes do not match the owner receipt")

    worker_receipt = support.load_mapping(paths["receipt"])
    if not isinstance(worker_receipt, dict):
        return invalid("retained worker receipt is missing or unreadable")
    for field, expected in (
        ("attempt_id", attempt),
        ("packet_identity", plan.get("packet_sha256")),
        ("reviewed_input_identity", plan.get("reviewed_input_identity_sha256")),
        ("parent_receipt_identity", plan.get("parent_receipt_identity")),
    ):
        if worker_receipt.get(field) != expected:
            return invalid(f"retained worker receipt {field} does not match the run plan")
    delivery = support.load_mapping(paths["ledger"])
    attempts = delivery.get("attempts") if isinstance(delivery, dict) else None
    delivery_attempt = next(
        (item for item in attempts or [] if isinstance(item, dict) and item.get("attempt_id") == attempt),
        None,
    )
    if not isinstance(delivery_attempt, dict):
        return invalid("retained delivery ledger has no requested attempt")
    for field, expected in (
        ("packet_identity", plan.get("packet_sha256")),
        ("reviewed_input_identity", plan.get("reviewed_input_identity_sha256")),
        ("parent_receipt_identity", plan.get("parent_receipt_identity")),
    ):
        if delivery_attempt.get(field) != expected:
            return invalid(f"retained delivery ledger {field} does not match the run plan")
    checks["delivery_chain"] = {
        "status": "verified",
        "attempt_id": attempt,
        "state": delivery_attempt.get("state"),
    }

    expected_packet = plan.get("packet_sha256")
    actual_packet = support.sha256(packet) if packet.is_file() else None
    checks["packet_sha256"] = {"expected": expected_packet, "actual": actual_packet}
    if not isinstance(expected_packet, str) or actual_packet != expected_packet:
        return invalid("retained packet bytes do not match the run plan")
    packet_payload = support.load_mapping(packet)
    if not isinstance(packet_payload, dict):
        return invalid("retained packet is not a mapping")
    try:
        packet_module.read_packet(
            support,
            root,
            support.relative(root, packet),
            package["verify_packet"],
        )
    except (support.RunReviewError, OSError, ValueError) as exc:
        return invalid(f"canonical retained packet verification failed: {exc}")
    packet_identity = packet_payload.get("reviewed_input_identity")
    if not isinstance(packet_identity, dict):
        return invalid("retained packet has no reviewed input identity")
    expected_input = plan.get("reviewed_input_identity_sha256")
    actual_input = packet_identity.get("identity_sha256")
    checks["reviewed_input_identity_sha256"] = {"expected": expected_input, "actual": actual_input}
    if not isinstance(expected_input, str) or actual_input != expected_input:
        return invalid("retained packet identity does not match the run plan")
    expected_parent = plan.get("parent_receipt_identity")
    actual_parent = parent_receipt_identity(plan)
    checks["parent_receipt_identity"] = {"expected": expected_parent, "actual": actual_parent}
    if not isinstance(expected_parent, str) or actual_parent != expected_parent:
        return invalid("retained parent receipt identity does not match the run plan")

    manifest_path = paths["run_dir"] / "semantic-input" / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        return invalid("retained semantic-input manifest is missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return invalid("retained semantic-input manifest is unreadable")
    entries = manifest.get("entries") if isinstance(manifest, dict) else None
    expected_content = {
        item.get("path"): item.get("content_sha256")
        for item in packet_identity.get("reviewed_content", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if not isinstance(entries, list) or {item.get("path") for item in entries if isinstance(item, dict)} != set(expected_content):
        return invalid("retained semantic-input manifest paths do not match the packet")
    semantic_root = manifest_path.parent.resolve()
    for entry in entries:
        if not isinstance(entry, dict):
            return invalid("retained semantic-input manifest contains a malformed entry")
        value = entry.get("carrier_path")
        if not isinstance(value, str) or not isinstance(entry.get("path"), str):
            return invalid("retained semantic-input manifest entry has no carrier path")
        try:
            carrier = support.repo_path(root, value, label="retained semantic carrier", require_file=True)
            carrier.resolve().relative_to(semantic_root)
        except (support.RunReviewError, ValueError):
            return invalid("retained semantic carrier escaped its run")
        expected = expected_content.get(entry["path"])
        if entry.get("content_sha256") != expected:
            return invalid("retained semantic carrier manifest does not match the packet", path=entry["path"])
        verified, reason = identity_verification.verify_semantic_carrier_entry(
            packet_identity, entry, carrier.read_bytes()
        )
        if not verified:
            return invalid(
                "retained semantic carrier bytes do not match the packet",
                path=entry["path"],
                expected=expected,
                reason=reason,
            )
    checks["semantic_input"] = {"status": "verified", "entries": len(entries)}
    return {"status": "verified", "ok": True, "checks": checks}


def validate_promoted_chain(
    root: Path,
    paths: dict[str, str],
    final_carrier: dict[str, Any],
    expected: dict[str, Any],
    *,
    support: Any,
    carrier_validation: Any,
    promotion: Any,
) -> dict[str, Any]:
    """Reopen every durable carrier before recovery removes retained bytes."""
    required = {"report", "receipt", "ledger", "output", "summary"}
    if not required.issubset(paths):
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted chain did not expose every durable carrier",
        }
    durable = {
        key: support.repo_path(root, paths[key], label=f"promoted {key}", require_file=True)
        for key in required
    }
    report = support.load_mapping(durable["report"])
    try:
        carrier_validation.validate_delivered_worker_report(
            repo_root=root,
            report=report,
            expected_attempt_id=expected["attempt_id"],
            expected_paths={
                "receipt": durable["receipt"],
                "delivery": durable["ledger"],
                "result": durable["output"],
            },
        )
    except (ValueError, OSError, KeyError) as exc:
        return {
            "status": "invalid",
            "ok": False,
            "reason": f"promoted worker chain validation failed: {exc}",
        }
    binding = promotion.identity_binding(report, expected)
    lifecycle = support.load_mapping(durable["summary"])
    manifest_path = durable["summary"].with_name("attempt-manifest.json")
    manifest = support.load_mapping(manifest_path)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    integrity = manifest.get("file_integrity") if isinstance(manifest, dict) else None
    if not isinstance(files, dict) or not isinstance(integrity, dict):
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted attempt manifest has no complete file-integrity map",
        }
    if set(files) != set(integrity):
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted attempt manifest file-integrity keys do not match its files",
        }
    for name, relative in files.items():
        descriptor = integrity.get(name)
        if not isinstance(relative, str) or not isinstance(descriptor, dict):
            return {
                "status": "invalid",
                "ok": False,
                "reason": f"promoted file-integrity descriptor is malformed for {name}",
            }
        try:
            file_path = support.repo_path(
                root, relative, label=f"promoted file {name}", require_file=True
            )
        except (support.RunReviewError, OSError, ValueError) as exc:
            return {
                "status": "invalid",
                "ok": False,
                "reason": f"promoted file-integrity path is invalid for {name}: {exc}",
            }
        if (
            descriptor.get("path") != relative
            or descriptor.get("bytes") != file_path.stat().st_size
            or descriptor.get("sha256") != support.sha256(file_path)
        ):
            return {
                "status": "invalid",
                "ok": False,
                "reason": f"promoted file-integrity check failed for {name}",
            }
    if lifecycle != final_carrier:
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted lifecycle carrier does not match the reconstructed final carrier",
        }
    if binding.get("matches") is not True:
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted worker report identity does not match the requested attempt",
            "identity_binding": binding,
        }
    expected_approval = final_carrier.get("approval_eligible") is True
    if manifest.get("approval_eligible") is not expected_approval:
        return {
            "status": "invalid",
            "ok": False,
            "reason": "promoted attempt manifest disagrees with the final lifecycle carrier",
        }
    return {
        "status": "verified",
        "ok": True,
        "durable_paths": {key: support.relative(root, value) for key, value in durable.items()},
        "attempt_manifest": support.relative(root, manifest_path),
        "identity_binding": binding,
        "file_integrity": {"status": "verified", "files": len(files)},
    }
