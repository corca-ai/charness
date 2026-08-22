#!/usr/bin/env python3
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


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_current_release = SKILL_RUNTIME.load_local_skill_module(__file__, "current_release")
_fresh_checkout = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
_real_host = SKILL_RUNTIME.load_local_skill_module(__file__, "check_real_host_proof")
_review_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "check_requested_review_gate")
_publish_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_planner_packets = SKILL_RUNTIME.load_local_skill_module(__file__, "plan_release_run_packets")
_claims_review = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_claims_review")
_publish_plan = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_plan")
_drafted_notes = SKILL_RUNTIME.load_local_skill_module(__file__, "drafted_release_notes")
_prepared_stop = SKILL_RUNTIME.load_local_skill_module(__file__, "plan_release_prepared_stop")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)

load_adapter = _resolve_adapter.load_adapter
build_release_payload = _current_release.build_payload
build_fresh_checkout_payload = _fresh_checkout.build_payload
build_real_host_payload = _real_host.build_payload
collect_changed_paths = _real_host.collect_changed_paths
build_review_gate_payload = _review_gate.build_payload
release_previous_version = _publish_helpers.release_previous_version
unreleased_scope = _publish_helpers.unreleased_scope
path_list_sha256 = _publish_helpers.path_list_sha256
current_branch = _publish_helpers.current_branch
update_instructions_version_blocker = _preflight.update_instructions_version_blocker
safe_real_host_payload = _preflight.safe_real_host_payload
release_binding_tokens = _preflight.release_binding_tokens
_closeout_evidence = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.check_prescribed_skill_executed_lib"
)
required_reads = _planner_packets.required_reads
gate_packets = _planner_packets.gate_packets
publish_packets = _planner_packets.publish_packets
prepared_claims_state = _planner_packets.prepared_claims_state
resume_claims_packets = _planner_packets.resume_claims_packets
next_action = _planner_packets.next_action
release_plan_target_version = _publish_plan.target_version
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        epilog=(
            "Use --detail before release mutation to inspect required_reads, "
            "gate_packets, evidence_packets, and real-host proof scope."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repository root for adapter and release-surface resolution.",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote used to inspect release tags and history.",
    )
    parser.add_argument(
        "--critique-artifact",
        help="Path to the release critique artifact to include in planned publish commands.",
    )
    parser.add_argument(
        "--critique-blocked",
        help="Host signal explaining why the bounded critique could not run.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--publish-current",
        action="store_true",
        help="Plan publishing the current version without bumping it.",
    )
    group.add_argument(
        "--part",
        choices=("patch", "minor", "major"),
        help="Version bump part to include in the release plan: patch, minor, or major.",
    )
    group.add_argument(
        "--set-version",
        help="Explicit target version to include in the release plan.",
    )
    parser.add_argument("--detail", action="store_true", help="Emit the full release plan as YAML.")
    return parser.parse_args()


def _target_version(args: argparse.Namespace, current_version: str | None) -> str | None:
    if not isinstance(current_version, str):
        return None
    if not (args.publish_current or args.set_version or args.part):
        return None
    return release_plan_target_version(args, current_version)


def resume_summary_lines(payload: dict[str, Any]) -> list[str]:
    """Resume commands for the one-line summary output.

    The summary is where an operator at a prepared stop actually looks; without the
    command here the resume invocation still has to be reconstructed by hand from
    `--detail`, which is the whole gap this reads the marker for.
    """
    return [
        f"{packet['id']}: {packet['command']}"
        for packet in payload.get("publish_packets") or []
        if str(packet.get("id", "")).startswith("publish-resume")
    ]


def _target_selector(args: argparse.Namespace) -> str | None:
    if args.publish_current:
        return "publish-current"
    if args.part:
        return args.part
    if args.set_version:
        return "set-version"
    return None


