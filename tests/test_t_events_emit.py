from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from scripts.t_events_emit_lib import (
    append_event,
    emit_lesson_cited,
    emit_retro_lesson_cites,
    extract_lesson_cites_from_markdown,
    load_adapter,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

jsonschema = pytest.importorskip("jsonschema")

T_EVENTS_DIR = REPO_ROOT / "integrations" / "t-events"


def _write_adapter(repo_root: Path, body: str) -> Path:
    adapter_dir = repo_root / ".agents"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    path = adapter_dir / "t-events-adapter.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_load_adapter_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_adapter(tmp_path) is None


def test_emit_no_op_without_adapter(tmp_path: Path) -> None:
    result = emit_lesson_cited(
        tmp_path,
        lesson_path="charness-artifacts/retro/x.md",
        citing_skill="retro",
    )
    assert result == {"emitted": False, "reason": "no_adapter"}
    assert not (tmp_path / ".charness").exists()


def test_emit_no_op_when_disabled(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "version: 1\nenabled: false\n")
    result = emit_lesson_cited(
        tmp_path,
        lesson_path="charness-artifacts/retro/x.md",
        citing_skill="retro",
    )
    assert result == {"emitted": False, "reason": "disabled"}


def test_emit_lesson_cited_writes_jsonl_validating_event_schema(tmp_path: Path) -> None:
    _write_adapter(
        tmp_path,
        "version: 1\nenabled: true\nstorage_path: .charness/t-events\n",
    )
    result = emit_lesson_cited(
        tmp_path,
        lesson_path="charness-artifacts/retro/2026-05-09-x.md",
        citing_skill="retro",
        citing_artifact_path="charness-artifacts/retro/2026-05-09-y.md",
    )
    assert result["emitted"] is True
    target = tmp_path / ".charness/t-events/lesson_cited.jsonl"
    assert target.is_file()
    rows = _read_jsonl(target)
    assert len(rows) == 1
    schema = json.loads((T_EVENTS_DIR / "event.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(rows[0], schema)
    assert rows[0]["citing_skill"] == "retro"


def test_event_filter_drops_unselected_event_type(tmp_path: Path) -> None:
    _write_adapter(
        tmp_path,
        textwrap.dedent(
            """
            version: 1
            enabled: true
            events:
              - skill_invoked
            """
        ).strip()
        + "\n",
    )
    result = emit_lesson_cited(
        tmp_path,
        lesson_path="charness-artifacts/retro/x.md",
        citing_skill="retro",
    )
    assert result == {"emitted": False, "reason": "event_filtered"}
    assert not (tmp_path / ".charness/t-events/lesson_cited.jsonl").exists()


def test_invalid_event_type_rejected_before_write(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "version: 1\nenabled: true\n")
    bad = {"event_type": "skill_archived", "timestamp": "2026-05-09T12:00:00Z"}
    result = append_event(tmp_path, bad)
    assert result == {"emitted": False, "reason": "invalid_event_type"}
    assert not (tmp_path / ".charness/t-events").exists()


def test_extract_lesson_cites_from_inline_and_sources(tmp_path: Path) -> None:
    text = textwrap.dedent(
        """
        # Retro

        - Plain inline (source: charness-artifacts/retro/2026-05-09-a.md)
        - Backticked inline (source: `charness-artifacts/retro/2026-05-09-b.md`)
        - Duplicate plain (source: charness-artifacts/retro/2026-05-09-a.md)
        - Duplicate backticked (source: `charness-artifacts/retro/2026-05-09-b.md`)

        ## Sources

        - charness-artifacts/retro/2026-05-09-c.md
        - `charness-artifacts/retro/2026-05-09-a.md`
        """
    )
    cites = extract_lesson_cites_from_markdown(text)
    assert cites == [
        "charness-artifacts/retro/2026-05-09-a.md",
        "charness-artifacts/retro/2026-05-09-b.md",
        "charness-artifacts/retro/2026-05-09-c.md",
    ]


def test_extract_lesson_cites_matches_charness_recent_lessons_format() -> None:
    r"""Guard against fixture-vs-real-content drift.

    The repo's actual ``charness-artifacts/retro/recent-lessons.md`` annotates
    each bullet with ``(source: `charness-artifacts/retro/...`)`` — the
    backticked form. Earlier the inline regex assumed bare paths, producing
    zero hits on real input despite all unit fixtures passing.
    """
    real_lessons = REPO_ROOT / "charness-artifacts" / "retro" / "recent-lessons.md"
    if not real_lessons.is_file():
        pytest.skip("recent-lessons.md not present in this checkout")
    cites = extract_lesson_cites_from_markdown(real_lessons.read_text(encoding="utf-8"))
    assert cites, "extractor returned 0 cites against real recent-lessons.md"
    assert all(c.startswith("charness-artifacts/retro/") for c in cites)


def test_emit_retro_lesson_cites_emits_per_unique_cite(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "version: 1\nenabled: true\n")
    text = textwrap.dedent(
        """
        # Retro

        - Lesson one (source: charness-artifacts/retro/2026-05-09-a.md)
        - Lesson two (source: charness-artifacts/retro/2026-05-09-b.md)
        """
    )
    summary = emit_retro_lesson_cites(
        tmp_path,
        markdown_text=text,
        citing_artifact_path="charness-artifacts/retro/2026-05-09-z.md",
    )
    assert summary == {
        "emitted_count": 2,
        "skipped_count": 0,
        "reasons": {},
        "cite_count": 2,
    }
    rows = _read_jsonl(tmp_path / ".charness/t-events/lesson_cited.jsonl")
    assert {row["lesson_path"] for row in rows} == {
        "charness-artifacts/retro/2026-05-09-a.md",
        "charness-artifacts/retro/2026-05-09-b.md",
    }
    assert all(row["citing_skill"] == "retro" for row in rows)
    assert all(
        row["citing_artifact_path"] == "charness-artifacts/retro/2026-05-09-z.md"
        for row in rows
    )


def test_emit_retro_lesson_cites_no_op_without_adapter(tmp_path: Path) -> None:
    summary = emit_retro_lesson_cites(
        tmp_path,
        markdown_text="(source: charness-artifacts/retro/x.md)",
        citing_artifact_path="charness-artifacts/retro/y.md",
    )
    assert summary == {
        "emitted_count": 0,
        "skipped_count": 1,
        "reasons": {"no_adapter": 1},
        "cite_count": 1,
    }


def test_rotation_renames_when_size_exceeds_threshold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_adapter(
        tmp_path,
        textwrap.dedent(
            """
            version: 1
            enabled: true
            rotation:
              max_files: 2
              max_size_mb: 1
            """
        ).strip()
        + "\n",
    )
    target_dir = tmp_path / ".charness/t-events"
    target_dir.mkdir(parents=True)
    target = target_dir / "lesson_cited.jsonl"
    target.write_bytes(b"x" * (1024 * 1024 + 16))
    result = emit_lesson_cited(
        tmp_path,
        lesson_path="charness-artifacts/retro/x.md",
        citing_skill="retro",
    )
    assert result["emitted"] is True
    survivors = sorted(p.name for p in target_dir.iterdir())
    rotated = [name for name in survivors if name != "lesson_cited.jsonl"]
    assert rotated, f"rotation did not run; saw {survivors}"
    assert target.is_file()
    assert target.stat().st_size < 1024 * 1024
