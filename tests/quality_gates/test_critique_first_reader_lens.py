from __future__ import annotations

from .support import ROOT

ANGLE_SELECTION = (
    ROOT / "skills" / "public" / "critique" / "references" / "angle-selection.md"
).read_text(encoding="utf-8")
RENAME_CRITIQUE = (
    ROOT / "skills" / "public" / "critique" / "references" / "rename-critique.md"
).read_text(encoding="utf-8")
def test_angle_selection_lists_first_reader_lens() -> None:
    text = ANGLE_SELECTION

    assert "`first-reader`" in text
    assert "plain-language" in text
    assert "legacy-coupled" in text
    assert "product-story-before-taxonomy" in text
    assert "title-slug coherence" in text


def test_angle_selection_triggers_first_reader_lens_for_durable_doc_decisions() -> None:
    text = ANGLE_SELECTION
    normalized = " ".join(text.split())

    rotation_section = normalized.split("Rotate or swap angles", 1)[1]
    for trigger in (
        "durable docs",
        "spec indexes",
        "public skill prose",
        "README-like surfaces",
        "source-of-truth narrative",
        "incoming links",
    ):
        assert trigger in rotation_section, f"missing trigger: {trigger}"


def test_proposal_flow_recommends_first_reader_check_for_rename_heavy_edits() -> None:
    text = (ROOT / "skills" / "public" / "quality" / "references" / "proposal-flow.md").read_text(
        encoding="utf-8"
    )

    assert "first-reader" in text
    assert "incoming" in text
    assert "across languages" in text


def test_rename_output_shape_uses_judgment_evidence_not_deleted_checker() -> None:
    normalized = " ".join(RENAME_CRITIQUE.split())
    assert "`Title-Slug Coherence Review`" in RENAME_CRITIQUE
    assert "H1/filename comparison" in RENAME_CRITIQUE
    assert "incoming-link/generated-index" in RENAME_CRITIQUE
    assert "without an aggregate clean verdict" in normalized
    assert "slug-drift checker" not in RENAME_CRITIQUE
