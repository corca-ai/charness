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


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_current_release = SKILL_RUNTIME.load_local_skill_module(__file__, "current_release")
_bump_version = SKILL_RUNTIME.load_local_skill_module(__file__, "bump_version")
_check_real_host = SKILL_RUNTIME.load_local_skill_module(__file__, "check_real_host_proof")
_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_preflight = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_preflight")
_issue_closeout = SKILL_RUNTIME.load_local_skill_module(__file__, "release_issue_closeout")
_release_retro = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_retro")

build_release_payload = _current_release.build_payload
bump_part = _bump_version.bump_part
build_real_host_payload = _check_real_host.build_payload
current_branch = _helpers.current_branch
unreleased_paths = _helpers.unreleased_paths
release_previous_version = _helpers.release_previous_version
ensure_release_target_available = _helpers.ensure_release_target_available
safe_real_host_payload = _preflight.safe_real_host_payload
release_adapter_preflight_payload = _preflight.release_adapter_preflight_payload
update_instructions_version_blocker = _preflight.update_instructions_version_blocker
github_repo_slug = _issue_closeout.github_repo_slug
build_retro_trigger_evaluation = _release_retro.build_retro_trigger_evaluation


def target_version(args: argparse.Namespace, current_version: str) -> str:
    if args.publish_current:
        return current_version
    if args.set_version:
        return args.set_version
    assert args.part is not None
    return bump_part(current_version, args.part)


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


def build_publish_plan(
    args: argparse.Namespace,
    repo_root: Path,
    adapter_data: dict[str, Any],
    critique_artifact: str | None,
    *,
    run_command,
    resume: bool = False,
) -> dict[str, Any]:
    current_payload = build_release_payload(repo_root)
    current_version = current_payload["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    next_version = target_version(args, current_version)
    previous_version = release_previous_version(repo_root, args.publish_current, current_version, next_version, args.remote)
    update_blocker = update_instructions_version_blocker(
        adapter_data.get("update_instructions"), target_version=next_version, previous_version=previous_version
    )
    if update_blocker:
        raise SystemExit(update_blocker)
    branch = current_branch(repo_root)
    tag_name = f"v{next_version}"
    title = args.title or tag_name
    backend = adapter_data["release_backend"]
    # On --resume the local release commit + tag are expected to already exist;
    # the resume path validates that partial state itself, so skip the
    # "tag must not exist" guard that would otherwise block recovery.
    if not resume:
        ensure_release_target_available(repo_root, tag_name=tag_name, remote=args.remote, backend=backend)
    release_content_paths = unreleased_paths(repo_root, remote=args.remote, branch=branch, previous_version=previous_version)
    safe_real_host_payload(repo_root, release_content_paths, build_payload=build_real_host_payload)
    adapter_preflight_payload = release_adapter_preflight_payload(
        repo_root, release_content_paths=release_content_paths, previous_version=previous_version
    )
    issue_repo = args.close_issue_repo or github_repo_slug(repo_root, backend, run=run_command)
    payload = build_publish_payload(
        args, adapter_data, current_version=current_version, previous_version=previous_version,
        next_version=next_version, branch=branch, tag_name=tag_name, title=title,
        critique_artifact=critique_artifact,
    )
    payload["release_adapter_preflight"] = adapter_preflight_payload
    payload["retro_trigger_evaluation"] = build_retro_trigger_evaluation(
        repo_root, release_content_paths, evaluated_at="release_content_paths",
        tag_name=tag_name, execute=False,
    )
    payload["close_issue_numbers"] = args.close_issue
    payload["close_issue_repo"] = issue_repo
    return {
        "payload": payload,
        "next_version": next_version,
        "branch": branch,
        "tag_name": tag_name,
        "title": title,
        "backend": backend,
        "release_content_paths": release_content_paths,
        "adapter_preflight_payload": adapter_preflight_payload,
        "issue_repo": issue_repo,
    }
