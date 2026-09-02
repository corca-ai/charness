"""Pins for the narrative-containment lint.

The rule under test: a release note's AUTHORED prose may not carry a quantity
nothing derived. The recorded sentence it exists for is *"twelve public skill
scripts still declare one"*, written over a measured zero — which is why
`twelve` (a word, not a digit) is asserted here. A digit-only rule reads that
sentence and finds nothing.

TWO SEVERITIES, and the split is what a bounded review forced. Measured against
this repo's own release note, a single-severity rule produced 49 findings and
refused honest-limits language like "verified only after the release has been
published". So quantities BLOCK and completeness words are ADVISORY, and both
sides of that line are pinned below — including that an advisory alone does not
fail the command, because a rule an author cannot get to zero is one they learn
to ignore.

Each exemption is tested as well as each refusal. An exemption is a hole in the
rule, and an untested hole is one nobody can see widen.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.script_loader import load_script_module

from .support import ROOT

LINT = load_script_module(
    "lint_release_narrative_under_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "lint_release_narrative.py",
)


def _kinds(text: str, versions: tuple[str, ...] = ()) -> list[str]:
    return [finding["kind"] for finding in LINT.lint_text(text, versions=versions)]


def _tokens(text: str, versions: tuple[str, ...] = ()) -> list[str]:
    return [finding["token"] for finding in LINT.lint_text(text, versions=versions)]


def _severities(text: str, versions: tuple[str, ...] = ()) -> list[str]:
    return [finding["severity"] for finding in LINT.lint_text(text, versions=versions)]


def test_the_recorded_false_sentence_is_refused() -> None:
    """Verbatim from the prepared notes, including the trailing `one`.

    `one` is the word the blocking arm deliberately omits, so this sentence is
    caught by `twelve` and not by `one` — which is exactly why the number-word
    arm has to exist at all."""
    sentence = "twelve public skill scripts still declare one, and that is the convention.\n"

    findings = LINT.lint_text(sentence)

    assert [(f["token"].lower(), f["kind"], f["severity"]) for f in findings] == [
        ("twelve", "bare-quantity", "blocking"),
        ("still", "bare-completeness-word", "advisory"),
    ]
    assert [f["token"] for f in LINT.blocking(findings)] == ["twelve"]


def test_a_bare_digit_in_prose_blocks() -> None:
    assert _kinds("We removed 27 hidden aliases.\n") == ["bare-quantity"]
    assert _severities("We removed 27 hidden aliases.\n") == ["blocking"]


@pytest.mark.parametrize("word", ["only", "all", "every", "none", "still", "repo-wide"])
def test_each_listed_completeness_word_is_advisory_not_blocking(word: str) -> None:
    findings = LINT.lint_text(f"The flag is {word} gone from the tree.\n")

    assert [f["kind"] for f in findings] == ["bare-completeness-word"]
    assert LINT.blocking(findings) == []


def test_honest_limits_language_does_not_block() -> None:
    """The sentence the first version of this rule refused.

    Verbatim from this repo's own 6.0.0 notes, `## Evidence limits`. A rule that
    refuses the wording which makes a note honest is a rule that gets disabled,
    and its disabling takes the arm that works with it."""
    sentence = (
        "Public release visibility and installed-host readback are verified only after\n"
        "the release has been published, through their distinct channels.\n"
    )

    assert LINT.blocking(LINT.lint_text(sentence)) == []


def test_the_same_quantity_inside_a_claim_marker_is_accepted() -> None:
    """The remedy has to pass, or the rule is one an author routes around."""
    assert LINT.lint_text("Scripts declaring it: {{claim:json-declaring-scripts.count=0}}.\n") == []


def test_a_number_inside_a_code_span_or_fence_is_accepted() -> None:
    """Paths, flags, and line citations are identifiers, not claims."""
    assert LINT.lint_text("See `scripts/gates/check_docs_graph.py:52` for the gated set.\n") == []
    assert LINT.lint_text("```yaml\ncount: 27\nquantifier: only\n```\n") == []


def test_html_comments_and_link_targets_and_urls_are_accepted() -> None:
    assert LINT.lint_text("<!-- 27 of them, and all still open -->\n") == []
    assert LINT.lint_text("Read the [notes](../release/2026-08-14-v6.0.0-notes.md) first.\n") == []
    assert LINT.lint_text("See https://github.com/corca-ai/charness/issues/599 for the report.\n") == []


def test_an_iso_date_and_an_ordered_list_marker_are_accepted() -> None:
    assert LINT.lint_text("Measured on 2026-08-15 against the shipped tree.\n") == []
    assert LINT.lint_text("1. Run the updater.\n2. Restart the host.\n") == []


def test_the_release_version_is_accepted_only_when_the_caller_names_it() -> None:
    """A general version-shaped exemption would also swallow `we measured 3.1.4
    seconds`, so the exemption is the caller's declared version and nothing else."""
    assert LINT.lint_text("# Charness 6.0.0\n", versions=("v6.0.0",)) == []
    # Only the leading run: a digit preceded by `.` is part of a larger token,
    # not a free-standing count. Enough to fail the line, without three findings
    # for one version.
    assert _tokens("# Charness 6.0.0\n") == ["6"]
    assert _tokens("The probe took 3.1.4 seconds.\n", versions=("v6.0.0",)) == ["3"]


