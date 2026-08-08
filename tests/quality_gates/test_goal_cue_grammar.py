"""Tests for the shared ``## Coordination Cues`` cue grammar.

Split from ``test_goal_coordination_floors.py`` on a real seam, not a length
spill: those tests pin each FLOOR's verdict (what is triggered, what refuses a
flip), while these pin the GRAMMAR every floor now shares — how a cue line is
recognised through inline markup, when a value is still an unreplaced template
placeholder, and the cross-floor opt-out census computed from the floors' own
verdicts. The grammar is one module (`goal_artifact_floor_grammar`) with one set
of callers, so its tests belong together.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cf = _load("goal_artifact_coordination_floors")
pr = _load("goal_artifact_phase_routing")
fg = _load("goal_artifact_floor_grammar")


def _coord(body: str):
    return cf._section_body(cf._mask_fences(body), "Coordination Cues")


# --- markup-tolerant cue grammar -------------------------------------------
# A correctly-filled cue wrapped in backticks or bold was INVISIBLE to every one
# of the five step-line matchers, so the floor refused a goal that had actually
# done the work. The matchers were clones, so the defect was identical in all
# five; they now compile through one shared `cue_pattern`.


@pytest.mark.parametrize(
    "line",
    [
        "- Routing: impl",
        "- `Routing: impl`",
        "- `Routing:` impl",
        "- **Routing:** impl",
        "- Routing: `impl`",
        "> Routing: impl",
        "-   Routing:impl",
    ],
)
def test_routing_cue_reads_through_inline_markup(line: str) -> None:
    assert pr._parse_routing_step(line, "impl") == ("ref", "impl")


@pytest.mark.parametrize(
    "ref_name",
    ["_GATHER_REF", "_RELEASE_REF", "_ISSUE_CLOSEOUT_REF", "_SUCCESSOR_GOAL_REF"],
)
def test_every_sibling_cue_reads_through_inline_markup(ref_name: str) -> None:
    """The fix is the cue GRAMMAR, not one regex: all four siblings move together."""
    label = {
        "_GATHER_REF": "Gather",
        "_RELEASE_REF": "Release",
        "_ISSUE_CLOSEOUT_REF": "Issue closeout",
        "_SUCCESSOR_GOAL_REF": "Successor goal",
    }[ref_name]
    ref_re = getattr(cf, ref_name)
    bare = _coord(f"## Coordination Cues\n\n- {label}: charness-artifacts/x.md\n")
    ticked = _coord(f"## Coordination Cues\n\n- `{label}: charness-artifacts/x.md`\n")
    bolded = _coord(f"## Coordination Cues\n\n- **{label}:** charness-artifacts/x.md\n")
    assert cf._parse_step(bare, ref_re) == ("ref", "charness-artifacts/x.md")
    assert cf._parse_step(ticked, ref_re) == ("ref", "charness-artifacts/x.md")
    assert cf._parse_step(bolded, ref_re) == ("ref", "charness-artifacts/x.md")


def test_markup_is_stripped_before_the_optout_floor_is_measured() -> None:
    """Wrapping markup must not PAD a short reason over `MIN_OPTOUT_REASON`.

    A backticked opt-out is read, but its length is measured on the reason, not
    on the reason plus the author's formatting.
    """
    short = "z" * (cf.MIN_OPTOUT_REASON - 1)
    body = _coord(f"## Coordination Cues\n\n- `Release: n/a - {short}`\n")
    kind, reason = cf._parse_step(body, cf._RELEASE_REF)
    assert kind == "optout_short"
    assert reason == short  # backticks are not reason content
    at_floor = "z" * cf.MIN_OPTOUT_REASON
    ok_body = _coord(f"## Coordination Cues\n\n- `Release: n/a - {at_floor}`\n")
    assert cf._parse_step(ok_body, cf._RELEASE_REF) == ("optout", at_floor)


@pytest.mark.parametrize(
    "value",
    [
        "<path>",
        "<reason>",
        "`<ref>`.",
        "<close-intended issue numbers>",
        # the template's OWN seeded cue form is two placeholders joined by prose;
        # an equals-the-whole-value guard let this through as a real reference
        "<path-or-ref> - <why none was designed>",
        # `joined_section_body` folds a continuation line into the value, so the
        # placeholder stops being the whole value while staying just as unfilled
        "<ref> (still deciding which gather artifact to point at)",
    ],
)
def test_unreplaced_placeholder_never_satisfies_a_cue(value: str) -> None:
    """Markup tolerance is only safe because the inert-value guard backs it.

    Widening the prefix exposed every seeded documentation example that starts a
    physical line. Anchoring cannot tell a seed from a filled cue; an unreplaced
    `<...>` can, and it reports as "no step line" rather than a near-miss. The
    guard is CONTAINS, not EQUALS -- both shapes above walked through an
    equals-the-whole-value check.
    """
    body = _coord(f"## Coordination Cues\n\n- `Gather: {value}`\n")
    assert cf._parse_step(body, cf._GATHER_REF) == (None, None)
    # A left-in placeholder is the SAME fact on both sides of the opt-out
    # grammar: the author never filled this cue in. Not a near-miss, not a line.
    na = _coord(f"## Coordination Cues\n\n- `Gather: n/a - {value}`\n")
    assert cf._parse_step(na, cf._GATHER_REF) == (None, None)


@pytest.mark.parametrize(
    "line",
    ["- `Successor goal:`", "- **Successor goal:**", '- "Successor goal:"'],
)
def test_a_cue_label_with_no_value_never_satisfies(line: str) -> None:
    """`strip_cue_markup` peels `` `Successor goal:` `` down to `""`, which fell
    through to `("ref", "")` and DISCHARGED the one floor that fires at every
    completion -- a label with no value at all satisfying a closeout obligation."""
    body = _coord(f"## Coordination Cues\n\n{line}\n")
    assert cf._parse_step(body, cf._SUCCESSOR_GOAL_REF) == (None, None)


@pytest.mark.parametrize(
    "value",
    ["n/a", "n/a -", "n/a:", "n/a - **", "n/a - `"],
)
def test_a_reasonless_optout_is_short_not_a_reference(value: str) -> None:
    """A reasonless `n/a` must be `optout_short` (present, not satisfying).

    Falling through to `ref` made the EMPTIEST opt-out the strongest one: it
    satisfied the floor outright while a one-word reason was correctly refused.
    Markup stripping newly opened this for the forms whose reason is erased into
    it (`n/a - **`); the bare `n/a` form predates the markup work.
    """
    body = _coord(f"## Coordination Cues\n\n- Successor goal: {value}\n")
    kind, _ = cf._parse_step(body, cf._SUCCESSOR_GOAL_REF)
    assert kind == "optout_short"
    assert kind not in cf._SATISFYING


def test_joined_continuation_cannot_upgrade_a_placeholder_optout() -> None:
    """The joined path appends a continuation line to the value, which pushed an
    unfilled `n/a - <reason>` past MIN_OPTOUT_REASON with the placeholder still
    in it. Production reads the JOINED body, so this is the real path."""
    text = (
        "## Coordination Cues\n\n"
        "- Gather: n/a - <reason>\n"
        "  the link was only background, not routed context\n"
    )
    joined = fg.joined_section_body(text, "Coordination Cues")
    assert cf._parse_step(joined, cf._GATHER_REF) == (None, None)


def test_placeholder_does_not_shadow_a_real_cue_below_it() -> None:
    body = _coord(
        "## Coordination Cues\n\n"
        "- `Gather: <path>`\n"
        "- `Gather: charness-artifacts/gather/2026-08-08-real.md`\n"
    )
    assert cf._parse_step(body, cf._GATHER_REF) == ("ref", "charness-artifacts/gather/2026-08-08-real.md")


# --- cross-floor opt-out aggregate -----------------------------------------
# Each opt-out passes its own floor, so nothing surfaced the PATTERN: a goal that
# declined four of six coordination obligations rendered identically to one that
# declined none. Non-blocking by construction.


def _aggregate(text: str) -> dict:
    report: dict = {"ok": True}
    cf.apply_coordination_floors(report, text)
    pr.apply_phase_routing_floor(report, text)
    cf.apply_coordination_optout_aggregate(report)
    return report


_AGG_GOAL = """# G
Created: 2026-08-08