def _real_host_path_scope(
    repo_root: Path,
    *,
    branch: str,
    remote: str,
    target_version: str | None,
    previous_version: str | None,
) -> dict[str, Any]:
    if target_version and previous_version:
        delta = unreleased_scope(
            repo_root,
            remote=remote,
            branch=branch,
            previous_version=previous_version,
        )
        changed_paths = delta["changed_paths"]
        return {
            "scope": "release_delta",
            "changed_paths": changed_paths,
            "previous_version": previous_version,
            "provenance": {
                "base_ref": delta["base_ref"],
                "base_sha": delta["base_sha"],
                "head_sha": delta["head_sha"],
                "path_count": len(changed_paths),
                "paths_sha256": delta["paths_sha256"],
            },
        }
    changed_paths = collect_changed_paths(repo_root)
    return {
        "scope": "worktree",
        "changed_paths": changed_paths,
        "previous_version": None,
        "provenance": {
            "path_count": len(changed_paths),
            "paths_sha256": path_list_sha256(changed_paths),
        },
    }


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    # GUARDED AT THE READ SITE, though this row is WEAKER than the three gate rows and is
    # recorded that way rather than dressed up. Measured at `dd5b6dee9`: the planner did
    # NOT go silent under a refused version -- it printed
    # `next_action=repair_adapter: Release adapter is invalid.` and left the two
    # `valid`-gated evidence packets null. What it DID emit, at exit 0, was a plan
    # asserting `package_id: <the temp directory's own name>` and two paths under
    # `packaging/` and `plugins/` that do not exist, with `blockers: []`.
    #
    # ROW 2 ALONE already made this exit 1 by inheritance -- row 3 cannot have
    # contributed, and a round-1 bounded review caught this comment crediting it.
    # `build_real_host_payload` is behind `if adapter.get("valid")` below AND wrapped in
    # `except SystemExit`, so its refusal becomes a payload field, never an exit.
    # `build_release_payload` is what refuses: it is called before the three
    # unconditional `data` reads (`update_instructions`, `release_record_path`,
    # `drafted_notes_candidates`) and its `SystemExit` is not
    # caught by the `except Exception` around it. That inheritance is REAL and was
    # measured, but it is positional -- reordering this function, or widening that
    # `except` to `BaseException`, restores the old behavior with no test failing. The
    # guard here makes the row's verdict a property of this file rather than of the order
    # its callees happen to be called in.
    #
    # Narrow by construction: only an UNSPEAKABLE version refuses. An adapter that is
    # speakable but otherwise invalid still plans and still reports its own next action,
    # which is the affordance this planner exists for.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="release-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
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
    branch = current_branch(repo_root)
    real_host_scope = None
    real_host_payload = None
    if adapter.get("valid"):
        try:
            real_host_scope = _real_host_path_scope(
                repo_root,
                branch=branch,
                remote=args.remote,
                target_version=target_version,
                previous_version=previous_version,
            )
            real_host_payload = safe_real_host_payload(
                repo_root,
                real_host_scope["changed_paths"],
                build_payload=build_real_host_payload,
            )
            real_host_payload.pop("changed_paths", None)
            real_host_payload["evidence_scope"] = real_host_scope["scope"]
            real_host_payload["evidence_previous_version"] = real_host_scope["previous_version"]
            real_host_payload["evidence_provenance"] = real_host_scope["provenance"]
        except SystemExit as exc:
            real_host_payload = {"status": "blocked", "error": str(exc)}
    review_payload = None
    if adapter.get("valid"):
        review_payload = build_review_gate_payload(repo_root, run_commands=False)
    record_path = _prepared_stop.release_record_path(data)
    prepared_claims = prepared_claims_state(
        repo_root,
        current_version=current_version if isinstance(current_version, str) else None,
        binding_tokens=release_binding_tokens(current_version if isinstance(current_version, str) else None),
        accepts=_prepared_stop.critique_acceptor(
            repo_root,
            release_binding_tokens(current_version if isinstance(current_version, str) else None),
            closeout_evidence=_closeout_evidence,
        ),
        marker_text=_prepared_stop.head_release_record(repo_root, record_path),
        release_record=record_path or "",
        committed_record=_prepared_stop.committed_claims_record(
            repo_root, claims_record_in_change_set=_claims_review.claims_record_in_change_set
        ),
        drafted_notes=_prepared_stop.drafted_notes_candidates(
            repo_root, data, f"v{current_version}" if isinstance(current_version, str) else None,
            find_drafted_notes=_drafted_notes.find_drafted_notes,
        ),
    )
    planned_next_action = next_action(
        args=args,
        adapter=adapter,
        release_payload=release_payload,
        target_version=target_version,
        update_blocker=update_blocker,
        prepared_claims=prepared_claims,
    )
    return ENVELOPE.build_envelope(
        schema_version="release.run_plan.v1",
        required_reads=ENVELOPE.measure_reads(required_reads(args, adapter), {None: SKILL_ROOT}),
        next_action=planned_next_action,
        gate_packets=gate_packets(real_host_scope),
        repo_root=str(repo_root),
        mode="publish-current" if args.publish_current else "bump-and-publish" if target_version else "inspect",
        branch=branch,
        remote=args.remote,
        adapter={
            "found": adapter.get("found"),
            "valid": adapter.get("valid"),
            "path": adapter.get("path"),
            "warnings": adapter.get("warnings", []),
            "errors": adapter.get("errors", []),
        },
        release_state=release_payload or {"status": "blocked", "error": release_error},
        target={
            "current_version": current_version,
            "target_version": target_version,
            "previous_version": previous_version,
            "selector": _target_selector(args),
            "tag_name": f"v{target_version}" if target_version else None,
        },
        evidence_packets={
            "fresh_checkout": build_fresh_checkout_payload(repo_root, run_probes=False),
            "real_host": real_host_payload,
            "requested_review": review_payload,
        },
        prepared_claims_review=prepared_claims,
        publish_packets=publish_packets(
            args,
            target_version=target_version,
            next_action_kind=planned_next_action["kind"],
        )
        or resume_claims_packets(prepared_claims),
        blockers=[item for item in (update_blocker,) if item],
        phase_barriers=[
            "Read required_reads before release mutation.",
            "Run report-first gate_packets before broad release work.",
            "Run publish-dry-run before publish-execute.",
            "Do not parallelize sync/export/bump/install/update/git mutation with validators.",
            "Treat public release verification and issue closeout as irreversible-boundary evidence, not terminal green.",
        ],
    )


