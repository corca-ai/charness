from __future__ import annotations

import runpy
import shlex
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


PREPARED_MARKER = "charness-release-state:prepared-awaiting-claims-review"
CRITIQUE_DIR = "charness-artifacts/critique"
CLAIMS_REVIEW_DIR = "charness-artifacts/release-review"


def read_packet(path: str, why: str) -> dict[str, str]:
    return _ENVELOPE.read(path, why)


def prepared_claims_state(
    repo_root: Path,
    *,
    current_version: str | None,
    binding_tokens: list[str],
    accepts: Any,
    marker_text: str | None,
    release_record: str,
    committed_record: str | None = None,
    drafted_notes: list[str] | None = None,
) -> dict[str, Any] | None:
    """Describe a `prepared-awaiting-claims-review` stop, or None when there is none.

    Normal release preparation now STOPS at a marked local record, and neither planner
    read that marker: the planner reported `inspect_only` and emitted no resume command,
    so the five-flag resume invocation -- including a `--critique-artifact` that must bind
    to the version being published -- had to be reconstructed by hand. A wrong critique
    path then fails as "standalone critique not satisfied" without naming an artifact that
    WOULD bind, which is the part a reader cannot recover from the refusal.
    """
    # The marker is read from the COMMIT, not the worktree file: every publish-side
    # consumer reads `git show <commit>:...`, and a worktree-only read makes the planner
    # confidently prescribe a claims resume for a HEAD the publish helper will not treat
    # as a prepared stop at all.
    if marker_text is None or PREPARED_MARKER not in marker_text:
        return None
    candidates: list[str] = []
    critique_root = repo_root / CRITIQUE_DIR
    if binding_tokens and critique_root.is_dir():
        # Judged by the publish gate's OWN acceptance, not by binding alone. The gate
        # applies three tests -- tracked-in-git, binding, and a stub-residual floor -- and
        # a binding-only filter named candidates the gate then refused with the exact
        # "standalone critique not satisfied" message this packet exists to prevent, or
        # named an UNTRACKED file whose real refusal is a dirty-worktree complaint that
        # never says "commit this first".
        candidates = sorted(
            rel for rel in (
                path.relative_to(repo_root).as_posix()
                for path in critique_root.rglob("*.md")
                if path.is_file() and path.stat().st_size
            )
            if accepts(rel)
        )
    return {
        "marker": PREPARED_MARKER,
        # Passed in rather than a module constant. A second copy of the record path in the
        # planner made the planner blind in exactly the repos the publish helper's own copy
        # made the claims floor blind: it read no marker, skipped the prepared-stop branch,
        # and reported `inspect_only` -- "nothing to do here" -- at a live prepared stop.
        "release_record": release_record,
        "target_version": current_version,
        "tag_name": f"v{current_version}" if current_version else None,
        "critique_artifact_candidates": candidates,
        "critique_binding_tokens": binding_tokens,
        "claims_review_artifact_dir": CLAIMS_REVIEW_DIR,
        "committed_claims_record": committed_record,
        "drafted_notes_candidates": sorted(drafted_notes or []),
    }


def resume_claims_packets(prepared: dict[str, Any] | None) -> list[dict[str, object]]:
    """The exact resume invocation, with every flag the stop requires already placed."""
    if not prepared:
        return []
    critique = prepared["critique_artifact_candidates"]
    critique_value = critique[0] if len(critique) == 1 else "<release-critique-artifact>"
    # Once the record is committed the path is fully derivable, and leaving it a hole in
    # exactly the state where it is knowable defeats the point of emitting the command.
    claims_value = prepared.get("committed_claims_record") or f"{CLAIMS_REVIEW_DIR}/<claims-review-record>.json"
    # Same reasoning, and now load-bearing rather than convenient: the resume lane RUNS the
    # notes-file preflight, so a command emitted without `--notes-file` in a repo that has
    # drafted notes for this tag is a command the operator will be refused for running
    # verbatim. Placed only when exactly one candidate exists; two candidates is a choice
    # the planner must not make silently.
    notes_candidates = prepared.get("drafted_notes_candidates") or []
    notes = ["--notes-file", notes_candidates[0]] if len(notes_candidates) == 1 else []

    def packet(packet_id: str, *, execute: bool) -> dict[str, object]:
        command = [
            'python3 "$SKILL_DIR/scripts/publish_release.py"', "--repo-root", ".",
            "--resume", "--publish-current",
            "--claims-review-artifact", claims_value,
            "--critique-artifact", critique_value,
            *notes,
        ]
        if execute:
            command.append("--execute")
        return {
            "id": packet_id,
            "command": command_text(command),
            "requires_user_confirmation": execute,
            "purpose": (
                "publish the already-prepared release commit once its claims review is committed"
                if execute
                else "re-validate the prepared-stop gates without mutation"
            ),
            # The notes half is now ENFORCED: the resume lane runs the notes-file preflight,
            # so dropping `--notes-file` where drafted notes exist is refused rather than
            # silently published as `--generate-notes`. It stays listed because the refusal
            # is a stop, not a substitute for passing the flag, and because the preflight
            # keys on a filename convention it admits it cannot see through.
            # The `--close-issue*` half is NOT enforced on this lane and cannot be from
            # here: no durable record of the original close-issue intent exists at a
            # prepared stop, so a dropped flag simply leaves the issue open. (The
            # post-publication lane does refuse the omission; this one has nothing to
            # compare against.)
            "repeat_original_arguments": [
                "--notes-file", "--close-issue", "--close-issue-classification",
                "--close-issue-carrier-file",
            ],
            "placeholders": sorted(
                {value for value in (critique_value, claims_value) if value.startswith("<") or "<" in value}
            ),
        }

    return [packet("publish-resume-dry-run", execute=False), packet("publish-resume-execute", execute=True)]


