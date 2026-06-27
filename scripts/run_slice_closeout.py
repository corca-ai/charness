#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
collect_changed_paths_since_base = _scripts_surfaces_lib_module.collect_changed_paths_since_base
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
_scripts_plan_cautilus_proof_module = import_repo_module(__file__, "scripts.plan_cautilus_proof")
plan_cautilus_proof = _scripts_plan_cautilus_proof_module.plan_cautilus_proof
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
plan_risk_interrupt = _scripts_risk_interrupt_lib_module.plan_risk_interrupt
_agent_browser_probe_policy = import_repo_module(__file__, "scripts.agent_browser_probe_policy")
unsafe_agent_browser_probe_reason = _agent_browser_probe_policy.unsafe_agent_browser_probe_reason
_slice_closeout_usage_episode = import_repo_module(__file__, "scripts.slice_closeout_usage_episode")
emit_usage_episode_for_slice_closeout = _slice_closeout_usage_episode.emit_usage_episode_for_slice_closeout
_slice_closeout_command_executor = import_repo_module(__file__, "scripts.slice_closeout_command_executor")
execute_command_plan = _slice_closeout_command_executor.execute_command_plan
_slice_closeout_advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
advise_prose_pin = _slice_closeout_advisories.advise_prose_pin
advise_skill_surface_preflight = _slice_closeout_advisories.advise_skill_surface_preflight
advise_doc_surface_preflight = _slice_closeout_advisories.advise_doc_surface_preflight
advise_new_pool_module = _slice_closeout_advisories.advise_new_pool_module
advise_over_slicing = _slice_closeout_advisories.advise_over_slicing
advise_floor_addition_restraint = _slice_closeout_advisories.advise_floor_addition_restraint
_slice_closeout_commit_advisories = import_repo_module(__file__, "scripts.slice_closeout_commit_advisories")
advise_close_keyword_leakage = _slice_closeout_commit_advisories.advise_close_keyword_leakage
advise_decaying_habits = _slice_closeout_commit_advisories.advise_decaying_habits
attach_gate_runtime_advisory = _slice_closeout_advisories.attach_gate_runtime_advisory
_slice_closeout_telemetry = import_repo_module(__file__, "scripts.slice_closeout_telemetry")
emit_closeout_telemetry_for_slice = _slice_closeout_telemetry.emit_closeout_telemetry_for_slice
_scripts_check_python_lengths = import_repo_module(__file__, "scripts.check_python_lengths")
headroom_for = _scripts_check_python_lengths.headroom_for
_staged_commit_gate_plan = import_repo_module(__file__, "scripts.staged_commit_gate_plan")
run_predict_commit = _staged_commit_gate_plan.run_predict_commit
block_on_structural_sweep = _staged_commit_gate_plan.block_on_structural_sweep
structural_sweep_planned_commands = _staged_commit_gate_plan.structural_sweep_planned_commands
_slice_closeout_broad_gate = import_repo_module(__file__, "scripts.slice_closeout_broad_gate")
_rca_link_advisory = import_repo_module(__file__, "scripts.rca_link_advisory")
_mutation_coverage_producer = import_repo_module(__file__, "scripts.mutation_coverage_producer")
_slice_closeout_reporting = import_repo_module(__file__, "scripts.slice_closeout_reporting")
_slice_closeout_run_command = import_repo_module(__file__, "scripts.slice_closeout_run_command")
plan_broad_pytest_policy = _slice_closeout_broad_gate.plan_broad_pytest_policy
should_block_broad_pytest_policy = _slice_closeout_broad_gate.should_block_broad_pytest_policy
closeout_producer_or_error = _mutation_coverage_producer.closeout_producer_or_error
closeout_producer_validation_error = _mutation_coverage_producer.closeout_producer_validation_error
run_focused_closeout_coverage = _mutation_coverage_producer.run_focused_closeout_coverage
print_text = _slice_closeout_reporting.print_text
run_command = _slice_closeout_run_command.run_command


def _agent_browser_hygiene_command(repo_root: Path) -> str | None:
    guard = repo_root / "scripts" / "agent_browser_runtime_guard.py"
    if not guard.is_file():
        return None
    assert_cmd = (
        "env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS "
        "python3 scripts/agent_browser_runtime_guard.py --repo-root . --assert-no-orphans"
    )
    cleanup_cmd = (
        "env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS "
        "python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute"
    )
    return f"{assert_cmd} || {{ rc=$?; {cleanup_cmd} >/dev/null 2>&1 || true; exit \"$rc\"; }}"


def _emit_payload(payload: dict[str, object], *, as_json: bool, stderr_message: str | None = None) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
        if stderr_message is not None:
            print(stderr_message, file=sys.stderr)
    return 0 if payload["status"] not in {"blocked", "failed"} else 1


