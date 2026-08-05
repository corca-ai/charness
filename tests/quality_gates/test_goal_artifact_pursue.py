from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _goal_text(tmp_path: Path, slug: str = "g", date: str = "2026-05-27") -> str:
    path = gal.goal_path(tmp_path, date, slug)
    return path.read_text(encoding="utf-8")


def _with_required_sections(body: str) -> str:
    """Append every required/portability heading the fixture omits.

    Section presence is part of the pursue-readiness verdict, but these fixtures
    each isolate a DIFFERENT dimension (placeholder marker, discussion gate,
    draft frame, fence masking) and were written when it was not. Empty headings
    keep each one testing its own dimension rather than incidentally failing the
    completeness check -- the alternative, asserting `pursue_ready is False` in
    all of them, would stop proving anything about the dimension named in the test.
    """
    present = {match.group(1).strip() for match in gal._H2.finditer(gal._mask_fences(body))}
    missing = [
        section
        for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS + gal.CLOSEOUT_PLAN_SECTIONS
        if section not in present
    ]
    chunks: list[str] = []
    for section in missing:
        chunks.append(f"\n## {section}\n")
        if section in gal.CLOSEOUT_PLAN_SECTIONS:
            chunks.append("".join(f"- {field} fixture value\n" for field in gal.CLOSEOUT_PLAN_FIELDS))
    return body + "".join(chunks)


def test_pursue_readiness_flags_unshaped_auto_draft() -> None:
    """#247: a goal still carrying the Before-phase placeholder marker is unshaped,
    so `/goal` must fail-fast (route to `/achieve`) instead of pursuing it."""
    unshaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\n*To be filled by the achieve Before-phase interview.*\n\n"
        "## Agent Verification Plan\n\n*To be filled by the achieve Before-phase interview.*\n"
    )
    report = gal.pursue_readiness(unshaped)
    assert report["pursue_ready"] is False
    assert report["placeholder_count"] >= 1
    assert "/achieve" in report["reason"]


def test_pursue_readiness_passes_when_shaped() -> None:
    """A shaped goal (no Before-phase placeholder marker) is safe to pursue."""
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n\n"
        "## Agent Verification Plan\n\nRun the suite; assert Z.\n"
    )
    report = gal.pursue_readiness(_with_required_sections(shaped))
    assert report["pursue_ready"] is True
    assert report["placeholder_count"] == 0
    assert report["discussion_required"] is False


def test_pursue_readiness_requires_closeout_binding_plan_for_draft() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n"
        + "".join(f"\n## {section}\n" for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS)
    )

    report = gal.pursue_readiness(shaped)

    assert report["pursue_ready"] is False
    assert report["missing_sections"] == list(gal.CLOSEOUT_PLAN_SECTIONS)
    assert "Closeout Binding Plan" in report["reason"]


def test_pursue_readiness_requires_minimum_closeout_binding_fields() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n"
        + "".join(f"\n## {section}\n" for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS)
        + "\n## Closeout Binding Plan\n- Reviewed inputs: fixture\n"
    )

    report = gal.pursue_readiness(shaped)

    assert report["pursue_ready"] is False
    assert report["closeout_plan_missing_fields"] == [
        "Frozen target:",
        "Fresh-eye:",
        "Verification lock:",
        "Complete flip:",
    ]
    assert "minimum plan fields" in report["reason"]


def test_pursue_readiness_rejects_duplicate_closeout_binding_plans() -> None:
    shaped = _with_required_sections(
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n"
    ) + "\n## Closeout Binding Plan\n" + "".join(
        f"- {field} second value\n" for field in gal.CLOSEOUT_PLAN_FIELDS
    )

    report = gal.pursue_readiness(shaped)

    assert report["pursue_ready"] is False
    assert report["closeout_plan_duplicate"] is True
    assert "more than once" in report["reason"]


def test_pursue_readiness_rejects_markdown_only_closeout_values() -> None:
    shaped = _with_required_sections(
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n"
    ).replace("- Reviewed inputs: fixture value", "- Reviewed inputs: **")

    report = gal.pursue_readiness(shaped)

    assert report["pursue_ready"] is False
    assert "Reviewed inputs:" in report["closeout_plan_missing_fields"]


