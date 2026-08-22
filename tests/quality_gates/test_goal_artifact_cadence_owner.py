"""Tests for the gate-cadence one-owner floor.

`## Active Operating Frame`'s `Gate cadence:` line owns WHEN broad proof runs.
A hand-written `## User Acceptance` that restates it per slice is a second owner,
and the measured behaviour is that an agent obeys the acceptance criteria: one
session ran a 12-minute suite about thirteen times, roughly two and a half hours
of pure waiting.

The floor is narrow on purpose (this goal's Non-Goals forbid a gate an operator
would learn to ignore), so most of what follows pins what it must NOT refuse.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "skills/public/achieve/scripts"
_CHECKER = _SCRIPTS / "check_goal_artifact.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gal = _load(_SCRIPTS / "goal_artifact_lib.py", "goal_artifact_lib")
_CADENCE = _load(_SCRIPTS / "goal_artifact_cadence_owner.py", "goal_artifact_cadence_owner")

_DEFERRING_CADENCE = (
    "- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;\n"
    "  final/bundle proof records the verification lock and uses `--verification-lock`."
)


def _artifact(*, status: str = "active", cadence: str = _DEFERRING_CADENCE, acceptance: str) -> str:
    """A minimal artifact carrying only the two sections this floor reads."""
    return (
        "# Achieve Goal: t\n\nStatus: " + status + "\nCreated: 2026-08-08\n"
        "Activation: `/goal @x.md`\n\n"
        "## Active Operating Frame\n\n"
        "- Current slice: one.\n"
        + cadence
        + "\n\n## User Acceptance\n\n"
        + acceptance
        + "\n\n## Slice Log\n"
    )


def _check(text: str, status: str = "active") -> dict:
    return gal.check_cadence_owner(text, status=status)


# --- the refusal ------------------------------------------------------------


def test_refuses_acceptance_that_restates_a_deferred_cadence() -> None:
    report = _check(_artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary."))
    assert report["applies"] is True
    assert report["ok"] is False
    assert "two owners for one rule" in report["reason"]


def test_the_seeded_frame_refusal_does_not_read_as_self_cancelling() -> None:
    """The refusal a real consumer is most likely to see must not dismiss itself.

    The scaffold seeds a two-clause cadence line whose FIRST clause defers, so
    refusing it beside a per-slice acceptance demand is a TRUE POSITIVE. The
    payload also discloses a known over-fire in the same sentence, and a release
    critique found the disclosure reachable from this side: a consumer refused
    correctly could read "known over-fire" and dismiss it, then run the broad
    suite every slice -- the measured waste this floor exists to prevent.

    So the disclosure must lead with the check that separates the two, and must
    say plainly that a deferring line makes the refusal correct.
    """
    scaffold = _load(_SCRIPTS / "goal_artifact_scaffold.py", "goal_artifact_scaffold")
    seeded = [line for line in scaffold.DEFAULT_DRAFT_ACTIVE_FRAME_LINES if "Gate cadence" in line]
    assert len(seeded) == 1, "the scaffold must seed exactly one cadence line"
    index = list(scaffold.DEFAULT_DRAFT_ACTIVE_FRAME_LINES).index(seeded[0])
    # The seeded value soft-wraps onto the following continuation line.
    cadence = "\n".join(scaffold.DEFAULT_DRAFT_ACTIVE_FRAME_LINES[index : index + 2])

    report = _check(
        _artifact(
            cadence=cadence,
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    # It is a real contradiction, not an over-fire.
    assert report["applies"] is True
    assert report["ok"] is False
    reason = report["reason"]
    # The disambiguator must come BEFORE the over-fire clause, or the reader meets
    # the escape hatch first.
    assert "CHECK FIRST" in reason
    assert reason.index("CHECK FIRST") < reason.index("over-fire")
    assert "this refusal is CORRECT" in reason
    # And the over-fire clause must be conditioned on never deferring, not merely
    # on where a flag appears.
    assert "Only when the line never defers" in reason


def test_refusal_binds_each_line_to_its_own_role() -> None:
    """The inversion mutant: swapping the two roles must not survive.

    A substring pin over the message cannot see an inversion — the reason still
    reads plausibly with the roles swapped. So this asserts the VALUES: the
    cadence line number is the frame's, the finding's is the acceptance's, and
    they are distinct.
    """
    text = _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.")
    report = _check(text)
    lines = text.splitlines()
    cadence_line = report["cadence"]["line"]
    finding_line = report["findings"][0]["line"]
    assert cadence_line != finding_line
    assert lines[cadence_line - 1].lstrip().startswith("- Gate cadence:")
    assert "pytest tests/" in lines[finding_line - 1]
    # And the reason names them in those roles, not the reverse.
    assert f"Frame` line {cadence_line}" in report["reason"]
    assert f"Acceptance` line {finding_line}" in report["reason"]


def test_soft_wrapped_cadence_line_still_counts_as_the_owner() -> None:
    """The FRAME wraps too, and two live artifacts wrap before the flag.

    Reading the frame per physical line while reading acceptance per logical line
    disarmed the floor entirely and then reported "no cadence line that defers
    broad proof" — a sentence that was false about the artifact.
    """
    report = _check(
        _artifact(
            cadence=(
                "- Gate cadence: pre-lock slices use\n"
                "  `run_slice_closeout.py --skip-broad-pytest`; final proof uses the lock."
            ),
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    assert report["applies"] is True
    assert report["ok"] is False


def test_fenced_example_in_acceptance_does_not_force_a_refusal() -> None:
    """An artifact QUOTING the banned shape to warn against it is correct, not wrong.

    This fires most readily on artifacts in this goal's own family, which are the
    ones that discuss the pattern.
    """
    report = _check(
        _artifact(
            acceptance=(
                "- Acceptance never restates cadence. The refused form is:\n"
                "  ```\n"
                "  - `pytest tests/ -q` reports zero failures at every slice boundary.\n"
                "  ```"
            )
        )
    )
    assert report["ok"] is True


def test_unbalanced_fence_is_reported_as_unestablished_not_refused() -> None:
    """`mask_fences` FAILS OPEN on odd parity, so `masked` is then the raw text.

    Every read would be over a reading nobody established, and this floor's own
    refusal names LINE NUMBERS that would point inside a code fence. Round-2 review
    found this was the one new reader consuming a possibly-fail-open mask while
    claiming a fenced example could not act as an owner.
    """
    report = _check(
        _artifact(
            acceptance=(
                "- The refused form is:\n"
                "  ```\n"
                "  - `pytest tests/ -q` reports zero failures at every slice boundary.\n"
            )
        )
    )
    assert report["applies"] is False
    assert report["ok"] is True
    assert "unestablished" in report["reason"]
    # Balanced, the SAME body passes for the real reason (the fenced example is
    # masked) — so the unbalanced branch is not standing in for a matcher that
    # never fires.
    assert _check(
        _artifact(
            acceptance=(
                "- The refused form is:\n"
                "  ```\n"
                "  - `pytest tests/ -q` reports zero failures at every slice boundary.\n"
                "  ```"
            )
        )
    )["applies"] is True


def test_flags_between_pytest_and_the_path_are_still_broad() -> None:
    """`pytest -q tests/` is the same demand with one token moved."""
    assert _check(_artifact(acceptance="- `pytest -q tests/` is green at every slice boundary.")) ["ok"] is False
    assert _check(
        _artifact(acceptance="- `python3 -m pytest -x tests/` is green at every slice boundary.")
    )["ok"] is False


def test_soft_wrapped_acceptance_line_is_still_caught() -> None:
    """The measured artifact wrapped mid-command; a physical-line scan misses it."""
    report = _check(
        _artifact(
            acceptance=(
                "- `./scripts/run-quality.sh --read-only` exits 0 at EVERY slice boundary, and\n"
                "  `pytest tests/ -q` reports zero failures."
            )
        )
    )
    assert report["ok"] is False


# --- what it must NOT refuse ------------------------------------------------


def test_per_slice_read_only_quality_gate_is_not_refused() -> None:
    """`run-quality.sh --read-only` is a ~110s gate, not the ~12min suite.

    Demanding it per slice AGREES with a deferring cadence, and the predecessor
    measured it naming four real defects nothing else caught. Refusing it would be
    the wolf-crier the goal's Non-Goals forbid.
    """
    report = _check(
        _artifact(acceptance="- `./scripts/run-quality.sh --read-only` exits 0 at every slice boundary.")
    )
    assert report["applies"] is True
    assert report["ok"] is True


def test_scoped_pytest_subdirectory_per_slice_is_not_refused() -> None:
    report = _check(
        _artifact(acceptance="- `pytest tests/quality_gates -q` passes at each slice boundary.")
    )
    assert report["ok"] is True


def test_broad_pytest_demanded_at_closeout_is_not_refused() -> None:
    report = _check(_artifact(acceptance="- `pytest tests/ -q` reports zero failures at closeout."))
    assert report["ok"] is True


def test_acceptance_with_no_cadence_restatement_passes() -> None:
    report = _check(_artifact(acceptance="- The exemption list shrinks and each removal has a measured reason."))
    assert report["applies"] is True
    assert report["ok"] is True


def test_no_deferring_cadence_line_means_one_owner_not_a_contradiction() -> None:
    """An acceptance rule with no competing owner is a rule, not a contradiction."""
    report = _check(
        _artifact(
            cadence="- Gate cadence: broad proof at every boundary.",
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    assert report["applies"] is False
    assert report["ok"] is True


# --- the two ways to decline are two different facts -------------------------
#
# #681: the payload claimed `## Active Operating Frame` "states no `Gate cadence:`
# line" while `cadence` beside it carried the line number and text the floor had
# just parsed. `applies` and the human reason now come off the same parsed value.


def test_unrecognised_cadence_vocabulary_names_the_line_it_found() -> None:
    """Found-but-not-deferring must not be reported as not-found."""
    report = _check(
        _artifact(
            cadence="- Gate cadence: broad proof at every boundary.",
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    assert report["applies"] is False
    assert report["cadence"] is not None
    assert report["cadence"]["text"] == "broad proof at every boundary."
    # Three behavioral facts, not three spellings: the reason cites the line it
    # parsed, does not deny that line, and names the literal spellings it looked
    # for. A reword that keeps all three keeps this test green on purpose.
    assert f"line {report['cadence']['line']}" in report["reason"]
    assert "states no `Gate cadence:` line" not in report["reason"]
    assert "--skip-broad-pytest" in report["reason"]
    assert "--verification-lock" in report["reason"]


def test_soft_wrapped_cadence_outside_the_vocabulary_is_still_named() -> None:
    """The reported shape: a wrapped prose cadence bullet, found across the wrap."""
    report = _check(
        _artifact(
            cadence=(
                "- Gate cadence: final broad gates once after the reviewed family queue reaches\n"
                "  zero; pre-push only at the final bundle."
            ),
            acceptance="- The exemption list shrinks and each removal has a measured reason.",
        )
    )
    assert report["applies"] is False
    assert report["cadence"] is not None
    # Reflow is load-bearing: the wrapped tail must be part of the parsed text, or
    # the floor is judging half a sentence.
    assert report["cadence"]["text"].endswith("pre-push only at the final bundle.")
    # POSITIVE pin, not only the negative one: a regression that reworded the
    # reason back into "no line stating deferral was recognised" would satisfy a
    # bare `not in` check while reintroducing exactly the misread that was filed.
    # This case is the reproduction, so it carries its own teeth.
    assert f"line {report['cadence']['line']}" in report["reason"]
    assert "states no `Gate cadence:` line" not in report["reason"]


def test_the_two_declines_are_distinguishable_from_the_payload() -> None:
    """Absent and found-but-unrecognised must be distinguishable from the payload.

    This is the repair. Both cases returned `applies: False, ok: True` before it
    too, so a per-case assertion cannot see the defect -- only the pair can: the
    old code served ONE sentence for both, and a reader could not tell which
    fact it was being told.

    Named for what it asserts. The two reasons DO still share a closing sentence
    (`## User Acceptance` is not evaluated as a second owner), which is true on
    both branches; what must differ is which fact each one reports.

    Round 2 caught this test passing a mutant that gave the ABSENT branch the
    FOUND branch's prose -- #681's mirror image, shipped by the test named for
    the repair. Confirmed by running it: 3/3 new tests survived that mutant. The
    positive pin below is what closes it.
    """
    absent = _check(
        _artifact(
            cadence="",
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    found = _check(
        _artifact(
            cadence="- Gate cadence: broad proof at every boundary.",
            acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
        )
    )
    assert absent["cadence"] is None
    assert found["cadence"] is not None
    assert absent["reason"] != found["reason"]
    # The absent branch must not cite a line NUMBER it never parsed.
    assert re.search(r"line \d+", absent["reason"]) is None
    assert re.search(r"line \d+", found["reason"]) is not None
    # POSITIVE pin on the absent branch. Inequality plus "no digits" is not
    # enough: a digit-free copy of the found branch's prose satisfies both while
    # telling the reader a cadence line was parsed for an artifact that has none.
    assert "states no `Gate cadence:` line" in absent["reason"]
    assert "DOES state a" not in absent["reason"]


def test_complete_artifacts_are_skipped() -> None:
    """A terminal record is one nobody may repair; reddening on it cries wolf."""
    text = _artifact(
        status="complete",
        acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.",
    )
    report = _check(text, status="complete")
    assert report["applies"] is False
    assert report["ok"] is True
    assert "terminal record" in report["reason"]
    # ...and the SAME body refuses at a non-terminal status, so the skip is the
    # only thing carrying it, not an accidentally-inert matcher.
    assert _check(text, status="active")["ok"] is False


def test_annotated_terminal_status_still_skips() -> None:
    """`read_status` returns the whole line, and this repo annotates terminal ones.

    A bare `== "complete"` test DISARMS the skip for the repo's own house style —
    round-1 review found the live instance. The status is read the way the real
    caller reads it, not handed in pre-normalized.
    """
    body = _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.")
    annotated = body.replace(
        "Status: active", "Status: COMPLETE (2026-06-07) — gate-phase coverage closed; see"
    )
    skipped = gal.check_cadence_owner(annotated, status=gal.read_status(annotated))
    assert skipped["applies"] is False
    # Pin WHICH producer: `applies: False` also fires for "no deferring cadence
    # line", so a mutant breaking `_CADENCE_LABEL` would satisfy the bare boolean.
    assert "terminal record" in skipped["reason"]
    # A DRAFT annotated the same way is not terminal and still evaluates.
    draft = body.replace("Status: active", "Status: draft — slice 2 in flight")
    assert gal.check_cadence_owner(draft, status=gal.read_status(draft))["ok"] is False


# --- call sites -------------------------------------------------------------


def test_check_goal_call_site_fails_and_names_the_floor() -> None:
    text = _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.")
    result = gal.check_goal(text)
    assert result["ok"] is False
    assert any(issue.startswith("gate-cadence owner floor — ") for issue in result["issues"])


def _shaped_non_terminal(path: Path) -> str:
    """A live, fully-shaped artifact, normalised to a NON-TERMINAL status.

    These two tests use a real goal artifact rather than a hand-built fixture on purpose: with
    a synthetic one, both readiness keys are already False for unrelated reasons and the
    assertion below is vacuous. But a live artifact carries a LIFECYCLE, and the cadence-owner
    refusal is deliberately skipped for a `complete` record — "a terminal record is one nobody
    may repair". So when that goal legitimately reached `complete`, these tests started
    asserting about a code path that no longer runs, and both went green-then-red for a reason
    that had nothing to do with the refusal they exist to prove.

    Normalising the status keeps the realism (every other section is the real thing) and drops
    the coupling to one artifact's lifecycle. Pursue-readiness is an ACTIVATION question, and
    activation only applies to a goal that has not terminated.
    """
    text = path.read_text(encoding="utf-8")
    normalized = re.sub(r"^Status: .+$", "Status: active", text, count=1, flags=re.MULTILINE)
    assert "Status: active" in normalized, "the artifact no longer carries a Status line"
    return normalized


def test_pursue_readiness_call_site_refuses_activation(tmp_path: Path) -> None:
    """Activation is where the cost is paid: one broad suite per slice, after."""
    goal = tmp_path / "goal.md"
    goal.write_text(
        _shaped_non_terminal(
            _ROOT / "charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md"
        ),
        encoding="utf-8",
    )
    text = goal.read_text(encoding="utf-8")
    assert gal.pursue_readiness(text)["pursue_ready"] is True  # repaired artifact
    poisoned = text.replace(
        "- Every slice is proven green at the cadence `## Active Operating Frame` states.",
        "- `pytest tests/ -q` reports zero failures at each slice boundary.",
    )
    assert poisoned != text
    report = gal.pursue_readiness(poisoned)
    assert report["pursue_ready"] is False
    assert report["cadence_owner"]["ok"] is False
    assert "two owners for one rule" in report["reason"]


def test_pursue_reason_keeps_every_other_refusal_alongside_this_one() -> None:
    """JOIN, never replace.

    `_reason` is deliberately every-reason-not-the-first: a single-winner chain
    made a second `/goal` attempt discover the rest. Clobbering it here rebuilt
    that defect along a new dimension — round-1 review caught it. An artifact that
    is BOTH contradictory AND missing headings must report both.
    """
    text = _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.")
    report = gal.pursue_readiness(text)
    assert report["pursue_ready"] is False
    assert "two owners for one rule" in report["reason"]
    # The minimal artifact is also missing required headings; that reason survives.
    assert report["missing_sections"]
    assert "incomplete:" in report["reason"]
    # And the reserved `unshaped:` vocabulary is NOT borrowed for THIS clause — it
    # routes a reader to the achieve Before-phase, and this defect's remedy is a
    # one-sentence edit to `## User Acceptance`. Pinned on the clause, not on the
    # joined string's prefix: a prefix assertion is vacuous once reasons are joined,
    # which is how the first cut of this test let the mutant live.
    assert "contradictory: two owners for one rule" in report["reason"]
    assert "unshaped: two owners" not in report["reason"]


def test_refusal_updates_both_readiness_keys() -> None:
    """`pursue_readiness` publishes the same fact twice; a refusal must set both.

    Updating only `pursue_ready` left a payload asserting `activation_ready: true`
    about a goal the same payload refuses — one fact with two owners, which is
    this slice's own subject. `check_goal_artifact.py` prints the whole report, so
    an operator or CLI consumer reads the stale field. Round-2 review.
    """
    # A FULLY shaped artifact whose ONLY defect is the contradiction — otherwise
    # both keys are already False for unrelated reasons and the assertion is vacuous.
    live = _shaped_non_terminal(
        _ROOT / "charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md"
    )
    assert gal.pursue_readiness(live)["activation_ready"] is True
    poisoned = live.replace(
        "- Every slice is proven green at the cadence `## Active Operating Frame` states.",
        "- `pytest tests/ -q` reports zero failures at each slice boundary.",
    )
    assert poisoned != live
    report = gal.pursue_readiness(poisoned)
    assert report["pursue_ready"] is False
    assert report["activation_ready"] is False


def test_terminal_status_with_a_trailing_period_still_skips() -> None:
    """`Status: complete.` is a live in-repo spelling.

    The fail direction matters: not recognising it reddens a finished record,
    which is the wolf-crier this floor's own docstring forbids.
    """
    body = _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary.")
    for spelling in ("complete.", "Complete;", "COMPLETE (2026-06-07) — closed; see"):
        text = body.replace("Status: active", f"Status: {spelling}")
        report = gal.check_cadence_owner(text, status=gal.read_status(text))
        assert report["applies"] is False, spelling
        assert "terminal record" in report["reason"], spelling


def test_cli_surfaces_the_floor(tmp_path: Path) -> None:
    goal_dir = tmp_path / "charness-artifacts/goals"
    goal_dir.mkdir(parents=True)
    goal = goal_dir / "2026-08-08-x.md"
    goal.write_text(
        _artifact(acceptance="- `pytest tests/ -q` reports zero failures at each slice boundary."),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(_CHECKER), "--repo-root", str(tmp_path), "--goal-path", str(goal)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert yaml.safe_load(proc.stdout)["cadence_owner"]["ok"] is False


# --- the surfaces this run repaired ----------------------------------------


def test_shipped_template_does_not_seed_the_contradiction() -> None:
    """The scaffold is the SOURCE that kept reproducing the sentence."""
    template = (_SCRIPTS / "goal_artifact_template.md").read_text(encoding="utf-8")
    assert "Gate cadence:" in template  # points at the owner
    frame = _load(_SCRIPTS / "goal_artifact_scaffold.py", "goal_artifact_scaffold")
    rendered = frame.render_goal_template(
        template,
        title="t",
        date="2026-08-08",
        status="draft",
        goal_rel_path="charness-artifacts/goals/2026-08-08-t.md",
        goal_body="body",
        frame_lines=list(frame.DEFAULT_DRAFT_ACTIVE_FRAME_LINES),
    )
    report = _check(rendered, status="draft")
    # `applies` too: `ok is True` has THREE producers (terminal skip, unbalanced
    # fence, not-applicable), so the boolean alone cannot tell "the template is
    # safe" from "the floor never ran on it" — and LOW-8's own repair hedged the
    # claim that a `Gate cadence:` line is always seeded.
    assert report["applies"] is True
    assert report["ok"] is True


def test_every_non_complete_checked_in_goal_passes_the_floor() -> None:
    """The population is every artifact a session can still read, not a sample."""
    offenders = []
    for path in sorted((_ROOT / "charness-artifacts/goals").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not gal.check_cadence_owner(text, status=gal.read_status(text))["ok"]:
            offenders.append(path.name)
    assert offenders == []


# --------------------------------------------------------------------------- #
# The recorded #694 decision: DECLINE on an ambiguous line rather than guess.
#
# `_DEFERS_BROAD_PROOF` matches the literal PRESENCE of a flag, so a cadence line
# telling the reader NOT to pass it read as deferring, and `/goal` refused a
# truthful artifact. Three options were on the table; the repo owner chose to
# refuse to render a verdict, which preserves this module's stated preference for
# silence over a guess and needs no migration of the 84 checked-in goals that
# carry a cadence line.
#
# The distinction that makes this NOT paraphrase matching: the floor does not
# decide that a negated line demands broad proof. It decides that it cannot tell,
# and says so.
# --------------------------------------------------------------------------- #

#: THE HOUSE SPELLING. ~60 checked-in cadence lines and the scaffold seed write
#: the flag as `run_slice_closeout.py --skip-broad-pytest`, and the first cut of
#: the clause splitter split on every `.` -- severing the negation from the flag,
#: so the REPORTED artifact was still refused. The original test used the bare
#: flag, which is the one spelling the corpus does not use, and therefore could
#: not see it.
_NEGATED_CADENCE = (
    "- Gate cadence: broad pytest at EVERY slice boundary this run; "
    "do not pass `run_slice_closeout.py --skip-broad-pytest`."
)
_NEGATED_CADENCE_BARE_FLAG = (
    "- Gate cadence: broad pytest at EVERY slice boundary this run; "
    "do NOT pass `--skip-broad-pytest`."
)
_PER_SLICE_ACCEPTANCE = "- `pytest tests/ -q` reports zero failures at each slice boundary."


def test_a_negated_flag_mention_renders_no_verdict() -> None:
    """The exact artifact from the report: frame and acceptance AGREE that broad
    proof runs every slice, and the floor refused the pair as contradictory."""
    report = _check(_artifact(cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["applies"] is False
    assert report["ok"] is True
    assert "unestablished" in report["reason"]


def test_the_bare_flag_spelling_declines_too() -> None:
    """Both spellings, because the corpus uses one and the report used the other."""
    report = _check(_artifact(cadence=_NEGATED_CADENCE_BARE_FLAG,
                              acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["applies"] is False and report["ok"] is True


def test_a_deferral_stated_NEGATIVELY_still_refuses() -> None:
    """THE round-1 blocker on this slice, and the sharper of the two.

    `not|never|without|no` is the ordinary vocabulary of stating a deferral
    negatively, not only of negating one. The first cut declined on this line --
    which genuinely defers -- and so disarmed the floor on a TRUE POSITIVE,
    restoring the measured 2.5 hours of re-proof it exists to prevent. Declining
    now requires EVERY flag mention on the line to be negated; one unnegated
    flag clause establishes the deferral.
    """
    cadence = (
        "- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`, "
        "and no broad pytest runs before then; final/bundle proof records the "
        "verification lock and uses `--verification-lock`."
    )
    report = _check(_artifact(cadence=cadence, acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["applies"] is True
    assert report["ok"] is False


def test_no_checked_in_cadence_line_declines() -> None:
    """A CENSUS with a DENOMINATOR, read through the floor's own parser.

    A boolean corpus test cannot see blanket disarmament, because a decline also
    reports `ok: True` -- widening the negation vocabulary until all 84 lines
    declined would keep it green. But a census is only as good as the set it
    counts, and the first version of this test had two holes a round-2 review
    named: it re-declared a PRIVATE copy of `_CADENCE_LABEL` (one rule, two
    owners, in the slice about one rule having one owner), and it asserted no
    minimum, so a drifted regex measuring zero lines would still pass.

    It now calls the module's own `_cadence_owner` on the module's own masked
    logical section -- the exact path the floor takes, including soft-wrap reflow,
    which the private-regex version missed on at least one checked-in goal that
    wraps before its flag.
    """
    examined, declined = [], []
    for goal in sorted((_ROOT / "charness-artifacts" / "goals").glob("*.md")):
        text = goal.read_text(encoding="utf-8")
        cadence = _CADENCE._cadence_owner(gal._mask_fences(text), gal._markdown)
        if cadence is None:
            continue
        examined.append(goal.name)
        if _CADENCE._negated_near_flag(cadence["text"]):
            declined.append(goal.name)

    assert len(examined) >= 80, (
        f"the census measured only {len(examined)} cadence lines; a drifted parser "
        "that finds none would otherwise pass this test silently"
    )
    assert declined == [], declined


def test_the_decline_is_distinguishable_from_the_payload_alone() -> None:
    """Five branches emit `applies: False, ok: True`, and two of them even lead
    with the same `unestablished:` token, so prose was the only discriminator. The
    repair that separated absent-from-found added a distinguishing FACT; this
    restores that invariant."""
    report = _check(_artifact(cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["decline"] == "negated-flag-unreadable"


def test_the_readiness_pass_sentence_says_a_floor_rendered_no_verdict() -> None:
    """A DECLINE IS NOT A PASS. Unlike the unbalanced-fence decline it imitates --
    which `check_goal` and `activation_ready` both refuse independently -- this one
    has no backstop, so without disclosure the payload said "safe to pursue" with
    no clause anywhere saying a floor had answered nothing."""
    text = _artifact(status="draft", cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE)

    report = gal.pursue_readiness(text)

    assert report["cadence_unestablished"] is True
    assert "rendered NO VERDICT" in report["reason"]


def test_the_decline_quotes_the_clause_it_could_not_read() -> None:
    """A decline that does not show its evidence is indistinguishable from a
    parser that skipped -- the exact confusion this module already repaired once
    for its other non-applicable branch."""
    report = _check(_artifact(cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE))

    assert "do not pass `run_slice_closeout.py --skip-broad-pytest`" in report["reason"], (
        "the quoted clause must be the WHOLE clause -- the first splitter cut it "
        "mid-token at the filename dot and quoted 'py --skip-broad-pytest'"
    )


def test_the_decline_does_not_block_activation() -> None:
    """`pursue_readiness` gates on `ok`, so an `ok: False` decline would keep
    refusing the artifact this decision exists to stop refusing."""
    text = _artifact(status="draft", cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE)

    assert _check(text, status="draft")["ok"] is True


def test_the_scaffolds_own_seeded_frame_is_STILL_refused() -> None:
    """THE guard on this change, and the one the constant's comment warns about
    by name: the seeded frame's FIRST clause genuinely defers, so refusing it
    beside a per-slice acceptance demand is a TRUE POSITIVE. A line-wide negation
    search would have declined here and disarmed the floor on its own template."""
    report = _check(_artifact(acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["applies"] is True
    assert report["ok"] is False


def test_a_negation_in_a_DIFFERENT_clause_does_not_disarm_the_floor() -> None:
    """Clause-scoped, not line-scoped. A deferring first clause plus an unrelated
    negation later must still refuse."""
    cadence = (
        "- Gate cadence: pre-lock slices use `--skip-broad-pytest`; "
        "the release is not cut until CI is green."
    )
    report = _check(_artifact(cadence=cadence, acceptance=_PER_SLICE_ACCEPTANCE))

    assert report["applies"] is True
    assert report["ok"] is False


def test_an_unambiguous_deferral_with_no_acceptance_conflict_still_passes() -> None:
    """The decline must not swallow the clean case: one owner, no findings."""
    report = _check(_artifact(acceptance="- The operator can resume a run without rebuilding."))

    assert report["applies"] is True
    assert report["ok"] is True


# --------------------------------------------------------------------------- #
# Round-2 repairs on slice A.
#
# The round almost did not happen: the goal's Slice Plan claimed "two rounds
# consumed" while its own Slice Log said one, and a claims round caught the
# contradiction. Everything below is what the owed round found.
# --------------------------------------------------------------------------- #


def test_every_non_applicable_branch_carries_a_distinct_decline() -> None:
    """TABLE-DRIVEN, because a per-case assertion cannot see this defect.

    The `decline` key was added so five branches emitting `applies: False,
    ok: True` could be told apart by a FACT rather than by prose -- and the first
    cut left two of them without one. The absent-cadence branch had no key at all,
    so `report["decline"]` raised `KeyError` and `report.get("decline")` read
    falsy on a real decline; the unbalanced-fence branch carried `""`, which is
    indistinguishable from the PASS branch. Both are the exact indistinguishability
    the key exists to close, and the single-branch test that shipped with it could
    not see either.
    """
    complete_frame = _artifact(acceptance=_PER_SLICE_ACCEPTANCE).replace(
        "Status: active", "Status: complete", 1
    )
    cases = {
        "terminal-status": (complete_frame, "complete"),
        "unbalanced-fences": (
            _artifact(acceptance=_PER_SLICE_ACCEPTANCE) + "\n```\nunclosed\n", "active"),
        "no-cadence-line": (
            _artifact(cadence="- Next action: go.", acceptance=_PER_SLICE_ACCEPTANCE), "active"),
        "vocabulary-not-recognised": (
            _artifact(cadence="- Gate cadence: broad pytest every slice.",
                      acceptance=_PER_SLICE_ACCEPTANCE), "active"),
        "negated-flag-unreadable": (
            _artifact(cadence=_NEGATED_CADENCE, acceptance=_PER_SLICE_ACCEPTANCE), "active"),
    }
    observed = {}
    for expected, (text, status) in cases.items():
        report = _check(text, status)
        assert report["applies"] is False, (expected, report["reason"])
        observed[expected] = report.get("decline", "<ABSENT>")

    assert observed == {name: name for name in cases}, observed


def test_the_applies_branches_carry_an_empty_decline_not_a_missing_key() -> None:
    """A consumer reading `report["decline"]` must not have to know which branch
    it is holding. Absent-vs-empty is the same schema defect one level down."""
    for text in (_artifact(acceptance="- The operator can resume."),
                 _artifact(acceptance=_PER_SLICE_ACCEPTANCE)):
        report = _check(text)
        assert report["applies"] is True
        assert report["decline"] == ""


def test_the_gate_wired_caller_also_discloses_the_decline() -> None:
    """`check_goal` decides the validator's EXIT CODE; `--pursue-ready` is the
    advisory lane. The first repair gave the disclosure only to the advisory one,
    so a decline left the blocking caller returning `ok: True, issues: []` with
    nothing anywhere saying a floor had rendered no verdict -- this repo's own
    'migrating the diagnosis without the fix' class, in the same file."""
    text = _artifact(cadence=_NEGATED_CADENCE,
                     acceptance="- The operator can resume without rebuilding.")

    report = gal.check_goal(text)

    assert any("rendered NO VERDICT" in entry for entry in report["advisories"]), report


def test_a_clean_artifact_carries_no_cadence_advisory() -> None:
    """The disclosure must not fire on every run, or it stops being a signal."""
    report = gal.check_goal(_artifact(acceptance="- The operator can resume."))

    assert [a for a in report["advisories"] if "cadence" in a] == []
