from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import skill_cut_safety_advisory as nudge


def _run(repo: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=repo, check=True, capture_output=True, text=True)


def _commit(repo: Path, message: str) -> None:
    _run(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", message)


def _seed_skill(repo: Path) -> Path:
    repo.mkdir()
    _run(repo, "git", "init")
    skill_md = repo / "skills" / "public" / "demo" / "SKILL.md"
    skill_md.parent.mkdir(parents=True)
    skill_md.write_text("---\nname: demo\n---\n\n# Demo\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _commit(repo, "seed")
    return skill_md


def test_provider_empty_without_staged_deletion(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(repo)
    assert nudge.provider(repo, []) == []


def test_provider_forces_review_on_staged_skill_md_deletion(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_md = _seed_skill(repo)
    _run(repo, "git", "rm", "-q", str(skill_md.relative_to(repo)))

    lines = nudge.provider(repo, [])

    assert lines
    assert lines[0].startswith("REVIEW:")
    assert "advisory only, never blocks" in lines[0]
    assert any("skills/public/demo/SKILL.md" in line for line in lines[1:])


def test_provider_ignores_unstaged_working_tree_deletion(tmp_path: Path) -> None:
    # `staged=True` (--cached): an unstaged deletion is not yet part of what will
    # be committed, so it must not force a question before it is even staged.
    repo = tmp_path / "repo"
    skill_md = _seed_skill(repo)
    skill_md.unlink()

    assert nudge.provider(repo, []) == []


def test_provider_ignores_unrelated_staged_deletion(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(repo)
    notes = repo / "notes.md"
    notes.write_text("unrelated\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _commit(repo, "add notes")
    _run(repo, "git", "rm", "-q", "notes.md")

    assert nudge.provider(repo, []) == []


def test_provider_ignores_selected_paths_argument(tmp_path: Path) -> None:
    # The provider re-derives staged deletions directly from git, independent of
    # whatever selected-paths set the gate plan computed (mirrors rca_link_advisory).
    repo = tmp_path / "repo"
    _seed_skill(repo)
    assert nudge.provider(repo, ["some/unrelated/path.py"]) == []


def test_main_exit_zero_and_forces_question_on_staged_deletion(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    skill_md = _seed_skill(repo)
    _run(repo, "git", "rm", "-q", str(skill_md.relative_to(repo)))

    rc = nudge.main(["--repo-root", str(repo)])
    out = capsys.readouterr().out

    assert rc == 0  # north-star P5: forces a question, never blocks
    assert "REVIEW" in out
    assert "skills/public/demo/SKILL.md" in out


def test_main_exit_zero_and_silent_without_deletion(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    _seed_skill(repo)

    rc = nudge.main(["--repo-root", str(repo)])

    assert rc == 0
    assert capsys.readouterr().out.strip() == ""
