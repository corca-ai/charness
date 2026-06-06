from __future__ import annotations

import json
from pathlib import Path

from scripts import rca_link_advisory as nudge

DEBUG_ARTIFACT = "charness-artifacts/debug/2026-06-06-example-bug.md"


def seed_ledger(tmp_path: Path, *, ref: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "metrics").mkdir(parents=True)
    lines = []
    if ref is not None:
        lines.append(json.dumps({"ref": ref, "source": "debug", "event_kind": "bug"}))
    (repo / "charness-artifacts" / "metrics" / "rca-ledger.jsonl").write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
    )
    return repo


# --- pure helpers -------------------------------------------------------------


def test_is_dated_debug_artifact_classification() -> None:
    assert nudge.is_dated_debug_artifact(DEBUG_ARTIFACT) is True
    # latest.md is the current pointer, not a distinct new artifact.
    assert nudge.is_dated_debug_artifact("charness-artifacts/debug/latest.md") is False
    assert nudge.is_dated_debug_artifact("scripts/foo.py") is False
    assert nudge.is_dated_debug_artifact("charness-artifacts/retro/x.md") is False


def test_unlinked_when_ledger_has_matching_ref(tmp_path: Path) -> None:
    repo = seed_ledger(tmp_path, ref=DEBUG_ARTIFACT)
    assert nudge.unlinked_debug_artifacts(repo, [DEBUG_ARTIFACT]) == []


def test_unlinked_when_ledger_missing_ref(tmp_path: Path) -> None:
    repo = seed_ledger(tmp_path, ref=None)
    assert nudge.unlinked_debug_artifacts(repo, [DEBUG_ARTIFACT]) == [DEBUG_ARTIFACT]


def test_unlinked_ignores_non_debug_and_pointer(tmp_path: Path) -> None:
    repo = seed_ledger(tmp_path, ref=None)
    paths = ["scripts/foo.py", "charness-artifacts/debug/latest.md", "docs/bar.md"]
    assert nudge.unlinked_debug_artifacts(repo, paths) == []


def test_unlinked_when_ledger_file_absent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert nudge.unlinked_debug_artifacts(repo, [DEBUG_ARTIFACT]) == [DEBUG_ARTIFACT]


# --- advisory_lines + main (the surfaced advisory) ----------------------------


def test_advisory_lines_silent_when_linked(tmp_path: Path) -> None:
    repo = seed_ledger(tmp_path, ref=DEBUG_ARTIFACT)
    assert nudge.advisory_lines(repo, [DEBUG_ARTIFACT]) == []


def test_advisory_lines_warn_when_unlinked(tmp_path: Path) -> None:
    repo = seed_ledger(tmp_path, ref=None)
    lines = nudge.advisory_lines(repo, [DEBUG_ARTIFACT])
    assert lines
    assert "ADVISORY" in lines[0]
    assert "rca-ledger.jsonl" in lines[0]
    assert any(DEBUG_ARTIFACT in line for line in lines)


def test_main_exit_zero_and_silent_when_linked(tmp_path: Path, capsys) -> None:
    repo = seed_ledger(tmp_path, ref=DEBUG_ARTIFACT)
    rc = nudge.main(["--repo-root", str(repo), "--paths", DEBUG_ARTIFACT])
    assert rc == 0
    assert capsys.readouterr().out.strip() == ""


def test_main_exit_zero_and_warns_when_unlinked(tmp_path: Path, capsys) -> None:
    # Advisory only: warns but still exits 0 (never blocks the commit).
    repo = seed_ledger(tmp_path, ref=None)
    rc = nudge.main(["--repo-root", str(repo), "--paths", DEBUG_ARTIFACT])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ADVISORY" in out
    assert DEBUG_ARTIFACT in out
