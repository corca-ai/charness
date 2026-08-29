from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module
from tests.quality_gates.seeding_support import write_retro_adapter

ROOT = Path(__file__).resolve().parents[2]
_refresh_recent_lessons = import_repo_module(
    ROOT / "skills" / "public" / "retro" / "scripts" / "refresh_recent_lessons.py",
    "skills.public.retro.scripts.refresh_recent_lessons",
)


def run_refresh(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["refresh_recent_lessons.py", *args])
    returncode = _refresh_recent_lessons.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_refresh_recent_lessons_from_latest_retro_artifact(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    write_retro_adapter(repo)
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

    result = run_refresh(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert payload["source_path"] == "charness-artifacts/retro/weekly-2026-04-14.md"
    assert payload["lesson_selection_index_path"] == "charness-artifacts/retro/lesson-selection-index.json"
    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "The repo should stop relearning sync boundaries." in summary_text
    assert "Source and installed surfaces drifted independently." in summary_text
    assert "Sync generated surfaces before broad validation." in summary_text
    assert "## Selection Policy" in summary_text
    assert "lesson-selection-index.json" in summary_text
    assert "source: `charness-artifacts/retro/weekly-2026-04-14.md`" in summary_text
    assert (output_dir / "lesson-selection-index.json").is_file()


def test_refresh_recent_lessons_accepts_explicit_source(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    write_retro_adapter(repo)
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

    result = run_refresh(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--source",
        "charness-artifacts/retro/session-2026-04-15.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["source_path"] == "charness-artifacts/retro/session-2026-04-15.md"
    assert payload["lesson_selection_index_path"] == "charness-artifacts/retro/lesson-selection-index.json"
    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "Explicit source should win." in summary_text
    assert "## Selection Policy" in summary_text


def test_refresh_refuses_when_the_projection_is_disabled(tmp_path: Path, monkeypatch, capsys) -> None:
    """`summary_path: null` is an opt-out, and this command exists to WRITE the digest.

    Reporting a no-op success would name a path the repository asked not to have,
    and the pre-repair behaviour was worse still: `repo_root / None` raised
    TypeError, so the consumer's declared opt-out surfaced as a crash.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: null\n", encoding="utf-8"
    )

    result = run_refresh(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 2
    assert "summary_path: null" in result.stderr
    assert "disabled" in result.stderr
    # Refusal, not a silent write: nothing was created at the default location.
    assert not (repo / "charness-artifacts" / "retro" / "recent-lessons.md").exists()
