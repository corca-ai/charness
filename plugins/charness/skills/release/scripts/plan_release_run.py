#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
_bump_version = SKILL_RUNTIME.load_local_skill_module(__file__, "bump_version")
_fresh_checkout = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
_real_host = SKILL_RUNTIME.load_local_skill_module(__file__, "check_real_host_proof")
_review_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "check_requested_review_gate")
_publish_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_planner_packets = SKILL_RUNTIME.load_local_skill_module(__file__, "plan_release_run_packets")

load_adapter = _resolve_adapter.load_adapter
build_release_payload = _current_release.build_payload
bump_part = _bump_version.bump_part
build_fresh_checkout_payload = _fresh_checkout.build_payload
build_real_host_payload = _real_host.build_payload
collect_changed_paths = _real_host.collect_changed_paths
build_review_gate_payload = _review_gate.build_payload
release_previous_version = _publish_helpers.release_previous_version
current_branch = _publish_helpers.current_branch
update_instructions_version_blocker = _preflight.update_instructions_version_blocker
safe_real_host_payload = _preflight.safe_real_host_payload
required_reads = _planner_packets.required_reads
gate_packets = _planner_packets.gate_packets
publish_packets = _planner_packets.publish_packets
next_action = _planner_packets.next_action


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--critique-artifact")
    parser.add_argument("--critique-blocked")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--publish-current", action="store_true")
    group.add_argument("--part", choices=("patch", "minor", "major"))
    group.add_argument("--set-version")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _target_version(args: argparse.Namespace, current_version: str | None) -> str | None:
    if not isinstance(current_version, str):
        return None
    if args.publish_current:
        return current_version
    if args.set_version:
        return args.set_version
    if args.part:
        return bump_part(current_version, args.part)
    return None


def _target_selector(args: argparse.Namespace) -> str | None:
    if args.publish_current:
        return "publish-current"
    if args.part:
        return args.part
    if args.set_version:
        return "set-version"
    return None


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    data = adapter.get("data") if isinstance(adapter.get("data"), dict) else {}
    release_payload: dict[str, Any] | None = None
    release_error: str | None = None
    try:
        release_payload = build_release_payload(repo_root)
    except Exception as exc:  # pragma: no cover - defensive packet
        release_error = f"{type(exc).__name__}: {exc}"
    current_version = None
    if release_payload:
        versions = release_payload.get("surface_versions")
        if isinstance(versions, dict):
            current_version = versions.get("packaging_manifest")
    target_version = _target_version(args, current_version if isinstance(current_version, str) else None)
    previous_version = None
    update_blocker = None
    if target_version and isinstance(current_version, str):
        previous_version = release_previous_version(
            repo_root,
            args.publish_current,
            current_version,
            target_version,
            args.remote,
        )
        update_blocker = update_instructions_version_blocker(
            data.get("update_instructions"),
            target_version=target_version,
            previous_version=previous_version,
        )
    real_host_payload = None
    if adapter.get("valid"):
        try:
            real_host_payload = safe_real_host_payload(
                repo_root,
                collect_changed_paths(repo_root),
                build_payload=build_real_host_payload,
            )
        except SystemExit as exc:
            real_host_payload = {"status": "blocked", "error": str(exc)}
    review_payload = None
    if adapter.get("valid"):
        review_payload = build_review_gate_payload(repo_root, run_commands=False)
    branch = current_branch(repo_root)
    planned_next_action = next_action(
        args=args,
        adapter=adapter,
        release_payload=release_payload,
        target_version=target_version,
        update_blocker=update_blocker,
    )
    return {
        "schema_version": "release.run_plan.v1",
        "repo_root": str(repo_root),
        "mode": "publish-current" if args.publish_current else "bump-and-publish" if target_version else "inspect",
        "branch": branch,
        "remote": args.remote,
        "adapter": {
            "found": adapter.get("found"),
            "valid": adapter.get("valid"),
            "path": adapter.get("path"),
            "warnings": adapter.get("warnings", []),
            "errors": adapter.get("errors", []),
        },
        "release_state": release_payload or {"status": "blocked", "error": release_error},
        "target": {
            "current_version": current_version,
            "target_version": target_version,
            "previous_version": previous_version,
            "selector": _target_selector(args),
            "tag_name": f"v{target_version}" if target_version else None,
        },
        "required_reads": required_reads(args, adapter),
        "gate_packets": gate_packets(),
        "evidence_packets": {
            "fresh_checkout": build_fresh_checkout_payload(repo_root, run_probes=False),
            "real_host": real_host_payload,
            "requested_review": review_payload,
        },
        "publish_packets": publish_packets(
            args,
            target_version=target_version,
            next_action_kind=planned_next_action["kind"],
        ),
        "blockers": [item for item in (update_blocker,) if item],
        "next_action": planned_next_action,
        "phase_barriers": [
            "Read required_reads before release mutation.",
            "Run report-first gate_packets before broad release work.",
            "Run publish-dry-run before publish-execute.",
            "Do not parallelize sync/export/bump/install/update/git mutation with validators.",
            "Treat public release verification and issue closeout as irreversible-boundary evidence, not terminal green.",
        ],
    }


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="release run planner")
    try:
        args = parse_args()
        payload = build_plan(args)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"next_action={payload['next_action']['kind']}: {payload['next_action']['reason']}")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
