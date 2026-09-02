from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.evidence import probe_record_lib
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gates" / "check_probe_record.py"

# The source every record in this module quotes from, so `verify_source_quote` has
# something real to read. Written into `tmp_path`, never into the repo.
SOURCE_BODY = """\
def resolve(payload):
    # A refused version means nothing the repo declared was honored.
    if payload["errors"]:
        raise SystemExit("refusing: the adapter version was not reconciled")
    return payload["value"]
"""
QUOTED = '        raise SystemExit("refusing: the adapter version was not reconciled")'


SECTION_KEYS = ("source_text", "stimulus", "base_observable", "head_observable")


def _record(**overrides: str) -> str:
    """A complete, measured record. Each test names ONLY the field it is about, so a
    later required-field addition fails every test loudly instead of silently changing
    what any one of them proves."""
    fields = {
        "claim": "the loader refuses instead of returning a charness default",
        "claim_kind": "change",
        "observable": "the process exit status of the resolve call",
        "source_ref": "adapter.py",
        "source_conditions": "the adapter declares a version the reader cannot speak",
        "base_ref": "aaaaaaa",
        "head_ref": "bbbbbbb",
        "base_arm": "base-observed",
        "call_sites_unproven": "none",
    }
    sections = {
        "source_text": QUOTED,
        "stimulus": "python3 -c 'resolve({\"errors\": [\"unknown version\"]})'",
        "base_observable": "exit 0 (returned the charness default)",
        "head_observable": "exit 1 (SystemExit: refusing)",
    }
    for key, value in overrides.items():
        target = sections if key in SECTION_KEYS else fields
        target[key] = value
    body = "# Probe Record: test\n\n"
    body += "".join(f"{name.replace('_', ' ').capitalize()}: {value}\n" for name, value in fields.items())
    for key, content in sections.items():
        body += f"\n## {key.replace('_', ' ').capitalize()}\n\n```\n{content}\n```\n"
    return body


def _resolve(text: str, tmp_path: Path) -> dict:
    (tmp_path / "adapter.py").write_text(SOURCE_BODY, encoding="utf-8")
    return probe_record_lib.resolve_probe_record_text(text, repo_root=tmp_path)


def _reasons(result: dict) -> str:
    return " | ".join(result["undetermined_reasons"])


# --- the measured case ------------------------------------------------------


def test_a_measured_record_is_evaluated(tmp_path: Path) -> None:
    result = _resolve(_record(), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)
    assert result["supports_claim"] is True
    assert result["undetermined_reasons"] == []
    assert result["source_quote"]["status"] == "verified"
    assert result["covers_all_call_sites"] is True


# --- the whole point: a probe that measured nothing says so -----------------


