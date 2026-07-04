from __future__ import annotations

import pytest

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


# Each consumer SKILL.md must anchor its own closeout-discipline vocabulary
# (verified ledger + target/source-identity phrasing). Folded from one function
# per skill into a declarative (skill_id, required substrings) table; every
# asserted substring is preserved, so collection count is unchanged.
SKILL_ANCHOR_GUARDS = [
    ("release", ("verified release ledger", "target_unavailable")),
    ("announcement", ("verification-carrying ledger", "external-source identity")),
    ("gather", ("verified gathered-asset ledger", "reuse the resolved source")),
    ("narrative", ("external originating context", "canonical source identity")),
    ("handoff", ("external originating context", "canonical source identity")),
]


@pytest.mark.parametrize(
    "skill_id, substrings",
    SKILL_ANCHOR_GUARDS,
    ids=[skill_id for skill_id, _ in SKILL_ANCHOR_GUARDS],
)
def test_skill_anchors_closeout_discipline(skill_id: str, substrings: tuple[str, ...]) -> None:
    text = (ROOT / "skills" / "public" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for substring in substrings:
        assert substring in normalized, f"missing {substring!r} in {skill_id} SKILL.md"
