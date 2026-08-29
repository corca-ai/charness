from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger
from scripts import lesson_score_outcome_lib as outcome_lib
from tests.lesson_ledger_fixtures import outcome_event

ROOT = Path(__file__).resolve().parents[1]


def _retro(repo: Path) -> None:
    path = repo / "charness-artifacts/retro/source.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- useful lesson (recurrence-class: a)\n",
        encoding="utf-8",
    )


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
        "active_lesson_budget": ledger.ACTIVE_LESSON_BUDGET,
        "lifecycle_events": [],
        "score_events": [],
        "lessons": {
            "a": {
                "source_retro": "charness-artifacts/retro/source.md",
                "transition_id": "seed-a",
                "score_total": 0,
                "score_count": 0,
                "outcome_counts": outcome_lib.outcome_counts([]),
                "state": "active",
                "last_lifecycle_event_id": None,
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
                "--lesson-id",
                "a",
                "--source-retro",
                "charness-artifacts/retro/source.md",
                "--outcome",
                "read-but-not-applied",
                "--anchor",
                "in view at the decision and still not applied",
            ],
        ),
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
            "outcome_counts": outcome_lib.outcome_counts([]),
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
    score = _score_event(score=2, anchor="evidence")
    for events, message in (
        ([None], "is not an object"),
        ([_score_event(event_id=" ")], "non-whitespace"),
        # The retired magnitude>=2 anchor rule, replaced by the rule that made it
        # unnecessary: every OUTCOME carries an anchor, so an outcome event missing
        # one fails as a key-set refusal rather than as a magnitude special case.
        (
            [
                {
                    k: v
                    for k, v in outcome_event(
                        event_id="score-a",
                        lesson_id="a",
                        source_retro="charness-artifacts/retro/source.md",
                    ).items()
                    if k != "anchor"
                }
            ],
            "unexpected or missing fields",
        ),
        # And the citation split: an OUTCOME event citing a path outside the retro
        # directory is refused on SHAPE, without the recurrence-tag rule that only
        # legacy events answer to.
        (
            [
                outcome_event(
                    event_id="score-a",
                    lesson_id="a",
                    source_retro="notes/elsewhere.md",
                )
            ],
            "must be a repo-relative",
        ),
        ([score, {**score, "event_id": "score-b"}], "duplicate"),
        (
            [{**_score_event(score=0), "source_retro": "other.md"}],
            "invalid legacy citation",
        ),
    ):
        with pytest.raises(ValueError, match=message):
            ledger._replay_scores(
                events,
                copy.deepcopy(replayed),
                {"a": {"charness-artifacts/retro/source.md"}},
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
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, json.dumps({}), ""),
    )
    with pytest.raises(ValueError, match="unrecognized shape"):
        ledger._committed_state(tmp_path, path)
    # NEWER committed version: refused. A tool must never write an older shape
    # over a ledger a newer tool committed, because `lessons` is derived and not
    # prefix-protected, so the downgrade would pass every remaining check.
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({"kind": ledger.KIND, "transitions": [], "schema_version": ledger.SCHEMA_VERSION + 1}), ""
        ),
    )
    with pytest.raises(ValueError, match="newer than this tool"):
        ledger._committed_state(tmp_path, path)
    current = {
        "kind": ledger.KIND,
        "transitions": [],
        "schema_version": ledger.SCHEMA_VERSION,
        "score_events": [],
        "lifecycle_events": [],
        "active_lesson_budget": ledger.ACTIVE_LESSON_BUDGET,
        "lessons": {},
    }
    monkeypatch.setattr(
        ledger.subprocess,
        "run", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, json.dumps(current), "")
    )
    assert ledger._committed_state(tmp_path, path) == ([], [], ledger.ACTIVE_LESSON_BUDGET, [])
    unsupported = {**current, "schema_version": ledger.SCHEMA_VERSION - 2}
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, json.dumps(unsupported), ""),
    )
    with pytest.raises(ValueError, match="unsupported schema version"):
        ledger._committed_state(tmp_path, path)
    # And a version-less or non-integer committed value is refused rather than
    # silently treated as older -- with its OWN message, because "newer than this
    # tool" is false for a missing version and was pinned that way until round 2.
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({**current, "schema_version": "7"}), ""
        ),
    )
    with pytest.raises(ValueError, match="non-integer schema_version"):
        ledger._committed_state(tmp_path, path)
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({k: v for k, v in current.items() if k != "schema_version"}), ""
        ),
    )
    with pytest.raises(ValueError, match="non-integer schema_version"):
        ledger._committed_state(tmp_path, path)
    # Missing append-only list: refused, and the message names what it checks.
    monkeypatch.setattr(
        ledger.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, json.dumps({k: v for k, v in current.items() if k != "score_events"}), ""
        ),
    )
    with pytest.raises(ValueError, match="missing a required append-only list"):
        ledger._committed_state(tmp_path, path)
