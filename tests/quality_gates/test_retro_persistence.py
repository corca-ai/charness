from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_persist_retro_artifact_writes_artifact_snapshot_and_recent_lessons(tmp_path: Path) -> None:
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
                "snapshot_path: .charness/retro/weekly-latest.json",
                "summary_path: charness-artifacts/retro/recent-lessons.md",
                "evidence_paths: []",
                "metrics_commands: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    markdown_file = repo / "weekly.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Weekly Retro",
                "",
                "## Context",
                "",
                "- Durable persistence should refresh recent lessons automatically.",
                "",
                "## Waste",
                "",
                "- Manual summary refresh was easy to forget.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: Use one persistence helper that writes the artifact and refreshes the digest.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    snapshot_file = repo / "snapshot.json"
    snapshot_file.write_text(
        json.dumps({"mode": "weekly", "window": {"start": "2026-04-07", "end": "2026-04-14"}}),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/persist_retro_artifact.py",
        "--repo-root",
        str(repo),
        "--artifact-name",
        "weekly-2026-04-14.md",
        "--markdown-file",
        str(markdown_file),
        "--snapshot-file",
        str(snapshot_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/retro/weekly-2026-04-14.md"
    assert payload["snapshot_path"] == ".charness/retro/weekly-latest.json"
    assert payload["summary_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert payload["lesson_selection_index_path"] == "charness-artifacts/retro/lesson-selection-index.json"
    assert payload["summary_refreshed"] is True

    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "Durable persistence should refresh recent lessons automatically." in summary_text
    assert "Manual summary refresh was easy to forget." in summary_text
    assert (output_dir / "lesson-selection-index.json").is_file()


def test_persist_retro_artifact_skips_self_refresh_for_summary_target(tmp_path: Path) -> None:
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
    markdown_file = repo / "summary.md"
    markdown_file.write_text("# Recent Retro Lessons\n", encoding="utf-8")

    result = run_script(
        "skills/public/retro/scripts/persist_retro_artifact.py",
        "--repo-root",
        str(repo),
        "--artifact-name",
        "recent-lessons.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert payload["summary_refreshed"] is False
