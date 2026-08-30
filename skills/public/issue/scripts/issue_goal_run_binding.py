"""Issue-side adapters for the canonical Achieve Goal Binding contract."""

from __future__ import annotations

import hashlib
import importlib.util
import runpy
from pathlib import Path
from typing import Any


def _load_achieve(name: str, alias: str) -> Any:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "achieve" / "scripts" / f"{name}.py"
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(alias, candidate)
        if spec is None or spec.loader is None:
            raise ImportError(f"unable to load canonical Achieve module {candidate}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"canonical Achieve module {name!r} was not found")


BINDING = _load_achieve("goal_binding", "issue_goal_run_binding_contract")
PICKUP = _load_achieve("goal_run_pickup_contract", "issue_goal_run_pickup_contract")
_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
AMENDMENT = _load_local("issue_goal_run_parent_amendment", "issue_goal_run_parent_amendment_contract")
BindingError = BINDING.BindingError


def _parent_identity(repo: str, number: int) -> dict[str, Any]:
    return {
        "repo": repo,
        "number": number,
        "url": f"https://github.com/{repo}/issues/{number}",
    }


def load_binding(
    repo_root: Path,
    binding_path: Any,
    *,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
) -> dict[str, Any]:
    """Validate one complete binding, including its frozen draft bytes."""
    root = repo_root.resolve()
    try:
        path = Path(binding_path)
        structural = BINDING.validate_structural_binding(
            root,
            path,
            expected_parent=_parent_identity(repo, parent_number),
            expected_draft_sha256=draft_sha256,
            expected_binding_sha256=binding_sha256,
        )
        return BINDING.validate_binding(
            root,
            path,
            expected_parent=_parent_identity(repo, parent_number),
            expected_draft_path=structural["draft_path"],
            expected_draft_sha256=draft_sha256,
            expected_binding_sha256=binding_sha256,
        )
    except BINDING.BindingError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise BINDING.BindingError(
            "binding-invalid", f"could not validate Goal Binding: {exc}"
        ) from exc


def approved_issue_identities(binding: dict[str, Any]) -> set[tuple[str, int]]:
    """Return the immutable issue identities known by the binding."""
    return {
        (item["issue"]["repo"].casefold(), item["issue"]["number"])
        for item in binding["approved_work_items"]
        if isinstance(item.get("issue"), dict)
    }


def work_item_marker(key: str) -> str:
    return f"<!-- charness-work-item-key: {key} -->"


def require_expected_children(
    binding: dict[str, Any], children: list[dict[str, Any]], *, context: str
) -> None:
    actual = {
        (child.get("repo", binding["parent"]["repo"]).casefold(), child["number"])
        for child in children
    }
    reused = approved_issue_identities(binding)
    expected_count = len(binding["approved_work_items"])
    if len(actual) != len(children) or not reused.issubset(actual) or len(actual) != expected_count:
        raise RuntimeError(
            f"{context} issue identities differ from the immutable Goal Binding: "
            f"missing_reused={sorted(reused - actual)!r} "
            f"expected_count={expected_count} actual_count={len(actual)}"
        )


def work_item_for_target(
    binding: dict[str, Any], key: str, *, number: int | None = None, context: str = "Work Item"
) -> dict[str, Any]:
    matches = [item for item in binding["approved_work_items"] if item.get("key") == key]
    if len(matches) != 1:
        raise RuntimeError(
            f"{context} key {key!r} is not uniquely approved by the immutable Goal Binding"
        )
    item = matches[0]
    issue = item.get("issue")
    if number is not None:
        if (
            not isinstance(issue, dict)
            or issue.get("repo") != binding["parent"]["repo"]
            or issue.get("number") != number
        ):
            raise RuntimeError(
                f"{context} key {key!r} does not identify issue "
                f"{binding['parent']['repo']}#{number} in the immutable Goal Binding"
            )
    return item


def validate_managed_body(
    binding: dict[str, Any], *, key: str, number: int, body: bytes
) -> tuple[dict[str, Any], str]:
    item = work_item_for_target(binding, key, number=number)
    if item["body_policy"] not in {"managed", "managed-addendum"} or item["body_sha256"] is None:
        raise RuntimeError(f"Work Item {key!r} does not approve a managed body update")
    submitted = hashlib.sha256(body).hexdigest()
    if submitted != item["body_sha256"]:
        raise RuntimeError(
            f"submitted body digest for Work Item {key!r} differs from its approved body digest"
        )
    observed = item["observed"]
    return item, observed["body_sha256"]


def require_issue_matches_item(
    binding: dict[str, Any],
    *,
    key: str,
    number: int,
    issue: dict[str, Any],
) -> None:
    """Bind a provider-resolved create identity to its approved body bytes."""
    item = work_item_for_target(binding, key)
    if item["intent"] == "reuse":
        work_item_for_target(binding, key, number=number)
        return
    body = issue.get("body")
    if issue.get("number") != number or not isinstance(body, str):
        raise RuntimeError(f"created Work Item {key!r} provider readback is incomplete")
    if (
        body.count(work_item_marker(key)) != 1
        or hashlib.sha256(body.encode("utf-8")).hexdigest() != item["body_sha256"]
    ):
        raise RuntimeError(
            f"issue #{number} does not carry the approved body for created Work Item {key!r}"
        )


def require_created_children(binding: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    """Match every provider-assigned create identity to one immutable Work Item."""
    reused_numbers = {number for _, number in approved_issue_identities(binding)}
    created = [item for item in binding["approved_work_items"] if item["intent"] == "create"]
    candidates = [issue for issue in issues if issue.get("number") not in reused_numbers]
    if len(candidates) != len(created):
        raise RuntimeError("live created-child count differs from the immutable Goal Binding")
    unmatched = list(candidates)
    for item in created:
        matches = [
            issue
            for issue in unmatched
            if isinstance(issue.get("body"), str)
            and issue["body"].count(work_item_marker(item["key"])) == 1
            and hashlib.sha256(issue["body"].encode("utf-8")).hexdigest() == item["body_sha256"]
        ]
        if len(matches) != 1:
            raise RuntimeError(f"created Work Item {item['key']!r} does not map to one live child")
        unmatched.remove(matches[0])


def validate_parent_metadata(
    metadata: dict[str, Any],
    binding: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    parent_url: str | None = None,
) -> dict[str, Any]:
    """Validate Goal Run metadata against one complete binding, not a Work Item."""
    try:
        PICKUP.validate_metadata(
            metadata,
            repo=repo,
            parent_number=parent_number,
            parent_url=parent_url or _parent_identity(repo, parent_number)["url"],
        )
    except PICKUP.PickupError as exc:
        raise RuntimeError(str(exc)) from exc
    if metadata["binding_schema"] != binding["kind"]:
        raise RuntimeError(
            "Goal Run metadata binding schema differs from the immutable Goal Binding"
        )
    if metadata["binding_sha256"] != binding["binding_sha256"]:
        raise RuntimeError("Goal Run metadata binding hash differs from the immutable Goal Binding")
    if metadata["draft_sha256"] != binding["draft_sha256"]:
        raise RuntimeError("Goal Run metadata draft hash differs from the immutable Goal Binding")
    if metadata["initial_graph_sha256"] != binding["approved_work_items_sha256"]:
        raise RuntimeError(
            "Goal Run metadata initial graph differs from the immutable Goal Binding"
        )
    if metadata["parent_identity"] != binding["parent"]:
        raise RuntimeError("Goal Run metadata parent differs from the immutable Goal Binding")
    return metadata


def validate_parent_body_update(
    current_body: str,
    desired_body: str,
    *,
    binding: dict[str, Any],
    repo: str,
    parent_number: int,
    parent_url: str | None,
    guard: Any,
    amendment_authorization_file: Path | None = None,
) -> None:
    AMENDMENT.validate_parent_body_update(
        current_body,
        desired_body,
        binding=binding,
        repo=repo,
        parent_number=parent_number,
        parent_url=parent_url,
        guard=guard,
        validate_parent_metadata=validate_parent_metadata,
        canonical_json_bytes=BINDING.canonical_json_bytes,
        amendment_authorization_file=amendment_authorization_file,
    )


def parent_body_validator(
    binding: dict[str, Any],
    *,
    repo: str,
    parent_number: int,
    guard: Any,
    amendment_authorization_file: Path | None = None,
) -> Any:
    def validate(current_body: str, desired_body: str) -> None:
        validate_parent_body_update(
            current_body,
            desired_body,
            binding=binding,
            repo=repo,
            parent_number=parent_number,
            parent_url=f"https://github.com/{repo}/issues/{parent_number}",
            guard=guard,
            amendment_authorization_file=amendment_authorization_file,
        )

    return validate


def validate_operation_binding(
    operation: dict[str, Any], repo_root: Path, *, repo_file: Any, tracker: Any
) -> dict[str, Any] | None:
    """Validate immutable inputs before provider selection or mutation."""
    name = operation["operation"]
    bound = {"update-body", "create-or-reuse-child", "list-children", "add-child", "remove-child"}
    if name not in bound:
        return None
    binding = load_binding(
        repo_root,
        operation["binding_path"],
        repo=operation["repo"],
        parent_number=operation["parent_number"],
        draft_sha256=operation["draft_sha256"],
        binding_sha256=operation["binding_sha256"],
    )
    target = operation["target"]
    if (
        name == "update-body"
        and target["number"] == operation["parent_number"]
        and operation.get("amendment_authorization_file") is not None
    ):
        repo_file(
            repo_root,
            operation["amendment_authorization_file"],
            context="amendment_authorization_file",
        )
    if name == "update-body" and target["number"] != operation["parent_number"]:
        body = repo_file(repo_root, operation["body_file"], context="body_file").read_bytes()
        _, observed_sha256 = validate_managed_body(
            binding, key=target["work_item_key"], number=target["number"], body=body
        )
        operation["observed_body_sha256"] = observed_sha256
    elif name == "create-or-reuse-child":
        body = repo_file(repo_root, operation["body_file"], context="body_file").read_bytes()
        item = work_item_for_target(binding, target["work_item_key"])
        if item["intent"] != "create":
            raise RuntimeError("create-or-reuse-child requires an approved create Work Item")
        if hashlib.sha256(body).hexdigest() != item["body_sha256"]:
            raise RuntimeError("submitted child body differs from the approved Work Item body")
    elif name == "list-children":
        expected_path = repo_file(
            repo_root, operation["expected_child_file"], context="expected_child_file"
        )
        expected = tracker.load_expected_child_set(
            expected_path, repo=operation["repo"], parent_number=operation["parent_number"]
        )
        require_expected_children(
            binding,
            [{"repo": operation["repo"], "number": number} for number in expected["children"]],
            context="expected child set",
        )
    elif name in {"add-child", "remove-child"}:
        item = work_item_for_target(binding, target["work_item_key"])
        if item["intent"] == "reuse":
            work_item_for_target(
                binding,
                target["work_item_key"],
                number=target["sub_issue_number"],
                context=f"{name} target",
            )
    return binding
