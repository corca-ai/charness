from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/issue/scripts/issue_tracker.py"


def _load():
    spec = importlib.util.spec_from_file_location("issue_tracker", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tracker = _load()
relationships = tracker.RELATIONSHIPS
BACKEND = {"id": "gh", "binary": "gh", "commands": None}


def _child(number: int, *, parent: int = 724, state: str = "open") -> dict[str, object]:
    return {
        "id": 9000 + number,
        "number": number,
        "title": f"child {number}",
        "state": state,
        "url": f"https://api.github.com/repos/corca-ai/charness/issues/{number}",
        "html_url": f"https://github.com/corca-ai/charness/issues/{number}",
        "parent_issue_url": f"https://api.github.com/repos/corca-ai/charness/issues/{parent}",
    }


def _completed(
    stdout: str = "", *, returncode: int = 0, stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["fake"], returncode, stdout, stderr)


def test_tracker_preflight_requires_all_operations_for_non_gh_backend() -> None:
    backend = {"id": "custom", "binary": "custom", "commands": {"update": ["update"]}}

    report = tracker.tracker_capability_report(backend, repo="owner/repo")

    assert report["ok"] is False
    assert "create" in report["missing_operations"]
    assert "view" in report["missing_operations"]
    assert "discover_managed_issues" in report["missing_operations"]
    assert "list_sub_issues" in report["missing_operations"]


def test_list_sub_issues_flattens_pages_and_proves_exact_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["list"])
    monkeypatch.setattr(
        relationships.JSON_PAGES,
        "run_backend",
        lambda _argv: _completed(json.dumps([[_child(1, state="closed")], [_child(2)]])),
    )

    result = tracker.list_sub_issues("corca-ai/charness", 724, backend=BACKEND)

    assert result["count"] == 2
    assert result["completed"] == 1
    assert result["children"][0]["state"] == "CLOSED"


def test_markdown_like_child_with_wrong_parent_is_not_a_relationship(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["list"])
    monkeypatch.setattr(
        relationships.JSON_PAGES,
        "run_backend",
        lambda _argv: _completed(json.dumps([_child(1, parent=999)])),
    )

    with pytest.raises(RuntimeError, match="did not prove parent"):
        tracker.list_sub_issues("corca-ai/charness", 724, backend=BACKEND)


def test_add_existing_sub_issue_is_idempotent_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        relationships,
        "list_sub_issues",
        lambda *_args, **_kwargs: {"count": 1, "children": [{"number": 725}]},
    )
    monkeypatch.setattr(
        relationships,
        "_resolve_issue_id",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not resolve")),
    )

    result = tracker.add_sub_issue("corca-ai/charness", 724, 725, backend=BACKEND)

    assert result["action"] == "already-linked"
    assert result["mutation_performed"] is False


def test_add_failure_is_unverified_and_preserves_prior_relations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        relationships,
        "list_sub_issues",
        lambda *_args, **_kwargs: {"count": 2, "children": [{"number": 1}, {"number": 2}]},
    )
    monkeypatch.setattr(relationships, "_resolve_issue_id", lambda *_args, **_kwargs: 9003)
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["add"])
    monkeypatch.setattr(
        relationships, "run_backend", lambda _argv: _completed(returncode=1, stderr="denied")
    )

    result = tracker.add_sub_issue("corca-ai/charness", 724, 3, backend=BACKEND)

    assert result["ok"] is False
    assert result["outcome"] == "unverified-write"
    assert result["mutation_invoked"] is True
    assert result["before"]["count"] == 2
    assert result["next_action"] == "stop-and-read-current-provider-state"


def test_add_sub_issue_verifies_relationship_after_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    readbacks = iter(
        [
            {"count": 1, "children": [{"number": 1}]},
            {"count": 2, "children": [{"number": 1}, {"number": 3}]},
        ]
    )
    monkeypatch.setattr(relationships, "list_sub_issues", lambda *_args, **_kwargs: next(readbacks))
    monkeypatch.setattr(relationships, "_resolve_issue_id", lambda *_args, **_kwargs: 9003)
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["add"])
    monkeypatch.setattr(relationships, "run_backend", lambda _argv: _completed())

    result = tracker.add_sub_issue("corca-ai/charness", 724, 3, backend=BACKEND)

    assert result["action"] == "linked"
    assert result["mutation_performed"] is True
    assert result["sub_issue_id"] == 9003
    assert result["readback"]["count"] == 2


