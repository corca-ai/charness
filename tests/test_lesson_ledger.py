from __future__ import annotations

import copy
import json
import multiprocessing
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger
from scripts import lesson_ledger_writer_lib as writer
from scripts import record_lesson_score as scorer
from scripts import record_lesson_session as session_recorder
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]


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
    legacy_score_event_count: int | None = None,
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
        "legacy_score_event_count": 0
        if legacy_score_event_count is None
        else legacy_score_event_count,
        "session_events": [] if session_events is None else session_events,
        "score_events": events,
        "lessons": {
            "a": {
                "source_retro": source,
                "transition_id": "seed-a",
                "score_total": 0,
                "score_count": 0,
                "state": "active",
                "last_lifecycle_event_id": None,
            }
        },
    }


def _materialize(payload: dict) -> dict:
    for lesson in payload["lessons"].values():
        lesson["score_total"] = 0
        lesson["score_count"] = 0
        lesson["state"] = "active"
        lesson["last_lifecycle_event_id"] = None
    for event in payload["lifecycle_events"]:
        lesson = payload["lessons"].get(event["lesson_id"])
        if lesson is not None:
            lesson["state"] = "archived" if event["action"] == "archive" else "active"
            lesson["last_lifecycle_event_id"] = event["event_id"]
    for event in payload["score_events"]:
        lesson = payload["lessons"].get(event["lesson_id"])
        if lesson is not None:
            lesson["score_total"] += event["score"]
            lesson["score_count"] += 1
    return payload


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


def test_ledger_replays_legacy_cited_scores_and_checker_cli(
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
    assert json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["score_total"] == 2


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
    cases.append((projection, "integer replay fields"))
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
    path = _ledger(
        tmp_path, session_events=[session], score_events=[event], legacy_score_event_count=0
    )
    assert _validate(tmp_path)["score_event_count"] == 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    invalids: list[tuple[dict, str]] = []
    unknown = copy.deepcopy(payload)
    unknown["score_events"][0]["session_id"] = "unknown"
    invalids.append((unknown, "unknown session"))
    missing = copy.deepcopy(payload)
    del missing["score_events"][0]["session_id"]
    invalids.append((missing, "unexpected or missing"))
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
        score=1,
        anchor=None,
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
    payload["lessons"]["b"] = {
        "source_retro": "charness-artifacts/retro/second.md",
        "transition_id": "seed-b",
        "score_total": 0,
        "score_count": 0,
        "state": "active",
        "last_lifecycle_event_id": None,
    }
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
            score=0,
            anchor=None,
        )
    assert path.read_bytes() == before


def test_uncommitted_v3_ledger_cannot_declare_legacy_scores(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(
        tmp_path,
        score_events=[_score_event(score=1)],
        legacy_score_event_count=1,
    )
    with pytest.raises(ValueError, match="only allowed when migrating"):
        _validate(tmp_path)


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
        score=2,
        anchor="decision evidence",
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
            score=0,
            anchor=None,
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
            score=0,
            anchor=None,
        )
    with pytest.raises(ValueError, match="score must be an integer"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="bad-score",
            session_id="session-a",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            score=True,
            anchor=None,
        )
    with pytest.raises(ValueError, match="unseeded"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unseeded",
            session_id="session-a",
            lesson_id="other",
            source_retro="charness-artifacts/retro/source.md",
            score=0,
            anchor=None,
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
            "--score",
            "-1",
        ],
    )
    assert scorer.main() == 0
    assert json.loads(capsys.readouterr().out)["session_id"] == "session-a"


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
    assert json.loads(capsys.readouterr().out)["session_id"] == "cli-session"
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


def _append_in_child(repo_text: str, event_id: str, source: str, barrier, queue) -> None:
    repo = Path(repo_text)
    try:
        barrier.wait(timeout=10)
        scorer.append_score(
            repo_root=repo,
            output_dir=repo / "charness-artifacts/retro",
            summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
            event_id=event_id,
            session_id="session-a",
            lesson_id="a",
            source_retro=source,
            score=0,
            anchor=None,
        )
        queue.put(None)
    except BaseException as exc:  # pragma: no cover - reported by parent assertion
        queue.put(repr(exc))


