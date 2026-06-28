from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

jsonschema = pytest.importorskip("jsonschema")

REPO_ROOT = Path(__file__).resolve().parent.parent
USAGE_DIR = REPO_ROOT / "integrations" / "usage-episodes"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def acme_episode() -> dict:
    return {
        "schema_version": 1,
        "event_type": "usage_episode",
        "timestamp": "2026-05-17T04:00:00Z",
        "product_id": "acme",
        "episode_id": "acme-episode-001",
        "actor_kind": "operator",
        "context_bucket": "slack_thread",
        "entry_point": "mention",
        "trigger_type": "explicit_request",
        "selected_job": "file_github_issue",
        "core_action": "created_issue_from_thread",
        "agent_action": {
            "surface": "github_issue_create",
            "capability_ref": "github.issue",
        },
        "first_value_ref": {
            "kind": "github_issue",
            "ref": "corca-ai/charness#171",
        },
        "outcome_status": "delivered",
        "feedback_signal": "follow_up_requested",
        "t_status": "candidate",
        "t_link": {
            "kind": "spec",
            "path": "charness-artifacts/spec/issue-171-hlam-usage-episodes.md",
            "ref": "issue-171-hlam-usage-episodes",
        },
        "t_evidence": {
            "rule_id": "product-stub-rule",
            "confidence": "medium",
            "matched_paths": ["charness-artifacts/spec/issue-171-hlam-usage-episodes.md"],
            "commit_refs": ["deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"],
            "diff_kind": "added",
        },
    }


def crill_episode() -> dict:
    return {
        "schema_version": 1,
        "event_type": "usage_episode",
        "timestamp": "2026-05-17T04:05:00Z",
        "product_id": "crill",
        "episode_id": "crill-episode-001",
        "actor_kind": "human",
        "context_bucket": "product_workspace",
        "entry_point": "ui",
        "trigger_type": "explicit_request",
        "selected_job": "review_product_state",
        "core_action": "generated_decision_snapshot",
        "agent_action": {
            "surface": "product_workflow",
        },
        "first_value_ref": {
            "kind": "product_artifact",
            "ref": "snapshot-001",
        },
        "outcome_status": "delivered",
        "feedback_signal": "accepted",
        "t_status": "none",
    }


def test_manifest_schema_is_draft07_valid() -> None:
    jsonschema.Draft7Validator.check_schema(_load_json(USAGE_DIR / "manifest.schema.json"))


def test_episode_schema_is_draft07_valid() -> None:
    jsonschema.Draft7Validator.check_schema(_load_json(USAGE_DIR / "episode.schema.json"))


def test_adapter_example_validates_against_manifest_schema() -> None:
    jsonschema.validate(
        _load_yaml(USAGE_DIR / "adapter.example.yaml"),
        _load_json(USAGE_DIR / "manifest.schema.json"),
    )


@pytest.mark.parametrize("record", [acme_episode(), crill_episode()])
def test_valid_usage_episode_records_pass(record: dict) -> None:
    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_candidate_usage_episode_may_omit_t_link() -> None:
    record = acme_episode()
    record["t_status"] = "candidate"
    record.pop("t_link")

    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_promoted_usage_episode_requires_t_link() -> None:
    record = acme_episode()
    record["t_status"] = "promoted"
    record.pop("t_link")

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_usage_episode_can_share_privacy_safe_context_ref() -> None:
    context_ref = {
        "kind": "slack_thread",
        "ref": "acme-context-opaque-001",
    }
    first = acme_episode()
    second = acme_episode()
    second["episode_id"] = "acme-episode-002"
    first["context_ref"] = dict(context_ref)
    second["context_ref"] = dict(context_ref)

    schema = _load_json(USAGE_DIR / "episode.schema.json")
    jsonschema.validate(first, schema)
    jsonschema.validate(second, schema)
    assert first["context_ref"] == second["context_ref"]


@pytest.mark.parametrize(
    "record",
    [
        {**acme_episode(), "agent_action": {}},
        {**acme_episode(), "t_status": "candidate", "t_link": None},
        {**crill_episode(), "t_status": "none", "t_link": {"kind": "x", "ref": "y"}},
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "body": "raw source content is not allowed",
            },
        },
        {**acme_episode(), "actor_kind": "customer"},
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "line one\nline two",
            },
        },
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "../outside.md",
            },
        },
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "/tmp/outside.md",
            },
        },
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "C:/tmp/outside.md",
            },
        },
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "C:\\tmp\\outside.md",
            },
        },
        {
            **acme_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "..\\outside.md",
            },
        },
    ],
)
def test_invalid_usage_episode_records_rejected(record: dict) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


