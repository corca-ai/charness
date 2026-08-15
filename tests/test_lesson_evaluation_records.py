"""What the retro router keeps when the frozen bundle stops being readable.

`lesson_evaluation_records_lib` serves the GATE and the ROUTER from one scan, and
the two owe different things to a damaged artifact. The gate reports a violation.
The router still has to send the author to the session that owes a score, because
`unclaimed-emission` will fail this repo tomorrow either way -- so the convenience
half of the row (the emitted wording) is allowed to disappear and the routing half
is not. These tests pin that split at the seam where it is decided.

Never touches the authoring repo's own ledger: it is append-only with a committed
prefix diffed against `git show HEAD:<path>`, so every fixture lands in tmp_path.
"""

from __future__ import annotations

from pathlib import Path

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_evaluation_records_lib as records
from tests.test_lesson_ledger import _ledger, _retro, _session_event

# After `continuity.ACTIVATION_DATE`, so the receipt is inside the cohort
# `unclaimed_receipted_sessions` considers at all.
EMITTED_AT = "2026-08-15T09:30:00+00:00"


def _receipted_session(repo: Path, *, stdout_bytes: bytes, session_id: str = "session-a") -> Path:
    """A declared session whose receipt attests exactly `stdout_bytes`.

    Written through `build_receipt`/`write_bundle` rather than by driving
    `open_lesson_session.py`, because that renderer can only emit its own valid
    UTF-8 output and the byte sequence under test here is one it would never
    produce. The receipt is still the real one: same builder, same digests, so it
    passes `validate_receipt` exactly as a declared session's does.
    """
    output_dir = repo / "charness-artifacts/retro"
    session = _session_event(session_id=session_id)
    _retro(repo, "source.md", "a")
    _ledger(repo, session_events=[session])
    continuity.write_bundle(continuity.bundle_path(output_dir, session_id), stdout_bytes)
    continuity.write_receipt(
        continuity.receipt_path(output_dir, session_id),
        continuity.build_receipt(
            session_id=session_id,
            snapshot_sha256=session["snapshot_sha256"],
            stdout_bytes=stdout_bytes,
            emitted_at=EMITTED_AT,
        ),
    )
    return output_dir


def test_a_bundle_that_is_not_text_drops_the_wording_and_keeps_the_routing(
    tmp_path: Path,
) -> None:
    """A digest-matching bundle that is not UTF-8 is the one damage a receipt cannot see.

    `validate_receipt` re-digests BYTES, so this receipt is valid and the session
    stays receipted and unclaimed -- unlike an edited bundle, which fails its digest
    and demotes the whole session out of the routing. The only thing that breaks is
    the decode, and the row it feeds is convenience: dropping the emitted wording
    costs the author a re-derivation, while dropping the row would cost them the
    session the continuity gate is about to fail this repo over.
    """
    _receipted_session(tmp_path, stdout_bytes=b"- a \xff\xfe not decodable as utf-8\n")

    payload = records.lesson_session_routing(
        tmp_path, source_retro="charness-artifacts/retro/2026-08-15-session-retro.md"
    )

    assert payload["state"] == "evaluated"
    session = payload["sessions"][0]
    assert session["session_id"] == "session-a"
    # The routing survives whole: the frozen ids, and a command that can be run.
    assert session["lesson_ids"] == ["a"]
    assert session["unscored_lesson_ids"] == ["a"]
    lesson = session["lessons"][0]
    assert lesson["lesson_id"] == "a"
    assert "--lesson-id a" in lesson["score_command_template"]
    # And the wording is ABSENT rather than empty or re-rendered from today's
    # selection, so a reader sees a missing text instead of another lesson's words.
    assert "lesson_text" not in lesson

    # The same fixture with decodable bytes DOES carry the wording, so the absence
    # above is the decode failing rather than the bundle never being read.
    readable = tmp_path / "readable"
    _receipted_session(readable, stdout_bytes="- a — useful lesson\n".encode("utf-8"))
    assert (
        records.lesson_session_routing(readable)["sessions"][0]["lessons"][0]["lesson_text"]
        == "useful lesson"
    )


def test_a_session_row_without_a_receipt_still_routes_its_frozen_lessons(
    tmp_path: Path,
) -> None:
    """`_session_row` takes `receipt: dict | None`, and `None` must not cost the row.

    Unreachable from `lesson_session_routing` today -- `unclaimed` is derived from
    the receipts mapping, so every routed session has one -- but the parameter is
    typed optional and the router's contract is that the bundle is best-effort. A
    caller that has a session and no receipt gets the ids, the bundle path, and a
    runnable score command; it just gets no wording, because there is no attested
    artifact to take wording from.
    """
    output_dir = _receipted_session(tmp_path, stdout_bytes="- a — useful lesson\n".encode("utf-8"))
    sessions, score_events = records.load_validated_ledger(tmp_path)

    row = records._session_row(
        repo_root=tmp_path,
        session_id="session-a",
        sessions=sessions,
        score_events=score_events,
        output_dir=output_dir,
        source_retro="charness-artifacts/retro/2026-08-15-session-retro.md",
        receipt=None,
    )

    assert row["lesson_ids"] == ["a"]
    assert row["bundle_path"] == "charness-artifacts/retro/lesson-session-receipts/session-a.md"
    assert row["existing_score_event_count"] == 0
    assert "lesson_text" not in row["lessons"][0]
    assert "record_lesson_score.py" in row["lessons"][0]["score_command_template"]
    # The solicitation is what makes the routing worth keeping: it names WHAT to
    # judge, and it does not come from the bundle.
    assert "WRONG action" in row["solicitation"]["pushed_a_wrong_action"]
