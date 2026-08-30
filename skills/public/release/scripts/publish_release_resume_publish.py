"""Publication tail for an already-classified release-resume state."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from scripts.yaml_output import emit_yaml

# Mirrors the claims-lane phase set owned by `publish_release_claims_review`; this
# module is loaded by `runpy` from the resume helper and does not import it.
_CLAIMS_PHASES = frozenset({
    "prepared-claims-review",
    "post-publication-claims-carrier",
    "post-publication-claims-final",
})

POST_PUBLICATION = {
    "post-publication-carrier", "post-publication-final",
    "post-publication-claims-carrier", "post-publication-claims-final",
}


def _assert_one_record_path(state: dict[str, Any], record_path: str) -> None:
    """Refuse a state classified against a different release record than this run derives.

    The state was classified against ONE record path; everything after it writes, commits,
    and reports against the path derived from the adapter. Production always passes a
    preflighted state, so these agree -- and that is exactly the kind of invariant that
    holds until a second caller appears.
    """
    if state.get("record_path") != record_path:
        raise SystemExit(
            f"--resume: this state was classified against release record {state.get('record_path')!r} "
            f"but the adapter now derives {record_path!r}; refusing to publish across two record paths."
        )


def _notes_preflight(
    repo_root: Path, *, cli: Any, state: dict[str, Any], tag_name: str, notes_file,
    previous_version: str | None = None,
) -> None:
    """The drafted-notes refusal, on the lane that actually publishes.

    A floor that fires at PREPARE time does not fire at the boundary that publishes. The
    prepare refuses a tag with drafted notes and no `--notes-file`, but it now always stops
    at the marked record, so this lane is the only path to `create_release` -- and it ran no
    notes preflight at all. A resume that dropped the flag published `--generate-notes`
    instead of the notes the prepare validated, with nothing refusing it.

    Called on BOTH lanes: `run_narrative_audit` (non-claims lane only) is a strict superset
    over the same helpers, so a duplicate call cannot disagree with it, and on that lane
    this moves the refusal ahead of the pre-push quality gates and the fresh-checkout
    probes, which is the preflight's own stated reason for existing.

    Skipped once the release exists: that resume is repairing a missing branch or tag push
    and cannot attach a body at all, so the blocker's premise ("the published body would be
    auto-generated") is false and its refusal would be a wrong stop.
    """
    if state["release_exists"]:
        return
    cli.run_notes_file_preflight(
        repo_root,
        target_tag=tag_name,
        notes_file=notes_file,
        on_resume=True,
        previous_version=previous_version,
    )


def _run_push_with_receipt(
    cli: Any,
    repo_root: Path,
    receipt_path: Path | None,
    command: list[str],
) -> None:
    """Expose the one-push receipt to the child command, then restore the host."""
    previous = os.environ.get("CHARNESS_PREPUSH_QUALITY_RECEIPT")
    if receipt_path is not None:
        os.environ["CHARNESS_PREPUSH_QUALITY_RECEIPT"] = str(receipt_path)
    try:
        cli.run(command, cwd=repo_root)
    finally:
        if previous is None:
            os.environ.pop("CHARNESS_PREPUSH_QUALITY_RECEIPT", None)
        else:
            os.environ["CHARNESS_PREPUSH_QUALITY_RECEIPT"] = previous


def resume_publish(repo_root: Path, *, args: Any, plan: dict[str, Any], adapter_data: dict[str, Any], cli: Any,
                   state: dict[str, Any] | None, resumable_state, assert_resumable, common: Any,
                   resume_closeout: Any, commit_artifact_before_push, release_record_path) -> None:
    payload, tag_name, branch, backend = plan["payload"], plan["tag_name"], plan["branch"], plan["backend"]
    record_path = release_record_path(adapter_data)
    state = state or resumable_state(repo_root, tag_name=tag_name, commit_message=payload["commit_message"],
                                     remote=args.remote, branch=branch, backend=backend,
                                     record_path=record_path, cli=cli)
    assert_resumable(state, tag_name=tag_name)
    _assert_one_record_path(state, record_path)
    # The claims floor lives in `preflight_resume_state`, a DIFFERENT function. A
    # reconstructed state (the `state or ...` fallback above) can resolve to a claims
    # phase, pass `assert_resumable`, carry no `claims_review`, and reach tag/push/release
    # create -- the exact "publishing path that never calls validate_claims_review" shape
    # this lane was repaired for, preserved one caller away. No production caller does
    # this today; the assertion is what keeps that true.
    if state["phase"] in _CLAIMS_PHASES and not state.get("claims_review"):
        raise SystemExit(
            f"--resume: phase `{state['phase']}` requires a validated claims review and this "
            "state carries none; refusing to publish through an unvalidated path."
        )
    payload["resume_state"] = state
    # Top-level, not only nested inside `resume_state`: the claims verdict is the strongest
    # floor this lane applies, and an auditor has to be able to find it without knowing the
    # resume state's shape. This is also what the artifact writer reads to emit the record's
    # `## Claims Review` section, so every artifact write below this line carries the
    # verdict and every write above it would not -- which is why it is here rather than
    # near the writes.
    if state.get("claims_review"):
        payload["claims_review"] = {
            "path": state["claims_review"]["path"],
            "verdict": state["claims_review"]["verdict"],
            "observer_distinctness": state["claims_review"]["observer_distinctness"],
            # Carried into the RECORD, not just validated. The scope split
            # publishes narrative defects as known-inaccurate instead of
            # repairing them into a new prepared commit -- so a record that says
            # `verdict: pass` and nothing else hides exactly what the split
            # waived. A fresh-eye round found these validated and then dropped
            # here, which made the "published as known-inaccurate" design intent
            # untrue at the one surface outside readers actually get.
            "review_scope": state["claims_review"].get("review_scope"),
            "advisory_findings": state["claims_review"].get("advisory_findings") or [],
        }
    if state["phase"] in POST_PUBLICATION:
        resume_closeout.resume_post_publication_closeout(repo_root, args=args, plan=plan, adapter_data=adapter_data,
                                                          state=state, common=common, cli=cli)
        return
    claims_lane = state["phase"] == "prepared-claims-review"
    notes_arg = getattr(args, "notes_file", None)
    notes_file = notes_arg.resolve() if notes_arg else None
    # Above the dry-run return, so the planner's own dry-run packet validates the argument
    # its `repeat_original_arguments` field warns about instead of only advising it.
    _notes_preflight(
        repo_root, cli=cli, state=state, tag_name=tag_name, notes_file=notes_file,
        previous_version=payload.get("previous_version"),
    )
    if not args.execute:
        payload["resume"] = "dry-run: would re-validate gates, create missing refs, then publish the existing release commit"
        emit_yaml(payload)
        return
    cli.run(cli.backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    common.preflight_close_issue_carrier(repo_root, args=args, issue_repo=plan["issue_repo"], payload=payload, cli=cli,
                                         carrier_source="release-resume")
    if args.close_issue:
        close_refs = cli.release_content_close_keyword_refs(cli.run(["git", "show", "-s", "--format=%B", "HEAD"], cwd=repo_root).stdout)
        payload["resume_head_release_content_close_refs"] = close_refs
        if close_refs:
            raise SystemExit("--resume: release-content HEAD contains issue close keywords before post-publication observer evidence: " + str(close_refs))
    # The prepared record is a stop, not a permanent assertion about the generated
    # surface. A maintainer can delete or corrupt a required manifest between the
    # claims review and this resume, so re-read the target surface immediately before
    # the gates and carry the disposition into the final release artifact.
    target_version = payload.get("target_version") or tag_name.removeprefix("v")
    payload["version_drift_check"] = cli.ensure_release_surface(
        repo_root, target_version, stage="post-claims-review, pre-push"
    )
    receipt_dir = tempfile.TemporaryDirectory(prefix="charness-prepush-quality-")
    receipt_path: Path | None = Path(receipt_dir.name) / "receipt.json"
    common.run_pre_push_quality_gates(
        repo_root,
        adapter_data,
        payload,
        cli=cli,
        stage="post-claims-review, pre-push",
        prepush_receipt_path=receipt_path,
    )
    fresh = common.timed(payload, "fresh_checkout_probes_resume", lambda: cli.run_fresh_checkout_probes(repo_root))
    payload["fresh_checkout_probe_status"] = fresh["status"]
    expected_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_url
    # Adapter-derived, not a literal: on the claims lane the writer below is SKIPPED, so
    # this value is what reaches `finalize_release_payload`, the post-publish artifact
    # commit, and `state["artifact_relpath"]`. A literal there pointed a consumer's
    # post-publish commit at a pathspec matching nothing -- and `git diff --quiet` over a
    # pathspec that matches nothing exits 0, so that commit was skipped silently.
    artifact = record_path
    if not claims_lane:
        artifact = cli.write_current_artifact(repo_root, adapter_data, payload, fresh_checkout_payload=fresh, release_url=expected_url)
        cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    # The claims record stays the exact P -> R direct child.  Revalidation can
    # still refresh generated quality inventory beneath charness-artifacts;
    # commit that follow-on evidence before the pre-push hook observes a dirty
    # worktree.  The tag remains anchored at P and the state retains R as the
    # bound review identity.
    # The gate, as opposed to the message: the early call is cheap, this one runs after the
    # pre-push gates and the fresh-checkout probes have had their chance to leave a
    # drafted-notes file in the tree. Read-only and silent on pass, so repeating it is free.
    #
    # ABOVE `commit_artifact_before_push`, not below. Below, a gate that FIRES strands the
    # resume it stopped: the commit sweeps the very file the refusal is about into a third
    # commit C on top of the claims evidence R, after which no single-parent prepared
    # boundary is identifiable and the next resume refuses with the marker recovery text --
    # whose advice is to reset past the committed claims record. A gate must not create the
    # state it then refuses.
    _notes_preflight(
        repo_root, cli=cli, state=state, tag_name=tag_name, notes_file=notes_file,
        previous_version=payload.get("previous_version"),
    )
    commit_artifact_before_push(repo_root, cli=cli, tag_name=tag_name, record_path=record_path)

    branch_needed = state["remote_branch_sha"] != (
        state.get("claims_evidence_commit") or state["head_sha"]
    )
    tag_needed = not state["tag_remote"]
    if not receipt_path.is_file():
        receipt_path = None

    def publish() -> tuple[str, Any]:
        if not state["tag_local"]:
            cli.run(["git", "tag", tag_name, state["prepared"]["commit"] if claims_lane else state["head_sha"]], cwd=repo_root)
        if branch_needed and tag_needed:
            _run_push_with_receipt(cli, repo_root, receipt_path, ["git", "push", args.remote, branch, tag_name])
        elif branch_needed:
            _run_push_with_receipt(cli, repo_root, receipt_path, ["git", "push", args.remote, branch])
        elif tag_needed:
            _run_push_with_receipt(cli, repo_root, receipt_path, ["git", "push", args.remote, tag_name])
        output = (
            expected_url or "" if state["release_exists"]
            else cli.create_release(repo_root, backend, tag_name=tag_name, title=plan["title"], notes_file=notes_file).stdout
        )
        return output, cli.verify_release_visible(repo_root, tag_name, backend, backend_command=cli.backend_command, run=cli.run)

    try:
        release_stdout, verified = common.timed(payload, "push_create_verify_release", publish)
    finally:
        receipt_dir.cleanup()
    # The TAGGED commit on the claims lane, not HEAD: `publish` tags
    # `state["prepared"]["commit"]`, while HEAD here is the follow-on evidence commit
    # `commit_artifact_before_push` may have just made. The non-claims lane has no such
    # commit, so `prepared` is HEAD there and the value is unchanged.
    cli.finalize_release_payload(repo_root, payload, artifact_relpath=artifact, release_stdout=release_stdout,
                                 expected_release_url=expected_url, release_verified=verified.returncode == 0,
                                 commit_sha=(state.get("prepared") or {}).get("commit") if claims_lane else None)
    if verified.returncode != 0:
        cli.commit_final_release_artifact(repo_root, adapter_data=adapter_data, payload=payload,
                                          fresh_checkout_payload=fresh, artifact_relpath=artifact, expected_release_url=expected_url,
                                          remote=args.remote, branch=branch, has_issue_closeout=False)
        cli.fail_after_post_create_verification(payload, verification_result=verified)
    state.update({"artifact_relpath": artifact, "backend": backend, "branch": branch, "expected_release_url": expected_url,
                  "fresh_checkout_payload": fresh, "tag_name": tag_name})
    common.run_release_closeout_tail(repo_root, args=args, adapter_data=adapter_data, state=state, issue_repo=plan["issue_repo"],
                                     payload=payload, cli=cli, carrier_source="release-resume")
    emit_yaml(payload)