def test_base_equals_head_measured_nothing(tmp_path: Path) -> None:
    same = "exit 1 (SystemExit: refusing)"
    result = _resolve(_record(base_observable=same, head_observable=same), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["supports_claim"] is False
    assert "measured nothing" in _reasons(result)


def test_base_equals_head_ignores_indentation_only_differences(tmp_path: Path) -> None:
    # Formatting is not a behavior change. A record that reflowed one capture and not the
    # other must not read as a disagreement.
    result = _resolve(
        _record(base_observable="  exit 1 (refusing)", head_observable="exit 1 (refusing)  "),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "measured nothing" in _reasons(result)


def test_a_base_that_could_not_run_is_not_a_base_that_disagreed(tmp_path: Path) -> None:
    # The sharpest rule in the module, and the `#528` shape: base and head DO differ
    # here -- base "differs" only because it crashed for an unrelated reason.
    result = _resolve(
        _record(base_arm="base-unrunnable", base_observable="ImportError: no module named x"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "not a base that disagreed" in _reasons(result)


# --- the arms Open Question 1 asked about -----------------------------------


def test_absent_base_establishes_an_existence_claim(tmp_path: Path) -> None:
    result = _resolve(
        _record(claim_kind="existence", base_arm="base-absent", base_observable="the surface does not exist at base"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)


def test_absent_base_does_not_establish_a_change_claim(tmp_path: Path) -> None:
    # The base capture must be SUBSTANTIVE, or the empty-capture check refuses first and
    # this test passes without ever reaching the branch it is named for.
    result = _resolve(
        _record(base_arm="base-absent", base_observable="the surface does not exist at base"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "no prior behavior" in _reasons(result)


def test_not_applicable_base_is_refused_for_a_behavioral_claim(tmp_path: Path) -> None:
    # The escape hatch: declare no base applies while still claiming a flip.
    result = _resolve(_record(base_arm="base-not-applicable"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "reserved for a `refusal` claim" in _reasons(result)


def test_unknown_base_arm_is_refused(tmp_path: Path) -> None:
    result = _resolve(_record(base_arm="base-obviously-fine"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "unknown base arm" in _reasons(result)


# --- a recorded refusal is not evidence of a repair -------------------------


def test_a_recorded_refusal_is_not_configured_not_evaluated(tmp_path: Path) -> None:
    result = _resolve(
        _record(claim_kind="refusal", base_arm="base-not-applicable", refusal_reason="no resolver contract exists for this adapter"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_CONFIGURED
    assert result["supports_claim"] is False
    assert "NOT evidence of a repair" in _reasons(result)


def test_a_refusal_without_a_reason_is_not_established(tmp_path: Path) -> None:
    result = _resolve(_record(claim_kind="refusal", base_arm="base-not-applicable"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`Refusal reason:`" in _reasons(result)


# --- stimulus provenance ----------------------------------------------------


def test_a_quote_absent_from_the_cited_source_is_refused(tmp_path: Path) -> None:
    # The `#528` countermeasure at its own level: a stimulus invented from a model of the
    # mechanism cannot be quoted from the source that defines it.
    result = _resolve(_record(source_text="deliberately_absent:\n  - some-key"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["source_quote"]["status"] == "absent"
    assert "provenance is unverified" in _reasons(result)


def test_a_nonlocal_source_needs_a_degraded_reason(tmp_path: Path) -> None:
    result = _resolve(_record(source_ref="#628"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["source_quote"]["status"] == "unresolvable"
    assert "Source degraded reason" in _reasons(result)


def test_a_nonlocal_source_with_a_degraded_reason_still_evaluates(tmp_path: Path) -> None:
    # An issue body is allowed provenance and cannot be read from here. Demoting every
    # issue-sourced probe would make the mechanism unusable at the boundary it is for.
    result = _resolve(
        _record(source_ref="#628", source_degraded_reason="the issue body is not readable from this repo; quoted from the GitHub UI on 2026-08-18"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)
    assert result["source_quote"]["status"] == "unresolvable"


def test_base_observed_with_no_captured_reading_is_refused(tmp_path: Path) -> None:
    # "I measured both sides" with an empty capture is this goal's class in miniature:
    # the arm ASSERTS a measurement the record does not contain.
    result = _resolve(_record(base_observable=""), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "owes a `Base observable` section" in _reasons(result)


def test_base_observed_with_no_head_reading_is_refused(tmp_path: Path) -> None:
    result = _resolve(_record(head_observable=""), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "no captured observable is not populated" in _reasons(result)


def test_a_source_ref_that_names_no_path_is_unresolvable(tmp_path: Path) -> None:
    result = probe_record_lib.verify_source_quote(tmp_path, "the loader docstring", QUOTED)
    assert result["status"] == "unresolvable"
    assert "does not name a readable path" in result["reason"]


def test_an_empty_quote_is_unresolvable_never_verified(tmp_path: Path) -> None:
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", "   ")
    assert result["status"] == "unresolvable"


def _git_repo_with_source(tmp_path: Path) -> str:
    """A repo whose committed `adapter.py` carries `QUOTED` and whose WORKTREE no longer
    does -- the living-document rot the pin exists for."""
    from scripts.core.git_checkout import head_oid_from_files
    from tests.quality_gates.repo_shapes import install_committed_repo

    install_committed_repo(tmp_path, {"adapter.py": SOURCE_BODY})
    sha = head_oid_from_files(tmp_path)
    assert sha is not None
    (tmp_path / "adapter.py").write_text("def resolve(payload):\n    return payload\n", encoding="utf-8")
    return sha


def test_an_unpinned_quote_rots_when_the_source_is_edited(tmp_path: Path) -> None:
    _git_repo_with_source(tmp_path)
    assert probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED)["status"] == "absent"


def test_a_pinned_quote_survives_the_edit(tmp_path: Path) -> None:
    sha = _git_repo_with_source(tmp_path)
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED, revision=sha)
    assert result["status"] == "verified", result["reason"]


def test_a_record_may_pin_its_source_revision(tmp_path: Path) -> None:
    sha = _git_repo_with_source(tmp_path)
    text = _record(source_revision=sha)
    result = probe_record_lib.resolve_probe_record_text(text, repo_root=tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)


def test_an_unresolvable_pin_is_unresolvable_not_verified(tmp_path: Path) -> None:
    _git_repo_with_source(tmp_path)
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED, revision="deadbee")
    assert result["status"] == "unresolvable"
    assert "revision" in result["reason"]


def test_dedent_of_an_empty_block_is_empty() -> None:
    # `min()` over no lines raises, and a window can be empty when the needle is longer
    # than the haystack.
    assert probe_record_lib._dedent([]) == []


def test_an_empty_needle_never_reports_containment() -> None:
    # Without this guard an empty quote matches every source by the empty-slice identity,
    # so "verified" would be the verdict for having quoted nothing.
    assert probe_record_lib._contains_block(["a", "b"], []) is False


def test_a_missing_source_file_is_unresolvable_not_a_crash(tmp_path: Path) -> None:
    result = _resolve(_record(source_ref="no_such_file.py"), tmp_path)
    assert result["source_quote"]["status"] == "unresolvable"
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED


# --- completeness -----------------------------------------------------------


def test_a_missing_required_field_is_refused_before_the_arm_is_read(tmp_path: Path) -> None:
    text = _record().replace("Observable: the process exit status of the resolve call\n", "")
    result = _resolve(text, tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`observable`" in _reasons(result)


def test_call_sites_unproven_may_not_be_silent(tmp_path: Path) -> None:
    # The census's own blind class replicated per row: a file flipped on one guarded call
    # site while a second still substitutes a default.
    text = _record().replace("Call sites unproven: none\n", "")
    result = _resolve(text, tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`call_sites_unproven`" in _reasons(result)


def test_named_unproven_call_sites_block_the_claim(tmp_path: Path) -> None:
    # The STATE assertion is the point and it was missing: the two reporting keys below
    # were already true before the repair, so the whole `reasons.append` could be deleted
    # with all 59 tests still green -- a verdict change on a proof surface that the suite
    # could not see. This is the third 2026-08-18 refutation's countermeasure; it is pinned
    # here or it is not pinned.
    result = _resolve(_record(call_sites_unproven="adapter.py:41 reads the payload through a helper"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "remain unproven" in _reasons(result)
    assert result["covers_all_call_sites"] is False
    assert result["call_sites_unproven"].startswith("adapter.py:41")


def test_none_with_a_reason_still_means_full_coverage(tmp_path: Path) -> None:
    # The markdown gate wraps long lines and a bare `none` loses the reason, so an author
    # writing the better answer must not be told they covered less.
    result = _resolve(_record(call_sites_unproven="none — the wait loop has exactly one call site"), tmp_path)
    assert result["covers_all_call_sites"] is True


def test_none_as_a_negation_is_not_full_coverage(tmp_path: Path) -> None:
    # The trap the anchored grammar exists for: `none of the call sites were checked`
    # says the OPPOSITE and shares its leading word.
    result = _resolve(_record(call_sites_unproven="none of the call sites were checked"), tmp_path)
    assert result["covers_all_call_sites"] is False


def test_a_wrapped_field_value_keeps_its_continuation(tmp_path: Path) -> None:
    # `line-anchored-ledger-fields`: a parser anchored on line starts drops the tail of a
    # value the markdown gate forced to wrap, and reports the truncation as a pass.
    parsed = probe_record_lib.parse_probe_record(
        "Claim: the loader refuses instead of returning a\n  charness default\n"
    )
    assert parsed["fields"]["claim"] == "the loader refuses instead of returning a charness default"


def test_an_unindented_following_line_is_not_a_continuation() -> None:
    parsed = probe_record_lib.parse_probe_record("Claim: the real claim\nsome other prose\n")
    assert parsed["fields"]["claim"] == "the real claim"


def test_a_blank_line_ends_a_wrapped_value() -> None:
    parsed = probe_record_lib.parse_probe_record("Claim: the real claim\n\n  indented prose\n")
    assert parsed["fields"]["claim"] == "the real claim"


# --- repairs from the slice-1 bounded review -------------------------------
# Each of these was MEASURED resolving `evaluated` before the repair, not reasoned about.


def test_absent_base_with_no_captured_reading_is_refused(tmp_path: Path) -> None:
    # The two-word bypass: relabel a change claim as an existence claim on an absent base
    # and the entire base/HEAD bar -- the actual `#528` countermeasure -- was skipped,
    # because only `base-observed` checked that the captures existed.
    text = _record(claim_kind="existence", base_arm="base-absent")
    text = text.split("\n## Base observable")[0] + "\n"
    assert "Head observable" not in text
    result = _resolve(text, tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "no captured observable is not populated" in _reasons(result)


def test_a_mistyped_local_path_may_not_be_excused_as_degraded(tmp_path: Path) -> None:
    # The escape hatch that was cheaper than fixing the quote: a fabricated quote is
    # refused, but a fabricated quote plus one dropped letter in the path was accepted.
    result = _resolve(
        _record(source_ref="adapterTYPO.py", source_degraded_reason="quoted from the file as of today"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "does not cover this" in _reasons(result)


def test_a_bad_revision_pin_may_not_be_excused_as_degraded(tmp_path: Path) -> None:
    _git_repo_with_source(tmp_path)
    result = probe_record_lib.resolve_probe_record_text(
        _record(source_revision="deadbee", source_degraded_reason="pinned to the pre-fix tree"),
        repo_root=tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "does not cover this" in _reasons(result)


def test_a_source_outside_the_repo_is_never_verified(tmp_path: Path) -> None:
    # Self-verifying provenance: a file the author wrote and no reviewer can open. The
    # containment check runs BEFORE any read, so this deliberately writes nothing outside
    # `tmp_path` -- an earlier version created a decorative file there and implied a
    # dependency the assertion does not have.
    inner = tmp_path / "repo"
    inner.mkdir()
    (tmp_path / "outside-notes.txt").write_text(SOURCE_BODY, encoding="utf-8")
    result = probe_record_lib.verify_source_quote(inner, "../outside-notes.txt", QUOTED)
    assert result["status"] == "unresolvable"
    assert "outside the repo" in result["reason"]
    assert result["local"] is True, "an outside-repo ref must be refused, never excused as degraded"


def test_an_extensionless_ref_is_not_excused_as_degraded(tmp_path: Path) -> None:
    # Round 2's blocker: the previous repair keyed `local` on the PATH GRAMMAR, which
    # requires a dot-extension -- so `adapterTYPO.py` was refused while `adapterTYPO` was
    # excused. Deleting three characters was cheaper than the typo the repair had just
    # closed. The repair shipped the class it repaired.
    result = _resolve(
        _record(source_ref="adapterTYPO", source_degraded_reason="quoted from the file as of today"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["source_quote"]["local"] is True
    assert "does not cover this" in _reasons(result)


def test_a_prose_source_ref_is_not_excused_as_degraded(tmp_path: Path) -> None:
    result = _resolve(
        _record(source_ref="the vocabulary docstring", source_degraded_reason="paraphrased"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED


def test_only_an_inherently_unreadable_source_opens_the_degraded_escape(tmp_path: Path) -> None:
    # The escape must stay OPEN for its real case, or the mechanism is unusable at the
    # boundary it exists for -- `#599`/`#628` provenance is a GitHub issue body.
    for ref in ("#628", "https://github.com/corca-ai/charness/issues/628", "issue #628"):
        result = probe_record_lib.verify_source_quote(tmp_path, ref, QUOTED)
        assert result["local"] is False, ref


def test_a_one_sided_arm_label_does_not_manufacture_a_disagreement(tmp_path: Path) -> None:
    # The asymmetric paste -- one transcript kept its arm banner line, the other retyped --
    # left `["", "exit 1"]` against `["exit 1"]`, unequal, on two identical readings.
    result = _resolve(
        _record(base_observable="exit 1 (refusing)", head_observable="head\nexit 1 (refusing)"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "measured nothing" in _reasons(result)


def test_an_unreadable_record_result_carries_the_full_shape(tmp_path: Path) -> None:
    # `_result` exists so no branch can omit a key a consumer branches on; a second,
    # hand-rolled construction of the same shape defeats exactly that, and the CLI's copy
    # had already drifted past two keys. Compared against a REAL result rather than
    # spot-checked, so a future key addition cannot skip this path either.
    unreadable = probe_record_lib.unreadable_record_result("could not read it")
    resolved = _resolve(_record(), tmp_path)
    assert set(unreadable) == set(resolved)
    assert set(unreadable["source_quote"]) == set(resolved["source_quote"])
    assert unreadable["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert unreadable["residual_judgment"] == []
    assert unreadable["source_quote"]["local"] is False


def test_a_flattened_quote_does_not_verify_against_a_nested_source(tmp_path: Path) -> None:
    # `#528`'s own mapping-vs-list confusion, which the first cut of this check passed.
    (tmp_path / "vocab.yaml").write_text(
        "deliberately_absent:\n  planner:\n    - some-key\n", encoding="utf-8"
    )
    flattened = "deliberately_absent:\nplanner:\n- some-key"
    assert probe_record_lib.verify_source_quote(tmp_path, "vocab.yaml", flattened)["status"] == "absent"


def test_a_correctly_nested_quote_still_verifies_when_the_record_indents_it(tmp_path: Path) -> None:
    # The other direction: markdown indents a quoted block wholesale and that is not a
    # structure change, so relative depth is what matters, never absolute column.
    (tmp_path / "vocab.yaml").write_text(
        "top:\ndeliberately_absent:\n  planner:\n    - some-key\n", encoding="utf-8"
    )
    indented = "    deliberately_absent:\n      planner:\n        - some-key"
    assert probe_record_lib.verify_source_quote(tmp_path, "vocab.yaml", indented)["status"] == "verified"


def test_captures_differing_only_by_an_arm_label_measured_nothing(tmp_path: Path) -> None:
    # The shape the first worked example taught, which would have made the base==head rule
    # unfalsifiable for every record copying it.
    result = _resolve(
        _record(base_observable="base  exit 1 (refusing)", head_observable="head  exit 1 (refusing)"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "measured nothing" in _reasons(result)


def test_a_duplicated_field_is_ambiguous_not_first_wins(tmp_path: Path) -> None:
    # A record whose intro DEMONSTRATES the format at column 0 used to resolve against the
    # example while a human read the real values below.
    result = _resolve("Claim: the example value\n" + _record(), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "more than once" in _reasons(result)


def test_an_indented_sublist_is_a_continuation_not_a_phantom_field() -> None:
    parsed = probe_record_lib.parse_probe_record(
        "Observable: the resolver status, one of\n  verified: the quote is present\n"
    )
    assert parsed["fields"]["observable"] == "the resolver status, one of verified: the quote is present"
    assert "verified" not in parsed["fields"]


def test_a_fence_with_a_multi_token_info_string_still_opens(tmp_path: Path) -> None:
    parsed = probe_record_lib.parse_probe_record(
        '## Stimulus\n\n```console session\nClaim: not a field\n```\n'
    )
    assert parsed["sections"]["stimulus"] == "Claim: not a field"
    assert "claim" not in parsed["fields"]


def test_a_four_backtick_fence_is_not_closed_by_an_inner_three(tmp_path: Path) -> None:
    # Quoting markdown that itself contains fences is exactly how this repo's most
    # quotable sources look, and a truncated quote is usually still a verifying prefix.
    parsed = probe_record_lib.parse_probe_record(
        "## Source text\n\n````\nline one\n```\nline two\n```\nline three\n````\n"
    )
    assert parsed["sections"]["source_text"] == "line one\n```\nline two\n```\nline three"


def test_two_fences_under_one_heading_are_both_kept(tmp_path: Path) -> None:
    parsed = probe_record_lib.parse_probe_record(
        "## Head observable\n\n```\nthe command\n```\n\n```\nthe output\n```\n"
    )
    assert parsed["sections"]["head_observable"] == "the command\nthe output"


def test_a_refusal_must_use_the_not_applicable_arm(tmp_path: Path) -> None:
    result = _resolve(
        _record(claim_kind="refusal", base_arm="banana", refusal_reason="no resolver contract exists"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "owes base arm" in _reasons(result)


def test_evaluated_carries_its_residual_judgment(tmp_path: Path) -> None:
    # `evaluated` is not a terminal green; the questions the mechanism cannot answer ride
    # along with the pass so the distinct observer is handed their agenda.
    result = _resolve(_record(), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED
    assert len(result["residual_judgment"]) == len(probe_record_lib.RESIDUAL_JUDGMENT)
    assert any("Source conditions" in line for line in result["residual_judgment"])


def test_a_refused_record_carries_no_residual_judgment(tmp_path: Path) -> None:
    result = _resolve(_record(base_arm="base-unrunnable"), tmp_path)
    assert result["residual_judgment"] == []


# --- holes that remain BY DESIGN, pinned as tests so slice 2 cannot forget them ---


def test_a_real_quote_with_a_contradicting_stimulus_still_evaluates(tmp_path: Path) -> None:
    # The `#528` author quotes a REAL line from the source that defines the claim and then
    # writes an invented stimulus. Nothing compares the two. This is the documented limit
    # of `verify_source_quote`, pinned here rather than left as prose, because the first
    # docstring claimed the opposite and its test encoded the same wrong model.
    result = _resolve(_record(stimulus="deliberately_absent:\n  - some-key   # invented shape"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)
    assert result["source_quote"]["status"] == "verified"


def test_source_conditions_is_compared_to_nothing(tmp_path: Path) -> None:
    # The `#628` countermeasure is presence-only. A stimulus that flatly contradicts the
    # stated conditions still evaluates; only a reader catches it.
    result = _resolve(
        _record(
            source_conditions="the scaffold run with NO arguments",
            stimulus="charness quality scaffold --title 'a different cohort'",
        ),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)


def test_a_placeholder_value_is_silence(tmp_path: Path) -> None:
    result = _resolve(_record(observable="TBD"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`observable`" in _reasons(result)


def test_an_unknown_claim_kind_is_refused(tmp_path: Path) -> None:
    result = _resolve(_record(claim_kind="probably-fine"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "unknown claim kind" in _reasons(result)


# --- parsing ----------------------------------------------------------------


def test_a_field_line_inside_a_fence_is_content_not_a_field(tmp_path: Path) -> None:
    # A stimulus that itself contains `Claim:` must not overwrite the record's claim.
    parsed = probe_record_lib.parse_probe_record(
        "Claim: the real claim\n\n## Stimulus\n\n```\nClaim: not a field\n```\n"
    )
    assert parsed["fields"]["claim"] == "the real claim"
    assert parsed["sections"]["stimulus"] == "Claim: not a field"


def test_a_heading_with_no_fence_is_an_empty_section_not_a_missing_one(tmp_path: Path) -> None:
    parsed = probe_record_lib.parse_probe_record("## Source text\n\n## Stimulus\n\n```\nrun it\n```\n")
    assert parsed["sections"]["source_text"] == ""
    assert parsed["sections"]["stimulus"] == "run it"


# --- the shipped exemplar ---------------------------------------------------


def test_the_shipped_probe_record_resolves_evaluated() -> None:
    """The repo's worked example is checked by the suite, not only by hand.

    It resolves through `git show 1b49a1ae0:docs/handoff.md`, so this also covers the
    pinned-revision path against real history. Every later record is written by copying
    this one; an exemplar that quietly stopped resolving would teach the wrong shape to
    all of them.
    """
    record = ROOT / "charness-artifacts" / "probe" / "2026-08-18-standing-lane-flake-bar.md"
    result = probe_record_lib.resolve_probe_record_text(
        record.read_text(encoding="utf-8"), repo_root=ROOT
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, result["undetermined_reasons"]
    assert result["source_quote"]["status"] == "verified"
    assert result["covers_all_call_sites"] is True


# --- the command surface ----------------------------------------------------


def _cli(tmp_path: Path, text: str, *args: str) -> subprocess.CompletedProcess:
    (tmp_path / "adapter.py").write_text(SOURCE_BODY, encoding="utf-8")
    record = tmp_path / "record.md"
    record.write_text(text, encoding="utf-8")
    return run_script(str(CLI), "--repo-root", str(tmp_path), "--record", str(record), *args)


def test_cli_reports_without_gating_by_default(tmp_path: Path) -> None:
    same = "exit 1"
    result = _cli(tmp_path, _record(base_observable=same, head_observable=same))
    assert result.returncode == 0, result.stderr
    assert "not-established" in result.stdout


def test_cli_require_evaluated_refuses_an_unmeasured_claim(tmp_path: Path) -> None:
    same = "exit 1"
    result = _cli(tmp_path, _record(base_observable=same, head_observable=same), "--require-evaluated")
    assert result.returncode == 1
    assert "does not establish the claim" in result.stderr


def test_cli_require_evaluated_accepts_a_measured_claim(tmp_path: Path) -> None:
    result = _cli(tmp_path, _record(), "--require-evaluated")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "state: evaluated" in result.stdout


def test_cli_require_evaluated_refuses_a_recorded_refusal(tmp_path: Path) -> None:
    # `not-configured` is an honest state and still not support for a close.
    result = _cli(
        tmp_path,
        _record(claim_kind="refusal", base_arm="base-not-applicable", refusal_reason="cannot be wired: no resolver contract"),
        "--require-evaluated",
    )
    assert result.returncode == 1
    assert "not-configured" in result.stdout


def test_cli_reports_an_unreadable_record_rather_than_crashing(tmp_path: Path) -> None:
    result = run_script(
        str(CLI), "--repo-root", str(tmp_path), "--record", str(tmp_path / "absent.md")
    )
    assert result.returncode == 0
    assert "not-established" in result.stdout
    assert "could not read the probe record" in result.stdout
    assert "Traceback" not in result.stderr
