#!/usr/bin/env python3
"""Read, validate, and select one issue-native Goal Run child."""

from __future__ import annotations

import argparse
import importlib.util
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from goal_run_pickup_contract import (  # noqa: E402 - the sibling contract is loaded after the portable path bootstrap
    PickupError,
    membership_digest,
    parse_objective,
    reconcile_and_select,
    validate_metadata,
)


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
        owner, repo, _ = runtime.parse_target(configured, str(data["default_org"]), source_prefix="adapter-default-repo")
        return {"full_name": f"{owner}/{repo}", "source": "adapter-default-repo"}
    remote_name = str(data.get("remote_name") or "origin")
    names = subprocess.run(["git", "remote"], cwd=repo_root, check=False, capture_output=True, text=True, timeout=10).stdout.splitlines()
    urls: list[tuple[str, str]] = []
    ordered = [remote_name] + [name for name in names if name != remote_name]
    for name in ordered:
        url = runtime.git_remote_url(repo_root, name)
        parsed = runtime.parse_remote_url(url) if url else None
        if parsed is not None and parsed not in urls:
            urls.append(parsed)
    if len(urls) == 1:
        owner, repo = urls[0]
        return {"full_name": f"{owner}/{repo}", "source": f"git-remote:{remote_name}" if ordered and ordered[0] == remote_name else "git-remote"}
    if not urls:
        raise PickupError("repository-unresolved", "no compatible configured git remote or adapter repository was found")
    raise PickupError("repository-ambiguous", "multiple compatible git remotes resolve to different repositories", details={"repositories": sorted(f"{owner}/{repo}" for owner, repo in urls)})


def _read_goal_run(repo_root: Path, repo: str, number: int) -> tuple[dict[str, Any], Any, Any, dict[str, Any]]:
    cli = runpy.run_path(str(_issue_script("issue_tracker_cli")))
    resolved = cli["_resolve_backend"](repo_root)
    if not resolved.get("adapter_ok"):
        raise PickupError("adapter-invalid", "issue adapter is invalid", details=resolved.get("adapter"))
    provider = runpy.run_path(str(_issue_script("issue_goal_run")))
    preflight = provider["_preflight"](
        repo=repo,
        parent_number=number,
        operations=["read-body", "read-state", "list-children"],
        resolved=resolved,
    )
    if not preflight["ok"]:
        raise PickupError(str(preflight.get("status") or "provider-unavailable"), str(preflight.get("error") or "Goal Run provider is not ready"), details=preflight)
    try:
        graph = provider["_read_graph"](repo, number, resolved["backend"])
    except RuntimeError as exc:
        raise PickupError("provider-read-failed", str(exc)) from exc
    return graph, cli, provider, resolved


def pickup(repo_root: Path, objective: str) -> dict[str, Any]:
    number = parse_objective(objective)
    adapter_module = _load_path(_issue_script("resolve_adapter"), "issue_pickup_adapter")
    adapter = adapter_module.load_adapter(repo_root)
    if not adapter["valid"]:
        raise PickupError("adapter-invalid", "issue adapter is invalid", details=adapter)
    runtime = _load_path(_issue_script("issue_runtime"), "issue_pickup_runtime")
    repository = _resolve_repository(repo_root, adapter, runtime)
    repo = repository["full_name"]
    graph, cli, provider, resolved = _read_goal_run(repo_root, repo, number)
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
    metadata = validate_metadata(metadata, repo=repo, parent_number=number, parent_url=parent["url"])
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
        raise PickupError("graph-digest-mismatch", "parent initial graph hash differs from the immutable binding")
    children = list(graph["children"])
    if membership_digest(repo, number, children) != metadata["current_membership_sha256"]:
        raise PickupError("membership-stale", "provider graph differs from the parent current-membership hash")
    read = provider["READ"]
    hydrated: list[dict[str, Any]] = []
    for child in children:
        issue = read.read_issue_with_comments(repo, child["number"], backend=resolved["backend"])["issue"]
        hydrated.append({**child, "body": issue.get("body"), "comments": issue.get("comments", [])})
    selection = reconcile_and_select(hydrated, binding["approved_work_items"], repo=repo)
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
        "binding": {"path": metadata["binding_path"], "sha256": binding["binding_sha256"], "draft_sha256": binding["draft_sha256"]},
        "graph": {"count": len(children), "membership_sha256": metadata["current_membership_sha256"], "children": [{k: child[k] for k in ("number", "state", "url")} for child in children]},
        "selected_child": selection["selected_child"],
        "blocked_children": selection["blocked"],
        "invalid_open_children": selection["invalid_open"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select one executable child from an issue-native Goal Run")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
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
