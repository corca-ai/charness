from __future__ import annotations

import contextlib
import copy
import json
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

from scripts import lesson_ledger_lib as ledger
from scripts import lesson_ledger_writer_lib as writer
from scripts import lesson_score_outcome_lib as outcome_lib
from scripts import record_lesson_score as scorer
from scripts import record_lesson_session as session_recorder
from tests.lesson_ledger_fixtures import blank_lesson, outcome_event
from tests.lesson_ledger_fixtures import materialize as _materialize
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# Satisfies the `changed-an-action` counterfactual bar, so tests about SESSION
# binding do not have to restate the anchor rule to exercise it.
ANCHOR = outcome_event(event_id="x", session_id="x", lesson_id="x", source_retro="x")["anchor"]


def _retro(repo: Path, name: str, lesson_class: str) -> None:
    path = repo / "charness-artifacts/retro" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: {lesson_class})\n",
        encoding="utf-8",
    )


def _score_event(
    *,
    event_id: str = "score-a",
    source: str = "charness-artifacts/retro/source.md",
    score: int = 0,
    **extra: object,
) -> dict:
    event = {"event_id": event_id, "source_retro": source, "lesson_id": "a", "score": score}
    event.update(extra)
    return event


def _session_event(
    *, session_id: str = "session-a", lesson_ids: list[str] | None = None, seed: str = "seed-a"
) -> dict:
    ids = ["a"] if lesson_ids is None else lesson_ids
    snapshot = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "selection_policy_version": 1,
        "seed": seed,
        "eligible_count": len(ids),
        "bucket_counts": {
            "recent": len(ids),
            "value": 0,
            "uncertainty": 0,
            "archive": 0,
            "archive_fallback_uncertainty": 0,
        },
        "lesson_ids": ids,
    }
    return {
        "session_id": session_id,
        "snapshot": snapshot,
        "snapshot_sha256": ledger.snapshot_sha256(snapshot),
    }


def _payload(
    *,
    source: str = "charness-artifacts/retro/source.md",
    score_events: list[dict] | None = None,
    session_events: list[dict] | None = None,
) -> dict:
    events = [] if score_events is None else score_events
    return {
        "kind": ledger.KIND,
        "schema_version": ledger.SCHEMA_VERSION,
        "transitions": [
            {"sequence": 1, "transition_id": "seed-a", "lesson_id": "a", "source_retro": source}
        ],
        "active_lesson_budget": ledger.ACTIVE_LESSON_BUDGET,
        "lifecycle_events": [],
        "session_events": [] if session_events is None else session_events,
        "score_events": events,
        "lessons": {"a": blank_lesson(source, "seed-a")},
    }


def _ledger(repo: Path, **kwargs: object) -> Path:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_materialize(_payload(**kwargs))), encoding="utf-8")
    return path


def _validate(repo: Path) -> dict:
    return ledger.validate_lesson_ledger(
        repo_root=repo,
        output_dir=repo / "charness-artifacts/retro",
        summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_ledger_replays_session_cited_scores_and_checker_cli(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(
        tmp_path,
        session_events=[_session_event()],
        score_events=[_score_event(score=2, anchor="decision evidence", session_id="session-a")],
    )
    assert _validate(tmp_path) == {
        "lesson_count": 1,
        "transition_count": 1,
        "score_event_count": 1,
        "lifecycle_event_count": 0,
        "active_lesson_count": 1,
        "path": "charness-artifacts/retro/lesson-ledger.json",
    }
    checker = load_script_module(
        "check_lesson_ledger_for_test", ROOT / "scripts/check_lesson_ledger.py"
    )
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(tmp_path)])
    assert checker.main() == 0
    assert capsys.readouterr().out == (
        "Validated lesson ledger: 1 lessons, 1 active, 1 seed transitions, "
        "0 lifecycle events.\n"
    )
    # ONE, not two: magnitude is retired from both vocabularies, so a legacy `+2`
    # contributes the sign of its scalar and never its size.
    assert json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["score_total"] == 1


