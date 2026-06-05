#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
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
_scripts_check_python_lengths = import_repo_module(__file__, "scripts.check_python_lengths")
headroom_for = _scripts_check_python_lengths.headroom_for
_staged_commit_gate_plan = import_repo_module(__file__, "scripts.staged_commit_gate_plan")
run_predict_commit = _staged_commit_gate_plan.run_predict_commit
_slice_closeout_broad_gate = import_repo_module(__file__, "scripts.slice_closeout_broad_gate")
plan_broad_pytest_policy = _slice_closeout_broad_gate.plan_broad_pytest_policy
print_broad_pytest_policy = _slice_closeout_broad_gate.print_broad_pytest_policy
should_block_broad_pytest_policy = _slice_closeout_broad_gate.should_block_broad_pytest_policy
COMMAND_TIMEOUT_SECONDS = 1800
PROGRESS_INTERVAL_SECONDS = 30.0

def _progress_interval_seconds() -> float:
    raw = os.environ.get("CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS")
    if raw is None:
        return PROGRESS_INTERVAL_SECONDS
    try:
        return max(0.1, float(raw))
    except ValueError:
        return PROGRESS_INTERVAL_SECONDS


def _short_command(command: str, limit: int = 120) -> str:
    collapsed = " ".join(command.split())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 3]}..."


def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
    python_executable = shlex.quote(sys.executable)
    with tempfile.TemporaryDirectory(prefix="charness-closeout-bin-") as wrapper_dir:
        wrapper_path = Path(wrapper_dir)
        wrappers = {
            "python3": f"#!/usr/bin/env bash\nexec {python_executable} \"$@\"\n",
            "pytest": f"#!/usr/bin/env bash\nexec {python_executable} -m pytest \"$@\"\n",
        }
        for name, body in wrappers.items():
            script = wrapper_path / name
            script.write_text(body, encoding="utf-8")
            script.chmod(0o755)
        inherited_path = os.environ.get("PATH", "")
        path = f"{wrapper_path}:{inherited_path}" if inherited_path else str(wrapper_path)
        wrapped_command = f"export PATH={shlex.quote(path)}; {command}"
        display_command = _short_command(command)
        print(f"RUN [{phase}] {display_command}", file=sys.stderr, flush=True)
        started_at = time.monotonic()
        process = subprocess.Popen(
            ["/bin/bash", "-lc", wrapped_command],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        dot_count = 0
        while True:
            try:
                stdout, stderr = process.communicate(timeout=_progress_interval_seconds())
                result = subprocess.CompletedProcess(
                    ["/bin/bash", "-lc", wrapped_command],
                    process.returncode,
                    stdout or "",
                    stderr or "",
                )
                break
            except subprocess.TimeoutExpired:
                dot_count += 1
                print(".", end="", file=sys.stderr, flush=True)
                if dot_count % 80 == 0:
                    print("", file=sys.stderr, flush=True)
            if time.monotonic() - started_at > COMMAND_TIMEOUT_SECONDS:
                process.kill()
                stdout, stderr = process.communicate()
                stderr = f"{stderr or ''}\ntimed out after {COMMAND_TIMEOUT_SECONDS}s".strip()
                result = subprocess.CompletedProcess(
                    ["/bin/bash", "-lc", wrapped_command],
                    124,
                    stdout or "",
                    stderr,
                )
                break
        if dot_count:
            print("", file=sys.stderr, flush=True)
        elapsed = time.monotonic() - started_at
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"{status} [{phase}] {elapsed:.1f}s {display_command}", file=sys.stderr, flush=True)
    return {
        "phase": phase,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_seconds": round(elapsed, 2),
    }


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


def _print_list(label: str, values: list[str]) -> None:
    if values:
        print(f"{label}:")
        for value in values:
            print(f"- {value}")
        return
    print(f"{label}: none")


def _cautilus_plan_has_visible_work(cautilus_plan: dict[str, object]) -> bool:
    return bool(
        cautilus_plan.get("required")
        or cautilus_plan.get("scenario_registry_review_required")
        or cautilus_plan.get("skill_validation_recommendations")
        or cautilus_plan.get("recommended_followups")
    )


def _print_cautilus_plan(cautilus_plan: dict[str, object]) -> None:
    print("Cautilus proof:")
    print(f"- run_mode: {cautilus_plan['run_mode']}")
    proof_kinds = cautilus_plan.get("proof_kinds", [])
    print(f"- proof_kinds: {', '.join(proof_kinds) if proof_kinds else 'none'}")
    print(f"- next_action: {cautilus_plan['next_action']}")
    changed_public_skills = cautilus_plan.get("changed_public_skills", [])
    if changed_public_skills:
        print(f"- changed_public_skills: {', '.join(changed_public_skills)}")
    if cautilus_plan.get("scenario_registry_review_required"):
        print("- scenario_registry_review_required: true")
    for note in cautilus_plan.get("notes", []):
        print(f"- note: {note}")
    for recommendation in cautilus_plan.get("skill_validation_recommendations", []):
        if isinstance(recommendation, dict):
            print(
                "- skill_review: "
                f"{recommendation.get('skill_id')} ({recommendation.get('validation_tier')})"
            )
    for followup in cautilus_plan.get("recommended_followups", []):
        print(f"- followup: {followup}")


