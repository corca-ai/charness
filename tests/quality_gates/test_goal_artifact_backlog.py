"""The backlog-recount floor: a goal must record what it claims and what it does not.

The defect this closes is that `--pursue-ready` -- the surface deciding a goal may
activate -- validated headings, placeholders and closeout-plan fields, so a goal whose
scope contradicted the tracker passed it cleanly. The floor cannot catch what the
contract never asks for.

Two properties carry the design and both are pinned here rather than argued in prose.
PRESENCE-ONLY: the floor never grades WHICH issues a goal claims, because that judgement
is the operator's and a floor grading it would be a new false-verdict surface inside the
tool built to stop them. GRANDFATHERED BY THE GOAL'S OWN `Created:` DATE, failing CLOSED
on a missing or malformed one: nineteen historical artifacts predate the rule, and a
floor that reddens the whole corpus is a floor that gets disarmed rather than obeyed.
"""
from __future__ import annotations

import importlib.util
import sys

from .support import ROOT

# Loaded by its quoted PATH, like every sibling floor test. A bare
# `import goal_artifact_backlog` after a `sys.path` insert works at runtime but is
# invisible to `suggest_mutation_coverage_command`, whose reference mapper looks for the
# quoted path, the dotted module, or the stem as a call argument. That is not cosmetic:
# the changed-line mutation gate selects its focused pytest targets from that mapping, so
# an unmappable import left this floor's own tests out of the selected set and its lines
# reported as UNCOVERED while they were in fact exercised.
_BACKLOG_PATH = ROOT / "skills/public/achieve/scripts/goal_artifact_backlog.py"
sys.path.insert(0, str(ROOT / "skills/public/achieve/scripts"))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


backlog = _load(_BACKLOG_PATH, "goal_artifact_backlog")

PRE_RULE = "Status: draft\nCreated: 2026-08-07\n\n## Goal\n\nsomething\n"
IN_SCOPE = "Status: draft\nCreated: 2026-08-08\n\n## Goal\n\nsomething\n"
FILLED = IN_SCOPE + (
    "\n## Backlog Recount\n\n"
    "- Counted: 28 open issues on 2026-08-08\n"
    "- Claims: #530, #554\n"
    "- Not claimed: #519 — different question\n"
)


def test_a_pre_rule_goal_is_grandfathered_and_says_so() -> None:
    """The report must not read as a satisfied floor.

    A bare `{"applies": False, "ok": True}` is the exact look-alike this goal family
    exists to remove: it renders as a pass to anyone scanning `ok`. The shared grammar's
    disclosing helper states that the floor was NOT EVALUATED and why.
    """
    report = backlog.check(PRE_RULE)

    assert report["applies"] is False
    assert report["ok"] is True
    assert report["evaluated"] is False
    assert "grandfathered off (not satisfied)" in report["reason"]


def test_a_missing_created_date_fails_closed() -> None:
    """An artifact with no parseable `Created:` is COVERED, not exempt.

    Failing open here would make the floor removable by deleting one line -- a gate whose
    bypass is easier than its compliance.
    """
    assert backlog.applies("Status: draft\n\n## Goal\n\nno created line\n") is True
    assert backlog.applies("Status: draft\nCreated: not-a-date\n") is True


def test_an_in_scope_goal_without_the_section_is_refused() -> None:
    report = backlog.check(IN_SCOPE)

    assert report["ok"] is False
    assert report["missing_fields"] == list(backlog.REQUIRED_FIELDS)
    assert "recount the tracker" in report["reason"]


def test_a_filled_section_passes() -> None:
    report = backlog.check(FILLED)

    assert report["ok"] is True
    assert report["missing_fields"] == []


def test_an_empty_field_value_is_refused_exactly_like_an_absent_one() -> None:
    """The look-alike case, which is the whole reason the floor exists.

    `Claims:` with nothing after it tells a reader precisely as much as no line at all,
    while LOOKING like the section was filled in. If the floor accepted it, satisfying
    the floor would be easier than doing the work it asks for.
    """
    empty = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims:\n- Not claimed: none\n"
    report = backlog.check(empty)

    assert report["ok"] is False
    assert report["missing_fields"] == ["Claims"]


