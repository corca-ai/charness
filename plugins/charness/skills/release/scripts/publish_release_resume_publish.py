"""Publication tail for an already-classified release-resume state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CLAIMS_PHASES = {
    "prepared-claims-review",
    "post-publication-claims-carrier",
    "post-publication-claims-final",
}
POST_PUBLICATION = {
    "post-publication-carrier", "post-publication-final",
    "post-publication-claims-carrier", "post-publication-claims-final",
}


def resume_publish(repo_root: Path, *, args: Any, plan: dict[str, Any], adapter_data: dict[str, Any], cli: Any,
                   state: dict[str, Any] | None, resumable_state, assert_resumable, common: Any,
                   resume_closeout: Any, commit_artifact_before_push) -> None:
    payload, tag_name, branch, backend = plan["payload"], plan["tag_name"], plan["branch"], plan["backend"]
    state = state or resumable_state(repo_root, tag_name=tag_name, commit_message=payload["commit_message"],
                                     remote=args.remote, branch=branch, backend=backend, cli=cli)
    assert_resumable(state, tag_name=tag_name)
    # The claims floor lives in `preflight_resume_state`, a DIFFERENT function. A
    # reconstructed state (the `state or ...` fallback above) can resolve to a claims
    # phase, pass `assert_resumable`, carry no `claims_review`, and reach tag/push/release
    # create -- the exact "publishing path that never calls validate_claims_review" shape
    # this lane was repaired for, preserved one caller away. No production caller does
    # this today; the assertion is what keeps that true.
    if state["phase"] in CLAIMS_PHASES and not state.get("claims_review"):
        raise SystemExit(
            f"--resume: phase `{state['phase']}` requires a validated claims review and this "
            "state carries none; refusing to publish through an unvalidated path."
        )
    payload["resume_state"] = state
    # Top-level, not only nested inside `resume_state`: the claims verdict is the
    # strongest floor this lane applies, and the published release record does not carry
    # it (tracked separately), so the payload is where an auditor has to be able to find
    # it without knowing the resume state's shape.
    if state.get("claims_review"):
        payload["claims_review"] = {
            "path": state["claims_review"]["path"],
            "verdict": state["claims_review"]["verdict"],
            "observer_distinctness": state["claims_review"]["observer_distinctness"],
        }
    if state["phase"] in POST_PUBLICATION:
        resume_closeout.resume_post_publication_closeout(repo_root, args=args, plan=plan, adapter_data=adapter_data,
                                                          state=state, common=common, cli=cli)
        return
    claims_lane = state["phase"] == "prepared-claims-review"
    if not args.execute:
        payload["resume"] = "dry-run: would re-validate gates, create missing refs, then publish the existing release commit"
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    notes_file = args.notes_file.resolve() if args.notes_file else None
    cli.run(cli.backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    common.preflight_close_issue_carrier(repo_root, args=args, issue_repo=plan["issue_repo"], payload=payload, cli=cli,
                                         carrier_source="release-resume")
    if args.close_issue:
        close_refs = cli.release_content_close_keyword_refs(cli.run(["git", "show", "-s", "--format=%B", "HEAD"], cwd=repo_root).stdout)
        payload["resume_head_release_content_close_refs"] = close_refs
        if close_refs:
            raise SystemExit("--resume: release-content HEAD contains issue close keywords before post-publication observer evidence: " + str(close_refs))
    common.run_pre_push_quality_gates(repo_root, adapter_data, payload, cli=cli)
    fresh = common.timed(payload, "fresh_checkout_probes_resume", lambda: cli.run_fresh_checkout_probes(repo_root))
    payload["fresh_checkout_probe_status"] = fresh["status"]
    expected_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_url
    host = cli.safe_real_host_payload(repo_root, plan["release_content_paths"], build_payload=cli.build_real_host_payload)
    payload["retro_trigger_evaluation"] = cli.build_retro_trigger_evaluation(
        repo_root, plan["release_content_paths"], evaluated_at="final_release_paths", tag_name=tag_name, execute=True)
    artifact = "charness-artifacts/release/latest.md"
    if not claims_lane:
        artifact = cli.write_current_artifact(repo_root, adapter_data, payload, host, fresh_checkout_payload=fresh, release_url=expected_url)
        cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    # The claims record stays the exact P -> R direct child.  Revalidation can
    # still refresh generated quality inventory beneath charness-artifacts;
    # commit that follow-on evidence before the pre-push hook observes a dirty
    # worktree.  The tag remains anchored at P and the state retains R as the
    # bound review identity.
    commit_artifact_before_push(repo_root, cli=cli, tag_name=tag_name)

    def publish() -> tuple[str, Any]:
        if not state["tag_local"]:
            cli.run(["git", "tag", tag_name, state["prepared"]["commit"] if claims_lane else state["head_sha"]], cwd=repo_root)
        branch_needed = state["remote_branch_sha"] != (state.get("claims_evidence_commit") or state["head_sha"])
        tag_needed = not state["tag_remote"]
        if branch_needed and tag_needed:
            cli.run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)
        elif branch_needed:
            cli.run(["git", "push", args.remote, branch], cwd=repo_root)
        elif tag_needed:
            cli.run(["git", "push", args.remote, tag_name], cwd=repo_root)
        output = (
            expected_url or "" if state["release_exists"]
            else cli.create_release(repo_root, backend, tag_name=tag_name, title=plan["title"], notes_file=notes_file).stdout
        )
        return output, cli.verify_release_visible(repo_root, tag_name, backend, backend_command=cli.backend_command, run=cli.run)

    release_stdout, verified = common.timed(payload, "push_create_verify_release", publish)
    cli.finalize_release_payload(repo_root, payload, artifact_relpath=artifact, host_payload=host, release_stdout=release_stdout,
                                 expected_release_url=expected_url, release_verified=verified.returncode == 0)
    if verified.returncode != 0:
        cli.commit_final_release_artifact(repo_root, adapter_data=adapter_data, payload=payload, host_payload=host,
                                          fresh_checkout_payload=fresh, artifact_relpath=artifact, expected_release_url=expected_url,
                                          remote=args.remote, branch=branch, has_issue_closeout=False)
        cli.fail_after_post_create_verification(payload, verification_result=verified)
    state.update({"artifact_relpath": artifact, "backend": backend, "branch": branch, "expected_release_url": expected_url,
                  "fresh_checkout_payload": fresh, "host_payload": host, "tag_name": tag_name})
    common.run_release_closeout_tail(repo_root, args=args, adapter_data=adapter_data, state=state, issue_repo=plan["issue_repo"],
                                     payload=payload, cli=cli, carrier_source="release-resume")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
