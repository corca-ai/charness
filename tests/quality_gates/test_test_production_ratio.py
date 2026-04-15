from __future__ import annotations

import importlib.util

from .support import ROOT, run_script

SPEC = importlib.util.spec_from_file_location(
    "check_test_production_ratio", ROOT / "scripts" / "check-test-production-ratio.py"
)
assert SPEC is not None and SPEC.loader is not None
RATIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RATIO)


def test_test_production_ratio_counts_source_truth_without_plugin_exports() -> None:
    summary = RATIO.summarize(ROOT)

    assert summary["scope"] == "python-source-truth"
    assert summary["source_lines"] > summary["test_lines"]
    assert 0 < summary["ratio"] < 1
    assert "plugins" in summary["excluded_source_dirs"]


def test_test_production_ratio_fails_above_max() -> None:
    result = run_script(
        "scripts/check-test-production-ratio.py",
        "--repo-root",
        str(ROOT),
        "--max-ratio",
        "0.01",
    )

    assert result.returncode == 1
    assert "exceeds max" in result.stdout