@pytest.mark.parametrize(
    "adapter",
    [
        {"version": 1, "enabled": True, "privacy": {"raw_prompt": True}},
        {"version": 1, "enabled": True, "privacy": {"raw_transcript": True}},
        {"version": 1, "enabled": True, "privacy": {"raw_prompt": False}},
        {"version": 1, "enabled": True, "storage_path": "/tmp/usage"},
        {"version": 1, "enabled": True, "storage_path": "../usage"},
        {"version": 1, "enabled": True, "storage_path": "C:/tmp/usage"},
        {"version": 1, "enabled": True, "storage_path": "C:\\tmp\\usage"},
        {"version": 1, "enabled": True, "storage_path": "..\\usage"},
    ],
)
def test_invalid_adapter_privacy_and_path_boundaries_rejected(adapter: dict) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(adapter, _load_json(USAGE_DIR / "manifest.schema.json"))


def test_usage_episodes_exported_to_checked_in_plugin() -> None:
    plugin_dir = REPO_ROOT / "plugins" / "charness" / "integrations" / "usage-episodes"
    for name in ("adapter.example.yaml", "episode.schema.json", "manifest.schema.json"):
        assert (plugin_dir / name).read_text(encoding="utf-8") == (USAGE_DIR / name).read_text(encoding="utf-8")


def test_session_id_accepted_when_present() -> None:
    record = crill_episode()
    record["session_id"] = "a1b2c3d4-e5f6-7890-abcd-ef0123456789"
    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


@pytest.mark.parametrize(
    "session_id",
    [
        "",
        "has space",
        "with/slash",
        "line\nbreak",
        "_leading_underscore_forbidden",
        "x" * 129,
    ],
)
def test_invalid_session_id_rejected(session_id: str) -> None:
    record = crill_episode()
    record["session_id"] = session_id

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_classifier_signal_episode_validates() -> None:
    record = crill_episode()
    record["t_status"] = "memory_lesson_added"
    record["t_evidence"] = {
        "rule_id": "retro-lesson-path-added",
        "confidence": "high",
        "matched_paths": ["charness-artifacts/retro/2026-05-22-foo-session.md"],
        "commit_refs": ["abc1234"],
        "diff_kind": "added",
    }
    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_classifier_signal_requires_t_evidence_when_t_status_nonempty() -> None:
    record = crill_episode()
    record["t_status"] = "memory_lesson_added"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_classification_skipped_forbidden_when_t_status_nonempty() -> None:
    record = crill_episode()
    record["t_status"] = "memory_lesson_added"
    record["t_evidence"] = {
        "rule_id": "retro-lesson-path-added",
        "confidence": "high",
        "matched_paths": ["charness-artifacts/retro/2026-05-22-foo-session.md"],
        "commit_refs": ["abc1234"],
        "diff_kind": "added",
    }
    record["classification_skipped"] = "no_parent"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_classification_skipped_allowed_when_t_status_none() -> None:
    record = crill_episode()
    record["classification_skipped"] = "no_parent"
    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


@pytest.mark.parametrize(
    "evidence",
    [
        {"rule_id": "bad rule", "confidence": "high", "matched_paths": ["a"], "commit_refs": ["abc1234"], "diff_kind": "added"},
        {"rule_id": "ok", "confidence": "unknown", "matched_paths": ["a"], "commit_refs": ["abc1234"], "diff_kind": "added"},
        {"rule_id": "ok", "confidence": "high", "matched_paths": [], "commit_refs": ["abc1234"], "diff_kind": "added"},
        {"rule_id": "ok", "confidence": "high", "matched_paths": ["../escape"], "commit_refs": ["abc1234"], "diff_kind": "added"},
        {"rule_id": "ok", "confidence": "high", "matched_paths": ["a"], "commit_refs": ["NOT-HEX"], "diff_kind": "added"},
        {"rule_id": "ok", "confidence": "high", "matched_paths": ["a"], "commit_refs": ["abc1234"], "diff_kind": "rotated"},
    ],
)
def test_invalid_t_evidence_rejected(evidence: dict) -> None:
    record = crill_episode()
    record["t_status"] = "memory_lesson_added"
    record["t_evidence"] = evidence

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))