def _unsafe_command_blockers(command_plan: list[tuple[str, str]]) -> list[str]:
    blockers: list[str] = []
    for phase, command in command_plan:
        reason = unsafe_agent_browser_probe_reason(command)
        if reason is not None:
            blockers.append(f"{phase} command uses unsafe agent-browser probe `{command}`: {reason}")
    return blockers


def _unsafe_blocker_command_plan(command_plan: list[tuple[str, str]], args) -> list[tuple[str, str]]:
    command = getattr(args, "mutation_coverage_command", None)
    if getattr(args, "produce_mutation_coverage", False) and command:
        return command_plan + [("verify", command)]
    return command_plan


def _maybe_block_on_unmatched(payload: dict[str, object], *, allow_unmatched: bool, as_json: bool) -> int | None:
    if not payload["unmatched_paths"] or allow_unmatched:
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        "changed paths are not covered by the surfaces manifest; "
        "add the missing coverage or rerun with --allow-unmatched"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def _maybe_block_on_cautilus(
    repo_root: Path, payload: dict[str, object], *, as_json: bool, ack_skill_review: bool
) -> int | None:
    cautilus_plan = plan_cautilus_proof(repo_root, payload["changed_paths"])
    payload["cautilus_plan"] = cautilus_plan
    missing_required_proof = (
        cautilus_plan["required"]
        and not cautilus_plan["artifact_changed"]
        and cautilus_plan["run_mode"] != "disabled"
    )
    if not missing_required_proof:
        if cautilus_plan["skill_validation_recommendations"] and not ack_skill_review:
            payload["status"] = "blocked"
            payload["error"] = (
                "public-skill validation review is required for this slice; inspect the dogfood/scenario "
                "follow-ups in `cautilus_plan` and rerun with --ack-cautilus-skill-review after recording "
                "the decision"
            )
            return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        f"cautilus proof is required for this slice; next_action=`{cautilus_plan['next_action']}` "
        f"and `{cautilus_plan['artifact_path']}` is not refreshed yet"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def _maybe_block_on_risk_interrupt(
    repo_root: Path, payload: dict[str, object], *, as_json: bool
) -> int | None:
    risk_interrupt_plan = plan_risk_interrupt(repo_root, payload["changed_paths"])
    payload["risk_interrupt_plan"] = risk_interrupt_plan
    if risk_interrupt_plan["status"] != "blocked":
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        f"risk interrupt is blocking ordinary closeout; next_action=`{risk_interrupt_plan['next_action']}`"
    )
    return _emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def _resolve_broad_producer(args, repo_root: Path, run_command):
    """Resolve the closeout broad-pytest mutation-coverage producer (or None) from
    args. Raises ``SurfaceError`` on misuse (e.g. --produce-mutation-coverage
    without --verification-lock) so the entrypoint reports it and exits non-zero."""
    producer, error = closeout_producer_or_error(args, repo_root, run_command)
    if error is not None:
        raise SurfaceError(error)
    return producer


def _advise_staged_reversion(repo_root: Path) -> None:
    # Advisory (#258): surface a staged reversion (index != HEAD while worktree
    # == HEAD) at closeout, before the human commit. Reads git directly; the
    # blocking teeth live in the pre-commit gate (check_staged_reversion.py).
    lib = import_repo_module(__file__, "scripts.check_staged_reversion")
    findings = lib.find_staged_reversions(str(repo_root))
    if findings:
        print(
            "WARN: staged reversion of already-committed file(s) — index != HEAD "
            "while worktree == HEAD (#258); the pre-commit gate will block this "
            "commit. Affected: " + ", ".join(f.path for f in findings),
            file=sys.stderr,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument(
        "--base",
        nargs="?",
        const="auto",
        default=None,
        help=(
            "Collect changed paths from the committed merge-base(<ref>, HEAD)..HEAD range "
            "in addition to the working-tree diff, so a post-commit closeout covers the "
            "bundle without a manual --paths list. Bare --base auto-detects origin/main — "
            "the same range anchor the changed-line mutation gate uses. Mutually exclusive "
            "with --paths; without --base the working-tree default is unchanged. Note: "
            "--produce-mutation-coverage always stamps its freshness fingerprint over the "
            "gate's origin/main anchor, even when an explicit non-origin/main ref is passed."
        ),
    )
    parser.add_argument("--plan-only", action="store_true", help="Print obligations without executing commands.")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--skip-broad-pytest", action="store_true", help="Run deterministic checks but skip broad pytest for pre-lock rehearsal.")
    parser.add_argument("--verification-lock", action="store_true", help="Acknowledge that the mutation set is locked before broad pytest runs.")
    parser.add_argument(
        "--refresh-broad-pytest-proof",
        action="store_true",
        help="Rerun broad pytest even when a cached verification-lock proof exists or was invalidated.",
    )
    parser.add_argument(
        "--produce-mutation-coverage",
        action="store_true",
        help=(
            "Emit reports/mutation/test-coverage.json plus a freshness fingerprint "
            "marker for the pre-push changed-line gate. By default this instruments "
            "the verification-lock broad pytest. With --mutation-coverage-command, "
            "the broad pytest proof stays on the normal closeout/cache path and the "
            "explicit command is instrumented separately. Requires --verification-lock."
        ),
    )
    parser.add_argument(
        "--mutation-coverage-command",
        help=(
            "Explicit pytest command to instrument for the changed-line mutation "
            "coverage producer, e.g. a focused test file or nodeid set. Requires "
            "--produce-mutation-coverage and --verification-lock."
        ),
    )
    parser.add_argument(
        "--mutation-coverage-extra-pytest-target",
        action="append",
        default=[],
        help=(
            "Additional pytest path or nodeid appended to the broad coverage producer "
            "without shell-chaining commands. Requires --produce-mutation-coverage and "
            "cannot be combined with --mutation-coverage-command."
        ),
    )
    parser.add_argument(
        "--ack-cautilus-skill-review",
        action="store_true",
        help=(
            "Acknowledge that public-skill dogfood/scenario review follow-ups from the Cautilus planner "
            "were inspected and the scenario-registry decision was recorded."
        ),
    )
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Proceed even when changed files are not covered by the surfaces manifest.",
    )
    parser.add_argument(
        "--predict-commit",
        action="store_true",
        help="Run the same staged-path pre-commit command plan consumed by .githooks/pre-commit.",
    )
    return parser

