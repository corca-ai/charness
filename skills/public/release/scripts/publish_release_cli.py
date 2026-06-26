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
_check_real_host = SKILL_RUNTIME.load_local_skill_module(__file__, "check_real_host_proof")
_check_review_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "check_requested_review_gate")
_fresh_checkout = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_artifact")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_audit_narrative = SKILL_RUNTIME.load_local_skill_module(__file__, "audit_public_release_narrative")
_issue_closeout = SKILL_RUNTIME.load_local_skill_module(__file__, "release_issue_closeout")
_post_create = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_post_create")
_release_retro = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_retro")
_release_plan = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_plan")
_resume = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_resume")
_execute = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_execute")
load_adapter = _resolve_adapter.load_adapter
build_release_payload = _current_release.build_payload
build_real_host_payload = _check_real_host.build_payload
build_review_gate_payload = _check_review_gate.build_payload
build_fresh_checkout_payload = _fresh_checkout.build_payload
build_narrative_audit_payload = _audit_narrative.build_payload
run = _helpers.run
run_shell = _helpers.run_shell
git_status = _helpers.git_status
changed_paths = _helpers.changed_paths
write_release_artifact = _artifact.write_release_artifact
backend_command = _helpers.backend_command
create_release = _helpers.create_release
expected_github_release_url = _helpers.expected_github_release_url
amend_fresh_checkout_artifact = _helpers.amend_fresh_checkout_artifact
commit_post_publish_artifact = _helpers.commit_post_publish_artifact
release_commit_body = _issue_closeout.release_commit_body
ensure_release_issues_closed = _issue_closeout.ensure_release_issues_closed
preflight_release_issues = _issue_closeout.preflight_release_issues
commit_issue_closeout_artifact = _issue_closeout.commit_issue_closeout_artifact
validate_critique_artifact_arg = _preflight.validate_critique_artifact_arg
enforce_release_critique_gate = _preflight.enforce_release_critique_gate
build_update_instructions_prep_payload = _preflight.build_update_instructions_prep_payload
safe_real_host_payload = _preflight.safe_real_host_payload
release_adapter_preflight_payload = _preflight.release_adapter_preflight_payload
run_release_adapter_preflight = _preflight.run_release_adapter_preflight
fail_after_post_create_verification = _post_create.fail_after_post_create_verification
verify_release_visible = _post_create.verify_release_visible
confirm_release_via_distinct_channel = _post_create.confirm_release_via_distinct_channel
evaluate_release_distinct_channel = _post_create.evaluate_release_distinct_channel
fail_release_distinct_channel_floor = _post_create.fail_release_distinct_channel_floor
run_post_publish_install_refresh = _post_create.run_post_publish_install_refresh
build_retro_trigger_evaluation = _release_retro.build_retro_trigger_evaluation
build_publish_plan = _release_plan.build_publish_plan
release_plan_target_version = _release_plan.target_version
release_previous_version = _helpers.release_previous_version
resume_publish = _resume.resume_publish


