#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
collect_changed_paths_since_base = _scripts_surfaces_lib_module.collect_changed_paths_since_base
collect_changed_paths_since_resolved_base = _scripts_surfaces_lib_module.collect_changed_paths_since_resolved_base
resolve_explicit_campaign_base = _scripts_surfaces_lib_module.resolve_explicit_campaign_base
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
_scripts_plan_cautilus_proof_module = import_repo_module(__file__, "scripts.plan_cautilus_proof")
plan_cautilus_proof = _scripts_plan_cautilus_proof_module.plan_cautilus_proof
_scripts_risk_interrupt_lib_module = import_repo_module(__file__, "scripts.risk_interrupt_lib")
plan_risk_interrupt = _scripts_risk_interrupt_lib_module.plan_risk_interrupt
_slice_closeout_risk_interrupt = import_repo_module(__file__, "scripts.slice_closeout_risk_interrupt")
risk_interrupt_observe_initial_paths = _slice_closeout_risk_interrupt.observe_initial_paths
risk_interrupt_observe_final_paths = _slice_closeout_risk_interrupt.observe_final_paths
risk_interrupt_block_reason = _slice_closeout_risk_interrupt.block_reason
_agent_browser_probe_policy = import_repo_module(__file__, "scripts.agent_browser_probe_policy")
unsafe_agent_browser_probe_reason = _agent_browser_probe_policy.unsafe_agent_browser_probe_reason
_slice_closeout_usage_episode = import_repo_module(__file__, "scripts.slice_closeout_usage_episode")
emit_usage_episode_for_slice_closeout = _slice_closeout_usage_episode.emit_usage_episode_for_slice_closeout
_slice_closeout_parser = import_repo_module(__file__, "scripts.slice_closeout_parser")
_slice_closeout_command_executor = import_repo_module(__file__, "scripts.slice_closeout_command_executor")
execute_command_plan = _slice_closeout_command_executor.execute_command_plan
_slice_closeout_advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
_artifact_citations = import_repo_module(__file__, "scripts.check_artifact_citations")
advise_artifact_citations = _artifact_citations.advise_artifact_citations
advise_prose_pin = _slice_closeout_advisories.advise_prose_pin
advise_skill_surface_preflight = _slice_closeout_advisories.advise_skill_surface_preflight
advise_doc_surface_preflight = _slice_closeout_advisories.advise_doc_surface_preflight
advise_new_pool_module = _slice_closeout_advisories.advise_new_pool_module
advise_repair_parity = _slice_closeout_advisories.advise_repair_parity
_removed_name_consumers = import_repo_module(__file__, "scripts.removed_name_consumers")
advise_removed_name_consumers = _removed_name_consumers.advise_removed_name_consumers
advise_over_slicing = _slice_closeout_advisories.advise_over_slicing
advise_floor_addition_restraint = _slice_closeout_advisories.advise_floor_addition_restraint
_slice_closeout_commit_advisories = import_repo_module(__file__, "scripts.slice_closeout_commit_advisories")
advise_close_keyword_leakage = _slice_closeout_commit_advisories.advise_close_keyword_leakage
advise_decaying_habits = _slice_closeout_commit_advisories.advise_decaying_habits
attach_gate_runtime_advisory = _slice_closeout_advisories.attach_gate_runtime_advisory
_new_proof_surface_advisory = import_repo_module(__file__, "scripts.new_proof_surface_advisory")
attach_new_proof_surface_advisory = _new_proof_surface_advisory.attach_new_proof_surface_advisory
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
_skill_cut_safety_advisory = import_repo_module(__file__, "scripts.skill_cut_safety_advisory")
_mutation_coverage_producer = import_repo_module(__file__, "scripts.mutation_coverage_producer")
_slice_closeout_run_command = import_repo_module(__file__, "scripts.slice_closeout_run_command")
_proof_receipt = import_repo_module(__file__, "scripts.proof_receipt")
plan_broad_pytest_policy = _slice_closeout_broad_gate.plan_broad_pytest_policy
should_block_broad_pytest_policy = _slice_closeout_broad_gate.should_block_broad_pytest_policy
closeout_producer_or_error = _mutation_coverage_producer.closeout_producer_or_error
closeout_producer_validation_error = _mutation_coverage_producer.closeout_producer_validation_error
run_focused_closeout_coverage = _mutation_coverage_producer.run_focused_closeout_coverage
run_produced_coverage_consumer = _mutation_coverage_producer.run_produced_coverage_consumer
run_command = _slice_closeout_run_command.run_command
closeout_receipt = _proof_receipt.closeout_receipt
ReceiptContractError = _proof_receipt.ReceiptContractError


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