def _resolve_changed_paths(repo_root: Path, args) -> list[str]:
    """--paths stays the explicit override; --base adds the committed
    merge-base(<ref>, HEAD)..HEAD range to the working-tree diff so a
    post-commit closeout does not no-op; the bare working-tree default is
    unchanged."""
    if args.base is not None and args.paths:
        raise SurfaceError("--base and --paths are mutually exclusive; --base derives the committed range itself")
    if args.paths:
        return args.paths
    if args.base is not None:
        return collect_changed_paths_since_base(repo_root, args.base)
    return collect_changed_paths(repo_root)


def _closeout_changed_paths_collector(
    initial_changed_paths: list[str],
):
    """Return a live proof-scope collector for broad pytest cache records.

    The closeout payload may be wider than the current worktree when `--base`
    covers already-committed slice changes. Keep those payload paths in the
    fingerprint while still adding any sync-generated worktree changes that
    appear during command execution.
    """

    def _collect(repo_root: Path) -> list[str]:
        return sorted(dict.fromkeys([*initial_changed_paths, *collect_changed_paths(repo_root)]))

    return _collect


def _planned_commands(
    repo_root: Path,
    changed_paths: list[str],
    command_plan: list[tuple[str, str]],
    args,
) -> list[dict[str, object]]:
    planned = structural_sweep_planned_commands(repo_root, changed_paths)
    planned += [{"phase": phase, "command": command} for phase, command in command_plan]
    if args.produce_mutation_coverage and args.mutation_coverage_command:
        planned.append(
            {
                "phase": "verify",
                "command": args.mutation_coverage_command,
                "coverage_producer": True,
            }
        )
    extra_targets = list(getattr(args, "mutation_coverage_extra_pytest_target", []) or [])
    if args.produce_mutation_coverage and extra_targets:
        planned.append(
            {
                "phase": "verify",
                "coverage_producer": True,
                "extra_pytest_targets": extra_targets,
            }
        )
    return planned


def _run_preexecution_blocks(repo_root: Path, payload: dict[str, object], args) -> int | None:
    """Fail-fast pre-execution gate chain; returns an exit code on the first block.
    #332: the cheap structural sweep runs FIRST (before surface-match / cautilus /
    risk interrupt / broad pytest), then advisories, unmatched, cautilus, risk.
    """
    blocked = block_on_structural_sweep(
        repo_root,
        payload,
        as_json=args.json,
        plan_only=args.plan_only,
        run_command=run_command,
        emit_payload=_emit_payload,
    )
    if blocked is not None:
        return blocked

    producer_error = closeout_producer_validation_error(args)
    if producer_error:
        payload["status"] = "blocked"
        payload["error"] = producer_error
        return _emit_payload(payload, as_json=args.json, stderr_message=producer_error)

    advise_prose_pin(repo_root, payload["changed_paths"])
    advise_skill_surface_preflight(repo_root, payload["changed_paths"])
    advise_doc_surface_preflight(repo_root, payload["changed_paths"])
    advise_new_pool_module(repo_root, payload["changed_paths"])
    advise_over_slicing(repo_root)
    advise_floor_addition_restraint(repo_root, payload["changed_paths"])
    advise_close_keyword_leakage(repo_root)
    advise_decaying_habits(repo_root, payload["changed_paths"])

    blocked = _maybe_block_on_unmatched(payload, allow_unmatched=args.allow_unmatched, as_json=args.json)
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_cautilus(
        repo_root, payload, as_json=args.json, ack_skill_review=args.ack_cautilus_skill_review
    )
    if blocked is not None:
        return blocked

    return _maybe_block_on_risk_interrupt(repo_root, payload, as_json=args.json)


