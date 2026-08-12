from __future__ import annotations

import json
import math
import runpy
import sys
from pathlib import Path

import pytest

from scripts import lesson_selection_preview_lib as preview
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
RETRO_DIR = ROOT / "charness-artifacts/retro"


def _build(seed: str = "stable-preview-seed") -> dict:
    return preview.build_lesson_selection_preview(
        repo_root=ROOT,
        output_dir=RETRO_DIR,
        summary_path=RETRO_DIR / "recent-lessons.md",
        seed=seed,
    )


def test_preview_is_flat_seeded_and_accounts_for_archive_fallback() -> None:
    first = _build()
    second = _build()
    assert first == second
    assert first["kind"] == preview.KIND
    assert first["schema_version"] == preview.SCHEMA_VERSION
    assert first["mode"] == "preview"
    assert first["eligible_count"] == 16
    assert first["bucket_counts"] == {
        "recent": 3,
        "value": 3,
        "uncertainty": 3,
        "archive": 0,
        "archive_fallback_uncertainty": 1,
    }
    assert len(first["items"]) == 10
    assert len({item["lesson_id"] for item in first["items"]}) == 10
    assert all(
        set(item) == {"lesson_id", "lesson", "latest_source_path"} for item in first["items"]
    )


def test_preview_uses_the_pinned_shrunk_mean_and_ucb_formula() -> None:
    row = {"score_total": 3, "score_count": 1}
    assert preview._value(row) == 1
    assert preview._uncertainty(row, 2) == pytest.approx(1 + math.sqrt(math.log(2) / 2))


def test_preview_requires_a_nonempty_seed() -> None:
    with pytest.raises(ValueError, match="seed must be"):
        _build("")


def test_preview_renderer_cli_emits_json_and_flat_text(monkeypatch, capsys) -> None:
    renderer = load_script_module(
        "render_lesson_selection_preview_for_test",
        ROOT / "scripts" / "render_lesson_selection_preview.py",
    )
    rendered = {
        "items": [{"lesson_id": "a", "lesson": "useful lesson"}],
        "eligible_count": 1,
    }
    monkeypatch.setattr(renderer, "build_lesson_selection_preview", lambda **_kwargs: rendered)
    monkeypatch.setattr(
        sys,
        "argv",
        ["render_lesson_selection_preview.py", "--seed", "stable-preview-seed", "--json"],
    )
    assert renderer.main() == 0
    assert json.loads(capsys.readouterr().out) == rendered
    monkeypatch.setattr(
        sys,
        "argv",
        ["render_lesson_selection_preview.py", "--seed", "stable-preview-seed"],
    )
    assert renderer.main() == 0
    assert (
        capsys.readouterr().out == "Lesson selection preview (1/1 eligible):\n- a — useful lesson\n"
    )


def test_preview_renderer_script_entrypoint_exits_successfully(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_lesson_selection_preview.py",
            "--repo-root",
            str(ROOT),
            "--seed",
            "stable-preview-seed",
            "--json",
        ],
    )
    with pytest.raises(SystemExit, match="0"):
        runpy.run_path(
            str(ROOT / "scripts" / "render_lesson_selection_preview.py"), run_name="__main__"
        )
    assert json.loads(capsys.readouterr().out)["kind"] == preview.KIND


def test_preview_rejects_closed_ledger_candidate_and_recent_shapes(
    tmp_path: Path, monkeypatch
) -> None:
    ledger_path = tmp_path / "lesson-ledger.json"
    ledger_path.write_text(json.dumps({"lessons": []}), encoding="utf-8")
    monkeypatch.setattr(preview, "validate_lesson_ledger", lambda **_kwargs: None)
    monkeypatch.setattr(preview, "lesson_ledger_path", lambda _output_dir: ledger_path)
    with pytest.raises(ValueError, match="could not be loaded"):
        preview._load_validated_ledger(tmp_path, tmp_path, tmp_path / "summary.md")

    lessons = {"a": {"score_total": 0, "score_count": 0}}
    base = {
        "recurrence_class": "a",
        "lesson": "text",
        "latest_source_path": "source.md",
        "selection_weight": 1,
    }
    cases = [
        ({}, lessons, "no candidate list"),
        ({"candidates": [None]}, lessons, "non-object"),
        ({"candidates": [base, base]}, lessons, "duplicate recurrence"),
        ({"candidates": [base]}, {"a": None}, "not an object"),
        ({"candidates": [{"recurrence_class": "a"}]}, lessons, "lacks"),
        ({"candidates": [base]}, {"a": {"score_total": True, "score_count": 0}}, "non-integer"),
        ({"candidates": [{**base, "lesson": 1}]}, lessons, "invalid rendered"),
        ({"candidates": []}, lessons, "every seeded"),
    ]
    for index, candidate_lessons, message in cases:
        with pytest.raises(ValueError, match=message):
            preview._candidate_rows(index, candidate_lessons)
    assert (
        preview._recent_key({**base, "lesson_id": "a", "latest_source_date": "not-a-date"})[-1]
        == "a"
    )
    with pytest.raises(ValueError, match="invalid selection_weight"):
        preview._recent_key(
            {**base, "lesson_id": "a", "latest_source_date": None, "selection_weight": True}
        )
