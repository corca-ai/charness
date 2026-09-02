from __future__ import annotations

from pathlib import Path

from tools import check_last_verified


def test_missing_last_verified_header_is_a_seeded_failure(tmp_path: Path, capsys) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")

    assert check_last_verified.check(tmp_path) == 1
    assert "docs/guide.md" in capsys.readouterr().err


def test_exact_last_verified_header_passes(tmp_path: Path, capsys) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("> Last verified: 2026-09-02\n# Guide\n", encoding="utf-8")

    assert check_last_verified.check(tmp_path) == 0
    assert capsys.readouterr().err == ""
