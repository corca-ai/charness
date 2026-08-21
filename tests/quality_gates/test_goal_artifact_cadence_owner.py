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
