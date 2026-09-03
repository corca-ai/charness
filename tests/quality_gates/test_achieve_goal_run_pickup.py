from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from .issue_goal_run_test_support import (
    _fixture_metadata,
    close_inputs,
)
from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_run_pickup.py"


def _load_module():
    return load_module("goal_run_pickup_under_test", SCRIPT)


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
        "subIssuesSummary": {"total": 31, "completed": 23, "percentCompleted": 74},
    }
    resolved = {"adapter_ok": True, "backend": {"id": "gh", "binary": "gh"}}

    class Selection:
        @staticmethod
        def resolve_backend(
            _root: Path,
            *,
            target_repo: str,
            adapter: dict[str, object] | None = None,
        ) -> dict[str, object]:
            assert target_repo == REPO
            assert adapter is None
            return dict(resolved)

    class Reader:
        @staticmethod
        def read_issue_with_comments(
            repo: str,
            number: int,
            *,
            backend: dict[str, object],
            include_sub_issues_summary: bool = False,
        ) -> dict[str, object]:
            calls.append((repo, number))
            assert backend == resolved["backend"]
            assert include_sub_issues_summary is True
            return {"issue": issue}

        normalise_sub_issues_summary = staticmethod(
            lambda _issue: {"total": 31, "completed": 23, "open": 8, "percent_completed": 74}
        )

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
    assert graph["parent"]["sub_issues_summary"]["completed"] == 23
    assert actual == resolved


def test_lesson_projection_reads_one_item_per_section_without_writing(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/recent-lessons.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Recent Lessons\n\n"
        "## Current Focus\n\n- current one\n- current two\n\n"
        "## Repeat Traps\n\n- trap one\n  continued\n\n"
        "## Next-Time Checklist\n\n- next one\n",
        encoding="utf-8",
    )

    before = path.read_bytes()
    result = pickup._read_lesson_projection(tmp_path)

    assert result["status"] == "selected"
    assert result["items"] == [
        {"section": "Current Focus", "lesson": "current one"},
        {"section": "Repeat Traps", "lesson": "trap one continued"},
        {"section": "Next-Time Checklist", "lesson": "next one"},
    ]
    assert path.read_bytes() == before


def test_missing_lesson_projection_is_advisory(tmp_path: Path) -> None:
    result = pickup._read_lesson_projection(tmp_path)

    assert result["status"] == "unavailable"


def test_seeded_digest_adapter_keeps_the_existing_pickup_projection(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: docs/lessons.md\n",
        encoding="utf-8",
    )
    digest = tmp_path / "docs" / "lessons.md"
    digest.parent.mkdir(parents=True)
    digest.write_text(
        "# Recent Lessons\n\n"
        "## Current Focus\n\n- configured current focus\n\n"
        "## Repeat Traps\n\n- configured repeat trap\n\n"
        "## Next-Time Checklist\n\n- configured next step\n",
        encoding="utf-8",
    )

    result = pickup._read_lesson_projection(tmp_path)

    assert result == {
        "source": "docs/lessons.md",
        "selection": "first-item-per-section",
        "status": "selected",
        "items": [
            {"section": "Current Focus", "lesson": "configured current focus"},
            {"section": "Repeat Traps", "lesson": "configured repeat trap"},
            {"section": "Next-Time Checklist", "lesson": "configured next step"},
        ],
        "item_count": 3,
    }


