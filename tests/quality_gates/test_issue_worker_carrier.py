"""File-backed worker carrier tests for issue closeout fresh-eye evidence.

These cases verify that process/media success cannot be consumed as reviewer approval.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from functools import cache
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.issue_closeout_support import bug_closeout_body, seed_commit
from tests.quality_gates.reviewer_capability_support import (
    non_claims_sha256,
    ready_capability,
    receipt_capability_fields,
    result_capability_fields,
    target_non_claim,
    unavailable_optional_capability,
)
from tests.quality_gates.seeding_support import load_module, verify_closeout_args
from tests.quality_gates.support import ROOT, run_script
from tests.reviewed_input_identity_fixtures import repo_seed as identity_repo_seed
from tests.reviewed_input_identity_fixtures import reviewed_identity_seed

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
CRITIQUE_REL = "charness-artifacts/critique/res-42.md"
CONTRACT_AGENTS_MD = (
    "# Agents\\n\\n## Subagent Delegation\\n\\n"
    "Repo-mandated bounded fresh-eye subagent reviews are already delegated by this contract.\\n"
)


def _load_observer():
    path = ROOT / "skills" / "public" / "issue" / "scripts" / "issue_critique_observer.py"
    return load_module("issue_critique_observer_worker_tests", path)


def _load_resolution_critique():
    path = ROOT / "skills" / "public" / "issue" / "scripts" / "issue_resolution_critique.py"
    return load_module("issue_resolution_critique_worker_tests", path)


def _verify(repo: Path):
    return run_script(SCRIPT, *verify_closeout_args(repo, commit_ref="HEAD"))


def _seed(repo: Path, *, satisfaction: str | None, contract: bool) -> None:
    critique = repo / CRITIQUE_REL
    critique.parent.mkdir(parents=True, exist_ok=True)
    body = "Critique of the #42 resolution.\n"
    if satisfaction is not None:
        body += f"\nFresh-eye satisfaction: {satisfaction}\n"
    critique.write_text(body, encoding="utf-8")
    if contract:
        (repo / "AGENTS.md").write_text(CONTRACT_AGENTS_MD, encoding="utf-8")
    seed_commit(repo, bug_closeout_body(critique_line=f"Critique: {CRITIQUE_REL}"))


@cache
def _captured_reviewed_input() -> dict:
    """Capture one immutable seed identity for carrier-only mutations.

    These tests exercise the file-backed worker joins, not Git capture.  The
    cached seed keeps the real current-identity check while avoiding a fresh
    repository and capture operation for every carrier mutation.
    """
    return reviewed_identity_seed()


def _worker_delivered_artifact(
    tmp_path: Path,
    *,
    report_changes: dict | None = None,
    capability: dict | None = None,
) -> Path:
    capability_payload = capability or ready_capability("issue-worker-1")
    shutil.copytree(identity_repo_seed(), tmp_path, dirs_exist_ok=True)
    reviewed_input = _captured_reviewed_input()
    input_identity = reviewed_input["identity_sha256"]
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(
        json.dumps(
            {
                "kind": "charness.critique_prepare_packet",
                "repo": "corca-ai/charness",
                "prepared_for": "corca-ai/charness#42 resolution-critique",
                "reviewed_input_identity": reviewed_input,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    packet_identity = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    result_path = tmp_path / "worker-result.json"
    result_path.write_text(
        json.dumps(
            {
                "kind": "charness.bounded_review.v1",
                "lens": "issue consumer fixture",
                "packet_sha256": packet_identity,
                "reviewed_input_identity_sha256": input_identity,
                "verdict": "pass",
                "findings": [],
                "counterweight_triage": [],
                "next_move": "fixture only",
                "non_claims": ["fixture only"],
                **result_capability_fields(capability_payload or {"capability_non_claims": []}),
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    result_identity = hashlib.sha256(result_path.read_bytes()).hexdigest()
    boundary_fingerprint = "boundary-1"
    prompt_sha256 = "a" * 64
    schema_sha256 = "b" * 64
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(
        json.dumps(
            {
                "schema_version": "charness.reviewer_worker.v1",
                "run_id": "issue-worker-run-1",
                "backend": "codex_exec",
                "status": "succeeded",
                "terminal": True,
                "exit_code": 0,
                "output_fresh": True,
                "output_file": str(result_path.resolve()),
                "output_sha256": result_identity,
                "output_size": result_path.stat().st_size,
                "attempt_id": "issue-worker-1",
                "scope": "issue-resolution",
                "packet_identity": packet_identity,
                "reviewed_input_identity": input_identity,
                "parent_receipt_identity": "Parent-Receipt-1",
                "boundary_fingerprint": boundary_fingerprint,
                "execution_mode": "file-backed-worker",
                "prompt_sha256": prompt_sha256,
                "schema_sha256": schema_sha256,
                **receipt_capability_fields("issue-worker-1", payload=capability_payload),
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    from skills.shared.scripts.reviewer_delivery import DeliveryLedger
    from skills.shared.scripts.reviewer_worker_report import build_report

    ledger = DeliveryLedger.empty()
    attempt = ledger.start(
        attempt_id="issue-worker-1",
        scope="issue-resolution",
        packet_identity=packet_identity,
        reviewed_input_identity=input_identity,
        parent_receipt_identity="Parent-Receipt-1",
        boundary_fingerprint=boundary_fingerprint,
        execution_mode="file-backed-worker",
        backend="codex_exec",
        prompt_sha256=prompt_sha256,
        schema_sha256=schema_sha256,
        capability_launch_envelope_sha256=receipt_capability_fields("issue-worker-1", payload=capability_payload)[
            "capability_launch_envelope_sha256"
        ],
        output_file=str(result_path.resolve()),
        receipt_file=str(receipt_path.resolve()),
        producer_run_id="issue-worker-run-1",
        recorded_at="2026-08-21T00:00:00Z",
    )
    attempt.record_findings(
        scope="issue-resolution",
        packet_identity=packet_identity,
        parent_receipt_identity="Parent-Receipt-1",
        findings_identity=result_identity,
        recorded_at="2026-08-21T00:00:01Z",
    )
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(ledger.to_dict(), separators=(",", ":")), encoding="utf-8")
    report = build_report(
        receipt_path=str(receipt_path.resolve()),
        ledger_path=str(ledger_path.resolve()),
        attempt_id="issue-worker-1",
        scope="issue-resolution",
        packet_identity=packet_identity,
        reviewed_input_identity=input_identity,
        parent_receipt_identity="Parent-Receipt-1",
    )
    if report_changes:
        report.update(report_changes)
    report_path = tmp_path / "worker-report.yaml"
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()
    artifact = tmp_path / "res-42.md"
    artifact.write_text(
        """Critique of the #42 resolution.

