from __future__ import annotations

import re

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


_NEGATED_OBLIGATION = re.compile(
    r"\b(?:does not|do not|never|no longer|is not|are not)\s+(?:\w+\s+){0,3}"
    r"(?:owe|owes|run|runs|require|required|need|needs)\b"
)


def _section_block(text: str, heading: str, surface: str) -> str:
    """The body of one `## <heading>` section, joined into a single string.

    Section-shaped rather than bullet-shaped because the vendored reference states the
    rule as prose paragraphs, not as a `- ` bullet. Fenced regions are dropped for the
    same reason `_bullet_blocks` drops them: a quoted example must not read as a second
    declaration of the rule.
    """
    body: list[str] | None = None
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            if body is not None:
                break
            if line[3:].strip() == heading:
                body = []
            continue
        if body is not None:
            body.append(line)
    assert body is not None, f"{surface} has no `## {heading}` section"
    joined = " ".join(part.strip() for part in body if part.strip())
    assert joined, f"{surface} has an empty `## {heading}` section"
    return joined


def test_two_round_rule_is_pinned_on_the_vendored_reference() -> None:
    """The vendored copy of the two-round rule carries the same actionable clauses as the
    authoring-repo copies, and stays portable while doing so.

    The two authoring-repo surfaces are pinned below, and the vendored reference was not:
    the critique that introduced the rule recorded that a fourth copy drifted to the
    touched-the-file trigger, the "scoped to the repairs" phrasing, and an unconditional
    two-round count precisely because no test could see it. This is the missing pin.

    The portability half is a separate assertion on purpose. This reference ships to
    consuming repos, so its copy must NOT name the authoring repo's contract as the
    reader's owning surface — it must say the consuming repo owns its own trigger
    definition. Pinning the clauses without pinning that would lock in a rule that reads
    as an instruction to obey a document the consuming repo does not have.
    """
    surface = "skills/shared/references/fresh-eye-subagent-review.md"
    text = (ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md").read_text(
        encoding="utf-8"
    )
    section = _section_block(text, "Two Rounds For Verdict-Rendering Code", surface)
    lowered = section.lower()

    # The obligation, and the clauses without which it is unaffordable or vacuous —
    # the same clause set the authoring-repo copies are held to.
    assert "second bounded round" in lowered or "second bounded review" in lowered, (
        f"{surface} states no second-round obligation"
    )
    assert "proof surface" in lowered, f"{surface} does not scope the trigger to proof surfaces"
    assert "repaired surface" in lowered, f"{surface} does not say round 2 reads the repaired surface"
    assert "not that its file" in lowered or "not the file" in lowered, (
        f"{surface} does not exclude a touched-the-file trigger"
    )
    assert "discharge" in lowered, f"{surface} does not state the zero-repair discharge"
    assert "cap is two" in lowered, f"{surface} does not state the two-round cap"
    negated = _NEGATED_OBLIGATION.search(lowered)
    assert not negated, f"{surface} states the obligation negatively: {negated.group(0)!r}"

    # The portability call: the vendored copy hands trigger ownership to the adopting
    # repo instead of pointing at an authoring-repo path the consumer cannot open.
    assert "consuming repo" in lowered and "own trigger definition" in lowered, (
        f"{surface} does not hand trigger ownership to the consuming repo"
    )
    assert "authoring-repo-internal" in lowered, (
        f"{surface} cites the authoring repo's contract without marking it as internal"
    )
