from __future__ import annotations

from pathlib import Path

from scripts.classify_goal_consumers import classify


def test_empty_scan_is_a_valid_empty_set(tmp_path: Path) -> None:
    payload = classify(tmp_path)

    assert payload["ok"] is True
    assert payload["rows"] == []


def test_active_legacy_consumer_is_a_defect(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "workflow.md").write_text("Use /goal @draft.md to activate.\n", encoding="utf-8")

    payload = classify(tmp_path)

    assert payload["ok"] is False
    assert any(row["classification"] == "defect" for row in payload["rows"])
    assert payload["summary"]["unassigned_rows"] == 0


def test_historical_fixture_and_generated_pair_are_distinguished(tmp_path: Path) -> None:
    fixture = tmp_path / "tests" / "test_goal_artifact_lib.py"
    fixture.parent.mkdir()
    fixture.write_text("# /goal @legacy\n", encoding="utf-8")
    source = tmp_path / "scripts" / "example.py"
    generated = tmp_path / "plugins" / "charness" / "scripts" / "example.py"
    source.parent.mkdir()
    generated.parent.mkdir(parents=True)
    source.write_text("# /goal @legacy\n", encoding="utf-8")
    generated.write_text("# /goal @legacy\n", encoding="utf-8")

    payload = classify(tmp_path)

    fixture_rows = [row for row in payload["rows"] if row["path"] == "tests/test_goal_artifact_lib.py"]
    generated_rows = [row for row in payload["rows"] if row["path"] == "plugins/charness/scripts/example.py"]
    assert fixture_rows and fixture_rows[0]["classification"] == "historical-fixture"
    assert generated_rows and generated_rows[0]["classification"] == "generated-mirror"
    assert generated_rows[0]["source_generated_pair"]["paired_path"] == "scripts/example.py"


def test_fixture_directory_and_planning_provenance_are_not_execution_defects(tmp_path: Path) -> None:
    fixture = tmp_path / "tests" / "fixtures" / "legacy.md"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("/goal @legacy.md\n", encoding="utf-8")
    provenance = tmp_path / "scripts" / "slice_manifest_lib.py"
    provenance.parent.mkdir()
    provenance.write_text("goal_path is immutable draft provenance\n", encoding="utf-8")

    payload = classify(tmp_path)

    fixture_row = next(row for row in payload["rows"] if row["path"] == "tests/fixtures/legacy.md")
    provenance_row = next(row for row in payload["rows"] if row["path"] == "scripts/slice_manifest_lib.py")
    assert fixture_row["classification"] == "historical-fixture"
    assert provenance_row["classification"] == "draft-provenance"
    assert payload["ok"] is True


def test_unreadable_file_is_reported_and_not_silently_skipped(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "broken.md").write_bytes(b"\xff\xfe")

    payload = classify(tmp_path)

    assert payload["ok"] is False
    row = next(row for row in payload["rows"] if row["path"] == "docs/broken.md")
    assert row["matched_token"] == "unreadable"
    assert row["classification"] == "defect"