def test_pursue_readiness_accepts_emphasized_closeout_labels() -> None:
    shaped = _with_required_sections(
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n"
    ).replace("- Reviewed inputs:", "- **Reviewed inputs:**")

    report = gal.pursue_readiness(shaped)

    assert report["pursue_ready"] is True


@pytest.mark.parametrize("status", ["active", "blocked", "complete"])
def test_pursue_readiness_keeps_legacy_non_draft_artifacts_heading_compatible(status: str) -> None:
    legacy = (
        f"# Achieve Goal: T\n\nStatus: {status}\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n"
        + "".join(f"\n## {section}\n" for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS)
    )

    report = gal.pursue_readiness(legacy)

    assert report["pursue_ready"] is True
    assert report["missing_sections"] == []


def test_pursue_readiness_warns_on_generic_draft_frame() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Active Operating Frame\n\n"
        "- Current slice: before activation.\n"
        "- Next action: activate with `/goal @x.md`.\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n\n"
        "## Agent Verification Plan\n\nRun the suite; assert Z.\n"
    )

    report = gal.pursue_readiness(_with_required_sections(shaped))

    assert report["pursue_ready"] is True
    assert report["draft_frame_disposition_present"] is False
    assert "lacks lifecycle disposition" in report["draft_frame_warning"]


def test_pursue_readiness_accepts_scaffolded_draft_frame(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    text = _goal_text(tmp_path)

    report = gal.pursue_readiness(text)

    assert report["draft_frame_disposition_present"] is True
    assert report["draft_frame_warning"] == ""


def test_pursue_readiness_blocks_hidden_consequential_decisions() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Boundaries\n\n#184 must close inside this bundled goal.\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse real GitHub lookup proof, not fixture-only proof.\n\n"
        "## Interview Decisions\n\nProduction contact is allowed, including apply/restart.\n\n"
        "## Plan Critique Findings\n\nNo blockers.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["placeholder_count"] == 0
    assert report["discussion_required"] is True
    assert "issue_close_or_split" in report["discussion_triggers"]
    assert "operator discussion required" in report["reason"]


@pytest.mark.parametrize(
    ("body", "trigger"),
    [
        ("## Agent Verification Plan\n\n### External Or Live Proof\n\nUse live proof in production.\n", "production_or_live_proof"),
        ("## Boundaries\n\nResolve #275 and #276 together.\n", "broad_bundle_scope"),
        ("## Boundaries\n\nComplete all four proposed changes.\n", "broad_bundle_scope"),
        ("## Agent Verification Plan\n\nProof non-claim: live proof not run.\n", "proof_nonclaim_or_downgrade"),
        ("## Interview Decisions\n\nIrreversible side effects are allowed.\n", "irreversible_side_effect"),
        ("## Non-Goals\n\nDo not close #276 until push and remote verification.\n", "issue_close_or_split"),
    ],
)
def test_pursue_readiness_discussion_trigger_families(body: str, trigger: str) -> None:
    report = gal.pursue_readiness(
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n" + body
    )
    assert report["pursue_ready"] is False
    assert trigger in report["discussion_triggers"]


def test_discussion_deploy_vocab_is_adapter_provided_with_english_default() -> None:
    # WS-3b b-ii migration proof: the deploy/irreversible vocab is adapter-provided,
    # with a behavior-preserving English default (no adapter -> byte-identical).
    header = "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
    deploy_body = "## Boundaries\n\nWe will deploy and apply/restart the instance.\n"
    # default (no adapter vocab): English deploy verbs still trigger (guard preserved)
    default = gal.pursue_readiness(header + deploy_body)
    assert "production_or_live_proof" in default["discussion_triggers"]
    assert "irreversible_side_effect" in default["discussion_triggers"]
    # a consumer's vocab REPLACES the default: its own verb triggers...
    rollout_body = "## Boundaries\n\nWe will rollout the change to the fleet.\n"
    rolled = gal.pursue_readiness(header + rollout_body, deploy_vocab=["rollout"])
    assert "production_or_live_proof" in rolled["discussion_triggers"]
    # ...and the English default deploy verb no longer triggers under that vocab
    # (the neutral concepts like `prod`/`irreversible` are unaffected and still fire)
    no_deploy = gal.pursue_readiness(header + deploy_body, deploy_vocab=["rollout"])
    assert "production_or_live_proof" not in no_deploy["discussion_triggers"]
    assert "irreversible_side_effect" not in no_deploy["discussion_triggers"]


def test_pursue_readiness_does_not_treat_empty_discussion_label_as_summary() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "Discuss before activation:\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse live proof.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_does_not_treat_empty_discussion_heading_as_summary() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Agent Verification Plan\n\n"
        "### Discuss before activation\n\n"
        "### External Or Live Proof\n\nUse live proof.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_ignores_stale_discussion_summary_in_slice_log() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Non-Goals\n\nDo not close #276 until push.\n\n"
        "## Slice Log\n\nDiscuss before activation: close #100 was already discussed.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_does_not_trigger_on_critique_not_yet_run() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Plan Critique Findings\n\nNot yet run. First active slice should run critique.\n"
    )
    report = gal.pursue_readiness(_with_required_sections(shaped))
    assert report["pursue_ready"] is True
    assert report["discussion_required"] is False


