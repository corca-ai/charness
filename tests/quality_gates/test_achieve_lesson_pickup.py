from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_lesson_pickup.py"
LESSON_PICKUP = load_script_module("achieve_goal_lesson_pickup", SCRIPT)


def _summary(repo: Path, text: str) -> None:
    path = repo / "charness-artifacts/retro/recent-lessons.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_pickup_reads_only_the_compact_digest_and_returns_bucketed_context(tmp_path: Path) -> None:
    _summary(
        tmp_path,
        """# Recent Retro Lessons

## Current Focus

- focus lesson

## Repeat Traps

- trap lesson

## Next-Time Checklist

- checklist lesson
""",
    )
    # An invalid ledger must not matter: pickup consumes the generated projection,
    # never the raw corpus or a validation/rebuild path.
    ledger = tmp_path / "charness-artifacts/retro/lesson-ledger.json"
    ledger.write_text("not json\n", encoding="utf-8")

    result = LESSON_PICKUP.read_goal_lessons(tmp_path, "demo#7")

    assert result["status"] == "selected"
    assert result["source"] == "recent-lessons"
    assert result["selection"] == "precomputed-projection-only"
    assert result["freshness"] == "not-checked"
    assert [item["lesson"] for item in result["items"]] == [
        "focus lesson",
        "trap lesson",
        "checklist lesson",
    ]
    assert result["source_path"] == "charness-artifacts/retro/recent-lessons.md"


def test_pickup_falls_back_to_index_without_rebuilding_it(tmp_path: Path) -> None:
    index = tmp_path / "charness-artifacts/retro/lesson-selection-index.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        json.dumps(
            {
                "kind": "retro-lesson-selection-index",
                "top_candidates": [
                    {"kind": "repeat_trap", "lesson": "indexed lesson"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = LESSON_PICKUP.read_goal_lessons(tmp_path, "demo#8")

    assert result["status"] == "selected"
    assert result["source"] == "lesson-selection-index"
    assert result["items"] == [{"section": "repeat_trap", "lesson": "indexed lesson"}]


def test_missing_projection_is_non_blocking(tmp_path: Path) -> None:
    result = LESSON_PICKUP.read_goal_lessons(tmp_path, "demo#9")

    assert result["status"] == "unavailable"
    assert result["reason"] == "lesson-projection-missing-or-empty"


def test_malformed_projection_encoding_is_non_blocking(tmp_path: Path) -> None:
    summary = tmp_path / "charness-artifacts/retro/recent-lessons.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_bytes(b"## Current Focus\n- \xff\n")
    index = summary.parent / "lesson-selection-index.json"
    index.write_bytes(b"{\xff")

    result = LESSON_PICKUP.read_goal_lessons(tmp_path, "demo#10")

    assert result["status"] == "unavailable"


def test_artifact_only_cli_reads_projection_without_writing_to_repo(tmp_path: Path) -> None:
    _summary(
        tmp_path,
        """# Recent Retro Lessons

## Current Focus

- cli lesson
""",
    )
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    runtime_root = tmp_path.parent / f"{tmp_path.name}-lesson-runtime"
    runtime_root.mkdir()
    (runtime_root / "tmp").mkdir()
    env = os.environ.copy()
    env.update(
        {
            "CHARNESS_RUNTIME_ROOT": str(runtime_root),
            "PYTHONPYCACHEPREFIX": str(runtime_root / "pycache"),
            "TMPDIR": str(runtime_root / "tmp"),
        }
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--goal-key",
            "artifact:demo-goal.md",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "status: selected" in result.stdout
    assert "cli lesson" in result.stdout
    assert {path.relative_to(tmp_path) for path in tmp_path.rglob("*")} == before


def test_goal_pickup_keeps_working_when_optional_reader_cannot_load(
    monkeypatch, tmp_path: Path
) -> None:
    import importlib.util

    path = ROOT / "skills/public/achieve/scripts/goal_run_pickup.py"
    spec = importlib.util.spec_from_file_location("goal_run_pickup_optional_reader", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_achieve_script", lambda _name: tmp_path / "missing.py")

    result = module.read_goal_lessons(tmp_path, "demo#11")

    assert result["status"] == "unavailable"
    assert result["kind"] == "charness.goal-lesson-pickup/v1"


def test_achieve_contract_routes_lesson_read_through_pickup() -> None:
    skill = " ".join(
        (ROOT / "skills/public/achieve/SKILL.md").read_text(encoding="utf-8").split()
    )
    during = " ".join(
        (
            ROOT / "skills/public/achieve/references/lifecycle-during.md"
        ).read_text(encoding="utf-8").split()
    )

    assert "goal_lesson_pickup.py" in skill
    assert "recent-lessons.md" in skill
    assert "artifact:<relative-goal-file>" in skill
    assert "do not invoke the lesson reader a second time" in skill
    assert "never rebuilds the ledger/index" in during
    assert "session receipt" in during