def action(kind: str, reason: str) -> dict[str, str]:
    return _ENVELOPE.next_action(kind, reason=reason)


def first_matching_action(checks: list[tuple[bool, str, str]]) -> dict[str, str] | None:
    for condition, kind, reason in checks:
        if condition:
            return action(kind, reason)
    return None


def required_reads(args: Any, adapter: dict[str, Any]) -> list[dict[str, str]]:
    reads = [
        read_packet("references/index.md", "Manual progressive-disclosure map for release references."),
        read_packet("references/version-policy.md", "Use when choosing or checking a target bump."),
    ]
    if not adapter.get("found") or not adapter.get("valid") or adapter.get("warnings"):
        reads.append(read_packet("references/adapter-contract.md", "Adapter is missing, invalid, or warning-bearing."))

    critique_reason = (
        "Release mutation needs a standalone critique artifact or honest blocked-host signal."
        if args.critique_artifact or args.critique_blocked
        else "Read before task-completing release mutation; planner currently lacks critique proof."
    )
    reads.append(read_packet("references/critique-boundary.md", critique_reason))
    reads.append(
        read_packet(
            "references/publication-boundary.md",
            "Tag, workflow, public visibility, and issue-close boundaries are not terminal green.",
        )
    )

    data = adapter.get("data") if isinstance(adapter.get("data"), dict) else {}
    if data.get("post_publish_install_refresh"):
        reads.append(
            read_packet(
                "references/install-refresh.md",
                "Adapter declares a post-publish install refresh command.",
            )
        )
    if data.get("real_host_required_surfaces") or data.get("real_host_required_path_globs"):
        reads.append(
            read_packet(
                "references/real-host-proof.md",
                "Adapter declares release-time real-host proof triggers.",
            )
        )
    return reads


def gate_packet(
    gate_id: str,
    command: str,
    purpose: str,
    trust_model: str,
    run_when: str,
) -> dict[str, str]:
    return _ENVELOPE.gate_packet(
        gate_id,
        trust_model,
        cost_tier="cheap",
        command=command,
        purpose=purpose,
        run_when=run_when,
    )


def command_text(parts: list[str]) -> str:
    return " ".join([parts[0], *(shlex.quote(part) for part in parts[1:])])


def _real_host_command(real_host_scope: dict[str, Any] | None) -> str:
    command = ['python3 "$SKILL_DIR/scripts/check_real_host_proof.py"', "--repo-root", ".", "--detail"]
    if real_host_scope and real_host_scope.get("scope") == "release_delta":
        provenance = real_host_scope.get("provenance", {})
        command.extend(
            ["--changed-range", f"{provenance.get('base_sha')}..{provenance.get('head_sha')}"]
        )
    return command_text(command)


def gate_packets(real_host_scope: dict[str, Any] | None = None) -> list[dict[str, str]]:
    return [
        gate_packet(
            "current-release",
            'python3 "$SKILL_DIR/scripts/current_release.py" --repo-root .',
            "release surface, version drift, worktree, and configured fresh-checkout status",
            "hard drift facts plus configured-but-not-run probe status",
            "always before release mutation",
        ),
        gate_packet(
            "fresh-checkout-probes",
            'python3 "$SKILL_DIR/scripts/check_fresh_checkout_probes.py" --repo-root . --detail',
            "detect whether fresh-checkout probes are declared",
            "configuration packet; publish helper runs probes before tag push",
            "always; add --run-probes only for explicit pre-publish proof",
        ),
        gate_packet(
            "real-host-proof",
            _real_host_command(real_host_scope),
            "determine whether release-time human/host proof is required",
            "trigger detector, not the proof itself",
            "always before closeout claims",
        ),
        gate_packet(
            "requested-review-gate",
            'python3 "$SKILL_DIR/scripts/check_requested_review_gate.py" --repo-root . --skip-commands --detail',
            "surface configured requested-review enforcement posture",
            "advisory when no requested_review_commands are configured",
            "before publish; execute commands in the publish helper",
        ),
    ]


