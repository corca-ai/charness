from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_current_release = SKILL_RUNTIME.load_local_skill_module(__file__, "current_release")
_bump_version = SKILL_RUNTIME.load_local_skill_module(__file__, "bump_version")
_check_real_host = SKILL_RUNTIME.load_local_skill_module(__file__, "check_real_host_proof")
_check_review_gate = SKILL_RUNTIME.load_local_skill_module(__file__, "check_requested_review_gate")
_fresh_checkout = SKILL_RUNTIME.load_local_skill_module(__file__, "check_fresh_checkout_probes")
_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_artifact")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_audit_narrative = SKILL_RUNTIME.load_local_skill_module(__file__, "audit_public_release_narrative")
_issue_closeout = SKILL_RUNTIME.load_local_skill_module(__file__, "release_issue_closeout")
_post_create = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_post_create")
load_adapter = _resolve_adapter.load_adapter
build_release_payload = _current_release.build_payload
bump_part = _bump_version.bump_part
build_real_host_payload = _check_real_host.build_payload
build_review_gate_payload = _check_review_gate.build_payload
build_fresh_checkout_payload = _fresh_checkout.build_payload
build_narrative_audit_payload = _audit_narrative.build_payload
run = _helpers.run
run_shell = _helpers.run_shell
git_status = _helpers.git_status
current_branch = _helpers.current_branch
changed_paths = _helpers.changed_paths
unreleased_paths = _helpers.unreleased_paths
write_release_artifact = _artifact.write_release_artifact
backend_command = _helpers.backend_command
create_release = _helpers.create_release
expected_github_release_url = _helpers.expected_github_release_url
amend_fresh_checkout_artifact = _helpers.amend_fresh_checkout_artifact
commit_post_publish_artifact = _helpers.commit_post_publish_artifact
release_previous_version = _helpers.release_previous_version
ensure_release_target_available = _helpers.ensure_release_target_available
github_repo_slug = _issue_closeout.github_repo_slug
release_commit_body = _issue_closeout.release_commit_body
ensure_release_issues_closed = _issue_closeout.ensure_release_issues_closed
preflight_release_issues = _issue_closeout.preflight_release_issues
commit_issue_closeout_artifact = _issue_closeout.commit_issue_closeout_artifact
validate_critique_artifact_arg = _preflight.validate_critique_artifact_arg
enforce_release_critique_gate = _preflight.enforce_release_critique_gate
safe_real_host_payload = _preflight.safe_real_host_payload
fail_after_post_create_verification = _post_create.fail_after_post_create_verification
verify_release_visible = _post_create.verify_release_visible


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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish-current", action="store_true", help="Publish the current packaging manifest version without bumping")
    group.add_argument("--part", choices=("patch", "minor", "major"), help="Semver component to bump before publishing")
    group.add_argument("--set-version", help="Explicit version string to set before publishing")
    return parser.parse_args()
def target_version(args: argparse.Namespace, current_version: str) -> str:
    if args.publish_current:
        return current_version
    if args.set_version:
        return args.set_version
    assert args.part is not None
    return bump_part(current_version, args.part)