def test_a_rollback_paragraph_passes_when_the_prior_version_is_supplied() -> None:
    """Every release note with a rollback path names the version it returns to.

    The publish gate reads that version from the packaging manifest rather than
    leaving it to the author, because a rule that refuses every rollback
    paragraph is one nobody keeps."""
    text = "To return to 5.2.0, reinstall the prior release.\n"

    assert _tokens(text, versions=("v6.0.0",)) == ["5"]
    assert LINT.lint_text(text, versions=("v6.0.0", "5.2.0")) == []


def test_exit_codes_and_tracker_references_are_not_quantities() -> None:
    """Both were false refusals measured against this repo's own note.

    An exit code names a program state and a hash-prefixed number names an
    issue; neither measures the tree. `exit-3` is spelled with a hyphen in the
    real note, which the first whitespace-only rule missed."""
    assert LINT.lint_text("The probe now exits 3 when the answer is undetermined.\n") == []
    assert LINT.lint_text("The exit-3 repair does not bind on any production path.\n") == []
    assert LINT.lint_text("Reported as #618 and fixed in this release.\n") == []


def test_a_digit_welded_to_a_word_is_an_identifier_not_a_count() -> None:
    """`H2` reported `2` as a quantity claim before the lookarounds existed."""
    assert LINT.lint_text("Any adapter block whose H2 matches a scaffold heading is dropped.\n") == []


def test_the_finding_names_the_line_and_the_token() -> None:
    findings = LINT.lint_text("# Notes\n\nEverything is fine.\n\nAll 27 of them shipped.\n")

    # Ordered by column, so an author reads them left to right along the line.
    assert [(finding["line"], finding["column"], finding["token"]) for finding in findings] == [
        (5, 1, "All"),
        (5, 5, "27"),
    ]


def test_one_is_deliberately_not_refused() -> None:
    """The stated hole, pinned so it is a decision rather than an oversight.

    `one of`, `no one`, and `one another` are structural English. Refusing them
    produces a lint an author disables, and a disabled lint contains nothing."""
    assert LINT.lint_text("This is one of the reasons the gate exists.\n") == []


def test_an_unbalanced_fence_is_reported_rather_than_swallowing_the_rest(tmp_path: Path) -> None:
    """The escape a non-greedy fence regex opened.

    An opening fence that is never closed used to pair with the next
    backticks-only line further down the file, blanking everything between —
    including the exact sentence this rule exists to refuse. It is now a
    blocking finding, the same decision the derived block makes for an
    unterminated block marker."""
    del tmp_path
    text = (
        "# Notes\n\n```\na snippet nobody closed\n\n"
        "twelve public skill scripts still declare one.\n\n"
        "```yaml\ncount: 0\n```\n"
    )

    findings = LINT.lint_text(text)
    kinds = [finding["kind"] for finding in findings]

    assert "unbalanced-code-fence" in kinds
    assert "bare-quantity" in kinds
    assert any(finding["token"].lower() == "twelve" for finding in findings)


