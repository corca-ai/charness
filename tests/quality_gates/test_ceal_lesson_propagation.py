from __future__ import annotations

from .support import ROOT


def test_announcement_draft_shape_lists_release_note_digest_density() -> None:
    text = (ROOT / "skills" / "public" / "announcement" / "references" / "draft-shape.md").read_text(
        encoding="utf-8"
    )

    assert "Release-Note Digest Density" in text
    assert "2-4 actionable items" in text
    assert "who cares" in text
    assert "source links" in text
    assert "thread" in text
    assert "unfurls" in text


def test_announcement_draft_shape_lists_public_body_shape_reframing() -> None:
    text = (ROOT / "skills" / "public" / "announcement" / "references" / "draft-shape.md").read_text(
        encoding="utf-8"
    )

    assert "Public Body Shape" in text
    assert "public_body_shape" in text
    assert "chat_update" in text
    assert "reader-visible outcomes" in text
    assert "coverage hints" in text
    assert "proof vocabulary" in text


def test_announcement_draft_shape_lists_affordance_and_alias_rewrite() -> None:
    text = (ROOT / "skills" / "public" / "announcement" / "references" / "draft-shape.md").read_text(
        encoding="utf-8"
    )

    assert "Affordance Rewrite Pass" in text
    assert "non-maintainer" in text
    assert "reader-visible affordances" in text
    assert "canonical behavior first" in text
    assert "$ceal:ignore" in text
    assert "$cig" in text


def test_gather_source_priority_includes_official_url_before_websearch() -> None:
    text = (ROOT / "skills" / "public" / "gather" / "references" / "source-priority.md").read_text(
        encoding="utf-8"
    )

    assert "Official URL Before WebSearch" in text
    assert "canonical source is identifiable" in text
    assert "WebSearch" in text
    assert "derivative summaries" in text


def test_create_skill_verification_lists_ownership_overlap_and_message_shape_regression() -> None:
    text = (ROOT / "skills" / "public" / "create-skill" / "references" / "portable-authoring.md").read_text(
        encoding="utf-8"
    )

    verification_section = text.split("## Verification", 1)[1].split("##", 1)[0]
    normalized = " ".join(verification_section.split())
    assert "ownership overlap" in normalized
    assert "semantic message-shape regression" in normalized
    assert "evaluator scenario" in normalized
    assert "proof level" in normalized


def test_debug_five_steps_lists_durable_follow_through() -> None:
    text = (ROOT / "skills" / "public" / "debug" / "references" / "five-steps.md").read_text(
        encoding="utf-8"
    )

    assert "Durable Follow-Through" in text
    normalized = " ".join(text.split())
    assert "update the durable surface" in normalized
    assert "file a follow-up issue" in normalized
    assert "explicitly record why" in normalized


def test_impl_verification_ladder_lists_completion_report_categories() -> None:
    text = (ROOT / "skills" / "public" / "impl" / "references" / "verification-ladder.md").read_text(
        encoding="utf-8"
    )

    assert "Completion Report Categories" in text
    for category in (
        "Durable changes",
        "External writes",
        "Test-only artifacts",
        "Verification",
        "Unverified future behavior",
    ):
        assert category in text, f"missing category: {category}"


def test_create_skill_packaging_documents_downstream_materialization_drift() -> None:
    text = (ROOT / "skills" / "public" / "create-skill" / "references" / "deployable-skill-packaging.md").read_text(
        encoding="utf-8"
    )

    assert "Downstream Materialization" in text
    assert "upstream-owned" in text
    assert "drift marker" in text
    assert "offline-unchanged" in text
