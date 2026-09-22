from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SUPPORT_PATH = ROOT / "skills/public/achieve/scripts/goal_binding_support.py"
EDGES_PATH = ROOT / "skills/public/achieve/scripts/goal_dependency_edges.py"
AMENDMENTS_PATH = ROOT / "skills/public/achieve/scripts/goal_run_amendments.py"
BINDING_PATH = ROOT / "skills/public/achieve/scripts/goal_binding.py"
PICKUP_PATH = ROOT / "skills/public/achieve/scripts/goal_run_pickup_contract.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


support = _load(SUPPORT_PATH, "binding_support_828")
edges = _load(EDGES_PATH, "dependency_edges_828")
amendments = _load(AMENDMENTS_PATH, "run_amendments_828")
binding = _load(BINDING_PATH, "goal_binding_828")
pickup = _load(PICKUP_PATH, "pickup_contract_828")

REPO = "corca-ai/charness"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _parent():
    return {
        "repo": REPO,
        "number": 724,
        "url": f"https://github.com/{REPO}/issues/724",
    }


def _created(key, dependencies=None, rank=1, kinds=None):
    item = {
        "key": key,
        "intent": "create",
        "issue": None,
        "dependencies": dependencies or [],
        "rank": rank,
        "observed": None,
    }
    if kinds is not None:
        item["dependency_kinds"] = kinds
    return item


def _approval():
    return {"response": "ok", "session_id": "s", "observed_at": "t"}


def test_soft_edge_ignores_rank_and_cycle():
    items = [
        _created("a", rank=2),
        _created("b", dependencies=["a"], rank=1, kinds={"a": "soft"}),
    ]
    validated = support._validate_manifest(items, parent=_parent())
    assert edges.hard_dependencies(validated[1]) == []
    assert edges.ready_frontier(validated, set()) == ["a", "b"]


def test_hard_edge_still_enforces_rank_and_cycle():
    with pytest.raises(support.BindingError, match="dependency-rank-invalid"):
        support._validate_manifest(
            [_created("a", rank=2), _created("b", dependencies=["a"], rank=1)],
            parent=_parent(),
        )
    with pytest.raises(support.BindingError, match="dependency-cycle"):
        support._validate_manifest(
            [_created("a", dependencies=["b"], rank=2), _created("b", dependencies=["a"], rank=3)],
            parent=_parent(),
        )


def test_unknown_edge_kind_and_unknown_dep_refused():
    with pytest.raises(support.BindingError, match="unknown edge kinds"):
        support._validate_manifest(
            [_created("a", rank=1), _created("b", dependencies=["a"], rank=2, kinds={"a": "maybe"})],
            parent=_parent(),
        )
    with pytest.raises(support.BindingError, match="unknown dependencies"):
        support._validate_manifest(
            [_created("a", rank=1), _created("b", dependencies=["a"], rank=2, kinds={"zzz": "soft"})],
            parent=_parent(),
        )


def test_integration_gate_does_not_gate_start():
    items = support._validate_manifest(
        [
            _created("a", rank=1),
            _created("b", dependencies=["a"], rank=2, kinds={"a": "integration-gate"}),
        ],
        parent=_parent(),
    )
    assert edges.ready_frontier(items, set()) == ["a", "b"]
    assert edges.ready_frontier(items, {"a"}) == ["a", "b"]


def test_build_binding_accepts_typed_edges():
    payload = binding.build_binding(
        draft_path="charness-artifacts/goals/demo.md",
        draft_sha256=_sha("draft"),
        briefing_sha256=_sha("briefing"),
        approval_response="ok",
        approval_session_id="s",
        approval_observed_at="t",
        parent=_parent(),
        approved_work_items=[
            _created("a", rank=1),
            _created("b", dependencies=["a"], rank=2, kinds={"a": "soft"}),
        ],
    )
    item = next(i for i in payload["approved_work_items"] if i["key"] == "b")
    assert item["dependency_kinds"] == {"a": "soft"}


