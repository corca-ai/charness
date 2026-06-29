from __future__ import annotations

import runpy
import shlex
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


def read_packet(path: str, why: str) -> dict[str, str]:
    return _ENVELOPE.read(path, why)


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
    command = ['python3 "$SKILL_DIR/scripts/check_real_host_proof.py"', "--repo-root", "."]
    if real_host_scope and real_host_scope.get("scope") == "release_delta":
        command.extend(["--paths", *real_host_scope.get("changed_paths", [])])
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
            'python3 "$SKILL_DIR/scripts/check_fresh_checkout_probes.py" --repo-root . --json',
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
            'python3 "$SKILL_DIR/scripts/check_requested_review_gate.py" --repo-root . --skip-commands --json',
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
    if update_blocker:
        return action("prep_update_instructions", update_blocker)
    if release_payload.get("git_status") and target_version is not None:
        return action("clean_worktree", "Publish helper requires a clean worktree before dry-run or execute.")
    if target_version is None:
        return action(
            "inspect_only",
            "No target selector was provided; review current release state and choose publish-current/part/set-version.",
        )
    if not (args.critique_artifact or args.critique_blocked):
        return action(
            "needs_critique",
            "Task-completing release mutation requires a critique artifact or honest blocked-host signal.",
        )
    return action(
        "publish_dry_run",
        "Release state has no planner blockers; run the dry-run packet before asking for publish execution.",
    )
