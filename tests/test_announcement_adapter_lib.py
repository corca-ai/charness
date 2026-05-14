from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.announcement_adapter_lib import (
    load_announcement_adapter,
    validate_announcement_adapter_data,
)

ROOT = Path(__file__).resolve().parents[1]


def write_adapter(repo_root: Path, body: str) -> None:
    target = repo_root / ".agents" / "announcement-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def test_legacy_adapter_without_new_fields_validates_with_default_values(tmp_path: Path) -> None:
    legacy_body = "\n".join(
        [
            "version: 1",
            "repo: demo",
            "product_name: Demo",
            "language: en",
            "output_dir: charness-artifacts/announcement",
            "sections:",
            "- Highlights",
            "- Changes",
            "audience_tags: []",
            "omission_lenses: []",
            "delivery_kind: none",
            "delivery_target: ''",
            "release_notes_path: ''",
            "post_command_template: ''",
            "delivery_capability: ''",
        ]
    ) + "\n"
    write_adapter(tmp_path, legacy_body)
    payload = load_announcement_adapter(tmp_path)
    assert payload["valid"] is True
    assert payload["errors"] == []
    data = payload["data"]
    assert data["outputs"] == []
    assert data["in_progress_sources"] == []
    assert data["format_rules_path"] == ""
    assert data["message_size_limit"] == 0
    assert data["public_body_shape"] == "chat_update"


def test_release_notes_delivery_defaults_public_body_shape_to_release_notes(tmp_path: Path) -> None:
    validated, errors, _warnings = validate_announcement_adapter_data(
        {"delivery_kind": "release-notes", "release_notes_path": "CHANGELOG.md"}, tmp_path
    )
    assert errors == []
    assert validated["public_body_shape"] == "release_notes"


def test_public_body_shape_can_be_set_explicitly(tmp_path: Path) -> None:
    validated, errors, _warnings = validate_announcement_adapter_data(
        {"delivery_kind": "release-notes", "public_body_shape": "chat_update"}, tmp_path
    )
    assert errors == []
    assert validated["public_body_shape"] == "chat_update"


def test_public_body_shape_rejects_unknown_values(tmp_path: Path) -> None:
    _validated, errors, _warnings = validate_announcement_adapter_data(
        {"public_body_shape": "adapter_taxonomy"}, tmp_path
    )
    assert any("public_body_shape" in error for error in errors)


def test_init_adapter_scaffolds_public_body_shape(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            str(ROOT / "skills" / "public" / "announcement" / "scripts" / "init_adapter.py"),
            "--repo-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    adapter_text = (tmp_path / ".agents" / "announcement-adapter.yaml").read_text(encoding="utf-8")
    assert "public_body_shape: chat_update" in adapter_text


def test_outputs_validation_rejects_duplicate_id_and_unknown_delivery_role(tmp_path: Path) -> None:
    data = {
        "outputs": [
            {"id": "body", "audience_tags": ["user"], "delivery_role": "parent"},
            {"id": "body", "audience_tags": ["user"], "delivery_role": "thread_reply"},
            {"id": "extra", "audience_tags": ["operator"], "delivery_role": "ghostly"},
        ],
    }
    validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("duplicated" in error for error in errors)
    assert any("delivery_role" in error for error in errors)
    assert validated["outputs"] == [
        {"id": "body", "audience_tags": ["user"], "delivery_role": "parent"}
    ]


def test_thread_reply_without_parent_handle_placeholder_emits_warning(tmp_path: Path) -> None:
    data = {
        "delivery_kind": "human-backend",
        "post_command_template": "slack-post --file {message_file_q}",
        "delivery_capability": "slack",
        "outputs": [
            {"id": "body", "audience_tags": ["user"], "delivery_role": "parent"},
            {"id": "reply", "audience_tags": ["operator"], "delivery_role": "thread_reply"},
        ],
    }
    _validated, errors, warnings = validate_announcement_adapter_data(data, tmp_path)
    assert errors == []
    assert any("{parent_delivery_handle}" in warning for warning in warnings)


def test_thread_reply_with_parent_handle_placeholder_does_not_warn(tmp_path: Path) -> None:
    data = {
        "delivery_kind": "human-backend",
        "post_command_template": "slack-post --file {message_file_q} --thread {parent_delivery_handle_q}",
        "delivery_capability": "slack",
        "outputs": [
            {"id": "body", "audience_tags": ["user"], "delivery_role": "parent"},
            {"id": "reply", "audience_tags": ["operator"], "delivery_role": "thread_reply"},
        ],
    }
    _validated, errors, warnings = validate_announcement_adapter_data(data, tmp_path)
    assert errors == []
    assert not any("{parent_delivery_handle}" in warning for warning in warnings)


def test_thread_reply_without_parent_output_emits_warning(tmp_path: Path) -> None:
    data = {
        "delivery_kind": "human-backend",
        "post_command_template": "slack-post --file {message_file_q} --thread {parent_delivery_handle_q}",
        "delivery_capability": "slack",
        "outputs": [
            {"id": "reply", "audience_tags": ["operator"], "delivery_role": "thread_reply"},
        ],
    }
    _validated, errors, warnings = validate_announcement_adapter_data(data, tmp_path)
    assert errors == []
    assert any("without a preceding `parent`" in warning for warning in warnings)


def test_in_progress_sources_validation_requires_path_for_kind_path(tmp_path: Path) -> None:
    data = {"in_progress_sources": [{"kind": "path"}]}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("kind=path" in error for error in errors)


def test_in_progress_sources_accepts_host_extensible_kind(tmp_path: Path) -> None:
    data = {
        "in_progress_sources": [
            {"kind": "control_repo", "path": "/srv/ceal-prod/workspace/control"},
            {"kind": "channel_automation", "summary": "Slack workspace events"},
        ]
    }
    validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert errors == []
    kinds = [entry["kind"] for entry in validated["in_progress_sources"]]
    assert kinds == ["control_repo", "channel_automation"]
    assert validated["in_progress_sources"][1]["summary"] == "Slack workspace events"


def test_in_progress_sources_rejects_invalid_kind_identifier(tmp_path: Path) -> None:
    data = {"in_progress_sources": [{"kind": "Control Repo", "path": "/srv"}]}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("kind" in error.lower() for error in errors)


def test_in_progress_sources_unknown_kind_requires_at_least_one_field(tmp_path: Path) -> None:
    data = {"in_progress_sources": [{"kind": "control_repo"}]}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("requires at least one of" in error for error in errors)


def test_message_size_limit_rejects_negative_int(tmp_path: Path) -> None:
    data = {"message_size_limit": -5}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("message_size_limit" in error for error in errors)