def test_ledger_rejects_closed_transition_score_and_projection_shapes(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    cases: list[tuple[dict, str]] = []
    broken_transition = _payload()
    broken_transition["transitions"] = [None]
    cases.append((broken_transition, "deferred fields"))
    wrong_schema = _payload()
    wrong_schema["schema_version"] = 2
    cases.append((wrong_schema, "schema version"))
    unknown_top_level = _payload()
    unknown_top_level["budget"] = 1
    cases.append((unknown_top_level, "schema version"))
    bad_score = _payload(
        session_events=[_session_event()],
        score_events=[_score_event(score=True, session_id="session-a")],
    )
    cases.append((bad_score, "integer"))
    bad_anchor = _payload(
        session_events=[_session_event()],
        score_events=[_score_event(anchor=" ", session_id="session-a")],
    )
    cases.append((bad_anchor, "non-whitespace"))
    projection = _payload()
    projection["lessons"]["a"]["score_total"] = 0.0
    cases.append((projection, "replayed fields"))
    for payload, message in cases:
        serialized = payload if payload is projection else _materialize(payload)
        path.write_text(json.dumps(serialized), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_session_snapshot_and_new_scores_are_coupled_without_rerendering(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "second.md", "a")
    session = _session_event()
    event = _score_event(
        event_id="new-score", session_id="session-a", score=2, anchor="decision evidence"
    )
    path = _ledger(tmp_path, session_events=[session], score_events=[event])
    assert _validate(tmp_path)["score_event_count"] == 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    invalids: list[tuple[dict, str]] = []
    unknown = copy.deepcopy(payload)
    unknown["score_events"][0]["session_id"] = "unknown"
    invalids.append((unknown, "unknown session"))
    missing = copy.deepcopy(payload)
    del missing["score_events"][0]["session_id"]
    # The refusal moved shape with the vocabulary: a legacy event missing
    # `session_id` is now a legacy KEY-SET refusal, and the message names both
    # shapes so an author who meant to write an outcome event is told so.
    invalids.append((missing, "legacy-scalar score event takes keys"))
    altered = copy.deepcopy(payload)
    altered["session_events"][0]["snapshot"]["seed"] = "other"
    invalids.append((altered, "snapshot_sha256"))
    duplicate = copy.deepcopy(payload)
    duplicate["session_events"].append(copy.deepcopy(session))
    invalids.append((duplicate, "duplicate session_id"))
    for invalid, message in invalids:
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_session_snapshot_refuses_invalid_counts_and_ids(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases: list[tuple[dict, str]] = []
    duplicate_ids = copy.deepcopy(payload)
    duplicate_ids["session_events"][0]["snapshot"]["lesson_ids"] = ["a", "a"]
    duplicate_ids["session_events"][0]["snapshot"]["eligible_count"] = 2
    duplicate_ids["session_events"][0]["snapshot"]["bucket_counts"]["recent"] = 2
    duplicate_ids["session_events"][0]["snapshot_sha256"] = ledger.snapshot_sha256(
        duplicate_ids["session_events"][0]["snapshot"]
    )
    cases.append((duplicate_ids, "ordered unique"))
    bad_counts = copy.deepcopy(payload)
    bad_counts["session_events"][0]["snapshot"]["bucket_counts"]["recent"] = 0
    bad_counts["session_events"][0]["snapshot_sha256"] = ledger.snapshot_sha256(
        bad_counts["session_events"][0]["snapshot"]
    )
    cases.append((bad_counts, "inconsistent snapshot"))
    bad_kind = copy.deepcopy(payload)
    bad_kind["session_events"][0]["snapshot"]["kind"] = "other"
    bad_kind["session_events"][0]["snapshot_sha256"] = ledger.snapshot_sha256(
        bad_kind["session_events"][0]["snapshot"]
    )
    cases.append((bad_kind, "invalid snapshot types"))
    boolean_schema = copy.deepcopy(payload)
    boolean_schema["session_events"][0]["snapshot"]["schema_version"] = True
    boolean_schema["session_events"][0]["snapshot_sha256"] = ledger.snapshot_sha256(
        boolean_schema["session_events"][0]["snapshot"]
    )
    cases.append((boolean_schema, "invalid snapshot types"))
    for invalid, message in cases:
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_session_recorder_freezes_current_preview_then_score_does_not_rerender_history(
    tmp_path: Path, monkeypatch
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    preview = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "seed": "recorded-seed",
        "eligible_count": 1,
        "bucket_counts": {
            "recent": 1,
            "value": 0,
            "uncertainty": 0,
            "archive": 0,
            "archive_fallback_uncertainty": 0,
        },
        "items": [
            {
                "lesson_id": "a",
                "lesson": "useful lesson",
                "latest_source_path": "charness-artifacts/retro/source.md",
            }
        ],
    }
    monkeypatch.setattr(
        session_recorder._preview, "build_lesson_selection_preview", lambda **_kwargs: preview
    )
    event = session_recorder.append_session(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        session_id="recorded",
        seed="recorded-seed",
    )
    assert event["snapshot"]["lesson_ids"] == ["a"]
    scorer.append_score(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id="after-recording",
        session_id="recorded",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        outcome="changed-an-action",
        anchor=ANCHOR,
    )
    monkeypatch.setattr(
        session_recorder._preview,
        "build_lesson_selection_preview",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("must not rerender history")),
    )
    assert _validate(tmp_path)["score_event_count"] == 1


def test_score_authoring_refuses_a_lesson_absent_from_an_existing_session(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "second.md", "b")
    payload = _payload(session_events=[_session_event(lesson_ids=["a"])])
    payload["transitions"].append(
        {
            "sequence": 2,
            "transition_id": "seed-b",
            "lesson_id": "b",
            "source_retro": "charness-artifacts/retro/second.md",
        }
    )
    payload["lessons"]["b"] = blank_lesson("charness-artifacts/retro/second.md", "seed-b")
    path = tmp_path / "charness-artifacts/retro/lesson-ledger.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert _validate(tmp_path)["lesson_count"] == 2
    before = path.read_bytes()
    with pytest.raises(ValueError, match="absent from session"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="wrong-session",
            session_id="session-a",
            lesson_id="b",
            source_retro="charness-artifacts/retro/second.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    assert path.read_bytes() == before



def test_score_authoring_requires_containing_session_and_leaves_refusals_unwritten(
    tmp_path: Path,
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])
    event = scorer.append_score(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id="event-a",
        session_id="session-a",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        outcome="changed-an-action",
        anchor=ANCHOR,
    )
    assert event["session_id"] == "session-a"
    assert _validate(tmp_path)["score_event_count"] == 1
    before = path.read_bytes()
    with pytest.raises(ValueError, match="unknown session"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="event-b",
            session_id="unknown",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    assert path.read_bytes() == before


def test_authoring_commands_refuse_invalid_inputs_and_empty_preview(
    tmp_path: Path, monkeypatch
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])
    with pytest.raises(ValueError, match="non-empty non-whitespace"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id=" ",
            session_id="session-a",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    # The retired scalar is not a value this writer can express any more, so the
    # refusal an author actually hits is an out-of-vocabulary outcome -- and the
    # message teaches the four questions rather than listing four slugs.
    with pytest.raises(ValueError, match="outcome must be one of"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="bad-outcome",
            session_id="session-a",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="+3",
            anchor=ANCHOR,
        )
    # The asymmetric bar, refused at AUTHORING time: a `changed-an-action` anchor
    # that names the action and not the counterfactual. This is the one outcome an
    # agent scoring its own session finds easiest and most flattering to claim.
    with pytest.raises(ValueError, match="would have gone otherwise"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unfalsifiable-positive",
            session_id="session-a",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor="it helped a lot",
        )
    # ...and the SAME anchor is accepted for an outcome that makes no
    # counterfactual claim, which is what makes the bar asymmetric rather than
    # just strict.
    assert scorer.append_score(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id="unanchored-negative-is-fine",
        session_id="session-a",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        outcome="read-but-not-applied",
        anchor="it helped a lot",
    )["outcome"] == "read-but-not-applied"
    with pytest.raises(ValueError, match="unseeded"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unseeded",
            session_id="session-a",
            lesson_id="other",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    with pytest.raises(ValueError, match="non-empty non-whitespace"):
        session_recorder.append_session(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            session_id=" ",
            seed="seed",
        )
    monkeypatch.setattr(
        session_recorder._preview, "build_lesson_selection_preview", lambda **_kwargs: {"items": []}
    )
    with pytest.raises(ValueError, match="selected no eligible"):
        session_recorder.append_session(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            session_id="empty",
            seed="seed",
        )


def test_score_authoring_cli_emits_session_bound_event(tmp_path: Path, monkeypatch, capsys) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path, session_events=[_session_event()])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "record_lesson_score.py",
            "--repo-root",
            str(tmp_path),
            "--event-id",
            "cli-event",
            "--session-id",
            "session-a",
            "--lesson-id",
            "a",
            "--source-retro",
            "charness-artifacts/retro/source.md",
            "--outcome",
            "changed-an-action",
            "--anchor",
            ANCHOR,
        ],
    )
    assert scorer.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["session_id"] == "session-a"


def test_session_recorder_cli_emits_snapshot_and_requires_seed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    preview = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "seed": "cli-seed",
        "eligible_count": 1,
        "bucket_counts": {
            "recent": 1,
            "value": 0,
            "uncertainty": 0,
            "archive": 0,
            "archive_fallback_uncertainty": 0,
        },
        "items": [{"lesson_id": "a"}],
    }
    monkeypatch.setattr(
        session_recorder._preview,
        "build_lesson_selection_preview",
        lambda **_kwargs: preview,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "record_lesson_session.py",
            "--repo-root",
            str(tmp_path),
            "--session-id",
            "cli-session",
            "--seed",
            "cli-seed",
        ],
    )
    assert session_recorder.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["session_id"] == "cli-session"
    monkeypatch.setattr(
        sys,
        "argv",
        ["record_lesson_session.py", "--repo-root", str(tmp_path), "--session-id", "missing-seed"],
    )
    with pytest.raises(SystemExit, match="2"):
        session_recorder.main()


