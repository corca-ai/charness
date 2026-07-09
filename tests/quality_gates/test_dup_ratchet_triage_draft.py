from __future__ import annotations

from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
triage = load_script_module(
    "draft_dup_ratchet_triage_under_test",
    ROOT / "skills/public/quality/scripts/draft_dup_ratchet_triage.py",
)


def test_build_report_suggests_extract_for_same_file_family() -> None:
    ratchet = {"status": "hard-block", "new_code_families": ["fam1"]}
    inventory = {
        "families": [
            {
                "family_fingerprint": "fam1",
                "shared_lines": 8,
                "members": 2,
                "sample_locations": [
                    {"file": "scripts/x.py", "start_line": 1, "end_line": 8},
                    {"file": "scripts/x.py", "start_line": 20, "end_line": 27},
                ],
            }
        ]
    }

    report = triage.build_report(ratchet, inventory)

    assert report["ok"] is True
    assert report["families"][0]["suggested_action"] == "extract"
    assert report["families"][0]["draft_dup_review_entry"]["class"] == "unreviewed"


def test_build_report_suggests_intentional_for_tiny_idiom() -> None:
    ratchet = {"status": "hard-block", "new_code_families": ["fam2"]}
    inventory = {
        "families": [
            {
                "family_fingerprint": "fam2",
                "shared_lines": 4,
                "members": 2,
                "sample_locations": [
                    {"file": "scripts/a.py", "start_line": 1, "end_line": 4},
                    {"file": "skills/public/x/scripts/b.py", "start_line": 9, "end_line": 12},
                ],
            }
        ]
    }

    report = triage.build_report(ratchet, inventory)

    assert report["families"][0]["suggested_action"] == "intentional"
    assert report["families"][0]["draft_dup_review_entry"]["class"] == "intentional"


def test_build_report_reports_inventory_misses() -> None:
    report = triage.build_report({"new_code_families": ["missing"]}, {"families": []})

    assert report["ok"] is False
    assert report["missing_from_inventory"] == ["missing"]
