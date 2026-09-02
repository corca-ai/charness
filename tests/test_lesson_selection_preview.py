from __future__ import annotations

import json
import math
import runpy
import sys
from pathlib import Path

import pytest
import yaml

from scripts.lessons import lesson_selection_preview_lib as preview
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
RETRO_DIR = ROOT / "charness-artifacts/retro"


def _build(seed: str = "stable-preview-seed") -> dict:
    return preview.build_lesson_selection_preview(
        repo_root=ROOT,
        output_dir=RETRO_DIR,
        summary_path=None,
        seed=seed,
    )


def run_index_builder(*args: str):
    module = load_script_module(
        "build_retro_lesson_selection_index_under_test",
        ROOT / "scripts" / "lessons" / "build_retro_lesson_selection_index.py",
    )
    return run_loaded_script_main("build_retro_lesson_selection_index.py", module, *args)


def test_preview_is_flat_seeded_and_fills_the_empty_archive_slot_from_uncertainty() -> None:
    first = _build()
    second = _build()
    assert first == second
    assert first["kind"] == preview.KIND
    assert first["schema_version"] == preview.SCHEMA_VERSION
    assert first["mode"] == "preview"
    # Derived from the live ledger, not transcribed. This asserted `== 16` until
    # `seed_lesson_transitions.py` (#625) made adding a lesson a routine command,
    # at which point a hardcoded count fails on every seed and says nothing about
    # the preview. The invariant is that every seeded lesson is eligible.
    assert first["eligible_count"] == len(
        json.loads((RETRO_DIR / "lesson-ledger.json").read_text(encoding="utf-8"))["lessons"]
    )
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


def test_preview_uses_only_active_first_nine_and_real_archive_slot(monkeypatch) -> None:
    lessons = {
        f"lesson-{index}": {
            "score_total": index,
            "score_count": 1,
            "state": "archived" if index == 9 else "active",
        }
        for index in range(10)
    }
    candidates = [
        {
            "recurrence_class": lesson_id,
            "lesson": lesson_id,
            "latest_source_path": f"{lesson_id}.md",
            "latest_source_date": "2026-08-13",
            "selection_weight": 1,
        }
        for lesson_id in lessons
    ]
    monkeypatch.setattr(preview, "check_lesson_selection_index", lambda *_args: None)
    monkeypatch.setattr(preview, "_load_validated_ledger", lambda *_args: {"lessons": lessons})
    monkeypatch.setattr(
        preview,
        "build_lesson_selection_index",
        lambda **_kwargs: {"candidates": candidates},
    )

    result = preview.build_lesson_selection_preview(
        repo_root=ROOT,
        output_dir=RETRO_DIR,
        summary_path=None,
        seed="archive-proof",
    )

    assert result["bucket_counts"] == {
        "recent": 3,
        "value": 3,
        "uncertainty": 3,
        "archive": 1,
        "archive_fallback_uncertainty": 0,
    }
    ids = {item["lesson_id"] for item in result["items"]}
    assert ids == set(lessons)


def test_preview_requires_a_nonempty_seed() -> None:
    with pytest.raises(ValueError, match="seed must be"):
        _build("")


def test_preview_renderer_cli_emits_only_the_selection_projection(monkeypatch, capsys) -> None:
    renderer = load_script_module(
        "render_lesson_selection_preview_for_test",
        ROOT / "scripts" / "lessons" / "render_lesson_selection_preview.py",
    )
    rendered = {
        "items": [{"lesson_id": "a", "lesson": "useful lesson"}],
        "eligible_count": 1,
    }
    monkeypatch.setattr(renderer, "build_lesson_selection_preview", lambda **_kwargs: rendered)
    monkeypatch.setattr(
        sys,
        "argv",
        ["render_lesson_selection_preview.py", "--seed", "stable-preview-seed"],
    )
    assert renderer.main() == 0
    assert yaml.safe_load(capsys.readouterr().out) == rendered


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
        ],
    )
    with pytest.raises(SystemExit, match="0"):
        runpy.run_path(
            str(ROOT / "scripts" / "lessons" / "render_lesson_selection_preview.py"),
            run_name="__main__",
        )
    assert yaml.safe_load(capsys.readouterr().out)["kind"] == preview.KIND


def test_preview_rejects_malformed_ledger_candidate_and_recent_shapes(
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


def test_a_legacy_schema_consumer_can_preview_without_its_ledger_changing(tmp_path) -> None:
    """Both halves of the release-review finding, asserted together.

    A consumer still on the previously released schema must be able to run the
    session-start preview -- AGENTS.md makes it the FIRST command of every session --
    and that read must leave their ledger byte-for-byte alone, because the release
    notes prescribe rollback by reinstalling the version that wrote it.
    """
    import json
    import shutil

    output_dir = tmp_path / "charness-artifacts" / "retro"
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: null\n", encoding="utf-8"
    )
    shutil.copytree(RETRO_DIR, output_dir)
    result = run_index_builder(
        "--repo-root",
        str(tmp_path),
        "--write",
    )
    assert result.returncode == 0, result.stderr
    ledger_path = output_dir / "lesson-ledger.json"
    current = json.loads(ledger_path.read_text(encoding="utf-8"))
    from tests.lesson_ledger_fixtures import legacy_v8_payload

    legacy = legacy_v8_payload(current)
    ledger_path.write_text(json.dumps(legacy), encoding="utf-8")
    before = ledger_path.read_bytes()

    rendered = preview.build_lesson_selection_preview(
        repo_root=tmp_path,
        output_dir=output_dir,
        summary_path=None,
        seed="probe",
    )

    assert rendered["eligible_count"] >= 1
    assert ledger_path.read_bytes() == before
    assert json.loads(ledger_path.read_text(encoding="utf-8"))["schema_version"] == 8
