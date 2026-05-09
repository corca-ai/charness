from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

jsonschema = pytest.importorskip("jsonschema")

REPO_ROOT = Path(__file__).resolve().parent.parent
T_EVENTS_DIR = REPO_ROOT / "integrations" / "t-events"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_manifest_schema_is_draft07_valid() -> None:
    schema = _load_json(T_EVENTS_DIR / "manifest.schema.json")
    jsonschema.Draft7Validator.check_schema(schema)


def test_event_schema_is_draft07_valid() -> None:
    schema = _load_json(T_EVENTS_DIR / "event.schema.json")
    jsonschema.Draft7Validator.check_schema(schema)


def test_adapter_example_validates_against_manifest_schema() -> None:
    schema = _load_json(T_EVENTS_DIR / "manifest.schema.json")
    example = _load_yaml(T_EVENTS_DIR / "adapter.example.yaml")
    jsonschema.validate(example, schema)


@pytest.mark.parametrize(
    "record",
    [
        {
            "event_type": "skill_invoked",
            "timestamp": "2026-05-09T12:00:00Z",
            "skill_id": "critique",
        },
        {
            "event_type": "skill_invoked",
            "timestamp": "2026-05-09T12:00:00Z",
            "skill_id": "retro",
            "session_id": "abc-123",
            "trigger_phrase": "let's run a retro",
        },
        {
            "event_type": "lesson_cited",
            "timestamp": "2026-05-09T12:00:01Z",
            "lesson_path": "charness-artifacts/retro/2026-05-09-x.md",
            "citing_skill": "retro",
        },
        {
            "event_type": "lesson_cited",
            "timestamp": "2026-05-09T12:00:01Z",
            "lesson_path": "charness-artifacts/retro/2026-05-09-x.md",
            "citing_skill": "critique",
            "citing_artifact_path": "charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md",
        },
        {
            "event_type": "anchor_invoked",
            "timestamp": "2026-05-09T12:00:02Z",
            "anchor_id": "engelbart",
            "applies_when": "system-improving-itself",
            "citing_skill": "critique",
        },
        {
            "event_type": "anchor_invoked",
            "timestamp": "2026-05-09T12:00:02Z",
            "anchor_id": "raskin",
            "applies_when": "lam-critique",
            "citing_skill": "critique",
            "previous_anchor_id": "jackson",
        },
    ],
)
def test_valid_event_records_pass(record: dict) -> None:
    schema = _load_json(T_EVENTS_DIR / "event.schema.json")
    jsonschema.validate(record, schema)


@pytest.mark.parametrize(
    "record",
    [
        # missing required field (skill_id)
        {"event_type": "skill_invoked", "timestamp": "2026-05-09T12:00:00Z"},
        # unknown event_type
        {
            "event_type": "skill_archived",
            "timestamp": "2026-05-09T12:00:00Z",
            "skill_id": "x",
        },
        # applies_when outside closed value set
        {
            "event_type": "anchor_invoked",
            "timestamp": "2026-05-09T12:00:02Z",
            "anchor_id": "engelbart",
            "applies_when": "meta-critique",
            "citing_skill": "critique",
        },
        # additional property on lesson_cited
        {
            "event_type": "lesson_cited",
            "timestamp": "2026-05-09T12:00:01Z",
            "lesson_path": "x.md",
            "citing_skill": "retro",
            "extra_field": "nope",
        },
    ],
)
def test_invalid_event_records_rejected(record: dict) -> None:
    schema = _load_json(T_EVENTS_DIR / "event.schema.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, schema)


def test_manifest_rejects_unknown_event_in_subset() -> None:
    schema = _load_json(T_EVENTS_DIR / "manifest.schema.json")
    bad = {
        "version": 1,
        "enabled": True,
        "events": ["skill_archived"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_manifest_minimal_form() -> None:
    schema = _load_json(T_EVENTS_DIR / "manifest.schema.json")
    minimal = {"version": 1, "enabled": False}
    jsonschema.validate(minimal, schema)
