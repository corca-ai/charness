from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script


def test_test_repo_copy_ignore_lives_in_canonical_module() -> None:
    result = run_script("scripts/check_test_repo_copy_invariants.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_flags_inline_ignore(tmp_path: Path) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text(
        "import shutil\nREPO_COPY_IGNORE = shutil.ignore_patterns('.git')\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_drift.py").write_text(
        "import shutil\nROOT = '/repo'\n"
        "DRIFT_IGNORE = shutil.ignore_patterns('.git', 'node_modules')\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check_test_repo_copy_invariants.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "shutil.ignore_patterns" in result.stderr


def test_check_test_repo_copy_invariants_flags_inline_copytree_root(tmp_path: Path) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_drift.py").write_text(
        "import shutil\nfrom pathlib import Path\nROOT = Path('/repo')\n"
        "def make(tmp): shutil.copytree(ROOT, tmp / 'repo')\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check_test_repo_copy_invariants.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "clone_seeded_charness_repo" in result.stderr or "shutil.copytree" in result.stderr
