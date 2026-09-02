"""Issue-side adapters for the canonical Achieve Goal Binding contract."""

from __future__ import annotations

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
AMENDMENT = _load_local(
    "issue_goal_run_parent_amendment", "issue_goal_run_parent_amendment_contract"
)
BindingError = BINDING.BindingError
OPERATION_IDENTITY_FIELDS = ("binding_path", "draft_sha256", "binding_sha256")


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
    """Validate one complete binding, including its frozen draft identity."""
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


def amended_items(metadata: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Work Items the parent appended after binding (validated by the pickup contract)."""
    if not metadata:
        return []
    PICKUP.validate_amendments(metadata.get("amendments"), repo=metadata["parent_identity"]["repo"])
    return PICKUP.amendment_items(metadata)


def all_work_items(
    binding: dict[str, Any], metadata: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return PICKUP.effective_work_items(binding["approved_work_items"], metadata or {})


def require_expected_children(
    binding: dict[str, Any],
    children: list[dict[str, Any]],
    *,
    context: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    actual = {
        (child.get("repo", binding["parent"]["repo"]).casefold(), child["number"])
        for child in children
    }
    known = approved_issue_identities(binding) | {
        (item["issue"]["repo"].casefold(), item["issue"]["number"])
        for item in amended_items(metadata)
    }
    expected_count = len(all_work_items(binding, metadata))
    if len(actual) != len(children) or not known.issubset(actual) or len(actual) != expected_count:
        raise RuntimeError(
            f"{context} issue identities differ from the Goal Run's approved Work Items: "
            f"missing_known={sorted(known - actual)!r} "
            f"expected_count={expected_count} actual_count={len(actual)}"
        )


def work_item_for_target(
    binding: dict[str, Any],
    key: str,
    *,
    number: int | None = None,
    context: str = "Work Item",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    matches = [item for item in all_work_items(binding, metadata) if item.get("key") == key]
    if len(matches) != 1:
        raise RuntimeError(
            f"{context} key {key!r} is not an approved Work Item (binding or parent amendment)"
        )
    item = matches[0]
    issue = item.get("issue")
    # A created Work Item's number is assigned by the provider and is not in the
    # binding; its identity is the marker, which the body checks enforce.
    if number is not None and not (item.get("intent") == "create" and issue is None):
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


def require_marker(key: str, body: bytes | str, *, context: str) -> None:
    """A child's identity is its work-item marker, present exactly once."""
    text = body.decode("utf-8") if isinstance(body, bytes) else body
    if text.count(work_item_marker(key)) != 1:
        raise RuntimeError(f"{context} must carry the marker for Work Item {key!r} exactly once")


def validate_managed_body(
    binding: dict[str, Any],
    *,
    key: str,
    number: int,
    body: bytes,
    metadata: dict[str, Any] | None = None,
) -> None:
    """A child body may change; only its identity marker is enforced.

    Prose is reversible and visible in the provider's edit history, so it is not
    hashed. The marker is the only child-body identity this operation enforces.
    """
    item = work_item_for_target(binding, key, number=number, metadata=metadata)
    if item["intent"] == "reuse" and item.get("body_policy") == "preserve-closed-evidence":
        raise RuntimeError(
            f"Work Item {key!r} preserves closed evidence and does not accept a body update"
        )
    require_marker(key, body, context=f"submitted body for Work Item {key!r}")


def resolve_operation_identity(
    operation: dict[str, Any], parent_metadata: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Fill operation identity from live parent metadata and check repetitions."""
    metadata = parent_metadata
    if metadata is None and isinstance(operation.get("parent_metadata"), dict):
        metadata = operation["parent_metadata"]
    if metadata is None:
        if all(operation.get(field) is not None for field in OPERATION_IDENTITY_FIELDS):
            return None
        raise BindingError(
            "identity-required",
            "provider-backed Goal Run operation needs parent metadata to resolve "
            "binding_path, draft_sha256, and binding_sha256",
        )
    try:
        PICKUP.validate_metadata(
            metadata,
            repo=operation["repo"],
            parent_number=operation["parent_number"],
            parent_url=metadata.get("parent_identity", {}).get("url"),
        )
    except (PICKUP.PickupError, AttributeError, KeyError, TypeError, ValueError) as exc:
        raise BindingError("identity-invalid", f"parent metadata is invalid: {exc}") from exc
    missing = [field for field in OPERATION_IDENTITY_FIELDS if field not in metadata]
    if missing:
        raise BindingError(
            "identity-required",
            f"parent metadata is missing Goal Run identities {missing!r}",
        )
    for field in OPERATION_IDENTITY_FIELDS:
        expected = metadata[field]
        carried = operation.get(field)
        if carried is not None and carried != expected:
            raise BindingError(
                "identity-mismatch",
                f"operation {field} differs from parent metadata: "
                f"operation={carried!r}, parent={expected!r}",
            )
        operation[field] = expected
    operation["parent_metadata"] = metadata
    return metadata


def require_issue_matches_item(
    binding: dict[str, Any],
    *,
    key: str,
    number: int,
    issue: dict[str, Any],
) -> None:
    """Bind a provider-resolved create identity to its approved Work Item."""
    item = work_item_for_target(binding, key)
    if item["intent"] == "reuse":
        work_item_for_target(binding, key, number=number)
        return
    body = issue.get("body")
    if issue.get("number") != number or not isinstance(body, str):
        raise RuntimeError(f"created Work Item {key!r} provider readback is incomplete")
    if item["intent"] == "amended":
        if item["issue"]["number"] != number:
            raise RuntimeError(f"issue #{number} is not the amended Work Item {key!r}")
        return
    require_marker(key, body, context=f"issue #{number}")


def require_created_children(
    binding: dict[str, Any],
    issues: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Match every non-reused live child to one approved Work Item by identity."""
    reused_numbers = {number for _, number in approved_issue_identities(binding)}
    amended = {item["issue"]["number"]: item for item in amended_items(metadata)}
    created = [item for item in binding["approved_work_items"] if item["intent"] == "create"]
    candidates = [
        issue
        for issue in issues
        if issue.get("number") not in reused_numbers and issue.get("number") not in amended
    ]
    if len(candidates) != len(created):
        raise RuntimeError("live created-child count differs from the approved Work Items")
    unmatched = list(candidates)
    for item in created:
        matches = [
            issue
            for issue in unmatched
            if isinstance(issue.get("body"), str)
            and issue["body"].count(work_item_marker(item["key"])) == 1
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
    operation: dict[str, Any],
    repo_root: Path,
    *,
    repo_file: Any,
    tracker: Any,
    parent_metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Validate immutable inputs before provider selection or mutation."""
    resolve_operation_identity(operation, parent_metadata)
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
    metadata = operation.get("parent_metadata")
    if name == "update-body" and target["number"] != operation["parent_number"]:
        body = repo_file(repo_root, operation["body_file"], context="body_file").read_bytes()
        validate_managed_body(
            binding,
            key=target["work_item_key"],
            number=target["number"],
            body=body,
            metadata=metadata,
        )
    elif name == "create-or-reuse-child":
        body = repo_file(repo_root, operation["body_file"], context="body_file").read_bytes()
        item = work_item_for_target(binding, target["work_item_key"])
        if item["intent"] != "create":
            raise RuntimeError("create-or-reuse-child requires an approved create Work Item")
        require_marker(target["work_item_key"], body, context="submitted child body")
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
            metadata=metadata,
        )
    elif name in {"add-child", "remove-child"}:
        amendment = operation.get("amendment")
        if amendment is not None:
            # Graph amendment: an operator-approved Work Item appended to a live run.
            entry = {
                **amendment,
                "key": target["work_item_key"],
                "repo": operation["repo"],
                "number": target["sub_issue_number"],
                "url": f"https://github.com/{operation['repo']}/issues/{target['sub_issue_number']}",
            }
            PICKUP.validate_amendments([entry], repo=operation["repo"])
            if any(item["key"] == entry["key"] for item in all_work_items(binding, metadata)):
                raise RuntimeError(
                    f"amendment key {entry['key']!r} is already an approved Work Item"
                )
            operation["amendment_entry"] = entry
            return binding
        item = work_item_for_target(binding, target["work_item_key"], metadata=metadata)
        if item["intent"] in {"reuse", "amended"}:
            work_item_for_target(
                binding,
                target["work_item_key"],
                number=target["sub_issue_number"],
                context=f"{name} target",
                metadata=metadata,
            )
    return binding
