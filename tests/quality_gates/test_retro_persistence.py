from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[2]
_persist_retro_artifact = import_repo_module(
    ROOT / "skills" / "public" / "retro" / "scripts" / "persist_retro_artifact.py",
    "skills.public.retro.scripts.persist_retro_artifact",
)


def run_persist(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["persist_retro_artifact.py", *args])
    returncode = _persist_retro_artifact.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_persist_retro_artifact_writes_artifact_snapshot_and_recent_lessons(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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

    result = run_persist(
        monkeypatch,
        capsys,
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
    assert "## Selection Policy" in summary_text
    assert "lesson-selection-index.json" in summary_text
    assert (output_dir / "lesson-selection-index.json").is_file()


def test_persist_retro_artifact_skips_self_refresh_for_summary_target(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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

    result = run_persist(
        monkeypatch,
        capsys,
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


def _write_default_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
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


def test_persist_retro_artifact_normalizes_artifact_name_without_md_extension(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    _write_default_adapter(repo)
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Retro",
                "",
                "## Context",
                "",
                "- Slice closed without lesson loss.",
                "",
                "## Waste",
                "",
                "- Lost time rediscovering trivia.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: Keep the persistence helper safe by default.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-session-no-extension",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["artifact_path"].endswith(".md"), payload
    assert payload["artifact_path"] == "charness-artifacts/retro/2026-05-07-session-no-extension.md"
    assert payload["artifact_name_normalized"] is True
    assert payload["summary_refreshed"] is True
    assert (output_dir / "2026-05-07-session-no-extension.md").is_file()
    assert "lacks .md" in result.stderr


def test_persist_retro_artifact_preserves_legacy_summary_when_no_candidates(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    _write_default_adapter(repo)
    legacy_summary = output_dir / "recent-lessons.md"
    legacy_text = (
        "# Recent Retro Lessons\n\n"
        "## Repeat Traps\n\n"
        "- Hand-curated trap line that predates the retro skill.\n"
    )
    legacy_summary.write_text(legacy_text, encoding="utf-8")

    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Retro\n\nA narrative-only retro with no Context/Waste/Next Improvements headers.\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-narrative-only.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary_refreshed"] is False
    assert payload["summary_skipped_reason"] == "no_candidates_existing_summary_protected"
    preserved = legacy_summary.read_text(encoding="utf-8")
    assert preserved == legacy_text
    assert "Hand-curated trap line that predates the retro skill." in preserved
    assert "refusing to overwrite" in result.stderr


def test_persist_retro_artifact_emits_t_events_lesson_cited_when_adapter_present(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    _write_default_adapter(repo)
    (repo / ".agents" / "t-events-adapter.yaml").write_text(
        "version: 1\nenabled: true\nstorage_path: .charness/t-events\n",
        encoding="utf-8",
    )
    cited_one = output_dir / "2026-05-08-prior-a.md"
    cited_two = output_dir / "2026-05-08-prior-b.md"
    cited_one.write_text("# prior a\n", encoding="utf-8")
    cited_two.write_text("# prior b\n", encoding="utf-8")

    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Retro",
                "",
                "## Context",
                "",
                "- One trap surfaced (source: charness-artifacts/retro/2026-05-08-prior-a.md)",
                "- Another trap surfaced (source: charness-artifacts/retro/2026-05-08-prior-b.md)",
                "",
                "## Waste",
                "",
                "- Time lost without dedicated trace.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: surface the cite chain in inventory.",
                "",
                "## Sources",
                "",
                "- charness-artifacts/retro/2026-05-08-prior-a.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-09-emit-smoke.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["t_events"]["emitted_count"] == 2
    assert payload["t_events"]["cite_count"] == 2

    jsonl = repo / ".charness/t-events/lesson_cited.jsonl"
    rows = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2
    assert {row["lesson_path"] for row in rows} == {
        "charness-artifacts/retro/2026-05-08-prior-a.md",
        "charness-artifacts/retro/2026-05-08-prior-b.md",
    }
    assert all(
        row["citing_artifact_path"] == "charness-artifacts/retro/2026-05-09-emit-smoke.md"
        for row in rows
    )
    assert all(row["citing_skill"] == "retro" for row in rows)


def test_persist_retro_artifact_t_events_emit_silent_without_adapter(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    _write_default_adapter(repo)
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Retro",
                "",
                "## Context",
                "",
                "- A trap (source: charness-artifacts/retro/2026-05-08-prior.md)",
                "",
                "## Waste",
                "",
                "- Lost time.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: keep the emit hook silent without adapter.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-09-no-adapter.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["t_events"]["emitted_count"] == 0
    assert payload["t_events"]["cite_count"] == 1
    assert payload["t_events"]["reasons"] == {"no_adapter": 1}
    assert not (repo / ".charness/t-events").exists()


def test_persist_retro_artifact_force_empty_summary_opts_in(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    _write_default_adapter(repo)
    legacy_summary = output_dir / "recent-lessons.md"
    legacy_text = (
        "# Recent Retro Lessons\n\n"
        "## Repeat Traps\n\n"
        "- Hand-curated trap line that the operator has chosen to drop.\n"
    )
    legacy_summary.write_text(legacy_text, encoding="utf-8")

    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Retro\n\nA narrative-only retro with no Context/Waste/Next Improvements headers.\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-narrative-only.md",
        "--markdown-file",
        str(markdown_file),
        "--force-empty-summary",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary_refreshed"] is True
    refreshed = legacy_summary.read_text(encoding="utf-8")
    assert "Hand-curated trap line that the operator has chosen to drop." not in refreshed
    assert "No current focus bullets found in retro lesson index." in refreshed
