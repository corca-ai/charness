"""Adapter-block validation behaviour reached through `load_quality_adapter`.

This is the #453 sibling sweep. #453 was filed because a rejection line inside a
parameterized validator helper was executed by tests but never asserted: the
natural test for a bad config (`assert not payload["valid"]`) exercises the
caller, so the message text and the "the rejected value never merged" guarantee
both stay unpinned. Rejection cases here therefore assert the exact
operator-facing message AND the post-rejection state. Acceptance and edge cases
are also present where a bound or a branch would otherwise only be pinned from
one side (range endpoints, `changed_quota: 0`, unknown-sub-key warnings that must
not block).

Boundary. This module owns the cases that go through the canonical
`load_quality_adapter` entrypoint — so the wiring in `quality_adapter_lib` is
part of what is proven — for these `scripts/adapters/quality_policy_defaults.py`
surfaces: the `validate_mutation_testing` scalar-slot and sub-mapping helpers,
`validate_standing_doc_provenance`, `validate_changed_line_mutation_gate`, and
`validate_skill_ergonomics_gate_rules`.

What deliberately stays in `test_quality_mutation_testing.py`: the
`mutation_testing` block's fixture/propose-probe acceptance cases, the workflow
template checks, and `test_auto_issue_label_with_comma_is_refused`, which calls
`_validate_mutation_auto_issue` directly rather than through the adapter and so
sits on the other side of this module's entrypoint boundary. The
`standing_doc_provenance` and `changed_line_mutation_gate` *gate scripts* keep
their own end-to-end tests in `test_standing_doc_provenance.py` and
`test_changed_line_coverage_gate.py`; those reach the same validators through a
separate `adapter_errors` payload, which is why the mapping-shape cases appear in
both places rather than being deduplicated into one.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from scripts.adapters import quality_adapter_lib
from scripts.adapters.quality_adapter_lib import load_quality_adapter
from scripts.adapters.quality_policy_defaults import (
    DEFAULT_CHANGED_LINE_MUTATION_GATE,
    DEFAULT_MUTATION_TESTING,
    DEFAULT_STANDING_DOC_PROVENANCE,
    VALID_SKILL_ERGONOMICS_GATE_RULES,
)

_ADAPTER_HEADER = dedent(
    """\
    version: 1
    repo: testrepo
    language: en
    output_dir: charness-artifacts/quality
    """
)


def _resolve(tmp_path: Path, block: str) -> dict:
    repo = tmp_path / "r"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER + block, encoding="utf-8"
    )
    return load_quality_adapter(repo)


def test_nose_inventory_paths_reject_repo_escape(tmp_path: Path) -> None:
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            nose_inventory_paths:
              - ../consumer-src
              - /tmp/outside
              - ..\\windows-src
              - C:\\outside
              - \\windows-root
            """
        ),
    )
    assert not payload["valid"]
    assert any(
        "nose_inventory_paths entries must be non-empty repo-relative paths" in error
        for error in payload["errors"]
    )
    assert payload["data"]["nose_inventory_paths"] == []


def test_nose_inventory_paths_null_keeps_the_default_scope(tmp_path: Path) -> None:
    errors: list[str] = []

    assert quality_adapter_lib.adapter_validators.nose_inventory_paths(None, errors) is None
    assert errors == []

    payload = _resolve(tmp_path, "nose_inventory_paths: null\n")

    assert payload["valid"]
    assert payload["data"]["nose_inventory_paths"] == []


def test_nose_inventory_paths_rejects_empty_entries() -> None:
    errors: list[str] = []

    assert quality_adapter_lib.adapter_validators.nose_inventory_paths([""], errors) is None
    assert errors == ["nose_inventory_paths must be a list of non-empty strings"]


@pytest.mark.parametrize("value", ["not-a-list", "[1]"])
def test_nose_inventory_paths_rejects_non_string_lists(tmp_path: Path, value: str) -> None:
    payload = _resolve(tmp_path, f"nose_inventory_paths: {value}\n")

    assert not payload["valid"]
    assert "nose_inventory_paths must be a list of strings" in payload["errors"]
    assert payload["data"]["nose_inventory_paths"] == []


def test_version_validator_rejects_non_integer() -> None:
    errors: list[str] = []
    validated: dict = {}

    quality_adapter_lib.adapter_validators.validate_version_field({"version": "one"}, validated, errors)

    assert validated == {}
    assert errors == ["version must be an integer"]


# ---------------------------------------------------------------------------
# mutation_testing sub-mapping rejections


