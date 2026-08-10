from __future__ import annotations

import importlib.util
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import scripts.lifecycle_usage_capture as lifecycle
from scripts.lifecycle_usage_capture import capture_lifecycle_outcome, episode_id_for


@pytest.fixture(autouse=True)
def _clear_ambient_quality_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep write-path tests independent of the suite's quality-run environment."""

    monkeypatch.delenv("CHARNESS_QUALITY_MODE", raising=False)
    monkeypatch.delenv("CHARNESS_QUALITY_READ_ONLY", raising=False)


def _adapter(repo: Path, *, enabled: bool = True, events: list[str] | None = None, include_privacy: bool = True) -> None:
    path = repo / ".agents"
    path.mkdir(parents=True, exist_ok=True)
    (path / "usage-episodes-adapter.yaml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "repo": "fixture",
                "enabled": enabled,
                "events": events or ["usage_episode", "usage_feedback"],
                **({"privacy": {"raw_prompt": False, "raw_transcript": False, "user_identity": "none"}} if include_privacy else {}),
            }
        ),
        encoding="utf-8",
    )


def _rows(repo: Path) -> list[dict]:
    return [json.loads(line) for line in (repo / ".charness/usage-episodes/usage_episode.jsonl").read_text().splitlines()]


def test_episode_identity_is_deterministic_from_kind_and_locator(tmp_path: Path) -> None:
    assert episode_id_for("issue_close", "acme/demo#42") == episode_id_for("issue_close", "acme/demo#42")
    assert episode_id_for("issue_close", "acme/demo#42") != episode_id_for("release_publish", "acme/demo#42")
    assert episode_id_for("issue_close", "acme/demo#42", "one") != episode_id_for("issue_close", "acme/demo#42", "two")


def test_capture_appends_delivery_then_linked_feedback_and_replays(tmp_path: Path) -> None:
    _adapter(tmp_path)
    first = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="acme/demo#42")
    replay = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="acme/demo#42")

    assert first["status"] == "appended"
    assert replay["status"] == "replay_noop"
    rows = _rows(tmp_path)
    assert [row["event_type"] for row in rows] == ["usage_episode", "usage_feedback"]
    assert rows[1]["target_episode_id"] == rows[0]["episode_id"]
    assert rows[1]["source_kind"] == "issue_lifecycle"
    assert rows[1]["feedback_signal"] == "closed_issue"


def test_capture_disabled_and_invalid_adapter_are_explicit(tmp_path: Path) -> None:
    _adapter(tmp_path, enabled=False)
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v1.0.0")["status"] == "disabled"
    _adapter(tmp_path)
    (tmp_path / ".agents/usage-episodes-adapter.yaml").write_text("version: 2\nenabled: true\n", encoding="utf-8")
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v1.0.0")["status"] == "invalid_adapter"


def test_capture_accepts_schema_valid_adapter_without_optional_privacy(tmp_path: Path) -> None:
    _adapter(tmp_path, include_privacy=False)
    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="acme/demo#7")
    assert result["status"] == "appended"


def test_capture_quality_mode_is_read_only(tmp_path: Path, monkeypatch) -> None:
    _adapter(tmp_path)
    monkeypatch.setenv("CHARNESS_QUALITY_MODE", "1")
    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v1.0.0")
    assert result["status"] == "readonly_quality_run"
    assert not (tmp_path / ".charness/usage-episodes/usage_episode.jsonl").exists()


def test_capture_rejects_locator_with_raw_prose(tmp_path: Path) -> None:
    _adapter(tmp_path)
    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="issue 42 body")
    assert result["status"] == "invalid"


@pytest.mark.parametrize("existing_index", [0, 1], ids=["delivery-only", "feedback-only"])
def test_capture_partial_existing_identity_conflicts_without_append(tmp_path: Path, existing_index: int) -> None:
    _adapter(tmp_path)
    capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="acme/demo#8")
    records_path = tmp_path / ".charness/usage-episodes/usage_episode.jsonl"
    existing = _rows(tmp_path)[existing_index]
    records_path.write_text(json.dumps(existing, sort_keys=True) + "\n", encoding="utf-8")
    before = records_path.read_bytes()

    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="acme/demo#8")

    assert result["status"] == "conflict"
    assert result["appended"] is False
    assert records_path.read_bytes() == before