def test_ledger_only_adapter_reads_the_bounded_selection_preview(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With `summary_path: null` the projection comes from the ledger preview, bounded.

    The preview builder is patched at the seam pickup binds, so the test proves
    pickup's own projection (source, bounding, empty-item filtering) without
    copying the real checkout's ledger (repo-copy invariant).
    """
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: null\n",
        encoding="utf-8",
    )
    retro_dir = tmp_path / "charness-artifacts" / "retro"
    retro_dir.mkdir(parents=True)
    (retro_dir / "lesson-selection-index.json").write_text("{}\n", encoding="utf-8")
    long_lesson = "x" * (pickup._LESSON_MAX_CHARS + 40)
    items = [{"lesson": f"lesson {index}"} for index in range(len(pickup._LESSON_SECTIONS) + 2)]
    items[0] = {"lesson": long_lesson}
    items.append({"lesson": "   "})
    monkeypatch.setattr(
        pickup._lesson_projection._lesson_preview,
        "build_lesson_selection_preview",
        lambda **_kwargs: {"items": items},
    )

    result = pickup._read_lesson_projection(tmp_path)

    assert result["source"] == "charness-artifacts/retro/lesson-selection-index.json"
    assert result["selection"] == "bounded-ledger-preview"
    assert result["status"] == "selected"
    assert result["item_count"] == len(pickup._LESSON_SECTIONS)
    assert all(len(item["lesson"]) <= pickup._LESSON_MAX_CHARS for item in result["items"])
    assert not (retro_dir / "recent-lessons.md").exists()


def test_pickup_refuses_closed_parent_before_binding_or_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    monkeypatch.setattr(
        pickup, "_resolve_repository", lambda *_args: {"full_name": REPO, "source": "fixture"}
    )
    monkeypatch.setattr(
        pickup, "_read_goal_parent", lambda *_args: (graph, {"adapter_ok": True, "backend": {}})
    )

    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(ROOT, "/goal #724")

    assert exc_info.value.code == "parent-closed"


@pytest.mark.parametrize("child_state", ["OPEN", "CLOSED"])
def test_pickup_reads_only_cursor_child_and_refuses_closed_cursor(
    monkeypatch: pytest.MonkeyPatch,
    child_state: str,
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
        if name == "issue_pickup_child_read":
            return SimpleNamespace(
                read_issue_with_comments=lambda *_args, **_kwargs: {
                    "issue": {
                        "number": 726,
                        "title": "Provider",
                        "state": child_state,
                        "url": f"https://github.com/{REPO}/issues/726",
                        "body": "child body",
                        "updatedAt": "2026-08-27T00:00:00Z",
                        "comments": [],
                    }
                }
            )
        raise AssertionError(name)

    monkeypatch.setattr(pickup, "_load_path", fake_load)
    monkeypatch.setattr(
        pickup, "_resolve_repository", lambda *_args: {"full_name": REPO, "source": "fixture"}
    )
    monkeypatch.setattr(
        pickup,
        "_read_goal_parent",
        lambda *_args: (graph, {"adapter_ok": True, "backend": {}}),
    )
    if child_state == "CLOSED":
        with pytest.raises(pickup.PickupError) as exc_info:
            pickup.pickup(ROOT, "/goal #724")
        assert exc_info.value.code == "cursor-child-closed"
        return

    result = pickup.pickup(ROOT, "/goal #724")

    assert result["ok"] is True
    assert result["outcome"] == "verified-read"
    assert result["mutation_invoked"] is False
    assert result["selected_child"]["key"] == "provider"
    assert result["graph"]["amended_work_items"] == []
    assert result["binding"]["draft_amended"] is False
    assert result["selection"] == {"source": "parent-progress", "child_reads": 1}
    assert result["child_issue"]["body"] == "child body"
    assert result["selected_child"]["state"] == "OPEN"


def test_metadata_amendment_shape_and_effective_items() -> None:
    """An amendment appends one approved Work Item to a live run without touching the binding."""
    contract = load_module(
        "goal_run_pickup_contract_under_test",
        ROOT / "skills/public/achieve/scripts/goal_run_pickup_contract.py",
    )
    metadata = _metadata()
    metadata.pop("current_membership_sha256")
    metadata["progress"].pop("membership_sha256")
    amendment = {
        "key": "late-item",
        "repo": REPO,
        "number": 773,
        "url": f"https://github.com/{REPO}/issues/773",
        "rank": 2,
        "dependencies": ["provider"],
        "reason": "operator asked to include it after binding",
        "approval": {
            "response": "approve",
            "session_id": "s",
            "observed_at": "2026-09-02T00:00:00+00:00",
        },
    }
    metadata["amendments"] = [amendment]
    validated = contract.validate_metadata(
        metadata, repo=REPO, parent_number=PARENT_NUMBER, parent_url=PARENT_URL
    )
    binding_items = [{"key": "provider", "rank": 1, "dependencies": []}]
    items = contract.effective_work_items(binding_items, validated)
    assert [item["key"] for item in items] == ["provider", "late-item"]
    assert items[1]["intent"] == "amended"
    assert items[1]["issue"]["number"] == 773

    metadata["progress"]["next"] = {
        "key": "late-item",
        "repo": REPO,
        "number": 773,
        "url": f"https://github.com/{REPO}/issues/773",
        "state": "OPEN",
    }
    progress = contract.validate_progress(
        metadata, binding_items, repo=REPO, parent_number=PARENT_NUMBER
    )
    assert progress["next"]["key"] == "late-item"

    with pytest.raises(contract.PickupError, match="collides"):
        contract.effective_work_items(
            binding_items, {**metadata, "amendments": [{**amendment, "key": "provider"}]}
        )
    for bad in (
        {**amendment, "repo": "other/repo"},
        {**amendment, "approval": {"response": "", "session_id": "s", "observed_at": "t"}},
    ):
        with pytest.raises(contract.PickupError, match="metadata-invalid|amendments"):
            contract.validate_metadata(
                {**metadata, "amendments": [bad]},
                repo=REPO,
                parent_number=PARENT_NUMBER,
                parent_url=PARENT_URL,
            )


def test_membership_hash_is_neither_required_nor_compared() -> None:
    contract = load_module(
        "goal_run_pickup_contract_under_test_membership",
        ROOT / "skills/public/achieve/scripts/goal_run_pickup_contract.py",
    )
    metadata = _metadata()
    metadata.pop("current_membership_sha256")
    metadata["progress"]["membership_sha256"] = _sha("e")  # stale leftover from an older parent
    contract.validate_metadata(
        metadata, repo=REPO, parent_number=PARENT_NUMBER, parent_url=PARENT_URL
    )
    contract.validate_progress(
        metadata,
        [{"key": "provider", "rank": 1, "dependencies": []}],
        repo=REPO,
        parent_number=PARENT_NUMBER,
    )


def test_seeded_run_reestablishes_by_identity_after_amendment_and_prose_edits(  # noqa: C901, PLR0915 -- one seeded scenario covers the full re-establishment loop
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run survives reversible prose edits while cursor and marker identities hold."""
    close_inputs(tmp_path)
    metadata = _fixture_metadata(tmp_path)
    metadata["progress"] = {
        "schema": "charness.goal-progress/v1",
        "revision": 1,
        "total": 1,
        "completed": 0,
        "open": 1,
        "next": {
            "key": "child-725",
            "repo": REPO,
            "number": 725,
            "url": f"https://github.com/{REPO}/issues/725",
            "state": "OPEN",
        },
    }
    amendment = {
        "key": "late-item",
        "repo": REPO,
        "number": 773,
        "url": f"https://github.com/{REPO}/issues/773",
        "rank": 2,
        "dependencies": ["child-725"],
        "reason": "operator-approved late Work Item",
        "approval": {
            "response": "approved",
            "session_id": "seeded-session",
            "observed_at": "2026-09-02T00:00:00+00:00",
        },
    }

    def render_parent() -> str:
        return (
            "<!-- charness-goal-run:v1\n"
            + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
            + "\n-->\n"
        )

    children: dict[int, dict[str, object]] = {
        725: {
            "number": 725,
            "title": "Child 725",
            "state": "OPEN",
            "url": f"https://github.com/{REPO}/issues/725",
            "body": "<!-- charness-work-item-key: child-725 -->\noriginal prose\n",
            "comments": [],
        },
        773: {
            "number": 773,
            "title": "Late Item",
            "state": "OPEN",
            "url": f"https://github.com/{REPO}/issues/773",
            "body": "<!-- charness-work-item-key: late-item -->\nlate prose\n",
            "comments": [],
        },
    }
    parent = {
        "number": PARENT_NUMBER,
        "title": "Goal Run",
        "state": "OPEN",
        "url": PARENT_URL,
        "body": render_parent(),
        "comments": [],
    }
    state: dict[str, object] = {"parent": parent, "children": children}

    provider = load_module(
        "goal_run_apply_identity_seed", ROOT / "skills/public/issue/scripts/issue_goal_run.py"
    )

    class Reader:
        @staticmethod
        def read_issue_with_comments(
            _repo: str, number: int, *, backend: dict[str, object], **_kwargs: object
        ) -> dict[str, object]:
            assert backend["id"] == "fixture"
            if number == PARENT_NUMBER:
                return {"issue": state["parent"]}
            return {"issue": state["children"][number]}

    def update_body(
        _repo: str,
        number: int,
        body_file: Path,
        *,
        backend: dict[str, object],
        parent_amendment_validator: object | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        assert backend["id"] == "fixture"
        current = (
            state["parent"]["body"]
            if number == PARENT_NUMBER
            else state["children"][number]["body"]
        )
        desired = body_file.read_text(encoding="utf-8")
        if parent_amendment_validator is not None:
            parent_amendment_validator(current, desired)
        if number == PARENT_NUMBER:
            state["parent"]["body"] = desired
        else:
            state["children"][number]["body"] = desired
        return {
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "body_verified": True,
            "number": number,
            "url": f"https://github.com/{REPO}/issues/{number}",
        }

    def add_child(
        _repo: str, _parent: int, number: int, *, backend: dict[str, object]
    ) -> dict[str, object]:
        assert backend["id"] == "fixture"
        assert number == amendment["number"]
        metadata["amendments"] = [amendment]
        metadata["progress"]["total"] = 2
        metadata["progress"]["open"] = 2
        metadata["progress"]["next"] = {
            "key": "child-725",
            "repo": REPO,
            "number": 725,
            "url": f"https://github.com/{REPO}/issues/725",
            "state": "OPEN",
        }
        state["parent"]["body"] = render_parent()
        return {
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "number": number,
        }

    provider.command_apply.__globals__["READ"] = Reader
    provider.command_apply.__globals__["TRACKER"] = SimpleNamespace(
        update_issue_body=update_body,
        add_sub_issue=add_child,
    )

    def write_operation(
        name: str, target: dict[str, object], *, attempt: str, **extra: object
    ) -> Path:
        path = tmp_path / f"{attempt}.json"
        path.write_text(
            json.dumps(
                {
                    "kind": "charness.goal-run-operation/v1",
                    "repo": REPO,
                    "parent_number": PARENT_NUMBER,
                    "operation": name,
                    "attempt_id": attempt,
                    "observation_dir": "observations",
                    "target": target,
                    **extra,
                }
            ),
            encoding="utf-8",
        )
        return path

    def apply(path: Path) -> dict[str, object]:
        emitted: list[dict[str, object]] = []
        rc = provider.command_apply(
            SimpleNamespace(
                repo=REPO, number=PARENT_NUMBER, operation_file=path, repo_root=tmp_path
            ),
            resolve_backend=lambda *_args, **_kwargs: {
                "adapter_ok": True,
                "backend": {"id": "fixture"},
            },
            emit=emitted.append,
        )
        assert rc == 0
        return emitted[0]

    add_result = apply(
        write_operation(
            "add-child",
            {"repo": REPO, "sub_issue_number": 773, "work_item_key": "late-item"},
            attempt="seed-add-amendment",
            amendment={
                "rank": amendment["rank"],
                "dependencies": amendment["dependencies"],
                "reason": amendment["reason"],
                "approval": amendment["approval"],
            },
        )
    )
    assert add_result["outcome"] == "verified-write"
    assert metadata["amendments"] == [amendment]

    # Child prose may change; losing its marker must still refuse.
    child_body = tmp_path / "child-corrected.md"
    child_body.write_text(
        "<!-- charness-work-item-key: child-725 -->\ncorrected prose\n", encoding="utf-8"
    )
    apply(
        write_operation(
            "update-body",
            {"repo": REPO, "number": 725, "work_item_key": "child-725"},
            attempt="seed-child-prose",
            body_file="child-corrected.md",
        )
    )

    real_guard = load_module(
        "goal_run_seed_pickup_guard", ROOT / "skills/public/issue/scripts/issue_goal_run_guard.py"
    )
    real_binding = load_module(
        "goal_run_seed_pickup_binding", ROOT / "skills/public/achieve/scripts/goal_binding.py"
    )

    def fake_pickup_load(_path: Path, name: str) -> object:
        if name == "issue_pickup_adapter":
            return SimpleNamespace(
                load_adapter=lambda _root: {
                    "valid": True,
                    "data": {"default_repo": REPO, "default_org": "corca-ai"},
                }
            )
        if name == "issue_pickup_runtime":
            return SimpleNamespace()
        if name == "issue_pickup_guard":
            return real_guard
        if name == "issue_pickup_binding":
            return real_binding
        if name == "issue_pickup_child_read":
            return Reader
        raise AssertionError(name)

    monkeypatch.setattr(pickup, "_load_path", fake_pickup_load)
    monkeypatch.setattr(
        pickup,
        "_resolve_repository",
        lambda *_args, **_kwargs: {"full_name": REPO, "source": "fixture"},
    )
    monkeypatch.setattr(
        pickup,
        "_read_goal_parent",
        lambda *_args, **_kwargs: (
            {"parent": state["parent"]},
            {"adapter_ok": True, "backend": {"id": "fixture"}},
        ),
    )

    # Corrected child prose re-establishes by parent cursor and marker identity.
    selected = pickup.pickup(tmp_path, "/goal #724")
    assert selected["outcome"] == "verified-read"
    assert selected["selected_child"]["key"] == "child-725"

    # Cursor movement is a parent identity update; pickup follows the amended key.
    metadata["progress"]["revision"] = 2
    metadata["progress"]["next"] = {
        "key": "late-item",
        "repo": REPO,
        "number": 773,
        "url": f"https://github.com/{REPO}/issues/773",
        "state": "OPEN",
    }
    parent_body_file = tmp_path / "parent-cursor.md"
    parent_body_file.write_text(render_parent(), encoding="utf-8")
    apply(
        write_operation(
            "update-body",
            {"repo": REPO, "number": PARENT_NUMBER},
            attempt="seed-parent-cursor",
            body_file="parent-cursor.md",
        )
    )
    selected = pickup.pickup(tmp_path, "/goal #724")
    assert selected["outcome"] == "verified-read"
    assert selected["selected_child"]["key"] == "late-item"

    # Swapping draft_path breaks the immutable plan identity, not child content.
    metadata["draft_path"] = "other-goal.md"
    state["parent"]["body"] = render_parent()
    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(tmp_path, "/goal #724")
    assert exc_info.value.code == "binding-invalid"
    metadata["draft_path"] = "goal.md"

    # An unapproved cursor key is a graph identity refusal.
    metadata["progress"]["next"]["key"] = "unapproved"
    state["parent"]["body"] = render_parent()
    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(tmp_path, "/goal #724")
    assert exc_info.value.code == "graph-work-item-mismatch"

    # A CLOSED cursor child is a state refusal requiring explicit sync.
    metadata["progress"]["next"] = {
        "key": "late-item",
        "repo": REPO,
        "number": 773,
        "url": f"https://github.com/{REPO}/issues/773",
        "state": "OPEN",
    }
    state["parent"]["body"] = render_parent()
    state["children"][773]["state"] = "CLOSED"
    with pytest.raises(pickup.PickupError) as exc_info:
        pickup.pickup(tmp_path, "/goal #724")
    assert exc_info.value.code == "cursor-child-closed"


# --- checkout-first routing (#788) -------------------------------------------------


def _source_tree(tmp_path: Path, *, lib_body: str) -> Path:
    root = tmp_path / "source"
    (root / "packaging").mkdir(parents=True)
    (root / "packaging" / "charness.json").write_text(
        json.dumps({"package_id": "charness", "version": "8.0.3"}), encoding="utf-8"
    )
    (root / "scripts").mkdir()
    (root / "scripts" / "runtime_bootstrap.py").write_text("# marker\n", encoding="utf-8")
    (root / "scripts" / "lessons_lib.py").write_text(lib_body, encoding="utf-8")
    scripts = root / "skills" / "public" / "achieve" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "goal_run_pickup.py").write_text("# pickup\n", encoding="utf-8")
    return root


def _installed_tree(tmp_path: Path, *, lib_body: str) -> Path:
    root = tmp_path / "installed"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "charness", "version": "8.0.2"}), encoding="utf-8"
    )
    (root / "scripts").mkdir()
    (root / "scripts" / "runtime_bootstrap.py").write_text("# marker\n", encoding="utf-8")
    (root / "scripts" / "lessons_lib.py").write_text(lib_body, encoding="utf-8")
    scripts = root / "skills" / "achieve" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "goal_run_pickup.py").write_text("# pickup\n", encoding="utf-8")
    return root


