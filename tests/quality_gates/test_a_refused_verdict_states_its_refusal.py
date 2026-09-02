"""Sweep rows S23 and S2: two singletons where a verdict outlived the check behind it.

S23 — a confirmation sentence built under an `if ok` guard, then a later fold flipping
`ok` to False without touching the sentence, so a refused verdict shipped a rendered
confirmation. S2 — an odd number of single backticks leaving one span open at end of
file, silently dropped, which shifts every pair after the stray one and lets a genuinely
wrapped span report clean.

They share no code. They are one file because they are one question: does the thing that
SAYS the verdict still agree with the thing that DECIDED it?

Each test names the pre-repair verdict it pins against, observed in the parent on
2026-08-01 before any repair was written.
"""
from __future__ import annotations

from .support import ROOT, _load_script_module

VERIFY = _load_script_module(
    "issue_verify_closeout_under_test",
    ROOT / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py",
)
INLINE = _load_script_module(
    "check_markdown_inline_code_under_test",
    ROOT / "scripts" / "gates" / "check_markdown_inline_code.py",
)

_LEDGER_GAP = """Close #123

## Proof Ledger

| Acceptance | Proof | Disposition |
| --- | --- | --- |
| the gate refuses a malformed adapter | not run |  |
"""


def _pre_fold_result() -> dict:
    """A result exactly as `verify_closeout` builds it before the fold: every pre-fold
    check passed, so the `if ok` guard rendered the confirmation line."""
    return {
        "ok": True,
        "status": "carrier_verified",
        "confirmation": {
            "observer": "issue_verify_closeout@gh",
            "channel": "carrier-body-checks",
            "scope": "carrier-checks-only",
            "line": "carrier-checked: issue_verify_closeout@gh via carrier-body-checks (carrier-checks-only)",
        },
    }


def test_s23_a_refused_verdict_drops_its_confirmation_line(tmp_path):
    # Pre-repair: ok=False, status='failed', and confirmation.line still read
    # "carrier-checked: issue_verify_closeout@gh via carrier-body-checks
    # (carrier-checks-only)". The `if ok` guard runs BEFORE the fold; the fold flips the
    # verdict afterward. This is why the row's REFUTE prediction was wrong.
    result = _pre_fold_result()

    VERIFY._fold_proof_mismatch(result, tmp_path, _LEDGER_GAP)

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["confirmation"]["line"] is None


def test_s23_a_body_with_no_proof_ledger_keeps_its_confirmation(tmp_path):
    # The fold is inert without a ledger, so nothing may change here.
    result = _pre_fold_result()

    VERIFY._fold_proof_mismatch(result, tmp_path, "Close #123\n\nNo ledger in this body.\n")

    assert result["ok"] is True
    assert result["confirmation"]["line"].startswith("carrier-checked:")


def test_s23_a_downward_flip_clears_the_line():
    # One direction only, and the test says so: the helper clears on refusal and does not
    # restore on a flip back to ok. The repair is a function rather than one more line
    # inside the fold because the verdict and the sentence describing it were maintained
    # in two places.
    result = _pre_fold_result()
    result["ok"] = False

    VERIFY.sync_confirmation_line(result)

    assert result["confirmation"]["line"] is None


def test_s23_sync_is_inert_when_there_is_no_confirmation():
    result = {"ok": False, "status": "failed"}

    VERIFY.sync_confirmation_line(result)

    assert "confirmation" not in result


# --- S2 ------------------------------------------------------------------------------


def test_s2_a_stray_backtick_no_longer_masks_a_real_cross_line_span():
    # Pre-repair: `find_wrapped_inline_code` returned [] for this text — exit 0, "a real
    # cross-line inline-code span is reported clean". The stray backtick in `don`t`
    # paired with the real opener, leaving the real closer unmatched and dropped.
    text = "A stray backtick don`t worry, then `python3 foo.py\n--bar` ends the span.\n"

    violations = INLINE.find_inline_code_violations(text)

    # Pinned precisely, not as "non-empty": the leftover is on line 2 and is reported as
    # unterminated, because the operator remedy is to audit the pairing, not collapse a
    # wrap that is not there.
    assert violations == [(2, "--bar` ends the span.", INLINE.UNTERMINATED_REASON)]


def test_s2_a_plain_cross_line_span_is_still_reported():
    text = "Line one has `a real cross-line span\nthat closes here` on line two.\n"

    assert [line for line, _ in INLINE.find_wrapped_inline_code(text)] == [1]


def test_s2_a_well_formed_file_is_still_clean():
    for text in (
        "Plain `inline code` on one line.\n",
        "Two `spans` on `one line`.\n",
        "A fenced block:\n\n```\n`unbalanced inside a fence`\n`\n```\n\nAfter.\n",
        "An escaped backtick \\` is not a span opener.\n",
    ):
        assert INLINE.find_wrapped_inline_code(text) == [], text


