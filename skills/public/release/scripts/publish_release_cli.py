from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_current_release = SKILL_RUNTIME.load_local_skill_module(__file__, "current_release")
_check_review_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "check_requested_review_gate")
_fresh_checkout = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_artifact")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_narrative_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_narrative_gate")
_issue_closeout = SKILL_RUNTIME.load_local_skill_module(__file__, "release_issue_closeout")
_post_create = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_post_create")
_release_plan = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_plan")
_release_runtime = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_runtime")
_resume = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_resume")
_execute = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_execute")
# The argument contract lives in its own module (one concept, and this file reached
# its length cap). Re-exported so `cli.parse_args` stays the one import site.
_args_module = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_args")
parse_args = _args_module.parse_args
_yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output.emit_yaml
load_adapter = _resolve_adapter.load_adapter
build_release_payload = _current_release.build_payload
build_review_gate_payload = _check_review_gate.build_payload
build_fresh_checkout_payload = _fresh_checkout.build_payload
build_narrative_audit_payload = _narrative_gate.build_narrative_audit_payload
audit_notes_text = _narrative_gate.audit_notes_text
run_narrative_audit = _narrative_gate.run_narrative_audit
run_notes_file_preflight = _narrative_gate.run_notes_file_preflight
run = _helpers.run
run_shell = _helpers.run_shell
run_phase = _helpers.run_phase
git_status = _helpers.git_status
changed_paths = _helpers.changed_paths
write_current_artifact = _artifact.write_current_artifact
backend_command = _helpers.backend_command
create_release = _helpers.create_release
expected_github_release_url = _helpers.expected_github_release_url
amend_fresh_checkout_artifact = _helpers.amend_fresh_checkout_artifact
commit_post_publish_artifact = _helpers.commit_post_publish_artifact
release_commit_body = _issue_closeout.release_commit_body
ensure_release_issues_closed = _issue_closeout.ensure_release_issues_closed
preflight_release_issues = _issue_closeout.preflight_release_issues
validate_release_closeout_commit_message = _issue_closeout.validate_release_closeout_commit_message
release_content_close_keyword_refs = _issue_closeout.release_content_close_keyword_refs
fail_release_closeout_draft_validation = _issue_closeout.fail_release_closeout_draft_validation
commit_issue_closeout_artifact = _issue_closeout.commit_issue_closeout_artifact
commit_issue_closeout_carrier_artifact = _issue_closeout.commit_issue_closeout_carrier_artifact
validate_critique_artifact_arg = _preflight.validate_critique_artifact_arg
validate_bump_rationale_arg = _preflight.validate_bump_rationale_arg
enforce_release_critique_gate = _preflight.enforce_release_critique_gate
build_update_instructions_prep_payload = _preflight.build_update_instructions_prep_payload
release_adapter_preflight_payload = _preflight.release_adapter_preflight_payload
run_release_adapter_preflight = _preflight.run_release_adapter_preflight
release_surface_blocker = _preflight.release_surface_blocker
fail_after_post_create_verification = _post_create.fail_after_post_create_verification
verify_release_visible = _post_create.verify_release_visible
confirm_release_via_distinct_channel = _post_create.confirm_release_via_distinct_channel
reconcile_public_release_verification = _post_create.reconcile_public_release_verification
audit_published_release_body = _post_create.audit_published_release_body
evaluate_release_distinct_channel = _post_create.evaluate_release_distinct_channel
fail_release_distinct_channel_floor = _post_create.fail_release_distinct_channel_floor
run_post_publish_install_refresh = _post_create.run_post_publish_install_refresh
collect_installed_readback = _post_create.collect_installed_readback
safe_write_release_observer = _post_create.safe_write_release_observer
validate_release_observer_record = _post_create.validate_release_observer_record
build_publish_plan = _release_plan.build_publish_plan
release_plan_target_version = _release_plan.target_version
gate_target_version = _release_plan.gate_target_version
release_previous_version = _helpers.release_previous_version
resume_publish = _resume.resume_publish
preflight_resume_state = _resume.preflight_resume_state


def _execution_context() -> SimpleNamespace:
    names = (
        "run_notes_file_preflight",
        "build_release_payload",
        "_helpers",
        "run",
        "backend_command",
        "expected_github_release_url",
        "preflight_release_issues",
        "validate_release_closeout_commit_message",
        "release_content_close_keyword_refs",
        "fail_release_closeout_draft_validation",
        "run_release_adapter_preflight",
        "run_bump",
        "ensure_release_surface",
        "release_surface_blocker",
        "changed_paths",
        "build_fresh_checkout_payload",
        "write_current_artifact",
        "run_requested_review_gate",
        "run_cli_skill_surface_gate",
        "run_shell",
        "run_phase",
        "run_narrative_audit",
        "release_commit_body",
        "run_fresh_checkout_probes",
        "amend_fresh_checkout_artifact",
        "create_release",
        "verify_release_visible",
        "confirm_release_via_distinct_channel",
        "reconcile_public_release_verification",
        "audit_published_release_body",
        "audit_notes_text",
        "evaluate_release_distinct_channel",
        "fail_release_distinct_channel_floor",
        "finalize_release_payload",
        "commit_final_release_artifact",
        "commit_issue_closeout_carrier_artifact",
        "fail_after_post_create_verification",
        "ensure_release_issues_closed",
        "run_post_publish_install_refresh",
        "collect_installed_readback",
        "safe_write_release_observer",
        "validate_release_observer_record",
    )
    return SimpleNamespace(**{name: globals()[name] for name in names})