def _amendment(key, number, rank=2, deps=None, kinds=None):
    entry = {
        "key": key,
        "repo": REPO,
        "number": number,
        "url": f"https://github.com/{REPO}/issues/{number}",
        "rank": rank,
        "dependencies": deps or [],
        "reason": "speed",
        "approval": _approval(),
    }
    if kinds is not None:
        entry["dependency_kinds"] = kinds
    return entry


def test_legacy_amendment_defaults_to_add_child_and_overlay_applies():
    legacy = [_amendment("c", 730)]
    validated = pickup.validate_amendments(legacy, repo=REPO)
    assert validated[0]["kind"] == "add-child"
    items = [{"key": "a", "rank": 1, "dependencies": []}, {"key": "b", "rank": 2, "dependencies": ["a"]}]
    metadata = {
        "amendments": [
            {
                "kind": "dependency-amendment",
                "key": "b",
                "dependencies": ["a"],
                "dependency_kinds": {"a": "soft"},
                "reason": "run alongside",
                "approval": _approval(),
            }
        ]
    }
    effective = pickup.effective_work_items(items, metadata)
    target = next(i for i in effective if i["key"] == "b")
    assert target["dependency_kinds"] == {"a": "soft"}
    assert pickup.ready_frontier(effective, set()) == ["a", "b"]


def _overlay(key="b", deps=None, kinds=None, **extra):
    entry = {
        "kind": "dependency-amendment",
        "key": key,
        "dependencies": deps if deps is not None else ["a"],
        "reason": "run alongside",
        "approval": _approval(),
    }
    if kinds is not None:
        entry["dependency_kinds"] = kinds
    entry.update(extra)
    return entry


def test_overlay_guards_shape_before_applying() -> None:
    with pytest.raises(amendments.PickupError, match="duplicate overlay"):
        amendments.validate_amendments(
            [_overlay(), _overlay()], repo=REPO
        )
    with pytest.raises(amendments.PickupError, match="wrong fields"):
        amendments.validate_amendments([_overlay(rank=3)], repo=REPO)
    with pytest.raises(amendments.PickupError, match="not canonical"):
        amendments.validate_amendments([_overlay(deps=["a", "a"])], repo=REPO)
    with pytest.raises(amendments.PickupError, match="key is invalid"):
        amendments.validate_amendments([_overlay(key="Bad")], repo=REPO)


def test_overlay_without_kinds_clears_target_kinds() -> None:
    items = [
        {"key": "a", "rank": 1, "dependencies": []},
        {"key": "b", "rank": 2, "dependencies": ["a"], "dependency_kinds": {"a": "soft"}},
    ]
    metadata = {"amendments": [_overlay(kinds=None) | {"dependencies": []}]}
    effective = amendments.effective_work_items(items, metadata)
    target = next(i for i in effective if i["key"] == "b")
    assert target["dependencies"] == []
    assert "dependency_kinds" not in target


def test_projection_skips_non_object_entries() -> None:
    metadata = {"amendments": [None, "stray", _overlay()]}
    assert [o["key"] for o in amendments.dependency_overlays(metadata)] == ["b"]
    assert amendments.amendment_items(metadata) == []
    assert amendments.amendment_items({"amendments": [_overlay()]}) == []


def _child(key="c", number=730, **over):
    entry = {
        "key": key,
        "repo": REPO,
        "number": number,
        "url": f"https://github.com/{REPO}/issues/{number}",
        "rank": 2,
        "dependencies": [],
        "reason": "speed",
        "approval": _approval(),
    }
    entry.update(over)
    return entry