def _execution_context() -> SimpleNamespace:
    names = (
        "run_notes_file_preflight",
        "_helpers",
        "run",
        "backend_command",
        "expected_github_release_url",
        "preflight_release_issues",
        "run_release_adapter_preflight",
        "run_bump",
        "ensure_release_surface",
        "changed_paths",
        "safe_real_host_payload",
        "build_real_host_payload",
        "build_retro_trigger_evaluation",
        "build_fresh_checkout_payload",
        "write_current_artifact",
        "run_requested_review_gate",
        "run_cli_skill_surface_gate",
        "run_shell",
        "run_narrative_audit",
        "release_commit_body",
        "run_fresh_checkout_probes",
        "amend_fresh_checkout_artifact",
        "create_release",
        "verify_release_visible",
        "confirm_release_via_distinct_channel",
        "evaluate_release_distinct_channel",
        "fail_release_distinct_channel_floor",
        "finalize_release_payload",
        "commit_final_release_artifact",
        "fail_after_post_create_verification",
        "ensure_release_issues_closed",
        "run_post_publish_install_refresh",
    )
    return SimpleNamespace(**{name: globals()[name] for name in names})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to resolve the release adapter")
    parser.add_argument("--remote", default="origin", help="Git remote to push to (default: origin)")
    parser.add_argument("--title", help="Release title (defaults to the tag name)")
    parser.add_argument("--notes-file", type=Path, help="Path to a release notes file; omit to generate notes from commits")
    parser.add_argument("--critique-artifact", help="Path to the required release critique artifact (under charness-artifacts/critique/)")
    parser.add_argument("--critique-blocked", help="Host signal (>=20 chars) when the bounded fresh-eye critique was genuinely blocked by the host runtime; mutually exclusive with --critique-artifact")
    parser.add_argument("--close-issue", action="append", type=int, default=[], help="Issue number to close at release time; repeat for multiple")
    parser.add_argument("--close-issue-repo", help="Repository (owner/repo) hosting --close-issue numbers; defaults to current repo")
    parser.add_argument("--execute", action="store_true", help="Execute the publish plan; without it the payload is printed dry-run")
    parser.add_argument("--prep-update-instructions", action="store_true", help="Emit version-agnostic update_instructions guidance + staleness report, then exit. Run this BEFORE the release critique so the adapter guard does not HOLD the publish; does not require a clean worktree or the critique gate.")
    parser.add_argument("--resume", action="store_true", help="Resume a partial publish: detect the existing local release commit+tag, re-validate, then push/release/verify (requires --publish-current)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish-current", action="store_true", help="Publish the current packaging manifest version without bumping")
    group.add_argument("--part", choices=("patch", "minor", "major"), help="Semver component to bump before publishing")
    group.add_argument("--set-version", help="Explicit version string to set before publishing")
    return parser.parse_args()
def run_requested_review_gate(repo_root: Path) -> dict[str, Any]:
    review_gate_payload = build_review_gate_payload(repo_root, run_commands=True)
    if review_gate_payload["status"] == "blocked":
        raise SystemExit("requested release review gate blocked publish:\n" + "\n".join(review_gate_payload["blockers"]))
    return review_gate_payload


def run_cli_skill_surface_gate(repo_root: Path, adapter_data: dict[str, Any]) -> None:
    if {"installable_cli", "bundled_skill"}.issubset(set(adapter_data.get("product_surfaces", []))):
        command = ["python3", "scripts/check_cli_skill_surface.py", "--repo-root", str(repo_root)]
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


def ensure_release_surface(repo_root: Path, expected_version: str) -> None:
    release_payload = build_release_payload(repo_root)
    if release_payload["drift"]:
        raise SystemExit(f"release surface drift detected: {release_payload['drift']}")
    if release_payload["surface_versions"]["packaging_manifest"] != expected_version:
        raise SystemExit(f"expected packaging manifest version `{expected_version}`")


def write_current_artifact(
    repo_root: Path, adapter_data: dict[str, Any], payload: dict[str, Any],
    host_payload: dict[str, Any], *, quality_status: str = "passed before publish",
    fresh_checkout_payload: dict[str, Any] | None = None,
    release_url: str | None = None,
    issue_closeout: dict[str, Any] | None = None,
    install_refresh: dict[str, Any] | None = None,
) -> str:
    return write_release_artifact(
        repo_root, output_dir=adapter_data["output_dir"], package_id=adapter_data["package_id"],
        previous_version=payload["previous_version"], target_version=payload["target_version"], remote=payload["remote"],
        branch=payload["branch"], quality_command=adapter_data["quality_command"], release_url=release_url,
        update_instructions=adapter_data["update_instructions"], real_host_payload=host_payload,
        release_adapter_preflight_payload=payload.get("release_adapter_preflight"),
        fresh_checkout_payload=fresh_checkout_payload, issue_closeout=issue_closeout, quality_status=quality_status,
        install_refresh=install_refresh or payload.get("install_refresh"),
        tag_name=payload["tag_name"],
        public_release_verification=payload.get("public_release_verification", "not checked by this helper"),
        review_proof=payload.get("critique_artifact"),
        requested_review_gate=payload.get("requested_review_gate"),
        retro_trigger_evaluation=payload.get("retro_trigger_evaluation"),
        distinct_channel_verification=payload.get("distinct_channel_verification"),
        release_runtime=payload.get("release_runtime"),
    )


