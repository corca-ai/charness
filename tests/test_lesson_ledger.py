from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger
from scripts import record_lesson_score as scorer
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]


def _retro(repo: Path, name: str, lesson_class: str) -> None:
    path = repo / "charness-artifacts/retro" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: {lesson_class})\n",
        encoding="utf-8",
    )


def _payload(*, source: str = "charness-artifacts/retro/source.md", score_events: list[dict] | None = None) -> dict:
    return {
        "kind": ledger.KIND,
        "schema_version": ledger.SCHEMA_VERSION,
        "transitions": [{"sequence": 1, "transition_id": "seed-a", "lesson_id": "a", "source_retro": source}],
        "score_events": [] if score_events is None else score_events,
        "lessons": {"a": {"source_retro": source, "transition_id": "seed-a", "score_total": 0, "score_count": 0}},
    }


def _ledger(repo: Path, **kwargs: object) -> Path:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    payload = _payload(**kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _validate(repo: Path) -> dict:
    return ledger.validate_lesson_ledger(
        repo_root=repo,
        output_dir=repo / "charness-artifacts/retro",
        summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
    )


def _score_event(*, score: int = 0, source: str = "charness-artifacts/retro/source.md", **extra: object) -> dict:
    event = {"event_id": "score-a", "source_retro": source, "lesson_id": "a", "score": score}
    event.update(extra)
    return event


def test_ledger_replays_a_cited_transition_and_zero_score(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    event = _score_event()
    path = _ledger(tmp_path, score_events=[event])
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["lessons"]["a"].update(score_total=0, score_count=1)
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = _validate(tmp_path)
    assert result == {
        "lesson_count": 1,
        "transition_count": 1,
        "score_event_count": 1,
        "path": "charness-artifacts/retro/lesson-ledger.json",
    }


def test_ledger_checker_cli_reports_the_replayed_count(tmp_path: Path, monkeypatch, capsys) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    checker = load_script_module(
        "check_lesson_ledger_for_test",
        ROOT / "scripts/check_lesson_ledger.py",
    )
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(tmp_path)])
    assert checker.main() == 0
    assert capsys.readouterr().out == "Validated lesson ledger: 1 lessons, 1 transitions.\n"


def test_ledger_checker_cli_reports_an_invalid_ledger(tmp_path: Path, monkeypatch, capsys) -> None:
    def fail_validation(**_kwargs: object) -> dict:
        raise ValueError("broken ledger")

    monkeypatch.setattr(ledger, "validate_lesson_ledger", fail_validation)
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(tmp_path)])
    with pytest.raises(SystemExit) as exit_result:
        runpy.run_path(str(ROOT / "scripts/check_lesson_ledger.py"), run_name="__main__")
    assert exit_result.value.code == 1
    assert capsys.readouterr().err == "broken ledger\n"


def test_ledger_rejects_projection_or_citation_rewrite(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path, source="charness-artifacts/retro/other.md")
    with pytest.raises(ValueError, match="citation does not declare"):
        _validate(tmp_path)
    payload = _payload()
    payload["lessons"]["a"]["transition_id"] = "edited"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="materialized lessons"):
        _validate(tmp_path)