def test_remove_sub_issue_verifies_absence_after_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    readbacks = iter(
        [
            {"count": 2, "children": [{"number": 1}, {"number": 3}]},
            {"count": 1, "children": [{"number": 1}]},
        ]
    )
    monkeypatch.setattr(relationships, "list_sub_issues", lambda *_args, **_kwargs: next(readbacks))
    monkeypatch.setattr(relationships, "_resolve_issue_id", lambda *_args, **_kwargs: 9003)
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["remove"])
    monkeypatch.setattr(relationships, "run_backend", lambda _argv: _completed())

    result = tracker.remove_sub_issue("corca-ai/charness", 724, 3, backend=BACKEND)

    assert result["action"] == "unlinked"
    assert result["mutation_performed"] is True
    assert result["readback"]["count"] == 1


def test_remove_missing_sub_issue_is_idempotent_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        relationships,
        "list_sub_issues",
        lambda *_args, **_kwargs: {"count": 1, "children": [{"number": 1}]},
    )
    monkeypatch.setattr(
        relationships,
        "_resolve_issue_id",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not resolve")),
    )

    result = tracker.remove_sub_issue("corca-ai/charness", 724, 3, backend=BACKEND)

    assert result["action"] == "already-unlinked"
    assert result["mutation_performed"] is False


def test_update_body_requires_byte_identical_readback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("new body\n", encoding="utf-8")
    monkeypatch.setattr(tracker, "resolve_op", lambda *_args, **_kwargs: ["update"])
    monkeypatch.setattr(tracker, "run_backend", lambda _argv: _completed())
    readbacks = iter(
        [
            {
                "body_verified": False,
                "body": "old body\n",
                "url": "https://github.com/corca-ai/charness/issues/724",
            },
            {
                "body_verified": True,
                "url": "https://github.com/corca-ai/charness/issues/724",
            },
        ]
    )
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: next(readbacks),
    )

    result = tracker.update_issue_body("corca-ai/charness", 724, body, backend=BACKEND)

    assert result["body_verified"] is True
    assert result["single_updater_assumption"] is True
    assert result["outcome"] == "verified-write"


def test_update_command_failure_is_never_no_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("new body\n", encoding="utf-8")
    monkeypatch.setattr(tracker, "resolve_op", lambda *_args, **_kwargs: ["update"])
    monkeypatch.setattr(
        tracker,
        "run_backend",
        lambda _argv: _completed(returncode=1, stderr="connection lost"),
    )
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: {
            "body_verified": False,
            "body": "old body\n",
            "readback_verified": True,
            "url": "https://github.com/corca-ai/charness/issues/724",
        },
    )

    result = tracker.update_issue_body("corca-ai/charness", 724, body, backend=BACKEND)

    assert result["ok"] is False
    assert result["outcome"] == "unverified-write"
    assert result["mutation_invoked"] is True


def test_update_body_refuses_live_prewrite_drift_before_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("approved new body\n", encoding="utf-8")
    provider_calls = 0

    def must_not_run(_argv: list[str]) -> None:
        nonlocal provider_calls
        provider_calls += 1
        raise AssertionError("live body drift must refuse before provider mutation")

    monkeypatch.setattr(tracker, "run_backend", must_not_run)
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: {
            "body_verified": False,
            "body": "drifted live body\n",
            "url": "https://github.com/corca-ai/charness/issues/725",
        },
    )

    with pytest.raises(RuntimeError, match="live pre-write body digest differs"):
        tracker.update_issue_body(
            "corca-ai/charness",
            725,
            body,
            backend=BACKEND,
            expected_body_sha256=hashlib.sha256(b"observed body\n").hexdigest(),
        )

    assert provider_calls == 0