def run_narrative_audit(
    repo_root: Path,
    *,
    target_tag: str,
    notes_file: Path | None = None,
) -> None:
    audit_payload = build_narrative_audit_payload(
        repo_root,
        target_tag=target_tag,
        notes_file=notes_file,
    )
    if audit_payload["status"] == "blocked":
        raise SystemExit(
            "public release narrative audit blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in audit_payload["blockers"])
        )


def run_notes_file_preflight(repo_root: Path, *, target_tag: str, notes_file: Path | None) -> None:
    if notes_file is None:
        return
    notes_blockers = _audit_narrative.audit_notes_file(notes_file, target_tag=target_tag)
    if notes_blockers:
        raise SystemExit(
            "public release notes preflight blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in notes_blockers)
        )


def finalize_release_payload(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    artifact_relpath: str,
    host_payload: dict[str, Any],
    release_stdout: str,
    expected_release_url: str | None,
    release_verified: bool,
) -> None:
    payload["commit_sha"] = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    payload["artifact_path"] = artifact_relpath
    payload["real_host_required"] = host_payload["required"]
    payload["real_host_checklist"] = host_payload["checklist"]
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
    host_payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    has_issue_closeout: bool,
) -> None:
    def writer(**kwargs):
        return write_current_artifact(repo_root, adapter_data, payload, host_payload, **kwargs)

    kwargs = {
        "repo_root": repo_root, "write_artifact": writer, "payload": payload,
        "fresh_checkout_payload": fresh_checkout_payload, "artifact_relpath": artifact_relpath,
        "expected_release_url": expected_release_url, "remote": remote, "branch": branch,
    }
    if has_issue_closeout:
        commit_issue_closeout_artifact(**kwargs, run=run)
    else:
        commit_post_publish_artifact(**kwargs, run_command=run)


def _load_adapter_and_gate(args: argparse.Namespace, repo_root: Path) -> tuple[dict[str, Any], str | None]:
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    critique_artifact = validate_critique_artifact_arg(repo_root, args.critique_artifact, run_command=run)
    enforce_release_critique_gate(repo_root, critique_artifact=critique_artifact, critique_blocked=args.critique_blocked)
    return adapter["data"], critique_artifact


def run_prep_update_instructions(args: argparse.Namespace, repo_root: Path) -> None:
    """Pre-publish, pre-critique affordance: emit version-agnostic
    `update_instructions` guidance + staleness report so the maintainer repairs
    the adapter before the release critique, pre-empting the adapter HOLD.
    Read-only: it loads the adapter, computes the target/previous versions the
    real publish would use, and prints the prep payload without requiring a clean
    worktree or the critique gate.
    """
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    adapter_data = adapter["data"]
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
    print(json.dumps(prep, ensure_ascii=False, indent=2))


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
    adapter_data, critique_artifact = _load_adapter_and_gate(args, repo_root)
    status = git_status(repo_root)
    if status:
        raise SystemExit("publish_release requires a clean worktree before it starts.\n" + "\n".join(status))

    plan = build_publish_plan(args, repo_root, adapter_data, critique_artifact, run_command=run, resume=args.resume)
    if args.resume:
        resume_publish(repo_root, args=args, plan=plan, adapter_data=adapter_data, cli=_execution_context())
        return
    if not args.execute:
        print(json.dumps(plan["payload"], ensure_ascii=False, indent=2))
        return
    execute_publish_plan(args, repo_root, plan, adapter_data)