def _print_risk_interrupt_plan(risk_interrupt_plan: dict[str, object]) -> None:
    print("Risk interrupt:")
    print(f"- status: {risk_interrupt_plan['status']}")
    for key in (
        "artifact_path",
        "interrupt_id",
        "handoff_artifact",
        "chosen_next_step",
        "impl_status",
        "next_action",
    ):
        value = risk_interrupt_plan.get(key)
        if value:
            print(f"- {key}: {value}")
    for reason in risk_interrupt_plan.get("reasons", []):
        print(f"- reason: {reason}")


def _print_executed_commands(payload: dict[str, object]) -> None:
    if not payload["executed_commands"]:
        return
    print("Executed commands:")
    for step in payload["executed_commands"]:
        status = "PASS" if step["returncode"] == 0 else "FAIL"
        print(f"- [{step['phase']}] {status} {step['command']}")
        if step["returncode"] != 0:
            if step["stdout"]:
                print(step["stdout"], end="" if step["stdout"].endswith("\n") else "\n")
            if step["stderr"]:
                print(step["stderr"], end="" if step["stderr"].endswith("\n") else "\n")


def _print_headroom(payload: dict[str, object]) -> None:
    # Advisory (#256): surface changed gated files already near the length limit
    # so the next slice chooses new-module-vs-append before writing. Never blocks.
    rows = payload.get("headroom")
    near = [row for row in rows if row.get("near_limit")] if isinstance(rows, list) else []
    if not near:
        return
    print("WARN: changed files near the length limit (consider a new module before adding more):")
    for row in near:
        print(
            f"- {row['path']}: {row['lines']}/{row['limit']} code lines "
            f"({row['headroom']} left)"
        )


def _print_usage_episode(payload: dict[str, object]) -> None:
    usage_episode = payload.get("usage_episode")
    if not isinstance(usage_episode, dict):
        return
    print("Usage episode:")
    print(f"- status: {usage_episode['status']}")
    if usage_episode.get("records_path"):
        print(f"- records_path: {usage_episode['records_path']}")
    if usage_episode.get("episode_id"):
        print(f"- episode_id: {usage_episode['episode_id']}")
    if usage_episode.get("error"):
        print(f"- error: {usage_episode['error']}")


def print_text(payload: dict[str, object]) -> None:
    print(f"Closeout status: {payload['status']}")
    _print_list("Changed paths", payload["changed_paths"])
    matched_surfaces = [
        f"{surface['surface_id']}: {surface['description']}" for surface in payload["matched_surfaces"]
    ]
    _print_list("Matched surfaces", matched_surfaces)
    if payload["unmatched_paths"]:
        _print_list("Unmatched paths", payload["unmatched_paths"])

    cautilus_plan = payload.get("cautilus_plan")
    if isinstance(cautilus_plan, dict) and _cautilus_plan_has_visible_work(cautilus_plan):
        _print_cautilus_plan(cautilus_plan)

    risk_interrupt_plan = payload.get("risk_interrupt_plan")
    if isinstance(risk_interrupt_plan, dict) and risk_interrupt_plan.get("status") != "not-applicable":
        _print_risk_interrupt_plan(risk_interrupt_plan)

    _print_headroom(payload)
    print_broad_pytest_policy(payload)
    _print_executed_commands(payload)
    _print_usage_episode(payload)


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

def main() -> int:
    args = _build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    if args.predict_commit:
        return run_predict_commit(
            repo_root,
            paths=args.paths,
            as_json=args.json,
            plan_only=args.plan_only,
            run_command=run_command,
            emit_payload=_emit_payload,
        )

    _advise_staged_reversion(repo_root)
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["executed_commands"] = []
    payload["headroom"] = headroom_for([Path(p) for p in payload["changed_paths"]], repo_root)

    if not payload["changed_paths"]:
        payload["status"] = "noop"
        return _emit_payload(payload, as_json=args.json)

    blocked = _maybe_block_on_unmatched(payload, allow_unmatched=args.allow_unmatched, as_json=args.json)
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_cautilus(
        repo_root,
        payload,
        as_json=args.json,
        ack_skill_review=args.ack_cautilus_skill_review,
    )
    if blocked is not None:
        return blocked

    blocked = _maybe_block_on_risk_interrupt(repo_root, payload, as_json=args.json)
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
        payload["planned_commands"] = [{"phase": phase, "command": command} for phase, command in command_plan]
        return _emit_payload(payload, as_json=args.json)

    unsafe_blockers = _unsafe_command_blockers(command_plan)
    if unsafe_blockers:
        payload["status"] = "blocked"
        payload["blockers"] = list(payload.get("blockers", [])) + unsafe_blockers
        return _emit_payload(payload, as_json=args.json)

    should_stop = execute_command_plan(
        repo_root,
        command_plan,
        payload,
        run_command=run_command,
        collect_changed_paths=collect_changed_paths,
        refresh_broad_pytest_proof=args.refresh_broad_pytest_proof,
    )
    if should_stop:
        return _emit_payload(payload, as_json=args.json, stderr_message=payload.get("error"))

    payload["status"] = "completed"
    usage_episode = emit_usage_episode_for_slice_closeout(repo_root, str(payload["status"]))
    payload["usage_episode"] = usage_episode
    if usage_episode["status"] in {"invalid_adapter", "invalid_records_path", "emit_failed"}:
        payload["status"] = "failed"
    return _emit_payload(payload, as_json=args.json)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
