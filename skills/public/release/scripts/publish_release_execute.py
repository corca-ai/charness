from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from typing import Any

# Same reach as the sibling `publish_release_runtime.py`: this module is always
# loaded through the publish CLI, which has already put the tree root on sys.path.
from scripts.yaml_output import emit_yaml

_common = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_common.py")))
_rollback = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_rollback.py")))
_claims_review = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_claims_review.py")))


def assert_no_outstanding_prepared_stop(repo_root: Path, *, adapter_data: dict[str, Any], run: Any) -> None:
    """Refuse a fresh prepare while HEAD still carries a prepared claims-review stop.

    The stop below is only an IMMUTABLE record for the claims reviewer if a second prepare
    cannot be started on top of it, and re-running the same `--execute` is the likeliest
    action at a stop: the stop exists to surface record blockers, and the command that
    produced it is the one in the operator's shell history.

    Unguarded, that second prepare SUCCEEDS. It bumps another version, re-runs the release
    quality gates and the fresh-checkout probes, and commits a second marked record whose
    parent already carries the marker -- after which `prepared_record` declines (no
    single-parent boundary), `assert_resumable`'s `marker_at_head` branch refuses the
    resume, and the only recovery that branch can name is a reset back to one prepared
    record. On top of a committed claims review that reset discards the review; on top of a
    stop whose tag already reached the remote it would rewrite history behind it. Refusing
    here costs one message instead.

    Keyed on the marker being PRESENT at HEAD, not on `prepared_record`: the marker is
    inherited by descendants, so it is still there at the claims-evidence commit R, which
    is exactly where a mistaken `--execute` (instead of `--resume`) is most destructive and
    where a prepared-boundary test would wave the prepare through.

    Publication rewrites the release record without the marker, so a finished release does
    not latch this refusal -- asserted by a test that prepares again after a full publish,
    because if that ever stopped holding the repo could never cut another release. A repo
    with no release record yet reads as "no marker": that is a first release, not a stop.

    Known residuals, stated rather than half-repaired. The path is derived from the CURRENT
    adapter, so an `output_dir` edited at the stop (an ordinary action there) reads as no
    marker, and a gitignored release output directory reads the same way. Neither can be
    closed by refusing an unreadable record the way the resume lane does: a first release
    legitimately has none.
    """
    record_path = _claims_review["release_record_path"](adapter_data)
    if not _claims_review["marker_at_commit"](repo_root, commit="HEAD", record_path=record_path, run=run):
        return
    # The abandon exit is NOT stated unconditionally, and the resume lane is why: its
    # sibling refusal splits the same advice on publication state, because a publish whose
    # closeout tail failed leaves the marker at HEAD with the tag pushed and the release
    # created. "Reset" there rewrites history behind a published tag and discards the
    # claims record. This gate is deliberately cheap (one `git show`, no remote reads), so
    # it names the condition for the operator instead of spending a `git ls-remote` here.
    raise SystemExit(
        f"publish_release: HEAD's release record `{record_path}` still carries "
        f"`{_claims_review['MARKER']}`, so a prepared claims-review stop is outstanding and a "
        "second prepare would destroy the boundary the claims review binds to.\n"
        "  publish it: --resume --publish-current --claims-review-artifact <record> (run "
        "plan_release_run.py --repo-root . for the exact invocation). This is the ONLY safe exit "
        "once the stop's tag has reached the remote -- a resume republishes idempotently.\n"
        "  abandon it: only while nothing has been published (check `git ls-remote --tags` for this "
        "record's tag, and the remote branch), reset to the commit before the prepared release "
        "record, then prepare again. That reset discards EVERY commit on top of the stop -- a "
        "committed claims review and any blocker fix included; rebase or cherry-pick them off "
        "first, and expect a force-push if the branch was already pushed."
    )