def test_score_events_reject_invalid_shapes_and_deferred_fields(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    cases = [
        (_score_event(score=True), "integer"),
        (_score_event(score=1.0), "integer"),
        (_score_event(score=2), "needs an anchor"),
        (_score_event(score=-3, anchor=""), "anchor"),
        (_score_event(event_id=" "), "non-whitespace"),
        (_score_event(anchor=" "), "non-whitespace"),
        (_score_event(score=1, shown_set="fake"), "unexpected or missing"),
        ({**_score_event(), "lesson_id": "other"}, "unseeded"),
    ]
    for event, message in cases:
        _ledger(tmp_path, score_events=[event])
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_score_events_require_cited_unique_retro_lesson_pairs(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    bad_source = _score_event(source="charness-artifacts/retro/other.md")
    with pytest.raises(ValueError, match="citation does not declare"):
        _ledger(tmp_path, score_events=[bad_source])
        _validate(tmp_path)
    duplicate_pair = [_score_event(), {**_score_event(), "event_id": "score-b"}]
    _ledger(tmp_path, score_events=duplicate_pair)
    with pytest.raises(ValueError, match="duplicate score"):
        _validate(tmp_path)


def test_score_replay_and_closed_v2_shapes(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "second.md", "a")
    events = [
        _score_event(score=2, anchor="decision evidence"),
        _score_event(event_id="score-b", score=-1, source="charness-artifacts/retro/second.md"),
    ]
    path = _ledger(tmp_path, score_events=events)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["lessons"]["a"].update(score_total=1, score_count=2)
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 2

    invalid_payloads = []
    projection = copy.deepcopy(payload)
    projection["lessons"]["a"]["score_total"] = 1.0
    invalid_payloads.append((projection, "score fields"))
    sequence = copy.deepcopy(payload)
    sequence["transitions"][0]["sequence"] = True
    invalid_payloads.append((sequence, "sequences"))
    unknown_top_level = copy.deepcopy(payload)
    unknown_top_level["budget"] = 1
    invalid_payloads.append((unknown_top_level, "top-level"))
    missing_events = copy.deepcopy(payload)
    del missing_events["score_events"]
    invalid_payloads.append((missing_events, "top-level"))
    duplicate_id = copy.deepcopy(payload)
    duplicate_id["score_events"][1]["event_id"] = "score-a"
    invalid_payloads.append((duplicate_id, "duplicate score event_id"))
    for invalid, message in invalid_payloads:
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_ledger_rejects_all_closed_transition_and_payload_shapes(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    cases = []
    non_object = _payload()
    non_object["transitions"] = [None]
    cases.append((non_object, "must be an object"))
    unexpected_transition = _payload()
    unexpected_transition["transitions"][0]["contract_target"] = "AGENTS.md"
    cases.append((unexpected_transition, "deferred graduation"))
    missing_transition_value = _payload()
    missing_transition_value["transitions"][0]["transition_id"] = ""
    cases.append((missing_transition_value, "non-empty"))
    duplicate_transition = _payload()
    duplicate_transition["transitions"].append(
        {"sequence": 2, "transition_id": "seed-a", "lesson_id": "b", "source_retro": "source.md"}
    )
    cases.append((duplicate_transition, "duplicate transition_id"))
    duplicate_lesson = _payload()
    duplicate_lesson["transitions"].append(
        {"sequence": 2, "transition_id": "seed-b", "lesson_id": "a", "source_retro": "source.md"}
    )
    cases.append((duplicate_lesson, "duplicate lesson_id"))
    missing_event_value = _payload(score_events=[_score_event(event_id="")])
    cases.append((missing_event_value, "non-empty"))
    wrong_container = _payload()
    wrong_container["score_events"] = {}
    cases.append((wrong_container, "must be lists"))
    wrong_lesson_shape = _payload()
    del wrong_lesson_shape["lessons"]["a"]["score_count"]
    cases.append((wrong_lesson_shape, "materialized lessons"))
    wrong_schema = _payload()
    wrong_schema["schema_version"] = 3
    cases.append((wrong_schema, "expected kind"))
    for payload, message in cases:
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)
    with pytest.raises(FileNotFoundError, match="missing lesson ledger"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "missing",
            summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        )
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        _validate(tmp_path)


def test_committed_ledger_must_have_a_supported_shape(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "charness-artifacts/retro/lesson-ledger.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    malformed_states = [
        ("{", "invalid JSON"),
        (json.dumps({"kind": "other", "transitions": []}), "unrecognized shape"),
        (json.dumps({"kind": ledger.KIND}), "no transition list"),
        (json.dumps({"kind": ledger.KIND, "schema_version": 2, "transitions": []}), "unsupported score-event"),
    ]
    for stdout, message in malformed_states:
        monkeypatch.setattr(
            ledger.subprocess,
            "run",
            lambda *_args, _stdout=stdout, **_kwargs: subprocess.CompletedProcess([], 0, _stdout, ""),
        )
        with pytest.raises(ValueError, match=message):
            ledger._committed_state(tmp_path, path)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _commit_v1_ledger(repo: Path) -> Path:
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _retro(repo, "source.md", "a")
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    v1 = _payload()
    del v1["score_events"]
    del v1["lessons"]["a"]["score_total"]
    del v1["lessons"]["a"]["score_count"]
    v1["schema_version"] = 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(v1), encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed v1 ledger")
    return path


def test_score_authoring_appends_a_replayed_cited_event_and_refusals_do_not_write(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    event = scorer.append_score(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id="event-a",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        score=2,
        anchor="decision evidence",
    )
    assert event["event_id"] == "event-a"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["lessons"]["a"]["score_total"] == 2
    assert payload["lessons"]["a"]["score_count"] == 1
    assert _validate(tmp_path)["score_event_count"] == 1
    before = path.read_bytes()
    for kwargs, message in (
        ({"event_id": "event-a", "score": 0, "anchor": None}, "duplicate score event_id"),
        ({"event_id": "event-b", "score": 1, "anchor": None}, "duplicate score"),
        ({"event_id": "event-c", "lesson_id": "other", "score": 1, "anchor": None}, "unseeded"),
        ({"event_id": "event-d", "score": 3, "anchor": None}, "needs an anchor"),
        ({"event_id": " ", "score": 0, "anchor": None}, "non-whitespace"),
    ):
        with pytest.raises(ValueError, match=message):
            scorer.append_score(
                repo_root=tmp_path,
                output_dir=path.parent,
                summary_path=path.parent / "recent-lessons.md",
                lesson_id=kwargs.pop("lesson_id", "a"),
                source_retro="charness-artifacts/retro/source.md",
                **kwargs,
            )
        assert path.read_bytes() == before
    with pytest.raises(ValueError, match="citation does not declare"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="wrong-source",
            lesson_id="a",
            source_retro="charness-artifacts/retro/not-a-source.md",
            score=0,
            anchor=None,
        )
    assert path.read_bytes() == before


def test_score_authoring_uses_windows_lock_fallback_and_fails_closed_without_a_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeMsvcrt:
        LK_LOCK = 1
        LK_UNLCK = 2

        def __init__(self) -> None:
            self.operations: list[int] = []

        def locking(self, _fd: int, operation: int, _length: int) -> None:
            self.operations.append(operation)

    path = tmp_path / "ledger.json"
    path.write_text("{}", encoding="utf-8")
    fake_msvcrt = FakeMsvcrt()
    monkeypatch.setattr(scorer, "fcntl", None)
    monkeypatch.setattr(scorer, "msvcrt", fake_msvcrt)
    with scorer._ledger_lock(path):
        pass
    assert fake_msvcrt.operations == [fake_msvcrt.LK_LOCK, fake_msvcrt.LK_UNLCK]
    assert not list(tmp_path.glob(".ledger.json.lock"))

    monkeypatch.setattr(scorer, "msvcrt", None)
    with pytest.raises(ValueError, match="no supported platform"):
        with scorer._ledger_lock(path):
            pass


def test_score_authoring_reports_lock_open_acquire_and_release_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ledger.json"
    path.write_text("{}", encoding="utf-8")
    system_tempdir = tempfile.gettempdir()
    blocked_temp = tmp_path / "not-a-directory"
    blocked_temp.write_text("x", encoding="utf-8")
    monkeypatch.setattr(scorer.tempfile, "gettempdir", lambda: str(blocked_temp))
    with pytest.raises(ValueError, match="unable to open lesson-ledger lock"):
        with scorer._ledger_lock(path):
            pass

    class FailingFcntl:
        LOCK_EX = 1
        LOCK_UN = 2

        def __init__(self, failed_operation: int) -> None:
            self.failed_operation = failed_operation

        def flock(self, _fd: int, operation: int) -> None:
            if operation == self.failed_operation:
                raise OSError("lock failure")

    monkeypatch.setattr(scorer.tempfile, "gettempdir", lambda: system_tempdir)
    monkeypatch.setattr(scorer, "msvcrt", None)
    monkeypatch.setattr(scorer, "fcntl", FailingFcntl(FailingFcntl.LOCK_EX))
    with pytest.raises(ValueError, match="unable to acquire lesson-ledger lock"):
        with scorer._ledger_lock(path):
            pass

    failing_release = FailingFcntl(FailingFcntl.LOCK_UN)
    monkeypatch.setattr(scorer, "fcntl", failing_release)
    with pytest.raises(ValueError, match="unable to release lesson-ledger lock"):
        with scorer._ledger_lock(path):
            pass

    class FailingMsvcrt:
        LK_LOCK = 1
        LK_UNLCK = 2

        def __init__(self, failed_operation: int) -> None:
            self.failed_operation = failed_operation

        def locking(self, _fd: int, operation: int, _length: int) -> None:
            if operation == self.failed_operation:
                raise OSError("windows lock failure")

    monkeypatch.setattr(scorer, "fcntl", None)
    monkeypatch.setattr(scorer, "msvcrt", FailingMsvcrt(FailingMsvcrt.LK_LOCK))
    with pytest.raises(ValueError, match="unable to acquire lesson-ledger lock"):
        with scorer._ledger_lock(path):
            pass

    monkeypatch.setattr(scorer, "msvcrt", FailingMsvcrt(FailingMsvcrt.LK_UNLCK))
    with pytest.raises(ValueError, match="unable to release lesson-ledger lock"):
        with scorer._ledger_lock(path):
            pass


def test_score_authoring_removes_an_unreplaced_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    monkeypatch.setattr(scorer.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("replace failed")))
    with pytest.raises(OSError, match="replace failed"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="replace-failure",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            score=0,
            anchor=None,
        )
    assert not list(path.parent.glob(".lesson-ledger.json.*"))


def test_score_authoring_cli_emits_the_appended_event(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "record_lesson_score.py",
            "--repo-root",
            str(tmp_path),
            "--event-id",
            "cli-event",
            "--lesson-id",
            "a",
            "--source-retro",
            "charness-artifacts/retro/source.md",
            "--score",
            "-1",
        ],
    )
    assert scorer.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "event_id": "cli-event",
        "lesson_id": "a",
        "score": -1,
        "source_retro": "charness-artifacts/retro/source.md",
    }