def test_pursue_readiness_blocks_surfaced_but_unresolved_decisions() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Boundaries\n\n#184 must close inside this bundled goal.\n\n"
        "Discuss before activation: close #184 in-goal; production contact is allowed with recorded target, preflight, stop condition, and post-proof.\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse real GitHub lookup proof.\n\n"
        "## Interview Decisions\n\nProduction contact is allowed, including apply/restart.\n\n"
        "## Plan Critique Findings\n\nNo blockers.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["shape_ready"] is True
    assert report["activation_ready"] is False
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is True
    assert report["discussion_resolved"] is False
    assert "unresolved" in report["activation_discussion_warning"]
    assert "not marked resolved" in report["reason"]


def test_pursue_readiness_blocks_summary_that_is_not_discussion_resolution() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Non-Goals\n\nDo not close #279 until proof-bearing commit lands.\n\n"
        "Discuss before activation: confirm issue closeout timing before activation.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["activation_ready"] is False
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is True
    assert report["discussion_resolved"] is False
    assert "Resolve or explicitly ask" in report["activation_discussion_warning"]
    assert "discussion_summary_present" not in report["reason"]
    assert "unresolved" in report["reason"]


def test_pursue_readiness_blocks_summary_starting_with_issue_number_without_resolution_marker() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Non-Goals\n\nDo not close #276 until push.\n\n"
        "Discuss before activation: #276 remains local-only until push verifies closure.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is True
    assert report["discussion_resolved"] is False


def test_pursue_readiness_allows_explicitly_resolved_consequential_decisions() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Boundaries\n\n#184 must close inside this bundled goal.\n\n"
        "Discuss before activation: RESOLVED in-thread. Close #184 in-goal; production contact is allowed with recorded target, preflight, stop condition, and post-proof.\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse real GitHub lookup proof.\n\n"
        "## Interview Decisions\n\nProduction contact is allowed, including apply/restart.\n\n"
    )
    report = gal.pursue_readiness(_with_required_sections(shaped))
    assert report["pursue_ready"] is True
    assert report["activation_ready"] is True
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is True
    assert report["discussion_resolved"] is True
    assert report["activation_discussion_warning"] == ""


def test_pursue_readiness_rejects_na_summary_when_decisions_are_consequential() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "Discuss before activation: n/a -- no discussion needed.\n\n"
        "## Interview Decisions\n\n#220 will use fixture-only proof.\n\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_ignores_marker_inside_code_fence() -> None:
    """A marker quoted inside a fenced block must not trip the detector (fences
    are masked), so a documentation example cannot force a false unshaped verdict."""
    fenced = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X.\n\n```\n"
        "To be filled by the achieve Before-phase interview.\n```\n"
    )
    assert gal.pursue_readiness(_with_required_sections(fenced))["pursue_ready"] is True


