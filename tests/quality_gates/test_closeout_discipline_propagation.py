from __future__ import annotations

from .support import ROOT


def test_shared_closeout_discipline_reference_exists() -> None:
    path = ROOT / "skills" / "shared" / "references" / "closeout-discipline.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    for section in ("Verified Ledger", "Target Durability", "External-Source Identity"):
        assert section in text, f"missing section: {section}"
    assert "target_unavailable" in text
    assert "charness-artifacts/gather" in text


def test_issue_closeout_discipline_cites_shared_reference() -> None:
    text = (ROOT / "skills" / "public" / "issue" / "references" / "closeout-discipline.md").read_text(
        encoding="utf-8"
    )

    assert "../../../shared/references/closeout-discipline.md" in text


def test_closeout_discipline_is_cited_across_consumer_skills() -> None:
    target = "shared/references/closeout-discipline.md"
    consumers = {
        "release SKILL.md": ROOT / "skills" / "public" / "release" / "SKILL.md",
        "announcement SKILL.md": ROOT / "skills" / "public" / "announcement" / "SKILL.md",
        "gather SKILL.md": ROOT / "skills" / "public" / "gather" / "SKILL.md",
        "narrative SKILL.md": ROOT / "skills" / "public" / "narrative" / "SKILL.md",
        "handoff SKILL.md": ROOT / "skills" / "public" / "handoff" / "SKILL.md",
    }
    missing = [name for name, path in consumers.items() if target not in path.read_text(encoding="utf-8")]

    assert not missing, f"consumers missing closeout-discipline cite: {missing}"


def test_release_skill_anchors_verified_ledger_and_target_durability() -> None:
    text = (ROOT / "skills" / "public" / "release" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "verified release ledger" in normalized
    assert "target_unavailable" in normalized


def test_announcement_skill_anchors_external_source_identity() -> None:
    text = (ROOT / "skills" / "public" / "announcement" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "verified delivery ledger" in normalized
    assert "external-source identity" in normalized


def test_gather_skill_anchors_verified_ledger_and_target_durability() -> None:
    text = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "verified gathered-asset ledger" in normalized
    assert "reuse the resolved source" in normalized


def test_narrative_skill_anchors_external_source_identity() -> None:
    text = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "external originating context" in normalized
    assert "canonical source identity" in normalized


def test_handoff_skill_anchors_external_source_identity() -> None:
    text = (ROOT / "skills" / "public" / "handoff" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "external originating context" in normalized
    assert "canonical source identity" in normalized
