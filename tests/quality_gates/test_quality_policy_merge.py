"""Direct unit tests for `scripts/adapters/quality_policy_merge.py`.

The module was extracted from `quality_policy_defaults` and its behaviour was
reachable only end-to-end through the bootstrap. That left the merges' own accept/
reject branches proven by inference, and it left the release changed-line proof with
a new pool file whose standing tests do not exercise it — which is how this file came
to exist: the lane refused the push and named `return merged_policy` as an uncovered
changed line, twice.

`merge_*` is deliberately PERMISSIVE — an unusable value keeps the default rather than
raising — so the tests that matter are the ones pinning exactly which values it accepts
and which it silently drops, because a silent drop is the operator intent that
`refilled_policy_subkeys` has to notice.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "scripts.adapters.quality_policy_defaults",
    ROOT / "scripts" / "adapters" / "quality_policy_defaults.py",
)
defaults = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(defaults)

merge_coverage_floor_policy = defaults.merge_coverage_floor_policy
merge_prompt_asset_policy = defaults.merge_prompt_asset_policy
refilled_policy_subkeys = defaults.refilled_policy_subkeys
FLOOR = defaults.DEFAULT_COVERAGE_FLOOR_POLICY
PROMPT = defaults.DEFAULT_PROMPT_ASSET_POLICY


def test_a_non_mapping_keeps_every_default() -> None:
    """`coverage_floor_policy: "see docs"` supplies nothing usable, so the merge keeps
    the whole preset — which is exactly why `refilled_policy_subkeys` must report every
    key for that input rather than an empty list."""
    for value in ("see docs/quality.md", ["a", "b"], 7, None):
        assert merge_coverage_floor_policy(value) == FLOOR
        assert merge_prompt_asset_policy(value) == PROMPT


def test_an_empty_mapping_keeps_every_default_too() -> None:
    assert merge_coverage_floor_policy({}) == FLOOR
    assert merge_prompt_asset_policy({}) == PROMPT


def test_accepted_values_replace_the_default() -> None:
    merged = merge_coverage_floor_policy({"fail_below_pct": 90.0, "lefthook_path": "hooks.yml"})

    assert merged["fail_below_pct"] == 90.0
    assert merged["lefthook_path"] == "hooks.yml"


def test_an_int_is_accepted_for_a_float_default_and_coerced() -> None:
    """The operator writing `80` for an `80.0` default means the same thing, and the
    coercion is what keeps `refilled_policy_subkeys` from calling it a refill."""
    merged = merge_coverage_floor_policy({"fail_below_pct": 80})

    assert merged["fail_below_pct"] == 80.0
    assert isinstance(merged["fail_below_pct"], float)
    assert refilled_policy_subkeys({"fail_below_pct": 80}, FLOOR, merged) == sorted(
        key for key in FLOOR if key != "fail_below_pct"
    )


def test_a_wrong_typed_value_is_silently_dropped_and_reported_as_a_refill() -> None:
    """The pairing that matters. The merge drops it (permissive by design) and the
    account of the merge is what makes the drop visible — a float against an int
    default fails every branch, so the default wins and the operator's value is gone."""
    raw = {"min_statements_threshold": 30.5}
    merged = merge_coverage_floor_policy(raw)

    assert merged["min_statements_threshold"] == FLOOR["min_statements_threshold"]
    assert "min_statements_threshold" in refilled_policy_subkeys(raw, FLOOR, merged)


def test_prompt_asset_lists_and_scalar_accept_and_reject() -> None:
    merged = merge_prompt_asset_policy(
        {"source_globs": ["src/**"], "exemption_globs": "not-a-list", "min_multiline_chars": 40}
    )

    assert merged["source_globs"] == ["src/**"]
    assert merged["exemption_globs"] == PROMPT["exemption_globs"]  # wrong type -> default
    assert merged["min_multiline_chars"] == 40
    assert "exemption_globs" in refilled_policy_subkeys(
        {"source_globs": ["src/**"], "exemption_globs": "not-a-list", "min_multiline_chars": 40},
        PROMPT,
        merged,
    )


def test_a_list_of_non_strings_is_rejected_wholesale() -> None:
    """Partial acceptance would be worse than none: half a glob list is a scope nobody
    declared. The merge requires every entry to be a string."""
    merged = merge_prompt_asset_policy({"source_globs": ["ok", 7]})

    assert merged["source_globs"] == PROMPT["source_globs"]


def test_the_merge_never_mutates_the_module_default() -> None:
    """`refilled_policy_subkeys` compares against the module-level defaults, so a merge
    that mutated them in place would make every later comparison meaningless."""
    before = dict(FLOOR)
    merge_coverage_floor_policy({"fail_below_pct": 12.0, "lefthook_path": "x.yml"})

    assert FLOOR == before


MUTATION = defaults.DEFAULT_MUTATION_TESTING


def _merged_mutation(**blocks: dict) -> dict:
    """The merge's result for a raw block: defaults, with the operator's leaves on top.

    Built here rather than by calling the bootstrap, because the defect under test is in
    what the REPORT says about a merge, not in what the merge produces.
    """
    merged = {key: dict(value) if isinstance(value, dict) else value for key, value in MUTATION.items()}
    for name, supplied in blocks.items():
        merged[name] = {**MUTATION[name], **supplied}
    return merged