def test_capture_conflicting_existing_identity_does_not_append(tmp_path: Path) -> None:
    _adapter(tmp_path)
    capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v1.2.3")
    records_path = tmp_path / ".charness/usage-episodes/usage_episode.jsonl"
    rows = _rows(tmp_path)
    rows[0]["core_action"] = "published_different_surface"
    records_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    before = records_path.read_bytes()

    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v1.2.3")

    assert result["status"] == "conflict"
    assert result["appended"] is False
    assert records_path.read_bytes() == before


def test_issue_close_capture_runs_after_state_readback(tmp_path: Path) -> None:
    module = runpy.run_path("skills/public/issue/scripts/issue_close.py")
    events: list[str] = []

    def fake_backend(argv):
        operation = "view" if "view" in argv else "close" if "close" in argv else "comment"
        events.append(operation)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"state": "CLOSED"}) if operation == "view" else "", stderr="")

    module["close_with_comment"].__globals__["_run_backend"] = fake_backend
    module["close_with_comment"].__globals__["_capture_lifecycle"] = lambda *_a, **_k: events.append("capture") or {"status": "appended"}
    body = tmp_path / "body.md"
    # Scaffolding: the provenance floor applies to every classification, and this
    # test is about lifecycle capture ordering, not the floor.
    body.write_text(
        "Multi-line\nclose comment.\n\nAI-provenance: authored by an agent session.\n",
        encoding="utf-8",
    )
    result = module["close_with_comment"](
        "acme/demo", 42, body, repo_root=tmp_path, classification="question",
        backend={"id": "gh", "binary": "gh", "commands": None},
    )
    assert result["lifecycle_capture"]["status"] == "appended"
    assert events == ["comment", "close", "view", "capture"]


def test_release_capture_runs_after_distinct_channel_floor() -> None:
    module = runpy.run_path("skills/public/release/scripts/publish_release_common.py")
    events: list[str] = []
    module["run_release_closeout_tail"].__globals__["run_distinct_channel_floor"] = lambda *_a, **_k: events.append("distinct")
    module["run_release_closeout_tail"].__globals__["_capture_lifecycle"] = lambda *_a, **_k: events.append("capture") or {"status": "appended"}
    module["run_release_closeout_tail"].__globals__["close_issues_install_refresh_and_commit"] = lambda *_a, **_k: events.append("close")
    module["run_release_closeout_tail"](
        Path("."), args=SimpleNamespace(), adapter_data={},
        state={"tag_name": "v1.0.0"}, issue_repo="acme/demo", payload={}, cli=SimpleNamespace(),
    )
    assert events == ["distinct", "capture", "close"]


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        (
            {"status": "appended", "appended": True, "episode_id": "episode-1", "feedback_id": "feedback-1", "errors": []},
            ["Lifecycle capture status: `appended`.", "Local telemetry pair appended: `True`.", "Delivery episode ID: `episode-1`.", "Capture error count: `0`."],
        ),
        (
            {"status": "disabled", "appended": False, "errors": []},
            ["Lifecycle capture status: `disabled`.", "Local telemetry pair appended: `False`.", "Capture error count: `0`."],
        ),
        (
            {"status": "capture_error", "appended": False, "errors": ["local detail"]},
            ["Lifecycle capture status: `capture_error`.", "Local telemetry pair appended: `False`.", "Capture error count: `1`."],
        ),
    ],
)
def test_release_artifact_lines_render_lifecycle_capture_dispositions(record: dict, expected: list[str]) -> None:
    sections = runpy.run_path("skills/public/release/scripts/publish_release_artifact_sections.py")
    rendered = "\n".join(sections["lifecycle_capture_lines"](record))
    assert "## Lifecycle Usage Capture" in rendered
    assert all(text in rendered for text in expected)
    assert "objective lifecycle capture is not human approval" in rendered
    assert "local detail" not in rendered


def test_exported_plugin_capture_smoke(tmp_path: Path) -> None:
    plugin_path = Path("plugins/charness/scripts/lifecycle_usage_capture.py")
    assert plugin_path.is_file(), "source/plugin sync must export lifecycle_usage_capture.py"
    _adapter(tmp_path, include_privacy=False)
    spec = importlib.util.spec_from_file_location("plugin_lifecycle_capture_test", plugin_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v9.9.9")
    replay = module.capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="release_publish", evidence_locator="v9.9.9")
    assert first["status"] == "appended"
    assert replay["status"] == "replay_noop"
    assert [row["event_type"] for row in _rows(tmp_path)] == ["usage_episode", "usage_feedback"]