## Reviewer Tier Evidence

- Worker report: worker-report.yaml
- Worker report identity: {report_identity}
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: {packet_identity}
- Worker report input identity: {input_identity}
- Worker report parent receipt identity: Parent-Receipt-1
- Worker report findings identity: {findings_identity}

## Fresh-Eye Satisfaction

worker-delivered

## Reviewed Input Identity

- Packet path: packet.json
- Packet SHA256: {packet_identity}
- Identity SHA256: {input_identity}
""".format(
            report_identity=report_identity,
            packet_identity=packet_identity,
            input_identity=input_identity,
            findings_identity=result_identity,
        ),
        encoding="utf-8",
    )
    return artifact


# --------------------------------------------------------------------------
# Twelve independent worker-report carrier scenarios, one node. Each installs
# its own copy of the cached identity-checkout seed via `_worker_delivered_artifact`
# (a copytree, not a git spawn) and asks `_observer_disposition` a single
# question about it. A failure names the exact `_case_*` function in its
# traceback, which is where each former test's rationale now lives.
# --------------------------------------------------------------------------


def _case_worker_delivered_requires_the_shared_report_carrier(case_dir: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(case_dir)
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(
        case_dir,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )

    assert observer["disposition"] == "delegated"
    assert observer["carrier_verified"] is True
    assert observer["carrier"] == "worker-report"


def _case_worker_delivered_foreign_packet_is_refused_by_the_issue_consumer(case_dir: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(case_dir, report_changes={"packet_identity": "d" * 64})
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(case_dir, check)

    assert observer["disposition"] == "carrier-unverified"
    assert "identity joins" in observer["carrier_reason"]


def _case_worker_carrier_rejects_capability_identity_foreign_to_the_attempt(case_dir: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(case_dir)
    report_path = case_dir / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    foreign_capability = "e" * 64
    report["capability_launch_envelope_sha256"] = foreign_capability
    report["provenance"]["capability_launch_envelope_sha256"] = foreign_capability
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()
    lines = []
    for line in artifact.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Worker report identity:"):
            line = f"- Worker report identity: {report_identity}"
        lines.append(line)
    artifact.write_text("\n".join(lines) + "\n", encoding="utf-8")

    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(case_dir, check)

    assert observer["disposition"] == "carrier-unverified"
    assert "capability_launch_envelope_sha256" in observer["carrier_reason"]


def _case_worker_carrier_rejects_optional_non_claim_result_mutation(
    case_dir: Path, mutation: str
) -> None:
    capability = unavailable_optional_capability("issue-worker-1")
    artifact = _worker_delivered_artifact(case_dir, capability=capability)
    result_path = case_dir / "worker-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if mutation == "missing":
        result.pop("capability_non_claims")
    else:
        result["capability_non_claims"] = [target_non_claim("github:issue:690", "unproved")]
    if mutation != "missing":
        result["capability_non_claims_sha256"] = non_claims_sha256(result.get("capability_non_claims", []))
    result_path.write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    result_identity = hashlib.sha256(result_path.read_bytes()).hexdigest()

    receipt_path = case_dir / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["output_sha256"] = result_identity
    receipt["output_size"] = result_path.stat().st_size
    receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")

    ledger_path = case_dir / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["attempts"][0]["findings_identity"] = result_identity
    ledger_path.write_text(json.dumps(ledger, separators=(",", ":")), encoding="utf-8")

    report_path = case_dir / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report["findings_identity"] = result_identity
    report["receipt_output_sha256"] = result_identity
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()
    artifact_lines = []
    for line in artifact.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Worker report identity:"):
            line = f"- Worker report identity: {report_identity}"
        elif line.startswith("- Worker report findings identity:"):
            line = f"- Worker report findings identity: {result_identity}"
        artifact_lines.append(line)
    artifact.write_text("\n".join(artifact_lines) + "\n", encoding="utf-8")

    module = _load_resolution_critique()
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(case_dir, check)
    assert observer["disposition"] == "carrier-unverified"
    expected_reason = "canonical schema" if mutation == "missing" else "non-claim"
    assert expected_reason in observer["carrier_reason"]


def _case_worker_delivered_provenance_alias_mismatch_is_refused(case_dir: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(case_dir)
    report_path = case_dir / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report["provenance"]["attempt_parent_receipt_identity"] = "foreign-parent"
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace(
            next(
                line for line in artifact.read_text(encoding="utf-8").splitlines()
                if line.startswith("- Worker report identity:")
            ),
            f"- Worker report identity: {report_identity}",
        ),
        encoding="utf-8",
    )
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(case_dir, check)

    assert observer["disposition"] == "carrier-unverified"
    assert "provenance aliases" in observer["carrier_reason"]


_WORKER_CARRIER_REFUSAL_CASES = {
    "requires-the-shared-report-carrier": _case_worker_delivered_requires_the_shared_report_carrier,
    "foreign-packet-is-refused-by-the-issue-consumer": (
        _case_worker_delivered_foreign_packet_is_refused_by_the_issue_consumer
    ),
    "capability-identity-foreign-to-the-attempt": (
        _case_worker_carrier_rejects_capability_identity_foreign_to_the_attempt
    ),
    "provenance-alias-mismatch": _case_worker_delivered_provenance_alias_mismatch_is_refused,
}

#: Both arms, named. The helper takes a `mutation` the others do not, so it
#: cannot ride the table above without silently dropping one of its two cases.
_OPTIONAL_NON_CLAIM_MUTATIONS = ("missing", "altered")


def test_worker_carrier_refusal_cases(tmp_path: Path) -> None:
    """Six carrier-refusal scenarios, one node.

    Each case below used to be its own test function; the docstring on each
    `_case_*` helper is that former test's rationale, kept next to the scenario
    it explains. A failure names the exact `_case_*` function in its traceback.
    Cases build their own artifact directory and share no state.

    This dispatcher is the control the consolidation itself needs: the helpers
    were extracted here with no collected caller, so eleven assertions sat in
    the file, uncollected, while an assertion COUNT over the file still balanced.
    A test that is present but unreachable is a worse state than a deleted one,
    because both the file and the count say it is still guarding.
    """
    for label, case in _WORKER_CARRIER_REFUSAL_CASES.items():
        case(tmp_path / label)
    for mutation in _OPTIONAL_NON_CLAIM_MUTATIONS:
        _case_worker_carrier_rejects_optional_non_claim_result_mutation(
            tmp_path / f"optional-non-claim-{mutation}", mutation
        )


def test_worker_delivered_prose_without_carrier_is_not_approval(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = tmp_path / "res-42.md"
    artifact.write_text(
        "Critique of the #42 resolution.\n\nFresh-eye satisfaction: worker-delivered\n",
        encoding="utf-8",
    )
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(tmp_path, check)

    assert observer["disposition"] == "carrier-unverified"
    assert observer["carrier_verified"] is False
    assert "carrier" in observer["carrier_reason"]


def _rebind_worker_packet(
    artifact: Path, prepared_for: str, *, repo: str | None = None
) -> None:
    """Rebind every carrier layer after changing packet context."""
    root = artifact.parent
    packet = root / "packet.json"
    packet_payload = json.loads(packet.read_text(encoding="utf-8"))
    packet_payload["prepared_for"] = prepared_for
    if repo is not None:
        packet_payload["repo"] = repo
    packet.write_text(json.dumps(packet_payload, separators=(",", ":")), encoding="utf-8")
    packet_identity = hashlib.sha256(packet.read_bytes()).hexdigest()

    result_path = root / "worker-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["packet_sha256"] = packet_identity
    result_path.write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    result_identity = hashlib.sha256(result_path.read_bytes()).hexdigest()

    receipt_path = root / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["packet_identity"] = packet_identity
    receipt["output_sha256"] = result_identity
    receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")

    ledger_path = root / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["attempts"][0]["packet_identity"] = packet_identity
    ledger["attempts"][0]["findings_identity"] = result_identity
    ledger_path.write_text(json.dumps(ledger, separators=(",", ":")), encoding="utf-8")

    report_path = root / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report["packet_identity"] = packet_identity
    report["findings_identity"] = result_identity
    report["receipt_output_sha256"] = result_identity
    for key in (
        "packet_identity",
        "attempt_packet_identity",
        "result_packet_identity",
    ):
        report["provenance"][key] = packet_identity
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()

    artifact_lines = []
    for line in artifact.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Worker report identity:"):
            line = f"- Worker report identity: {report_identity}"
        elif line.startswith("- Worker report packet identity:"):
            line = f"- Worker report packet identity: {packet_identity}"
        elif line.startswith("- Worker report findings identity:"):
            line = f"- Worker report findings identity: {result_identity}"
        elif line.startswith("- Packet SHA256:"):
            line = f"- Packet SHA256: {packet_identity}"
        artifact_lines.append(line)
    artifact.write_text("\n".join(artifact_lines) + "\n", encoding="utf-8")


def _rebind_worker_result(artifact: Path, *, verdict: str | None = None) -> None:
    """Change result semantics while rebinding every transport hash."""
    root = artifact.parent
    result_path = root / "worker-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if verdict is not None:
        result["verdict"] = verdict
    result_path.write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    result_identity = hashlib.sha256(result_path.read_bytes()).hexdigest()

    receipt_path = root / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["output_sha256"] = result_identity
    receipt["output_size"] = result_path.stat().st_size
    receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")

    ledger_path = root / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["attempts"][0]["findings_identity"] = result_identity
    ledger_path.write_text(json.dumps(ledger, separators=(",", ":")), encoding="utf-8")

    report_path = root / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report["findings_identity"] = result_identity
    report["receipt_output_sha256"] = result_identity
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()

    artifact_lines = []
    for line in artifact.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Worker report identity:"):
            line = f"- Worker report identity: {report_identity}"
        elif line.startswith("- Worker report findings identity:"):
            line = f"- Worker report findings identity: {result_identity}"
        artifact_lines.append(line)
    artifact.write_text("\n".join(artifact_lines) + "\n", encoding="utf-8")


def test_worker_delivered_packet_for_another_issue_is_refused_at_close(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    _rebind_worker_packet(artifact, "corca-ai/charness#99 resolution-critique")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )

    assert observer["disposition"] == "carrier-unverified"
    assert "prepared_for" in observer["carrier_reason"] or "issue #42" in observer["carrier_reason"]


def test_worker_delivered_same_number_from_foreign_repository_is_refused(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    _rebind_worker_packet(artifact, "other-org/other-repo#42 resolution-critique")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}

    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )

    assert observer["disposition"] == "carrier-unverified"
    assert "prepared_for" in observer["carrier_reason"]


def test_worker_delivered_packet_repository_must_rejoin_the_target(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    _rebind_worker_packet(
        artifact,
        "corca-ai/charness#42 resolution-critique",
        repo="other-org/other-repo",
    )
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )
    assert observer["disposition"] == "carrier-unverified"
    assert "packet repo" in observer["carrier_reason"]


def test_worker_delivered_canonical_result_verdict_is_consumed(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    _rebind_worker_result(artifact, verdict="block")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )
    assert observer["disposition"] == "carrier-unverified"
    assert "verdict" in observer["carrier_reason"]


def test_worker_delivered_canonical_history_is_consumed(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    ledger_path = tmp_path / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["attempts"][0]["history"] = [
        {"state": "findings-received", "terminal": True, "attempt_id": "issue-worker-1"}
    ]
    ledger_path.write_text(json.dumps(ledger, separators=(",", ":")), encoding="utf-8")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )
    assert observer["disposition"] == "carrier-unverified"
    assert "canonical history" in observer["carrier_reason"]


def test_worker_delivered_report_attempt_id_must_rejoin_provenance(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    artifact = _worker_delivered_artifact(tmp_path)
    report_path = tmp_path / "worker-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report["attempt_id"] = "foreign-attempt"
    report_path.write_text(yaml.safe_dump(report, sort_keys=True), encoding="utf-8")
    report_identity = hashlib.sha256(report_path.read_bytes()).hexdigest()
    lines = []
    for line in artifact.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Worker report identity:"):
            line = f"- Worker report identity: {report_identity}"
        lines.append(line)
    artifact.write_text("\n".join(lines) + "\n", encoding="utf-8")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(artifact)}]}
    observer = module._observer_disposition(
        tmp_path,
        check,
        expected_issue_numbers=[42],
        expected_repository="corca-ai/charness",
    )
    assert observer["disposition"] == "carrier-unverified"
    assert "attempt_id" in observer["carrier_reason"]


def test_worker_carrier_does_not_import_a_consumer_shadow_helper(tmp_path: Path) -> None:
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "reviewer_delivery_fields.py").write_text(
        "import re\nPARENT_RECEIPT_ID_RE = re.compile(r'.*')\n", encoding="utf-8"
    )
    carrier = ROOT / "skills/shared/scripts/reviewer_worker_carrier.py"
    code = (
        "import importlib.util; "
        f"s=importlib.util.spec_from_file_location('carrier', {str(carrier)!r}); "
        "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        "print(m.PARENT_RECEIPT_ID_RE.fullmatch('not a valid receipt') is not None)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": f"{shadow}:{ROOT}"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"


def test_worker_delivered_carrier_refusal_is_unconditional_without_repo_contract(tmp_path: Path) -> None:
    _seed(tmp_path, satisfaction="worker-delivered", contract=False)

    result = _verify(tmp_path)

    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    observer = payload["resolution_critique_check"]["fresh_eye_observer"]
    assert observer["disposition"] == "carrier-unverified"
    assert payload["resolution_critique_check"]["observer_refusals"][0]["disposition"] == "carrier-unverified"


def test_typed_subagent_claim_over_non_delivery_state_is_refused_at_issue_close(tmp_path: Path) -> None:
    critique = tmp_path / CRITIQUE_REL
    critique.parent.mkdir(parents=True, exist_ok=True)
    critique.write_text(
        """Critique of the #42 resolution.