def test_a2_command_slot_non_string_is_rejected_by_name(tmp_path: Path) -> None:
    """Every `mutation_testing` command slot is interpolated into the workflow as a
    shell command. A non-string slot (a YAML bare number, or a list from a stray
    `-`) would render as its Python repr and fail at runtime inside CI, far from the
    config that caused it. The rejection must name the offending section AND key, so
    the operator does not have to bisect the block."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              commands:
                full: 5
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.commands.full must be a string" in payload["errors"]
    # The rejected value never reaches the merged config.
    assert (
        payload["data"]["mutation_testing"]["commands"]["full"]
        == DEFAULT_MUTATION_TESTING["commands"]["full"]
    )


def test_a2_auto_issue_string_slot_non_string_is_rejected(tmp_path: Path) -> None:
    """`auto_issue` runs its own value check (the comma-in-label rule), so it does
    not inherit the shared string check for free — it has to delegate to it. A
    non-string `label` here would be attached to a real GitHub issue, so the
    delegation is load-bearing rather than cosmetic."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              auto_issue:
                label: 42
                enabled: "yes"
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.auto_issue.label must be a string" in payload["errors"]
    assert (
        payload["data"]["mutation_testing"]["auto_issue"]["label"]
        == DEFAULT_MUTATION_TESTING["auto_issue"]["label"]
    )
    # `enabled` keeps its own boolean check rather than falling through to the
    # string one, so the two paths do not collapse into each other.
    assert "mutation_testing.auto_issue.enabled must be a boolean" in payload["errors"]
    assert "mutation_testing.auto_issue.enabled must be a string" not in payload["errors"]


@pytest.mark.parametrize("section", ["commands", "auto_issue", "report_paths"])
def test_a2_mapping_section_given_a_scalar_is_rejected(tmp_path: Path, section: str) -> None:
    """A scalar where a sub-mapping belongs is the shape a hand-edited adapter
    produces (`commands: npm run test:mutation` instead of the nested form). Without
    this check the loop over `raw.items()` would raise AttributeError and surface as
    a crash instead of a config error, so each section must refuse it by name."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              {section}: "not a mapping"
            """
        ),
    )
    assert not payload["valid"]
    assert f"mutation_testing.{section} must be a mapping" in payload["errors"]
    # Refusal leaves the defaults intact rather than a half-merged section.
    assert payload["data"]["mutation_testing"][section] == DEFAULT_MUTATION_TESTING[section]


# ---------------------------------------------------------------------------
# mutation_testing scalar-slot rejections (#453 sibling sweep)
#
# Each helper below is a parameterized collapse of what used to be N duplicated
# validation branches. That collapse is exactly the shape that produced #453: the
# rejection message moves out from under the tests that covered it, and the
# natural test for a bad config (`assert not payload["valid"]`) exercises the
# caller while leaving the message and the post-rejection state unasserted. These
# assert the message text AND that the rejected value never merged.


def test_a2_score_break_wrong_type_rejected(tmp_path: Path) -> None:
    """The type branch of `_validate_mutation_score_break`. It lives next to its
    range sibling below on purpose: the two branches of one helper are the seam a
    later consolidation collapses, and #453 happened when such a pair's proof was
    split across files."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              score_break: "high"
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.score_break must be an integer" in payload["errors"]
    # The type check returns before the range check, so no range error is emitted
    # for a value that has no order at all.
    assert "mutation_testing.score_break must be between 0 and 100" not in payload["errors"]
    assert (
        payload["data"]["mutation_testing"]["score_break"]
        == DEFAULT_MUTATION_TESTING["score_break"]
    )


@pytest.mark.parametrize("bad", [-1, 101])
def test_a2_score_break_outside_zero_to_one_hundred_is_rejected(tmp_path: Path, bad: int) -> None:
    """`score_break` is a percentage compared against a mutation score, so a value
    outside 0-100 is either unsatisfiable (>100) or vacuous (<0) — a gate that can
    never fail is worse than no gate. The range check is separate from the type
    check, so it needs its own message and its own proof."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              score_break: {bad}
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.score_break must be between 0 and 100" in payload["errors"]
    # The out-of-range value never reaches the merged config.
    assert (
        payload["data"]["mutation_testing"]["score_break"]
        == DEFAULT_MUTATION_TESTING["score_break"]
    )


@pytest.mark.parametrize("edge", [0, 100])
def test_a2_score_break_accepts_both_range_endpoints(tmp_path: Path, edge: int) -> None:
    """The endpoints are inside the range. Pinning them keeps the bound from
    silently tightening to an exclusive comparison, which would reject a legitimate
    `score_break: 100` (every mutant must die) with a range error."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              score_break: {edge}
            """
        ),
    )
    assert payload["valid"], payload["errors"]
    assert payload["data"]["mutation_testing"]["score_break"] == edge


