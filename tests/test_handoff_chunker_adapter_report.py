"""The D46 issue-adapter report must survive the whole documented pipeline.

D46 recorded that its uninterpreted-line warnings are "legibility, not teeth.
Nothing reads it today". Slice 1 gave them a reader. These tests own the
*pipeline-survival* half of that claim: the parse -> propose -> packet flow
already dropped ``issue_source_diagnostic`` once (recorded as F3 in
charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-postcommit-subagent-critique.md),
and a field that lives for exactly one stage is a field no agent ever reads.

The per-shape behaviour of the report itself lives in
tests/test_handoff_chunker_issue_source.py; this module is the transport.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"
PARSER_SCRIPT = SCRIPTS / "parse_handoff_entries.py"


def _load_parser_module():
    spec = importlib.util.spec_from_file_location("parse_handoff_entries", PARSER_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse_payload_with_adapter_report(tmp_path, monkeypatch, capsys, report):
    peh = _load_parser_module()
    handoff = tmp_path / "handoff.md"
    handoff.write_text(
        "## Next Session\n\n1. **Only.** do a thing.\n\n## End\n", encoding="utf-8"
    )
    iss = peh.chunked_routing_issue_source

    def fake_build(repo_root, *, start_index):
        iss.LAST_ISSUE_ADAPTER_REPORT = report
        return []

    monkeypatch.setattr(iss, "build_issue_entries", fake_build)
    monkeypatch.setattr(
        sys, "argv",
        ["parse_handoff_entries.py", "--handoff-path", str(handoff),
         "--repo-root", str(tmp_path), "--with-issues"],
    )
    assert peh.main() == 0
    return json.loads(capsys.readouterr().out)


def test_cli_emits_issue_adapter_report_when_the_adapter_had_something_to_say(
    tmp_path, monkeypatch, capsys
):
    report = {"valid": False, "errors": ["version must be an integer"],
              "warnings": [], "path": "/x/.agents/issue-adapter.yaml"}
    payload = _parse_payload_with_adapter_report(tmp_path, monkeypatch, capsys, report)
    assert payload["issue_adapter_report"] == report
    # Reporting only: an invalid adapter does not fail the CLI or empty the run.
    assert payload["ok"] is True


def test_cli_omits_issue_adapter_report_for_a_clean_adapter(
    tmp_path, monkeypatch, capsys
):
    payload = _parse_payload_with_adapter_report(tmp_path, monkeypatch, capsys, None)
    assert "issue_adapter_report" not in payload


def test_adapter_report_survives_propose_merges_and_prepare_chunk_packet(tmp_path):
    """Both downstream stages forward it, as they already do for `staleness`."""
    report = {"valid": False, "errors": ["boom"], "warnings": [], "path": None}
    payload = {
        "entries": [{
            "index": 1, "title": "t", "body": "b", "referenced_paths": [],
            "referenced_issues": [], "referenced_skills": [], "boundary_tokens": [],
        }],
        "issue_adapter_report": report,
    }
    merged = json.loads(subprocess.run(
        [sys.executable, str(SCRIPTS / "propose_merges.py")],
        input=json.dumps(payload), capture_output=True, text=True, check=True,
    ).stdout)
    assert merged["issue_adapter_report"] == report

    packet = json.loads(subprocess.run(
        [sys.executable, str(SCRIPTS / "prepare_chunk_packet.py"), "--repo-root", str(tmp_path)],
        input=json.dumps(payload), capture_output=True, text=True, check=True,
    ).stdout)
    assert packet["issue_adapter_report"] == report


# --- the shared pipeline-stage helpers the forwarding extraction created ---------


def _load_cli_module():
    spec = importlib.util.spec_from_file_location(
        "chunked_routing_cli", SCRIPTS / "chunked_routing_cli.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_malformed_payload_refuses_at_the_stage_that_read_it():
    """`entries_from_pipeline_payload` must turn a restore failure into a stage
    refusal, not a traceback two stages downstream."""
    cli = _load_cli_module()

    class _Lib:
        @staticmethod
        def entries_from_payload(payload):
            raise ValueError("entries[] is not a list")

    with pytest.raises(SystemExit) as excinfo:
        cli.entries_from_pipeline_payload({"entries": "nope"}, _Lib)

    assert "entries[] is not a list" in str(excinfo.value)


def test_forwarding_a_non_payload_is_a_no_op_not_a_crash():
    """The stages accept either the full parser payload or a bare entries array."""
    cli = _load_cli_module()
    output = {"kept": True}

    cli.forward_carried_keys([{"index": 1}], output, ("staleness",))

    assert output == {"kept": True}


def test_forwarding_copies_only_present_non_null_keys():
    cli = _load_cli_module()
    output = {}

    cli.forward_carried_keys(
        {"staleness": {"paths_checked": True}, "issue_source_diagnostic": None},
        output,
        ("staleness", "issue_source_diagnostic", "issue_adapter_report"),
    )

    # Absent stays absent, so a missing key never reads as "the check ran and found
    # nothing" -- and an explicit null is treated the same as absent.
    assert output == {"staleness": {"paths_checked": True}}
