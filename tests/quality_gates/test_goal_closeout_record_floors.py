"""Floors on the goal artifact's own closeout record.

Both floors here were built because a checked-in closeout-claims review found the
defects in a real goal's `## Final Verification`, not because they were imagined.
Each is form/identity only: neither decides whether a citation is honest or
whether a review was independent, because neither question is decidable from a
checked-in file, and a validator that pretended otherwise would ship as the
Goodhart proxy this repo refuses.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from datetime import date

from .support import ROOT

SCRIPT_DIR = ROOT / "skills" / "public" / "achieve" / "scripts"
IN_SCOPE = "2026-08-01"
GRANDFATHERED = "2026-07-01"
DISTINCTNESS_IN_SCOPE = "2026-08-01"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact(created: str, final_verification: str) -> str:
    return (
        f"# Goal\n\nCreated: {created}\nStatus: complete\n\n"
        f"## Final Verification\n\n{final_verification}\n"
    )


# --- figure form ------------------------------------------------------------


def _figure_check(created: str, body: str) -> dict:
    return _load("goal_artifact_figure_form").check(_artifact(created, body))


def test_a_bare_figure_is_refused() -> None:
    """The defect itself: a number a later session plans against, with no source."""
    result = _figure_check(IN_SCOPE, "- Mutation score was 94.9% across the suite.")

    assert result["applies"] is True
    assert result["ok"] is False
    assert result["figure_lines"] == 1
    assert "no source cited on the line" in result["offenders"][0]["reason"]


def test_a_sourced_figure_passes() -> None:
    result = _figure_check(
        IN_SCOPE,
        "- Mutation score 94.9% — `cosmic-ray dump reports/mutation/session.sqlite`",
    )

    assert result["ok"] is True
    assert result["figure_lines"] == 1


def test_an_explicitly_unbacked_figure_passes_with_a_reason() -> None:
    """The escape hatch is the point: an honest closeout can state an unmeasured
    number, as long as it says so. Without this arm the floor would push authors
    to delete inconvenient figures rather than label them."""
    result = _figure_check(
        IN_SCOPE, "- Roughly 40 sessions affected — unbacked: no host log retains that window"
    )

    assert result["ok"] is True


def test_a_bare_unbacked_marker_is_refused() -> None:
    """`unbacked:` with no reason is the floor satisfied by a magic word."""
    result = _figure_check(IN_SCOPE, "- Roughly 40 sessions affected — unbacked: n/a")

    assert result["ok"] is False


def test_prose_after_the_separator_is_not_a_source() -> None:
    result = _figure_check(IN_SCOPE, "- Mutation score 94.9% — this was verified carefully")

    assert result["ok"] is False
    assert "cites no path, command, or URL" in result["offenders"][0]["reason"]


def test_a_source_cited_before_the_separator_counts() -> None:
    """The form must not demand a PUNCTUATION where a citation already exists.

    Measured: the separator-mandatory form refused 90 of the 127 dated checked-in
    artifacts, including lines that name the exact command that produced the
    number. That is the form being wrong about the repo.
    """
    result = _figure_check(
        IN_SCOPE, "- `bash scripts/run-quality.sh` full: 82 passed, 1 failed."
    )

    assert result["ok"] is True


def test_a_short_unbacked_marker_does_not_hide_a_real_citation() -> None:
    """The every-segment loop used to bail on the first short `unbacked:`."""
    result = _figure_check(
        IN_SCOPE, "- 6 mutants survived — unbacked: n/a — see `scripts/mutants.py`"
    )

    assert result["ok"] is True


def test_an_ordered_list_item_is_its_own_figure_line() -> None:
    """Soft-wrap joining used to absorb `2. <figure>` into the bullet above it, so
    the figure silently inherited that line's citation."""
    body = "1. Ran the suite — `pytest`\n2. 6515 tests passed"
    result = _figure_check(IN_SCOPE, body)

    assert result["ok"] is False, result
    assert any("6515" in o["line"] for o in result["offenders"])


