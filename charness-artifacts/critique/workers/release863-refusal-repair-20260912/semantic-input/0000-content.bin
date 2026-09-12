"""Validate and promote a retained critique reviewer attempt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def resume_retained_attempt(
    root: Path,
    attempt: str,
    *,
    support: Any,
    packet: Any,
    promotion: Any,
    script_dir: Path,
) -> int:
    """Retry durable promotion for an identity-bound retained reviewer run."""
    if not attempt or attempt.startswith(".") or "/" in attempt or "\\" in attempt:
        raise support.RunReviewError("attempt-invalid", "retained attempt id must be a plain run identity")
    run_id = "review-" + hashlib.sha256(attempt.encode("utf-8")).hexdigest()[:32]
    owner = support.owned_scratch(
        root,
        "critique-review",
        run_id=run_id,
        runtime_root_path=root / ".charness",
    )
    owner.reopen_existing()
    try:
        package = support.package_paths(script_dir)
        carrier_validation = support.load_module(
            package["carrier_validation"], "charness_reviewer_worker_carrier_support_recovery"
        )
        identity_verification = support.load_module(
            package["identity_verification"], "charness_reviewed_input_verification_recovery"
        )
        carrier_module = support.load_module(
            script_dir / "run_review_carrier.py", "charness_run_review_carrier_recovery"
        )
        retained_inputs = support.load_module(
            script_dir / "run_review_recovery_inputs.py",
            "charness_run_review_recovery_inputs",
        )
        lifecycle = support.load_module(package["lifecycle"], "charness_run_review_lifecycle_recovery")
        run_dir = owner.path
        plan_path = run_dir / "run-plan.json"
        plan = support.load_mapping(plan_path)
        if not isinstance(plan, dict):
            raise support.RunReviewError("recovery-invalid", "retained run plan is not a mapping")
        packet_value = plan.get("packet_path")
        if not isinstance(packet_value, str):
            raise support.RunReviewError("recovery-invalid", "retained run plan has no packet_path")
        packet_path = support.repo_path(root, packet_value, label="retained packet", require_file=True)
        paths = packet.run_paths(run_dir, packet_path)
        report = support.load_mapping(paths["report"]) if paths["report"].is_file() else None
        recovery_validation = retained_inputs.validate_retained_inputs(
            root,
            plan,
            packet_path,
            paths,
            attempt=attempt,
            owner_receipt=owner.receipt_path,
            package=package,
            support=support,
            packet_module=packet,
            identity_verification=identity_verification,
        )
        expected = {
            "attempt_id": attempt,
            "packet_sha256": plan.get("packet_sha256"),
            "reviewed_input_identity_sha256": plan.get("reviewed_input_identity_sha256"),
            "parent_receipt_identity": plan.get("parent_receipt_identity"),
        }
        final_carrier = None
        if recovery_validation["ok"] and not isinstance(report, dict):
            recovery_validation = {
                **recovery_validation,
                "status": "invalid",
                "ok": False,
                "reason": "retained worker report is missing or unreadable",
            }
        if recovery_validation["ok"] and isinstance(report, dict):
            try:
                carrier_validation.validate_delivered_worker_report(
                    repo_root=root,
                    report=report,
                    expected_attempt_id=attempt,
                    expected_paths={
                        "receipt": paths["receipt"],
                        "delivery": paths["ledger"],
                        "result": paths["output"],
                    },
                )
            except (ValueError, OSError, KeyError) as exc:
                recovery_validation = {
                    **recovery_validation,
                    "status": "invalid",
                    "ok": False,
                    "reason": f"delivered worker report validation failed: {exc}",
                    "report_validation": {"status": "invalid", "reason": str(exc)},
                }
            else:
                actual_identity = promotion.identity_binding(report, expected)
                actual_stream = carrier_module.compare_report_stream(support, paths["runner_stdout"], paths["report"])
                final_carrier = lifecycle.build_lifecycle(
                    status="runner-completed",
                    report=report,
                    returncode=0,
                    reviewer_started=True,
                    boundary_mode=report.get("boundary_mode"),
                    boundary_ok=True,
                    paths={
                        key: support.relative(root, value)
                        for key, value in paths.items()
                        if key != "run_dir"
                    },
                )
                final_carrier.update(
                    {
                        "ok": actual_identity.get("matches") is True and actual_stream.get("consistent") is True,
                        "carrier_ok": actual_identity.get("matches") is True and actual_stream.get("consistent") is True,
                        "packet_verification": {
                            "status": "current",
                            "packet_sha256": expected.get("packet_sha256"),
                            "identity_sha256": expected.get("reviewed_input_identity_sha256"),
                        },
                        "identity_check": actual_identity,
                        "runner_stream": actual_stream,
                    }
                )
                if actual_identity.get("matches") is not True or actual_stream.get("consistent") is not True:
                    recovery_validation = {
                        **recovery_validation,
                        "status": "invalid",
                        "ok": False,
                        "reason": "retained report identity or runner stream does not match the requested attempt",
                        "report_validation": {
                            "status": "invalid",
                            "identity": actual_identity,
                            "runner_stream": actual_stream,
                        },
                    }
                approval, binding = promotion.approval_for(
                    report,
                    expected_identities=expected,
                    final_carrier=final_carrier,
                )
                final_carrier["identity_check"] = binding
                final_carrier["approval_eligible"] = approval
        if not recovery_validation.get("ok"):
            owner.close(state="failed")
            support.emit(
                {
                    "schema_version": "charness.reviewer_recovery.v1",
                    "status": "refused",
                    "attempt_id": attempt,
                    "approval_eligible": False,
                    "recovery_validation": recovery_validation,
                    "retained": True,
                    "paths": {
                        key: support.relative(root, value)
                        for key, value in paths.items()
                        if key != "run_dir"
                    },
                }
            )
            return 1
        context = {
            "packet_sha256": expected["packet_sha256"],
            "reviewed_input_identity_sha256": expected["reviewed_input_identity_sha256"],
            "parent_receipt_identity": expected["parent_receipt_identity"],
            "paths": {
                key: support.relative(root, value)
                for key, value in paths.items()
                if key != "run_dir"
            },
        }
        carrier_module.finalize_carrier(
            support,
            promotion,
            root,
            attempt,
            paths,
            context,
            final_carrier,
            report,
            recovery_validation,
        )
        promoted_chain = retained_inputs.validate_promoted_chain(
            root,
            context["paths"],
            final_carrier,
            expected,
            support=support,
            carrier_validation=carrier_validation,
            promotion=promotion,
        )
        if not promoted_chain.get("ok"):
            owner.close(state="failed")
            support.emit(
                {
                    "schema_version": "charness.reviewer_recovery.v1",
                    "status": "refused",
                    "attempt_id": attempt,
                    "approval_eligible": False,
                    "recovery_validation": {
                        **recovery_validation,
                        "status": "invalid",
                        "ok": False,
                        "reason": promoted_chain.get("reason"),
                        "promoted_chain": promoted_chain,
                    },
                    "retained": True,
                    "paths": context["paths"],
                }
            )
            return 1
        recovery_validation["promoted_chain"] = promoted_chain
        manifest_path = root / promoted_chain["attempt_manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        promoted = dict(context["paths"])
        promoted["attempt-manifest.json"] = promoted_chain["attempt_manifest"]
        owner.close(state="succeeded", remove_retained=True)
        support.emit(
            {
                "schema_version": "charness.reviewer_recovery.v1",
                "status": "recovered",
                "attempt_id": attempt,
                "approval_eligible": manifest.get("approval_eligible") is True,
                "identity_binding": manifest.get("identity_binding"),
                "recovery_validation": recovery_validation,
                "paths": promoted,
            }
        )
        return 0 if manifest.get("approval_eligible") is True else 1
    except BaseException:
        owner.close(state="failed")
        raise