def test_writer_uses_windows_fallback_fails_closed_and_removes_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeMsvcrt:
        LK_LOCK, LK_UNLCK = 1, 2

        def __init__(self) -> None:
            self.operations: list[int] = []

        def locking(self, _fd: int, operation: int, _length: int) -> None:
            self.operations.append(operation)

    path = tmp_path / "ledger.json"
    path.write_text("{}", encoding="utf-8")
    fake = FakeMsvcrt()
    monkeypatch.setattr(writer, "fcntl", None)
    monkeypatch.setattr(writer, "msvcrt", fake)
    with writer.ledger_lock(path):
        pass
    assert fake.operations == [fake.LK_LOCK, fake.LK_UNLCK]
    monkeypatch.setattr(writer, "msvcrt", None)
    with pytest.raises(ValueError, match="no supported platform"):
        with writer.ledger_lock(path):
            pass
    monkeypatch.setattr(writer, "fcntl", object())
    monkeypatch.setattr(
        writer.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("replace failed"))
    )
    with pytest.raises(OSError, match="replace failed"):
        writer.replace_payload(path, {"x": 1})
    assert not list(tmp_path.glob(".ledger.json.*"))


def test_writer_reports_open_acquire_and_release_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ledger.json"
    path.write_text("{}", encoding="utf-8")
    system_tempdir = tempfile.gettempdir
    blocked = tmp_path / "blocked"
    blocked.write_text("x", encoding="utf-8")
    monkeypatch.setattr(writer.tempfile, "gettempdir", lambda: str(blocked))
    with pytest.raises(ValueError, match="unable to open"):
        with writer.ledger_lock(path):
            pass

    class FailingFcntl:
        LOCK_EX = 1
        LOCK_UN = 2

        def __init__(self, failure: int) -> None:
            self.failure = failure

        def flock(self, _fd: int, operation: int) -> None:
            if operation == self.failure:
                raise OSError("lock failure")

    monkeypatch.setattr(writer.tempfile, "gettempdir", system_tempdir)
    monkeypatch.setattr(writer, "msvcrt", None)
    monkeypatch.setattr(writer, "fcntl", FailingFcntl(FailingFcntl.LOCK_EX))
    with pytest.raises(ValueError, match="unable to acquire"):
        with writer.ledger_lock(path):
            pass
    monkeypatch.setattr(writer, "fcntl", FailingFcntl(FailingFcntl.LOCK_UN))
    with pytest.raises(ValueError, match="unable to release"):
        with writer.ledger_lock(path):
            pass

    class FailingMsvcrt:
        LK_LOCK = 1
        LK_UNLCK = 2

        def __init__(self, failure: int) -> None:
            self.failure = failure

        def locking(self, _fd: int, operation: int, _length: int) -> None:
            if operation == self.failure:
                raise OSError("windows lock failure")

    monkeypatch.setattr(writer, "fcntl", None)
    monkeypatch.setattr(writer, "msvcrt", FailingMsvcrt(FailingMsvcrt.LK_LOCK))
    with pytest.raises(ValueError, match="unable to acquire"):
        with writer.ledger_lock(path):
            pass
    monkeypatch.setattr(writer, "msvcrt", FailingMsvcrt(FailingMsvcrt.LK_UNLCK))
    with pytest.raises(ValueError, match="unable to release"):
        with writer.ledger_lock(path):
            pass