def test_malformed_declared_template_fails_preflight_rendering() -> None:
    commands = {operation: [operation, "{repo}"] for operation in tracker.BOOTSTRAP_OPERATIONS}
    backend = {"id": "custom", "binary": "custom", "commands": commands}

    report = tracker.tracker_capability_report(backend, repo="owner/repo")

    assert report["ok"] is False
    assert "create" in report["template_errors"]
    assert "update" in report["template_errors"]


def test_malformed_format_grammar_is_a_typed_preflight_error() -> None:
    commands = {
        "create": ["create", "{repo}", "{title}", "{body_file}"],
        "view": ["view", "{repo}", "{number}", "{json_fields}"],
        "discover_managed_issues": ["discover", "{repo}"],
        "update": ["update", "{repo}", "{number}", "{body_file}", "{"],
        "list_sub_issues": ["list", "{repo}", "{number}"],
        "resolve_issue_id": ["resolve", "{repo}", "{sub_issue_number}"],
        "add_sub_issue": ["add", "{repo}", "{number}", "{sub_issue_id}"],
        "remove_sub_issue": ["remove", "{repo}", "{number}", "{sub_issue_id}"],
    }
    backend = {"id": "custom", "binary": "custom", "commands": commands}

    report = tracker.tracker_capability_report(backend, repo="owner/repo")

    assert report["ok"] is False
    assert "malformed format grammar" in report["template_errors"]["update"]


def test_create_or_reuse_returns_existing_exact_managed_issue_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("<!-- charness-work-item-key: goal-binding-v1 -->\nbody\n", encoding="utf-8")
    existing = {
        "ok": True,
        "count": 1,
        "matches": [
            {
                "number": 800,
                "title": "Binding",
                "body": body.read_text(),
                "url": "https://example/800",
            }
        ],
    }
    monkeypatch.setattr(tracker, "discover_managed_issues", lambda *_args, **_kwargs: existing)
    monkeypatch.setattr(
        tracker.CREATE,
        "create_issue",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not create")),
    )

    result = tracker.create_or_reuse_child(
        "corca-ai/charness", 724, "goal-binding-v1", "Binding", body, backend=BACKEND
    )

    assert result["action"] == "reused"
    assert result["outcome"] == "verified-read"
    assert result["mutation_invoked"] is False


def test_ambiguous_create_stops_when_work_item_is_not_discoverable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("<!-- charness-work-item-key: goal-binding-v1 -->\nbody\n", encoding="utf-8")
    discoveries = iter(
        [
            {"ok": True, "count": 0, "matches": []},
            {"ok": True, "count": 0, "matches": []},
        ]
    )
    monkeypatch.setattr(
        tracker, "discover_managed_issues", lambda *_args, **_kwargs: next(discoveries)
    )
    monkeypatch.setattr(
        tracker.CREATE,
        "create_issue",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            tracker.CREATE.IssueMutationError("connection lost", exit_code=1)
        ),
    )

    result = tracker.create_or_reuse_child(
        "corca-ai/charness", 724, "goal-binding-v1", "Binding", body, backend=BACKEND
    )

    assert result["outcome"] == "unverified-write"
    assert result["mutation_invoked"] is True
    assert result["work_item_key"] == "goal-binding-v1"
    assert result["next_action"] == "stop-and-read-current-provider-state"


def test_direct_verified_create_does_not_wait_for_search_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("<!-- charness-work-item-key: goal-binding-v1 -->\nbody\n", encoding="utf-8")
    discovery_calls = 0

    def discover(*_args, **_kwargs):
        nonlocal discovery_calls
        discovery_calls += 1
        if discovery_calls > 1:
            raise AssertionError("verified provider readback must not depend on search indexing")
        return {"ok": True, "count": 0, "matches": []}

    monkeypatch.setattr(tracker, "discover_managed_issues", discover)
    monkeypatch.setattr(
        tracker.CREATE,
        "create_issue",
        lambda *_args, **_kwargs: {
            "ok": True,
            "repo": "corca-ai/charness",
            "number": 800,
            "url": "https://example/800",
            "body_verified": True,
        },
    )

    result = tracker.create_or_reuse_child(
        "corca-ai/charness", 724, "goal-binding-v1", "Binding", body, backend=BACKEND
    )

    assert result["status"] == "verified-write"
    assert result["outcome"] == "verified-write"
    assert result["action"] == "created"
    assert result["number"] == 800
    assert result["body_verified"] is True
    assert discovery_calls == 1


