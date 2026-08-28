from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
import yaml

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
    # The live hard bound (test LOC < source LOC) was removed deliberately: the
    # gate posture is advisory (run-quality.sh runs this script with --advisory;
    # its help text owns the rationale); a hard live pin pressured against
    # writing tests.
    assert summary["source_lines"] > 0
    assert summary["test_lines"] > 0
    assert summary["ratio"] > 0
    assert "plugins" in summary["excluded_source_dirs"]
    assert summary["skipped"]["status"] == "skipped"
    assert summary["skipped"]["count"] == 2
    assert summary["skipped"]["paths"] == [
        "native/repograph/fixtures/non_utf8.py",
        "native/repograph/fixtures/null_byte.py",
    ]


def test_test_production_ratio_typed_skips_unreadable_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "app.py").write_text("print('line')\n", encoding="utf-8")
    (repo / "scripts" / "bad.py").write_bytes(b"\xff\n")
    (repo / "scripts" / "null_byte.py").write_bytes(b'print("before")\x00\n')
    (repo / "tests" / "test_app.py").write_text(
        "def test_app():\n    assert True\n", encoding="utf-8"
    )
    init_git_repo(
        repo,
        "scripts/app.py",
        "scripts/bad.py",
        "scripts/null_byte.py",
        "tests/test_app.py",
    )

    summary = RATIO.summarize(repo)

    assert summary["source_lines"] == 1
    assert summary["skipped"] == {
        "status": "skipped",
        "reason": "unreadable-python-source",
        "count": 2,
        "paths": ["scripts/bad.py", "scripts/null_byte.py"],
    }
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(repo),
        "--max-ratio",
        "3",
    )
    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["skipped"] == summary["skipped"]


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


def test_test_production_ratio_advisory_warns_above_max_without_blocking(monkeypatch, capsys) -> None:
    # --advisory demotes the over-threshold block to a non-blocking WARN posture
    # (north-star P1: a LOC ratio is a smell sensor, not an irreversible-boundary
    # contract). The WARN: prefix is what run-quality.sh:294 surfaces non-blocking.
    # Tested in-process (main() return value + captured stdout) rather than via
    # run_script: a second exit-contract subprocess assertion would flip this test
    # file to a keep-boundary in inventory_boundary_bypass and trip its ratchet.
    monkeypatch.setattr(
        sys, "argv",
        ["check_test_production_ratio.py", "--repo-root", str(ROOT), "--max-ratio", "0.01", "--advisory"],
    )

    rc = RATIO.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "WARN:" in out
    assert "exceeds max" in out


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


def test_cli_under_threshold_returns_zero_on_synthetic_repo(tmp_path: Path, monkeypatch, capsys) -> None:
    # The under-threshold rc-0 main() branch previously had no synthetic fixture
    # (only the live repo exercised it, and the live ratio can sit over the
    # threshold); the other two main() ratio branches (blocking over-threshold
    # rc1, advisory WARN rc0) already have tests.
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "scripts" / "app.py").write_text("print('line')\n" * 20, encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text(
        "def test_app():\n    assert True\n", encoding="utf-8"
    )
    init_git_repo(repo, "scripts/app.py", "tests/test_app.py")

    monkeypatch.setattr(sys, "argv", ["check_test_production_ratio.py", "--repo-root", str(repo)])

    rc = RATIO.main()
    payload = yaml.safe_load(capsys.readouterr().out)

    assert rc == 0
    # The "Test-production ratio: ..." sentence is gone; the same verdict is the
    # payload's `ratio` + `status`. `advisory` is the key the WARN posture adds,
    # so its absence is what "no WARN" means now.
    assert payload["status"] == "within-max"
    assert payload["ratio"] == pytest.approx(0.1)
    assert "advisory" not in payload