## Context Sources
- https://example.com/spec

## Coordination Cues
{cues}

## Slice Log
- What changed: scripts/x.py
- bump_version was run
"""


def test_optout_aggregate_counts_only_triggered_floors() -> None:
    report = _aggregate(
        _AGG_GOAL.format(
            cues=(
                "- Gather: n/a - the external link was read by a teammate here\n"
                "- Release: n/a - no version bump or install manifest was touched\n"
                "- Successor goal: charness-artifacts/goals/2026-08-09-next.md\n"
                "- Routing: impl - selected from installed skill metadata\n"
            )
        )
    )
    agg = report["coordination_optout_aggregate"]
    assert agg["opted_out"] == 2
    assert agg["eligible"] == 4
    assert agg["routed"] == 2
    assert agg["opted_out_obligations"] == ["gather", "release"]
    assert "2 of its 4" in agg["reason"]
    # untriggered floors must not inflate the denominator
    assert "issue_closeout" not in agg["eligible_obligations"]


def test_optout_aggregate_never_blocks() -> None:
    """Every counted opt-out already satisfied its own floor; re-refusing here
    would punish a valve the contract deliberately provides."""
    report = _aggregate(
        _AGG_GOAL.format(
            cues=(
                "- Gather: n/a - the external link was read by a teammate here\n"
                "- Release: n/a - no version bump or install manifest was touched\n"
                "- Successor goal: n/a - the operator asked for no successor goal\n"
                "- Routing: n/a - nothing crossed a phase boundary in this run\n"
            )
        )
    )
    assert report["ok"] is True
    agg = report["coordination_optout_aggregate"]
    assert agg["opted_out"] == agg["eligible"] > 0


def test_optout_aggregate_reports_a_clean_run_without_a_reason() -> None:
    report = _aggregate(
        _AGG_GOAL.format(
            cues=(
                "- Gather: charness-artifacts/gather/2026-08-08-spec.md\n"
                "- Release: charness-artifacts/release/v3.2.0.md\n"
                "- Successor goal: charness-artifacts/goals/2026-08-09-next.md\n"
                "- Routing: impl - selected from installed skill metadata\n"
            )
        )
    )
    agg = report["coordination_optout_aggregate"]
    assert agg["opted_out"] == 0
    assert agg["routed"] == agg["eligible"] > 0
    assert "reason" not in agg  # nothing to hand the reviewer


def test_optout_aggregate_counts_the_issue_closeout_floor_positively() -> None:
    """The `issue_closeout` key had only a NEGATIVE assertion, which passes
    identically whether the key is spelled right or typo'd. A typo'd key would
    silently count zero — a false-clean worse than having no census at all."""
    text = _AGG_GOAL.format(
        cues=(
            "- Issue closeout: n/a - the tracked issue is context only, not closed here\n"
            "- Successor goal: charness-artifacts/goals/2026-08-09-next.md\n"
            "- Gather: charness-artifacts/gather/2026-08-08-spec.md\n"
            "- Release: charness-artifacts/release/v3.2.0.md\n"
            "- Routing: impl - selected from installed skill metadata\n"
        )
    ).replace("- https://example.com/spec", "- https://example.com/spec\n- tracked issue #999")
    agg = _aggregate(text)["coordination_optout_aggregate"]
    assert "issue_closeout" in agg["eligible_obligations"]
    assert "issue_closeout" in agg["opted_out_obligations"]


def test_optout_aggregate_does_not_call_an_unmet_floor_routed() -> None:
    """`routed` was computed by SUBTRACTION, so a floor with no cue line at all
    counted as routed — telling a reviewer the goal routed the obligation it
    skipped, on the very refusal report where they would read it."""
    report = _aggregate(_AGG_GOAL.format(cues="- Routing: impl - selected from metadata\n"))
    agg = report["coordination_optout_aggregate"]
    # gather + release triggered with no cue line; neither is routed nor an opt-out
    assert "gather" in agg["unsatisfied_obligations"]
    assert "release" in agg["unsatisfied_obligations"]
    assert agg["routed"] == 1  # only the routing cue is genuinely routed
    assert agg["routed"] + agg["opted_out"] + agg["unsatisfied"] == agg["eligible"]


def test_one_blanket_routing_optout_counts_as_one_decision() -> None:
    """`_parse_routing_step` answers per skill, so a single blanket
    `Routing: n/a` returned `optout` for every required route and the census
    reported four opt-outs for one authored decision."""
    text = _AGG_GOAL.format(
        cues=(
            "- Gather: charness-artifacts/gather/2026-08-08-spec.md\n"
            "- Release: charness-artifacts/release/v3.2.0.md\n"
            "- Successor goal: charness-artifacts/goals/2026-08-09-next.md\n"
            "- Routing: n/a - nothing crossed a phase boundary in this run at all\n"
        )
    )
    agg = _aggregate(text)["coordination_optout_aggregate"]
    routing_labels = [o for o in agg["eligible_obligations"] if o.startswith("routing")]
    assert routing_labels == ["routing"]
    assert agg["opted_out_obligations"] == ["routing"]


def test_optout_aggregate_never_appends_to_coordination_missing() -> None:
    report = _aggregate(
        _AGG_GOAL.format(
            cues=(
                "- Gather: n/a - the external link was read by a teammate here\n"
                "- Release: n/a - no version bump or install manifest was touched\n"
                "- Successor goal: n/a - the operator asked for no successor goal\n"
                "- Routing: n/a - nothing crossed a phase boundary in this run\n"
            )
        )
    )
    assert report["ok"] is True
    assert "coordination_missing" not in report


def test_grandfathered_goal_carries_its_own_scope_in_the_census() -> None:
    """A grandfathered goal short-circuits before any floor key is written, so a
    bare `eligible: 0` was indistinguishable from an in-scope goal that triggered
    nothing. The census is what a reviewer reads, so it carries its own scope."""
    old = _AGG_GOAL.replace("Created: 2026-08-08", "Created: 2026-01-01")
    agg = _aggregate(old.format(cues="- Routing: impl - selected from metadata\n"))
    agg = agg["coordination_optout_aggregate"]
    assert agg["coordination_in_scope"] is False


# --- round-2: the placeholder guard must not eat REAL values ----------------


@pytest.mark.parametrize(
    "line,ref",
    [
        ("- Successor goal: <charness-artifacts/goals/2026-08-09-next.md>", "_SUCCESSOR_GOAL_REF"),
        ("- Gather: <https://example.com/thread>", "_GATHER_REF"),
        ("- Release: <charness-artifacts/release/v3.2.0.md>", "_RELEASE_REF"),
    ],
)
def test_a_markdown_autolink_is_a_filled_reference_not_a_placeholder(line: str, ref: str) -> None:
    """A CONTAINS placeholder scan whose character class included `/` and `.`
    swallowed an autolinked artifact path — reintroducing the exact false refusal
    this whole slice exists to remove, from the other direction."""
    body = _coord(f"## Coordination Cues\n\n{line}\n")
    kind, _ = cf._parse_step(body, getattr(cf, ref))
    assert kind == "ref"


@pytest.mark.parametrize(
    "reason",
    [
        "the thread only discussed Dict<str, int> annotations, nothing was routed",
        "the diff only touches List<String> conversions in the parser, no routing",
    ],
)
def test_a_generic_type_in_an_optout_reason_is_not_a_placeholder(reason: str) -> None:
    """`Dict<str, int>` is preceded by an identifier character; a placeholder is
    not. Without that exclusion a valid 60-char opt-out read as 'no step at all'."""
    body = _coord(f"## Coordination Cues\n\n- Gather: n/a - {reason}\n")
    kind, _ = cf._parse_step(body, cf._GATHER_REF)
    assert kind == "optout"


@pytest.mark.parametrize(
    "value",
    ["<link to the thread (if any)>", "<TBD: the next goal>", "<reason: which owner skill owned this>"],
)
def test_a_placeholder_carrying_punctuation_still_never_satisfies(value: str) -> None:
    """The first character class omitted `:` and `(`, so these classified as real
    references and SATISFIED a floor."""
    body = _coord(f"## Coordination Cues\n\n- Gather: {value}\n")
    assert cf._parse_step(body, cf._GATHER_REF) == (None, None)
    na = _coord(f"## Coordination Cues\n\n- Gather: n/a - {value}\n")
    assert cf._parse_step(na, cf._GATHER_REF) == (None, None)


@pytest.mark.parametrize(
    "value",
    ["n/a.", "n/a, nope", "n/a (nothing external was routed)", "N/A;", "n / a", "na"],
)
def test_an_optout_with_any_separator_is_never_a_reference(value: str) -> None:
    """Enumerating the four separators meant `n/a, nope` SATISFIED the floor while
    `n/a - nope` was correctly refused — a one-character bypass of the reason
    floor, and the same 'emptiest opt-out is strongest' inversion in new clothes."""
    body = _coord(f"## Coordination Cues\n\n- Gather: {value}\n")
    kind, _ = cf._parse_step(body, cf._GATHER_REF)
    assert kind not in cf._SATISFYING


@pytest.mark.parametrize("value", ["national coverage of the release notes", "n/august-report.md"])
def test_a_value_merely_starting_with_n_is_still_a_reference(value: str) -> None:
    body = _coord(f"## Coordination Cues\n\n- Gather: {value}\n")
    assert cf._parse_step(body, cf._GATHER_REF)[0] == "ref"


def test_the_routing_loop_also_demotes_a_placeholder_optout() -> None:
    """The demotion had a test on the coordination consumer only; reverting the
    phase-routing call site alone left the whole suite green while
    `Routing: n/a - <why...>` satisfied routing for every required skill."""
    line = "- Routing: n/a - <why none of the phase skills owned this slice at all>"
    assert pr._parse_routing_step(line, "impl") == (None, None)


# --- round-2: routing census must follow the floor's own verdict ------------

_MIXED_GOAL = """# G
Created: 2026-08-08