def _attach_closeout_telemetry(repo_root: Path, payload: dict[str, object]) -> None:
    """Append the objective operational-waste record for this run (spec
    achieve-efficiency-improvements, E1). Reads the final ``status`` already on the
    payload, so callers must set it first. Never raises (the emitter degrades
    silently); attaches its status dict for visibility."""
    payload["closeout_telemetry"] = emit_closeout_telemetry_for_slice(repo_root, payload)


def main() -> int:
    args = _build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    if args.predict_commit:
        if args.base is not None:
            raise SurfaceError("--base is not supported with --predict-commit; it scopes the closeout payload only")
        return run_predict_commit(
            repo_root,
            paths=args.paths,
            as_json=args.json,
            plan_only=args.plan_only,
            run_command=run_command,
            emit_payload=_emit_payload,
            advisory_provider=_rca_link_advisory.provider,
        )

    _advise_staged_reversion(repo_root)
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = _resolve_changed_paths(repo_root, args)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["executed_commands"] = []
    payload["headroom"] = headroom_for([Path(p) for p in payload["changed_paths"]], repo_root)

    if not payload["changed_paths"]:
        payload["status"] = "noop"
        return _emit_payload(payload, as_json=args.json)

    blocked = _run_preexecution_blocks(repo_root, payload, args)
    if blocked is not None:
        return blocked

    command_plan: list[tuple[str, str]] = []
    if not args.skip_sync:
        command_plan.extend(("sync", command) for command in payload["sync_commands"])
    if not args.skip_verify:
        command_plan.extend(("verify", command) for command in payload["verify_commands"])
        hygiene_command = _agent_browser_hygiene_command(repo_root)
        if hygiene_command is not None:
            command_plan.append(("verify", hygiene_command))

    broad_policy = plan_broad_pytest_policy(
        command_plan,
        skip_broad_pytest=args.skip_broad_pytest,
        verification_lock=args.verification_lock,
    )
    command_plan = broad_policy.pop("command_plan")
    payload.update({key: value for key, value in broad_policy.items() if value and key != "block_error"})

    if should_block_broad_pytest_policy(broad_policy, plan_only=args.plan_only):
        payload["status"] = "blocked"
        payload["error"] = broad_policy["block_error"]
        return _emit_payload(payload, as_json=args.json, stderr_message=payload["error"])

    if args.plan_only:
        payload["status"] = "planned"
        payload["planned_commands"] = _planned_commands(
            repo_root, list(payload["changed_paths"]), command_plan, args
        )
        return _emit_payload(payload, as_json=args.json)

    unsafe_blockers = _unsafe_command_blockers(_unsafe_blocker_command_plan(command_plan, args))
    if unsafe_blockers:
        payload["status"] = "blocked"
        payload["blockers"] = list(payload.get("blockers", [])) + unsafe_blockers
        return _emit_payload(payload, as_json=args.json)

    broad_pytest_producer = _resolve_broad_producer(args, repo_root, run_command)

    should_stop = execute_command_plan(
        repo_root,
        command_plan,
        payload,
        run_command=run_command,
        collect_changed_paths=_closeout_changed_paths_collector(list(payload["changed_paths"])),
        refresh_broad_pytest_proof=args.refresh_broad_pytest_proof,
        broad_pytest_producer=broad_pytest_producer,
    )
    if not should_stop:
        should_stop = run_focused_closeout_coverage(args, repo_root, payload, run_command)

    # Gate-baseline runtime advisory (spec achieve-efficiency-improvements C):
    # a gate that PASSES but is slow by design is code-quality debt. Runs
    # POST-execution (it needs elapsed_seconds), attaches a verdict to the durable
    # JSON payload (spec C2), and is honest about scope — only gates run THROUGH
    # this script, never the separate-process host pre-push hook (spec C1).
    attach_gate_runtime_advisory(payload)

    if should_stop:
        _attach_closeout_telemetry(repo_root, payload)
        return _emit_payload(payload, as_json=args.json, stderr_message=payload.get("error"))

    payload["status"] = "completed"
    usage_episode = emit_usage_episode_for_slice_closeout(repo_root, str(payload["status"]))
    payload["usage_episode"] = usage_episode
    if usage_episode["status"] in {"invalid_adapter", "invalid_records_path", "emit_failed"}:
        payload["status"] = "failed"
    _attach_closeout_telemetry(repo_root, payload)
    return _emit_payload(payload, as_json=args.json)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
