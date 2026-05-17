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


def ceal_episode() -> dict:
    return {
        "schema_version": 1,
        "event_type": "usage_episode",
        "timestamp": "2026-05-17T04:00:00Z",
        "product_id": "ceal",
        "episode_id": "ceal-episode-001",
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


@pytest.mark.parametrize("record", [ceal_episode(), crill_episode()])
def test_valid_usage_episode_records_pass(record: dict) -> None:
    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_candidate_usage_episode_may_omit_t_link() -> None:
    record = ceal_episode()
    record["t_status"] = "candidate"
    record.pop("t_link")

    jsonschema.validate(record, _load_json(USAGE_DIR / "episode.schema.json"))


def test_usage_episode_can_share_privacy_safe_context_ref() -> None:
    context_ref = {
        "kind": "slack_thread",
        "ref": "ceal-context-opaque-001",
    }
    first = ceal_episode()
    second = ceal_episode()
    second["episode_id"] = "ceal-episode-002"
    first["context_ref"] = dict(context_ref)
    second["context_ref"] = dict(context_ref)

    schema = _load_json(USAGE_DIR / "episode.schema.json")
    jsonschema.validate(first, schema)
    jsonschema.validate(second, schema)
    assert first["context_ref"] == second["context_ref"]


@pytest.mark.parametrize(
    "record",
    [
        {**ceal_episode(), "agent_action": {}},
        {**ceal_episode(), "t_status": "candidate", "t_link": None},
        {**crill_episode(), "t_status": "none", "t_link": {"kind": "x", "ref": "y"}},
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "body": "raw source content is not allowed",
            },
        },
        {**ceal_episode(), "actor_kind": "customer"},
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "line one\nline two",
            },
        },
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "../outside.md",
            },
        },
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "/tmp/outside.md",
            },
        },
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "C:/tmp/outside.md",
            },
        },
        {
            **ceal_episode(),
            "first_value_ref": {
                "kind": "github_issue",
                "ref": "corca-ai/charness#171",
                "path": "C:\\tmp\\outside.md",
            },
        },
        {
            **ceal_episode(),
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
