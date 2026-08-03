"""Direct unit tests for `scripts/quality_policy_merge.py`.

The module was extracted from `quality_policy_defaults` and its behaviour was
reachable only end-to-end through the bootstrap. That left the merges' own accept/
reject branches proven by inference, and it left the pre-push changed-line lane with
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
    "scripts.quality_policy_defaults", ROOT / "scripts" / "quality_policy_defaults.py"
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
