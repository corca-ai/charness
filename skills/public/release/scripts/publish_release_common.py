from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_runtime = runpy.run_path(str(Path(__file__).resolve().with_name("publish_release_runtime.py")))


def timed(payload: dict[str, Any], key: str, func):
    return _runtime["timed"](payload, key, func)


def preflight_close_issue_carrier(
    repo_root: Path,
    *,
    args: Any,
    issue_repo: str,
    payload: dict[str, Any],
    cli: Any,
    carrier_source: str = "release",
) -> None:
    """`carrier_source` names WHICH release lane is asking.

    All three lanes funnel through here, so collapsing them to a single "release"
    string meant the authorization record could not tell a first publish from a
    recovery resume — and recovery is the lane an operator reaches for precisely when
    the primary path has already refused them.
    """
    cli.preflight_release_issues(
        repo_root,
        repo=issue_repo,
        issue_numbers=args.close_issue,
        payload=payload,
        run=cli.run,
        carrier_source=carrier_source,
        behavior_lines=args.close_issue_behavior,
        probe_record_lines=args.close_issue_probe_record,
        classification=args.close_issue_classification,
        carrier_file=args.close_issue_carrier_file.resolve() if args.close_issue_carrier_file else None,
    )


def run_pre_push_quality_gates(repo_root: Path, adapter_data: dict[str, Any], payload: dict[str, Any], *, cli: Any, stage: str) -> None:
    payload["requested_review_gate"] = timed(
        payload, "requested_review_gate", lambda: cli.run_requested_review_gate(repo_root)
    )
    timed(payload, "cli_skill_surface_gate", lambda: cli.run_cli_skill_surface_gate(repo_root, adapter_data))
    # `run_phase`, NOT `run_shell`: this is the longest child in the whole publish
    # (the repo's standing quality runner, bounded at 1800s) and the one an operator
    # actually waits on. `run_shell` buffers it, so a runner that streams its own
    # per-check lifecycle produced pure silence until it exited -- indistinguishable
    # from a hang, at the exact moment the operator is deciding whether to abort a
    # publish. The body stays isolated; only the lifecycle reaches stderr.
    timed(
        payload,
        "quality_command",
        lambda: cli.run_phase(str(adapter_data["quality_command"]), cwd=repo_root, phase="quality_command"),
    )
    # STAMP THE RESULT, do not let the record render a default literal.
    #
    # `run_phase` raises on a non-zero exit, so reaching this line means the gate
    # exited 0 -- but the RECORD said so from a hardcoded default
    # (`publish_release_artifact.write_current_artifact`'s
    # `quality_status="passed before publish"`), which renders identically whether
    # the gate ran, did not run, or was skipped. That is the exact defect
    # `version_drift_lines` was already repaired for, on the line directly beneath
    # it: "the record read `current_release.py reported no version drift`
    # identically whether the check ran, did not run, or found drift."
    #
    # A claims round caught the survivor. Now the sentence carries the command, the
    # stage it ran at, and the measured elapsed time, so a reader can tell a real
    # pass from a template.
    #
    # `stage` is a REQUIRED argument, not a default. It was a hardcoded
    # `post-bump, pre-commit` literal, which is true on the prepare lane and FALSE
    # on the resume/claims lane -- that lane runs this gate again after the
    # prepared commit already exists and without bumping anything, and its payload
    # is what `commit_post_publish_artifact` rewrites and pushes to `main`. So the
    # sentence written to kill a render-identically-either-way literal contained a
    # narrower one, and the comment above claimed it carried "the stage it ran at"
    # when it carried a constant. A default here would let a third lane inherit the
    # wrong stage silently; requiring it makes a new caller state what is true.
    elapsed = next(
        (
            entry.get("elapsed_seconds")
            for entry in payload.get("release_runtime", [])
            if entry.get("label") == "quality_command"
        ),
        None,
    )
    measured = f" in {elapsed:.1f}s" if isinstance(elapsed, (int, float)) else ""
    payload["quality_status"] = (
        f"exited 0{measured} at `{stage}`, measured by this helper "
        f"(`{adapter_data['quality_command']}`)"
    )


