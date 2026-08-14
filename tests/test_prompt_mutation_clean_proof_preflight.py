from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

preflight = load_script_module(
    "prompt_mutation_clean_proof_preflight_under_test",
    ROOT / "scripts" / "prompt_mutation_clean_proof_preflight.py",
)


def test_scenario_scan_ignores_author_comments(tmp_path: Path) -> None:
    """`_`-prefixed keys are author comments: the captured run never sees them, so
    scanning them would report a blinding risk on text the agent cannot read. The
    comment is nested INSIDE a visible key here -- a top-level `_comment` is dropped
    by the visible-key filter anyway, so it would pass whether or not this skip
    exists."""
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "declaredReferences": [
                    {"_note": "historical git show note", "ref": "docs/x.md"}
                ],
                "prompt": "run refresh",
            }
        ),
        encoding="utf-8",
    )

    report = preflight.run(preflight.parse_args(["--scenario-spec", str(spec)]))

    assert report["ok"] is True
    assert report["findings"] == []


def test_non_object_scenario_spec_is_scanned_whole(tmp_path: Path) -> None:
    """The visible-key filter only applies to object-shaped specs. A spec whose
    top level is a list has no keys to select from, so skipping it would silently
    make a probe-carrying spec look clean; every string in it is scanned instead."""
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(["warm up", "then run git log --oneline"]), encoding="utf-8")

    report = preflight.run(preflight.parse_args(["--scenario-spec", str(spec)]))

    assert report["clean_proof_claim"] is False
    assert report["clean_proof_blocker_count"] == 1
    assert report["findings"][0]["rule"] == "git-log"
    assert report["findings"][0]["field"] == "$[1]"


def test_scenario_scan_blocks_visible_prompt_probe(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "run git diff main HEAD"}), encoding="utf-8")

    report = preflight.run(preflight.parse_args(["--scenario-spec", str(spec)]))

    assert report["ok"] is True
    assert report["clean_proof_claim"] is False
    assert report["clean_proof_blocker_count"] == 1
    assert report["findings"][0]["rule"] == "git-diff"
    assert report["findings"][0]["severity"] == "clean-proof-blocker"


def test_scenario_scan_blocks_git_global_option_probe(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "run git -C . log --oneline"}), encoding="utf-8")

    report = preflight.run(preflight.parse_args(["--scenario-spec", str(spec)]))

    assert report["clean_proof_claim"] is False
    assert report["findings"][0]["rule"] == "git-log"


def test_transcript_scan_reports_history_probe(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("tool ran: git log --all\n", encoding="utf-8")

    report = preflight.run(preflight.parse_args(["--transcript", str(transcript)]))

    assert report["blocking_count"] == 1
    assert report["findings"][0]["source"] == str(transcript)


def test_no_inputs_reports_no_clean_proof_claim(capsys) -> None:
    report = preflight.run(preflight.parse_args([]))

    assert report["ok"] is True
    assert report["clean_proof_claim"] is False
    assert report["no_inputs"] is True
    assert "No input files were supplied" in report["non_claim"]

    rc = preflight.main([])
    assert rc == 0
    # The retired prose renderer's "no input files supplied" line is now carried by
    # the emitted payload itself. Assert the parsed fields, not a raw substring: the
    # YAML emitter line-wraps long scalars, so `non_claim` spans several lines.
    emitted = yaml.safe_load(capsys.readouterr().out)
    assert emitted["no_inputs"] is True
    assert "No input files were supplied" in emitted["non_claim"]


def test_cli_probe_findings_remain_advisory_exit_zero(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "run git show HEAD~1:file"}), encoding="utf-8")

    rc = preflight.main(["--scenario-spec", str(spec)])

    assert rc == 0
