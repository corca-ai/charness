from __future__ import annotations

import importlib.util

from .support import ROOT, run_script

SPEC = importlib.util.spec_from_file_location(
    "check_coverage_module", ROOT / "scripts" / "check-coverage.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK_COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_COVERAGE)


def test_per_file_floor_report_classifies_floor_violations() -> None:
    report = CHECK_COVERAGE.build_per_file_floor_report(
        [
            {
                "path": "scripts/weak.py",
                "covered": 20,
                "total": 100,
                "coverage": 0.2,
            },
            {
                "path": "scripts/warn.py",
                "covered": 90,
                "total": 100,
                "coverage": 0.9,
            },
            {
                "path": "scripts/small.py",
                "covered": 1,
                "total": 2,
                "coverage": 0.5,
            },
            {
                "path": "scripts/healthy.py",
                "covered": 98,
                "total": 100,
                "coverage": 0.98,
            },
        ]
    )

    assert report["status"] == "enforced"
    assert report["relationship"] == "per-file-floor"
    assert report["floor"] == 0.85
    assert [item["path"] for item in report["violations"]] == ["scripts/weak.py"]
    assert [item["path"] for item in report["warn_band"]] == ["scripts/warn.py"]


def test_check_coverage_json_includes_per_file_floor() -> None:
    result = run_script("scripts/check-coverage.py", "--repo-root", str(ROOT), "--json")

    assert result.returncode == 0, result.stderr
    assert '"per_file_floor"' in result.stdout
    assert '"relationship": "per-file-floor"' in result.stdout
    assert '"floor": 0.85' in result.stdout