def test_add_child_top_level_guards() -> None:
    assert amendments.validate_amendments(None, repo=REPO) == []
    with pytest.raises(amendments.PickupError, match="must be a list"):
        amendments.validate_amendments("nope", repo=REPO)
    with pytest.raises(amendments.PickupError, match="must be an object"):
        amendments.validate_amendments([None], repo=REPO)
    with pytest.raises(amendments.PickupError, match="unknown amendment"):
        amendments.validate_amendments([_child(kind="nope")], repo=REPO)
    with pytest.raises(amendments.PickupError, match="key is invalid"):
        amendments.validate_amendments([_child(key="Bad")], repo=REPO)
    with pytest.raises(amendments.PickupError, match="dependencies are invalid"):
        amendments.validate_amendments([_child(dependencies="x")], repo=REPO)
    with pytest.raises(amendments.PickupError, match="duplicated"):
        amendments.validate_amendments([_child(), _child()], repo=REPO)


def test_add_child_field_guards() -> None:
    with pytest.raises(amendments.PickupError, match="reason must be non-empty"):
        amendments.validate_amendments([_child(reason="  ")], repo=REPO)
    with pytest.raises(amendments.PickupError, match="approval must record"):
        amendments.validate_amendments([_child(approval={})], repo=REPO)
    no_repo = {k: v for k, v in _child().items() if k != "repo"}
    with pytest.raises(amendments.PickupError, match="missing 'repo'"):
        amendments.validate_amendments([no_repo], repo=REPO)
    with pytest.raises(amendments.PickupError, match="wrong fields"):
        amendments.validate_amendments([_child(extra=1)], repo=REPO)
    with pytest.raises(amendments.PickupError, match="differs"):
        amendments.validate_amendments([_child(repo="other/x")], repo=REPO)
    with pytest.raises(amendments.PickupError, match="positive integer"):
        amendments.validate_amendments([_child(number=0)], repo=REPO)
    with pytest.raises(amendments.PickupError, match="does not match"):
        amendments.validate_amendments(
            [_child(url="https://github.com/other/x/issues/1")], repo=REPO
        )
    with pytest.raises(amendments.PickupError, match="rank must be positive"):
        amendments.validate_amendments([_child(rank=0)], repo=REPO)


def test_add_child_projection_and_collision() -> None:
    items = amendments.amendment_items({"amendments": [_child(dependency_kinds={})]})
    assert items[0]["dependency_kinds"] == {}
    plain = amendments.amendment_items({"amendments": [_child()]})
    assert "dependency_kinds" not in plain[0]
    binding = [{"key": "c", "rank": 1, "dependencies": []}]
    with pytest.raises(amendments.PickupError, match="collides"):
        amendments.effective_work_items(binding, {"amendments": [_child()]})
    grown = amendments.effective_work_items(
        [{"key": "a", "rank": 1, "dependencies": []}], {"amendments": [_child()]}
    )
    assert [item["key"] for item in grown] == ["a", "c"]


def test_overlay_unknown_target_refused():
    items = [{"key": "a", "rank": 1, "dependencies": []}]
    metadata = {
        "amendments": [
            {
                "kind": "dependency-amendment",
                "key": "zzz",
                "dependencies": [],
                "reason": "x",
                "approval": _approval(),
            }
        ]
    }
    pickup.validate_amendments(metadata["amendments"], repo=REPO)
    with pytest.raises(pickup.PickupError, match="unknown Work Item"):
        pickup.effective_work_items(items, metadata)


def test_validate_edge_kinds_refuses_non_mapping() -> None:
    with pytest.raises(ValueError, match="dependency_kinds are invalid"):
        edges.validate_edge_kinds(
            ["hard"], [], context="work item 'b'", error=ValueError, code="schema-invalid"
        )


