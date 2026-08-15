"""Acceptance for the S3 lesson-loop criteria: SC6 (vocabulary) and SC7 (slot).

These are the checks the 6.0.0 release contract names for this slice, kept in
their own file so the criterion each one answers is legible without reading a
schema fixture first.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts import check_lesson_evaluation_continuity as checker
from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_evaluation_reconcile_lib as reconcile
from scripts import lesson_score_outcome_lib as outcome_lib
from scripts import lesson_selection_preview_lib as preview
from scripts import recent_lessons_lib as _index
from scripts import record_lesson_score as scorer
from scripts import render_lesson_lifecycle_review as _review_module
from tests.lesson_ledger_fixtures import outcome_event
from tests.test_lesson_ledger import (
    _ledger,
    _retro,
    _score_event,
    _session_event,
    _validate,
)

ENCOUNTER_RETRO = "charness-artifacts/retro/2026-08-15-encounter.md"


def _write_index(repo: Path, output_dir: Path) -> None:
    """The digest and its selection index, written the way the refresh CLI does.

    Both steps, because `write_lesson_selection_index` reads the digest and
    refuses when it is absent. In-process on purpose: this is fixture setup, not
    the boundary under test, and shelling out counted against the
    boundary-bypass ratchet for no proof. The one subprocess this file keeps is
    the SC7 lifecycle command, where crossing the real entrypoint IS the claim.
    """
    summary = output_dir / "recent-lessons.md"
    digest = _index.build_indexed_recent_lessons(
        repo_root=repo, output_dir=output_dir, summary_path=summary
    )
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(digest.summary_text, encoding="utf-8")
    _index.write_lesson_selection_index(repo, output_dir, summary)


def _seeded(tmp_path: Path, *, with_index: bool = False) -> Path:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])
    if with_index:
        # The review renders over the rebuilt selection index, so a repo that has
        # a ledger and no index is a refusal rather than an empty report. Written
        # IN-PROCESS: this is fixture setup, not the boundary under test, and
        # shelling out here counted against the boundary-bypass ratchet for no
        # proof. The one subprocess this file keeps is the SC7 lifecycle command,
        # where crossing the real entrypoint IS the claim.
        _write_index(tmp_path, path.parent)
    return path


def _score(tmp_path: Path, path: Path, **overrides: object) -> dict:
    arguments: dict[str, object] = {
        "repo_root": tmp_path,
        "output_dir": path.parent,
        "summary_path": path.parent / "recent-lessons.md",
        "event_id": "encounter-1",
        "session_id": "session-a",
        "lesson_id": "a",
        "source_retro": ENCOUNTER_RETRO,
        "outcome": "changed-an-action",
        "anchor": "ran the measured command instead of transcribing a count, which would have shipped a false one",
    }
    arguments.update(overrides)
    return scorer.append_score(**arguments)


# --- SC6: "a lesson that is read and then works can be recorded as such
# --- without declaring a recurrence"


def test_a_lesson_that_worked_records_without_declaring_that_it_recurred(tmp_path: Path) -> None:
    """The defect the whole vocabulary exists to remove.

    `charness-artifacts/retro/source.md` is the only retro carrying
    `recurrence-class: a`, and the encounter cites a DIFFERENT path that carries
    no such tag and does not even exist yet. Under the old rule this was the only
    way to credit a working lesson and it was refused, so three lessons that
    measurably changed an action in the 2026-08-14 session went unrecorded.
    """
    path = _seeded(tmp_path)
    assert not (tmp_path / ENCOUNTER_RETRO).exists()

    event = _score(tmp_path, path)

    assert event["outcome"] == "changed-an-action"
    assert event["source_retro"] == ENCOUNTER_RETRO
    assert "score" not in event
    lesson = json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]
    assert lesson["outcome_counts"]["changed-an-action"] == 1
    # A positive moves the ranking UP. The narrow true claim, measured: the
    # ledger held zero NEGATIVE scores until 2026-08-14, not because nothing
    # failed but because the signal had no path in. (Positives were expressible
    # as legacy scalars all along -- an earlier version of this comment said
    # otherwise and a bounded reviewer refuted it. What was impossible was
    # crediting a lesson a SECOND time without declaring its class recurred.)
    assert lesson["score_total"] == 1


def test_the_four_value_vocabulary_round_trips_and_routes_to_one_disposition_each(
    tmp_path: Path,
) -> None:
    """One outcome per SESSION, which is the only shape the gate also accepts.

    An earlier version of this test put all four outcomes in one session under
    four fabricated retro paths. It passed, and a bounded reviewer showed it
    passed in a configuration `foreign_scores` would reject in production: only
    the retro claiming a session owns that session's encounters, so three of the
    four were foreign. Proving a vocabulary in a shape the gate forbids is not
    proving it. One session per encounter, each citing the retro that records it,
    is what an author actually writes.
    """
    outcomes = sorted(outcome_lib.SCORE_OUTCOMES)
    _retro(tmp_path, "source.md", "a")
    for index, _outcome_value in enumerate(outcomes):
        # `not-consulted` asserts the class recurred, and the writer now refuses it
        # unless the recording retro carries the tag -- so each recording retro is
        # a REAL tagged retro rather than an invented path.
        _retro(tmp_path, f"2026-08-15-r{index}.md", "a")
    path = _ledger(
        tmp_path,
        session_events=[_session_event(session_id=f"s-{index}") for index in range(len(outcomes))],
    )
    recorded = {}
    for index, outcome in enumerate(outcomes):
        recorded[outcome] = _score(
            tmp_path,
            path,
            event_id=f"encounter-{index}",
            session_id=f"s-{index}",
            source_retro=f"charness-artifacts/retro/2026-08-15-r{index}.md",
            outcome=outcome,
            anchor="was in view at the decision and the work would have gone elsewhere otherwise",
        )
    assert _validate(tmp_path)["score_event_count"] == 4
    # And every one of them is OWNED by the retro that records it, so none is
    # foreign -- the property the earlier shape silently violated.
    for index in range(len(outcomes)):
        declaring = f"charness-artifacts/retro/2026-08-15-r{index}.md"
        events = json.loads(path.read_text(encoding="utf-8"))["score_events"]
        assert not outcome_lib.foreign_scores(events, session_id=f"s-{index}", path=declaring)
    assert {event["outcome"] for event in recorded.values()} == set(outcome_lib.SCORE_OUTCOMES)
    counts = json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["outcome_counts"]
    assert all(counts[outcome] == 1 for outcome in outcome_lib.SCORE_OUTCOMES)
    # The split earns its keep only if each value lands on ONE disposition without
    # a human re-deriving which.
    assert {outcome_lib.SCORE_OUTCOMES[outcome] for outcome in outcome_lib.SCORE_OUTCOMES} == {
        "graduate",
        "rewrite-in-place",
        "strengthen-binding",
    }


def test_an_outcome_with_no_anchor_is_refused(tmp_path: Path) -> None:
    """With magnitude gone there is no unanchored tier left to fall back to.

    Both layers, because round 3 found this test only ever reached the writer's
    `_nonblank` guard -- whose message also contains "anchor", so the regex
    matched an unrelated earlier failure and `anchor_shape_error`'s blank branch
    was never exercised. A blank anchor reaching the ledger by hand edit would
    have validated.
    """
    path = _seeded(tmp_path)
    for anchor in ("", "   "):
        with pytest.raises(ValueError, match="non-empty non-whitespace"):
            _score(tmp_path, path, outcome="read-but-not-applied", anchor=anchor)
    assert json.loads(path.read_text(encoding="utf-8"))["score_events"] == []
    # The validator's own arm, reached directly rather than through the writer.
    for anchor in ("", "   ", None, 7):
        assert outcome_lib.anchor_shape_error("read-but-not-applied", anchor) is not None
    assert outcome_lib.anchor_shape_error("read-but-not-applied", "it did not land") is None


def test_the_legacy_scalar_shape_cannot_come_back_once_an_outcome_lands(tmp_path: Path) -> None:
    """One-way, and held by two independent refusals rather than a version flag."""
    path = _seeded(tmp_path)
    _score(tmp_path, path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["score_events"].append(
        _score_event(event_id="regression", session_id="session-a", score=3)
    )
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="retired legacy-scalar shape"):
        _validate(tmp_path)


# --- SC6: "a session scoring lessons from two origin retros satisfies
# --- check_lesson_evaluation_continuity.py"


def _reconcile(score_events: list[dict], *, declaring: str, count: int) -> dict:
    return reconcile.reconcile_records(
        retros=[
            (
                declaring,
                {"status": "effect-recorded", "session_id": "s-1", "score_event_count": count},
            )
        ],
        sessions={"s-1": {"snapshot_sha256": "a" * 64}},
        score_events=score_events,
        receipts={"s-1": {"emitted_at": "2026-08-15T00:00:00Z"}},
        receipt_violations=[],
        as_of=date(2026, 8, 15),
        recurrence_sources={},
    )


def test_a_session_scoring_two_origin_retros_no_longer_violates(tmp_path: Path) -> None:
    """#631, reproduced exactly as reported and then cleared.

    Two LEGACY events whose lessons originate in two different retros, both in
    one session. `record_lesson_score.py` accepted only a lesson's own origin as
    `source_retro`, so `session_scores` was 2 while `matching` could be at most 1
    for ANY declaring path -- the violation was guaranteed for every retro that
    could claim the session, and no disposition could clear it.
    """
    events = [
        {
            "event_id": "durable-proof-lag",
            "session_id": "s-1",
            "lesson_id": "durable-proof-lag",
            "source_retro": "charness-artifacts/retro/2026-08-08-workerd-crash-repair.md",
            "score": 1,
        },
        {
            "event_id": "recorded-not-selected",
            "session_id": "s-1",
            "lesson_id": "recorded-not-selected",
            "source_retro": "charness-artifacts/retro/2026-08-14-review-queue-and-sweep-retro.md",
            "score": 1,
        },
    ]
    report = _reconcile(events, declaring="charness-artifacts/retro/2026-08-14-both.md", count=2)

    assert [item["id"] for item in report["violations"]] == []
    assert report["ok"] is True


def test_a_genuinely_foreign_encounter_still_fails(tmp_path: Path) -> None:
    """The check keeps the failure it exists for; only the false positive goes.

    An OUTCOME event names the retro that records the encounter, so one citing a
    retro that does not claim this session is a real attribution error -- exactly
    what `foreign-score-source` was written to catch and could not distinguish
    from #631's legitimate case.
    """
    events = [
        outcome_event(
            event_id="elsewhere",
            session_id="s-1",
            lesson_id="a",
            source_retro="charness-artifacts/retro/2026-08-15-somebody-elses.md",
        )
    ]
    report = _reconcile(events, declaring="charness-artifacts/retro/2026-08-15-mine.md", count=0)

    assert "foreign-score-source" in {item["id"] for item in report["violations"]}


def test_not_consulted_requires_the_session_to_have_committed_the_class() -> None:
    """The third asymmetry, enforced where the retro exists.

    Without this precondition `not-consulted` is trivially true of every lesson a
    session had no occasion to use, and a ten-lesson presentation would emit ten
    `strengthen-binding` signals per session for lessons that were merely
    irrelevant.
    """
    declaring = "charness-artifacts/retro/2026-08-15-mine.md"
    events = [
        outcome_event(
            event_id="never-revisited",
            session_id="s-1",
            lesson_id="a",
            source_retro=declaring,
            outcome="not-consulted",
        )
    ]
    unrecurred = _reconcile(events, declaring=declaring, count=1)
    assert "unrecurred-encounter" in {item["id"] for item in unrecurred["violations"]}

    recurred = reconcile.reconcile_records(
        retros=[
            (
                declaring,
                {"status": "effect-recorded", "session_id": "s-1", "score_event_count": 1},
            )
        ],
        sessions={"s-1": {"snapshot_sha256": "a" * 64}},
        score_events=events,
        receipts={"s-1": {"emitted_at": "2026-08-15T00:00:00Z"}},
        receipt_violations=[],
        as_of=date(2026, 8, 15),
        recurrence_sources={"a": {declaring}},
    )
    assert recurred["violations"] == []
    # And the outcomes that make no recurrence claim are never held to it, which
    # is what keeps this a precondition rather than a blanket tax.
    for outcome in sorted(set(outcome_lib.SCORE_OUTCOMES) - outcome_lib.RECURRENCE_ASSERTING_OUTCOMES):
        free = _reconcile(
            [
                outcome_event(
                    event_id=outcome,
                    session_id="s-1",
                    lesson_id="a",
                    source_retro=declaring,
                    outcome=outcome,
                )
            ],
            declaring=declaring,
            count=1,
        )
        assert [item["id"] for item in free["violations"]] == [], outcome


# --- SC7: "the archive/resurrection/graduation slot is reached from its
# --- production caller, and the check fails when that caller is absent"


def _review(repo: Path) -> dict:
    """The review payload, read in-process.

    What SC7 needs from the review is the COMMAND it emits; whether the CLI
    wrapper serialises that payload is `test_lesson_lifecycle_review.py`'s
    question and is already covered there. Reading it in-process keeps this
    file's only real boundary the one that matters.
    """
    return _review_module.build_lifecycle_review(repo)


def test_the_resurrection_slot_is_reached_through_the_review_that_briefs_it(
    tmp_path: Path,
) -> None:
    """SC7, exercised through the PRODUCTION CALLER rather than by direct call.

    A direct call to `record_lesson_lifecycle.py` is explicitly not acceptance for
    this criterion -- that is the #586 shape where a slot has a test and no
    caller, which is exactly how the archive bucket stayed structurally empty for
    the entire life of the ledger while three writers sat there validating.

    So this test never names the writer. It asks the review what to run, runs
    THAT, and then asks the preview whether the slot filled. If the review stops
    emitting the command, `archive` below is empty and this fails at that line --
    which is the "fails when the caller is absent" half of the criterion.
    """
    path = _seeded(tmp_path, with_index=True)
    # Deliberately OUTSIDE the retro directory: a new file in there is a new
    # retro artifact, which staleness-checks the selection index this review
    # renders over. The lifecycle contract wants a reviewed decision document,
    # not specifically a retro.
    decision = tmp_path / "quality-review.md"
    decision.write_text("# Quality Review\n", encoding="utf-8")

    reviewed = _review(tmp_path)["lessons"]
    assert [item["lesson_id"] for item in reviewed] == ["a"]
    archive = [
        template
        for template in reviewed[0]["lifecycle_command_templates"]
        if "--action archive" in template
    ]
    assert archive, "the review must brief a runnable archive move, not just a judgment"
    # Only `archive` is offered while the lesson is active: offering `resurrect`
    # here would route an operator to a guaranteed state-machine refusal.
    assert not any("--action resurrect" in t for t in reviewed[0]["lifecycle_command_templates"])

    argv = shlex.split(archive[0])
    argv[argv.index("--decision-ref") + 1] = str(decision.relative_to(tmp_path))
    argv[argv.index("--rationale") + 1] = "Reviewed: this prose belongs in a validator."
    argv[argv.index("--repo-root") + 1] = str(tmp_path)
    applied = subprocess.run([sys.executable, *argv[1:]], capture_output=True, text=True, check=False)
    assert applied.returncode == 0, applied.stderr

    # The slot, now reachable: `state == "archived"` exists for the first time, so
    # the archive bucket has something to draw and the fallback stands down.
    assert json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["state"] == "archived"
    rendered = preview.build_lesson_selection_preview(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        seed="sc7",
    )
    assert rendered["bucket_counts"]["archive"] == 1
    assert rendered["bucket_counts"]["archive_fallback_uncertainty"] == 0
    assert [item["lesson_id"] for item in rendered["items"]] == ["a"]

    # THE ROUND TRIP, EXECUTED rather than asserted as a string. An earlier
    # version stopped at "a resurrect template is present", and a bounded reviewer
    # showed that shape could not see the real defect: the emitted `--event-id`
    # was constant per lesson, so the third move died on `duplicate lifecycle
    # event_id`. Running archive -> resurrect -> archive is what catches it.
    for expected_action, expected_state in (("resurrect", "active"), ("archive", "archived")):
        templates = _review(tmp_path)["lessons"][0]["lifecycle_command_templates"]
        move = [t for t in templates if f"--action {expected_action}" in t]
        assert move, f"the review must offer `{expected_action}` from the current state"
        argv = shlex.split(move[0])
        argv[argv.index("--decision-ref") + 1] = str(decision.relative_to(tmp_path))
        argv[argv.index("--rationale") + 1] = f"Reviewed: {expected_action}."
        argv[argv.index("--repo-root") + 1] = str(tmp_path)
        applied = subprocess.run(
            [sys.executable, *argv[1:]], capture_output=True, text=True, check=False
        )
        assert applied.returncode == 0, applied.stderr
        assert (
            json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["state"] == expected_state
        )


def test_the_graduation_move_is_offered_only_with_two_evidence_sessions(tmp_path: Path) -> None:
    """SC7's third slot, which an earlier version of this slice left unwired.

    `record_contract_graduation_proposal.py` requires two distinct evidence
    sessions, so the review offers the command only when the lesson has them --
    otherwise it would route an operator to a guaranteed refusal, which is the
    defect the archive template was repaired for. Absent key means "not yet
    proposable", never "forgotten".
    """
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "2026-08-15-one.md", "a")
    _retro(tmp_path, "2026-08-15-two.md", "a")
    path = _ledger(
        tmp_path,
        session_events=[_session_event(session_id="s-0"), _session_event(session_id="s-1")],
    )
    _write_index(tmp_path, path.parent)

    _score(tmp_path, path, event_id="e-0", session_id="s-0",
           source_retro="charness-artifacts/retro/2026-08-15-one.md")
    assert "graduation_command_template" not in _review(tmp_path)["lessons"][0]

    _score(tmp_path, path, event_id="e-1", session_id="s-1",
           source_retro="charness-artifacts/retro/2026-08-15-two.md")
    template = _review(tmp_path)["lessons"][0]["graduation_command_template"]
    assert "record_contract_graduation_proposal.py" in template
    # Both evidence sessions named, because that is the writer's own floor and a
    # template naming one would be refused on submission.
    assert template.count("--evidence-session-id") == 2
    assert "--displacement-unit-id" in template
    # The register refuses a proposal whose source_retro is not the lesson's
    # seeded value, so this is emitted as a real value rather than a placeholder.
    assert "--source-retro charness-artifacts/retro/source.md" in template

    # ...and an ARCHIVED lesson is not proposable, the same way it is not offered
    # `archive`. Round 3 found `_graduation_command` had no state filter, so the
    # report could brief "propose this for graduation" for a lesson it was
    # simultaneously briefing as archived. Reached here because this is the one
    # fixture that satisfies the evidence floor AND can be archived.
    decision = tmp_path / "quality-review.md"
    decision.write_text("# Quality Review\n", encoding="utf-8")
    archive = [
        line
        for line in _review(tmp_path)["lessons"][0]["lifecycle_command_templates"]
        if "--action archive" in line
    ][0]
    argv = shlex.split(archive)
    argv[argv.index("--decision-ref") + 1] = "quality-review.md"
    argv[argv.index("--rationale") + 1] = "Reviewed: archived."
    argv[argv.index("--repo-root") + 1] = str(tmp_path)
    applied = subprocess.run([sys.executable, *argv[1:]], capture_output=True, text=True, check=False)
    assert applied.returncode == 0, applied.stderr
    assert "graduation_command_template" not in _review(tmp_path)["lessons"][0]


def test_one_lesson_cannot_carry_two_encounters_in_one_session(tmp_path: Path) -> None:
    """The hole the #631 narrowing opened, closed.

    The ledger's uniqueness key is `(source_retro, lesson_id)` with no session
    component, and a legacy citation is valid against ANY retro carrying the class
    tag. So one lesson could take two legacy encounters in one session via two
    tagged origins, and once `foreign_scores` stopped reading legacy citations,
    nothing compared them to the declaring retro any more.
    """
    declaring = "charness-artifacts/retro/2026-08-15-mine.md"
    events = [
        {
            "event_id": f"legacy-{index}",
            "session_id": "s-1",
            "lesson_id": "a",
            "source_retro": f"charness-artifacts/retro/2026-08-0{index}-origin.md",
            "score": 2,
        }
        for index in (1, 2)
    ]
    report = _reconcile(events, declaring=declaring, count=2)

    assert "duplicate-encounter" in {item["id"] for item in report["violations"]}
    # One encounter for that lesson is still fine, so this is a duplicate rule
    # rather than a ban on legacy events.
    assert [
        item["id"] for item in _reconcile(events[:1], declaring=declaring, count=1)["violations"]
    ] == []


def test_the_write_time_refusals_cover_what_the_gate_would_otherwise_strand(
    tmp_path: Path,
) -> None:
    """Both append-only traps, refused before they can be committed.

    Round 2 found that each of these checks existed only at gate time, where the
    ledger's append-only rule makes them unclearable: the offending event cannot
    be rewritten, so the only escapes are a permanently red gate or asserting the
    very thing the check exists to verify. Neither refusal had a test.
    """
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])

    # `not-consulted` against a retro with no `recurrence-class: a` bullet.
    with pytest.raises(ValueError, match="must already carry a `recurrence-class"):
        _score(
            tmp_path,
            path,
            outcome="not-consulted",
            source_retro="charness-artifacts/retro/2026-08-15-untagged.md",
        )
    assert json.loads(path.read_text(encoding="utf-8"))["score_events"] == []

    # ...and the same outcome against a retro that DOES carry it is accepted, so
    # this is a precondition rather than a ban on the outcome.
    _retro(tmp_path, "2026-08-15-tagged.md", "a")
    assert _score(
        tmp_path,
        path,
        outcome="not-consulted",
        source_retro="charness-artifacts/retro/2026-08-15-tagged.md",
    )["outcome"] == "not-consulted"

    # A second encounter for the same lesson in the same session, whatever retro
    # it cites -- the shape `(source_retro, lesson_id)` uniqueness lets through.
    _retro(tmp_path, "2026-08-15-other.md", "a")
    with pytest.raises(ValueError, match="already records an encounter"):
        _score(
            tmp_path,
            path,
            event_id="second-encounter",
            source_retro="charness-artifacts/retro/2026-08-15-other.md",
        )
    assert len(json.loads(path.read_text(encoding="utf-8"))["score_events"]) == 1


@pytest.mark.parametrize(
    "citation",
    [
        "charness-artifacts/retro/../../../tmp/escape.md",
        "charness-artifacts/retro/recent-lessons.md",
        "charness-artifacts/retro/nested/a.md",
        "charness-artifacts/retro/./a.md",
        "notes/a.md",
        "charness-artifacts/retro/a.txt",
    ],
)
def test_a_score_citation_outside_the_canonical_retro_shape_is_refused(
    tmp_path: Path, citation: str
) -> None:
    """Each of these was accepted by the loose prefix check round 1 replaced.

    They matter because the ledger cannot rewrite a committed score event, so a
    citation that no disposition can ever claim -- an escaped path, a file that is
    structurally not a retro, a typo'd spelling -- is a permanent gate violation.
    """
    path = _seeded(tmp_path)
    with pytest.raises(ValueError, match="must be a repo-relative"):
        _score(tmp_path, path, source_retro=citation)
    assert json.loads(path.read_text(encoding="utf-8"))["score_events"] == []


def test_an_encounter_that_did_not_work_lowers_the_ranking_statistic(tmp_path: Path) -> None:
    """`valence` returning -1, which nothing proved.

    Round 3 mutated it to `return 1` and the whole suite stayed green: the writer
    and the replay call the SAME function, so `lessons != replayed` is blind to
    it, and no fixture held a non-`changed-an-action` outcome event. This is the
    field the selection ranking is built on, and "the ledger had no path in for
    negative signal" is the defect the vocabulary exists to remove -- so a
    negative that does not move score_total DOWN is the whole thing failing
    silently.
    """
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "2026-08-15-r0.md", "a")
    _retro(tmp_path, "2026-08-15-r1.md", "a")
    path = _ledger(
        tmp_path,
        session_events=[_session_event(session_id="s-0"), _session_event(session_id="s-1")],
    )
    _score(tmp_path, path, event_id="e-0", session_id="s-0",
           source_retro="charness-artifacts/retro/2026-08-15-r0.md")
    assert json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["score_total"] == 1

    _score(tmp_path, path, event_id="e-1", session_id="s-1",
           source_retro="charness-artifacts/retro/2026-08-15-r1.md",
           outcome="read-but-not-applied", anchor="in view at the decision and still not applied")
    lesson = json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]
    assert lesson["score_total"] == 0, "a failing encounter must cancel a working one"
    assert lesson["score_count"] == 2
    # And directly, so every arm is pinned rather than only the two used above.
    assert outcome_lib.valence({"outcome": "changed-an-action"}) == 1
    for failing in ("read-but-not-applied", "not-consulted", "pushed-a-wrong-action"):
        assert outcome_lib.valence({"outcome": failing}) == -1, failing
    assert outcome_lib.valence({"score": 3}) == 1
    assert outcome_lib.valence({"score": -3}) == -1


def test_each_outcome_routes_to_its_own_named_disposition() -> None:
    """The mapping, pinned VALUE BY VALUE rather than as a set.

    Round 3 showed the set assertion survives swapping `changed-an-action` and
    `not-consulted`'s dispositions -- which would route a lesson that worked to
    `strengthen-binding` and one that was never consulted to `graduate`. The
    routing is the load-bearing half of the split; a set only pins that three
    dispositions exist.
    """
    assert outcome_lib.SCORE_OUTCOMES == {
        "changed-an-action": "graduate",
        "read-but-not-applied": "rewrite-in-place",
        "not-consulted": "strengthen-binding",
        "pushed-a-wrong-action": "rewrite-in-place",
    }
    # The one that must never drift: the outcome asserting the lesson WORKED is
    # the only one feeding `graduate`.
    assert outcome_lib.SCORE_OUTCOMES[outcome_lib.WORKING_OUTCOME] == "graduate"
    assert [o for o, d in outcome_lib.SCORE_OUTCOMES.items() if d == "graduate"] == [
        outcome_lib.WORKING_OUTCOME
    ]


def test_graduation_is_not_offered_on_legacy_or_failing_evidence(tmp_path: Path) -> None:
    """The round-2 narrowing, which had no negative case.

    Round 3 deleted the `changed-an-action` filter and this file stayed green,
    because the only graduation test used two working sessions. The filter exists
    because `graduate` is the disposition `changed-an-action` routes to, so
    offering a promote move on legacy or failing encounters hands quality
    evidence that appears nowhere in `by_disposition`.
    """
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "2026-08-15-one.md", "a")
    _retro(tmp_path, "2026-08-15-two.md", "a")
    path = _ledger(
        tmp_path,
        session_events=[_session_event(session_id="s-0"), _session_event(session_id="s-1")],
    )
    _write_index(tmp_path, path.parent)

    _score(tmp_path, path, event_id="e-0", session_id="s-0",
           source_retro="charness-artifacts/retro/2026-08-15-one.md")
    _score(tmp_path, path, event_id="e-1", session_id="s-1",
           source_retro="charness-artifacts/retro/2026-08-15-two.md",
           outcome="read-but-not-applied", anchor="in view at the decision and still not applied")

    lesson = _review(tmp_path)["lessons"][0]
    assert lesson["score_count"] == 2, "two sessions carry encounters"
    assert "graduation_command_template" not in lesson, (
        "two sessions, but only one of them changed an action -- not graduate evidence"
    )


def test_by_disposition_reports_the_routing_the_author_chose(tmp_path: Path) -> None:
    """`by_disposition`, which had no test at all.

    It could `return {}` silently while the module docstring calls it "the answer
    to the question quality actually asks". Every disposition key is present even
    when empty, and the legacy cohort routes NOWHERE -- inferring a disposition
    from events recorded before `changed-an-action` was expressible would
    manufacture evidence nobody gave.
    """
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "2026-08-15-one.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event(session_id="s-0")])
    _write_index(tmp_path, path.parent)

    empty = _review(tmp_path)["by_disposition"]
    assert empty == {"graduate": [], "rewrite-in-place": [], "strengthen-binding": []}, (
        "every disposition key present even with nothing to report"
    )

    _score(tmp_path, path, event_id="e-0", session_id="s-0",
           source_retro="charness-artifacts/retro/2026-08-15-one.md",
           outcome="read-but-not-applied", anchor="in view at the decision and still not applied")
    assert _review(tmp_path)["by_disposition"] == {
        "graduate": [],
        "rewrite-in-place": ["a"],
        "strengthen-binding": [],
    }


def test_the_named_gate_runs_the_precondition_over_a_real_ledger(tmp_path: Path, monkeypatch) -> None:
    """SC6's integration half, through `check_lesson_evaluation_continuity.py`.

    SC6 names that command, and its Acceptance Check labels the proof
    `integration` -- but every existing proof called the pure reconciler directly
    with hand-supplied inputs, so round 3 could replace
    `recurrence_sources=_records.recurrence_sources(repo_root)` in the CLI with
    `{}` and leave the suite green. That is the "reachable only from its own
    test" class SC7 exists to refuse, sitting on the precondition round 2 added.

    `{}` is MAXIMALLY strict, not inert: it makes every `not-consulted` encounter
    unrecurred. So a properly tagged encounter passing this gate is exactly the
    assertion that kills the mutation.
    """
    _retro(tmp_path, "source.md", "a")
    output = tmp_path / "charness-artifacts/retro"
    declaring = "2026-08-15-encounter.md"
    # The recording retro carries BOTH the recurrence tag the precondition reads
    # and the disposition line the reconciler claims the session with.
    (output / declaring).write_text(
        "# Session Retro\nDate: 2026-08-15\n\n"
        "## North Star Alignment\n\n- P1 held.\n\n"
        "## Waste\n\n- the class came up again (recurrence-class: a)\n\n"
        "## Lesson Evaluation\n\n"
        + continuity.disposition_line(
            {"status": "effect-recorded", "session_id": "session-a", "score_event_count": 1}
        )
        + "\n\n## Next Improvements\n\n- workflow: do it\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/" + declaring + "\n",
        encoding="utf-8",
    )
    session = _session_event()
    path = _ledger(tmp_path, session_events=[session])
    _write_index(tmp_path, output)

    rendered = b"preview\n"
    continuity.write_bundle(continuity.bundle_path(output, "session-a"), rendered)
    continuity.write_receipt(
        continuity.receipt_path(output, "session-a"),
        continuity.build_receipt(
            session_id="session-a",
            snapshot_sha256=session["snapshot_sha256"],
            stdout_bytes=rendered,
            emitted_at="2026-08-15T00:00:00Z",
        ),
    )
    _score(
        tmp_path,
        path,
        source_retro=f"charness-artifacts/retro/{declaring}",
        outcome="not-consulted",
        anchor="never revisited it when the class came up",
    )

    report = checker.build_report(tmp_path, as_of=date(2026, 8, 16))

    assert report["violations"] == [], report["violations"]
    assert report["ok"] is True
    assert report["status_counts"]["effect-recorded"] == 1
    # The mutation this test exists to kill, asserted directly: hand the pure
    # core an empty map and the same encounter is refused.
    starved = reconcile.reconcile_records(
        retros=[(f"charness-artifacts/retro/{declaring}",
                 {"status": "effect-recorded", "session_id": "session-a", "score_event_count": 1})],
        sessions={"session-a": session},
        score_events=json.loads(path.read_text(encoding="utf-8"))["score_events"],
        receipts={"session-a": continuity.build_receipt(
            session_id="session-a", snapshot_sha256=session["snapshot_sha256"],
            stdout_bytes=rendered, emitted_at="2026-08-15T00:00:00Z")},
        receipt_violations=[],
        as_of=date(2026, 8, 16),
        recurrence_sources={},
    )
    assert "unrecurred-encounter" in {item["id"] for item in starved["violations"]}


def test_the_emitted_graduation_command_is_accepted_by_the_register(tmp_path: Path) -> None:
    """SC7's THIRD slot, executed rather than asserted.

    Archive and resurrect are run end-to-end above, and this file's own docstring
    records why "a template is present" was rejected as proof for them. Round 3
    caught graduation still sitting in exactly that rejected shape: the flags
    happen to line up with the writer's argparse today, so a renamed or reordered
    flag would ship a template that dies on `unrecognized arguments` with a green
    suite. Running it closes the last of the three slots SC7 names.
    """
    from tests.test_contract_register import _contract_sources, _register

    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "2026-08-15-one.md", "a")
    _retro(tmp_path, "2026-08-15-two.md", "a")
    _contract_sources(tmp_path)
    path = _ledger(
        tmp_path,
        session_events=[_session_event(session_id="s-0"), _session_event(session_id="s-1")],
    )
    _write_index(tmp_path, path.parent)
    _register(tmp_path)
    _score(tmp_path, path, event_id="e-0", session_id="s-0",
           source_retro="charness-artifacts/retro/2026-08-15-one.md")
    _score(tmp_path, path, event_id="e-1", session_id="s-1",
           source_retro="charness-artifacts/retro/2026-08-15-two.md")

    template = _review(tmp_path)["lessons"][0]["graduation_command_template"]
    argv = shlex.split(template)
    argv[argv.index("--repo-root") + 1] = str(tmp_path)
    argv[argv.index("--target-path") + 1] = "AGENTS.md"
    # A NEW heading: the register refuses a proposal whose unit id collides with
    # an existing one, which is the conservation rule doing its job.
    argv[argv.index("--target-heading") + 1] = "Check Premises Against Source"
    argv[argv.index("--rationale") + 1] = "This belongs in the always-loaded contract."
    # DISPLACEMENT IS BUDGET-CONDITIONAL, and this fixture proves which branch it
    # is in rather than assuming: the seeded register is at its fixed unit budget,
    # so the register refuses the proposal without a displacement. Filled with a
    # real seeded unit id, because it also refuses any id that is not already
    # known. Deleting the flag here is what the placeholder tells an operator to
    # do only when the budget is NOT full -- asserted below.
    argv[argv.index("--displacement-unit-id") + 1] = "AGENTS.md#alpha"

    proposed = subprocess.run(
        [sys.executable, *argv[1:]], capture_output=True, text=True, check=False
    )

    assert proposed.returncode == 0, proposed.stderr
    assert yaml.safe_load(proposed.stdout)["lesson_id"] == "a"

    # The other branch of the same rule: drop the displacement and the full-budget
    # register refuses. This is why the template emits the flag unconditionally
    # with a placeholder that says to delete it, rather than omitting it.
    drop = argv.index("--displacement-unit-id")
    without = [*argv[:drop], *argv[drop + 2 :]]
    without[without.index("--proposal-id") + 1] = "graduate-a-again"
    # A fresh target too, so the refusal we observe is the BUDGET rule and not the
    # identity rule firing first on the unit the accepted proposal just claimed.
    without[without.index("--target-heading") + 1] = "Score What Actually Bit"
    refused = subprocess.run(
        [sys.executable, *without[1:]], capture_output=True, text=True, check=False
    )
    assert refused.returncode == 1
    assert "unit budget" in refused.stderr
