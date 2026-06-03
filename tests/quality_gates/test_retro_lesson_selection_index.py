from __future__ import annotations

from pathlib import Path

from tests.dsl import Repo, run_at

RETRO = Repo().adapter(
    "retro",
    {
        "version": 1,
        "repo": "demo",
        "language": "en",
        "output_dir": "charness-artifacts/retro",
        "summary_path": "charness-artifacts/retro/recent-lessons.md",
        "evidence_paths": [],
        "metrics_commands": [],
    },
)

BUILD_INDEX = "scripts/build_retro_lesson_selection_index.py"
REFRESH = "skills/public/retro/scripts/refresh_recent_lessons.py"


def artifact(name: str, body: str) -> tuple[str, str]:
    return (f"charness-artifacts/retro/{name}", body)


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
    res = (
        RETRO.file(
            *artifact(
                "2026-04-01-old.md",
                retro_artifact(
                    "2026-04-01",
                    waste="Plugin export was verified too late.",
                    improvement="Sync generated surfaces before broad validation.",
                ),
            )
        )
        .file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Plugin export was verified too late.",
                    improvement="Validate committed state directly.",
                ),
            )
        )
        .run(tmp_path, BUILD_INDEX, "--write", "--json")
        .ok()
    )
    payload = res.json
    assert payload["index_path"] == "charness-artifacts/retro/lesson-selection-index.json"

    index = res.file_json(payload["index_path"])
    assert index["kind"] == "retro-lesson-selection-index"
    assert index["selection_policy"]["advisory"] is True
    assert index["selection_policy"]["alpha_t"] == "alpha_base * min(1, source_count / warmup_n)"
    repeated = next(item for item in index["candidates"] if item["lesson"] == "Plugin export was verified too late.")
    assert repeated["kind"] == "repeat_trap"
    assert repeated["source_count"] == 2
    assert repeated["latest_source_path"] == "charness-artifacts/retro/2026-04-15-new.md"
    assert repeated["selection_weight"] > repeated["recency_weight"]


def test_build_retro_lesson_selection_index_check_rejects_stale_index(tmp_path: Path) -> None:
    (
        RETRO.file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Manual summary refresh was easy to forget.",
                    improvement="Refresh recent lessons through the persistence helper.",
                ),
            )
        )
        .file("charness-artifacts/retro/lesson-selection-index.json", "{}\n")
        .run(tmp_path, BUILD_INDEX, "--check")
        .failed(1)
        .stderr_has("retro lesson selection index", "--write")
    )


def test_build_retro_lesson_selection_index_check_rejects_stale_digest(tmp_path: Path) -> None:
    repo = RETRO.file(
        *artifact(
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Manual summary refresh was easy to forget.",
                improvement="Refresh recent lessons through the persistence helper.",
            ),
        )
    ).build(tmp_path)

    run_at(repo, REFRESH).ok()
    (repo / "charness-artifacts" / "retro" / "recent-lessons.md").write_text(
        "# Recent Retro Lessons\n\nstale\n", encoding="utf-8"
    )

    run_at(repo, BUILD_INDEX, "--check").failed(1).stderr_has(
        "recent lessons digest", "refresh_recent_lessons.py"
    )


def test_refresh_recent_lessons_prefers_index_ranked_repeated_lessons(tmp_path: Path) -> None:
    res = (
        RETRO.file(
            *artifact(
                "2026-04-01-old.md",
                retro_artifact(
                    "2026-04-01",
                    waste="Plugin export was verified too late.",
                    improvement="Sync generated surfaces before broad validation.",
                ),
            )
        )
        .file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Plugin export was verified too late.",
                    improvement="Validate committed state directly.",
                ),
            )
        )
        .run(tmp_path, REFRESH)
        .ok()
    )

    summary_text = res.file_text("charness-artifacts/retro/recent-lessons.md")
    assert "Plugin export was verified too late." in summary_text
    assert "sources: 2" in summary_text
    assert "## Selection Policy" in summary_text
