"""Declared recurrence classes drive the task-run lesson injection block."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from scripts.lessons import lesson_ledger_lib
from scripts.task_run import task_run, task_run_lane_runner as lane_runner
from tests.charness_cli.test_task_run_fixtures import _commit, _repo


def _repo_with_lesson(tmp_path: Path, *, slug: str, wording: str) -> Path:
    repo = _repo(tmp_path)
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    source_ref = "charness-artifacts/retro/source-retro.md"
    source = repo / source_ref
    source.write_text(
        f"# Source retro\n\n## Waste\n\n- {wording} recurrence-class: {slug}\n",
        encoding="utf-8",
    )
    transitions = [
        {
            "sequence": 1,
            "transition_id": f"transition-{slug}",
            "lesson_id": slug,
            "source_retro": source_ref,
        }
    ]
    lessons = lesson_ledger_lib._replay_transitions(
        transitions,
        lesson_ledger_lib.candidate_sources(
            repo, output_dir, output_dir / "recent-lessons.md"
        ),
    )
    payload = {
        "kind": lesson_ledger_lib.KIND,
        "schema_version": lesson_ledger_lib.SCHEMA_VERSION,
        "transitions": transitions,
        "score_events": [],
        "lessons": lessons,
        "lifecycle_events": [],
        "active_lesson_budget": lesson_ledger_lib.ACTIVE_LESSON_BUDGET,
    }
    ledger_path = lesson_ledger_lib.lesson_ledger_path(output_dir)
    ledger_path.write_text(json.dumps(payload), encoding="utf-8")
    _commit(repo, "add validated lesson ledger", source_ref, ledger_path.relative_to(repo).as_posix())
    return repo


def test_declared_class_reaches_the_prepared_lane_command(tmp_path: Path, monkeypatch) -> None:
    repo = _repo_with_lesson(
        tmp_path, slug="known-class", wording="Check the source boundary first."
    )
    brief = "Lane size: 30 minutes; 1 commit unit\nrecurrence-class: known-class"
    command_prompt: list[str] = []
    monkeypatch.setattr(lane_runner, "lane_writable_dirs", lambda *_args, **_kwargs: [])

    def record_command(**kwargs):
        command_prompt.append(kwargs["prompt"])
        return ["codex"]

    monkeypatch.setattr(lane_runner, "lane_command", record_command)
    payload = {"repo_root": str(repo)}
    _, prompt, command = lane_runner.prepare_lane_execution(
        payload,
        {},
        repo,
        tmp_path / "runtime",
        prompt=brief,
        require_change=True,
        scopes=["module.py"],
        executor="codex",
        executable="codex",
        effort="medium",
        worktree=repo,
    )

    assert command == ["codex"]
    assert command_prompt == [prompt]
    assert "- known-class: Check the source boundary first." in prompt
    assert "Full ledger: charness-artifacts/retro/lesson-ledger.json" in prompt
    assert payload["lesson_injection"]["injected_ids"] == ["known-class"]


def test_unknown_class_is_unmatched_and_never_injected(tmp_path: Path) -> None:
    repo = _repo_with_lesson(
        tmp_path, slug="known-class", wording="Check the source boundary first."
    )
    block, result = lane_runner._prepare_lesson_injection(
        repo, "recurrence-class: missing-class"
    )

    assert result["unmatched_slugs"] == ["missing-class"]
    assert result["injected_ids"] == []
    assert "- missing-class:" not in block


def test_lesson_injection_byte_budget_excludes_oversized_lesson(tmp_path: Path) -> None:
    repo = _repo_with_lesson(
        tmp_path, slug="large-class", wording="교훈 " + "가" * 5000
    )
    block, result = lane_runner._prepare_lesson_injection(
        repo, "recurrence-class: large-class", budget_bytes=512
    )

    assert len(("\n\n" + block).encode("utf-8")) <= 512
    assert result["used_bytes"] <= 512
    assert result["injected_ids"] == []
    assert result["budget_excluded_ids"] == ["large-class"]


def test_result_json_records_injected_and_unmatched_ids(tmp_path: Path) -> None:
    repo = _repo_with_lesson(
        tmp_path, slug="known-class", wording="Check the source boundary first."
    )
    captured_prompt = tmp_path / "captured-prompt.txt"
    codex = tmp_path / "codex"
    codex.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        "from pathlib import Path\n"
        f"Path({str(captured_prompt)!r}).write_text(sys.stdin.read(), encoding='utf-8')\n"
        "print('task complete')\n",
        encoding="utf-8",
    )
    codex.chmod(0o755)
    brief = (
        "Lane size: 30 minutes; 1 commit unit\n"
        "recurrence-class: known-class\n"
        "recurrence-class: missing-class\n"
    )
    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane-worktree",
        branch="lane/lesson-injection",
        base="HEAD",
        scopes=["module.py"],
        prompt=brief,
        codex=os.fspath(codex),
        effort="medium",
        require_change=True,
    )

    block = payload["lesson_injection"]
    saved = json.loads(Path(payload["result_path"]).read_text(encoding="utf-8"))
    assert "- known-class: Check the source boundary first." in captured_prompt.read_text(
        encoding="utf-8"
    )
    assert block["injected_ids"] == ["known-class"]
    assert block["unmatched_slugs"] == ["missing-class"]
    assert saved["lesson_injection"] == block
    assert "Scope-path matching is deferred" in block["non_claim"]