def run_distinct_channel_floor(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    payload: dict[str, Any],
    cli: Any,
) -> None:
    timed(
        payload,
        "distinct_channel_verification",
        lambda: cli.confirm_release_via_distinct_channel(
            repo_root,
            payload,
            adapter_data=adapter_data,
            run_shell=cli.run_shell,
            tag_name=state["tag_name"],
            expected_release_url=state["expected_release_url"],
            backend=state["backend"],
            backend_command=cli.backend_command,
        ),
    )
    cli.reconcile_public_release_verification(payload)
    # The pre-publish notes audit only runs when a notes FILE was supplied, so
    # the `--generate-notes` default published a body nothing had inspected.
    # Post-hoc by necessity and advisory by design — the release already exists.
    timed(
        payload,
        "published_notes_audit",
        lambda: cli.audit_published_release_body(
            repo_root,
            payload,
            tag_name=state["tag_name"],
            backend=state["backend"],
            backend_command=cli.backend_command,
            # `run`, NOT `run_shell`: the command is a LIST, and `run_shell` uses
            # `shell=True`, where a list makes args[0] the command string and
            # drops the rest into `$0,$1,...`. `git status --short` runs as bare
            # `git`. The audit would have recorded `unavailable` on every publish
            # — closed-looking rather than closed.
            run=cli.run,
            audit_notes_text=cli.audit_notes_text,
        ),
    )
    if cli.evaluate_release_distinct_channel(payload)["ok"]:
        return
    _commit_final_release_artifact(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        payload=payload,
        cli=cli,
        has_issue_closeout=False,
    )
    cli.fail_release_distinct_channel_floor(payload)


def _commit_final_release_artifact(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    payload: dict[str, Any],
    cli: Any,
    has_issue_closeout: bool,
) -> None:
    cli.commit_final_release_artifact(
        repo_root,
        adapter_data=adapter_data,
        payload=payload,
        fresh_checkout_payload=state["fresh_checkout_payload"],
        artifact_relpath=state["artifact_relpath"],
        expected_release_url=state["expected_release_url"],
        remote=args.remote,
        branch=state["branch"],
        has_issue_closeout=has_issue_closeout,
    )


def close_issues_install_refresh_and_commit(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    issue_repo: str,
    payload: dict[str, Any],
    cli: Any,
    carrier_already_committed: bool = False,
    carrier_source: str = "release",
) -> None:
    payload["install_refresh"] = timed(
        payload,
        "post_publish_install_refresh",
        lambda: cli.run_post_publish_install_refresh(
            repo_root,
            command=adapter_data.get("post_publish_install_refresh", ""),
            run_shell=cli.run_shell,
        ),
    )
    payload["installed_readback"] = timed(
        payload,
        "post_publish_installed_readback",
        lambda: cli.collect_installed_readback(
            repo_root,
            install_refresh=payload["install_refresh"],
            version_command=adapter_data.get("post_publish_version_readback", ""),
            doctor_command=adapter_data.get("post_publish_doctor_readback", ""),
            run_shell=cli.run_shell,
            # The value read back is only evidence if something compares it.
            expected_version=payload.get("target_version"),
        ),
    )
    payload["release_observer"] = timed(
        payload,
        "release_observer",
        lambda: cli.safe_write_release_observer(
            repo_root,
            payload=payload,
            installed_readback=payload["installed_readback"],
        ),
    )
    if args.close_issue and not carrier_already_committed:
        timed(
            payload,
            "issue_closeout_carrier",
            lambda: cli.commit_issue_closeout_carrier_artifact(
                repo_root,
                write_artifact=lambda **kwargs: cli.write_current_artifact(
                    repo_root, adapter_data, payload, **kwargs
                ),
                payload=payload,
                fresh_checkout_payload=state["fresh_checkout_payload"],
                artifact_relpath=state["artifact_relpath"],
                expected_release_url=state["expected_release_url"],
                remote=args.remote,
                branch=state["branch"],
                run=cli.run,
            ),
        )
    timed(
        payload,
        "issue_closeout",
        lambda: cli.ensure_release_issues_closed(
            repo_root,
            repo=issue_repo,
            issue_numbers=args.close_issue,
            payload=payload,
            run=cli.run,
            behavior_lines=args.close_issue_behavior,
            probe_record_lines=args.close_issue_probe_record,
            # The lane name must reach HERE above all: this is the call that runs
            # `gh issue close`. Threading it only through the preflight left the
            # irreversible call misattributing which lane asked for it.
            carrier_source=carrier_source,
        ),
    )
    _commit_final_release_artifact(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        payload=payload,
        has_issue_closeout=bool(args.close_issue),
        cli=cli,
    )


def run_release_closeout_tail(
    repo_root: Path,
    *,
    args: Any,
    adapter_data: dict[str, Any],
    state: dict[str, Any],
    issue_repo: str,
    payload: dict[str, Any],
    cli: Any,
    carrier_already_committed: bool = False,
    carrier_source: str = "release",
) -> None:
    run_distinct_channel_floor(repo_root, args=args, adapter_data=adapter_data, state=state, payload=payload, cli=cli)
    close_issues_install_refresh_and_commit(
        repo_root,
        args=args,
        adapter_data=adapter_data,
        state=state,
        issue_repo=issue_repo,
        payload=payload,
        cli=cli,
        carrier_already_committed=carrier_already_committed,
        carrier_source=carrier_source,
    )
