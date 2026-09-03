#!/usr/bin/env python3
"""Execute the declarative quality gate list used by the thin runner."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from run_quality_engine_model import RunnerError, load_gate_list
from run_quality_engine_output import Ledger, add_filter_failure, consume_result
from run_quality_engine_phase import run_phase
from run_quality_engine_receipt import finish
from run_quality_engine_runtime import (
    changed_line_base_sha_available,
    close_runtime,
    compute_runner_variables,
    coverage_relevant_changes_present,
    prepare_runtime,
    provenance_contract_checker_available,
    record_runtime_batch,
    run_preamble,
    timestamp,
)
from run_quality_engine_selection import (
    explicit_labels,
    not_run_gates,
    requires_prior_phases_green,
    select_gates,
    selected_count,
)


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _guard.run_process


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--read-only", action="store_true")
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--review", action="store_true")
    parser.add_argument("--non-claim", default="")
    parser.add_argument("--receipt-json", default=None)
    parser.add_argument("--labels", default=None)
    parser.add_argument(
        "--print-docs-only-labels",
        action="store_true",
        help="print declared docs-only labels and exit",
    )
    return parser


def _options(
    args: argparse.Namespace, environment: dict[str, str]
) -> tuple[str, bool, bool, str, str]:
    mode = "read-only" if args.read_only else environment.get("CHARNESS_QUALITY_MODE", "full")
    if args.full or args.review or args.release:
        mode = "full" if not args.read_only else "read-only"
    if mode not in {"full", "read-only"}:
        raise RunnerError(f"CHARNESS_QUALITY_MODE must be 'full' or 'read-only', got {mode!r}")
    labels = (
        args.labels if args.labels is not None else environment.get("CHARNESS_QUALITY_LABELS", "")
    )
    if args.release and labels:
        raise RunnerError("--release is one indivisible lane; --labels cannot narrow it")
    if args.non_claim and args.non_claim != "release-changed-line-coverage":
        raise RunnerError(f"unsupported --non-claim label {args.non_claim}")
    if args.non_claim and not args.release:
        raise RunnerError("--non-claim=release-changed-line-coverage requires --release")
    if args.receipt_json == "":
        raise RunnerError("--receipt-json= requires a non-empty path")
    heartbeat = environment.get("CHARNESS_QUALITY_HEARTBEAT_SECONDS", "15")
    if not heartbeat.isdigit():
        raise RunnerError("CHARNESS_QUALITY_HEARTBEAT_SECONDS must be a non-negative integer")
    if args.labels is not None:
        environment["CHARNESS_QUALITY_LABELS"] = labels
    full_queue = (
        args.full
        or args.review
        or args.release
        or environment.get("CHARNESS_QUALITY_FULL_QUEUE", "0") == "1"
    )
    if args.review:
        environment["CHARNESS_QUALITY_VERBOSE"] = "1"
        environment["CHARNESS_LINK_CHECK_ONLINE"] = "1"
    release = args.release
    receipt = (
        args.receipt_json
        if args.receipt_json is not None
        else environment.get("CHARNESS_QUALITY_RECEIPT_JSON", "")
    )
    return mode, full_queue, release, labels, receipt


def _native_preflight(context, gates) -> int:
    for gate in gates:
        if not gate.native_preflight:
            continue
        result = run_process(
            [
                "python3",
                "scripts/native_gate_lib.py",
                "--repo-root",
                str(context.repo_root),
                "--probe",
                "export-safe",
            ],
            cwd=context.repo_root,
            env=context.environment,
            timeout_seconds=None,
        )
        if result.returncode != 0:
            print(f"run-quality: native gate preflight failed for {gate.label}", file=sys.stderr)
            return 1
        return 0
    return 0


def _mutation_recovery_pending(context) -> bool:
    git_dir = run_process(
        ["git", "-C", str(context.repo_root), "rev-parse", "--git-dir"],
        cwd=context.repo_root,
        env=context.environment,
        timeout_seconds=None,
    )
    git_path = Path(git_dir.stdout.strip()) if git_dir.returncode == 0 else None
    if git_path is not None and not git_path.is_absolute():
        git_path = context.repo_root / git_path
    return bool(
        (git_path is not None and (git_path / "charness-mutation-recovery").exists())
        or (context.repo_root / ".charness" / "mutation-recovery").exists()
    )


def _cached(probe):
    """Answer a predicate once; selection and the not-run pass both ask."""
    answer: list[bool] = []

    def call() -> bool:
        if not answer:
            answer.append(bool(probe()))
        return answer[0]

    return call


def _predicates(context):
    repo_root = context.repo_root
    environment = context.environment
    return {
        "coverage_relevant_changes_present": lambda: coverage_relevant_changes_present(
            context, environment.get("CHARNESS_QUALITY_LABELS", "")
        ),
        "changed_line_base_sha_available": lambda: changed_line_base_sha_available(context),
        "provenance_contract_checker_available": lambda: provenance_contract_checker_available(
            context
        ),
        "provenance_contract_checker_unavailable": lambda: not provenance_contract_checker_available(
            context
        ),
        "inventory_gitignore_scan_hygiene_unavailable": lambda: not (
            repo_root / "skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py"
        ).is_file(),
        "inventory_cli_ergonomics_unavailable": lambda: not (
            repo_root / "skills/public/quality/scripts/inventory_cli_ergonomics.py"
        ).is_file(),
        "inventory_nose_clones_unavailable": lambda: not (
            repo_root / "skills/public/quality/scripts/inventory_nose_clones.py"
        ).is_file(),
        "runtime_profile_present": lambda: bool(environment.get("CHARNESS_RUNTIME_PROFILE", "")),
        "runtime_profile_absent": lambda: not environment.get("CHARNESS_RUNTIME_PROFILE", ""),
        "release_final_base_sha_present": lambda: changed_line_base_sha_available(context),
        "release_final_base_sha_absent": lambda: not changed_line_base_sha_available(context),
    }


def _run_phases(
    gate_list, selected, context, variables, environment, ledger, heartbeat_seconds, release
):
    overall_rc = 0
    prior_phases_green = True
    for phase in gate_list.phases:
        gates = tuple(
            gate
            for gate in selected[phase.identifier]
            if prior_phases_green or not requires_prior_phases_green(gate)
        )
        if not gates:
            continue
        results, phase_rc = run_phase(
            phase,
            gates,
            context=context,
            variables=variables,
            heartbeat_seconds=heartbeat_seconds,
        )
        records = []
        for result in results:
            consume_result(
                result,
                verbose=environment.get("CHARNESS_QUALITY_VERBOSE", "0") == "1",
                failure_dir=context.failure_log_dir,
                ledger=ledger,
            )
            records.append(
                {
                    "label": result.gate.label,
                    "elapsed_ms": result.elapsed_ms,
                    "status": result.status,
                    "timestamp": timestamp(),
                }
            )
        record_runtime_batch(context, records)
        if phase.identifier == "agent-browser-hygiene" and phase_rc:
            cleanup_environment = context.environment.copy()
            cleanup_environment.pop("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS", None)
            run_process(
                [
                    "python3",
                    "scripts/evidence/agent_browser_runtime_guard.py",
                    "--repo-root",
                    str(context.repo_root),
                    "--cleanup-orphans",
                    "--execute",
                ],
                cwd=context.repo_root,
                env=cleanup_environment,
                timeout_seconds=None,
            )
        if phase_rc:
            overall_rc = phase_rc
            prior_phases_green = False
            if phase.fail_fast:
                fail_message = phase.fail_message
                if release and phase.identifier == "pytest":
                    fail_message = "release pytest failed; stopping before later release checks."
                if fail_message:
                    print(f"run-quality: {fail_message}", file=sys.stderr)
                break
    return overall_rc


def run(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    environment = os.environ.copy()
    mode, full_queue, release, labels, receipt_json = _options(args, environment)
    gate_list = load_gate_list(
        (repo_root / args.gates).resolve() if not args.gates.is_absolute() else args.gates.resolve()
    )
    if args.print_docs_only_labels:
        seen: set[str] = set()
        for gate in gate_list.gates:
            if gate.docs_only and gate.label not in seen:
                print(gate.label)
                seen.add(gate.label)
        return 0
    context = prepare_runtime(repo_root, mode=mode, labels=labels, base_environment=environment)
    started_at = time.monotonic()
    ledger = Ledger()
    try:
        if _mutation_recovery_pending(context):
            print(
                "run-quality: FAIL interrupted mutation recovery is REQUIRED; run "
                "python3 scripts/mutation/mutate_and_restore.py --repo-root . --check-recovery, "
                "then --recover",
                file=sys.stderr,
            )
            return 2
        include_release_only = (
            release or environment.get("CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY", "0") == "1"
        )
        environment["CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY"] = "1" if include_release_only else "0"
        requested_scope = labels or ("full" if full_queue else "core")
        print(
            f"run-quality: START mode={mode} release={int(include_release_only)} "
            f"requested_scope={requested_scope} outputs=isolated status=streamed",
            file=sys.stderr,
        )
        scope = dict(
            repo_root=repo_root,
            mode=mode,
            full_queue=full_queue,
            release=release,
            include_release_only=include_release_only,
            labels=labels,
            non_claim=args.non_claim,
            environment=environment,
            predicates={
                name: _cached(probe) for name, probe in _predicates(context).items()
            },
            excluded_labels=frozenset({args.non_claim}) if args.non_claim else frozenset(),
        )
        selected = select_gates(gate_list, **scope)
        not_run = not_run_gates(gate_list, selected, **scope)
        named_labels = frozenset(explicit_labels(labels))
        explicit_match_count = sum(
            gate.label in named_labels
            for gates in selected.values()
            for gate in gates
        )
        if selected_count(selected) == 0:
            print(
                "run-quality: explicit label filter matched no queued checks."
                if labels
                else "run-quality: no quality gates selected.",
                file=sys.stderr,
            )
            add_filter_failure(ledger)
            finish(
                context,
                ledger,
                started_at=started_at,
                mode=mode,
                release=release,
                full_queue=full_queue,
                non_claim=args.non_claim,
                receipt_json=receipt_json,
                labels=labels,
                overall_rc=2,
                not_run=not_run,
            )
            if selected_count(selected) == 0:
                return 2
        if _native_preflight(context, [gate for gates in selected.values() for gate in gates]):
            return 1
        if run_preamble(context, read_only=mode == "read-only"):
            return 1
        selected_probe = {gate.label for gates in selected.values() for gate in gates}
        variables = compute_runner_variables(
            context,
            gate_list,
            mode=mode,
            release=release,
            include_release_only=include_release_only,
            labels=labels,
            selected_labels=selected_probe,
        )
        heartbeat_seconds = int(environment.get("CHARNESS_QUALITY_HEARTBEAT_SECONDS", "15"))
        overall_rc = _run_phases(
            gate_list,
            selected,
            context,
            variables,
            environment,
            ledger,
            heartbeat_seconds,
            release,
        )
        if args.non_claim and release and overall_rc == 0:
            print(
                "NON-CLAIM: release-changed-line-coverage was not run by explicit release policy; "
                "no changed-line verdict exists",
                file=sys.stderr,
            )
        if labels and explicit_match_count == 0:
            print(
                "run-quality: explicit label filter matched no queued checks.",
                file=sys.stderr,
            )
            add_filter_failure(ledger)
            overall_rc = 2
        finish(
            context,
            ledger,
            started_at=started_at,
            mode=mode,
            release=release,
            full_queue=full_queue,
            non_claim=args.non_claim,
            receipt_json=receipt_json,
            labels=labels,
            overall_rc=overall_rc,
            not_run=not_run,
        )
        return overall_rc
    finally:
        close_runtime(context)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        return run(args)
    except RunnerError as exc:
        print(f"run-quality: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