def test_a_heading_cannot_swallow_the_figure_beneath_it() -> None:
    """Joining then skipping `#` lines discarded the figure entirely."""
    body = "### Bundle proof\n6515 tests passed"
    result = _figure_check(IN_SCOPE, body)

    assert result["figure_lines"] == 1
    assert result["ok"] is False


def test_tokens_that_are_digits_without_being_figures_do_not_trigger() -> None:
    """The false-refusal direction is the dangerous one: a gate that fires on
    dates, versions, issue refs, and paths would make an ordinary closeout
    unrecordable and train people to pad text until it passes."""
    body = "\n".join(
        [
            "- Landed on 2026-08-01 with no rollback.",
            "- Released as v3.0.1 to the plugin surface.",
            "- Tracked in #467 and closed there.",
            "- Wrote scripts/check_doc_links.py and its test.",
            "- Gate took 40.7s on this machine.",
        ]
    )
    result = _figure_check(IN_SCOPE, body)

    assert result["figure_lines"] == 0, result.get("offenders")
    assert result["ok"] is True


def test_a_figure_inside_a_code_fence_is_the_author_showing_a_shape() -> None:
    text = (
        f"# Goal\n\nCreated: {IN_SCOPE}\nStatus: complete\n\n"
        "## Final Verification\n\n"
        "```\n- Mutation score 94.9%\n```\n"
    )
    result = _load("goal_artifact_figure_form").check(text)

    assert result["figure_lines"] == 0
    assert result["ok"] is True


def test_evidence_lines_are_left_to_their_own_floor() -> None:
    """A retro path can contain digits; reading it as a figure would double-refuse
    one defect and hide which floor to fix."""
    result = _figure_check(
        IN_SCOPE, "Retro: charness-artifacts/retro/2026-08-01-v3-0-1-retro.md"
    )

    assert result["figure_lines"] == 0
    assert result["ok"] is True


def test_figure_floor_grandfathers_a_prior_goal() -> None:
    """Without this, a floor landing today is in scope for every prior goal, and
    the only way to green those is to edit frozen artifacts."""
    result = _figure_check(GRANDFATHERED, "- Mutation score was 94.9% across the suite.")

    assert result["applies"] is False
    assert result["ok"] is True
    assert result["evaluated"] is False
    assert result["rule_date"] == "2026-08-01"
    # The scope verdict rests on a line the author wrote, with no corroborating
    # channel, and the reason has to say so rather than read as established fact.
    assert "self-declared" in result["reason"]


def test_figure_floor_rule_date_is_not_in_the_future() -> None:
    """A rule date after today would silently grandfather every goal forever."""
    module = _load("goal_artifact_figure_form")

    # `<= today`, not `today + 1`. Round 2 caught the one-day slack permitting
    # exactly the state the name forbids — and it was permitting it, because the
    # rule date had been pushed to tomorrow to manufacture a clean corpus.
    assert module.FIGURE_FORM_RULE_DATE <= date.today()


# --- evidence distinctness --------------------------------------------------


def _distinctness_check(created: str, retro: str, review: str) -> dict:
    report = {
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": retro},
            {"name": "disposition_review", "via": "evidence", "path": review},
        ]
    }
    return _load("goal_artifact_evidence_distinctness").check(report, _artifact(created, "x"))


def test_one_file_cannot_be_both_the_record_and_its_own_review() -> None:
    same = "charness-artifacts/retro/2026-08-01-a-retro.md"
    result = _distinctness_check(DISTINCTNESS_IN_SCOPE, same, same)

    assert result["applies"] is True
    assert result["ok"] is False
    assert "resolve to the same file" in result["reason"]


