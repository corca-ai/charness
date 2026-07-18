from __future__ import annotations

import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module
from scripts import check_coverage
from tests import repo_copy

from .support import ROOT, run_script

_repo_copy_invariants = import_repo_module(
    ROOT / "scripts/check_test_repo_copy_invariants.py",
    "scripts.check_test_repo_copy_invariants",
)


def run_repo_copy_invariants(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_test_repo_copy_invariants.py", *args])
    returncode = _repo_copy_invariants.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)

REQUIRED_VOLATILE_COPY_EXCLUDES = {
    ".cautilus",
    ".charness",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".venv",
    "charness-artifacts",
    "node_modules",
    "reports",
}


def test_test_repo_copy_ignore_lives_in_canonical_module() -> None:
    result = run_script("scripts/check_test_repo_copy_invariants.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_repo_copy_excludes_volatile_artifact_roots() -> None:
    assert REQUIRED_VOLATILE_COPY_EXCLUDES <= set(repo_copy.REPO_COPY_EXCLUDE_NAMES)


def test_coverage_copy_excludes_volatile_artifact_roots() -> None:
    assert REQUIRED_VOLATILE_COPY_EXCLUDES <= set(check_coverage.COPY_IGNORE_NAMES)


def test_repo_copy_ignore_drops_cautilus_runtime_payload(tmp_path: Path) -> None:
    source = tmp_path / "source"
    payload = source / ".cautilus" / "runs" / "demo-run" / "codex-home" / "tmp" / "wrapper"
    payload.mkdir(parents=True)
    (payload / "payload.txt").write_text("large runtime payload\n", encoding="utf-8")
    (source / "README.md").write_text("# source\n", encoding="utf-8")

    target = tmp_path / "target"
    shutil.copytree(source, target, ignore=repo_copy.REPO_COPY_IGNORE)

    assert (target / "README.md").is_file()
    assert not (target / ".cautilus").exists()


def test_repo_copy_ignore_drops_generated_reports(tmp_path: Path) -> None:
    source = tmp_path / "source"
    payload = source / "reports" / "mutation" / "large-run.log"
    payload.parent.mkdir(parents=True)
    payload.write_text("large generated report\n", encoding="utf-8")
    (source / "README.md").write_text("# source\n", encoding="utf-8")

    target = tmp_path / "target"
    shutil.copytree(source, target, ignore=repo_copy.REPO_COPY_IGNORE)

    assert (target / "README.md").is_file()
    assert not (target / "reports").exists()


def test_coverage_copy_ignore_drops_cautilus_runtime_payload(tmp_path: Path) -> None:
    source = tmp_path / "coverage-source"
    payload = source / ".cautilus" / "runs" / "demo-run" / "codex-home" / "tmp" / "wrapper"
    payload.mkdir(parents=True)
    (payload / "payload.txt").write_text("large runtime payload\n", encoding="utf-8")
    (source / "scripts").mkdir()
    (source / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")

    target = tmp_path / "coverage-target"
    shutil.copytree(source, target, ignore=check_coverage.COPY_IGNORE)

    assert (target / "scripts" / "demo.py").is_file()
    assert not (target / ".cautilus").exists()


def test_coverage_copy_ignore_drops_generated_reports(tmp_path: Path) -> None:
    source = tmp_path / "coverage-source"
    payload = source / "reports" / "mutation" / "large-run.log"
    payload.parent.mkdir(parents=True)
    payload.write_text("large generated report\n", encoding="utf-8")
    (source / "scripts").mkdir()
    (source / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")

    target = tmp_path / "coverage-target"
    shutil.copytree(source, target, ignore=check_coverage.COPY_IGNORE)

    assert (target / "scripts" / "demo.py").is_file()
    assert not (target / "reports").exists()


def test_check_test_repo_copy_invariants_flags_inline_ignore(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "shutil.ignore_patterns" in result.stderr


def test_check_test_repo_copy_invariants_flags_inline_copytree_root(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_drift.py").write_text(
        "import shutil\nfrom pathlib import Path\nROOT = Path('/repo')\n"
        "def make(tmp): shutil.copytree(ROOT, tmp / 'repo')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "clone_seeded_charness_repo" in result.stderr or "shutil.copytree" in result.stderr


def test_check_test_repo_copy_invariants_flags_unmarked_copy_heavy_test(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "def test_copy(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_copy_heavy.py::test_copy" in result.stderr
    assert "pytest.mark.release_only" in result.stderr


def test_check_test_repo_copy_invariants_accepts_release_only_copy_heavy_test(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.release_only\n"
        "def test_copy(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_flags_real_repo_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_shared_write.py").write_text(
        "from pathlib import Path\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        "def test_write():\n"
        "    target = ROOT / 'charness-artifacts' / 'temporary.md'\n"
        "    target.write_text('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_shared_write.py:5" in result.stderr
    assert "mutates a path derived from the real repository root" in result.stderr
    assert "tmp_path or an isolated repo" in result.stderr


def test_check_test_repo_copy_invariants_flags_import_time_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_import_write.py").write_text(
        "from .support import ROOT\n"
        "(ROOT / 'temporary.txt').touch()\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "module import mutates" in result.stderr


def test_check_test_repo_copy_invariants_flags_aliased_root_path_open(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_alias_write.py").write_text(
        "from pathlib import Path\n"
        "from .support import ROOT as checkout\n"
        "def test_write():\n"
        "    target = Path(checkout).joinpath('temporary.txt')\n"
        "    with target.open(mode='w') as stream:\n"
        "        stream.write('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "Path.open(mode='w')" in result.stderr


def test_check_test_repo_copy_invariants_flags_annotated_root_builtin_open(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_builtin_open.py").write_text(
        "from pathlib import Path\n"
        "from .support import ROOT\n"
        "def test_write():\n"
        "    target: Path = ROOT / 'temporary.txt'\n"
        "    with open(target, 'w') as stream:\n"
        "        stream.write('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "open(mode='w')" in result.stderr


def test_check_test_repo_copy_invariants_flags_class_style_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_class_write.py").write_text(
        "from .support import ROOT\n"
        "class TestSharedState:\n"
        "    def test_write(self):\n"
        "        (ROOT / 'temporary.txt').write_text('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "`test_write` mutates" in result.stderr


def test_check_test_repo_copy_invariants_accepts_non_checkout_root_name(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_local_root.py").write_text(
        "from pathlib import Path\n"
        "ROOT = Path('/tmp/test-output')\n"
        "def test_write():\n"
        "    (ROOT / 'result.txt').write_text('isolated')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_accepts_tmp_write_and_root_read(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_isolated.py").write_text(
        "from .support import ROOT\n"
        "def test_isolated(tmp_path):\n"
        "    source = (ROOT / 'AGENTS.md').read_text()\n"
        "    (tmp_path / 'AGENTS.md').write_text(source)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_skips_ast_for_irrelevant_files(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_irrelevant.py").write_text(
        "def not_valid_python(:\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