def test_pickup_reports_the_checkout_as_its_own_tree() -> None:
    origin = pickup._script_origin(ROOT)
    assert origin["status"] == "same-tree"
    assert origin["script"] == str(SCRIPT)
    assert origin["target_root"] == str(ROOT)
    assert "refusal" not in origin


def test_a_drifted_installed_copy_inside_the_authoring_repo_is_refused_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _source_tree(tmp_path, lib_body="VALUE = 2\n")
    installed = _installed_tree(tmp_path, lib_body="VALUE = 1\n")
    origin = pickup._script_origin(
        source, script_file=installed / "skills" / "achieve" / "scripts" / "goal_run_pickup.py"
    )
    assert origin["status"] == "drifted"
    assert origin["own_version"] == "8.0.2" and origin["target_version"] == "8.0.3"
    assert origin["checkout_script"].endswith("skills/public/achieve/scripts/goal_run_pickup.py")
    assert "provenance refusal" in origin["refusal"]

    monkeypatch.setattr(pickup, "_script_origin", lambda _root: origin)

    def never(_path: Path, name: str):
        raise AssertionError(f"a refused pickup must read nothing, loaded {name}")

    monkeypatch.setattr(pickup, "_load_path", never)
    with pytest.raises(pickup.PickupError) as excinfo:
        pickup.pickup(source, "/goal #784")
    assert excinfo.value.code == "stale-installed-copy"
    assert "python3 " in str(excinfo.value)
    assert "skills/public/achieve/scripts/goal_run_pickup.py" in str(excinfo.value)
    assert excinfo.value.details["status"] == "drifted"


def test_an_installed_copy_in_a_consuming_repo_is_not_refused(tmp_path: Path) -> None:
    installed = _installed_tree(tmp_path, lib_body="VALUE = 1\n")
    consuming = tmp_path / "consumer"
    consuming.mkdir()
    origin = pickup._script_origin(
        consuming, script_file=installed / "skills" / "achieve" / "scripts" / "goal_run_pickup.py"
    )
    assert origin["status"] == "consuming-repo"
    assert "refusal" not in origin