def main() -> int:
    # The planner's own budget, not the shared 10s script default. It shells git,
    # reads the adapter, resolves surface versions, and walks the prepared-stop
    # topology; measured unloaded on this repo it takes 7.00s / 6.90s / 8.81s, so a
    # 10s ceiling is a 1.1x margin against its own typical cost. Every gate lane
    # here is parallel by construction, so that margin is not a margin: under
    # `pytest -n` the planner is killed mid-report and
    # `test_detail_yaml_is_structured` fails on the empty stdout, naming the
    # timeout only as `isinstance(None, dict)`.
    #
    # Same reasoning as `check_fresh_checkout_probes.py`, which takes
    # `default_seconds=0` because it shells arbitrary-length probes: a wrapper
    # default sized for small scripts must not kill a valid report before its
    # owner can finish. A finite ceiling is kept here rather than 0 because the
    # planner's work IS bounded -- a run of this length means something is wrong,
    # and a report-only command should say so rather than hang. An explicit
    # CHARNESS_SCRIPT_TIMEOUT_SECONDS still overrides this.
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(
        label="release run planner", default_seconds=90
    )
    try:
        args = parse_args()
        payload = build_plan(args)
        if args.detail:
            yaml_output.emit_yaml(payload)
        else:
            print(f"next_action={payload['next_action']['kind']}: {payload['next_action']['reason']}")
            for line in resume_summary_lines(payload):
                print(line)
            real_host = payload.get("evidence_packets", {}).get("real_host")
            if isinstance(real_host, dict) and real_host.get("required"):
                scope = real_host.get("evidence_scope") or "unknown"
                print(f"real_host=required scope={scope}; inspect --detail evidence_packets.real_host before closeout")
            elif isinstance(real_host, dict) and "required" not in real_host and "error" not in real_host:
                # No verdict key means the probe evaluated nothing. Staying SILENT
                # here reads the same as a clean non-match in the one summary the
                # release preflight prints, which is the conflation this whole
                # slice removes -- one surface over.
                evaluation_scope = real_host.get("evaluation_scope") or "unknown"
                print(
                    f"real_host=not-established evaluation_scope={evaluation_scope}; "
                    "no real-host verdict was produced for this plan"
                )
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