def test_score_authoring_refuses_non_integer_scores_and_missing_ledger(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    with pytest.raises(ValueError, match="score must be an integer"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="not-int",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            score=True,
            anchor=None,
        )
    with pytest.raises(FileNotFoundError, match="missing lesson ledger"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=tmp_path / "missing",
            summary_path=path.parent / "recent-lessons.md",
            event_id="missing-ledger",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            score=0,
            anchor=None,
        )


def test_score_authoring_script_prints_a_refusal(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/record_lesson_score.py"),
            "--repo-root",
            str(tmp_path),
            "--event-id",
            "missing-ledger",
            "--lesson-id",
            "a",
            "--source-retro",
            "charness-artifacts/retro/source.md",
            "--score",
            "0",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "missing lesson ledger" in result.stderr


def test_v1_migration_and_v2_score_event_prefix_are_append_only(tmp_path: Path) -> None:
    path = _commit_v1_ledger(tmp_path)
    v2 = _payload()
    path.write_text(json.dumps(v2), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 0

    rewritten_transition = copy.deepcopy(v2)
    rewritten_transition["transitions"][0]["transition_id"] = "rewritten-seed"
    rewritten_transition["lessons"]["a"]["transition_id"] = "rewritten-seed"
    path.write_text(json.dumps(rewritten_transition), encoding="utf-8")
    with pytest.raises(ValueError, match="committed transitions"):
        _validate(tmp_path)
    deleted_transition = copy.deepcopy(v2)
    deleted_transition["transitions"] = []
    deleted_transition["lessons"] = {}
    path.write_text(json.dumps(deleted_transition), encoding="utf-8")
    with pytest.raises(ValueError, match="committed transitions"):
        _validate(tmp_path)

    _retro(tmp_path, "second.md", "a")
    first = _score_event(score=2, anchor="decision evidence")
    second = _score_event(event_id="score-b", score=-1, source="charness-artifacts/retro/second.md")
    v2["score_events"] = [first, second]
    v2["lessons"]["a"].update(score_total=1, score_count=2)
    path.write_text(json.dumps(v2), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 2
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "add score events")

    _retro(tmp_path, "third.md", "a")
    appended_event = _score_event(
        event_id="score-c",
        score=3,
        source="charness-artifacts/retro/third.md",
        anchor="third cited decision",
    )
    appended = copy.deepcopy(v2)
    appended["score_events"].append(appended_event)
    appended["lessons"]["a"].update(score_total=4, score_count=3)
    path.write_text(json.dumps(appended), encoding="utf-8")
    assert _validate(tmp_path)["score_event_count"] == 3

    rewritten_event = copy.deepcopy(v2)
    rewritten_event["score_events"][0]["score"] = 1
    rewritten_event["lessons"]["a"].update(score_total=0, score_count=2)
    path.write_text(json.dumps(rewritten_event), encoding="utf-8")
    with pytest.raises(ValueError, match="committed score events"):
        _validate(tmp_path)
    deleted_event = copy.deepcopy(v2)
    deleted_event["score_events"] = [first]
    deleted_event["lessons"]["a"].update(score_total=2, score_count=1)
    path.write_text(json.dumps(deleted_event), encoding="utf-8")
    with pytest.raises(ValueError, match="committed score events"):
        _validate(tmp_path)
    reordered_events = copy.deepcopy(v2)
    reordered_events["score_events"].reverse()
    path.write_text(json.dumps(reordered_events), encoding="utf-8")
    with pytest.raises(ValueError, match="committed score events"):
        _validate(tmp_path)
