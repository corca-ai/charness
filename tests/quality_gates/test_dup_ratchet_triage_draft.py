from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

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


def test_triage_help_describes_repo_root_and_offers_no_json(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        triage.parse_args(["--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    _assert_help_pairs(
        output,
        {"--repo-root": "Repository root used to locate ratchet and inventory inputs."},
    )
    # Output is unconditionally YAML now; offering `--json` in the help would send
    # the operator to a flag the parser rejects with exit 2.
    assert "--json" not in output


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


def test_family_without_sample_locations_is_never_suggested_intentional() -> None:
    # Sweep S27: an empty basename set made `basenames <= {adapter copies}` vacuously
    # true, so a 9-member/400-shared-line family whose locations the inventory omitted
    # (a --summary view, a truncated record) was suggested `intentional` and drafted a
    # permanent accept into dup-review.json over ZERO established evidence.
    ratchet = {"status": "hard-block", "new_code_families": ["fam-noloc"]}
    inventory = {
        "families": [{"family_fingerprint": "fam-noloc", "members": 9, "shared_lines": 400}]
    }

    report = triage.build_report(ratchet, inventory)

    family = report["families"][0]
    assert family["suggested_action"] == "review-needed"
    assert "no sampled member locations" in family["reason"]
    assert family["draft_dup_review_entry"]["class"] == "unreviewed"


def test_family_with_empty_sample_locations_is_never_suggested_intentional() -> None:
    action, reason = triage.suggest_action(
        {"family_fingerprint": "f", "members": 9, "shared_lines": 400, "sample_locations": []}
    )
    assert action == "review-needed" and "no sampled member locations" in reason


def test_family_without_shared_lines_is_not_read_as_a_tiny_idiom() -> None:
    # The same defect one field over: `int(None or 0)` made an ABSENT span size satisfy
    # the `shared_lines <= 5` small-idiom branch, again drafting `intentional`.
    action, reason = triage.suggest_action(
        {
            "family_fingerprint": "f",
            "members": 2,
            "sample_locations": [
                {"file": "scripts/a.py", "start_line": 1, "end_line": 40},
                {"file": "skills/public/x/scripts/b.py", "start_line": 9, "end_line": 48},
            ],
        }
    )
    assert action == "review-needed" and "no shared_lines" in reason


def test_adapter_copy_branch_refuses_a_truncated_member_set() -> None:
    # `sample_locations` is capped at 6 by family_summary, so on a 20-member family the
    # basename subset rules on 6 of 20. Suggesting the permanent accept from a truncated
    # member set is the same unestablished-scope call as suggesting it from an empty one.
    action, reason = triage.suggest_action(
        {
            "family_fingerprint": "f",
            "members": 20,
            "shared_lines": 40,
            "sample_locations": [
                {
                    "file": f"skills/public/s{i}/scripts/resolve_adapter.py",
                    "start_line": 1,
                    "end_line": 40,
                }
                for i in range(6)
            ],
        }
    )
    assert action == "review-needed"
    assert "samples only 6 of 20 members" in reason


def test_build_report_refuses_a_ratchet_payload_that_never_evaluated() -> None:
    # `ratchet.get("new_code_families") or []` turned a gate that could not judge
    # (invalid adapter, inert, rebaseline mode) into "0 families to triage", ok, exit 0.
    for ratchet in (
        {"status": "adapter-invalid", "messages": ["bad adapter"]},
        {"status": "inert"},
        {"status": "baseline-written", "code_family_count": 7},
        {"status": "clean"},  # evaluated statuses still need the list itself
    ):
        report = triage.build_report(ratchet, {"families": []})
        assert report["ok"] is False, ratchet
        assert report["family_count"] == 0
        assert (
            "no new_code_families list" in report["unestablished_reason"]
            or "never evaluated the gate" in report["unestablished_reason"]
        )


def test_build_report_refuses_a_degraded_ratchet_payload() -> None:
    # `degraded` is the canonical could-not-judge status and the one this subsystem now
    # produces most: every code-arm degrade this slice added leaves `evaluate` with an empty
    # live id set, so the verdict is `{"status": "degraded", "new_code_families": [], "ok":
    # true}` — which passed a status-set guard that omitted it. The gate is right to treat a
    # degrade as advisory; this drafter is a WRITER whose output drafts a permanent accept.
    ratchet = {
        "ok": True,
        "status": "degraded",
        "new_code_families": [],
        "new_doc_families": [],
        "degraded_reasons": ["injected code inventory unreadable (/tmp/empty.json)"],
    }
    report = triage.build_report(ratchet, {"families": []})
    assert report["ok"] is False
    assert "DEGRADED" in report["unestablished_reason"]
    assert "unreadable" in report["unestablished_reason"]  # the gate's own reason is carried


def test_degraded_ratchet_payload_still_lists_the_families_it_named() -> None:
    # The refusal must not hide evidence: whatever a degraded gate DID name is still
    # summarized, so the operator loses nothing by the packet being marked unestablished.
    ratchet = {
        "status": "degraded",
        "new_code_families": ["fam-named"],
        "degraded_reasons": ["doc inventory produced no output"],
    }
    inventory = {
        "families": [
            {
                "family_fingerprint": "fam-named",
                "members": 2,
                "shared_lines": 30,
                "sample_locations": [
                    {"file": "scripts/a.py", "start_line": 1, "end_line": 30},
                    {"file": "scripts/a.py", "start_line": 40, "end_line": 69},
                ],
            }
        ]
    }
    report = triage.build_report(ratchet, inventory)
    assert report["ok"] is False
    assert [family["id"] for family in report["families"]] == ["fam-named"]


def test_build_report_accepts_an_evaluated_empty_family_list() -> None:
    # The discriminating control: an evaluated gate with nothing new to triage.
    report = triage.build_report({"status": "clean", "new_code_families": []}, {"families": []})
    assert report["ok"] is True and report["family_count"] == 0
    assert "unestablished_reason" not in report


def test_adapter_copy_family_still_reads_intentional_with_evidence() -> None:
    # DISCRIMINATING CONTROL (passes before and after): the adapter-copy rule is intact when
    # the record establishes its FULL member set — `members` declared and every member
    # sampled. This is the truncation guard's non-firing arm, so it also pins the
    # `members - len(files)` arithmetic that no other test exercises at equality.
    action, _reason = triage.suggest_action(
        {
            "family_fingerprint": "f",
            "members": 2,
            "shared_lines": 30,
            "sample_locations": [
                {
                    "file": "skills/public/a/scripts/resolve_adapter.py",
                    "start_line": 1,
                    "end_line": 30,
                },
                {
                    "file": "skills/public/b/scripts/resolve_adapter.py",
                    "start_line": 1,
                    "end_line": 30,
                },
            ],
        }
    )
    assert action == "intentional"


def test_adapter_copy_branch_refuses_an_undeclared_member_count() -> None:
    # Absent `members` is not zero unsampled: a record that never says how many members it
    # has establishes no coverage, so it must not reach the permanent-accept suggestion.
    action, reason = triage.suggest_action(
        {
            "family_fingerprint": "f",
            "shared_lines": 30,
            "sample_locations": [
                {
                    "file": "skills/public/a/scripts/resolve_adapter.py",
                    "start_line": 1,
                    "end_line": 30,
                },
                {
                    "file": "skills/public/b/scripts/resolve_adapter.py",
                    "start_line": 1,
                    "end_line": 30,
                },
            ],
        }
    )
    assert action == "review-needed"
    assert "does not say how many members" in reason


def test_main_output_carries_the_refusal_to_the_reader(monkeypatch, capsys) -> None:
    # There is one output channel now, so the refusal has to ride on the emitted
    # payload itself: a packet showing `family_count: 0` with no refusal field renders
    # an unestablished scope as an evaluated empty one.
    monkeypatch.setattr(
        triage,
        "run",
        lambda _args: {
            "ok": False,
            "family_count": 0,
            "families": [],
            "unestablished_reason": "ratchet report is DEGRADED: baseline unreadable",
        },
    )

    assert triage.main(["--repo-root", "."]) == 1

    emitted = yaml.safe_load(capsys.readouterr().out)
    assert emitted["ok"] is False
    assert emitted["family_count"] == 0
    assert emitted["unestablished_reason"] == "ratchet report is DEGRADED: baseline unreadable"


def test_build_report_reports_inventory_misses() -> None:
    report = triage.build_report({"new_code_families": ["missing"]}, {"families": []})

    assert report["ok"] is False
    assert report["missing_from_inventory"] == ["missing"]


# --- `--detail` consumption -------------------------------------------------
#
# `run()` had zero coverage: every test above monkeypatches it away. That is why
# both of its argv lists could keep passing a `--json` the producers had stopped
# declaring, leaving the DEFAULT mode of this script exiting 2 on a clean tree.


def test_run_asks_both_producers_for_detail_and_never_for_json(monkeypatch) -> None:
    commands: list[list[str]] = []

    def record(script: Path, argv: list[str]) -> dict[str, object]:
        commands.append([str(script), *argv])
        return {"status": "hard-block", "new_code_families": [], "families": []}

    monkeypatch.setattr(triage, "_run_detail", record)
    triage.run(triage.parse_args(["--repo-root", str(ROOT)]))

    assert len(commands) == 2
    assert [Path(cmd[0]).name for cmd in commands] == [
        "check_dup_ratchet.py",
        "inventory_nose_clones.py",
    ]
    for cmd in commands:
        assert "--detail" in cmd
        assert "--json" not in cmd


def test_detail_payload_is_read_as_yaml_and_as_json() -> None:
    # `--detail` is YAML, and `scripts/yaml_output.render_yaml` falls back to
    # compact JSON when PyYAML is missing. Both have to read, or the fix trades an
    # exit 2 for a JSONDecodeError on a working producer.
    assert triage._parse_detail_payload("status: ok\nfamilies: []\n", "probe") == {
        "status": "ok",
        "families": [],
    }
    assert triage._parse_detail_payload('{"status":"ok","families":[]}', "probe") == {
        "status": "ok",
        "families": [],
    }


def test_a_non_mapping_detail_payload_is_refused() -> None:
    with pytest.raises(RuntimeError, match="not a mapping"):
        triage._parse_detail_payload("- one\n- two\n", "probe")


def test_an_injected_report_file_may_be_yaml(tmp_path: Path) -> None:
    # `--ratchet-report` / `--code-inventory` name a saved producer payload, and
    # the producer now writes YAML. A reader that only took JSON would make the
    # help text a lie the moment an operator followed it.
    ratchet = tmp_path / "ratchet.yaml"
    ratchet.write_text("status: hard-block\nnew_code_families: [fam1]\n", encoding="utf-8")
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(
        "families:\n"
        "- family_fingerprint: fam1\n"
        "  shared_lines: 8\n"
        "  members: 2\n"
        "  sample_locations:\n"
        "  - {file: scripts/x.py, start_line: 1, end_line: 8}\n"
        "  - {file: scripts/x.py, start_line: 20, end_line: 27}\n",
        encoding="utf-8",
    )

    report = triage.run(
        triage.parse_args(
            [
                "--repo-root",
                str(ROOT),
                "--ratchet-report",
                str(ratchet),
                "--code-inventory",
                str(inventory),
            ]
        )
    )

    assert report["ok"] is True
    assert report["family_count"] == 1


def test_triage_help_names_the_detail_payload_its_reader_accepts(capsys) -> None:
    # The third coupled edit. Migrating the flag and the parser while leaving the
    # help text naming `--json` sends the operator to a producer mode that exits 2.
    with pytest.raises(SystemExit):
        triage.parse_args(["--help"])

    _assert_help_pairs(
        capsys.readouterr().out,
        {
            "--ratchet-report": "Existing check_dup_ratchet --detail payload.",
            "--code-inventory": "Existing inventory_nose_clones --detail payload.",
        },
    )