def test_a_tilde_fence_masks_like_a_backtick_fence() -> None:
    """The sibling audit in this skill handles `~~~`; this rule now agrees.

    Two fence models in one skill meant a note fenced with tildes was masked by
    one and scanned by the other."""
    assert LINT.lint_text("~~~yaml\ncount: 27\nquantifier: only\n~~~\n") == []


def test_an_unreadable_notes_file_is_a_finding_rather_than_a_traceback(tmp_path: Path) -> None:
    assert [finding["kind"] for finding in LINT.lint_file(tmp_path / "gone.md")] == ["notes-unreadable"]


def test_a_non_utf8_notes_file_is_a_finding_rather_than_a_traceback(tmp_path: Path) -> None:
    """`UnicodeDecodeError` is a `ValueError`, not an `OSError`.

    Catching `OSError` alone let it traceback out of the one function whose
    whole contract is to return a finding instead."""
    notes = tmp_path / "notes.md"
    notes.write_bytes(b"\xff\xfe# Notes\n")

    assert [finding["kind"] for finding in LINT.lint_file(notes)] == ["notes-unreadable"]


def test_lint_file_reads_a_clean_note(tmp_path: Path) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text("# Release\n\nThe updater refreshes the install.\n", encoding="utf-8")

    assert LINT.lint_file(notes) == []


def test_a_hyphenated_compound_number_blocks() -> None:
    """Every cardinal from 21 to 99 is hyphenated in English.

    A hyphen in the word lookarounds made both halves fail, so "twenty-seven
    public skill scripts still declare one" passed the blocking arm clean — the
    recorded sentence, one hyphen away."""
    findings = LINT.blocking(LINT.lint_text("twenty-seven public skill scripts still declare one.\n"))

    assert [finding["token"].lower() for finding in findings] == ["twenty", "seven"]


def test_a_numeric_range_blocks() -> None:
    """Same root cause on the digit arm: `12-15` matched nothing."""
    assert [f["token"] for f in LINT.blocking(LINT.lint_text("We removed 12-15 hidden aliases.\n"))] == ["12", "15"]


def test_zero_blocks() -> None:
    """The recorded failure's TRUE value was zero, which makes "zero scripts
    declare it" a likely sentence and an ungrounded claim like any other."""
    assert [f["token"] for f in LINT.blocking(LINT.lint_text("zero scripts declare it.\n"))] == ["zero"]


def test_a_legitimate_nested_fence_is_not_reported_as_mis_paired() -> None:
    """A note showing an example claim block wraps it in a LONGER fence.

    Ignoring fence length closed the outer run three lines early, reported a
    correct note as unbalanced, and then flagged every digit in the example —
    refusing a correct publish with no remedy but deleting the example."""
    text = (
        "# Notes\n\n````markdown\n<!-- claim-surface: public-skills -->\n\n"
        "```yaml\ncount: 4\n```\n````\n"
    )

    assert LINT.lint_text(text) == []


def test_a_generated_block_of_several_yaml_chunks_is_not_mis_paired() -> None:
    """The derived block emits one ```yaml chunk per surface, back to back."""
    text = "# Notes\n\n" + "\n\n".join("```yaml\ncount: 1\n```" for _ in range(4)) + "\n"

    assert LINT.lint_text(text) == []


def test_the_exit_code_exemption_does_not_span_a_line_break() -> None:
    """`\\s` matched a newline, so a hard-wrapped note ending in "exits" blanked
    the count that opened the next line."""
    findings = LINT.blocking(LINT.lint_text("The probe exits\n27 scripts were removed.\n"))

    assert [finding["token"] for finding in findings] == ["27"]