def run_requested_review_gate(repo_root: Path) -> dict[str, Any]:
    review_gate_payload = build_review_gate_payload(repo_root, run_commands=True)
    if review_gate_payload["status"] == "blocked":
        raise SystemExit("requested release review gate blocked publish:\n" + "\n".join(review_gate_payload["blockers"]))
    return review_gate_payload


def run_cli_skill_surface_gate(repo_root: Path, adapter_data: dict[str, Any]) -> None:
    if {"installable_cli", "bundled_skill"}.issubset(set(adapter_data.get("product_surfaces", []))):
        command = ["python3", "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo_root)]
        command.extend(["--adapter-path", ".agents/release-adapter.yaml", "--run-probes"])
        for path in changed_paths(repo_root):
            command.extend(["--changed-path", path])
        run(command, cwd=repo_root)


def run_fresh_checkout_probes(repo_root: Path) -> dict[str, Any]:
    payload = build_fresh_checkout_payload(repo_root, run_probes=True)
    if payload["status"] == "blocked":
        raise SystemExit("fresh checkout release probes blocked publish:\n" + "\n".join(payload.get("blockers", [])))
    return payload

def run_bump(args: argparse.Namespace, repo_root: Path) -> None:
    if args.publish_current:
        return
    bump_command = ["python3", str(Path(__file__).resolve().with_name("bump_version.py")), "--repo-root", str(repo_root)]
    bump_command.extend(["--set-version", args.set_version] if args.set_version else ["--part", args.part])
    run(bump_command, cwd=repo_root)


def ensure_release_surface(repo_root: Path, expected_version: str, *, stage: str = "unrecorded stage") -> dict[str, Any]:
    """Refuse a drifted release surface, and RETURN what the check established.

    The return value is not decoration: the release record used to assert
    "`current_release.py` reported no version drift" as an unconditional literal, so
    the sentence rendered identically on a lane that never called this. Callers store
    the disposition on the payload as `version_drift_check`, and the record says the
    check was not recorded when they did not.
    """
    release_payload = build_release_payload(repo_root)
    blocker = release_surface_blocker(release_payload, expected_version)
    if blocker:
        raise SystemExit(blocker)
    versioned_surfaces = release_payload.get("versioned_surfaces")
    presence_surfaces = release_payload.get("presence_surfaces")
    return {
        "status": "passed",
        "stage": stage,
        "checked_version": expected_version,
        "versioned_surfaces": sorted(versioned_surfaces)
        if isinstance(versioned_surfaces, (list, tuple))
        else [],
        "presence_surfaces": sorted(presence_surfaces)
        if isinstance(presence_surfaces, (list, tuple))
        else [],
        # Always empty on this path -- a non-empty `drift` raised above. Recorded so the
        # disposition reads as the output of a check rather than as a constant.
        "drift": list(release_payload.get("drift") or []),
        "absence_corroboration": release_payload.get("absence_corroboration"),
    }


def finalize_release_payload(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    artifact_relpath: str,
    release_stdout: str,
    expected_release_url: str | None,
    release_verified: bool,
    commit_sha: str | None = None,
) -> None:
    # `commit_sha` is the TAGGED commit when the caller knows it, and HEAD only as a
    # fallback. On the claims lane those differ: the tag is created at the prepared
    # record P, while HEAD by this point is the follow-on evidence commit the resume
    # makes for refreshed quality inventory. This value is rendered into the durable
    # release record, into the release-observer JSON's `target.commit`, and into the
    # comment posted on EVERY issue this release closes -- so reading HEAD told each
    # reporter a commit that `v6.0.0` does not point at. A silent mis-report at an
    # irreversible boundary, which is the class this lane exists to hold.
    payload["commit_sha"] = commit_sha or run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    payload["artifact_path"] = artifact_relpath
    payload["public_release_verification"] = "verified" if release_verified else "failed"
    payload["release_url"] = next((line.strip() for line in reversed(release_stdout.splitlines()) if line.strip()), None)
    if payload["release_url"] and expected_release_url and payload["release_url"] != expected_release_url:
        payload["release_url_warning"] = (
            f"release create returned `{payload['release_url']}` but the committed artifact "
            f"recorded expected URL `{expected_release_url}`"
        )

def commit_final_release_artifact(
    repo_root: Path,
    *,
    adapter_data: dict[str, Any],
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    has_issue_closeout: bool,
) -> None:
    def writer(**kwargs):
        return write_current_artifact(repo_root, adapter_data, payload, **kwargs)

    kwargs = {
        "repo_root": repo_root, "write_artifact": writer, "payload": payload,
        "fresh_checkout_payload": fresh_checkout_payload, "artifact_relpath": artifact_relpath,
        "expected_release_url": expected_release_url, "remote": remote, "branch": branch,
    }
    if has_issue_closeout:
        commit_issue_closeout_artifact(**kwargs, run=run)
    else:
        commit_post_publish_artifact(**kwargs, run_command=run)


def _valid_adapter_data(repo_root: Path) -> dict[str, Any]:
    """The one place an invalid release adapter stops a run, for every entrypoint."""
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    return adapter["data"]


def _load_adapter_and_gate(
    args: argparse.Namespace, repo_root: Path
) -> tuple[dict[str, Any], str | None, dict[str, Any]]:
    """Returns the gate REPORT too: discarded here, a presence-only publish left
    no durable record at an irreversible boundary."""
    adapter_data = _valid_adapter_data(repo_root)
    validate_bump_rationale_arg(args.bump_rationale)
    critique_artifact = validate_critique_artifact_arg(repo_root, args.critique_artifact, run_command=run)
    critique_gate = enforce_release_critique_gate(
        repo_root,
        critique_artifact=critique_artifact,
        critique_blocked=args.critique_blocked,
        # Resolved here, not left to the plan: the gate runs BEFORE
        # `build_publish_plan`, and a gate that cannot name its release cannot
        # bind to it.
        target_version=gate_target_version(repo_root, args),
    )
    return adapter_data, critique_artifact, critique_gate


def run_prep_update_instructions(args: argparse.Namespace, repo_root: Path) -> None:
    """Pre-publish, pre-critique affordance: emit version-agnostic
    `update_instructions` guidance + staleness report so the maintainer repairs
    the adapter before the release critique, pre-empting the adapter HOLD.
    Read-only: it loads the adapter, computes the target/previous versions the
    real publish would use, and prints the prep payload without requiring a clean
    worktree or the critique gate.
    """
    adapter_data = _valid_adapter_data(repo_root)
    current_payload = build_release_payload(repo_root)
    current_version = current_payload["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    next_version = release_plan_target_version(args, current_version)
    previous_version = release_previous_version(
        repo_root, args.publish_current, current_version, next_version, args.remote
    )
    prep = build_update_instructions_prep_payload(
        package_id=adapter_data["package_id"],
        current_version=current_version,
        target_version=next_version,
        previous_version=previous_version,
        update_instructions=adapter_data.get("update_instructions"),
    )
    emit_yaml(prep)


def execute_publish_plan(
    args: argparse.Namespace, repo_root: Path, plan: dict[str, Any], adapter_data: dict[str, Any]
) -> None:
    _execute.execute_publish_plan(args, repo_root, plan, adapter_data, cli=_execution_context())


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if args.prep_update_instructions:
        if args.execute or args.resume:
            raise SystemExit(
                "--prep-update-instructions is a read-only pre-publish affordance; "
                "do not combine it with --execute or --resume"
            )
        run_prep_update_instructions(args, repo_root)
        return
    if args.resume and not args.publish_current:
        raise SystemExit("--resume requires --publish-current (the manifest is already at the target version)")
    if args.claims_review_artifact and not args.resume:
        raise SystemExit("--claims-review-artifact is only valid with --resume --publish-current")
    adapter_data, critique_artifact, critique_gate = _load_adapter_and_gate(args, repo_root)
    status = git_status(repo_root)
    if status:
        raise SystemExit("publish_release requires a clean worktree before it starts.\n" + "\n".join(status))

    if args.execute and not args.resume:
        # Here rather than inside the prepare, so the refusal precedes every mutation AND
        # the plan build's remote reads, and so it stays a gate refusal instead of a
        # release-attempt failure payload. Its reasoning lives with the function.
        _execute.assert_no_outstanding_prepared_stop(repo_root, adapter_data=adapter_data, run=run)

    resume_state = (
        preflight_resume_state(repo_root, args=args, adapter_data=adapter_data, cli=_execution_context())
        if args.resume
        else None
    )
    plan = build_publish_plan(args, repo_root, adapter_data, critique_artifact, run_command=run, resume=args.resume)
    plan["payload"]["critique_gate"] = {
        "binding_checked": critique_gate.get("binding_checked", False),
        "binding_tokens": critique_gate.get("binding_tokens", []),
    }
    try:
        if args.resume:
            resume_publish(
                repo_root,
                args=args,
                plan=plan,
                adapter_data=adapter_data,
                cli=_execution_context(),
                state=resume_state,
            )
            return
        if not args.execute:
            emit_yaml(plan["payload"])
            return
        execute_publish_plan(args, repo_root, plan, adapter_data)
    except BaseException as exc:
        _release_runtime.print_failure_payload(plan["payload"], exc, repo_root=repo_root)
        raise
