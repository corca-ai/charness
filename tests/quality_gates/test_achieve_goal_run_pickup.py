from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_run_pickup.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("goal_run_pickup_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pickup = _load_module()


REPO = "corca-ai/charness"
PARENT_NUMBER = 724
PARENT_URL = f"https://github.com/{REPO}/issues/{PARENT_NUMBER}"
PARENT_API_URL = f"https://api.github.com/repos/{REPO}/issues/{PARENT_NUMBER}"
GOAL_RUN_SCHEMA = "charness.goal-binding/v1"
VERIFIED_BOOTSTRAP = "verified-target-roundtrip"


def _sha(char: str) -> str:
    return char * 64


def _metadata(*, bootstrap: str = VERIFIED_BOOTSTRAP) -> dict[str, object]:
    return {
        "binding_schema": GOAL_RUN_SCHEMA,
        "binding_path": "charness-artifacts/goals/demo.binding.json",
        "binding_sha256": _sha("a"),
        "draft_path": "charness-artifacts/goals/demo.md",
        "draft_sha256": _sha("b"),
        "initial_graph_sha256": _sha("c"),
        "current_membership_sha256": _sha("d"),
        "bootstrap_verification": bootstrap,
        "parent_identity": {"repo": REPO, "number": PARENT_NUMBER, "url": PARENT_URL},
    }


def _child(
    number: int,
    *,
    state: str = "OPEN",
    key: str | None = None,
    title: str | None = None,
) -> dict[str, object]:
    body = None
    if key is not None:
        body = (
            f"<!-- charness-work-item-key: {key} -->\n"
            f"# {title or key}\n\n"
            "## Purpose\nDo the bounded work.\n\n"
            "## Bounded contract\nOwn the change.\n\n"
            "## Acceptance and verification\nRun the proof.\n\n"
            "## Evidence boundary\nRecord non-claims.\n"
        )
    return {
        "repo": REPO,
        "number": number,
        "state": state,
        "title": title or f"issue {number}",
        "url": f"https://github.com/{REPO}/issues/{number}",
        "parent_issue_url": PARENT_API_URL,
        "body": body,
    }


def _item(
    key: str,
    *,
    rank: int,
    dependencies: list[str] | None = None,
    issue: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "key": key,
        "rank": rank,
        "dependencies": dependencies or [],
        "issue": issue,
    }


def test_objective_accepts_only_trimmed_goal_number() -> None:
    assert pickup.parse_objective("  /goal #724  ") == 724
    for value in ("/goal @demo.md", "/goal #0", "/goal #724 extra", "/goal\t#724"):
        with pytest.raises(pickup.PickupError) as exc_info:
            pickup.parse_objective(value)
        assert exc_info.value.code == "objective-invalid"


def test_pending_bootstrap_is_a_typed_refusal_after_identity_is_complete() -> None:
    metadata = _metadata(bootstrap="pending-target-roundtrip")

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.validate_metadata(
            metadata,
            repo=REPO,
            parent_number=PARENT_NUMBER,
            parent_url=PARENT_URL,
        )

    assert exc_info.value.code == "establishment-pending"
    assert exc_info.value.details == {"bootstrap_verification": "pending-target-roundtrip"}


def test_membership_digest_is_order_independent_and_rejects_foreign_identity() -> None:
    children = [_child(726), _child(734)]
    expected = pickup.membership_digest(REPO, PARENT_NUMBER, children)

    assert pickup.membership_digest(REPO, PARENT_NUMBER, list(reversed(children))) == expected

    foreign = [dict(children[0], url="https://github.com/other/repo/issues/726"), children[1]]
    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.membership_digest(REPO, PARENT_NUMBER, foreign)
    assert exc_info.value.code == "graph-identity-mismatch"


def test_reconcile_maps_created_items_by_marker_and_selects_satisfied_rank() -> None:
    binding_items = [
        _item("provider", rank=1),
        _item("binding", rank=2, dependencies=["provider"]),
        _item(
            "closed",
            rank=3,
            issue={"repo": REPO, "number": 628, "url": f"https://github.com/{REPO}/issues/628"},
        ),
    ]
    children = [
        _child(726, key="provider"),
        _child(734, key="binding"),
        _child(628, state="CLOSED"),
    ]

    result = pickup.reconcile_and_select(children, binding_items, repo=REPO)

    assert result["selected_child"]["key"] == "provider"
    assert result["blocked"] == [{"key": "binding", "number": 734, "unmet_dependencies": ["provider"]}]
    assert result["invalid_open"] == []


def test_reconcile_refuses_open_child_without_executable_body() -> None:
    items = [_item("provider", rank=1)]
    child = _child(726, key="provider")
    child["body"] = "<!-- charness-work-item-key: provider -->\n# Missing contract"

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.reconcile_and_select([child], items, repo=REPO)

    assert exc_info.value.code == "no-executable-child"
    assert exc_info.value.details["invalid_open"][0]["number"] == 726


def test_pickup_refuses_closed_parent_before_binding_or_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    metadata = _metadata()
    parent = {
        "repo": REPO,
        "number": PARENT_NUMBER,
        "state": "CLOSED",
        "url": PARENT_URL,
        "body": "<!-- charness-goal-run:v1\n" + json.dumps(metadata) + "\n-->\n",
    }
    graph = {"parent": parent, "children": []}

    monkeypatch.setattr(
        pickup,
        "_load_path",
        lambda _path, name: (
            SimpleNamespace(load_adapter=lambda _root: {"valid": True, "data": {}})
            if name == "issue_pickup_adapter"
            else SimpleNamespace(parse_goal_run_metadata=lambda *_args, **_kwargs: metadata)
            if name == "issue_pickup_guard"
            else SimpleNamespace()
        ),
    )
    monkeypatch.setattr(pickup, "_resolve_repository", lambda *_args: {"full_name": REPO, "source": "fixture"})
    monkeypatch.setattr(pickup, "_read_goal_run", lambda *_args: (graph, None, None, {"adapter_ok": True, "backend": {}}))

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(ROOT, "/goal #724")

    assert exc_info.value.code == "parent-closed"


def test_pickup_selects_from_fresh_hydrated_provider_state_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_item = _item("provider", rank=1)
    binding_item = _item("binding", rank=2, dependencies=["provider"])
    closed_item = _item(
        "closed",
        rank=3,
        issue={"repo": REPO, "number": 628, "url": f"https://github.com/{REPO}/issues/628"},
    )
    items = [provider_item, binding_item, closed_item]
    children = [_child(726, key="provider"), _child(734, key="binding"), _child(628, state="CLOSED")]
    membership = pickup.membership_digest(REPO, PARENT_NUMBER, children)
    metadata = _metadata()
    metadata["current_membership_sha256"] = membership
    metadata["initial_graph_sha256"] = _sha("e")
    parent = {
        "repo": REPO,
        "number": PARENT_NUMBER,
        "state": "OPEN",
        "url": PARENT_URL,
        "body": "goal body",
    }
    graph = {"parent": parent, "children": children}
    fake_read = SimpleNamespace(
        read_issue_with_comments=lambda _repo, number, *, backend: {
            "issue": next(child for child in children if child["number"] == number) | {"comments": []}
        }
    )
    fake_provider = {"READ": fake_read}
    fake_binding = SimpleNamespace(
        validate_binding=lambda *_args, **_kwargs: {
            "binding_sha256": metadata["binding_sha256"],
            "draft_sha256": metadata["draft_sha256"],
            "approved_work_items_sha256": metadata["initial_graph_sha256"],
            "approved_work_items": items,
        }
    )
    fake_guard = SimpleNamespace(parse_goal_run_metadata=lambda *_args, **_kwargs: metadata)

    def fake_load(_path: Path, name: str):
        if name == "issue_pickup_adapter":
            return SimpleNamespace(load_adapter=lambda _root: {"valid": True, "data": {}})
        if name == "issue_pickup_runtime":
            return SimpleNamespace()
        if name == "issue_pickup_guard":
            return fake_guard
        if name == "issue_pickup_binding":
            return fake_binding
        raise AssertionError(name)

    monkeypatch.setattr(pickup, "_load_path", fake_load)
    monkeypatch.setattr(pickup, "_resolve_repository", lambda *_args: {"full_name": REPO, "source": "fixture"})
    monkeypatch.setattr(
        pickup,
        "_read_goal_run",
        lambda *_args: (graph, None, fake_provider, {"adapter_ok": True, "backend": {}}),
    )

    result = pickup.pickup(ROOT, "/goal #724")

    assert result["ok"] is True
    assert result["outcome"] == "verified-read"
    assert result["mutation_invoked"] is False
    assert result["selected_child"]["key"] == "provider"
    assert result["graph"]["membership_sha256"] == membership