def test_two_distinct_paths_pass() -> None:
    result = _distinctness_check(
        IN_SCOPE,
        "charness-artifacts/retro/2026-08-01-a-retro.md",
        "charness-artifacts/critique/2026-08-01-a-claims-review.md",
    )

    assert result["ok"] is True


def test_the_same_file_reached_by_two_spellings_is_still_one_file() -> None:
    """Path identity, not string identity: `./x.md` and `x.md` are one artifact."""
    result = _distinctness_check(
        IN_SCOPE,
        "charness-artifacts/retro/2026-08-01-a-retro.md",
        "./charness-artifacts/retro/2026-08-01-a-retro.md",
    )

    assert result["ok"] is False


def test_a_skipped_review_does_not_collide_with_the_retro() -> None:
    """A host-blocked subagent recorded as `skipped:` has no path. Refusing it
    would punish the documented degradation instead of the defect."""
    report = {
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": "a/retro.md"},
            {"name": "disposition_review", "via": "skip", "reason": "host-blocked-subagent"},
        ]
    }
    result = _load("goal_artifact_evidence_distinctness").check(
        report, _artifact(DISTINCTNESS_IN_SCOPE, "x")
    )

    assert result["ok"] is True
    assert "nothing to compare" in result["reason"]


def test_distinctness_floor_grandfathers_a_prior_goal() -> None:
    same = "charness-artifacts/retro/2026-07-01-a-retro.md"
    result = _distinctness_check(GRANDFATHERED, same, same)

    assert result["applies"] is False
    assert result["ok"] is True


def test_distinctness_floor_does_not_claim_to_check_authorship() -> None:
    """Pinned as a NON-claim, deliberately: the stronger rule ("a different
    author reviewed this") is unbuildable, and the docstring must keep saying so
    rather than letting a reader assume path-distinctness proves independence."""
    source = (SCRIPT_DIR / "goal_artifact_evidence_distinctness.py").read_text(encoding="utf-8")

    assert "does not check that the two files have different AUTHORS" in source
    assert "authorship PROXY" in source


def test_the_figure_floor_reports_without_refusing() -> None:
    """NON-BLOCKING, and the reason is a measurement — see the docstring on
    `apply_figure_form_floor`. It still answers the form question and still
    publishes its denominator; what it does not do is refuse."""
    module = _load("goal_artifact_figure_form")
    report = {"ok": True}
    module.apply_figure_form_floor(report, _artifact(IN_SCOPE, "- Score was 94.9% overall."))

    fragment = report["final_verification_figure_form"]
    assert fragment["ok"] is False
    assert fragment["blocking"] is False
    assert fragment["figure_lines"] == 1
    assert report["ok"] is True


