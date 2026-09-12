"""Identity binding rules for reviewer approval and durable reuse."""

from __future__ import annotations

from typing import Any


def identity_binding(
    report: dict[str, Any] | None, expected: dict[str, Any] | None
) -> dict[str, Any]:
    """Compare worker provenance with the current run plan before approval."""
    required = {
        "packet_identity": "packet_sha256",
        "reviewed_input_identity": "reviewed_input_identity_sha256",
        "parent_receipt_identity": "parent_receipt_identity",
    }
    if expected is not None and expected.get("attempt_id") is not None:
        required["attempt_id"] = "attempt_id"
    checks: dict[str, dict[str, Any]] = {}
    if report is None:
        return {"status": "unavailable", "matches": False, "checks": checks}
    if expected is None:
        return {
            "status": "unbound",
            "matches": False,
            "checks": checks,
            "reason": "promotion was not given the current run-plan identities",
        }
    for report_key, expected_key in required.items():
        expected_value = expected.get(expected_key)
        actual_value = report.get(report_key)
        matches = expected_value is not None and actual_value == expected_value
        checks[report_key] = {
            "expected": expected_value,
            "actual": actual_value,
            "matches": matches,
        }
        provenance = report.get("provenance")
        if isinstance(provenance, dict) and expected_value is not None:
            provenance_value = provenance.get(report_key)
            if provenance_value is not None:
                checks[report_key]["provenance"] = provenance_value
                checks[report_key]["matches"] = matches and provenance_value == expected_value
    matches = bool(checks) and all(item["matches"] for item in checks.values())
    return {
        "status": "matched" if matches else "mismatch",
        "matches": matches,
        "checks": checks,
        "reason": None if matches else "worker provenance does not match the current run plan",
    }


def approval_for(
    report: dict[str, Any] | None,
    *,
    expected_identities: dict[str, Any] | None,
    final_carrier: dict[str, Any] | None = None,
) -> tuple[bool, dict[str, Any]]:
    binding = identity_binding(report, expected_identities)
    approval = bool(
        report
        and report.get("schema_version") == "charness.reviewer_worker_report.v1"
        and report.get("delivery_state") == "findings-received"
        and report.get("review_verdict") == "pass"
        and report.get("approval_eligible") is True
        and binding["matches"]
    )
    # A worker report is only one input to approval.  The canonical lifecycle
    # carrier must also have reached terminal findings delivery and must have
    # been written/read back with matching stream and identity evidence.  In
    # particular, an early metadata promotion without a final carrier is
    # diagnostic-retryable, never approval-eligible.
    if final_carrier is None:
        approval = False
        binding = {
            **binding,
            "approval": {
                "status": "incomplete",
                "matches": False,
                "reason": "final lifecycle carrier was not supplied",
            },
        }
    else:
        carrier_identity = final_carrier.get("identity_check")
        stream = final_carrier.get("runner_stream")
        output = final_carrier.get("output")
        lifecycle_ok = (
            final_carrier.get("schema_version") == "charness.reviewer_lifecycle.v1"
            and final_carrier.get("execution_state") == "terminal"
            and final_carrier.get("lifecycle_state") == "terminal"
            and final_carrier.get("delivery_state") == "findings-received"
            and final_carrier.get("verdict_state") == "pass"
            and final_carrier.get("ok") is True
            and final_carrier.get("carrier_ok") is True
            and final_carrier.get("approval_eligible") is True
            and isinstance(output, dict)
            and output.get("state") == "terminal"
            and output.get("approval_eligible") is True
            and isinstance(carrier_identity, dict)
            and carrier_identity.get("matches") is True
            and isinstance(stream, dict)
            and stream.get("consistent") is True
        )
        approval = approval and lifecycle_ok
        binding = {
            **binding,
            "approval": {
                "status": "matched" if lifecycle_ok else "mismatch",
                "matches": lifecycle_ok,
                "reason": None if lifecycle_ok else "final lifecycle carrier is not terminal approval evidence",
            },
        }
    return approval, binding
