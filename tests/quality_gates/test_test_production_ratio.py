from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

from .support import ROOT, init_git_repo, run_script

SPEC = importlib.util.spec_from_file_location(
    "check_test_production_ratio", ROOT / "scripts" / "check_test_production_ratio.py"
)
assert SPEC is not None and SPEC.loader is not None
RATIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RATIO)


def test_test_production_ratio_counts_source_truth_without_plugin_exports() -> None:
    summary = RATIO.summarize(ROOT)

    assert summary["scope"] == "python-source-truth"
    assert summary["engine"] == "splitlines"
    assert summary["source_lines"] > summary["test_lines"]
    assert 0 < summary["ratio"] < 1
    assert "plugins" in summary["excluded_source_dirs"]


def test_test_production_ratio_fails_above_max() -> None:
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(ROOT),
        "--max-ratio",
        "0.01",
    )

    assert result.returncode == 1
    assert "exceeds max" in result.stdout


def test_summarize_rejects_unknown_engine() -> None:
    with pytest.raises(ValueError):
        RATIO.summarize(ROOT, engine="cloc")


def test_summarize_tokei_engine_raises_when_binary_missing(tmp_path: Path, monkeypatch) -> None:
    # Force the missing-binary path deterministically by pointing PATH at an empty
    # dir. tokei is installed locally AND in CI, so the old `skip` guard meant this
    # degraded-path assertion never ran in any standard environment (#368
    # test-quality fix). The tokei engine checks `shutil.which` before any file/git
    # work, so an empty PATH is safe.
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(RATIO.TokeiUnavailableError):
        RATIO.summarize(ROOT, engine="tokei")


def test_cli_tokei_engine_returns_two_when_binary_missing(tmp_path: Path) -> None:
    # Same #368 fix for the CLI surface: force the degraded path via an empty PATH
    # instead of skipping when tokei is present.
    nobin = tmp_path / "nobin"
    nobin.mkdir()
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(ROOT),
        "--engine",
        "tokei",
        env={**os.environ, "PATH": str(nobin)},
    )

    assert result.returncode == 2
    assert "tokei" in result.stdout


def test_splitlines_ratio_ignores_gitignored_python_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / ".gitignore").write_text("scripts/generated.py\n", encoding="utf-8")
    (repo / "scripts" / "kept.py").write_text("print('kept')\n", encoding="utf-8")
    (repo / "scripts" / "generated.py").write_text("print('ignored')\n" * 100, encoding="utf-8")
    (repo / "tests" / "test_kept.py").write_text("def test_kept():\n    assert True\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "scripts/kept.py", "tests/test_kept.py")

    summary = RATIO.summarize(repo)

    assert summary["source_file_count"] == 1
    assert summary["source_lines"] == 1
