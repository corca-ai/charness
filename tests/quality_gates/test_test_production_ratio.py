from __future__ import annotations

import importlib.util
import shutil

import pytest

from .support import ROOT, run_script

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


def test_summarize_tokei_engine_raises_when_binary_missing() -> None:
    if shutil.which("tokei") is not None:
        pytest.skip("tokei is installed; degraded path is not exercised in this env")
    with pytest.raises(RATIO.TokeiUnavailableError):
        RATIO.summarize(ROOT, engine="tokei")


def test_cli_tokei_engine_returns_two_when_binary_missing() -> None:
    if shutil.which("tokei") is not None:
        pytest.skip("tokei is installed; degraded CLI path is not exercised in this env")
    result = run_script(
        "scripts/check_test_production_ratio.py",
        "--repo-root",
        str(ROOT),
        "--engine",
        "tokei",
    )

    assert result.returncode == 2
    assert "tokei" in result.stdout
