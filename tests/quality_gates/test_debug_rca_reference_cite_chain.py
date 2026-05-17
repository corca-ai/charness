from __future__ import annotations

import re

from .support import ROOT

REFERENCE_PATH = ROOT / "skills" / "public" / "debug" / "references" / "five-whys-causal-chain.md"
SIBLING_SEARCH = ROOT / "skills" / "public" / "debug" / "references" / "sibling-search.md"
DEBUG_SKILL = ROOT / "skills" / "public" / "debug" / "SKILL.md"
CAUSAL_REVIEW = ROOT / "skills" / "public" / "issue" / "references" / "causal-review.md"
ISSUE_SKILL = ROOT / "skills" / "public" / "issue" / "SKILL.md"

SIBLING_DECISIONS = (
    "same bug, fix now",
    "same class, diagnostic-only for this slice",
    "intentional plain-text or non-rendering boundary",
    "valid follow-up outside the slice",
)
PROOF_LEVELS = (
    "static scan only",
    "local payload proof",
    "runtime/provider roundtrip",
    "not inspected",
)


def test_debug_rca_reference_file_exists() -> None:
    assert REFERENCE_PATH.is_file(), f"missing reference: {REFERENCE_PATH}"


def test_debug_skill_cites_five_whys_causal_chain() -> None:
    text = DEBUG_SKILL.read_text(encoding="utf-8")
    assert "five-whys-causal-chain" in text, "debug/SKILL.md must cite five-whys-causal-chain reference"


def test_causal_review_cites_five_whys_causal_chain() -> None:
    text = CAUSAL_REVIEW.read_text(encoding="utf-8")
    assert "five-whys-causal-chain" in text, "causal-review.md Lens 1 must cite five-whys-causal-chain substrate"


def test_issue_skill_step_4_dispatches_to_debug_substrate() -> None:
    text = ISSUE_SKILL.read_text(encoding="utf-8")
    pattern = re.compile(r"consume.*debug.*substrate|debug.*RCA.*reference", re.IGNORECASE | re.DOTALL)
    assert pattern.search(text), "issue/SKILL.md step 4 must dispatch to debug substrate"


def test_debug_skill_marks_standalone_callable() -> None:
    text = DEBUG_SKILL.read_text(encoding="utf-8")
    pattern = re.compile(r"callable directly|without GitHub issue|standalone", re.IGNORECASE)
    assert pattern.search(text), "debug/SKILL.md must mark itself as standalone-callable"


def test_issue_skill_close_comment_has_debug_artifact_slot() -> None:
    text = ISSUE_SKILL.read_text(encoding="utf-8")
    assert "Debug artifact:" in text, "issue/SKILL.md close-comment shape must have `Debug artifact:` slot"


def test_causal_review_does_not_re_derive_rca_body() -> None:
    text = CAUSAL_REVIEW.read_text(encoding="utf-8")
    forbidden = re.compile(
        r"Common bottoms that count|race condition.*synchronization|edge case.*classifier",
        re.IGNORECASE | re.DOTALL,
    )
    assert not forbidden.search(text), (
        "causal-review.md must not re-derive the RCA body; "
        "Lens 1 should dispatch to debug substrate only"
    )


def test_causal_review_lens_1_stays_dispatch_only() -> None:
    text = CAUSAL_REVIEW.read_text(encoding="utf-8")
    match = re.search(r"### Lens 1[^\n]*\n(.*?)\n### Lens 2", text, re.DOTALL)
    assert match, "could not locate Lens 1 section between headings"
    body = match.group(1).strip("\n")
    line_count = body.count("\n") + 1
    assert line_count <= 15, (
        f"Lens 1 body grew to {line_count} lines; dispatch paragraph should "
        "stay ≤15 lines (regrowth indicates RCA re-derivation drift)"
    )


def test_causal_review_subagent_prompt_must_include_substrate_cite() -> None:
    text = CAUSAL_REVIEW.read_text(encoding="utf-8")
    contract_match = re.search(
        r"The subagent's prompt must:(.*?)(?=\n###|\Z)",
        text,
        re.DOTALL,
    )
    assert contract_match, "could not locate subagent prompt contract block"
    contract = contract_match.group(1)
    assert "five-whys-causal-chain" in contract, (
        "subagent prompt contract must require including the substrate cite "
        "so the spawned reviewer triages instead of regrowing the chain"
    )


def test_debug_sibling_search_requires_decision_taxonomy_and_proof_levels() -> None:
    text = SIBLING_SEARCH.read_text(encoding="utf-8")
    for decision in SIBLING_DECISIONS:
        assert decision in text, f"sibling-search.md must preserve decision label `{decision}`"
    for proof_level in PROOF_LEVELS:
        assert proof_level in text, f"sibling-search.md must preserve proof level `{proof_level}`"
    assert "proof level separate from the decision" in text
    assert "provider roundtrip" in text


def test_debug_workflow_invokes_classified_sibling_scan() -> None:
    text = DEBUG_SKILL.read_text(encoding="utf-8")
    assert "classify each sibling decision" in text
    assert "proof level separately from the decision" in text
    assert "wrong mental model" in text


def test_causal_review_preserves_sibling_decisions_and_proof_levels() -> None:
    text = CAUSAL_REVIEW.read_text(encoding="utf-8")
    lens_match = re.search(r"### Lens 3[^\n]*\n(.*?)\n### Output shape", text, re.DOTALL)
    assert lens_match, "could not locate Lens 3 body"
    lens_body = lens_match.group(1)
    for decision in SIBLING_DECISIONS:
        assert decision in lens_body, f"causal-review Lens 3 must preserve `{decision}`"
    for proof_level in PROOF_LEVELS:
        assert proof_level in lens_body, f"causal-review Lens 3 must preserve `{proof_level}`"
    assert "omits sibling classification" in lens_body
    assert "merges proof level into the decision" in lens_body