def test_pursue_readiness_refuses_an_artifact_whose_sections_were_never_written() -> None:
    """The live #490 instance: a goal artifact reached `/goal` with nine required
    sections absent and `--pursue-ready` called it `safe to pursue`, because an
    artifact whose sections were never WRITTEN carries no placeholder marker
    either — so marker-absence was read as shaping-presence."""
    gutted = (
        "# Achieve Goal: anything\n\nStatus: draft\nActivation: `/goal @x.md`\n"
    )

    report = gal.pursue_readiness(gutted)

    assert report["pursue_ready"] is False
    assert report["placeholder_count"] == 0  # the old signal is silent here
    assert report["shape_ready"] is True  # ...and still reports its own narrow fact
    assert report["sections_complete"] is False
    assert "Boundaries" in report["missing_sections"]
    assert "Slice Plan" in report["missing_sections"]
    assert "incomplete:" in report["reason"]
    assert "/achieve" in report["reason"]
    assert "safe to pursue" not in report["reason"]


def test_pursue_readiness_control_the_same_artifact_with_its_headings_passes() -> None:
    """False-refusal guard for the section floor: the ONLY difference from the
    refused fixture above is the headings, and it must pass — otherwise the new
    rule is refusing on something else and the test above proves nothing."""
    gutted = "# Achieve Goal: anything\n\nStatus: draft\nActivation: `/goal @x.md`\n"

    report = gal.pursue_readiness(_with_required_sections(gutted))

    assert report["pursue_ready"] is True
    assert report["sections_complete"] is True
    assert report["missing_sections"] == []


def test_pursue_readiness_refuses_when_an_unclosed_fence_makes_the_reading_open() -> None:
    """Round-1 bounded review: `mask_fences` FAILS OPEN on odd fence parity and
    returns the raw text, so an artifact with every heading inside one unclosed
    fence — and no real sections at all — would read `sections_complete: true`.
    `check_goal` already refuses an unbalanced document; this gate must too, or
    the section floor is one stray fence marker away from the class it closes."""
    fenced_away = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n```md\n"
        + "".join(
            f"## {section}\n"
            for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS + gal.CLOSEOUT_PLAN_SECTIONS
        )
    )  # the fence is never closed

    report = gal.pursue_readiness(fenced_away)

    assert report["pursue_ready"] is False
    assert report["fences_balanced"] is False
    assert report["sections_reading_established"] is False
    assert "unreadable:" in report["reason"]
    assert "safe to pursue" not in report["reason"]


def test_pursue_readiness_control_a_balanced_fence_is_still_readable() -> None:
    """False-refusal guard for the fence clause: a goal carrying an ordinary
    CLOSED fenced example is unaffected."""
    report = gal.pursue_readiness(
        _with_required_sections(
            "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
            "```md\n## Not A Real Heading\n```\n"
        )
    )

    assert report["pursue_ready"] is True
    assert report["fences_balanced"] is True
    assert report["sections_reading_established"] is True


def test_pursue_readiness_pass_message_states_the_scope_it_measured() -> None:
    """The refusal path was made honest first; the PASS sentence is the one an
    operator acts on, and it used to name only the marker fact while standing in
    for a verdict covering markers, headings, fences, and discussion."""
    reason = gal.pursue_readiness(
        _with_required_sections(
            "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n"
        )
    )["reason"]

    assert "safe to pursue" in reason  # legacy substring preserved for matchers
    assert "heading is present" in reason
    assert "section content not checked" in reason


def test_pursue_readiness_states_what_its_verdict_did_not_measure() -> None:
    """A narrow verdict carries its own scope, so a caller reads what was NOT
    established from the answer rather than from the flag's help text."""
    report = gal.pursue_readiness(
        _with_required_sections(
            "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n"
        )
    )

    assert report["pursue_ready"] is True
    assert "status validity" in report["scope_not_checked"]
    assert any("section CONTENT" in entry for entry in report["scope_not_checked"])


def test_pursue_readiness_reason_names_every_refusal_not_only_the_first() -> None:
    """A goal that is BOTH unshaped and missing sections reports both, so fixing
    the named one does not surface the other on a second `/goal` attempt."""
    both = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Goal\n\n*To be filled by the achieve Before-phase interview.*\n"
    )

    reason = gal.pursue_readiness(both)["reason"]

    assert "unshaped:" in reason
    assert "incomplete:" in reason