def _emit_payload(payload: dict[str, object], *, stderr_message: str | None = None) -> int:
    effective_exit_code = 0 if payload["status"] not in {"blocked", "failed"} else 1
    try:
        receipt = closeout_receipt(payload, effective_exit_code=effective_exit_code)
    except ReceiptContractError as exc:
        # A failed/blocked path without a command still needs a named cause. Make
        # the missing producer fact itself explicit, then render that contract
        # failure instead of emitting a bare status that cannot be acted on.
        if not isinstance(payload.get("error"), str) or not payload["error"].strip():
            payload["error"] = f"closeout receipt could not identify a cause: {exc}"
        receipt = closeout_receipt(payload, effective_exit_code=effective_exit_code)
    payload["effective_exit_code"] = effective_exit_code
    payload["proof_receipt"] = receipt.as_dict()
    # Unconditional YAML. The retired `slice_closeout_reporting.print_text`
    # rendering was a projection OF this payload, so the payload is a superset of
    # what it showed and nothing it stated is lost. The stderr cause line is kept:
    # it was the default (non-`--json`) behavior, and it is what makes a blocked
    # closeout visible in a runner's error channel.
    emit_yaml(payload)
    if stderr_message is not None:
        print(stderr_message, file=sys.stderr)
    return effective_exit_code


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


def _maybe_block_on_unmatched(payload: dict[str, object], *, allow_unmatched: bool) -> int | None:
    if not payload["unmatched_paths"] or allow_unmatched:
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        "changed paths are not covered by the surfaces manifest; "
        "add the missing coverage or rerun with --allow-unmatched"
    )
    return _emit_payload(payload, stderr_message=payload["error"])


def _maybe_block_on_cautilus(
    repo_root: Path, payload: dict[str, object], *, ack_skill_review: bool
) -> int | None:
    cautilus_plan = plan_cautilus_proof(repo_root, payload["changed_paths"])
    payload["cautilus_plan"] = cautilus_plan
    # Cautilus is eval-only and ask-before-run, so the planner never declares a
    # slice's proof mandatory; the public-skill review below is the only arm that
    # blocks. A `required` flag used to sit here, hardcoded False since 66c7a729,
    # with a whole blocking branch behind it that could not execute.
    if cautilus_plan["skill_validation_recommendations"] and not ack_skill_review:
        payload["status"] = "blocked"
        payload["error"] = (
            "public-skill validation review is required for this slice; inspect the dogfood/scenario "
            "follow-ups in `cautilus_plan` and rerun with --ack-cautilus-skill-review after recording "
            "the decision"
        )
        return _emit_payload(payload, stderr_message=payload["error"])
    return None


def _maybe_block_on_risk_interrupt(
    repo_root: Path, payload: dict[str, object], risk_interrupt_paths: list[str] | None
) -> int | None:
    payload["risk_interrupt_paths"] = list(risk_interrupt_paths or [])
    risk_interrupt_plan = plan_risk_interrupt(repo_root, risk_interrupt_paths)
    payload["risk_interrupt_plan"] = risk_interrupt_plan
    reason = risk_interrupt_block_reason(risk_interrupt_plan)
    if reason is None:
        return None
    payload["status"] = "blocked"
    payload["error"] = f"risk interrupt is blocking ordinary closeout: {reason}"
    return _emit_payload(payload, stderr_message=payload["error"])


