from __future__ import annotations

import contextlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

from scripts.lessons import lesson_ledger_lib as ledger
from scripts.lessons import lesson_ledger_writer_lib as writer
from scripts.lessons import record_lesson_score as scorer
from tests.lesson_ledger_fixtures import blank_lesson, legacy_v8_payload, outcome_event
from tests.lesson_ledger_fixtures import materialize as _materialize
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = outcome_event(event_id="x", lesson_id="x", source_retro="x")["anchor"]


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


def _payload(
    *,
    source: str = "charness-artifacts/retro/source.md",
    score_events: list[dict] | None = None,
) -> dict:
    return {
        "kind": ledger.KIND,
        "schema_version": ledger.SCHEMA_VERSION,
        "transitions": [
            {"sequence": 1, "transition_id": "seed-a", "lesson_id": "a", "source_retro": source}
        ],
        "active_lesson_budget": ledger.ACTIVE_LESSON_BUDGET,
        "lifecycle_events": [],
        "score_events": [] if score_events is None else score_events,
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


def test_ledger_replays_cited_scores_and_checker_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(
        tmp_path,
        score_events=[_score_event(score=2, anchor="decision evidence")],
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
        "check_lesson_ledger_for_test", ROOT / "scripts/lessons/check_lesson_ledger.py"
    )
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(tmp_path)])
    assert checker.main() == 0
    assert capsys.readouterr().out == (
        "Validated lesson ledger: 1 lessons, 1 active, 1 seed transitions, 0 lifecycle events.\n"
    )
    assert json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]["score_total"] == 1


def test_v8_ledger_migration_preserves_the_live_lesson_corpus(tmp_path: Path) -> None:
    source_dir = ROOT / "charness-artifacts/retro"
    output_dir = tmp_path / "charness-artifacts/retro"
    shutil.copytree(source_dir, output_dir)
    path = output_dir / "lesson-ledger.json"
    current = json.loads(path.read_text(encoding="utf-8"))
    legacy = legacy_v8_payload(current)
    path.write_text(json.dumps(legacy), encoding="utf-8")
    before_transitions = legacy["transitions"]
    before_scores = legacy["score_events"]

    result = ledger.validate_lesson_ledger(
        repo_root=tmp_path,
        output_dir=output_dir,
        summary_path=output_dir / "recent-lessons.md",
    )
    # Read back through the VALIDATOR, not off disk: validation migrates in memory
    # and no longer writes, so the on-disk copy is deliberately still legacy here.
    migrated = ledger.migrate_ledger_payload(json.loads(path.read_text(encoding="utf-8")))[0]

    # The live corpus grows by one seed transition per retro class; pin the
    # migration to the corpus it read, not to the count on the day this was written.
    # The v8 corpus is the live working set (archived and graduated lessons left it
    # through events v8 cannot express; see `legacy_v8_payload`).
    live_count = len(legacy["lessons"])
    assert result["lesson_count"] == live_count
    assert len(migrated["lessons"]) == live_count
    assert migrated["schema_version"] == 9
    assert migrated["transitions"] == before_transitions
    assert migrated["score_events"] == before_scores
    assert migrated["lifecycle_events"] == []
    assert migrated["active_lesson_budget"] == ledger.ACTIVE_LESSON_BUDGET
    assert all(
        lesson["state"] == "active" and lesson["last_lifecycle_event_id"] is None
        for lesson in migrated["lessons"].values()
    )


