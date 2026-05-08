from __future__ import annotations

from pathlib import Path

from scripts.announcement_adapter_lib import (
    load_announcement_adapter,
    validate_announcement_adapter_data,
)


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


def test_in_progress_sources_validation_requires_path_for_kind_path(tmp_path: Path) -> None:
    data = {"in_progress_sources": [{"kind": "path"}]}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("kind=path" in error for error in errors)


def test_message_size_limit_rejects_negative_int(tmp_path: Path) -> None:
    data = {"message_size_limit": -5}
    _validated, errors, _warnings = validate_announcement_adapter_data(data, tmp_path)
    assert any("message_size_limit" in error for error in errors)