def _resolve_broad_producer(args, repo_root: Path, run_command, *, base_sha: str | None = None):
    """Resolve the closeout broad-pytest mutation-coverage producer (or None) from
    args. Raises ``SurfaceError`` on misuse (e.g. --produce-mutation-coverage
    without --verification-lock) so the entrypoint reports it and exits non-zero."""
    producer, error = closeout_producer_or_error(
        args, repo_root, run_command, base_sha=base_sha
    )
    if error is not None:
        raise SurfaceError(error)
    return producer


def _run_produced_coverage_consumer_if_ready(
    should_stop: bool,
    repo_root: Path,
    payload: dict[str, object],
) -> bool:
    """Keep consumer verification out of ``main``'s already-tight branch budget."""
    if should_stop:
        return True
    return run_produced_coverage_consumer(repo_root, payload, run_command)


def _advise_staged_reversion(repo_root: Path) -> None:
    # Advisory (#258): surface a staged reversion (index != HEAD while worktree
    # == HEAD) at closeout, before the human commit. Reads git directly; the
    # blocking teeth live in the pre-commit gate (check_staged_reversion.py).
    lib = import_repo_module(__file__, "scripts.check_staged_reversion")
    try:
        findings = lib.find_staged_reversions(str(repo_root))
    except RuntimeError as exc:
        # git could not read the index, so this advisory established nothing.
        # Say so rather than let silence read as "no staged reversion".
        print(
            "WARN: staged-reversion advisory unavailable — git could not read the "
            f"index at {repo_root} ({exc}); the pre-commit gate still applies.",
            file=sys.stderr,
        )
        return
    if findings:
        print(
            "WARN: staged reversion of already-committed file(s) — index != HEAD "
            "while worktree == HEAD (#258); the pre-commit gate will block this "
            "commit. Affected: " + ", ".join(f.path for f in findings),
            file=sys.stderr,
        )


def _build_parser() -> argparse.ArgumentParser:
    return _slice_closeout_parser.build_parser(repo_root=REPO_ROOT, surfaces_path=SURFACES_PATH)

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


def _proof_scope_paths(proof: object) -> list[str]:
    if not isinstance(proof, dict):
        return []
    if isinstance(proof.get("changed_paths"), list):
        return [str(path) for path in proof["changed_paths"]]
    match = proof.get("match")
    if isinstance(match, dict) and isinstance(match.get("changed_paths"), list):
        return [str(path) for path in match["changed_paths"]]
    return []


def _maybe_fail_on_broad_pytest_scope_drift(payload: dict[str, object]) -> bool:
    expected = {str(path) for path in payload.get("changed_paths", []) if path}
    if not expected:
        return False
    findings: list[dict[str, object]] = []
    for proof_key in ("recorded_broad_pytest_proofs", "reused_broad_pytest_proofs"):
        proofs = payload.get(proof_key)
        if not isinstance(proofs, list):
            continue
        for proof in proofs:
            actual = set(_proof_scope_paths(proof))
            missing = sorted(expected - actual)
            if missing:
                findings.append(
                    {
                        "proof_key": proof_key,
                        "command": proof.get("command") if isinstance(proof, dict) else None,
                        "missing_changed_paths": missing,
                    }
                )
    if not findings:
        return False
    payload["status"] = "failed"
    payload["broad_pytest_scope_findings"] = findings
    payload["error"] = (
        "broad pytest proof scope is narrower than the closeout payload; "
        "rerun closeout after fixing the proof collector"
    )
    return True


def _planned_commands(
    repo_root: Path,
    changed_paths: list[str],
    command_plan: list[tuple[str, str]],
    args,
    *,
    structural_paths: list[str] | None = None,
) -> list[dict[str, object]]:
    planned = structural_sweep_planned_commands(
        repo_root, changed_paths if structural_paths is None else structural_paths
    )
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