def test_the_corpus_measurement_the_non_arming_rests_on() -> None:
    """Executed, not asserted, and over a denominator that is not empty.

    Round 1 armed this floor on "0 refused" — a number measured over 20 artifacts
    that carry no `Created:` line at all, with ZERO dated artifacts in scope. This
    test exists so that mistake cannot be repeated silently: it measures over
    DATED artifacts, and fails if the refusal rate ever drops to zero (arm it) or
    if the denominator ever collapses (the measurement stopped meaning anything).
    """
    module = _load("goal_artifact_figure_form")
    grammar = _load("goal_artifact_floor_grammar")
    refused = 0
    dated = 0
    for path in sorted((ROOT / "charness-artifacts" / "goals").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if grammar.parse_created_date(text) is None:
            continue
        dated += 1
        if not module.check(text)["ok"]:
            refused += 1

    assert dated > 100, f"denominator collapsed to {dated}; the measurement is empty"
    assert refused > 0, (
        "no dated checked-in artifact refuses any more; the corpus has moved to "
        "the form, so re-open whether this floor should be ARMED"
    )


def test_an_unbalanced_fence_refuses_to_render_a_verdict() -> None:
    """`applies()` fails closed while `mask_fences` fails open, so without this
    guard the two combine into: forced in scope, fenced examples read as real."""
    text = (
        f"# Goal\n\nCreated: {IN_SCOPE}\nStatus: complete\n\n"
        "## Final Verification\n\n```\n- Mutation score 94.9%\n"
    )
    result = _load("goal_artifact_figure_form").check(text)

    assert result["evaluated"] is False
    assert "unbalanced" in result["reason"]


def test_a_four_digit_figure_is_seen() -> None:
    """The first cut capped the digit run at three, so the exact line the floor
    was built for slipped past it."""
    result = _figure_check(IN_SCOPE, "- 1024 mutants tested with no source.")

    assert result["figure_lines"] == 1
    assert result["ok"] is False


def test_a_bare_prose_slash_is_not_a_citation() -> None:
    """`pass/fail` and `2/3` used to certify a line as sourced — worse than a
    miss, because the figure was detected and then affirmatively cleared."""
    for body in (
        "- 12 rows remain — pass/fail unknown at this point",
        "- 6 mutants survived — about 2/3 of the suite",
    ):
        assert _figure_check(IN_SCOPE, body)["ok"] is False, body


def test_a_citation_followed_by_commentary_still_passes() -> None:
    """Rightmost-separator-wins false-refused a correctly-sourced line that kept
    talking. A false refusal teaches padding, which is the failure mode a form
    floor most has to avoid."""
    result = _figure_check(
        IN_SCOPE,
        "- 9 of 9 rows — `charness-artifacts/critique/x.md` — the 10th was out of scope",
    )

    assert result["ok"] is True


def test_a_wrapped_command_argument_is_not_read_as_a_figure() -> None:
    """Inline-code masking is single-line, so a soft-wrapped command left its
    second line with no backtick pair and its arguments exposed as figures."""
    result = _figure_check(
        IN_SCOPE,
        "- Ran `python3 scripts/plan_cautilus_proof.py --repo-root .\n  --limit 250` and it passed",
    )

    assert result["ok"] is True, result.get("offenders")


# --- the floors' own wiring, which the direct-`check` tests do not reach --------

# A report with every list-shaped key `_evidence_missing_bits` indexes, so these
# tests exercise the two new branches without asserting the rest of its shape.
_EMPTY_EVIDENCE_REPORT = {
    "missing": [],
    "missing_evidence_files": [],
    "invalid_skips": [],
    "unbound_evidence": [],
    "binding_failures": [],
    "stub_evidence": [],
    "coordination_missing": [],
    "section_placeholders": [],
    "invalid_early_close_reports": [],
}


def test_the_distinctness_floor_flips_the_caller_verdict() -> None:
    """`check` returning `ok: False` is not the same as the caller refusing.

    The direct-`check` tests above prove the verdict; this proves the wiring that
    turns it into a refusal. Authoring a proof surface is an irreversible
    boundary, so its own arming path needs a test rather than an assumption.
    """
    module = _load("goal_artifact_evidence_distinctness")
    same = "charness-artifacts/retro/2026-08-01-a-retro.md"
    report = {
        "ok": True,
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": same},
            {"name": "disposition_review", "via": "evidence", "path": same},
        ],
    }
    module.apply_evidence_distinctness_floor(report, _artifact(DISTINCTNESS_IN_SCOPE, "x"))

    assert report["ok"] is False
    assert report["closeout_evidence_distinctness"]["ok"] is False


def test_the_distinctness_floor_leaves_a_clean_verdict_alone() -> None:
    module = _load("goal_artifact_evidence_distinctness")
    report = {
        "ok": True,
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": "a/retro.md"},
            {"name": "disposition_review", "via": "evidence", "path": "b/review.md"},
        ],
    }
    module.apply_evidence_distinctness_floor(report, _artifact(DISTINCTNESS_IN_SCOPE, "x"))

    assert report["ok"] is True


