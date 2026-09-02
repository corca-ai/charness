#!/usr/bin/env python3
"""Read, validate, and select one issue-native Goal Run child."""

from __future__ import annotations

import argparse
import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_SKILL_RUNTIME.repo_root_from_skill_script(__file__)
run_process = _SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import goal_run_pickup_lessons as _lesson_projection  # noqa: E402
from goal_run_pickup_contract import (  # noqa: E402 - the sibling contract is loaded after the portable path bootstrap
    PickupError,
    effective_work_items,
    parse_objective,
    select_from_parent_progress,
    validate_metadata,
    validate_progress,
)

_LESSON_SECTIONS = _lesson_projection.LESSON_SECTIONS
_LESSON_MAX_CHARS = _lesson_projection.LESSON_MAX_CHARS
_bounded_lesson = _lesson_projection.bounded_lesson
_read_lesson_digest = _lesson_projection._read_lesson_digest
_read_lesson_preview = _lesson_projection._read_lesson_preview
_read_lesson_projection = _lesson_projection.read_lesson_projection


def _emit_yaml(payload: dict[str, Any]) -> None:
    """Render command output through the repository's portable YAML helper."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        helper = ancestor / "scripts" / "yaml_output.py"
        if not helper.is_file():
            continue
        spec = importlib.util.spec_from_file_location("charness_goal_run_yaml_output", helper)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.emit_yaml(payload)
        return
    raise RuntimeError("scripts/yaml_output.py not found above goal_run_pickup.py")


def _load_path(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PickupError("runtime-unavailable", f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _issue_script(name: str) -> Path:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "issue" / "scripts" / f"{name}.py"
        if candidate.is_file():
            return candidate
    raise PickupError("runtime-unavailable", f"issue skill file not found: {name}.py")


def _achieve_script(name: str) -> Path:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "achieve" / "scripts" / f"{name}.py"
        if candidate.is_file():
            return candidate
    raise PickupError("runtime-unavailable", f"achieve skill file not found: {name}.py")


def _resolve_repository(repo_root: Path, adapter: dict[str, Any], runtime: Any) -> dict[str, str]:
    data = adapter["data"]
    configured = data.get("default_repo")
    if isinstance(configured, str) and configured.strip():
        owner, repo, _ = runtime.parse_target(
            configured, str(data["default_org"]), source_prefix="adapter-default-repo"
        )
        return {"full_name": f"{owner}/{repo}", "source": "adapter-default-repo"}
    remote_name = str(data.get("remote_name") or "origin")
    names = run_process(["git", "remote"], cwd=repo_root, timeout_seconds=10).stdout.splitlines()
    urls: list[tuple[str, str]] = []
    ordered = [remote_name] + [name for name in names if name != remote_name]
    for name in ordered:
        url = runtime.git_remote_url(repo_root, name)
        parsed = runtime.parse_remote_url(url) if url else None
        if parsed is not None and parsed not in urls:
            urls.append(parsed)
    if len(urls) == 1:
        owner, repo = urls[0]
        return {
            "full_name": f"{owner}/{repo}",
            "source": f"git-remote:{remote_name}"
            if ordered and ordered[0] == remote_name
            else "git-remote",
        }
    if not urls:
        raise PickupError(
            "repository-unresolved",
            "no compatible configured git remote or adapter repository was found",
        )
    raise PickupError(
        "repository-ambiguous",
        "multiple compatible git remotes resolve to different repositories",
        details={"repositories": sorted(f"{owner}/{repo}" for owner, repo in urls)},
    )


def _read_goal_parent(
    repo_root: Path,
    repo: str,
    number: int,
    adapter: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Routine pickup is deliberately a read path, not a second bootstrap. The
    # provider read itself is the live backend check; a separate auth/capability
    # probe followed by another parent read added latency without changing the
    # answer. Full preflight remains owned by bootstrap/sync/closeout commands.
    selection = _load_path(_issue_script("issue_provider_selection"), "issue_pickup_selection")
    try:
        resolved = selection.resolve_backend(repo_root, target_repo=repo, adapter=adapter)
    except RuntimeError as exc:
        raise PickupError("provider-selection-invalid", str(exc)) from exc
    if not resolved.get("adapter_ok"):
        raise PickupError(
            "adapter-invalid", "issue adapter is invalid", details=resolved.get("adapter")
        )
    reader = _load_path(_issue_script("issue_read"), "issue_pickup_read")
    try:
        issue = reader.read_issue_with_comments(
            repo,
            number,
            backend=resolved["backend"],
            include_sub_issues_summary=True,
        )["issue"]
        body = issue.get("body")
        parent = {
            "repo": repo,
            "number": issue.get("number", number),
            "title": issue.get("title"),
            "state": issue.get("state"),
            "url": issue.get("url"),
            "updated_at": issue.get("updatedAt"),
            "body": body,
            "comment_count": len(issue.get("comments", []))
            if isinstance(issue.get("comments"), list)
            else None,
        }
        summary = reader.normalise_sub_issues_summary(issue)
        if summary is not None:
            parent["sub_issues_summary"] = summary
    except RuntimeError as exc:
        raise PickupError("provider-read-failed", str(exc)) from exc
    return {"parent": parent}, resolved


def pickup(repo_root: Path, objective: str) -> dict[str, Any]:
    number = parse_objective(objective)
    adapter_module = _load_path(_issue_script("resolve_adapter"), "issue_pickup_adapter")
    adapter = adapter_module.load_adapter(repo_root)
    if not adapter["valid"]:
        raise PickupError("adapter-invalid", "issue adapter is invalid", details=adapter)
    runtime = _load_path(_issue_script("issue_runtime"), "issue_pickup_runtime")
    repository = _resolve_repository(repo_root, adapter, runtime)
    repo = repository["full_name"]
    graph, resolved = _read_goal_parent(repo_root, repo, number, adapter)
    parent = graph["parent"]
    guard = _load_path(_issue_script("issue_goal_run_guard"), "issue_pickup_guard")
    try:
        metadata = guard.parse_goal_run_metadata(parent.get("body"), context="Goal Run parent body")
    except RuntimeError as exc:
        raise PickupError("metadata-invalid", str(exc)) from exc
    if metadata is None:
        raise PickupError("not-a-goal-run", "target issue has no Goal Run metadata")
    if parent.get("state") != "OPEN":
        raise PickupError("parent-closed", "a closed Goal Run parent cannot be picked up")
    metadata = validate_metadata(
        metadata, repo=repo, parent_number=number, parent_url=parent["url"]
    )
    binding_module = _load_path(_achieve_script("goal_binding"), "issue_pickup_binding")
    try:
        binding = binding_module.validate_binding(
            repo_root,
            repo_root / metadata["binding_path"],
            expected_parent={"repo": repo, "number": number, "url": parent["url"]},
            expected_draft_path=metadata["draft_path"],
            expected_draft_sha256=metadata["draft_sha256"],
            expected_binding_sha256=metadata["binding_sha256"],
        )
    except (ValueError, OSError) as exc:
        raise PickupError("binding-invalid", str(exc)) from exc
    if metadata["initial_graph_sha256"] != binding["approved_work_items_sha256"]:
        raise PickupError(
            "graph-digest-mismatch", "parent initial graph hash differs from the immutable binding"
        )
    progress = validate_progress(
        metadata,
        binding["approved_work_items"],
        repo=repo,
        parent_number=number,
    )
    work_items = effective_work_items(binding["approved_work_items"], metadata)
    selection = select_from_parent_progress(progress, work_items, repo=repo)
    child_reader = _load_path(_issue_script("issue_read"), "issue_pickup_child_read")
    selected_number = selection["selected_child"]["number"]
    try:
        child_issue = child_reader.read_issue_with_comments(
            repo, selected_number, backend=resolved["backend"]
        )["issue"]
    except RuntimeError as exc:
        raise PickupError("cursor-child-read-failed", str(exc)) from exc
    child_state = child_issue.get("state")
    if child_state != "OPEN":
        raise PickupError(
            "cursor-child-closed",
            f"parent cursor points to child #{selected_number} in state {child_state!r}; run explicit Goal Run sync",
            details={
                "cursor": selection["selected_child"],
                "child": {
                    "repo": repo,
                    "number": child_issue.get("number", selected_number),
                    "state": child_state,
                    "url": child_issue.get("url"),
                },
            },
        )
    selected_child = dict(selection["selected_child"])
    selected_child.update(
        title=child_issue.get("title"),
        state=child_state,
        url=child_issue.get("url"),
    )
    summary = parent.get("sub_issues_summary")
    count_status = "unavailable"
    if isinstance(summary, dict):
        count_status = (
            "matched"
            if all(
                summary.get(field) == progress[field] for field in ("total", "completed", "open")
            )
            else "parent-count-stale"
        )
    lessons = _read_lesson_projection(repo_root)
    return {
        "ok": True,
        "kind": "charness.goal-run-pickup/v1",
        "status": "selected",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "objective": objective.strip(),
        "repository": repository,
        "parent": {"repo": repo, "number": number, "url": parent["url"], "state": parent["state"]},
        "metadata": metadata,
        "binding": {
            "path": metadata["binding_path"],
            "sha256": binding["binding_sha256"],
            "draft_sha256": binding["draft_sha256"],
            "draft_amended": binding.get("draft_amended", False),
        },
        "progress": progress,
        "sub_issues_summary": summary,
        "graph": {
            "count": progress["total"],
            "amended_work_items": [
                item["key"] for item in work_items if item.get("intent") == "amended"
            ],
            "source": "parent-progress",
            "reconciliation": "explicit-sync-only",
            "provider_summary": summary,
            "count_status": count_status,
        },
        "selection": {"source": "parent-progress", "child_reads": 1},
        "lessons": lessons,
        "selected_child": selected_child,
        "child_issue": {
            "repo": repo,
            "number": child_issue.get("number", selected_number),
            "title": child_issue.get("title"),
            "state": child_state,
            "url": child_issue.get("url"),
            "body": child_issue.get("body"),
            "updated_at": child_issue.get("updatedAt"),
            "comment_count": len(child_issue.get("comments", []))
            if isinstance(child_issue.get("comments"), list)
            else None,
            "comments": child_issue.get("comments", []),
        },
        "blocked_children": selection["blocked"],
        "invalid_open_children": selection["invalid_open"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select one executable child from an issue-native Goal Run"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root that owns the Goal Run adapter and artifacts",
    )
    parser.add_argument("--objective", required=True, help="Exact `/goal #N` objective")
    args = parser.parse_args(argv)
    try:
        result = pickup(args.repo_root.resolve(), args.objective)
    except PickupError as exc:
        result = {
            "ok": False,
            "kind": "charness.goal-run-pickup/v1",
            "status": exc.code,
            "outcome": "refused",
            "mutation_invoked": False,
            "error_code": exc.code,
            "error": str(exc),
        }
        if exc.details is not None:
            result["details"] = exc.details
        _emit_yaml(result)
        return 2
    _emit_yaml(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
