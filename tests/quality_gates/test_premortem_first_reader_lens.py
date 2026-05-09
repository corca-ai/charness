from __future__ import annotations

from .support import ROOT


def test_angle_selection_lists_first_reader_lens() -> None:
    text = (ROOT / "skills" / "public" / "premortem" / "references" / "angle-selection.md").read_text(
        encoding="utf-8"
    )

    assert "`first-reader`" in text
    assert "plain-language" in text
    assert "legacy-coupled" in text
    assert "product-story-before-taxonomy" in text
    assert "title-slug coherence" in text


def test_angle_selection_triggers_first_reader_lens_for_durable_doc_decisions() -> None:
    text = (ROOT / "skills" / "public" / "premortem" / "references" / "angle-selection.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(text.split())

    rotation_section = normalized.split("Rotate or swap angles", 1)[1]
    for trigger in (
        "durable docs",
        "spec indexes",
        "public skill prose",
        "README-like surfaces",
        "source-of-truth narrative",
        "check_title_slug_drift.py",
    ):
        assert trigger in rotation_section, f"missing trigger: {trigger}"


def test_proposal_flow_recommends_drift_check_for_rename_heavy_edits() -> None:
    text = (ROOT / "skills" / "public" / "quality" / "references" / "proposal-flow.md").read_text(
        encoding="utf-8"
    )

    assert "check_title_slug_drift.py" in text
    assert "docs/specs" in text
