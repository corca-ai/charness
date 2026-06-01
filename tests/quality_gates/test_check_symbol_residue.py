from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

from .support import run_script

csr = importlib.import_module("scripts.check_symbol_residue")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    return repo


def test_symbol_residue_warns_on_deleted_symbol_phrase(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "scripts").mkdir()
    (repo / "docs").mkdir()
    (repo / "scripts" / "goal.py").write_text(
        "def is_non_trivial_goal(text):\n    return bool(text)\n", encoding="utf-8"
    )
    (repo / "docs" / "contract.md").write_text(
        "The Non-Trivial Goal exemption still exists.\n", encoding="utf-8"
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "seed")

    (repo / "scripts" / "goal.py").write_text("", encoding="utf-8")

    findings = csr.find_residue(repo)
    assert [(f.symbol, f.variant, f.path) for f in findings] == [
        ("is_non_trivial_goal", "Non-Trivial Goal", "docs/contract.md")
    ]


def test_symbol_residue_cli_is_advisory_exit_zero(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "scripts").mkdir()
    (repo / "skills").mkdir()
    (repo / "scripts" / "rules.py").write_text(
        "TRIVIAL_GOAL_MARKER = 'x'\n", encoding="utf-8"
    )
    (repo / "skills" / "note.md").write_text(
        "The trivial-goal-marker path remains documented.\n", encoding="utf-8"
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "seed")

    (repo / "scripts" / "rules.py").write_text("", encoding="utf-8")

    result = run_script("scripts/check_symbol_residue.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["finding_count"] == 1
    assert payload["findings"][0]["symbol"] == "TRIVIAL_GOAL_MARKER"


def test_symbol_residue_accepts_explicit_concept(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "docs").mkdir()
    (repo / "docs" / "contract.md").write_text(
        "The Trivial Goal Exemption section is stale.\n", encoding="utf-8"
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "seed")

    findings = csr.find_residue(repo, concepts=["trivial goal exemption"])
    assert [(f.symbol, f.variant, f.path) for f in findings] == [
        ("trivial goal exemption", "Trivial Goal Exemption", "docs/contract.md")
    ]
