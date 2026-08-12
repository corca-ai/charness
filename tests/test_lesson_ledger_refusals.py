from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger

ROOT = Path(__file__).resolve().parents[1]


def _retro(repo: Path) -> None:
    path = repo / "charness-artifacts/retro/source.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: a)\n",
        encoding="utf-8",
    )


def _session_event() -> dict:
    snapshot = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "selection_policy_version": 1,
        "seed": "seed-a",
        "eligible_count": 1,
        "bucket_counts": {
            "recent": 1,
            "value": 0,
            "uncertainty": 0,
            "archive": 0,
            "archive_fallback_uncertainty": 0,
        },
        "lesson_ids": ["a"],
    }
    return {
        "session_id": "session-a",
        "snapshot": snapshot,
        "snapshot_sha256": ledger.snapshot_sha256(snapshot),
    }


def _score_event(**extra: object) -> dict:
    event = {
        "event_id": "score-a",
        "source_retro": "charness-artifacts/retro/source.md",
        "lesson_id": "a",
        "score": 0,
    }
    event.update(extra)
    return event


def _payload() -> dict:
    return {
        "kind": ledger.KIND,
        "schema_version": ledger.SCHEMA_VERSION,
        "transitions": [
            {
                "sequence": 1,
                "transition_id": "seed-a",
                "lesson_id": "a",
                "source_retro": "charness-artifacts/retro/source.md",
            }
        ],
        "legacy_score_event_count": 0,
        "session_events": [],
        "score_events": [],
        "lessons": {
            "a": {
                "source_retro": "charness-artifacts/retro/source.md",
                "transition_id": "seed-a",
                "score_total": 0,
                "score_count": 0,
            }
        },
    }


def _write_ledger(repo: Path) -> Path:
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_payload()), encoding="utf-8")
    return path


def test_ledger_checker_and_writer_scripts_print_refusals(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(tmp_path)])
    with pytest.raises(SystemExit, match="1"):
        runpy.run_path(str(ROOT / "scripts/check_lesson_ledger.py"), run_name="__main__")
    assert "missing lesson ledger" in capsys.readouterr().err
    for script, args in (
        (
            "record_lesson_score.py",
            [
                "--event-id",
                "x",
                "--session-id",
                "s",
                "--lesson-id",
                "a",
                "--source-retro",
                "source.md",
                "--score",
                "0",
            ],
        ),
        ("record_lesson_session.py", ["--session-id", "s", "--seed", "seed"]),
    ):
        monkeypatch.setenv("CHARNESS_REPO_ROOT", str(tmp_path))
        monkeypatch.setattr(sys, "argv", [script, "--repo-root", str(tmp_path), *args])
        with pytest.raises(SystemExit, match="1"):
            runpy.run_path(str(ROOT / "scripts" / script), run_name="__main__")
        assert "missing lesson ledger" in capsys.readouterr().err


def test_ledger_validator_exercises_replay_refusal_paths(tmp_path: Path, monkeypatch) -> None:
    _retro(tmp_path)
    replayed = {
        "a": {
            "source_retro": "charness-artifacts/retro/source.md",
            "transition_id": "seed-a",
            "score_total": 0,
            "score_count": 0,
        }
    }
    transition = {
        "sequence": 1,
        "transition_id": "seed-a",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
    }
    for invalid, message in (
        ([{**transition, "sequence": True}], "sequences"),
        ([{**transition, "transition_id": ""}], "non-empty"),
        ([transition, {**transition, "sequence": 2, "lesson_id": "b"}], "duplicate"),
        ([{**transition, "source_retro": "other.md"}], "citation"),
    ):
        with pytest.raises(ValueError, match=message):
            ledger._replay_transitions(invalid, {"a": {"charness-artifacts/retro/source.md"}})
    valid_session = _session_event()
    for invalid, message in (
        ([None], "unexpected"),
        ([{"session_id": "", "snapshot": {}, "snapshot_sha256": "x"}], "non-empty"),
        ([{**valid_session, "snapshot": {}}], "snapshot shape"),
    ):
        with pytest.raises(ValueError, match=message):
            ledger._replay_sessions(invalid, replayed)
    unknown_lesson = _session_event()
    unknown_lesson["snapshot"]["lesson_ids"] = ["other"]
    unknown_lesson["snapshot"]["eligible_count"] = 1
    unknown_lesson["snapshot_sha256"] = ledger.snapshot_sha256(unknown_lesson["snapshot"])
    with pytest.raises(ValueError, match="unseeded"):
        ledger._replay_sessions([unknown_lesson], replayed)
    bad_digest = _session_event()
    bad_digest["snapshot_sha256"] = "z" * 64
    with pytest.raises(ValueError, match="lowercase SHA"):
        ledger._replay_sessions([bad_digest], replayed)
    bad_buckets = _session_event()
    bad_buckets["snapshot"]["bucket_counts"] = {}
    bad_buckets["snapshot_sha256"] = ledger.snapshot_sha256(bad_buckets["snapshot"])
    with pytest.raises(ValueError, match="bucket_counts"):
        ledger._replay_sessions([bad_buckets], replayed)
    score = _score_event(session_id="session-a", score=2, anchor="evidence")
    sessions = {"session-a": {"a"}}
    for events, message in (
        ([None], "unexpected"),
        ([_score_event(event_id=" ", session_id="session-a")], "non-whitespace"),
        ([_score_event(session_id="session-a", score=2)], "needs an anchor"),
        ([score, {**score, "event_id": "score-b"}], "duplicate"),
        (
            [{**_score_event(session_id="session-a", score=0), "source_retro": "other.md"}],
            "invalid citation",
        ),
    ):
        with pytest.raises(ValueError, match=message):
            ledger._replay_scores(
                events,
                0,
                copy.deepcopy(replayed),
                {"a": {"charness-artifacts/retro/source.md"}},
                sessions,
            )
    path = _write_ledger(tmp_path)
    with pytest.raises(ValueError, match="invalid containers"):
        ledger.replay_validated_ledger_payload(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            path=path,
            payload={**_payload(), "score_events": {}},
        )
    mismatched = _payload()
    mismatched["lessons"]["a"]["transition_id"] = "wrong"
    with pytest.raises(ValueError, match="deterministic replay"):
        ledger.replay_validated_ledger_payload(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
            path=path,
            payload=mismatched,
        )
    with pytest.raises(FileNotFoundError, match="missing lesson ledger"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=tmp_path / "missing",
            summary_path=path.parent / "recent-lessons.md",
        )
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        ledger.validate_lesson_ledger(
            repo_root=tmp_path,
            output_dir=path.parent,
            summary_path=path.parent / "recent-lessons.md",
        )
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, "{", ""),
    )
    with pytest.raises(ValueError, match="committed ledger is invalid JSON"):
        ledger._committed_state(tmp_path, path)
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({"kind": ledger.KIND, "transitions": [], "schema_version": 1}), ""
        ),
    )
    assert ledger._committed_state(tmp_path, path) == ([], [], 0, [])
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, json.dumps({}), ""),
    )
    with pytest.raises(ValueError, match="unrecognized shape"):
        ledger._committed_state(tmp_path, path)
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({"kind": ledger.KIND, "transitions": [], "schema_version": 9}), ""
        ),
    )
    with pytest.raises(ValueError, match="unsupported session"):
        ledger._committed_state(tmp_path, path)