def test_s2_the_checkers_own_scope_carries_no_odd_backtick_count():
    # The measurement behind arming: of the files this checker actually governs, ZERO
    # carry an odd single-backtick count, so reporting the leftover costs nothing. Three
    # files repo-wide do, all under `charness-artifacts/`, which EXCLUDE_PARTS excludes.
    offenders = []
    for path in INLINE._candidate_files(ROOT):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        stripped = INLINE._strip_fences(text)
        runs = 0
        for line in stripped.split("\n"):
            column = 0
            while column < len(line):
                if line[column] == "\\" and column + 1 < len(line):
                    column += 2
                    continue
                if line[column] != "`":
                    column += 1
                    continue
                start = column
                while column < len(line) and line[column] == "`":
                    column += 1
                if column - start == 1:
                    runs += 1
        if runs % 2:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_s2_charness_artifacts_stay_outside_the_checkers_scope():
    # The zero above is only meaningful while the exclusion holds.
    assert "charness-artifacts" in INLINE.EXCLUDE_PARTS
    scoped = {p.relative_to(ROOT).parts[0] for p in INLINE._candidate_files(ROOT)}
    assert "charness-artifacts" not in scoped


def test_s23_the_release_carrier_also_clears_its_confirmation(tmp_path):
    """The S23 class one level up, pinned by BEHAVIOR.

    Round 1 found that `release_issue_closeout_message` flips `ok` after `verify_closeout`
    has already rendered the confirmation sentence. The FIRST version of this test asserted
    that the string `sync_confirmation_line` appeared in the source file — which passes if
    the call is deleted and a comment remains, if it sits in an unreachable branch, or if
    it runs BEFORE the flip. Round 2 caught it: a test whose verdict outlived its check, in
    the file whose thesis is that verdicts must not outlive their checks.
    """
    from tests.quality_gates.test_release_issue_closeout_preflight import (  # noqa: PLC0415
        _load_release_closeout_message_module,
        bug_closeout_body,
    )

    message = _load_release_closeout_message_module()
    commit_message = "\n\n".join([
        "Release demo v1.0.0",
        bug_closeout_body(
            close_line="Close #44.\n\nClose #45.",
            behavior_line="Behavior #44: confirmed via fresh checkout install",
        ),
    ])

    result = message.validate_release_closeout_commit_message(
        tmp_path,
        repo="example/demo",
        issue_numbers=[44],
        classification="bug",
        commit_message=commit_message,
    )

    assert result["ok"] is False
    assert result["unexpected_close_keywords"] == [{"repo": None, "number": 45}]
    assert result["confirmation"]["line"] is None


def test_s2_the_unterminated_case_has_its_own_message():
    # Reusing the "wraps across line" sentence pointed an operator at a line where nothing
    # wraps: the leftover is the tail of a shifted pairing, not the wrapped span.
    text = "A stray backtick don`t worry, then `python3 foo.py\n--bar` ends the span.\n"

    violations = INLINE.find_inline_code_violations(text)

    assert [reason for _, _, reason in violations] == [INLINE.UNTERMINATED_REASON]
    wrapped = INLINE.find_inline_code_violations(
        "Line one has `a real cross-line span\nthat closes here` on line two.\n"
    )
    assert [reason for _, _, reason in wrapped] == [INLINE.WRAPPED_REASON]


# --- lines the armed changed-line gate named as uncovered ----------------------------


def test_the_unterminated_finding_prints_its_own_cli_message(tmp_path, monkeypatch, capsys):
    # `check_markdown_inline_code.py:150` — the unterminated branch of the CLI printer.
    #
    # Written into tmp_path, never the real repo: the first version of this test wrote a
    # scratch file under `docs/` and deleted it, and `check_test_repo_copy_invariants`
    # refused it. That is sweep row S112's class — transient worktree state another
    # pytest worker can observe — caught by the gate that owns it.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "unterminated.md").write_text("Use `foo to run.\n", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["check", "--repo-root", str(tmp_path)])

    code = INLINE.main()
    err = capsys.readouterr().err

    assert code == 1
    assert "unterminated inline code span" in err
    assert "inline code span issue(s) found" in err


def test_the_preflight_keeps_the_unterminated_class_distinguishable(tmp_path):
    # Reporting an UNTERMINATED span as a wrapped one was round 2's blocker: the two
    # have different remedies, and an operator sent to a line where nothing wraps
    # cannot act. `_inline_code_lines` — the renderer that split them under separate
    # labels — was deleted with `--json` on 2026-08-14, so the split now has to
    # survive in the emitted payload's `reason` token instead. This pins it there,
    # end to end through the collector rather than on a hand-built row, because the
    # documented way the token gets LOST is a shim dropping it in transit.
    preflight = _load_script_module(
        "check_doc_authoring_preflight_under_test",
        ROOT / "scripts" / "gates" / "check_doc_authoring_preflight.py",
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "unterminated.md").write_text("Use `foo to run.\n", encoding="utf-8")
    (tmp_path / "docs" / "wrapped.md").write_text("A wrapped `inline\ncode` span.\n", encoding="utf-8")

    unterminated = preflight.report_payload(
        preflight.build_report(tmp_path, "docs/unterminated.md")
    )["wrapped_inline_code"]
    wrapped = preflight.report_payload(
        preflight.build_report(tmp_path, "docs/wrapped.md")
    )["wrapped_inline_code"]

    assert [row["reason"] for row in unterminated] == ["unterminated"]
    assert unterminated[0]["line"] == 1
    # The control: a genuinely wrapped span must NOT be labelled unterminated, or
    # the two classes have collapsed again under a different name.
    assert wrapped and all(row["reason"] != "unterminated" for row in wrapped)
