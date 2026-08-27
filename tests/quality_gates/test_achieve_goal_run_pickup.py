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
        "progress": {
            "schema": "charness.goal-progress/v1",
            "revision": 1,
            "total": 3,
            "completed": 1,
            "open": 2,
            "membership_sha256": _sha("d"),
            "next": {
                "key": "provider",
                "repo": REPO,
                "number": 726,
                "url": f"https://github.com/{REPO}/issues/726",
                "state": "OPEN",
            },
        },
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


def test_parent_progress_selects_without_child_state_or_body_reads() -> None:
    metadata = _metadata()
    items = [_item("provider", rank=1), _item("other", rank=1)]

    progress = pickup.validate_progress(metadata, items, repo=REPO, parent_number=PARENT_NUMBER)
    result = pickup.select_from_parent_progress(progress, items, repo=REPO)

    assert result["selected_child"]["key"] == "provider"
    assert result["selected_child"]["number"] == 726
    assert result["selected_child"]["selection_source"] == "parent-progress"
    assert result["blocked"] == []
    assert result["invalid_open"] == []


def test_parent_progress_is_required_instead_of_implicit_full_graph_fallback() -> None:
    metadata = _metadata()
    del metadata["progress"]

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.validate_progress(
            metadata,
            [_item("provider", rank=1)],
            repo=REPO,
            parent_number=PARENT_NUMBER,
        )

    assert exc_info.value.code == "progress-sync-required"


def test_parent_read_fast_path_does_one_live_read_without_goal_run_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, int]] = []
    issue = {
        "number": PARENT_NUMBER,
        "title": "Goal Run",
        "state": "OPEN",
        "url": PARENT_URL,
        "body": "parent body",
        "comments": [],
    }
    resolved = {"adapter_ok": True, "backend": {"id": "gh", "binary": "gh"}}

    class Selection:
        @staticmethod
        def select_backend(_root: Path) -> dict[str, object]:
            return dict(resolved)

        @staticmethod
        def bind_provider_selection(
            value: dict[str, object], *, target_repo: str, operations: list[str]
        ) -> dict[str, object]:
            assert target_repo == REPO
            assert operations == ["read-body", "read-state"]
            return value

    class Reader:
        @staticmethod
        def read_issue_with_comments(
            repo: str, number: int, *, backend: dict[str, object]
        ) -> dict[str, object]:
            calls.append((repo, number))
            assert backend == resolved["backend"]
            return {"issue": issue}

    def fake_load(_path: Path, name: str):
        if name == "issue_pickup_selection":
            return Selection
        if name == "issue_pickup_read":
            return Reader
        raise AssertionError(f"routine pickup loaded unexpected module: {name}")

    monkeypatch.setattr(pickup, "_load_path", fake_load)

    graph, actual = pickup._read_goal_parent(ROOT, REPO, PARENT_NUMBER)

    assert calls == [(REPO, PARENT_NUMBER)]
    assert graph["parent"]["body"] == "parent body"
    assert actual == resolved


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
    monkeypatch.setattr(pickup, "_read_goal_parent", lambda *_args: (graph, {"adapter_ok": True, "backend": {}}))

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(ROOT, "/goal #724")

    assert exc_info.value.code == "parent-closed"


def test_pickup_selects_from_parent_cursor_without_child_reads_or_mutation(
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
    membership = _sha("d")
    metadata = _metadata()
    metadata["current_membership_sha256"] = membership
    metadata["initial_graph_sha256"] = _sha("e")
    metadata["progress"] = {
        "schema": "charness.goal-progress/v1",
        "revision": 4,
        "total": 3,
        "completed": 1,
        "open": 2,
        "membership_sha256": membership,
        "next": {
            "key": "provider",
            "repo": REPO,
            "number": 726,
            "url": f"https://github.com/{REPO}/issues/726",
            "state": "OPEN",
        },
    }
    parent = {
        "repo": REPO,
        "number": PARENT_NUMBER,
        "state": "OPEN",
        "url": PARENT_URL,
        "body": "goal body",
    }
    graph = {"parent": parent, "children": []}
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
        "_read_goal_parent",
        lambda *_args: (graph, {"adapter_ok": True, "backend": {}}),
    )

    result = pickup.pickup(ROOT, "/goal #724")

    assert result["ok"] is True
    assert result["outcome"] == "verified-read"
    assert result["mutation_invoked"] is False
    assert result["selected_child"]["key"] == "provider"
    assert result["graph"]["membership_sha256"] == membership
    assert result["selection"] == {"source": "parent-progress", "child_reads": 0}
