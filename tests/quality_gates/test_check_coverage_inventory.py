from __future__ import annotations

import importlib.util
import json

from .support import ROOT

SPEC = importlib.util.spec_from_file_location(
    "check_coverage_module", ROOT / "scripts" / "check_coverage.py"
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


def test_check_coverage_json_includes_per_file_floor(monkeypatch, capsys) -> None:
    def fake_collect_counts(repo_root):
        return {
            (repo_root / rel_path).resolve(): CHECK_COVERAGE.executable_lines(repo_root / rel_path)
            for rel_path in CHECK_COVERAGE.TARGET_FILES
        }

    monkeypatch.setattr(CHECK_COVERAGE, "collect_counts", fake_collect_counts)
    monkeypatch.setattr(
        CHECK_COVERAGE.sys,
        "argv",
        ["check_coverage.py", "--repo-root", str(ROOT), "--json"],
    )

    assert CHECK_COVERAGE.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["per_file_floor"]["relationship"] == "per-file-floor"
    assert payload["per_file_floor"]["floor"] == 0.85