def test_prior_unresolved_create_blocks_reinvocation_after_empty_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("<!-- charness-work-item-key: goal-binding-v1 -->\nbody\n", encoding="utf-8")
    monkeypatch.setattr(
        tracker,
        "discover_managed_issues",
        lambda *_args, **_kwargs: {"ok": True, "count": 0, "matches": []},
    )
    monkeypatch.setattr(
        tracker.CREATE,
        "create_issue",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not create")),
    )

    with pytest.raises(RuntimeError, match="prior matching provider attempt remains unresolved"):
        tracker.create_or_reuse_child(
            "corca-ai/charness",
            724,
            "goal-binding-v1",
            "Binding",
            body,
            backend=BACKEND,
            prior_unresolved_observation={"started_path": "observations/first.started.json"},
        )


def test_prior_unresolved_create_reuses_later_exact_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = tmp_path / "body.md"
    body.write_text("<!-- charness-work-item-key: goal-binding-v1 -->\nbody\n", encoding="utf-8")
    monkeypatch.setattr(
        tracker,
        "discover_managed_issues",
        lambda *_args, **_kwargs: {
            "ok": True,
            "count": 1,
            "matches": [
                {
                    "number": 800,
                    "title": "Binding",
                    "body": body.read_text(encoding="utf-8"),
                    "url": "https://example/800",
                }
            ],
        },
    )
    monkeypatch.setattr(
        tracker.CREATE,
        "create_issue",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not create")),
    )

    result = tracker.create_or_reuse_child(
        "corca-ai/charness",
        724,
        "goal-binding-v1",
        "Binding",
        body,
        backend=BACKEND,
        prior_unresolved_observation={"started_path": "observations/first.started.json"},
    )

    assert result["action"] == "reused"
    assert result["number"] == 800


def test_update_body_refuses_to_strip_goal_run_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    desired = tmp_path / "body.md"
    desired.write_text("plain body\n", encoding="utf-8")
    current = '<!-- charness-goal-run:v1\n{"binding_sha256":"a","draft_sha256":"b"}\n-->\n'
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: {
            "body_verified": False,
            "body": current,
            "url": "https://github.com/corca-ai/charness/issues/724",
        },
    )
    monkeypatch.setattr(
        tracker,
        "run_backend",
        lambda _argv: (_ for _ in ()).throw(AssertionError("must not write")),
    )

    with pytest.raises(RuntimeError, match="strip Goal Run metadata"):
        tracker.update_issue_body("corca-ai/charness", 724, desired, backend=BACKEND)


def test_generic_update_refuses_to_publish_terminal_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = '<!-- charness-goal-run:v1\n{"binding_sha256":"a","draft_sha256":"b"}\n-->\n'
    desired = tmp_path / "body.md"
    desired.write_text(
        '<!-- charness-goal-run:v1\n{"binding_sha256":"a","draft_sha256":"b",'
        '"terminal_observation_path":"observations/close.terminal.json",'
        '"terminal_observation_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"}\n-->\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: {
            "body_verified": False,
            "body": current,
            "url": "https://github.com/corca-ai/charness/issues/724",
        },
    )
    monkeypatch.setattr(
        tracker,
        "run_backend",
        lambda _argv: (_ for _ in ()).throw(AssertionError("must not write")),
    )

    with pytest.raises(RuntimeError, match="dedicated close ingress"):
        tracker.update_issue_body("corca-ai/charness", 724, desired, backend=BACKEND)


