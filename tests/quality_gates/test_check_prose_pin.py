from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import check_prose_pin as prose_pin

PINNED_PHRASE = "the closeout ledger never reports a number not present in the verified set"


def _run(repo: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=repo, check=True, capture_output=True, text=True)


def _commit(repo: Path, message: str) -> None:
    _run(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", message)


def _seed_repo(repo: Path) -> None:
    repo.mkdir()
    _run(repo, "git", "init")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text(
        f"# Guide\n\nRule: {PINNED_PHRASE}.\n",
        encoding="utf-8",
    )
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: demo\n---\n\n# Demo\n", encoding="utf-8")
    tests_dir = repo / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_prose.py").write_text(
        f'def test_guide_pins_rule(text):\n    assert "{PINNED_PHRASE}" in text\n',
        encoding="utf-8",
    )
    (tests_dir / "test_path.py").write_text(
        'PATH = "skills/public/demo/SKILL.md"\n',
        encoding="utf-8",
    )
    _run(repo, "git", "add", "-A")
    _commit(repo, "base")


def test_prose_pin_flags_edited_doc_prose(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    # Reword the pinned rule out of the doc -> the literal-string test will break.
    (repo / "docs" / "guide.md").write_text(
        "# Guide\n\nRule: the ledger only reports verified entries.\n",
        encoding="utf-8",
    )

    report = prose_pin.build_report(repo.resolve(), paths=None, test_roots=[repo / "tests"])
    assert report["status"] == "findings"
    prose = [f for f in report["findings"] if f["kind"] == "prose"]
    assert len(prose) == 1
    assert prose[0]["doc"] == "docs/guide.md"
    assert prose[0]["test"] == "tests/test_prose.py"
    assert PINNED_PHRASE in prose[0]["phrase"]


def test_prose_pin_flags_renamed_skill_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "skills" / "public" / "demo2").mkdir(parents=True)
    _run(
        repo,
        "git",
        "mv",
        "skills/public/demo/SKILL.md",
        "skills/public/demo2/SKILL.md",
    )

    report = prose_pin.build_report(repo.resolve(), paths=None, test_roots=[repo / "tests"])
    path_pins = [f for f in report["findings"] if f["kind"] == "path"]
    assert len(path_pins) == 1
    assert path_pins[0]["doc"] == "skills/public/demo/SKILL.md"
    assert path_pins[0]["test"] == "tests/test_path.py"


def test_prose_pin_clean_when_pinned_prose_untouched(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    # Edit the doc without touching the pinned rule line.
    guide = repo / "docs" / "guide.md"
    guide.write_text(guide.read_text(encoding="utf-8") + "\nAn unrelated trailing note.\n", encoding="utf-8")

    report = prose_pin.build_report(repo.resolve(), paths=None, test_roots=[repo / "tests"])
    assert report["status"] == "clean"
    assert report["findings"] == []


def test_prose_pin_cli_strict_exits_nonzero(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "docs" / "guide.md").write_text("# Guide\n\nRule: reworded entirely.\n", encoding="utf-8")

    # In-process (not a subprocess CLI spawn) so this stays off the boundary-bypass
    # ratchet; the real git repo the checker reads is the only boundary it needs.
    monkeypatch.setattr(
        "sys.argv",
        ["check_prose_pin.py", "--repo-root", str(repo), "--tests-root", "tests", "--strict"],
    )
    assert prose_pin.main() == 1
    assert "prose-pin found" in capsys.readouterr().out

    monkeypatch.setattr(
        "sys.argv",
        ["check_prose_pin.py", "--repo-root", str(repo), "--tests-root", "tests"],
    )
    assert prose_pin.main() == 0
