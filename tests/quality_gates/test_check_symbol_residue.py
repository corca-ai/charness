from __future__ import annotations

import importlib
from pathlib import Path

import yaml

from .repo_shapes import replace_with_committed_repo
from .support import run_script

csr = importlib.import_module("scripts.check_symbol_residue")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
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
    replace_with_committed_repo(repo)

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
    replace_with_committed_repo(repo)

    (repo / "scripts" / "rules.py").write_text("", encoding="utf-8")

    result = run_script("scripts/check_symbol_residue.py", "--repo-root", str(repo))
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["finding_count"] == 1
    assert payload["findings"][0]["symbol"] == "TRIVIAL_GOAL_MARKER"
    # Exit 0 with findings only reads correctly if the payload says these are POSSIBLE
    # stale references; a bare finding list reads as a defect verdict this scan never makes.
    assert "advisory" in payload["advisory"]
    assert "possible stale reference(s)" in payload["advisory"]


def test_symbol_residue_accepts_explicit_concept(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "docs").mkdir()
    (repo / "docs" / "contract.md").write_text(
        "The Trivial Goal Exemption section is stale.\n", encoding="utf-8"
    )
    replace_with_committed_repo(repo)

    findings = csr.find_residue(repo, concepts=["trivial goal exemption"])
    assert [(f.symbol, f.variant, f.path) for f in findings] == [
        ("trivial goal exemption", "Trivial Goal Exemption", "docs/contract.md")
    ]
