"""Tests for the #358 mutation-run proof gate.

`scripts/check_mutation_run_proof.py` is the gate-shaped upgrade of the
`mutation-dispatch-no-base-sha-false-proof` durable artifact: a deterministic
refusal when a mutation workflow run is cited as proof of a claim its trigger
cannot evaluate. The classifier is pure, so the refusal matrix is pinned
without network or git state; the CLI is exercised over facts and manifests.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT, run_script

_GATE = "scripts/check_mutation_run_proof.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("check_mutation_run_proof", ROOT / _GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GATE = _load_gate()


# Classifier matrix --------------------------------------------------------
def test_changed_line_claim_refused_for_workflow_dispatch() -> None:
    verdict = GATE.classify_run_proof("changed-line", event="workflow_dispatch")
    assert verdict["provable"] is False
    assert verdict["class_key"] == GATE.CLASS_KEY
    assert "no base_sha" in verdict["reason"]
    assert verdict["supported_proof_paths"] == GATE.SUPPORTED_CHANGED_LINE_PROOF_PATHS


def test_changed_line_claim_refused_for_pull_request_dry_run() -> None:
    verdict = GATE.classify_run_proof("changed-line", event="pull_request")
    assert verdict["provable"] is False
    assert "dry-run" in verdict["reason"]
    # PR dry-run is mode confusion, not the dispatch/no-base-sha class.
    assert "class_key" not in verdict


def test_changed_line_claim_refused_without_base_sha_evidence() -> None:
    # A schedule run can still lack a base (no previous completed run) and an
    # event-less fact set proves nothing: refuse-by-default is the gate shape.
    for facts in ({"event": "schedule"}, {}, {"base_sha": "   "}):
        verdict = GATE.classify_run_proof("changed-line", **facts)
        assert verdict["provable"] is False, facts
        assert verdict["class_key"] == GATE.CLASS_KEY


def test_changed_line_claim_provable_with_real_base_range() -> None:
    for event in ("schedule", None):
        verdict = GATE.classify_run_proof("changed-line", event=event, base_sha="abc123")
        assert verdict["provable"] is True, event
        assert "live" in verdict["reason"]


def test_score_claim_provable_for_dispatch_and_schedule_but_not_pr() -> None:
    assert GATE.classify_run_proof("score", event="workflow_dispatch")["provable"] is True
    assert GATE.classify_run_proof("score", event="schedule")["provable"] is True
    assert GATE.classify_run_proof("score", event="pull_request")["provable"] is False


def test_non_success_conclusion_refuses_every_claim() -> None:
    for claim in ("changed-line", "score"):
        verdict = GATE.classify_run_proof(
            claim, event="schedule", base_sha="abc123", conclusion="failure"
        )
        assert verdict["provable"] is False, claim
        assert "not success" in verdict["reason"]


# Manifest fact extraction --------------------------------------------------
def test_manifest_facts_from_json_and_md(tmp_path: Path) -> None:
    json_manifest = tmp_path / "sample.json"
    json_manifest.write_text(json.dumps({"base_sha": "abc123"}), encoding="utf-8")
    assert GATE.facts_from_manifest(json_manifest) == {"base_sha": "abc123"}

    json_manifest.write_text(json.dumps({"base_sha": None}), encoding="utf-8")
    assert GATE.facts_from_manifest(json_manifest) == {"base_sha": ""}

    md_manifest = tmp_path / "sample.md"
    md_manifest.write_text(
        "# Mutation Sample\n\n- Base SHA: `abc123`\n- Head SHA: `def456`\n", encoding="utf-8"
    )
    assert GATE.facts_from_manifest(md_manifest) == {"base_sha": "abc123"}

    md_manifest.write_text(
        "# Mutation Sample\n\n- Base SHA: `(none)`\n- Head SHA: `def456`\n", encoding="utf-8"
    )
    assert GATE.facts_from_manifest(md_manifest) == {"base_sha": ""}


def test_manifest_without_base_line_is_an_error(tmp_path: Path) -> None:
    md_manifest = tmp_path / "sample.md"
    md_manifest.write_text("# Mutation Sample\n\n- Seed: `x`\n", encoding="utf-8")
    try:
        GATE.facts_from_manifest(md_manifest)
    except ValueError as error:
        assert "Base SHA" in str(error)
    else:
        raise AssertionError("expected ValueError for a manifest without a Base SHA line")


# Run-facts resolution (gh) --------------------------------------------------
def test_facts_from_run_parses_gh_payload(monkeypatch) -> None:
    def fake_run(command, capture_output, text):
        assert command[:3] == ["gh", "run", "view"]
        assert "--repo" in command and "corca-ai/charness" in command
        return subprocess_result(0, json.dumps({"event": "workflow_dispatch", "conclusion": "success"}), "")

    monkeypatch.setattr(GATE.subprocess, "run", fake_run)
    facts = GATE.facts_from_run("123", "corca-ai/charness")
    assert facts == {"event": "workflow_dispatch", "conclusion": "success"}


def test_facts_from_run_omits_repo_flag_and_raises_on_failure(monkeypatch) -> None:
    def fake_run(command, capture_output, text):
        assert "--repo" not in command
        return subprocess_result(1, "", "run not found")

    monkeypatch.setattr(GATE.subprocess, "run", fake_run)
    try:
        GATE.facts_from_run("123", None)
    except RuntimeError as error:
        assert "run not found" in str(error)
    else:
        raise AssertionError("expected RuntimeError when gh run view fails")


def subprocess_result(returncode: int, stdout: str, stderr: str):
    class Result:
        pass

    result = Result()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_main_run_id_branch_refuses_dispatch(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        GATE, "facts_from_run", lambda run_id, repo: {"event": "workflow_dispatch", "conclusion": "success"}
    )
    exit_code = GATE.main(["--claim", "changed-line", "--run-id", "123"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out)["class_key"] == GATE.CLASS_KEY
    assert GATE.CLASS_KEY in captured.err


def test_main_run_id_gh_failure_is_a_diagnostic_exit(monkeypatch, capsys) -> None:
    def boom(run_id, repo):
        raise RuntimeError("gh run view failed: auth")

    monkeypatch.setattr(GATE, "facts_from_run", boom)
    exit_code = GATE.main(["--claim", "score", "--run-id", "123"])
    assert exit_code == 1
    assert "could not resolve run facts" in capsys.readouterr().err


# CLI ------------------------------------------------------------------------
def test_cli_refuses_dispatch_changed_line_claim_with_class_key() -> None:
    result = run_script(_GATE, "--claim", "changed-line", "--event", "workflow_dispatch")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["provable"] is False
    assert payload["class_key"] == GATE.CLASS_KEY
    assert "REFUSED" in result.stderr
    assert GATE.CLASS_KEY in result.stderr
    assert "Supported changed-line proof paths" in result.stderr


def test_cli_accepts_changed_line_claim_with_base_sha() -> None:
    result = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--base-sha", "abc123"
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["provable"] is True
    assert result.stderr == ""


def test_cli_judges_changed_line_claim_from_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "sample.md"
    manifest.write_text("- Base SHA: `(none)`\n", encoding="utf-8")
    refused = run_script(_GATE, "--claim", "changed-line", "--sample-manifest", str(manifest))
    assert refused.returncode == 1
    assert json.loads(refused.stdout)["class_key"] == GATE.CLASS_KEY

    manifest.write_text("- Base SHA: `abc123`\n", encoding="utf-8")
    provable = run_script(_GATE, "--claim", "changed-line", "--sample-manifest", str(manifest))
    assert provable.returncode == 0, provable.stderr


def test_cli_missing_manifest_fails_with_diagnostic(tmp_path: Path) -> None:
    result = run_script(
        _GATE, "--claim", "changed-line", "--sample-manifest", str(tmp_path / "absent.md")
    )
    assert result.returncode == 1
    assert "could not resolve run facts" in result.stderr