@pytest.mark.parametrize(
    "field", ["terminal_observation_path", "terminal_observation_sha256"]
)
def test_generic_update_treats_a_null_terminal_key_as_a_change(field: str) -> None:
    current = '<!-- charness-goal-run:v1\n{"binding_sha256":"a","draft_sha256":"b"}\n-->\n'
    desired = (
        '<!-- charness-goal-run:v1\n'
        f'{{"binding_sha256":"a","draft_sha256":"b","{field}":null}}\n-->\n'
    )

    with pytest.raises(RuntimeError, match="dedicated close ingress"):
        tracker._guard_goal_run_metadata(current, desired)


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("<!-- charness-goal-run:v2\n{}\n-->\n", "unsupported Goal Run metadata"),
        ("<!-- charness-goal-run:v1\n{}\n", "duplicate or malformed"),
        (
            "<!-- charness-goal-run:v1\n{}\n-->\n<!-- charness-goal-run:v1\n{}\n-->\n",
            "duplicate or malformed",
        ),
    ],
)
def test_already_current_body_still_validates_goal_run_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str, message: str
) -> None:
    desired = tmp_path / "body.md"
    desired.write_text(body, encoding="utf-8")
    monkeypatch.setattr(
        tracker.VERIFY_CREATE,
        "verify_created_issue",
        lambda *_args, **_kwargs: {
            "body_verified": True,
            "body": body,
            "url": "https://github.com/corca-ai/charness/issues/724",
        },
    )
    monkeypatch.setattr(
        tracker,
        "run_backend",
        lambda _argv: (_ for _ in ()).throw(AssertionError("must not write")),
    )

    with pytest.raises(RuntimeError, match=message):
        tracker.update_issue_body("corca-ai/charness", 724, desired, backend=BACKEND)


def test_expected_child_set_is_target_bound_and_rejects_duplicates(tmp_path: Path) -> None:
    manifest = tmp_path / "children.json"
    manifest.write_text(
        json.dumps(
            {
                "kind": "charness.expected-sub-issue-set/v1",
                "repo": "corca-ai/charness",
                "parent_number": 724,
                "children": [727, 725, 726],
                "source": {"binding": "pending-bootstrap"},
            }
        ),
        encoding="utf-8",
    )

    result = tracker.load_expected_child_set(manifest, repo="corca-ai/charness", parent_number=724)

    assert result["children"] == [725, 726, 727]
    assert len(result["sha256"]) == 64
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["children"] = [725, 725]
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="duplicate"):
        tracker.load_expected_child_set(manifest, repo="corca-ai/charness", parent_number=724)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload.update(repo="corca-ai/other"), "target does not match"),
        (lambda payload: payload.update(extra=True), "unknown fields"),
    ],
)
def test_expected_child_set_rejects_foreign_or_extended_manifest(
    tmp_path: Path, mutation, message: str
) -> None:
    manifest = tmp_path / "children.json"
    payload = {
        "kind": "charness.expected-sub-issue-set/v1",
        "repo": "corca-ai/charness",
        "parent_number": 724,
        "children": [],
    }
    mutation(payload)
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        tracker.load_expected_child_set(manifest, repo="corca-ai/charness", parent_number=724)


def test_expected_child_set_rejects_malformed_json(tmp_path: Path) -> None:
    manifest = tmp_path / "children.json"
    manifest.write_text("{", encoding="utf-8")

    with pytest.raises(RuntimeError, match="not valid UTF-8 JSON"):
        tracker.load_expected_child_set(manifest, repo="corca-ai/charness", parent_number=724)


def test_add_success_with_absent_readback_is_unverified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    readbacks = iter(
        [
            {"count": 1, "children": [{"number": 1}]},
            {"count": 1, "children": [{"number": 1}]},
        ]
    )
    monkeypatch.setattr(relationships, "list_sub_issues", lambda *_args, **_kwargs: next(readbacks))
    monkeypatch.setattr(relationships, "_resolve_issue_id", lambda *_args, **_kwargs: 9003)
    monkeypatch.setattr(relationships, "resolve_op", lambda *_args, **_kwargs: ["add"])
    monkeypatch.setattr(relationships, "run_backend", lambda _argv: _completed())

    result = tracker.add_sub_issue("corca-ai/charness", 724, 3, backend=BACKEND)

    assert result["ok"] is False
    assert result["outcome"] == "unverified-write"
    assert result["mutation_invoked"] is True