def _prepare_release_attempt(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    payload = plan["payload"]
    next_version = plan["next_version"]
    tag_name = plan["tag_name"]
    backend = plan["backend"]
    adapter_preflight_payload = plan["adapter_preflight_payload"]
    issue_repo = plan["issue_repo"]

    notes_file = args.notes_file.resolve() if args.notes_file else None
    cli.run_notes_file_preflight(
        repo_root,
        target_tag=tag_name,
        notes_file=notes_file,
        previous_version=plan["payload"].get("previous_version"),
    )

    cli.run(cli.backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    expected_release_url = cli.expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    _common["preflight_close_issue_carrier"](
        repo_root, args=args, issue_repo=issue_repo, payload=payload, cli=cli,
        carrier_source="publish-execute",
    )
    cli.run_release_adapter_preflight(repo_root, adapter_preflight_payload, run_command=cli.run)
    cli.run_bump(args, repo_root)
    payload["version_drift_check"] = cli.ensure_release_surface(
        repo_root, next_version, stage="post-bump, pre-commit"
    )

    fresh_checkout_plan = cli.build_fresh_checkout_payload(repo_root, run_probes=False)
    cli.write_current_artifact(
        repo_root,
        adapter_data,
        payload,
        release_url=expected_release_url,
        quality_status="is queued for this publish attempt",
        fresh_checkout_payload=fresh_checkout_plan,
        release_stage="charness-release-state:prepared-awaiting-claims-review",
    )
    _common["run_pre_push_quality_gates"](
        repo_root, adapter_data, payload, cli=cli, stage="post-bump, pre-commit"
    )
    return {
        "payload": payload,
        "branch": plan["branch"],
        "tag_name": tag_name,
        "title": plan["title"],
        "backend": backend,
        "issue_repo": issue_repo,
        "notes_file": notes_file,
        "expected_release_url": expected_release_url,
        "fresh_checkout_plan": fresh_checkout_plan,
    }


def _commit_release_artifact(
    args: argparse.Namespace,
    repo_root: Path,
    state: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    payload = state["payload"]
    tag_name = state["tag_name"]
    notes_file = state["notes_file"]
    expected_release_url = state["expected_release_url"]
    fresh_checkout_plan = state["fresh_checkout_plan"]

    artifact_relpath = cli.write_current_artifact(
        repo_root,
        adapter_data,
        payload,
        fresh_checkout_payload=fresh_checkout_plan,
        release_url=expected_release_url,
        release_stage="charness-release-state:prepared-awaiting-claims-review",
    )
    cli.run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    cli.run(["git", "add", "-A"], cwd=repo_root)
    commit_command = ["git", "commit", "-m", payload["commit_message"]]
    # The validated issue-close paragraphs are reserved for the post-observer
    # carrier commit. The first default-branch push must not auto-close issues.
    cli.run(commit_command, cwd=repo_root)
    fresh_checkout_payload = _common["timed"](
        payload, "fresh_checkout_probes_initial", lambda: cli.run_fresh_checkout_probes(repo_root)
    )
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    if fresh_checkout_payload["status"] == "passed":
        cli.amend_fresh_checkout_artifact(
            repo_root,
            write_artifact=lambda **kwargs: cli.write_current_artifact(
                repo_root,
                adapter_data,
                payload,
                release_stage="charness-release-state:prepared-awaiting-claims-review",
                **kwargs,
            ),
            fresh_checkout_payload=fresh_checkout_payload,
            release_url=expected_release_url,
            artifact_relpath=artifact_relpath,
            tag_name=tag_name,
            notes_file=notes_file,
            run_narrative_audit=cli.run_narrative_audit,
            run_command=cli.run,
        )
        fresh_checkout_payload = _common["timed"](
            payload, "fresh_checkout_probes_after_amend", lambda: cli.run_fresh_checkout_probes(repo_root)
        )
        payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    state["fresh_checkout_payload"] = fresh_checkout_payload
    state["artifact_relpath"] = artifact_relpath
    return state


def _create_release_commit(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> dict[str, Any]:
    snapshot = _rollback["snapshot_clean_head"](repo_root, run_command=cli.run)
    try:
        state = _prepare_release_attempt(args, repo_root, plan, adapter_data, cli=cli)
        return _commit_release_artifact(args, repo_root, state, adapter_data, cli=cli)
    except BaseException:
        plan["payload"]["precommit_rollback"] = _rollback["rollback_precommit_changes"](
            repo_root,
            snapshot,
            tag_name=plan["tag_name"],
            run_command=cli.run,
        )
        raise



def execute_publish_plan(
    args: argparse.Namespace,
    repo_root: Path,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    *,
    cli: Any,
) -> None:
    state = _create_release_commit(args, repo_root, plan, adapter_data, cli=cli)
    payload = state["payload"]
    payload["release_stage"] = "prepared-awaiting-claims-review"
    payload["prepared_release_commit"] = cli.run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    payload["next_action"] = "commit a bound claims-review artifact, then resume publication"
    emit_yaml(payload)
