from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import check_skill_cut_safety as csafety

SKILL_REL = "skills/public/demo/SKILL.md"
CORE_PIN = "Always prefer the primary source over a cached summary."
SEDIMENT = "This sentence is pure sediment with no behavioral effect at all."
MOVABLE = "Detail that has outgrown the body and belongs in a reference home."


def _run(repo: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=repo, check=True, capture_output=True, text=True)


def _commit(repo: Path, message: str) -> None:
    _run(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", message)


def _seed_repo(repo: Path) -> Path:
    repo.mkdir()
    _run(repo, "git", "init")
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\n"
        f"{CORE_PIN}\n"
        f"{SEDIMENT}\n"
        f"{MOVABLE}\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "detail.md").write_text("# Detail\n\nUnrelated note.\n", encoding="utf-8")
    (repo / "tests").mkdir()
    _run(repo, "git", "add", "-A")
    _commit(repo, "base")
    return skill_dir


def _patch_pins(monkeypatch, core=(), package=()) -> None:
    monkeypatch.setattr(csafety._contracts, "CORE_CONTRACTS", {SKILL_REL: tuple(core)})
    monkeypatch.setattr(csafety._contracts, "PACKAGE_CONTRACTS", {SKILL_REL: tuple(package)})


def test_core_contract_break_blocks(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(CORE_PIN, "Primary source is usually nicer."), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "blocked"
    [skill] = report["skills"]
    kinds = {b["kind"] for b in skill["blocks"]}
    assert "core-contract" in kinds


def test_reference_home_gap_is_review_not_block(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])  # pin survives; only sediment removed
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"  # no contract/test pin broke -> exit 0
    [skill] = report["skills"]
    assert not skill["blocks"]
    assert any(SEDIMENT[:30] in r["phrase"] for r in skill["reviews"])


def test_sprawl_split_to_reference_is_lossless_clean(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    # Move the movable line OUT of the body and INTO a reference home (the sprawl cure).
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(MOVABLE + "\n", ""), encoding="utf-8")
    detail = skill_dir / "references" / "detail.md"
    detail.write_text(detail.read_text() + f"\n{MOVABLE}\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    [skill] = report["skills"]
    assert not skill["blocks"]
    # The moved line survives in the reference, so it is NOT a reference-home gap.
    assert not any(MOVABLE[:30] in r["phrase"] for r in skill["reviews"])


def test_package_pin_may_move_to_reference(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN], package=[MOVABLE])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(MOVABLE + "\n", ""), encoding="utf-8")
    detail = skill_dir / "references" / "detail.md"
    detail.write_text(detail.read_text() + f"\n{MOVABLE}\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    [skill] = report["skills"]
    # A package pin that moved to a reference still survives the package -> no break.
    assert not any(b["kind"] == "package-contract" for b in skill["blocks"])


def test_test_literal_pin_blocks(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch)  # no contract pins; isolate the test-literal signal
    (repo / "tests" / "test_demo.py").write_text(
        f'def test_demo_pins(text):\n    assert "{SEDIMENT}" in text\n', encoding="utf-8"
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "blocked"
    [skill] = report["skills"]
    assert any(b["kind"] == "test-pin" for b in skill["blocks"])


def test_clean_when_nothing_removed(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text() + "\nA purely additive trailing line of guidance.\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "clean"


def test_cli_strict_fails_on_review(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_cut_safety.py", "--repo-root", str(repo), "--tests-root", "tests", "--strict"],
    )
    assert csafety.main() == 1
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_cut_safety.py", "--repo-root", str(repo), "--tests-root", "tests"],
    )
    assert csafety.main() == 0  # review-only is exit 0 without --strict
