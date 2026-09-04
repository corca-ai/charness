#!/usr/bin/env python3
"""Run one file-backed critique review from semantic inputs."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
READ_ONLY_BOUNDARY_MODE = "read-only-worker"


def _load_support() -> Any:
    path = SCRIPT_DIR / "run_review_support.py"
    spec = importlib.util.spec_from_file_location("charness_run_review_support", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load semantic review support: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUPPORT = _load_support()
PACKET = SUPPORT.load_module(SCRIPT_DIR / "run_review_packet.py", "charness_run_review_packet")
INVOCATION = SUPPORT.load_module(
    SCRIPT_DIR / "run_review_invocation.py", "charness_run_review_invocation"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--packet-file", help="Existing repo-relative critique packet JSON")
    parser.add_argument("--prepared-for", default="working tree", help="Semantic label for generated packet input")
    parser.add_argument("--reviewed-path", action="append", default=None, help="Repo-relative path to include")
    parser.add_argument("--reviewed-paths-file", help="Repo-relative newline-delimited reviewed-path manifest")
    parser.add_argument("--commit", help="Generate packet for one commit")
    parser.add_argument("--range", dest="changed_range", help="Generate packet for an endpoint diff range")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--lens", required=True)
    parser.add_argument("--attempt-id")
    parser.add_argument("--backend", choices=("codex_exec", "claude_p"))
    parser.add_argument("--goal-lineage-file", help="Repo-relative full Goal Run evidence-lineage JSON")
    parser.add_argument("--dry-run", action="store_true", help="Derive and validate the run without starting a reviewer")
    parser.add_argument(
        "--hold-out",
        action="append",
        default=None,
        help="Repo-relative path to hide from the reviewer tree for this run (repeatable)",
    )
    return parser


def _failure_carrier(
    lifecycle: Any,
    *,
    scope: str,
    lens: str,
    error: str,
    code: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    if lifecycle is None:
        return {
            "schema_version": "charness.reviewer_lifecycle.v1",
            "status": "runner-invalid",
            "execution_state": "preflight-blocked",
            "lifecycle_state": "preflight-blocked",
            "reviewer_started": False,
            "delivery_state": "none",
            "verdict_state": "not-applicable",
            "review_verdict": None,
            "classification": None,
            "approval_eligible": False,
            "output": {"state": "none", "approval_eligible": False, "artifacts": []},
            "output_state": "none",
            "failure_identity": None,
            "next_move": "repair the named preflight boundary and rerun; reviewer did not start",
            "runner_returncode": None,
            "runner_status": "runner-invalid",
            "boundary_ok": None,
            "boundary_reason": None,
            "paths": {},
        }
    carrier = lifecycle.build_lifecycle(
        status="runner-invalid", error=error, reviewer_started=False, paths={}
    )
    carrier.update({
        "ok": False,
        "carrier_ok": False,
        "reason_code": code,
        "error": error,
        "details": details,
        "scope": scope,
        "lens": lens,
    })
    for field in PACKET.REFUSAL_DETAIL_FIELDS:
        if field in details:
            carrier[field] = details[field]
    return carrier


def _adapter_name(root: Path, adapter: dict[str, Any]) -> str:
    value = adapter.get("path")
    if isinstance(value, str) and value:
        try:
            return SUPPORT.relative(root, Path(value))
        except (ValueError, OSError):
            return value
    return ".agents/critique-adapter.yaml"


def _materialize_semantic_input(root: Path, packet: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    try:
        return PACKET.materialize_semantic_input(root, packet, run_dir)
    except PACKET.SemanticInputError as exc:
        raise SUPPORT.RunReviewError(exc.code, str(exc), details=exc.details) from exc


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.repo_root.expanduser().resolve()
    attempt = SUPPORT.attempt_id(args.attempt_id)
    if args.packet_file is not None and any(
        value is not None for value in (args.reviewed_paths_file, args.commit, args.changed_range)
    ):
        _parser().error("--packet-file cannot be combined with packet-generation inputs")
    if args.commit is not None and args.changed_range is not None:
        _parser().error("--commit and --range are mutually exclusive")

    context: dict[str, Any] = {"attempt_id": attempt, "scope": args.scope, "lens": args.lens}
    lifecycle = None
    goal_lineage: dict[str, Any] | None = None
    try:
        goal_lineage = SUPPORT.load_goal_lineage(
            root,
            args.goal_lineage_file,
            reason="critique review was run without a Goal Run Work Item identity",
        )
        package = SUPPORT.package_paths(SCRIPT_DIR)
        lifecycle, capability_lib = SUPPORT.load_runtime(package)
        partial_output = SUPPORT.load_module(
            package["partial_output"], "charness_run_review_partial_output"
        )
        adapter = SUPPORT.resolve_adapter(root, package["resolve_adapter"])
        data = adapter.get("data")
        sections = data.get("packet_sections", []) if isinstance(data, dict) else []
        if not isinstance(sections, list) or not sections:
            adapter_name = _adapter_name(root, adapter)
            remedy = (
                f"Declare at least one packet_sections entry in `{adapter_name}` "
                "and rerun; no reviewer was started."
            )
            raise SUPPORT.RunReviewError(
                "adapter-no-sections",
                f"critique adapter `{adapter_name}` declares no packet_sections; "
                "run_review cannot start without semantic review input",
                details={
                    "adapter_path": adapter_name,
                    "scope_status": "adapter-no-sections",
                    "section_count": 0,
                    "usable": False,
                    "remedy": remedy,
                },
            )
        backend, timeout = SUPPORT.select_backend(adapter, args.backend, dry_run=args.dry_run)
        reviewed_paths = PACKET.manifest_paths(SUPPORT, root, args.reviewed_paths_file, args.reviewed_path)
        if args.packet_file is not None:
            packet, packet_payload, packet_sha, input_sha, verification = PACKET.read_packet(
                SUPPORT, root, args.packet_file, package["verify_packet"]
            )
        else:
            packet = PACKET.prepare_packet(
                SUPPORT, root, args, attempt, reviewed_paths, adapter, package["prepare"]
            )
            packet, packet_payload, packet_sha, input_sha, verification = PACKET.read_packet(
                SUPPORT, root, SUPPORT.relative(root, packet), package["verify_packet"]
            )
        identity = packet_payload.get("reviewed_input_identity")
        packet_paths = identity.get("reviewed_paths", []) if isinstance(identity, dict) else []
        if reviewed_paths and sorted(reviewed_paths) != sorted(packet_paths):
            raise SUPPORT.RunReviewError("input-mismatch", "explicit reviewed paths do not match packet identity")

        run_dir = SUPPORT.new_run_dir(root, attempt)
        paths = PACKET.run_paths(run_dir, packet)
        context["paths"] = {
            key: SUPPORT.relative(root, value) for key, value in paths.items() if key != "run_dir"
        }
        semantic_input = _materialize_semantic_input(root, packet_payload, paths["run_dir"])
        context["semantic_input"] = semantic_input
        paths["schema"].write_bytes(package["schema"].read_bytes())
        schema_sha = SUPPORT.sha256(paths["schema"])
        if schema_sha != SUPPORT.sha256(package["schema"]):
            raise SUPPORT.RunReviewError("schema-drift", "materialized result schema is not byte-identical to the canonical schema")
        capability = PACKET.default_capability(root)
        decision = capability_lib.validate_capability_envelope(
            capability, attempt_id=attempt, require_ready=True
        )
        SUPPORT.write_json(paths["capability"], capability)
        capability_sha = decision.envelope_sha256
        PACKET.write_prompt(
            paths["prompt"], packet_payload, scope=args.scope, lens=args.lens,
            packet_sha=packet_sha, input_sha=input_sha, goal_lineage=goal_lineage,
            semantic_input=semantic_input,
        )
        boundary_mode = READ_ONLY_BOUNDARY_MODE
        boundary_sha = None
        plan = {
            "kind": "charness.review_run_plan.v1",
            "attempt_id": attempt,
            "scope": args.scope,
            "lens": args.lens,
            "packet_path": SUPPORT.relative(root, packet),
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
        SUPPORT.write_json(paths["plan"], plan)
        parent_receipt = "parent-" + SUPPORT.sha256(paths["plan"])[:48]
        context.update({
            "packet_sha256": packet_sha,
            "reviewed_input_identity_sha256": input_sha,
            "parent_receipt_identity": parent_receipt,
            "backend": backend,
            "timeout_seconds": timeout,
        })
        if args.dry_run:
            carrier = lifecycle.build_lifecycle(
                status="dry-run-ready", dry_run=True, boundary_mode=boundary_mode,
                boundary_ok=True, paths=context["paths"]
            )
            carrier.update({
                "ok": True,
                "carrier_ok": True,
                "packet_verification": verification,
                "capability_envelope_sha256": capability_sha,
                "schema_sha256": schema_sha,
                "backend": backend,
                "timeout_seconds": timeout,
                "scope": args.scope,
                "lens": args.lens,
                "semantic_input": semantic_input,
                "goal_lineage": goal_lineage,
            })
            SUPPORT.write_yaml(paths["summary"], carrier)
            SUPPORT.emit(carrier)
            return 0

        if backend is None:
            raise SUPPORT.RunReviewError("backend-unavailable", "no backend selected for a live run")
        command = INVOCATION.runner_command(
            SUPPORT, package, paths, root=root, backend=backend, scope=args.scope, attempt=attempt,
            packet_sha=packet_sha, input_sha=input_sha, parent_receipt=parent_receipt,
            boundary_mode=boundary_mode, boundary_sha=boundary_sha,
        )
        returncode, status, started, error = SUPPORT.run_runner_held_out(
            command, root=root, stdout_path=paths["runner_stdout"],
            stderr_path=paths["runner_stderr"], timeout=timeout,
            hold_out_paths=list(args.hold_out or []),
        )
        returncode, status, started, error = SUPPORT.classify_runner_output(
            paths["runner_stdout"], returncode=returncode, status=status,
            started=started, error=error,
        )
        report = SUPPORT.load_and_promote_report(root, attempt, paths, context)
        stream_evidence = SUPPORT.compare_report_stream(paths["runner_stdout"], paths["report"])
        boundary_ok = True
        carrier = lifecycle.build_lifecycle(
            status=status,
            report=report,
            error=error or stream_evidence["reason"],
            returncode=returncode,
            reviewer_started=started,
            boundary_mode=boundary_mode,
            boundary_ok=boundary_ok,
            boundary_reason=None,
            paths=context["paths"],
            partial_outputs=(
                []
                if isinstance(report, dict) and report.get("delivery_state") == "findings-received"
                else partial_output.collect_run_logs(root, paths)
            ),
        )
        carrier.update({
            "ok": bool(report) and status != "runner-invalid" and boundary_ok and stream_evidence["consistent"],
            "carrier_ok": bool(report) and status != "runner-invalid" and stream_evidence["consistent"],
            "packet_verification": verification,
            "capability_envelope_sha256": capability_sha,
            "schema_sha256": schema_sha,
            "backend": backend,
            "timeout_seconds": timeout,
            "scope": args.scope,
            "lens": args.lens,
            "parent_receipt_identity": parent_receipt,
            "semantic_input": semantic_input,
            "runner_output": {"status": status, "returncode": returncode},
            "runner_stream": stream_evidence,
            "boundary_readback": {"mode": boundary_mode, "required": False},
            "goal_lineage": goal_lineage,
        })
        if not stream_evidence["consistent"]:
            carrier["approval_eligible"] = False
            carrier["next_move"] = "inspect runner stdout versus the canonical report; do not approve this run"
        SUPPORT.write_yaml(paths["summary"], carrier)
        SUPPORT.emit(carrier)
        return 0 if carrier["approval_eligible"] else 1
    except SUPPORT.RunReviewError as exc:
        carrier = _failure_carrier(
            lifecycle, scope=args.scope, lens=args.lens, error=str(exc),
            code=exc.code, details=exc.details,
        )
        SUPPORT.emit(carrier)
        return 2
    except Exception as exc:
        carrier = _failure_carrier(
            lifecycle, scope=args.scope, lens=args.lens, error=str(exc),
            code="runner-invalid", details={},
        )
        SUPPORT.emit(carrier)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