def _run_preexecution_blocks(
    repo_root: Path,
    payload: dict[str, object],
    args,
    *,
    structural_paths: list[str] | None = None,
    risk_interrupt_paths: list[str] | None,
    base: str = "origin/main",
) -> int | None:
    """Fail-fast pre-execution gate chain; returns an exit code on the first block.
    #332: the cheap structural sweep runs FIRST (before surface-match / cautilus /
    risk interrupt / broad pytest), then advisories, unmatched, cautilus, risk.
    """
    payload["risk_interrupt_paths"] = list(risk_interrupt_paths or [])
    blocked = block_on_structural_sweep(
        repo_root,
        payload,
        plan_only=args.plan_only,
        run_command=run_command,
        emit_payload=_emit_payload,
        paths=structural_paths,
    )
    if blocked is not None:
        return blocked

    producer_error = closeout_producer_validation_error(args)
    if producer_error:
        payload["status"] = "blocked"
        payload["error"] = producer_error
        return _emit_payload(payload, stderr_message=producer_error)

    advise_prose_pin(repo_root, payload["changed_paths"])
    advise_skill_surface_preflight(repo_root, payload["changed_paths"])
    advise_doc_surface_preflight(repo_root, payload["changed_paths"])
    advise_new_pool_module(repo_root, payload["changed_paths"], base=base)
    advise_repair_parity(repo_root, payload["changed_paths"], base=base)
    # Against the slice BASE, and over the slice-base PATH SET too: a name deleted
    # in an earlier slice commit leaves its file clean, so the worktree-dirty set
    # alone would never inspect it. `advise_removed_name_consumers` widens the set
    # itself and falls back to this one when the base does not resolve.
    advise_removed_name_consumers(repo_root, payload["changed_paths"], against=base)
    advise_over_slicing(repo_root)
    advise_floor_addition_restraint(repo_root, payload["changed_paths"], base=base)
    attach_new_proof_surface_advisory(payload, repo_root, base=base)
    advise_close_keyword_leakage(repo_root, base=base)
    advise_decaying_habits(repo_root, payload["changed_paths"])
    advise_artifact_citations(repo_root, payload["changed_paths"])

    blocked = _maybe_block_on_unmatched(payload, allow_unmatched=args.allow_unmatched)
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_cautilus(
        repo_root, payload, ack_skill_review=args.ack_cautilus_skill_review
    )
    if blocked is not None:
        return blocked

    return _maybe_block_on_risk_interrupt(repo_root, payload, risk_interrupt_paths)


def _attach_closeout_telemetry(repo_root: Path, payload: dict[str, object]) -> None:
    """Append the objective operational-waste record for this run (spec
    achieve-efficiency-improvements, E1). Reads the final ``status`` already on the
    payload, so callers must set it first. Never raises (the emitter degrades
    silently); attaches its status dict for visibility."""
    payload["closeout_telemetry"] = emit_closeout_telemetry_for_slice(repo_root, payload)


def _predict_commit_advisories(repo_root: Path, selected_paths: list[str]) -> list[str]:
    """Compose every non-blocking predict-commit advisory: the RCA-link nudge and
    the skill-deletion REVIEW nudge (#floor-addition-restraint site). Each source
    is independently exit-0-only; run_predict_commit takes a single provider."""
    return _rca_link_advisory.provider(repo_root, selected_paths) + _skill_cut_safety_advisory.provider(
        repo_root, selected_paths
    )