Fresh-eye satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer
- Requested spawn fields: typed bounded reviewer
- Host exposure state: pending-parent-spawn
- Application state: n/a
- Delivery state: pending-parent-spawn
- Execution mode: typed-subagent
""",
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text(CONTRACT_AGENTS_MD, encoding="utf-8")
    seed_commit(tmp_path, bug_closeout_body(critique_line=f"Critique: {CRITIQUE_REL}"))

    result = _verify(tmp_path)

    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    observer = payload["resolution_critique_check"]["fresh_eye_observer"]
    assert observer["disposition"] == "delegation-contradicted"


def test_cited_critique_outside_repo_is_refused(tmp_path: Path) -> None:
    module = _load_resolution_critique()
    foreign = tmp_path.parent / "foreign-critique.md"
    foreign.write_text("Critique of #42.\nFresh-eye satisfaction: parent-delegated\n", encoding="utf-8")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(foreign)}]}

    observer = module._observer_disposition(tmp_path, check, expected_issue_numbers=[42])

    assert observer["disposition"] == "outside-repo"


def test_collapsed_plugin_issue_loader_works_from_an_unrelated_cwd(tmp_path: Path) -> None:
    script = ROOT / "plugins" / "charness" / "skills" / "issue" / "scripts" / "issue_tool.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "ModuleNotFoundError" not in result.stderr