def test_empty_ledger_bootstrap_is_valid_reachable_and_refuses_to_overwrite(tmp_path: Path) -> None:
    """The opt-in that makes the lifecycle reachable, and its honest limit.

    Every lifecycle entry point required this file to already exist and nothing
    created it, so a repo that adopted charness after the ledger landed had the
    reporting half of the loop and no path to the evaluating half. The bootstrap
    is deliberately EMPTY: seeding transitions from the selection index would
    commit append-only rows citing mutable retro files, which break unrepairably
    when a retro is renamed or its tag edited away.
    """
    init = load_script_module("init_lesson_ledger_for_test", ROOT / "scripts/init_lesson_ledger.py")
    output_dir = tmp_path / "charness-artifacts/retro"
    summary_path = output_dir / "recent-lessons.md"

    result = init.init_lesson_ledger(
        repo_root=tmp_path, output_dir=output_dir, summary_path=summary_path
    )

    assert result == {
        "lesson_count": 0,
        "transition_count": 0,
        "score_event_count": 0,
        "lifecycle_event_count": 0,
        "active_lesson_count": 0,
        "path": "charness-artifacts/retro/lesson-ledger.json",
    }
    assert _validate(tmp_path)["lesson_count"] == 0
    payload = json.loads((output_dir / "lesson-ledger.json").read_text(encoding="utf-8"))
    assert set(payload) == ledger.TOP_LEVEL_KEYS
    assert payload["schema_version"] == ledger.SCHEMA_VERSION
    assert payload["active_lesson_budget"] == ledger.ACTIVE_LESSON_BUDGET

    with pytest.raises(FileExistsError, match="append-only"):
        init.init_lesson_ledger(
            repo_root=tmp_path, output_dir=output_dir, summary_path=summary_path
        )


