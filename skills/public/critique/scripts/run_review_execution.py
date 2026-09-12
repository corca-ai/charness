"""Execute the live portion of a semantic critique review."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def run_live(  # noqa: C901, PLR0915
    args: Any,
    root: Path,
    *,
    support: Any,
    packet: Any,
    invocation: Any,
    promotion: Any,
    carrier_module: Any,
    script_dir: Path,
    read_only_boundary_mode: str,
    lifecycle_semantic_input: Any,
    materialize_semantic_input: Any,
    adapter_name: Any,
) -> int:  # noqa: C901, PLR0915
    """Run a reviewer and retain every terminal carrier, including failures."""
    context: dict[str, Any] = {"attempt_id": args.attempt_id, "scope": args.scope, "lens": args.lens}
    lifecycle = None
    goal_lineage: dict[str, Any] | None = None
    run_owner: Any = None
    paths: dict[str, Path] | None = None
    run_state = "failed"
    promotion_complete = False
    artifact_key = args.artifact_key
    try:
        goal_lineage = support.load_goal_lineage(
            root,
            args.goal_lineage_file,
            reason="critique review was run without a Goal Run Work Item identity",
        )
        package = support.package_paths(script_dir)
        lifecycle, capability_lib = support.load_runtime(package)
        partial_output = support.load_module(
            package["partial_output"], "charness_run_review_partial_output"
        )
        adapter = support.resolve_adapter(root, package["resolve_adapter"])
        data = adapter.get("data")
        sections = data.get("packet_sections", []) if isinstance(data, dict) else []
        if not isinstance(sections, list) or not sections:
            name = adapter_name(root, adapter)
            remedy = (
                f"Declare at least one packet_sections entry in `{name}` "
                "and rerun; no reviewer was started."
            )
            raise support.RunReviewError(
                "adapter-no-sections",
                f"critique adapter `{name}` declares no packet_sections; "
                "run_review cannot start without semantic review input",
                details={
                    "adapter_path": name,
                    "scope_status": "adapter-no-sections",
                    "section_count": 0,
                    "usable": False,
                    "remedy": remedy,
                },
            )
        backend, timeout = support.select_backend(adapter, args.backend, dry_run=args.dry_run)
        reviewed_paths = packet.manifest_paths(support, root, args.reviewed_paths_file, args.reviewed_path)
        packet_path, packet_payload, packet_sha, input_sha, verification = packet.select_packet(
            support, root, args, artifact_key, reviewed_paths, adapter, package
        )

        durable_attempt_dir = root / promotion.DURABLE_WORKER_REPORTS / artifact_key
        if durable_attempt_dir.exists() or durable_attempt_dir.is_symlink():
            raise support.RunReviewError(
                "stale-artifact-refused",
                f"refusing to reuse durable reviewer attempt: {durable_attempt_dir}",
            )
        run_owner = support.new_run_owner(root, artifact_key)
        run_dir = run_owner.path
        paths = packet.run_paths(run_dir, packet_path)
        context["paths"] = {
            key: support.relative(root, value) for key, value in paths.items() if key != "run_dir"
        }
        semantic_input = materialize_semantic_input(root, packet_payload, paths["run_dir"])
        projected_input = lifecycle_semantic_input(semantic_input)
        context["semantic_input"] = semantic_input
        paths["schema"].write_bytes(package["schema"].read_bytes())
        schema_sha = support.sha256(paths["schema"])
        if schema_sha != support.sha256(package["schema"]):
            raise support.RunReviewError(
                "schema-drift", "materialized result schema is not byte-identical to the canonical schema"
            )
        capability = packet.default_capability(root)
        decision = capability_lib.validate_capability_envelope(
            capability, attempt_id=args.attempt_id, require_ready=True
        )
        support.write_json(paths["capability"], capability)
        capability_sha = decision.envelope_sha256
        packet.write_prompt(
            paths["prompt"], packet_payload, scope=args.scope, lens=args.lens,
            packet_sha=packet_sha, input_sha=input_sha, goal_lineage=goal_lineage,
            semantic_input=semantic_input,
        )
        boundary_mode = read_only_boundary_mode
        boundary_sha = None
        plan = {
            "kind": "charness.review_run_plan.v1",
            "attempt_id": args.attempt_id,
            "scope": args.scope,
            "lens": args.lens,
            "packet_path": support.relative(root, packet_path),
            "packet_sha256": packet_sha,
            "reviewed_input_identity_sha256": input_sha,
            "schema_sha256": schema_sha,
            "capability_envelope_sha256": capability_sha,
            "backend": backend,
            "timeout_seconds": timeout,
            "goal_lineage": goal_lineage,
            "semantic_input": semantic_input,
            "boundary_mode": boundary_mode,
            "boundary_fingerprint": boundary_sha,
        }
        support.write_json(paths["plan"], plan)
        parent_receipt = "parent-" + support.sha256(paths["plan"])[:48]
        plan["parent_receipt_identity"] = parent_receipt
        support.write_json(paths["plan"], plan)
        run_owner.update(
            attempt_id=args.attempt_id,
            plan_sha256=support.sha256(paths["plan"]),
            packet_identity=packet_sha,
            reviewed_input_identity=input_sha,
            parent_receipt_identity=parent_receipt,
        )
        context.update(
            {
                "packet_sha256": packet_sha,
                "reviewed_input_identity_sha256": input_sha,
                "parent_receipt_identity": parent_receipt,
                "backend": backend,
                "timeout_seconds": timeout,
            }
        )
        if args.dry_run:
            result = lifecycle.build_lifecycle(
                status="dry-run-ready", dry_run=True, boundary_mode=boundary_mode,
                boundary_ok=True, paths=context["paths"]
            )
            result.update(
                {
                    "ok": True,
                    "carrier_ok": True,
                    "packet_verification": verification,
                    "capability_envelope_sha256": capability_sha,
                    "schema_sha256": schema_sha,
                    "backend": backend,
                    "timeout_seconds": timeout,
                    "scope": args.scope,
                    "lens": args.lens,
                    "semantic_input": projected_input,
                    "goal_lineage": goal_lineage,
                }
            )
            support.write_yaml(paths["summary"], result)
            carrier_module.finalize_carrier(
                support, promotion, root, artifact_key, paths, context, result, None
            )
            promotion_complete = True
            support.emit(result)
            run_state = "succeeded"
            return 0

        if backend is None:
            raise support.RunReviewError("backend-unavailable", "no backend selected for a live run")
        command = invocation.runner_command(
            support, package, paths, root=root, backend=backend, scope=args.scope,
            attempt=args.attempt_id, packet_sha=packet_sha, input_sha=input_sha,
            parent_receipt=parent_receipt, boundary_mode=boundary_mode, boundary_sha=boundary_sha,
        )
        returncode, status, started, error = support.run_runner_held_out(
            command, root=root, stdout_path=paths["runner_stdout"],
            stderr_path=paths["runner_stderr"], timeout=timeout,
            hold_out_paths=list(args.hold_out or []),
        )
        returncode, status, started, error = support.classify_runner_output(
            paths["runner_stdout"], returncode=returncode, status=status,
            started=started, error=error,
        )
        report = promotion.load_and_promote_report(root, artifact_key, paths, context)
        stream_evidence = carrier_module.compare_report_stream(support, paths["runner_stdout"], paths["report"])
        result = lifecycle.build_lifecycle(
            status=status,
            report=report,
            error=error or stream_evidence["reason"],
            returncode=returncode,
            reviewer_started=started,
            boundary_mode=boundary_mode,
            boundary_ok=True,
            boundary_reason=None,
            paths=context["paths"],
            partial_outputs=(
                []
                if isinstance(report, dict) and report.get("delivery_state") == "findings-received"
                else partial_output.collect_run_logs(root, paths)
            ),
        )
        result.update(
            {
                "ok": bool(report) and status != "runner-invalid" and stream_evidence["consistent"],
                "carrier_ok": bool(report) and status != "runner-invalid" and stream_evidence["consistent"],
                "packet_verification": verification,
                "capability_envelope_sha256": capability_sha,
                "schema_sha256": schema_sha,
                "backend": backend,
                "timeout_seconds": timeout,
                "scope": args.scope,
                "lens": args.lens,
                "parent_receipt_identity": parent_receipt,
                "semantic_input": projected_input,
                "runner_output": {"status": status, "returncode": returncode},
                "runner_stream": stream_evidence,
                "boundary_readback": {"mode": boundary_mode, "required": False},
                "goal_lineage": goal_lineage,
            }
        )
        if not stream_evidence["consistent"]:
            result["approval_eligible"] = False
            result["next_move"] = "inspect runner stdout versus the canonical report; do not approve this run"
        identity = promotion.identity_binding(
            report,
            {
                "packet_sha256": packet_sha,
                "reviewed_input_identity_sha256": input_sha,
                "parent_receipt_identity": parent_receipt,
            },
        )
        result["identity_check"] = identity
        if not identity["matches"]:
            result["approval_eligible"] = False
            result["carrier_ok"] = False
            result["ok"] = False
            result["next_move"] = "rebind the worker report to this run plan; do not approve this run"
        run_state = carrier_module.owner_terminal_state(status, result)
        support.write_yaml(paths["summary"], result)
        carrier_module.finalize_carrier(
            support, promotion, root, artifact_key, paths, context, result, report
        )
        promotion_complete = True
        support.emit(result)
        return 0 if result["approval_eligible"] else 1
    except support.RunReviewError as exc:
        result = carrier_module.failure_carrier(
            packet, lifecycle, scope=args.scope, lens=args.lens, error=str(exc),
            code=exc.code, details=exc.details,
        )
        if paths is not None:
            try:
                report_path = paths.get("report")
                report = support.load_mapping(report_path) if report_path is not None else None
                carrier_module.finalize_carrier(
                    support, promotion, root, artifact_key, paths, context, result, report
                )
                promotion_complete = True
            except (OSError, support.RunReviewError, ValueError):
                result.setdefault("durable_promotion", {})["status"] = "failed"
        support.emit(result)
        return 2
    except Exception as exc:
        result = carrier_module.failure_carrier(
            packet, lifecycle, scope=args.scope, lens=args.lens, error=str(exc),
            code="runner-invalid", details={},
        )
        if paths is not None:
            try:
                report_path = paths.get("report")
                report = support.load_mapping(report_path) if report_path is not None else None
                carrier_module.finalize_carrier(
                    support, promotion, root, artifact_key, paths, context, result, report
                )
                promotion_complete = True
            except (OSError, support.RunReviewError, ValueError):
                result.setdefault("durable_promotion", {})["status"] = "failed"
        support.emit(result)
        return 2
    finally:
        if run_owner is not None:
            if not promotion_complete:
                # Do not treat a metadata-only promotion as complete.  The
                # lifecycle carrier may still be missing or unreadable, so a
                # retry needs the original scratch bytes.  The exception
                # handlers above already attempted a full finalization; a
                # second metadata-only attempt here used to make the owner
                # look promoted and then delete the only recoverable source.
                retained_hashes = {}
                retained_path_keys = {
                    "receipt": "receipt",
                    # The on-disk carrier names are ledger/output, while the
                    # recovery receipt exposes their semantic roles as
                    # delivery/result.  Keep the receipt contract stable so a
                    # retained scratch run can be resumed without guessing
                    # which alias was used by the producer.
                    "delivery": "ledger",
                    "result": "output",
                    "report": "report",
                    "summary": "summary",
                }
                for label, path_key in retained_path_keys.items():
                    path = (paths or {}).get(path_key)
                    if path is not None and path.is_file():
                        retained_hashes[f"{label}_sha256"] = support.sha256(path)
                run_owner.retain_with(
                    recovery_command=(
                        "python3 skills/public/critique/scripts/run_review.py "
                        f"--repo-root . --resume-retained-attempt {artifact_key}"
                    ),
                    packet_identity=context.get("packet_sha256"),
                    reviewed_input_identity=context.get("reviewed_input_identity_sha256"),
                    parent_receipt_identity=context.get("parent_receipt_identity"),
                    attempt_id=args.attempt_id,
                    plan_sha256=(
                        support.sha256(paths["plan"])
                        if paths is not None and paths.get("plan", Path()).is_file()
                        else None
                    ),
                    **retained_hashes,
                    recovery_reason="durable reviewer promotion failed; retained scratch is retryable",
                )
            run_owner.close(state=run_state)
