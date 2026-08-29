"""Identity-checked recovery for post-publication issue-closeout commits."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Same reach as the sibling `publish_release_runtime.py`: this module is always
# loaded through the publish CLI, which has already put the tree root on sys.path.
# `json` stays for the release-observer ARTIFACT read below -- that file is stored
# JSON and is not this command's stdout.
from scripts.yaml_output import emit_yaml


def _require_closeout_resume_inputs(args: Any) -> None:
    """Refuse to infer irreversible issue-close context from commit text."""
    required = {
        "--close-issue": bool(args.close_issue),
        "--close-issue-classification": bool(args.close_issue_classification),
        "--close-issue-carrier-file": bool(args.close_issue_carrier_file),
        "--close-issue-behavior": bool(args.close_issue_behavior),
    }
    missing = [flag for flag, present in required.items() if not present]
    if not missing:
        return
    raise SystemExit(
        "--resume: post-publication issue-closeout recovery requires the original "
        "closeout inputs; missing " + ", ".join(missing) + ". Re-run with "
        "--resume --publish-current plus the exact original --close-issue, "
        "--close-issue-classification, --close-issue-carrier-file, and "
        "--close-issue-behavior flags, plus --close-issue-probe-record where the behavioral verdict "
        "claims a verification (and --close-issue-repo when it was explicit). "
        "Recovery never infers or omits issue-close context."
    )


def _commit_file(repo_root: Path, *, commit_ref: str, path: str, cli: Any) -> str:
    result = cli.run(["git", "show", f"{commit_ref}:{path}"], cwd=repo_root, check=False)
    if result.returncode != 0:
        raise SystemExit(f"--resume: `{commit_ref}` does not contain required evidence `{path}`")
    return result.stdout


def _validate_carrier_evidence_tree(
    repo_root: Path,
    *,
    commit_ref: str,
    artifact_relpath: str,
    tag_name: str,
    payload: dict[str, Any],
    cli: Any,
) -> None:
    changed = cli.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_ref],
        cwd=repo_root,
    ).stdout.splitlines()
    observer_suffix = f"-{tag_name}-release-observer.json"
    observers = [
        path for path in changed
        if path.startswith("charness-artifacts/probe/") and path.endswith(observer_suffix)
    ]
    if artifact_relpath not in changed or len(observers) != 1:
        raise SystemExit(
            "--resume: carrier evidence tree must change the release artifact and exactly one release observer"
        )
    observer_path = observers[0]
    artifact = _commit_file(repo_root, commit_ref=commit_ref, path=artifact_relpath, cli=cli)
    observer = json.loads(_commit_file(repo_root, commit_ref=commit_ref, path=observer_path, cli=cli))
    cli.validate_release_observer_record(observer)
    if observer.get("target", {}).get("tag") != tag_name:
        raise SystemExit("--resume: carrier observer targets a different release tag")
    if observer_path not in artifact or "carrier-pending-state-verification" not in artifact:
        raise SystemExit("--resume: carrier artifact does not bind its observer and pending closeout state")
    payload["resume_carrier_evidence"] = {
        "status": "validated",
        "artifact_path": artifact_relpath,
        "observer_path": observer_path,
    }


def _validate_final_evidence_tree(
    repo_root: Path, *, commit_ref: str, artifact_relpath: str, payload: dict[str, Any], cli: Any
) -> None:
    changed = cli.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_ref],
        cwd=repo_root,
    ).stdout.splitlines()
    artifact = _commit_file(repo_root, commit_ref=commit_ref, path=artifact_relpath, cli=cli)
    if artifact_relpath not in changed or "Issue closeout verification: `state-verified`" not in artifact:
        raise SystemExit("--resume: final closeout commit lacks its state-verified release artifact")
    payload["resume_final_evidence"] = {"status": "validated", "artifact_path": artifact_relpath}


def _validated_carrier_message(
    repo_root: Path,
    *,
    args: Any,
    issue_repo: str,
    payload: dict[str, Any],
    commit_message: str,
    commit_ref: str,
    artifact_relpath: str,
    tag_name: str,
    cli: Any,
) -> None:
    validation = cli.validate_release_closeout_commit_message(
        repo_root,
        repo=issue_repo,
        issue_numbers=args.close_issue,
        classification=args.close_issue_classification,
        commit_message=commit_message,
        commit_ref=commit_ref,
    )
    payload["resume_carrier_validation"] = validation
    expected = str(payload["issue_closeout_draft_validation"].get("commit_message", "")).strip()
    exact = commit_message.strip() == expected
    payload["resume_carrier_validation"]["matches_preflight_draft"] = exact
    if not validation["ok"] or not exact:
        raise SystemExit(
            "--resume: post-publication carrier does not exactly match the newly validated closeout draft"
        )
    _validate_carrier_evidence_tree(
        repo_root,
        commit_ref=commit_ref,
        artifact_relpath=artifact_relpath,
        tag_name=tag_name,
        payload=payload,
        cli=cli,
    )


def _reconcile_push(
    repo_root: Path,
    *,
    state: dict[str, Any],
    remote: str,
    branch: str,
    payload: dict[str, Any],
    cli: Any,
) -> None:
    if state["remote_branch_sha"] == state["head_sha"]:
        payload["resume_remote_reconcile"] = {"status": "already-shared", "sha": state["head_sha"]}
        return
    try:
        cli.run(["git", "push", remote, branch], cwd=repo_root)
        status = "pushed"
    except BaseException:
        result = cli.run(
            ["git", "ls-remote", "--heads", remote, f"refs/heads/{branch}"],
            cwd=repo_root,
            check=False,
        )
        remote_sha = result.stdout.split(maxsplit=1)[0] if result.returncode == 0 and result.stdout.strip() else ""
        if remote_sha != state["head_sha"]:
            raise
        status = "push-error-but-shared"
    payload["resume_remote_reconcile"] = {"status": status, "sha": state["head_sha"]}


def resume_post_publication_closeout(
    repo_root: Path,
    *,
    args: Any,
    plan: dict[str, Any],
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    common: Any,
    cli: Any,
) -> None:
    payload = plan["payload"]
    issue_repo = plan["issue_repo"]
    # The path the state was CLASSIFIED against, not a second derivation of it. The local
    # `Path(adapter_data["output_dir"]) / "latest.md"` that used to sit here differed from
    # the floor's `PurePosixPath` derivation on a platform whose separator is not `/`, where
    # it produced backslashes while `git diff-tree --name-only` emits forward slashes --
    # failing `_validate_carrier_evidence_tree` on a legitimate recovery. Two derivations of
    # one path is the defect class this slice exists to close.
    artifact_relpath = state["record_path"]
    _require_closeout_resume_inputs(args)
    common.preflight_close_issue_carrier(
        repo_root, args=args, issue_repo=issue_repo, payload=payload, cli=cli,
        carrier_source="release-resume-closeout",
    )
    carrier_message = state["head_message"]
    carrier_ref = "HEAD"
    final_phase = state["phase"] in {"post-publication-final", "post-publication-claims-final"}
    if final_phase:
        carrier_message = state["parent_message"]
        carrier_ref = "HEAD^"
    _validated_carrier_message(
        repo_root,
        args=args,
        issue_repo=issue_repo,
        payload=payload,
        commit_message=carrier_message,
        commit_ref=carrier_ref,
        artifact_relpath=artifact_relpath,
        tag_name=plan["tag_name"],
        cli=cli,
    )
    if final_phase:
        _validate_final_evidence_tree(
            repo_root,
            commit_ref="HEAD",
            artifact_relpath=artifact_relpath,
            payload=payload,
            cli=cli,
        )
    payload["resume_state"] = state
    if not args.execute:
        payload["resume"] = f"dry-run: would reconcile {state['phase']} against the remote branch"
        emit_yaml(payload)
        return

    _reconcile_push(
        repo_root,
        state=state,
        remote=args.remote,
        branch=plan["branch"],
        payload=payload,
        cli=cli,
    )
    if final_phase:
        payload["resume"] = "final closeout artifact commit reconciled"
        emit_yaml(payload)
        return

    expected_url = cli.expected_github_release_url(
        repo_root, plan["backend"], plan["tag_name"]
    )
    fresh_checkout_payload = cli.run_fresh_checkout_probes(repo_root)
    verify = cli.verify_release_visible(
        repo_root,
        plan["tag_name"],
        plan["backend"],
        backend_command=cli.backend_command,
        run=cli.run,
    )
    # The TAGGED commit, on the lane that posts the comments. This is the sibling
    # caller of `finalize_release_payload`, and the repair that stopped HEAD being
    # reported as the released commit was applied only to the other one -- so this
    # recovery lane, which is exactly where an operator lands after a failed close,
    # still told every closed issue a commit `v<tag>` does not point at. On the claims
    # phases the classifier binds `state["prepared"]` to the TAGGED prepared record.
    claims_phase = state.get("phase") in {
        "post-publication-claims-carrier",
        "post-publication-claims-final",
    }
    cli.finalize_release_payload(
        repo_root,
        payload,
        artifact_relpath=artifact_relpath,
        release_stdout=expected_url or "",
        expected_release_url=expected_url,
        release_verified=verify.returncode == 0,
        commit_sha=(state.get("prepared") or {}).get("commit") if claims_phase else None,
    )
    payload["issue_closeout_carrier_commit_sha"] = state["head_sha"]
    tail_state = {
        "artifact_relpath": artifact_relpath,
        "backend": plan["backend"],
        "branch": plan["branch"],
        "expected_release_url": expected_url,
        "fresh_checkout_payload": fresh_checkout_payload,
        "tag_name": plan["tag_name"],
    }
    common.run_release_closeout_tail(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=tail_state,
        issue_repo=issue_repo,
        payload=payload,
        cli=cli,
        carrier_already_committed=True,
        carrier_source="release-resume-closeout",
    )
    emit_yaml(payload)