def main() -> int:
    args = _build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    if args.predict_commit:
        if args.base is not None:
            raise SurfaceError("--base is not supported with --predict-commit; it scopes the closeout payload only")
        return run_predict_commit(
            repo_root,
            paths=args.paths,
            plan_only=args.plan_only,
            run_command=run_command,
            emit_payload=_emit_payload,
            advisory_provider=_predict_commit_advisories,
        )

    _advise_staged_reversion(repo_root)
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    campaign_base_sha = resolve_explicit_campaign_base(repo_root, args.base, has_paths=bool(args.paths))
    changed_paths = (
        collect_changed_paths_since_resolved_base(repo_root, campaign_base_sha)
        if campaign_base_sha
        else _resolve_changed_paths(repo_root, args)
    )
    initial_risk_observation = risk_interrupt_observe_initial_paths(
        repo_root=repo_root,
        campaign_base_sha=campaign_base_sha,
        base=args.base,
        collect_live=collect_changed_paths,
        collect_since_base=collect_changed_paths_since_base,
        collect_since_resolved_base=collect_changed_paths_since_resolved_base,
        observation_error=SurfaceError,
    )
    risk_interrupt_paths = initial_risk_observation["paths"]
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["executed_commands"] = []
    payload["risk_interrupt_path_observations"] = [initial_risk_observation]
    payload["headroom"] = headroom_for([Path(p) for p in payload["changed_paths"]], repo_root)

    if not payload["changed_paths"]:
        payload["status"] = "noop"
        return _emit_payload(payload)

    structural_paths = collect_changed_paths(repo_root) if args.base is not None else None
    blocked = _run_preexecution_blocks(
        repo_root,
        payload,
        args,
        structural_paths=structural_paths,
        risk_interrupt_paths=risk_interrupt_paths,
        base=campaign_base_sha or "origin/main",
    )
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
        return _emit_payload(payload, stderr_message=payload["error"])

    if args.plan_only:
        payload["status"] = "planned"
        payload["planned_commands"] = _planned_commands(
            repo_root,
            list(payload["changed_paths"]),
            command_plan,
            args,
            structural_paths=structural_paths,
        )
        return _emit_payload(payload)

    unsafe_blockers = _unsafe_command_blockers(_unsafe_blocker_command_plan(command_plan, args))
    if unsafe_blockers:
        payload["status"] = "blocked"
        payload["blockers"] = list(payload.get("blockers", [])) + unsafe_blockers
        return _emit_payload(payload)

    broad_pytest_producer = _resolve_broad_producer(
        args, repo_root, run_command, base_sha=campaign_base_sha
    )

    should_stop = execute_command_plan(
        repo_root,
        command_plan,
        payload,
        run_command=run_command,
        collect_changed_paths=_closeout_changed_paths_collector(list(payload["changed_paths"])),
        refresh_broad_pytest_proof=args.refresh_broad_pytest_proof,
        broad_pytest_producer=broad_pytest_producer,
        stop_on_sync_drift=args.verification_lock,
    )
    if not should_stop:
        should_stop = run_focused_closeout_coverage(
            args, repo_root, payload, run_command, base_sha=campaign_base_sha
        )
    should_stop = _run_produced_coverage_consumer_if_ready(should_stop, repo_root, payload)

    # Gate-baseline runtime advisory (spec achieve-efficiency-improvements C):
    # a gate that PASSES but is slow by design is code-quality debt. Runs
    # POST-execution (it needs elapsed_seconds), attaches a verdict to the durable
    # JSON payload (spec C2), and is honest about scope — only gates run THROUGH
    # this script, never the separate-process host pre-push hook (spec C1).
    attach_gate_runtime_advisory(payload)

    if should_stop:
        _attach_closeout_telemetry(repo_root, payload)
        return _emit_payload(payload, stderr_message=payload.get("error"))

    if _maybe_fail_on_broad_pytest_scope_drift(payload):
        _attach_closeout_telemetry(repo_root, payload)
        return _emit_payload(payload, stderr_message=payload.get("error"))

    # Sync, verification, and coverage producers may add generated or artifact
    # paths after the fail-fast check. Preserve committed campaign paths and add
    # the final live Git set before success; --paths never narrows this decision.
    final_risk_observation = risk_interrupt_observe_final_paths(
        repo_root,
        initial_observation=initial_risk_observation,
        collect_live=collect_changed_paths,
        observation_error=SurfaceError,
    )
    payload["risk_interrupt_path_observations"].append(final_risk_observation)
    final_risk_interrupt_paths = final_risk_observation["paths"]
    blocked = _maybe_block_on_risk_interrupt(repo_root, payload, final_risk_interrupt_paths)
    if blocked is not None:
        return blocked

    payload["status"] = "completed"
    usage_episode = emit_usage_episode_for_slice_closeout(repo_root, str(payload["status"]))
    payload["usage_episode"] = usage_episode
    payload["status"] = (
        "failed"
        if usage_episode["status"] in {"invalid_adapter", "invalid_records_path", "emit_failed"}
        else payload["status"]
    )
    _attach_closeout_telemetry(repo_root, payload)
    return _emit_payload(payload)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
