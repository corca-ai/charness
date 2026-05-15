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
_audit_narrative = SKILL_RUNTIME.load_local_skill_module(__file__, "audit_public_release_narrative")
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
tag_exists = _helpers.tag_exists
release_exists = _helpers.release_exists
changed_paths = _helpers.changed_paths
unreleased_paths = _helpers.unreleased_paths
write_release_artifact = _helpers.write_release_artifact
backend_command = _helpers.backend_command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--title")
    parser.add_argument("--notes-file", type=Path)
    parser.add_argument("--execute", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish-current", action="store_true")
    group.add_argument("--part", choices=("patch", "minor", "major"))
    group.add_argument("--set-version")
    return parser.parse_args()


def target_version(args: argparse.Namespace, current_version: str) -> str:
    if args.publish_current:
        return current_version
    if args.set_version:
        return args.set_version
    assert args.part is not None
    return bump_part(current_version, args.part)


def safe_real_host_payload(repo_root: Path, repo_paths: list[str]) -> dict[str, Any]:
    try:
        return build_real_host_payload(repo_root, repo_paths)
    except Exception as exc:  # pragma: no cover - fallback only
        return {"required": False, "changed_paths": repo_paths, "surface_hits": [], "path_hits": [], "checklist": [], "reason": f"Real-host/public verification probe could not run: {exc}"}


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
) -> str:
    return write_release_artifact(
        repo_root, output_dir=adapter_data["output_dir"], package_id=adapter_data["package_id"],
        previous_version=payload["previous_version"], target_version=payload["target_version"], remote=payload["remote"],
        branch=payload["branch"], quality_command=adapter_data["quality_command"], release_url=release_url,
        update_instructions=adapter_data["update_instructions"], real_host_payload=host_payload,
        fresh_checkout_payload=fresh_checkout_payload, quality_status=quality_status,
        tag_name=payload["tag_name"],
    )


def expected_github_release_url(repo_root: Path, backend: dict[str, Any], tag_name: str) -> str | None:
    if backend.get("id", "gh") != "gh":
        return None
    result = run(["gh", "repo", "view", "--json", "url", "--jq", ".url"], cwd=repo_root, check=False)
    if result.returncode != 0:
        return None
    repo_url = result.stdout.strip().rstrip("/")
    if not repo_url:
        return None
    return f"{repo_url}/releases/tag/{tag_name}"


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
    next_version: str,
    branch: str,
    tag_name: str,
    title: str,
) -> dict[str, Any]:
    return {
        "package_id": adapter_data["package_id"],
        "current_version": current_version,
        "target_version": next_version,
        "previous_version": current_version,
        "remote": args.remote,
        "branch": branch,
        "tag_name": tag_name,
        "title": title,
        "mode": "publish-current" if args.publish_current else "bump-and-publish",
        "quality_command": adapter_data["quality_command"],
        "fresh_checkout_probes": adapter_data["fresh_checkout_probes"],
        "commit_message": f"Release {adapter_data['package_id']} {next_version}",
        "notes_mode": "notes-file" if args.notes_file else "generate-notes",
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
) -> None:
    payload["commit_sha"] = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    payload["artifact_path"] = artifact_relpath
    payload["real_host_required"] = host_payload["required"]
    payload["real_host_checklist"] = host_payload["checklist"]
    payload["public_release_verification"] = "not_checked"
    payload["release_url"] = next((line.strip() for line in reversed(release_stdout.splitlines()) if line.strip()), None)
    if payload["release_url"] and expected_release_url and payload["release_url"] != expected_release_url:
        payload["release_url_warning"] = (
            f"release create returned `{payload['release_url']}` but the committed artifact "
            f"recorded expected URL `{expected_release_url}`"
        )


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    adapter_data = adapter["data"]
    status = git_status(repo_root)
    if status:
        raise SystemExit("publish_release requires a clean worktree before it starts.\n" + "\n".join(status))

    current_payload = build_release_payload(repo_root)
    current_version = current_payload["surface_versions"]["packaging_manifest"]
    if not isinstance(current_version, str):
        raise SystemExit("current_release did not report a packaging manifest version")
    next_version = target_version(args, current_version)
    branch = current_branch(repo_root)
    tag_name = f"v{next_version}"
    title = args.title or tag_name
    tag_state = tag_exists(repo_root, tag_name, remote=args.remote)
    if tag_state["local"] or tag_state["remote"]:
        raise SystemExit(f"tag `{tag_name}` already exists locally or on `{args.remote}`")
    backend = adapter_data["release_backend"]
    if release_exists(repo_root, tag_name, backend):
        raise SystemExit(f"GitHub release `{tag_name}` already exists")
    release_content_paths = unreleased_paths(repo_root, remote=args.remote, branch=branch)

    payload = build_publish_payload(
        args, adapter_data, current_version=current_version, next_version=next_version,
        branch=branch, tag_name=tag_name, title=title,
    )
    if not args.execute:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    notes_file = args.notes_file.resolve() if args.notes_file else None
    run_notes_file_preflight(repo_root, target_tag=tag_name, notes_file=notes_file)

    run(backend_command(backend, "auth_check", ["gh", "auth", "status"]), cwd=repo_root)
    expected_release_url = expected_github_release_url(repo_root, backend, tag_name)
    payload["expected_release_url"] = expected_release_url
    run_bump(args, repo_root)
    ensure_release_surface(repo_root, next_version)

    host_payload = safe_real_host_payload(repo_root, sorted(set(release_content_paths + changed_paths(repo_root))))
    fresh_checkout_plan = build_fresh_checkout_payload(repo_root, run_probes=False)
    write_current_artifact(
        repo_root, adapter_data, payload, host_payload=host_payload,
        quality_status="is queued for this publish attempt", fresh_checkout_payload=fresh_checkout_plan,
        release_url=expected_release_url,
    )
    run_requested_review_gate(repo_root)
    run_cli_skill_surface_gate(repo_root, adapter_data)
    run_shell(str(adapter_data["quality_command"]), cwd=repo_root)
    artifact_relpath = write_current_artifact(
        repo_root, adapter_data, payload, host_payload,
        fresh_checkout_payload=fresh_checkout_plan, release_url=expected_release_url,
    )
    run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    run(["git", "add", "-A"], cwd=repo_root)
    run(["git", "commit", "-m", payload["commit_message"]], cwd=repo_root)
    fresh_checkout_payload = run_fresh_checkout_probes(repo_root)
    payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    if fresh_checkout_payload["status"] == "passed":
        write_current_artifact(
            repo_root, adapter_data, payload, host_payload,
            fresh_checkout_payload=fresh_checkout_payload, release_url=expected_release_url,
        )
        run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
        run(["git", "add", artifact_relpath], cwd=repo_root)
        run(["git", "commit", "--amend", "--no-edit"], cwd=repo_root)
        fresh_checkout_payload = run_fresh_checkout_probes(repo_root)
        payload["fresh_checkout_probe_status"] = fresh_checkout_payload["status"]
    run(["git", "tag", tag_name], cwd=repo_root)
    run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)

    release_command = backend_command(
        backend,
        "release_create",
        ["gh", "release", "create", "{tag}", "--verify-tag", "--title", "{title}"],
        tag=tag_name,
        title=title,
    )
    release_command.extend(["--notes-file", str(args.notes_file.resolve())] if args.notes_file else ["--generate-notes"])
    release_result = run(release_command, cwd=repo_root)
    finalize_release_payload(
        repo_root, payload, artifact_relpath=artifact_relpath, host_payload=host_payload,
        release_stdout=release_result.stdout, expected_release_url=expected_release_url,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