def test_private_helpers_cover_fallbacks_and_rejections(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sys_path_before = list(__import__("sys").path)
    try:
        loaded = lifecycle._load_sibling(tmp_path, "lifecycle_usage_capture")
        assert "capture_lifecycle_outcome" in loaded
        with monkeypatch.context() as patch:
            patch.setattr(lifecycle.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
            with pytest.raises(ImportError, match="unable to load"):
                lifecycle._load_sibling(tmp_path, "lifecycle_usage_capture")
    finally:
        __import__("sys").path[:] = sys_path_before

    # Schema discovery is delegated to the shared records runtime, whose
    # installed-plugin fallback is rooted at that sibling module.
    assert lifecycle._schema_root(tmp_path).name == "usage-episodes"
    assert lifecycle._portable_path(tmp_path, tmp_path / "inside") == "inside"
    assert lifecycle._portable_path(tmp_path, Path("/outside")) == "/outside"
    assert lifecycle._privacy_ok({"privacy": "bad"}) is False
    assert lifecycle._records_path(tmp_path, {"storage_path": "../outside"})[1] == "storage_path must stay under repo_root"
    assert lifecycle._valid_adapter(tmp_path / "missing.yaml", tmp_path)[0] is None


def test_load_sibling_inserts_fallback_parent_on_sys_path(tmp_path: Path) -> None:
    import sys

    parent = str(Path(lifecycle.__file__).resolve().parent)
    original = list(sys.path)
    try:
        sys.path[:] = [entry for entry in sys.path if entry != parent]
        assert parent not in sys.path
        lifecycle._load_sibling(tmp_path, "lifecycle_usage_capture")
        assert sys.path[0] == parent
    finally:
        sys.path[:] = original


def test_schema_root_prefers_repo_local_integration(tmp_path: Path) -> None:
    integration = tmp_path / "integrations" / "usage-episodes"
    integration.mkdir(parents=True)
    (integration / "manifest.schema.json").write_text("{}", encoding="utf-8")
    (integration / "episode.schema.json").write_text("{}", encoding="utf-8")

    assert lifecycle._schema_root(tmp_path) == integration


def test_valid_adapter_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter.yaml"
    adapter.write_text("- not-a-mapping\n", encoding="utf-8")

    result, error = lifecycle._valid_adapter(adapter, tmp_path)

    assert result is None
    assert error and "usage-episodes adapter must be a mapping" in error


def test_capture_rejects_unsupported_kind_and_other_invalid_inputs(tmp_path: Path) -> None:
    unsupported = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="other", evidence_locator="v1")
    assert unsupported == {"status": "invalid", "appended": False, "errors": ["unsupported lifecycle kind: other"]}
    _adapter(tmp_path)
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="v1", product_id="bad id")["status"] == "invalid"
    (tmp_path / ".agents/usage-episodes-adapter.yaml").write_text(
        yaml.safe_dump({"version": 1, "repo": "fixture", "enabled": True, "events": ["usage_episode", "usage_feedback"], "privacy": {"raw_prompt": True, "raw_transcript": False, "user_identity": "none"}}), encoding="utf-8"
    )
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="v1")["status"] == "invalid_adapter"