@pytest.mark.skipif(writer.fcntl is None, reason="requires POSIX cooperative-lock proof")
def test_two_concurrent_score_writers_preserve_both_events(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "second.md", "a")
    path = _ledger(tmp_path, session_events=[_session_event()])
    context = multiprocessing.get_context("fork")
    barrier, queue = context.Barrier(2), context.Queue()
    processes = [
        context.Process(
            target=_append_in_child,
            args=(
                str(tmp_path),
                "concurrent-a",
                "charness-artifacts/retro/source.md",
                barrier,
                queue,
            ),
        ),
        context.Process(
            target=_append_in_child,
            args=(
                str(tmp_path),
                "concurrent-b",
                "charness-artifacts/retro/second.md",
                barrier,
                queue,
            ),
        ),
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(15)
    assert all(process.exitcode == 0 for process in processes)
    assert [queue.get(timeout=2), queue.get(timeout=2)] == [None, None]
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert {event["event_id"] for event in payload["score_events"]} == {
        "concurrent-a",
        "concurrent-b",
    }
    assert _validate(tmp_path)["score_event_count"] == 2


def _commit_v2_ledger(repo: Path) -> Path:
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _retro(repo, "source.md", "a")
    _retro(repo, "second.md", "a")
    events = [
        _score_event(score=2, anchor="decision evidence"),
        _score_event(event_id="score-b", source="charness-artifacts/retro/second.md", score=-1),
    ]
    payload = _materialize(_payload(score_events=events))
    payload = {
        key: value
        for key, value in payload.items()
        if key not in {"legacy_score_event_count", "session_events"}
    }
    payload["schema_version"] = 2
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "v2 scored ledger")
    return path


def test_v2_migration_and_v3_session_score_prefixes_are_append_only(tmp_path: Path) -> None:
    path = _commit_v2_ledger(tmp_path)
    v3 = _materialize(
        _payload(
            score_events=[
                _score_event(score=2, anchor="decision evidence"),
                _score_event(
                    event_id="score-b", source="charness-artifacts/retro/second.md", score=-1
                ),
            ],
            legacy_score_event_count=2,
        )
    )
    path.write_text(json.dumps(v3), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 2
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "migrate v3")
    rewritten_transition = copy.deepcopy(v3)
    rewritten_transition["transitions"][0]["transition_id"] = "rewritten-seed"
    rewritten_transition["lessons"]["a"]["transition_id"] = "rewritten-seed"
    path.write_text(json.dumps(rewritten_transition), encoding="utf-8")
    with pytest.raises(ValueError, match="committed transitions"):
        _validate(tmp_path)
    rewritten_v2 = copy.deepcopy(v3)
    rewritten_v2["score_events"][0]["score"] = 1
    _materialize(rewritten_v2)
    path.write_text(json.dumps(rewritten_v2), encoding="utf-8")
    with pytest.raises(ValueError, match="committed score events"):
        _validate(tmp_path)
    path.write_text(json.dumps(v3), encoding="utf-8")
    with pytest.raises(ValueError, match="committed legacy_score_event_count"):
        changed_cutoff = copy.deepcopy(v3)
        changed_cutoff["legacy_score_event_count"] = 1
        path.write_text(json.dumps(changed_cutoff), encoding="utf-8")
        _validate(tmp_path)
    _retro(tmp_path, "third.md", "a")
    appended = copy.deepcopy(v3)
    appended["session_events"] = [
        _session_event(session_id="session-a"),
        _session_event(session_id="session-b", seed="seed-b"),
    ]
    appended["score_events"].append(
        _score_event(
            event_id="score-c",
            source="charness-artifacts/retro/third.md",
            score=3,
            anchor="third evidence",
            session_id="session-a",
        )
    )
    _materialize(appended)
    path.write_text(json.dumps(appended), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 3
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "append sessions and score")
    for mutation in ("rewrite", "delete", "reorder"):
        invalid = copy.deepcopy(appended)
        if mutation == "rewrite":
            invalid["session_events"][0]["snapshot"]["seed"] = "rewritten"
            invalid["session_events"][0]["snapshot_sha256"] = ledger.snapshot_sha256(
                invalid["session_events"][0]["snapshot"]
            )
        elif mutation == "delete":
            invalid["session_events"] = invalid["session_events"][:1]
        else:
            invalid["session_events"].reverse()
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with pytest.raises(ValueError, match="committed session events"):
            _validate(tmp_path)
