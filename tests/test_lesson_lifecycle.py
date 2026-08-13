from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import lesson_ledger_lib as ledger
from scripts import record_lesson_lifecycle as lifecycle_recorder
from tests.test_lesson_ledger import (
    ROOT,
    _git,
    _ledger,
    _retro,
    _score_event,
    _session_event,
    _validate,
)


def test_archive_and_resurrection_preserve_scores_and_refuse_invalid_transition(
    tmp_path: Path,
) -> None:
    _retro(tmp_path, "source.md", "a")
    decision = tmp_path / "decision.md"
    decision.write_text("# Reviewed Decision\n", encoding="utf-8")
    path = _ledger(
        tmp_path,
        session_events=[_session_event()],
        score_events=[_score_event(session_id="session-a", score=2, anchor="evidence")],
    )
    command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/record_lesson_lifecycle.py"),
            "--repo-root",
            str(tmp_path),
            "--event-id",
            "archive-a",
            "--lesson-id",
            "a",
            "--action",
            "archive",
            "--decision-ref",
            "decision.md",
            "--rationale",
            "Reviewed low-value slot decision.",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert command.returncode == 0, command.stderr
    assert json.loads(command.stdout)["event_id"] == "archive-a"
    archived = json.loads(path.read_text(encoding="utf-8"))
    assert archived["lessons"]["a"]["score_total"] == 2
    assert archived["lessons"]["a"]["state"] == "archived"
    before = path.read_bytes()
    with pytest.raises(ValueError, match="cannot archive"):
        lifecycle_recorder.append_lifecycle_event(
            repo_root=tmp_path,
            event_id="archive-again",
            lesson_id="a",
            action="archive",
            decision_ref="decision.md",
            rationale="Invalid duplicate archive.",
        )
    assert path.read_bytes() == before
    lifecycle_recorder.append_lifecycle_event(
        repo_root=tmp_path,
        event_id="resurrect-a",
        lesson_id="a",
        action="resurrect",
        decision_ref="decision.md",
        rationale="Reviewed archive-slot resurrection.",
    )
    resurrected = json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]
    assert (resurrected["score_total"], resurrected["score_count"]) == (2, 1)
    assert resurrected["state"] == "active"


def test_lifecycle_cli_refuses_unknown_lesson_without_rewriting(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    (tmp_path / "decision.md").write_text("# Reviewed Decision\n", encoding="utf-8")
    path = _ledger(tmp_path)
    before = path.read_bytes()
    command = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/record_lesson_lifecycle.py"),
            "--repo-root",
            str(tmp_path),
            "--event-id",
            "archive-missing",
            "--lesson-id",
            "missing",
            "--action",
            "archive",
            "--decision-ref",
            "decision.md",
            "--rationale",
            "Invalid unknown lesson.",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert command.returncode == 1
    assert command.stderr == "record lesson lifecycle: lesson_id `missing` is not seeded\n"
    assert path.read_bytes() == before


def test_lifecycle_budget_and_committed_prefix_are_enforced(tmp_path: Path) -> None:
    (tmp_path / "decision.md").write_text("# Decision\n", encoding="utf-8")
    replayed = {
        f"lesson-{index}": {"state": "active", "last_lifecycle_event_id": None}
        for index in range(51)
    }
    with pytest.raises(ValueError, match="exceeds fixed budget"):
        ledger._replay_lifecycle([], replayed, budget=50, repo_root=tmp_path)

    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    _retro(tmp_path, "source.md", "a")
    path = _ledger(tmp_path)
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "seed v4 ledger")
    lifecycle_recorder.append_lifecycle_event(
        repo_root=tmp_path,
        event_id="archive-a",
        lesson_id="a",
        action="archive",
        decision_ref="decision.md",
        rationale="Reviewed archive.",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "archive lesson")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["lifecycle_events"][0]["rationale"] = "rewritten"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="committed lifecycle events"):
        _validate(tmp_path)