def test_append_pair_handles_stream_semantic_schema_and_unexpected_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class Lock:
        def __enter__(self): return self
        def __exit__(self, *_): return False

    monkeypatch.setattr(lifecycle, "_stream_lock", lambda _path: Lock())
    delivery = {"episode_id": "episode-1", "event_type": "usage_episode"}
    feedback = {"feedback_id": "feedback-1", "event_type": "usage_feedback"}
    monkeypatch.setattr(lifecycle, "_load_sibling", lambda _root, name: {"read_schema_valid_records": lambda *_a: ([], ["bad"])} if name == "usage_episode_records" else {})
    assert lifecycle._append_pair_locked(repo_root=tmp_path, records_path=tmp_path / "records", schema={}, delivery=delivery, feedback=feedback)["status"] == "invalid_stream"
    monkeypatch.setattr(lifecycle, "_load_sibling", lambda _root, name: {"read_schema_valid_records": lambda *_a: ([], []), "semantic_feedback_errors": lambda *_a: ["bad"]} if name == "usage_episode_records" else {"semantic_feedback_errors": lambda *_a: ["bad"]})
    assert lifecycle._append_pair_locked(repo_root=tmp_path, records_path=tmp_path / "records", schema={}, delivery=delivery, feedback=feedback)["status"] == "invalid_stream"
    monkeypatch.setattr(lifecycle, "_load_sibling", lambda *_a: {"read_schema_valid_records": lambda *_a: ([], []), "semantic_feedback_errors": lambda *_a: []})
    assert lifecycle._append_pair_locked(repo_root=tmp_path, records_path=tmp_path / "records", schema={"type": "object", "required": ["missing"]}, delivery=delivery, feedback=feedback)["status"] == "invalid_record"
    monkeypatch.setattr(lifecycle, "_load_sibling", lambda *_a: (_ for _ in ()).throw(RuntimeError("boom")))
    result = lifecycle._append_pair_locked(repo_root=tmp_path, records_path=tmp_path / "records", schema={}, delivery=delivery, feedback=feedback)
    assert result["status"] == "capture_error" and "boom" in result["errors"][0]


def test_capture_handles_storage_and_outer_exceptions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _adapter(tmp_path)
    monkeypatch.setattr(lifecycle, "_records_path", lambda *_a: (None, "bad storage"))
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="v1")["status"] == "invalid_storage_path"
    monkeypatch.setattr(lifecycle, "_schema_root", lambda *_a: (_ for _ in ()).throw(RuntimeError("boom")))
    assert capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="v1")["status"] == "capture_error"


def test_capture_rejects_privacy_enabled_adapter_after_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _adapter(tmp_path)
    monkeypatch.setattr(
        lifecycle,
        "_valid_adapter",
        lambda *_a: ({"enabled": True, "events": ["usage_episode", "usage_feedback"], "privacy": {"raw_prompt": True, "raw_transcript": False}}, None),
    )

    result = capture_lifecycle_outcome(repo_root=tmp_path, lifecycle_kind="issue_close", evidence_locator="v1")

    assert result["status"] == "invalid_adapter"


@pytest.mark.parametrize("script", [
    "skills/public/issue/scripts/issue_close.py",
    "skills/public/release/scripts/publish_release_common.py",
])
def test_lifecycle_producers_report_missing_helper_and_capture_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, script: str) -> None:
    module = runpy.run_path(script)
    capture = module["_capture_lifecycle"]
    class NoParentsPath:
        def resolve(self):
            return self

        @property
        def parents(self):
            return ()

    capture.__globals__["Path"] = lambda *_a, **_k: NoParentsPath()
    kwargs = {"repo_root": tmp_path}
    if script.endswith("issue_close.py"):
        kwargs.update(repo="acme/demo", number=1)
    else:
        kwargs.update(tag_name="v1.0.0")
    assert capture(**kwargs)["status"] == "capture_error"
    capture.__globals__["Path"] = Path

    monkeypatch.setattr(module["runpy"], "run_path", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    kwargs = {"repo_root": tmp_path}
    if script.endswith("issue_close.py"):
        kwargs.update(repo="acme/demo", number=1)
    else:
        kwargs.update(tag_name="v1.0.0")
    result = capture(**kwargs)
    assert result["status"] == "capture_error" and "boom" in result["errors"][0]


def test_issue_capture_delegates_successfully(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = runpy.run_path("skills/public/issue/scripts/issue_close.py")
    capture = module["_capture_lifecycle"]
    observed: dict[str, object] = {}

    def fake_capture(**kwargs):
        observed.update(kwargs)
        return {"status": "appended"}

    monkeypatch.setattr(module["runpy"], "run_path", lambda *_a, **_k: {"capture_lifecycle_outcome": fake_capture})

    result = capture(repo_root=tmp_path, repo="acme/demo", number=42)

    assert result == {"status": "appended"}
    assert observed == {"repo_root": tmp_path, "lifecycle_kind": "issue_close", "evidence_locator": "acme/demo#42"}