def publish_packets(
    args: Any,
    *,
    target_version: str | None,
    next_action_kind: str,
) -> list[dict[str, object]]:
    if target_version is None:
        return []
    if next_action_kind != "publish_dry_run":
        return []

    if args.publish_current:
        selector = ["--publish-current"]
    elif args.set_version:
        selector = ["--set-version", target_version]
    else:
        selector = ["--part", str(args.part)]

    critique = []
    if args.critique_artifact:
        critique = ["--critique-artifact", args.critique_artifact]
    elif args.critique_blocked:
        critique = ["--critique-blocked", args.critique_blocked]

    def packet(packet_id: str, *, execute: bool) -> dict[str, object]:
        command = ['python3 "$SKILL_DIR/scripts/publish_release.py"', "--repo-root", ".", *selector, *critique]
        if execute:
            command.append("--execute")
        purpose = (
            "mutate, verify, push/tag, publish, and record closeout evidence"
            if execute
            else "build the publish payload without mutation"
        )
        return {
            "id": packet_id,
            "command": command_text(command),
            "requires_user_confirmation": execute,
            "purpose": purpose,
        }

    return [packet("publish-dry-run", execute=False), packet("publish-execute", execute=True)]


def next_action(
    *,
    args: Any,
    adapter: dict[str, Any],
    release_payload: dict[str, Any] | None,
    target_version: str | None,
    update_blocker: str | None,
    prepared_claims: dict[str, Any] | None = None,
) -> dict[str, str]:
    if adapter_action := first_matching_action(
        [
            (
                not adapter.get("found"),
                "scaffold_adapter",
                "No release adapter was found; declare release boundaries before mutation.",
            ),
            (not adapter.get("valid"), "repair_adapter", "Release adapter is invalid."),
        ]
    ):
        return adapter_action
    if release_payload is None:
        return action("repair_release_surface", "Current release state could not be built.")
    if release_payload.get("drift"):
        return action("sync_release_surface", "Generated release surfaces drift from the packaging manifest.")
    # Deliberately NOT routed on `absence_corroboration` here. The planner runs BEFORE
    # the sync command, so a generated surface being absent at plan time is the ordinary
    # fresh-checkout state, not evidence of anything -- routing on it would refuse every
    # pre-sync plan. The publish gate runs immediately AFTER sync, where an absent
    # surface means the sync did not write it, which is the state D48 is about. Cost of
    # that placement, accepted and recorded: the refusal lands after the version bump has
    # already rewritten the worktree.
    if update_blocker:
        return action("prep_update_instructions", update_blocker)
    if release_payload.get("git_status") and target_version is not None:
        return action("clean_worktree", "Publish helper requires a clean worktree before dry-run or execute.")
    if prepared_claims:
        # BEFORE `inspect_only`. A prepared stop with no `--part`/`--publish-current`
        # selector is exactly the shape that used to read as "nothing to do here": the
        # release is mid-flight and its next step is a resume, not a fresh selector.
        candidates = prepared_claims["critique_artifact_candidates"]
        if len(candidates) == 1:
            critique_hint = f"--critique-artifact {candidates[0]}"
        elif candidates:
            critique_hint = (
                f"--critique-artifact one of {candidates} (each binds "
                f"{prepared_claims['critique_binding_tokens']})"
            )
        else:
            critique_hint = (
                f"--critique-artifact <path> -- no artifact under {CRITIQUE_DIR} binds "
                f"{prepared_claims['critique_binding_tokens']}, so the release critique is owed first"
            )
        return action(
            "resume_prepared_claims_review",
            f"{prepared_claims['release_record']} carries `{PREPARED_MARKER}` for "
            f"{prepared_claims['tag_name'] or 'the prepared version'}; commit the bound claims review, "
            f"then run the publish-resume packets. Critique: {critique_hint}.",
        )
    if target_version is None:
        return action(
            "inspect_only",
            "No target selector was provided; review current release state and choose publish-current/part/set-version.",
        )
    if not (args.critique_artifact or args.critique_blocked):
        # Name the PRODUCER, not only the `--critique-artifact` validator flag:
        # the required artifact shape is otherwise discoverable only by failing
        # `validate_critique_artifacts.py`.
        return _ENVELOPE.next_action(
            "needs_critique",
            reason="Task-completing release mutation requires a critique artifact or honest blocked-host signal.",
            scaffold_command='python3 "$SKILL_DIR/../critique/scripts/scaffold_critique_artifact.py" --repo-root .',
        )
    return action(
        "publish_dry_run",
        "Release state has no planner blockers; run the dry-run packet before asking for publish execution.",
    )