## Context Sources
- local only

## Coordination Cues
{cues}

## Slice Log
- What changed: scripts/x.py
- the validator was updated
"""


@pytest.mark.parametrize(
    "order",
    [
        ("- Routing: impl - selected from installed metadata\n"
         "- Routing: n/a - nothing else crossed a phase boundary in this run\n"),
        ("- Routing: n/a - nothing else crossed a phase boundary in this run\n"
         "- Routing: impl - selected from installed metadata\n"),
    ],
)
def test_mixed_routing_evidence_is_censused_by_the_floors_own_verdict(order: str) -> None:
    """Two defects in one: a set-equality collapse censused a SATISFIED routing
    floor as `unsatisfied` (and dropped the authored opt-out, so no advisory was
    raised at all), and the verdict flipped purely on which cue line came first.
    """
    # `Phases: quality` is what makes this fixture mixed now. It used to be mixed
    # because the word "validator" appeared in its Slice Log, which is exactly the
    # prose guess that got replaced by this declaration.
    text = _MIXED_GOAL.format(
        cues="- Phases: quality\n" + order + "- Successor goal: charness-artifacts/goals/x.md\n"
    )
    report = _aggregate(text)
    assert report["phase_routing_floor"]["satisfied"] is True
    assert len(report["phase_routing_floor"]["required"]) >= 2  # the fixture really is mixed
    agg = report["coordination_optout_aggregate"]
    assert "routing" in agg["opted_out_obligations"]
    assert "routing" not in agg["unsatisfied_obligations"]
    assert agg["reason"]  # an authored opt-out always reaches the reviewer


def test_routing_triggered_with_a_malformed_evidence_map_fails_closed() -> None:
    report = {"phase_routing_floor": {"triggered": True, "satisfied": True, "evidence": {}}}
    assert cf._routing_aggregate_kind(report["phase_routing_floor"]) == "unsatisfied"