def test_none_is_an_acceptable_answer_but_must_be_written() -> None:
    """A goal may genuinely claim nothing tracked. The floor is presence, not volume."""
    nothing = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 0 open issues\n- Claims: none\n- Not claimed: none\n"

    assert backlog.check(nothing)["ok"] is True


def test_the_floor_never_grades_which_issues_were_claimed() -> None:
    """PRESENCE-ONLY, pinned as a property rather than trusted to the docstring.

    Two goals with contradictory claim splits over the same tracker both pass. That is
    correct and deliberate: the floor makes the reasoning visible so a human or reviewer
    can grade it, and a floor that tried to decide "should this goal have claimed that
    one" would be asserting a verdict nothing can establish from the artifact.
    """
    one = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims: #530\n- Not claimed: #554\n"
    other = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims: #554\n- Not claimed: #530\n"

    assert backlog.check(one)["ok"] is True
    assert backlog.check(other)["ok"] is True


def test_the_shipped_template_carries_the_section_and_its_placeholders() -> None:
    """A floor the scaffold cannot satisfy is a floor every new goal trips blind."""
    template = (ROOT / "skills/public/achieve/scripts/goal_artifact_template.md").read_text(encoding="utf-8")

    assert f"## {backlog.SECTION}" in template
    for field in backlog.REQUIRED_FIELDS:
        assert f"- {field}: To be filled by the achieve Before-phase" in template, field


def test_this_repos_own_active_goal_satisfies_the_floor_it_ships() -> None:
    """Dogfood, and the reason the rule date is what it is.

    The goal that introduced this floor is deliberately IN SCOPE of it. A rule whose
    author's own artifact escapes it is a rule nobody has run, and the floor's first real
    use is what caught this goal's shaping count (25) already disagreeing with the live
    tracker (28).
    """
    goal = ROOT / "charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md"
    text = goal.read_text(encoding="utf-8")

    assert backlog.applies(text) is True, "the rule date must cover the goal that ships the rule"
    assert backlog.check(text)["ok"] is True


def test_the_floor_actually_gates_activation_not_just_reports() -> None:
    """The WIRING, not the helper — and this is the second time in one session.

    A mutation removing `and not backlog_recount_missing_fields` from
    `pursue_readiness`'s `activation_ready` conjunction passed every other test in this
    file and in the pursue suite: `check()` still returned the right verdict, the payload
    still carried the missing fields, and nothing noticed that `/goal` would activate the
    goal anyway. A floor that reports but does not refuse is exactly the false green this
    goal family exists to remove, so the refusal is asserted through the composed verdict
    rather than through the module that computes it.

    Slice 1 of this goal shipped the identical shape (a scope helper proven correct while
    its call site was reverted), which is why this test exists at all.
    """
    import goal_artifact_lib as gal  # noqa: PLC0415

    draft = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n"
        + "".join(
            f"\n## {section}\n"
            for section in gal.REQUIRED_SECTIONS + gal.PORTABILITY_SECTIONS
        )
        + "\n## Closeout Binding Plan\n"
        + "".join(f"- {field} fixture value\n" for field in gal.CLOSEOUT_PLAN_FIELDS)
    )

    without = gal.pursue_readiness(draft)
    assert without["pursue_ready"] is False, "a draft with no backlog recount must not activate"
    assert without["backlog_recount_missing_fields"] == list(backlog.REQUIRED_FIELDS)
    assert "backlog recount" in without["reason"]

    # Control: the ONLY difference is the section, so the refusal above is attributable to
    # this floor rather than to some other unmet condition in the same fixture.
    with_section = gal.pursue_readiness(
        draft + "\n## Backlog Recount\n- Counted: 28\n- Claims: none\n- Not claimed: none\n"
    )
    assert with_section["pursue_ready"] is True, with_section["reason"]