def test_empty_ledger_bootstrap_refuses_to_wipe_a_committed_ledger(tmp_path: Path) -> None:
    """A committed ledger absent from the worktree is not an uninitialized repo.

    `not path.exists()` alone would have written an empty file over a ledger whose
    committed transitions, scores and lifecycle decisions are append-only and
    globally unique forever. Validating BEFORE the write is what catches it.
    """
    init = load_script_module("init_lesson_ledger_wipe_test", ROOT / "scripts/init_lesson_ledger.py")
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    _git(tmp_path, "init")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "seed")
    path.unlink()

    with pytest.raises(ValueError, match="committed transitions were rewritten"):
        init.init_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "charness-artifacts/retro",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )
    assert not path.exists()


def test_empty_ledger_bootstrap_yields_to_a_ledger_that_appeared_inside_the_lock(
    tmp_path: Path, monkeypatch
) -> None:
    """The re-check the pre-lock `path.exists()` cannot make.

    Two opt-ins racing on one repo both pass the pre-check and both pass the replay
    validation, because at that instant neither ledger exists yet. Only the loser's
    re-read INSIDE the lock can see the winner's file, and without it the loser
    replaces a ledger whose transitions are already append-only and unique forever.
    The lock is stubbed with one that plants the winner's bytes on entry, which is
    the interleaving the real `flock` window admits and a wall-clock race cannot be
    made to reproduce on demand.
    """
    init = load_script_module("init_lesson_ledger_race_test", ROOT / "scripts/init_lesson_ledger.py")
    winner = b'{"the winner already wrote this"}'

    @contextlib.contextmanager
    def _lock_that_loses_the_race(path: Path):
        path.write_bytes(winner)
        yield

    monkeypatch.setattr(init._writer, "ledger_lock", _lock_that_loses_the_race)

    with pytest.raises(FileExistsError) as raised:
        init.init_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "charness-artifacts/retro",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )

    # Named as the RACE it is, not as the ordinary "you ran this twice" refusal --
    # the two demand different things of the reader, and the repo-relative path is
    # what a consuming repo can act on.
    assert "appeared at `charness-artifacts/retro/lesson-ledger.json`" in str(raised.value)
    assert "while initializing" in str(raised.value)
    # The whole point: the winner's bytes are still there.
    assert (tmp_path / "charness-artifacts/retro/lesson-ledger.json").read_bytes() == winner