def test_ledger_rejects_invalid_transition_score_and_projection_shapes(tmp_path: Path) -> None:
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
    bad_score = _payload(score_events=[_score_event(score=True)])
    cases.append((bad_score, "integer"))
    bad_anchor = _payload(score_events=[_score_event(anchor=" ")])
    cases.append((bad_anchor, "non-whitespace"))
    projection = _payload()
    projection["lessons"]["a"]["score_total"] = 0.0
    cases.append((projection, "replayed fields"))
    for payload, message in cases:
        serialized = payload if payload is projection else _materialize(payload)
        path.write_text(json.dumps(serialized), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            _validate(tmp_path)


def test_score_authoring_requires_one_cited_encounter_and_preserves_refusals(
    tmp_path: Path,
) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    scorer.append_score(
        repo_root=tmp_path,
        output_dir=path.parent,
        summary_path=path.parent / "recent-lessons.md",
        event_id="event-a",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        outcome="changed-an-action",
        anchor=ANCHOR,
    )
    assert _validate(tmp_path)["score_event_count"] == 1
    before = path.read_bytes()
    with pytest.raises(ValueError, match="duplicate score event_id or score source"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="event-b",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    assert path.read_bytes() == before


def test_authoring_refuses_invalid_score_inputs(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    with pytest.raises(ValueError, match="non-empty non-whitespace"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id=" ",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
    with pytest.raises(ValueError, match="outcome must be one of"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="bad-outcome",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="+3",
            anchor=ANCHOR,
        )
    with pytest.raises(ValueError, match="would have gone otherwise"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unfalsifiable-positive",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor="it helped a lot",
        )
    assert (
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unanchored-negative-is-fine",
            lesson_id="a",
            source_retro="charness-artifacts/retro/source.md",
            outcome="read-but-not-applied",
            anchor="it helped a lot",
        )["outcome"]
        == "read-but-not-applied"
    )
    with pytest.raises(ValueError, match="unseeded"):
        scorer.append_score(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            event_id="unseeded",
            lesson_id="other",
            source_retro="charness-artifacts/retro/source.md",
            outcome="changed-an-action",
            anchor=ANCHOR,
        )


def test_score_authoring_cli_emits_a_ledger_event(tmp_path: Path, monkeypatch, capsys) -> None:
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
            "--outcome",
            "changed-an-action",
            "--anchor",
            ANCHOR,
        ],
    )
    assert scorer.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["lesson_id"] == "a"


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


def test_empty_ledger_bootstrap_is_valid_and_refuses_overwrite(tmp_path: Path) -> None:
    init = load_script_module("init_lesson_ledger_for_test", ROOT / "scripts/lessons/init_lesson_ledger.py")
    output_dir = tmp_path / "charness-artifacts/retro"
    result = init.init_lesson_ledger(
        repo_root=tmp_path, output_dir=output_dir, summary_path=output_dir / "recent-lessons.md"
    )
    assert result["lesson_count"] == 0
    assert _validate(tmp_path)["lesson_count"] == 0
    payload = json.loads((output_dir / "lesson-ledger.json").read_text(encoding="utf-8"))
    assert set(payload) == ledger.TOP_LEVEL_KEYS
    assert payload["schema_version"] == ledger.SCHEMA_VERSION
    with pytest.raises(FileExistsError, match="append-only"):
        init.init_lesson_ledger(
            repo_root=tmp_path, output_dir=output_dir, summary_path=output_dir / "recent-lessons.md"
        )


def test_empty_ledger_bootstrap_refuses_to_wipe_a_committed_ledger(tmp_path: Path) -> None:
    init = load_script_module(
        "init_lesson_ledger_wipe_test", ROOT / "scripts/lessons/init_lesson_ledger.py"
    )
    from tests.quality_gates.repo_shapes import replace_with_committed_repo

    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    replace_with_committed_repo(tmp_path)
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
    init = load_script_module(
        "init_lesson_ledger_race_test", ROOT / "scripts/lessons/init_lesson_ledger.py"
    )
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
    assert "appeared at `charness-artifacts/retro/lesson-ledger.json`" in str(raised.value)
    assert (tmp_path / "charness-artifacts/retro/lesson-ledger.json").read_bytes() == winner


def test_empty_ledger_bootstrap_entrypoint_reports_refusal_without_traceback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    monkeypatch.setattr(sys, "argv", ["init_lesson_ledger.py", "--repo-root", str(tmp_path)])
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(ROOT / "scripts/lessons/init_lesson_ledger.py"), run_name="__main__")
    assert caught.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "it is append-only" in captured.err
    assert "check_lesson_ledger.py" in captured.err
    assert "Traceback" not in captured.err


def test_validation_migrates_in_memory_and_never_writes_the_ledger(tmp_path: Path) -> None:
    """A read must not perform a durable schema upgrade.

    `lesson_selection_preview_lib` calls `validate_lesson_ledger`, and AGENTS.md makes
    that preview the FIRST command a session runs. While validation persisted the
    migration, merely OPENING a session upgraded a consumer's ledger to a schema the
    previously released version cannot read -- and the release notes prescribe
    rollback by reinstalling that version. Measured before the repair: a schema-8
    ledger came back schema 9 after nothing but `render_lesson_selection_preview.py`.

    Nothing is lost. Score, lifecycle and seed each migrate inside their own lock, so
    the upgrade still lands on the first authorized WRITE.
    """
    source_dir = ROOT / "charness-artifacts/retro"
    output_dir = tmp_path / "charness-artifacts/retro"
    shutil.copytree(source_dir, output_dir)
    path = output_dir / "lesson-ledger.json"
    legacy = legacy_v8_payload(json.loads(path.read_text(encoding="utf-8")))
    path.write_text(json.dumps(legacy), encoding="utf-8")
    before = path.read_bytes()

    result = ledger.validate_lesson_ledger(
        repo_root=tmp_path,
        output_dir=output_dir,
        summary_path=output_dir / "recent-lessons.md",
    )

    # The verdict is complete (over the v8 corpus, which is the live working set;
    # see `legacy_v8_payload`)...
    assert result["lesson_count"] == len(legacy["lessons"])
    # ...and the consumer's file is byte-for-byte what it was.
    assert path.read_bytes() == before
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 8
