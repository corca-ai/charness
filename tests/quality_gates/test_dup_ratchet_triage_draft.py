from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
triage = load_script_module(
    "draft_dup_ratchet_triage_under_test",
    ROOT / "skills/public/quality/scripts/draft_dup_ratchet_triage.py",
)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each option's wrapped argparse block contains its own help text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_triage_help_describes_repo_root_and_json(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        triage.parse_args(["--help"])

    assert excinfo.value.code == 0
    _assert_help_pairs(
        capsys.readouterr().out,
        {
            "--repo-root": "Repository root used to locate ratchet and inventory inputs.",
            "--json": "Emit the triage packet as JSON.",
        },
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