def test_a_partially_written_nested_block_names_its_refilled_leaves() -> None:
    """The issue's reproduction: `report_paths` kept, `summary_md` the only leaf left.

    Comparing top-level keys only reported the whole block as one refilled key, so the
    two leaves the merge actually refilled were named nowhere. #481 was whole-field,
    #489 sub-key, this is sub-sub-key — the rule stopping one level above the next
    instance for the third time in the family.
    """
    # No `score_break` in the raw block: `_merged_mutation` can only overlay NESTED
    # blocks, so pairing a customised scalar with a merged block that still carries the
    # default would model a merge the real bootstrap cannot produce.
    raw = {"report_paths": {"summary_md": MUTATION["report_paths"]["summary_md"]}}

    reported = refilled_policy_subkeys(raw, MUTATION, _merged_mutation())

    assert "report_paths.sample_md" in reported
    assert "report_paths.log" in reported
    assert "report_paths.summary_md" not in reported, "the operator wrote this one"
    assert "report_paths" not in reported, "the coarse block name is replaced, not added to"


def test_a_customised_leaf_no_longer_hides_the_whole_block() -> None:
    """The quieter and worse arm of the same defect. With `report_paths` refilled to
    exactly the default the block at least got NAMED; once the operator customised one
    leaf the merged block stopped equalling the default, the `merged == default` test
    failed, and a partially refilled block vanished from the report altogether."""
    raw = {"report_paths": {"summary_md": "custom/summary.md"}}
    merged = _merged_mutation(report_paths={"summary_md": "custom/summary.md"})

    reported = refilled_policy_subkeys(raw, MUTATION, merged)

    assert "report_paths.sample_md" in reported and "report_paths.log" in reported


def test_a_fully_specified_nested_block_reports_nothing() -> None:
    """The false-positive control. A report that fires on a block the operator wrote out
    in full is a report that gets walked past — which this repo has already measured as
    the way a warning stops working."""
    raw = {"report_paths": dict(MUTATION["report_paths"]), "auto_issue": dict(MUTATION["auto_issue"])}

    reported = refilled_policy_subkeys(raw, MUTATION, _merged_mutation())

    assert not [name for name in reported if name.startswith(("report_paths", "auto_issue"))]


def test_a_fully_specified_nested_block_with_CUSTOM_values_reports_nothing() -> None:
    """The control above used the DEFAULT values, so the merged block equalled the
    defaults — and that is exactly why it could not catch this.

    A block written out in full with customised values is also unequal to the defaults.
    A `merged_sub != default` fallback therefore named it as refilled when nothing was,
    which is a MIS-name; this function may only ever err by over-naming a real loss. The
    broad suite caught it (`test_quality_bootstrap_adapter_preserves_existing_explicit_commands`
    flipped `mutation_testing` from `preserved` to `augmented`) after the slice gate and
    both bounded rounds passed, so the predicate is now structural: did the merge produce
    a block carrying every default key?
    """
    custom = {"summary_md": "custom/summary.md", "sample_md": "custom/sample.md", "log": "custom/run.log"}
    raw = {"report_paths": dict(custom)}
    merged = _merged_mutation(report_paths=custom)

    reported = refilled_policy_subkeys(raw, MUTATION, merged)

    assert not [name for name in reported if name.startswith("report_paths")], reported


def test_a_nested_block_refilled_whole_keeps_its_block_name() -> None:
    """Granularity goes where the ambiguity is. A block the operator never wrote is
    refilled entirely, and one block name says that better than every leaf under it —
    a report nobody reads is the failure mode being avoided, not a target."""
    for raw_block in ({}, {"report_paths": {}}, {"report_paths": "see docs/quality.md"}):
        reported = refilled_policy_subkeys(raw_block, MUTATION, _merged_mutation())
        assert "report_paths" in reported, raw_block
        assert not [name for name in reported if name.startswith("report_paths.")], raw_block


def test_recursion_does_not_change_the_flat_blocks_it_already_covered() -> None:
    """`coverage_floor_policy` has no nested defaults, so every name it reports must stay
    undotted. The recursion is an addition at a level that had no reporting, not a
    re-spelling of the level that did."""
    merged = {**FLOOR, "fail_below_pct": 80}

    reported = refilled_policy_subkeys({"fail_below_pct": 80}, FLOOR, merged)

    assert reported and not [name for name in reported if "." in name]


def test_a_block_the_merge_did_not_produce_reports_its_name_not_silence() -> None:
    """The repair must not carry the class it repairs.

    Recursing with an empty `merged` returns no leaves — every leaf test compares against
    `merged.get(leaf)`, which is then always `None` — and swallowing the block name on top
    of that would report a partially refilled block as NOTHING. Silence is the arm of this
    defect that was worse than the coarseness it replaced.

    The first cut of this guard tested `not isinstance(merged_sub, dict)` and this test
    covered only non-dicts, so both stopped at the TYPE boundary while the boundary that
    breaks the leaf comparison is whether the merge produced the block at all. `{}` is a
    dict: it recursed, found nothing, and went silent — the repair carrying the class it
    repairs, one value away from where the guard was put. The empty and partial dicts
    below are that case.
    """
    raw = {"report_paths": {"summary_md": "custom/summary.md"}}

    for lost in (None, "see docs/quality.md", [], {}, {"summary_md": "custom/summary.md"}):
        merged = {**_merged_mutation(), "report_paths": lost}
        reported = refilled_policy_subkeys(raw, MUTATION, merged)
        assert "report_paths" in reported, lost