def test_an_unreadable_path_falls_back_instead_of_passing(monkeypatch) -> None:
    """`samefile` raising must not read as "proven distinct".

    An OSError here means the comparison did not happen. Passing on it would let
    an unreadable pair satisfy a floor that never compared them, so the code
    falls through to the textual comparison — and this pins that it does.
    """
    module = _load("goal_artifact_evidence_distinctness")
    from pathlib import Path as _Path

    monkeypatch.setattr(_Path, "exists", lambda self: True)

    def _raise(self, other):
        raise OSError("stat failed")

    monkeypatch.setattr(_Path, "samefile", _raise)

    same = _Path("charness-artifacts/retro/a-retro.md")
    other = _Path("charness-artifacts/critique/a-review.md")

    assert module._same_file(same, same) is True, "identical paths still compare equal"
    assert module._same_file(same, other) is False


def test_both_new_floors_name_themselves_in_the_refusal_message() -> None:
    """The round-1 blocker, pinned: a refusal must name the floor that refused.

    Without these branches the message named a floor that had PASSED, which is
    the shape `_evidence_missing_bits`' own docstring records as why it exists.
    """
    main_module = _load("check_goal_artifact")
    report = {
        **_EMPTY_EVIDENCE_REPORT,
        "operator_decision_queue": {"applies": True, "ok": True, "reason": "queue disposition recorded"},
        "closeout_evidence_distinctness": {"applies": True, "ok": False, "reason": "resolve to the same file"},
        "final_verification_figure_form": {"applies": True, "ok": False, "reason": "2 figure line(s) state a number"},
    }
    bits = main_module._evidence_missing_bits(report)
    joined = "; ".join(bits)

    assert "closeout-evidence distinctness: resolve to the same file" in joined
    assert "final-verification figure form: 2 figure line(s) state a number" in joined
    # And the PASSING floor stays out of the refusal message.
    assert "operator-decision-queue" not in joined


def test_a_refusing_queue_floor_still_names_itself() -> None:
    """The control for the line above: re-guarding must not silence a real
    operator-queue refusal, only stop it narrating someone else's."""
    main_module = _load("check_goal_artifact")
    report = {
        **_EMPTY_EVIDENCE_REPORT,
        "operator_decision_queue": {"applies": True, "ok": False, "reason": "`## Operator Decision Queue` is blank"},
    }
    joined = "; ".join(main_module._evidence_missing_bits(report))

    assert "operator-decision-queue floor: `## Operator Decision Queue` is blank" in joined


def test_an_artifact_with_no_final_verification_declines_to_answer() -> None:
    """Absent section is another floor's question. Reporting a satisfied form
    over a section that does not exist would be a pass over nothing read."""
    text = f"# Goal\n\nCreated: {IN_SCOPE}\nStatus: complete\n\n## Goal\n\nsomething\n"
    result = _load("goal_artifact_figure_form").check(text)

    assert result["evaluated"] is False
    assert result["figure_lines"] == 0
    assert "no `## Final Verification` section" in result["reason"]


def test_each_floor_module_bootstraps_itself_in_a_fresh_interpreter() -> None:
    """The `sys.path` insert is how each module finds its shared substrate.

    In-process tests never execute it: the first module loaded inserts the
    directory and every later one short-circuits, so the branch that makes the
    module work standalone — the installed-plugin case — is exercised by no test
    at all. A subprocess per module is the only way to reach it.
    """
    for name in ("goal_artifact_evidence_distinctness", "goal_artifact_figure_form"):
        script = (
            "import importlib.util, sys;"
            f"spec = importlib.util.spec_from_file_location('{name}', r'{SCRIPT_DIR / (name + '.py')}');"
            "m = importlib.util.module_from_spec(spec);"
            "spec.loader.exec_module(m);"
            "print(m.applies.__name__)"
        )
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=tempfile.gettempdir(),
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, f"{name}: {result.stderr}"
        assert result.stdout.strip() == "applies"