_MUTATION_INT_KEYS = [
    "changed_quota",
    "max_files",
    "max_executable_mutants",
    "max_executable_mutants_per_file",
    "max_test_nodeids",
]


@pytest.mark.parametrize("key", _MUTATION_INT_KEYS)
def test_a2_int_slot_non_integer_is_rejected_by_name(tmp_path: Path, key: str) -> None:
    """Every one of these slots becomes a numeric limit in the mutation run's
    selection budget. A string would survive validation and then fail deep inside
    the run, so the rejection has to name the offending key rather than the shared
    helper that checked it."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              {key}: "lots"
            """
        ),
    )
    assert not payload["valid"]
    assert f"mutation_testing.{key} must be an integer" in payload["errors"]
    assert (
        payload["data"]["mutation_testing"][key] == DEFAULT_MUTATION_TESTING[key]
    )


@pytest.mark.parametrize("key", _MUTATION_INT_KEYS)
def test_a2_int_slot_negative_is_rejected_by_name(tmp_path: Path, key: str) -> None:
    """A negative budget is not a small budget: it is a limit no candidate can
    satisfy, which silently empties the mutation selection. The lower-bound check is
    a different failure from the type check and carries a different message."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              {key}: -1
            """
        ),
    )
    assert not payload["valid"]
    assert (
        f"mutation_testing.{key} must be greater than or equal to 0" in payload["errors"]
    )
    assert f"mutation_testing.{key} must be an integer" not in payload["errors"]
    assert payload["data"]["mutation_testing"][key] == DEFAULT_MUTATION_TESTING[key]


def test_a2_int_slot_accepts_zero(tmp_path: Path) -> None:
    """Zero is the deliberate "select nothing from this axis" setting and sits on
    the inclusive edge of the bound. Without this, tightening `raw < 0` to
    `raw <= 0` would reject it with a lower-bound error and read as valid."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              changed_quota: 0
            """
        ),
    )
    assert payload["valid"], payload["errors"]
    assert payload["data"]["mutation_testing"]["changed_quota"] == 0


