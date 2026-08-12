from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lesson_ledger_lib as ledger  # noqa: E402


def _retro(repo: Path, name: str, lesson_class: str) -> None:
    path = repo / "charness-artifacts/retro" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: {lesson_class})\n",
        encoding="utf-8",
    )


def _ledger(repo: Path, *, source: str = "charness-artifacts/retro/source.md") -> Path:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    payload = {
        "kind": ledger.KIND,
        "schema_version": ledger.SCHEMA_VERSION,
        "transitions": [{"sequence": 1, "transition_id": "seed-a", "lesson_id": "a", "source_retro": source}],
        "lessons": {"a": {"source_retro": source, "transition_id": "seed-a"}},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_ledger_replays_a_cited_transition(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    result = ledger.validate_lesson_ledger(
        repo_root=tmp_path,
        output_dir=tmp_path / "charness-artifacts/retro",
        summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
    )
    assert result["lesson_count"] == 1


def test_ledger_rejects_a_projection_or_citation_rewrite(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, source="charness-artifacts/retro/other.md")
    with pytest.raises(ValueError, match="citation does not declare"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "charness-artifacts/retro",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["transitions"][0]["source_retro"] = "charness-artifacts/retro/source.md"
    payload["lessons"]["a"]["transition_id"] = "edited"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="materialized lessons"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "charness-artifacts/retro",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )


def test_ledger_rejects_deferred_graduation_fields(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["transitions"][0]["contract_target"] = "AGENTS.md"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="deferred graduation"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "charness-artifacts/retro",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )
