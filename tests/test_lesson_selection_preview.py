from __future__ import annotations

import math
from pathlib import Path

import pytest

from scripts import lesson_selection_preview_lib as preview

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
    assert all(set(item) == {"lesson_id", "lesson", "latest_source_path"} for item in first["items"])


def test_preview_uses_the_pinned_shrunk_mean_and_ucb_formula() -> None:
    row = {"score_total": 3, "score_count": 1}
    assert preview._value(row) == 1
    assert preview._uncertainty(row, 2) == pytest.approx(1 + math.sqrt(math.log(2) / 2))


def test_preview_requires_a_nonempty_seed() -> None:
    with pytest.raises(ValueError, match="seed must be"):
        _build("")