def test_empty_ledger_bootstrap_entrypoint_reports_a_refusal_as_exit_one(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The refusal has to survive the trip through `__main__` as a message.

    Everything this bootstrap refuses -- an existing ledger, a committed ledger
    missing from the worktree, an unreadable output dir -- arrives as an exception,
    and an operator running the opt-in a second time must get the sentence naming
    the validator, on stderr, with a nonzero code. A bare traceback would be exit 1
    too, so the assertion is on the sentence.
    """
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["init_lesson_ledger.py", "--repo-root", str(tmp_path)]
    )

    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(ROOT / "scripts/init_lesson_ledger.py"), run_name="__main__")

    assert caught.value.code == 1
    captured = capsys.readouterr()
    # Nothing on stdout: a payload consumer must not be handed a half-receipt.
    assert captured.out == ""
    assert "it is append-only" in captured.err
    assert "check_lesson_ledger.py" in captured.err
    assert "Traceback" not in captured.err


def test_ledger_refusals_name_the_key_set_or_next_step_they_demand(tmp_path: Path) -> None:
    """A hand-seeder's first errors used to state a requirement without its values.

    The reporter who hand-authored a ledger guessed a `legacy_score_event_count`
    key and the wrong schema version, because no refusal ever named the accepted
    set. Each constant is defined in the same module as its check and was never
    rendered.
    """
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    cases: list[tuple[dict, list[str]]] = []

    unknown_top_level = _payload()
    unknown_top_level["legacy_score_event_count"] = 0
    cases.append((unknown_top_level, sorted(ledger.TOP_LEVEL_KEYS)))

    broken_transition = _payload()
    broken_transition["transitions"] = [{"sequence": 1, "transition_id": "seed-a"}]
    cases.append((broken_transition, sorted(ledger.TRANSITION_KEYS)))

    broken_lifecycle = _payload()
    broken_lifecycle["lifecycle_events"] = [{"sequence": 1, "event_id": "e-1"}]
    cases.append((broken_lifecycle, sorted(ledger.LIFECYCLE_EVENT_KEYS)))

    broken_session = _payload(session_events=[{"session_id": "s-1"}])
    cases.append((broken_session, sorted(ledger.SESSION_EVENT_KEYS)))

    broken_snapshot = _payload(session_events=[_session_event()])
    del broken_snapshot["session_events"][0]["snapshot"]["seed"]
    cases.append((broken_snapshot, sorted(ledger.SNAPSHOT_KEYS)))

    broken_buckets = _payload(session_events=[_session_event()])
    del broken_buckets["session_events"][0]["snapshot"]["bucket_counts"]["archive"]
    cases.append((broken_buckets, sorted(ledger.SNAPSHOT_BUCKET_KEYS)))

    broken_score = _payload(
        session_events=[_session_event()],
        score_events=[{"event_id": "score-a", "lesson_id": "a", "score": 0}],
    )
    cases.append((broken_score, sorted(outcome_lib.LEGACY_REQUIRED_KEYS)))

    empty_selection = _payload(session_events=[_session_event()])
    empty_selection["session_events"][0]["snapshot"]["lesson_ids"] = []
    cases.append((empty_selection, ["recurrence-class:", "init_lesson_ledger.py"]))

    # Written raw, not through `_materialize`: every case above fails its own
    # shape check long before the lessons-equal-replay comparison, and the helper
    # cannot walk events that are malformed on purpose.
    for payload, expected in cases:
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError) as excinfo:
            _validate(tmp_path)
        for token in expected:
            assert token in str(excinfo.value), (token, str(excinfo.value))

    projection = _payload()
    projection["lessons"]["a"]["score_total"] = 0.0
    path.write_text(json.dumps(projection), encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        _validate(tmp_path)
    for token in sorted(ledger.LESSON_KEYS):
        assert token in str(excinfo.value)


def test_lifecycle_refusal_enumerates_the_only_legal_moves(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    payload = _payload()
    payload["lifecycle_events"] = [
        {
            "sequence": 1,
            "event_id": "life-1",
            "lesson_id": "a",
            "action": "resurrect",
            "decision_ref": "charness-artifacts/retro/source.md",
            "rationale": "wrong move for an active lesson",
        }
    ]
    path.write_text(json.dumps(_materialize(payload)), encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        _validate(tmp_path)

    message = str(excinfo.value)
    assert "archive a lesson in state `active`" in message
    assert "resurrect a lesson in state `archived`" in message