def run_requested_review_gate(repo_root: Path) -> None:
    review_gate_payload = build_review_gate_payload(repo_root, run_commands=True)
    if review_gate_payload["status"] == "blocked":
        raise SystemExit("requested release review gate blocked publish:\n" + "\n".join(review_gate_payload["blockers"]))


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
) -> str:
    return write_release_artifact(
        repo_root, output_dir=adapter_data["output_dir"], package_id=adapter_data["package_id"],
        previous_version=payload["previous_version"], target_version=payload["target_version"], remote=payload["remote"],
        branch=payload["branch"], quality_command=adapter_data["quality_command"], release_url=release_url,
        update_instructions=adapter_data["update_instructions"], real_host_payload=host_payload,
        fresh_checkout_payload=fresh_checkout_payload, issue_closeout=issue_closeout, quality_status=quality_status,
        tag_name=payload["tag_name"],
        public_release_verification=payload.get("public_release_verification", "not checked by this helper"),
        review_proof=payload.get("critique_artifact"),
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


def build_publish_payload(
    args: argparse.Namespace,
    adapter_data: dict[str, Any],
    *,
    current_version: str,
    previous_version: str,
    next_version: str,
    branch: str,
    tag_name: str,
    title: str,
    critique_artifact: str | None,
) -> dict[str, Any]:
    return {
        "package_id": adapter_data["package_id"],
        "current_version": current_version,
        "target_version": next_version,
        "previous_version": previous_version,
        "remote": args.remote,
        "branch": branch,
        "tag_name": tag_name,
        "title": title,
        "mode": "publish-current" if args.publish_current else "bump-and-publish",
        "quality_command": adapter_data["quality_command"],
        "fresh_checkout_probes": adapter_data["fresh_checkout_probes"],
        "commit_message": f"Release {adapter_data['package_id']} {next_version}",
        "notes_mode": "notes-file" if args.notes_file else "generate-notes",
        "critique_artifact": critique_artifact,
        "execute": args.execute,
    }


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


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter_data, critique_artifact = _load_adapter_and_gate(args, repo_root)
    status = git_status(repo_root)
    if status:
        raise SystemExit("publish_release requires a clean worktree before it starts.\n" + "\n".join(status))

    current_payload = build_release_payload(repo_root)
    current_version = current_payload["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    next_version = target_version(args, current_version)
    previous_version = release_previous_version(repo_root, args.publish_current, current_version, next_version, args.remote)
    branch = current_branch(repo_root)
    tag_name = f"v{next_version}"
    title = args.title or tag_name
    backend = adapter_data["release_backend"]
    ensure_release_target_available(repo_root, tag_name=tag_name, remote=args.remote, backend=backend)
    release_content_paths = unreleased_paths(repo_root, remote=args.remote, branch=branch, previous_version=previous_version)
    safe_real_host_payload(repo_root, release_content_paths, build_payload=build_real_host_payload)
    issue_repo = args.close_issue_repo or github_repo_slug(repo_root, backend, run=run)

    payload = build_publish_payload(args, adapter_data, current_version=current_version, previous_version=previous_version, next_version=next_version, branch=branch, tag_name=tag_name, title=title, critique_artifact=critique_artifact)
    payload["close_issue_numbers"] = args.close_issue
    payload["close_issue_repo"] = issue_repo
    if not args.execute:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    notes_file = args.notes_file.resolve() if args.notes_file else None
    run_notes_file_preflight(repo_root, target_tag=tag_name, notes_file=notes_file)

    run(backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    expected_release_url = expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    preflight_release_issues(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=run)
    run_bump(args, repo_root)
    ensure_release_surface(repo_root, next_version)

    host_payload = safe_real_host_payload(repo_root, sorted(set(release_content_paths + changed_paths(repo_root))), build_payload=build_real_host_payload)
    fresh_checkout_plan = build_fresh_checkout_payload(repo_root, run_probes=False)
    write_current_artifact(repo_root, adapter_data, payload, host_payload=host_payload, release_url=expected_release_url, quality_status="is queued for this publish attempt", fresh_checkout_payload=fresh_checkout_plan)
    run_requested_review_gate(repo_root)
    run_cli_skill_surface_gate(repo_root, adapter_data)
    run_shell(str(adapter_data["quality_command"]), cwd=repo_root)
    artifact_relpath = write_current_artifact(repo_root, adapter_data, payload, host_payload, fresh_checkout_payload=fresh_checkout_plan, release_url=expected_release_url)
    run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    run(["git", "add", "-A"], cwd=repo_root)
    commit_command = ["git", "commit", "-m", payload["commit_message"]]
    for body_line in release_commit_body(payload, args.close_issue):
        commit_command.extend(["-m", body_line])
    run(commit_command, cwd=repo_root)
    fresh_checkout_payload = run_fresh_checkout_probes(repo_root)
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    if fresh_checkout_payload["status"] == "passed":
        amend_fresh_checkout_artifact(
            repo_root, write_artifact=lambda **kwargs: write_current_artifact(
                repo_root, adapter_data, payload, host_payload, **kwargs
            ), fresh_checkout_payload=fresh_checkout_payload, release_url=expected_release_url,
            artifact_relpath=artifact_relpath, tag_name=tag_name, notes_file=notes_file,
            run_narrative_audit=run_narrative_audit, run_command=run,
        )
        fresh_checkout_payload = run_fresh_checkout_probes(repo_root)
        payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    run(["git", "tag", tag_name], cwd=repo_root)
    run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)

    release_result = create_release(repo_root, backend, tag_name=tag_name, title=title, notes_file=notes_file)
    release_verify_result = verify_release_visible(
        repo_root, tag_name, backend, backend_command=backend_command, run=run
    )
    release_verified = release_verify_result.returncode == 0
    finalize_release_payload(
        repo_root, payload, artifact_relpath=artifact_relpath, host_payload=host_payload,
        release_stdout=release_result.stdout, expected_release_url=expected_release_url,
        release_verified=release_verified,
    )
    if not release_verified:
        commit_final_release_artifact(
            repo_root, adapter_data=adapter_data, payload=payload, host_payload=host_payload,
            fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
            expected_release_url=expected_release_url, remote=args.remote, branch=branch,
            has_issue_closeout=False,
        )
        fail_after_post_create_verification(payload, verification_result=release_verify_result)
    ensure_release_issues_closed(repo_root, repo=issue_repo, issue_numbers=args.close_issue, payload=payload, run=run)
    commit_final_release_artifact(
        repo_root, adapter_data=adapter_data, payload=payload, host_payload=host_payload,
        fresh_checkout_payload=fresh_checkout_payload, artifact_relpath=artifact_relpath,
        expected_release_url=expected_release_url, remote=args.remote, branch=branch,
        has_issue_closeout=bool(args.close_issue),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
