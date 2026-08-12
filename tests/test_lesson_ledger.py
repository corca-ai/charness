from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger
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
