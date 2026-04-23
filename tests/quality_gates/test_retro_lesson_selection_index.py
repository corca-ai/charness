from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def seed_repo(tmp_path: Path, *artifacts: tuple[str, str]) -> Path:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/retro",
                "summary_path: charness-artifacts/retro/recent-lessons.md",
                "evidence_paths: []",
                "metrics_commands: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for filename, body in artifacts:
        (output_dir / filename).write_text(body, encoding="utf-8")
    return repo


def retro_artifact(date: str, *, waste: str, improvement: str) -> str:
    return (
        "\n".join(
            [
                "# Session Retro",
                f"Date: {date}",
                "",
                "## Context",
                "",
                "- Context should stay source-linked.",
                "",
                "## Waste",
                "",
                f"- {waste}",
                "",
                "## Next Improvements",
                "",
                f"- workflow: {improvement}",
            ]
        )
        + "\n"
    )


def test_build_retro_lesson_selection_index_writes_source_linked_candidates(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        (
            "2026-04-01-old.md",
            retro_artifact(
                "2026-04-01",
                waste="Plugin export was verified too late.",
                improvement="Sync generated surfaces before broad validation.",
            ),
        ),
        (
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Plugin export was verified too late.",
                improvement="Validate committed state directly.",
            ),
        ),
    )
    result = run_script("scripts/build_retro_lesson_selection_index.py", "--repo-root", str(repo), "--write", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["index_path"] == "charness-artifacts/retro/lesson-selection-index.json"

    index = json.loads((repo / payload["index_path"]).read_text(encoding="utf-8"))
    assert index["kind"] == "retro-lesson-selection-index"
    assert index["selection_policy"]["advisory"] is True
    assert index["selection_policy"]["alpha_t"] == "alpha_base * min(1, source_count / warmup_n)"
    repeated = next(item for item in index["candidates"] if item["lesson"] == "Plugin export was verified too late.")
    assert repeated["kind"] == "repeat_trap"
    assert repeated["source_count"] == 2
    assert repeated["latest_source_path"] == "charness-artifacts/retro/2026-04-15-new.md"
    assert repeated["selection_weight"] > repeated["recency_weight"]


def test_build_retro_lesson_selection_index_check_rejects_stale_index(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        (
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Manual summary refresh was easy to forget.",
                improvement="Refresh recent lessons through the persistence helper.",
            ),
        ),
    )
    stale = repo / "charness-artifacts" / "retro" / "lesson-selection-index.json"
    stale.write_text("{}\n", encoding="utf-8")
    result = run_script("scripts/build_retro_lesson_selection_index.py", "--repo-root", str(repo), "--check")
    assert result.returncode == 1
    assert "retro lesson selection index" in result.stderr
    assert "--write" in result.stderr


def test_refresh_recent_lessons_prefers_index_ranked_repeated_lessons(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        (
            "2026-04-01-old.md",
            retro_artifact(
                "2026-04-01",
                waste="Plugin export was verified too late.",
                improvement="Sync generated surfaces before broad validation.",
            ),
        ),
        (
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Plugin export was verified too late.",
                improvement="Validate committed state directly.",
            ),
        ),
    )
    result = run_script("skills/public/retro/scripts/refresh_recent_lessons.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr

    summary_text = (repo / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")
    assert "Plugin export was verified too late." in summary_text
    assert "sources: 2" in summary_text
    assert "## Selection Policy" in summary_text
