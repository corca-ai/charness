from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts import lesson_ledger_lib as ledger
from scripts import record_lesson_lifecycle as lifecycle_recorder
from tests.script_main import run_loaded_script_main
from tests.test_lesson_ledger import (
    _git,
    _ledger,
    _retro,
    _score_event,
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
        score_events=[_score_event(score=2, anchor="evidence")],
    )
    # In-process, not subprocess: the recorder is already imported above, and this
    # repo ratchets the test-suite process boundary down. Driving the same `main()`
    # through argv keeps the CLI contract (exit code and emitted payload) under test
    # without minting a new convertible bypass.
    command = run_loaded_script_main(
        "record_lesson_lifecycle.py",
        lifecycle_recorder,
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
    )
    assert command.returncode == 0, command.stderr
    assert yaml.safe_load(command.stdout)["event_id"] == "archive-a"
    archived = json.loads(path.read_text(encoding="utf-8"))
    # 1, not 2: archiving still PRESERVES the score, and the score itself is now
    # a valence sum -- a legacy `+2` contributes its sign, never its size.
    assert archived["lessons"]["a"]["score_total"] == 1
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
    assert (resurrected["score_total"], resurrected["score_count"]) == (1, 1)
    assert resurrected["state"] == "active"


def test_lifecycle_cli_refuses_unknown_lesson_without_rewriting(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    (tmp_path / "decision.md").write_text("# Reviewed Decision\n", encoding="utf-8")
    path = _ledger(tmp_path)
    before = path.read_bytes()
    command = run_loaded_script_main(
        "record_lesson_lifecycle.py",
        lifecycle_recorder,
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
        # The entrypoint block maps these to exit 1 with the message on stderr; the
        # in-process runner has to be told the same vocabulary or it would re-raise
        # and the refusal contract would go untested.
        cli_error_types=(FileNotFoundError, OSError, ValueError, KeyError),
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
