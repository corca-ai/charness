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
    assert index["selection_policy"]["alpha_t"] == "alpha_base * min(1, independent_source_count / warmup_n)"
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


def generated_release_trigger_artifact(date: str, tag: str, *, improvement: str) -> str:
    """The exact shape `publish_release_retro.py` emits, one per publish."""
    return (
        "\n".join(
            [
                f"# Retro: Release Auto-Retro Trigger {tag}",
                f"Date: {date}",
                "Mode: release-trigger",
                "",
                "## Context",
                "",
                "- Release publish triggered a configured automatic retro.",
                "",
                "## Waste",
                "",
                "- Boilerplate waste line identical in every emission.",
                "",
                "## Next Improvements",
                "",
                f"- workflow: {improvement}",
            ]
        )
        + "\n"
    )


def test_recurrence_boost_counts_observations_not_template_emissions(tmp_path: Path) -> None:
    """One template emitted N times is ONE observation, not N recurring ones.

    The index's recurrence boost is `1 + alpha * (source_count - 1)`, and
    `source_count` counted artifacts. The release helper writes one auto-retro per
    publish with a fixed body, so its boilerplate accumulated 121 "sources" in this
    repo and outranked genuine human lessons for a slot in the next session's opening
    checklist — boosted precisely BECAUSE it was boilerplate. Recurrence is supposed
    to measure independent observation; across one generator it measures release
    frequency.

    A human lesson repeated across two hand-written retros must still get its boost.
    """
    repo = RETRO
    for index, (date, tag) in enumerate(
        [("2026-04-02", "v1.0.0"), ("2026-04-03", "v1.1.0"), ("2026-04-04", "v1.2.0"), ("2026-04-05", "v1.3.0")]
    ):
        repo = repo.file(
            *artifact(
                f"{date}-{tag.replace('.', '-')}-release-auto-retro.md",
                generated_release_trigger_artifact(date, tag, improvement="Generated boilerplate improvement."),
            )
        )
    # Two independently authored retros carrying the same human lesson.
    repo = repo.file(
        *artifact("2026-04-02-session-a.md", retro_artifact("2026-04-02", waste="w", improvement="Hand-authored lesson."))
    ).file(
        *artifact("2026-04-03-session-b.md", retro_artifact("2026-04-03", waste="w", improvement="Hand-authored lesson."))
    )

    index = repo.run(tmp_path, BUILD_INDEX, "--write", "--json").ok().file_json(
        "charness-artifacts/retro/lesson-selection-index.json"
    )
    by_lesson = {item["lesson"]: item for item in index["candidates"]}

    generated = by_lesson["Generated boilerplate improvement."]
    human = by_lesson["Hand-authored lesson."]

    # The raw count stays honest for auditing...
    assert generated["source_count"] == 4
    # ...but four emissions of one template are one independent observation, so the
    # recurrence multiplier is 1.0 and the weight is pure recency.
    assert generated["independent_source_count"] == 1
    assert generated["selection_weight"] == generated["recency_weight"]

    # A genuinely repeated human lesson keeps its boost.
    assert human["independent_source_count"] == 2
    assert human["selection_weight"] > human["recency_weight"]


def test_generator_signature_ignores_a_quoted_header_in_a_human_retro(tmp_path: Path) -> None:
    """The retro that DOCUMENTS the generator must not be classified as one.

    Both signatures are header fields, but matched over the whole body they fire on a
    fenced quote of the generated title. The artifact is then tagged as a template
    emission, every one of its lessons merges into the generator bucket, and it
    contributes zero independent observations — one quoted line mutes a real retro.
    """
    body = "\n".join(
        [
            "# Session Retro",
            "Date: 2026-04-20",
            "",
            "## Context",
            "",
            "- Documented the generated-retro signature.",
            "",
            "## Waste",
            "",
            "- Generated retros were titled:",
            "  ```",
            "  # Retro: Release Auto-Retro Trigger v2.11.0",
            "  Mode: release-trigger",
            "  ```",
            "  which made every emission look like an independent observation.",
            "",
            "## Next Improvements",
            "",
            "- workflow: Quoted-header lesson.",
            "",
        ]
    )
    index = (
        RETRO.file(*artifact("2026-04-20-session-quoting.md", body))
        .file(
            *artifact(
                "2026-04-21-session-other.md",
                retro_artifact("2026-04-21", waste="w", improvement="Quoted-header lesson."),
            )
        )
        .run(tmp_path, BUILD_INDEX, "--write", "--json")
        .ok()
        .file_json("charness-artifacts/retro/lesson-selection-index.json")
    )

    lesson = next(item for item in index["candidates"] if item["lesson"] == "Quoted-header lesson.")
    # Two hand-authored retros = two independent observations, quote notwithstanding.
    assert lesson["independent_source_count"] == 2
    assert lesson["generator_authored"] == 0


def test_hand_authored_lesson_outranks_boilerplate_at_equal_weight(tmp_path: Path) -> None:
    """Collapsing the multiplier was not enough; the tiebreaker undid it.

    Same-day candidates all reach selection_weight 1.0, so ordering fell through to
    the raw `source_count` — and 120-vs-1 put the template line back at rank 1, pushing
    a real lesson out of the digest's four slots. Observed in the shipped digest before
    this fix.
    """
    repo = RETRO
    for date, tag in [("2026-04-20", "v1.0.0"), ("2026-04-20", "v1.1.0"), ("2026-04-20", "v1.2.0")]:
        repo = repo.file(
            *artifact(
                f"{date}-{tag.replace('.', '-')}-release-auto-retro.md",
                generated_release_trigger_artifact(date, tag, improvement="Template boilerplate."),
            )
        )
    repo = repo.file(
        *artifact("2026-04-20-human.md", retro_artifact("2026-04-20", waste="w", improvement="Human observation."))
    )

    index = repo.run(tmp_path, BUILD_INDEX, "--write", "--json").ok().file_json(
        "charness-artifacts/retro/lesson-selection-index.json"
    )
    improvements = [item for item in index["candidates"] if item["kind"] == "next_improvement"]
    assert improvements[0]["lesson"] == "Human observation.", [item["lesson"] for item in improvements]
    assert improvements[0]["selection_weight"] == improvements[1]["selection_weight"]