def test_a2_int_slot_rejects_a_bool(tmp_path: Path) -> None:
    """`true` is an `int` subclass in Python, so a bare boolean would otherwise
    merge as the limit `1` — a budget of one mutant that looks configured. The
    explicit bool exclusion in the shared helper is load-bearing."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              max_files: true
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.max_files must be an integer" in payload["errors"]
    assert (
        payload["data"]["mutation_testing"]["max_files"]
        == DEFAULT_MUTATION_TESTING["max_files"]
    )


@pytest.mark.parametrize("key", ["schedule_cron", "workflow_path"])
def test_a2_top_level_string_slot_non_string_is_rejected_by_name(
    tmp_path: Path, key: str
) -> None:
    """`schedule_cron` is interpolated into the workflow's `cron:` field and
    `workflow_path` into a filesystem path. A non-string in either renders as its
    Python repr inside generated YAML, so the check must refuse it by key name here
    too — not only inside the nested `commands` mapping."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            mutation_testing:
              {key}: 5
            """
        ),
    )
    assert not payload["valid"]
    assert f"mutation_testing.{key} must be a string" in payload["errors"]
    assert payload["data"]["mutation_testing"][key] == DEFAULT_MUTATION_TESTING[key]


def test_a2_declined_non_boolean_is_rejected(tmp_path: Path) -> None:
    """`declined` decides whether the whole mutation surface is opted out, and the
    propose probe reports `status: declined` off it. A truthy non-bool (`1`, or the
    string `"true"`) must not opt a repo out by accident, so the check is an
    identity check rather than a truthiness one."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            mutation_testing:
              declined: 1
            """
        ),
    )
    assert not payload["valid"]
    assert "mutation_testing.declined must be a boolean" in payload["errors"]
    # The rejected value never merges, so the repo stays opted IN.
    assert (
        payload["data"]["mutation_testing"]["declined"]
        == DEFAULT_MUTATION_TESTING["declined"]
    )
    assert payload["data"]["mutation_testing"]["declined"] is False


# ---------------------------------------------------------------------------
# standing_doc_provenance


def test_standing_doc_provenance_scalar_block_is_rejected(tmp_path: Path) -> None:
    """A scalar where the mapping belongs is what a hand-edited adapter produces.
    Without the shape check the loop over `value.items()` raises AttributeError and
    the operator sees a traceback instead of a config error."""
    payload = _resolve(tmp_path, "standing_doc_provenance: docs/*.md\n")
    assert not payload["valid"]
    assert "standing_doc_provenance must be a mapping" in payload["errors"]
    # Honest scope: the message assertion above is what has teeth here. The line
    # below only discriminates a validator that returns the scalar instead of None,
    # because `infer_quality_defaults` seeds this key either way.
    assert payload["data"]["standing_doc_provenance"] == DEFAULT_STANDING_DOC_PROVENANCE


def test_standing_doc_provenance_unknown_subkey_warns_without_blocking(
    tmp_path: Path,
) -> None:
    """Typo drift in an opt-in block is silent failure: the gate stays inert and
    reads as configured. The unknown key surfaces as a warning by name (so the typo
    is visible) but must not block, because the block is otherwise usable.

    The known key is supplied AFTER the typo so the assertion has teeth: skipping
    the unknown key has to be a `continue`, not a `break` or an early return, or the
    rest of a real operator's block would be dropped on the floor behind a warning
    that reads as harmless."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            standing_doc_provenance:
              standing_doc: ["docs/*.md"]
              inline_allow_marker: keep-me
            """
        ),
    )
    assert payload["valid"], payload["errors"]
    assert "unknown standing_doc_provenance sub-key: standing_doc" in payload["warnings"]
    # The typo did not become configuration...
    assert (
        payload["data"]["standing_doc_provenance"]["standing_docs"]
        == DEFAULT_STANDING_DOC_PROVENANCE["standing_docs"]
    )
    # ...and the keys after it still did.
    assert payload["data"]["standing_doc_provenance"]["inline_allow_marker"] == "keep-me"


@pytest.mark.parametrize("key", ["standing_docs", "tracking_allowlist"])
def test_standing_doc_provenance_glob_list_rejects_non_strings_by_name(
    tmp_path: Path, key: str
) -> None:
    """Both keys are glob lists consumed by `fnmatch`. A non-string entry raises at
    match time inside the gate, far from the adapter that caused it, so the message
    has to name which of the two lists was wrong."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            standing_doc_provenance:
              {key}:
                - docs/*.md
                - 7
            """
        ),
    )
    assert not payload["valid"]
    assert (
        f"standing_doc_provenance.{key} must be a list of strings" in payload["errors"]
    )
    # The whole list is refused, not partially merged: a half-applied allowlist
    # would silently narrow or widen what the gate inspects.
    assert (
        payload["data"]["standing_doc_provenance"][key]
        == DEFAULT_STANDING_DOC_PROVENANCE[key]
    )


def test_standing_doc_provenance_glob_list_rejects_a_bare_scalar(tmp_path: Path) -> None:
    """`standing_docs: docs/*.md` (no `-`) is the likeliest hand-edit.
    A bare string is iterable, so without the list check it would degrade into a
    per-character glob list rather than failing."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            standing_doc_provenance:
              standing_docs: docs/*.md
            """
        ),
    )
    assert not payload["valid"]
    assert (
        "standing_doc_provenance.standing_docs must be a list of strings"
        in payload["errors"]
    )
    assert payload["data"]["standing_doc_provenance"]["standing_docs"] == []


@pytest.mark.parametrize("bad", ['""', "3"])
def test_standing_doc_provenance_empty_or_non_string_marker_is_rejected(
    tmp_path: Path, bad: str
) -> None:
    """`inline_allow_marker` is the per-line escape hatch, matched as a substring.
    An empty string matches every line, which would disable the gate everywhere
    while the adapter still reads as configured — so empty is refused as hard as a
    wrong type, and both share one message."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            standing_doc_provenance:
              inline_allow_marker: {bad}
            """
        ),
    )
    assert not payload["valid"]
    assert (
        "standing_doc_provenance.inline_allow_marker must be a non-empty string"
        in payload["errors"]
    )
    assert (
        payload["data"]["standing_doc_provenance"]["inline_allow_marker"]
        == DEFAULT_STANDING_DOC_PROVENANCE["inline_allow_marker"]
    )


# ---------------------------------------------------------------------------
# changed_line_mutation_gate
#
# Near-identical to the block above by construction. That duplication is the
# recurrence surface #453's critique named: whoever consolidates the two helpers
# moves both sets of messages out from under their tests at once.


def test_changed_line_mutation_gate_scalar_block_is_rejected(tmp_path: Path) -> None:
    """Same shape failure as its sibling block, and it must fail the same way —
    by name, not by traceback."""
    payload = _resolve(tmp_path, "changed_line_mutation_gate: reports/coverage.json\n")
    assert not payload["valid"]
    assert "changed_line_mutation_gate must be a mapping" in payload["errors"]
    # Same honest scope as its sibling above.
    assert (
        payload["data"]["changed_line_mutation_gate"]
        == DEFAULT_CHANGED_LINE_MUTATION_GATE
    )


def test_changed_line_mutation_gate_unknown_subkey_warns_without_blocking(
    tmp_path: Path,
) -> None:
    """`eligible_glob` (singular) leaves `eligible_globs` empty, which makes the
    gate inert — the exact fail-open shape this repo keeps re-filing. The warning
    names the key so the typo is visible in the run output, and the known key that
    follows it must still apply (see the sibling test: skip must be `continue`)."""
    payload = _resolve(
        tmp_path,
        dedent(
            """\
            changed_line_mutation_gate:
              eligible_glob: ["scripts/*.py"]
              coverage_json: reports/keep-me.json
            """
        ),
    )
    assert payload["valid"], payload["errors"]
    assert (
        "unknown changed_line_mutation_gate sub-key: eligible_glob"
        in payload["warnings"]
    )
    assert payload["data"]["changed_line_mutation_gate"]["eligible_globs"] == []
    assert (
        payload["data"]["changed_line_mutation_gate"]["coverage_json"]
        == "reports/keep-me.json"
    )


@pytest.mark.parametrize("key", ["eligible_globs", "exclude_globs"])
def test_changed_line_mutation_gate_glob_list_rejects_non_strings_by_name(
    tmp_path: Path, key: str
) -> None:
    """The two glob lists have opposite effects — one selects what the gate guards,
    the other carves holes in it — so a message that named the wrong one would send
    the operator to the wrong line of the adapter."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            changed_line_mutation_gate:
              {key}:
                - scripts/*.py
                - 7
            """
        ),
    )
    assert not payload["valid"]
    assert (
        f"changed_line_mutation_gate.{key} must be a list of strings"
        in payload["errors"]
    )
    assert (
        payload["data"]["changed_line_mutation_gate"][key]
        == DEFAULT_CHANGED_LINE_MUTATION_GATE[key]
    )


@pytest.mark.parametrize("bad", ['""', "3"])
def test_changed_line_mutation_gate_empty_or_non_string_coverage_json_is_rejected(
    tmp_path: Path, bad: str
) -> None:
    """`coverage_json` is joined onto the repo root to find the coverage report.
    An empty string resolves to the repo root itself — a directory, which the gate
    would report as a missing/unreadable report and then skip. Refusing it here
    keeps that skip from being reachable by config."""
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            changed_line_mutation_gate:
              coverage_json: {bad}
            """
        ),
    )
    assert not payload["valid"]
    assert (
        "changed_line_mutation_gate.coverage_json must be a non-empty string"
        in payload["errors"]
    )
    assert (
        payload["data"]["changed_line_mutation_gate"]["coverage_json"]
        == DEFAULT_CHANGED_LINE_MUTATION_GATE["coverage_json"]
    )


# ---------------------------------------------------------------------------
# skill_ergonomics_gate_rules


@pytest.mark.parametrize("bad", ['""', "7"])
def test_skill_ergonomics_gate_rules_entry_must_be_a_non_empty_string(
    tmp_path: Path, bad: str
) -> None:
    """Rule entries are looked up against the known-rule set. An empty or non-string
    entry can never match a rule, so without this check it would merge as a rule
    that silently does nothing — and the operator would read the adapter as
    enabling one more check than it does."""
    valid_rule = sorted(VALID_SKILL_ERGONOMICS_GATE_RULES)[0]
    payload = _resolve(
        tmp_path,
        dedent(
            f"""\
            skill_ergonomics_gate_rules:
              - {valid_rule}
              - {bad}
            """
        ),
    )
    assert not payload["valid"]
    assert (
        "skill_ergonomics_gate_rules entries must be non-empty strings"
        in payload["errors"]
    )
    # One error, not two: the entry is abandoned here rather than falling through to
    # the known-rule lookup, which would also reject it and hand the operator a
    # second, misleading "unknown rule `7`" for the same line of adapter.
    assert not any("contains unknown rule" in e for e in payload["errors"]), payload["errors"]
    # The unusable entry is dropped while the valid rule survives: the failure is
    # per-entry, not all-or-nothing.
    assert payload["data"]["skill_ergonomics_gate_rules"] == [valid_rule]