def test_a_punctuation_only_value_is_refused() -> None:
    """"Present but says nothing" is the same look-alike as empty.

    Round-1 review found `Claims: **` passing: the first cut only stripped whitespace, so
    any non-empty string counted. The closeout-plan floor in the very function that
    consumes this one had already solved it, and its solution is now reused. If this
    passed, satisfying the floor would be cheaper than reading the tracker.
    """
    noise = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: —\n- Claims: **\n- Not claimed: .\n"
    report = backlog.check(noise)

    assert report["ok"] is False
    assert report["missing_fields"] == list(backlog.REQUIRED_FIELDS)


def test_emphasised_and_alternate_bullets_are_read_not_reported_absent() -> None:
    """A visibly-present field must not be reported missing.

    `**Claims:**`, `+ ` bullets and a lower-case label are all valid markdown an operator
    will write. The first regex refused all three — failing closed, so never a false
    green, but a refusal saying "field absent" about a field plainly on the page.
    """
    emphasised = (
        IN_SCOPE
        + "\n## Backlog Recount\n\n- **Counted:** 28\n+ Claims: none\n- not claimed: none\n"
    )

    assert backlog.check(emphasised)["ok"] is True, backlog.check(emphasised)


def test_the_floor_cannot_be_disarmed_by_removing_or_mis_casing_the_status() -> None:
    """FAIL CLOSED on status, matching the `Created:` direction.

    Round-1 review found the draft gate keyed to `status == "draft"`, while `read_status`
    returns None for a missing `Status:` line and the raw string otherwise, and
    `--pursue-ready` explicitly does not validate status. So deleting one line, or writing
    `Status: Draft`, skipped the floor — and disarmed the closeout-plan floor in the same
    edit — while two shipped docstrings claimed the floor could not be removed that way.
    """
    import goal_artifact_lib as gal  # noqa: PLC0415

    base = "# Achieve Goal: T\n\n{status}Activation: `/goal @x.md`\n\n## Goal\n\nx\n"
    for status_line in ("", "Status: Draft\n", "Status: DRAFT\n", "Status: nonsense\n"):
        report = gal.pursue_readiness(base.format(status=status_line))
        assert report["backlog_recount_missing_fields"] == list(backlog.REQUIRED_FIELDS), status_line

    # The recognised non-shaping statuses still skip it — that scoping is deliberate.
    for status_line in ("Status: active\n", "Status: blocked\n", "Status: complete\n"):
        report = gal.pursue_readiness(base.format(status=status_line))
        assert report["backlog_recount_missing_fields"] == [], status_line


def test_a_section_missing_a_whole_field_line_names_only_that_field() -> None:
    """The partial-section case: heading present, one field line absent entirely.

    Distinct from the empty-value case above — there the line exists and says nothing;
    here the line is gone. The verdict must name the ONE missing field rather than
    reporting the whole section absent, or the operator re-writes a section that is
    mostly correct.
    """
    partial = IN_SCOPE + "\n## Backlog Recount\n\n- Counted: 28\n- Claims: none\n"
    report = backlog.check(partial)

    assert report["ok"] is False
    assert report["missing_fields"] == ["Not claimed"]


def test_the_sibling_loaders_name_what_they_could_not_find(monkeypatch) -> None:
    """Both floor modules fail with a NAMED diagnostic, not an AttributeError later.

    These loaders are unreachable in a well-formed tree, which is exactly why they are
    worth a test: if the export ever drops a sibling, the failure should say which file is
    missing at import time rather than surfacing as a mystery attribute error deep in a
    verdict. Driven by forcing the spec to None rather than by deleting a shipped file.
    """
    import importlib.util  # noqa: PLC0415

    import goal_artifact_pursue as pursue  # noqa: PLC0415

    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)

    for loader, expected in (
        (backlog._load_floor_grammar, "goal_artifact_floor_grammar.py"),
        (pursue._load_backlog_floor, "goal_artifact_backlog.py"),
    ):
        try:
            loader()
        except ImportError as exc:
            assert expected in str(exc), (expected, str(exc))
        else:  # pragma: no cover - the loader must not succeed with a None spec
            raise AssertionError(f"{expected} loader did not refuse a None spec")
