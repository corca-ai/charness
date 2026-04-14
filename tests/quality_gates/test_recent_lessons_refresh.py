from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_refresh_recent_lessons_from_latest_retro_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "skill-outputs" / "retro"
    output_dir.mkdir(parents=True)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: skill-outputs/retro",
                "summary_path: skill-outputs/retro/recent-lessons.md",
                "evidence_paths: []",
                "metrics_commands: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    older = output_dir / "session-2026-04-10.md"
    older.write_text("## Context\n- old\n", encoding="utf-8")
    latest = output_dir / "weekly-2026-04-14.md"
    latest.write_text(
        "\n".join(
            [
                "# Weekly Retro",
                "",
                "## Context",
                "",
                "- The repo should stop relearning sync boundaries.",
                "- Focus on durable retro memory, not chat-only recollection.",
                "",
                "## Waste",
                "",
                "- Source and installed surfaces drifted independently.",
                "- Plugin export was verified too late.",
                "",
                "## Next Improvements",
                "",
                "- `workflow`: Sync generated surfaces before broad validation.",
                "- `memory`: Refresh recent lessons from the latest durable retro.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/retro/scripts/refresh_recent_lessons.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary_path"] == "skill-outputs/retro/recent-lessons.md"
    assert payload["source_path"] == "skill-outputs/retro/weekly-2026-04-14.md"
    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "The repo should stop relearning sync boundaries." in summary_text
    assert "Source and installed surfaces drifted independently." in summary_text
    assert "Sync generated surfaces before broad validation." in summary_text


def test_refresh_recent_lessons_accepts_explicit_source(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "skill-outputs" / "retro"
    output_dir.mkdir(parents=True)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: skill-outputs/retro",
                "summary_path: skill-outputs/retro/recent-lessons.md",
                "evidence_paths: []",
                "metrics_commands: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    source = output_dir / "session-2026-04-15.md"
    source.write_text(
        "\n".join(
            [
                "## Context",
                "- Explicit source should win.",
                "",
                "## Waste",
                "- Missing explicit source would be ambiguous.",
                "",
                "## Next Improvements",
                "- `workflow`: Pass --source when the intended retro artifact is not the newest one.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/refresh_recent_lessons.py",
        "--repo-root",
        str(repo),
        "--source",
        "skill-outputs/retro/session-2026-04-15.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source_path"] == "skill-outputs/retro/session-2026-04-15.md"
    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "Explicit source should win." in summary_text
