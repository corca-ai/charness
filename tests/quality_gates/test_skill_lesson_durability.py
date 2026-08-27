"""Durability guards for high-leverage lessons propagated into skill reference
docs: each case asserts a specific learned rule still lives in the doc that owns
it, so a future edit cannot silently drop the lesson. The guards check the
abstract lesson (its heading and rule sentence), not illustrative example tokens,
which are free to change.

The lessons that read a whole doc and assert plain substrings share one shape, so
they are a declarative `LESSON_GUARDS` table (batch C prose-pin fold). The two
lessons with distinct scoping logic (section-scoped, raw+normalized) stay their
own named functions below. Obsolete Prove output vocabulary is intentionally not
pinned here."""

from __future__ import annotations

import pytest

from .support import ROOT

# (id, relpath under skills/, required substrings). Each case reads the whole doc
# and asserts every substring is present. Same-file lessons stay separate rows so
# each remains its own collected item with a descriptive failure id.
LESSON_GUARDS = [
    (
        "announcement-draft-shape-release-note-digest-density",
        "public/announcement/references/draft-shape.md",
        (
            "Release-Note Digest Density",
            "2-4 actionable items",
            "who cares",
            "source links",
            "thread",
            "unfurls",
        ),
    ),
    (
        "announcement-draft-shape-public-body-shape-reframing",
        "public/announcement/references/draft-shape.md",
        (
            "Public Body Shape",
            "public_body_shape",
            "chat_update",
            "reader-visible outcomes",
            "coverage hints",
            "proof vocabulary",
        ),
    ),
    (
        "announcement-draft-shape-affordance-and-alias-rewrite",
        "public/announcement/references/draft-shape.md",
        (
            "Affordance Rewrite Pass",
            "non-maintainer",
            "reader-visible affordances",
            "canonical behavior first",
        ),
    ),
    (
        "gather-source-priority-official-url-before-websearch",
        "public/gather/references/source-priority.md",
        (
            "Official URL Before WebSearch",
            "canonical source is identifiable",
            "WebSearch",
            "derivative summaries",
        ),
    ),
    (
        "create-skill-packaging-downstream-materialization-drift",
        "public/create-skill/references/deployable-skill-packaging.md",
        (
            "Downstream Materialization",
            "upstream-owned",
            "drift marker",
            "offline-unchanged",
        ),
    ),
]


@pytest.mark.parametrize(
    "relpath, substrings",
    [pytest.param(relpath, substrings, id=case_id) for case_id, relpath, substrings in LESSON_GUARDS],
)
def test_skill_lesson_is_durable(relpath: str, substrings: tuple[str, ...]) -> None:
    text = (ROOT / "skills" / relpath).read_text(encoding="utf-8")
    for substring in substrings:
        assert substring in text, f"missing {substring!r} in {relpath}"


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