def _run_bare_module(tmp_path: Path, rel: str, attr: str) -> None:
    """Import one script in a fresh interpreter with no repo root on sys.path.

    Each module runs alone so its import bootstrap executes exactly as it
    does when the skill entrypoint loads the script standalone.
    """
    import subprocess
    import sys

    code = (
        "import runpy, sys; "
        "sys.path[:] = [p for p in sys.path if 'charness' not in p]; "
        f"m = runpy.run_path({str(ROOT / rel)!r}); "
        f"assert {attr!r} in m, sorted(m)"
    )
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_standalone_skill_modules_import_without_repo_root_on_path(tmp_path: Path) -> None:
    _run_bare_module(tmp_path, "skills/public/achieve/scripts/goal_dependency_edges.py", "EDGE_KINDS")
    _run_bare_module(tmp_path, "skills/public/achieve/scripts/goal_run_amendments.py", "PickupError")
    _run_bare_module(tmp_path, "skills/public/achieve/scripts/goal_binding_support.py", "SCHEMA")
    _run_bare_module(
        tmp_path, "skills/public/achieve/scripts/goal_run_pickup_contract.py", "PROGRESS_SCHEMA"
    )


def test_cursor_ready_keys_must_contain_next():
    items = [{"key": "a", "rank": 1, "dependencies": []}, {"key": "b", "rank": 2, "dependencies": []}]
    base = {
        "binding_schema": "charness.goal-binding/v1",
        "binding_path": "d.binding.json",
        "binding_sha256": "a" * 64,
        "draft_path": "d.md",
        "draft_sha256": "b" * 64,
        "initial_graph_sha256": "c" * 64,
        "bootstrap_verification": "verified-target-roundtrip",
        "parent_identity": {"repo": REPO, "number": 724, "url": f"https://github.com/{REPO}/issues/724"},
        "progress": {
            "schema": "charness.goal-progress/v1",
            "revision": 1,
            "total": 2,
            "completed": 0,
            "open": 2,
            "next": {"key": "a", "repo": REPO, "number": 725, "url": f"https://github.com/{REPO}/issues/725", "state": "OPEN"},
            "ready_keys": ["a", "b"],
        },
    }
    progress = pickup.validate_progress(base, items, repo=REPO, parent_number=724)
    selected = pickup.select_from_parent_progress(progress, items, repo=REPO)
    assert selected["ready_keys"] == ["a", "b"]
    bad = next(i for i in [dict(base)] for _ in [0])
    bad["progress"] = dict(base["progress"], ready_keys=["b"])
    with pytest.raises(pickup.PickupError, match="ready frontier"):
        pickup.validate_progress(bad, items, repo=REPO, parent_number=724)
    for ready_keys, match in [
        (["b", "a"], "sorted unique"),
        (["a", "zzz"], "unknown items"),
    ]:
        mutated = dict(base)
        mutated["progress"] = dict(base["progress"], ready_keys=ready_keys)
        with pytest.raises(pickup.PickupError, match=match):
            pickup.validate_progress(mutated, items, repo=REPO, parent_number=724)
    done = dict(base)
    done["progress"] = dict(
        base["progress"], completed=2, open=0, next=None, ready_keys=["a"]
    )
    with pytest.raises(pickup.PickupError, match="completed cursor"):
        pickup.validate_progress(done, items, repo=REPO, parent_number=724)


def test_select_carries_dependency_kinds_through() -> None:
    items = [
        {"key": "a", "rank": 1, "dependencies": [], "dependency_kinds": {}},
        {
            "key": "b",
            "rank": 2,
            "dependencies": ["a"],
            "dependency_kinds": {"a": "soft"},
        },
    ]
    progress = {
        "schema": "charness.goal-progress/v1",
        "revision": 2,
        "total": 2,
        "completed": 0,
        "open": 2,
        "next": {
            "key": "b",
            "repo": REPO,
            "number": 727,
            "url": f"https://github.com/{REPO}/issues/727",
            "state": "OPEN",
        },
    }
    selected = pickup.select_from_parent_progress(progress, items, repo=REPO)
    assert selected["selected_child"]["dependency_kinds"] == {"a": "soft"}
    assert selected["ready_keys"] == ["b"]
