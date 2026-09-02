from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.adversarial_evidence import EvidenceValidationError, validate
from tests.script_main import load_script_module, run_loaded_script_main

REPO_ROOT = Path(__file__).resolve().parents[1]


def _artifact(*records: str, metadata: str | None = None) -> str:
    evidence_digest = "sha256:" + hashlib.sha256("\n".join(record.strip() for record in records).encode()).hexdigest()
    return "\n".join(
        [
            "## Evidence Disposition",
            metadata
            or "\n".join(
                [
                    "- Report Identity: review:2026-08-25#sha256:" + "a" * 64,
                    f"- Reported Findings: {len(records)}",
                    "- Dispositioned Findings: " + ", ".join(record.split("|", 1)[0].split(":", 1)[1].strip() for record in records),
                    "- Missing Findings: none",
                    f"- Evidence Digest: {evidence_digest}",
                    "- Report Source: fixture/report.json",
                    "- Report Source SHA256: " + "a" * 64,
                ]
            ),
            "## Adversarial Verification",
            *records,
        ]
    )


def _record(
    *,
    finding: str = "F1",
    disposition: str = "reproduced",
    proof: str = "executable fixture",
    observed: str = "final consumer refused",
) -> str:
    receipt = "receipt: none | receipt sha256: none" if disposition in {"unproven", "not-applicable"} else "receipt: receipt.json | receipt sha256: " + "a" * 64
    return (
        f"- Finding: {finding} | source: review.md | expected: consumer refuses missing input "
        f"| stimulus: remove input in temp fixture | disposition: {disposition} "
        f"| observed: {observed} | proof: {proof} | handoff: debug.md "
        "| next move: inspect invariant | " + receipt
    )


def test_evidence_mode_is_noop_when_not_declared() -> None:
    validate("# Historical artifact\n\n## Root Cause\nold memory\n", artifact_label="debug")


def test_valid_typed_record_and_metadata_pass() -> None:
    validate(_artifact(_record()), artifact_label="debug")


def test_reproduced_static_scan_is_rejected() -> None:
    with pytest.raises(EvidenceValidationError, match="cannot use static scan"):
        validate(_artifact(_record(proof="static scan only")), artifact_label="debug")


def test_disconfirmed_static_scan_is_rejected() -> None:
    with pytest.raises(EvidenceValidationError, match="disconfirmed finding"):
        validate(
            _artifact(_record(disposition="disconfirmed", proof="static scan only")),
            artifact_label="debug",
        )


def test_count_and_identity_cover_are_required() -> None:
    with pytest.raises(EvidenceValidationError, match="cover the reported count"):
        validate(
            _artifact(
                _record(),
                metadata="\n".join(
                    [
                        "- Report Identity: review:2026-08-25#sha256:" + "a" * 64,
                        "- Reported Findings: 2",
                        "- Dispositioned Findings: F1",
                        "- Missing Findings: none",
                        "- Evidence Digest: sha256:" + hashlib.sha256(_record().encode()).hexdigest(),
                        "- Report Source: fixture/report.json",
                        "- Report Source SHA256: " + "a" * 64,
                    ]
                ),
            ),
            artifact_label="critique",
        )


def test_partial_report_is_explicitly_non_claimed() -> None:
    validate(
        _artifact(
            _record(),
            metadata="\n".join(
                [
                    "- Report Identity: review:2026-08-25#sha256:" + "a" * 64,
                    "- Reported Findings: 2",
                    "- Dispositioned Findings: F1",
                    "- Missing Findings: F2",
                    "- Evidence Digest: sha256:" + hashlib.sha256(_record().encode()).hexdigest(),
                    "- Report Source: fixture/report.json",
                    "- Report Source SHA256: " + "a" * 64,
                ]
            ),
        ),
        artifact_label="critique",
    )


def test_both_evidence_headings_are_required() -> None:
    with pytest.raises(EvidenceValidationError, match="requires both"):
        validate("## Evidence Disposition\n- Report Identity: x\n", artifact_label="critique")


def test_explicit_evidence_mode_rejects_omitted_sections() -> None:
    with pytest.raises(EvidenceValidationError, match="--evidence-led requires"):
        validate("# Debug Review\n## Root Cause\nold\n", artifact_label="debug", evidence_mode=True)


def test_placeholder_suffixes_and_tiny_identity_are_rejected() -> None:
    with pytest.raises(EvidenceValidationError, match="finding record"):
        validate(_artifact(_record(observed="TODO observed")), artifact_label="debug")
    with pytest.raises(EvidenceValidationError, match="Report Identity"):
        validate(
            _artifact(
                _record(),
                metadata="\n".join(
                    [
                        "- Report Identity: x",
                        "- Reported Findings: 1",
                        "- Dispositioned Findings: F1",
                        "- Missing Findings: none",
                        "- Evidence Digest: sha256:" + hashlib.sha256(_record().encode()).hexdigest(),
                        "- Report Source: fixture/report.json",
                        "- Report Source SHA256: " + "a" * 64,
                    ]
                ),
            ),
            artifact_label="debug",
        )


def test_reproduced_finding_needs_handoff_and_next_move() -> None:
    with pytest.raises(EvidenceValidationError, match="debug handoff"):
        validate(
            _artifact(_record()).replace("handoff: debug.md", "handoff: none"),
            artifact_label="debug",
        )


def test_evidence_digest_binds_record_content() -> None:
    with pytest.raises(EvidenceValidationError, match="Evidence Digest"):
        validate(
            _artifact(_record(observed="a different consumer output")).replace(
                "a different consumer output", "another consumer output"
            ),
            artifact_label="debug",
        )


def test_reproduced_claim_cannot_pass_without_consumer_receipt(tmp_path: Path) -> None:
    with pytest.raises(EvidenceValidationError, match="receipt does not exist"):
        validate(_artifact(_record()), artifact_label="debug", repo_root=tmp_path)


def test_report_source_digest_is_recomputed_when_repo_root_is_available(tmp_path) -> None:
    source = tmp_path / "fixture" / "report.json"
    source.parent.mkdir()
    source.write_bytes(b"reported finding")
    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    record = _record()
    receipt = tmp_path / "receipt.json"
    receipt.write_text(
        json.dumps(
            {
                "schema": "charness.adversarial-evidence.receipt.v1",
                "finding": "F1",
                "source": "review.md",
                "expected": "consumer refuses missing input",
                "stimulus": "remove input in temp fixture",
                "disposition": "reproduced",
                "observed": "final consumer refused",
                "command": "fixture-runner",
                "fixture": "tmp-fixture",
                "final_consumer": "consumer",
                "executed": True,
                "final_consumer_observed": True,
                "returncode": 0,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    receipt_sha256 = hashlib.sha256(receipt.read_bytes()).hexdigest()
    artifact = _artifact(record.replace("a" * 64, receipt_sha256, 1), metadata="\n".join([
        "- Report Identity: review:2026-08-25#sha256:" + source_sha256,
        "- Reported Findings: 1",
        "- Dispositioned Findings: F1",
        "- Missing Findings: none",
        "- Evidence Digest: sha256:" + hashlib.sha256(record.replace("a" * 64, receipt_sha256, 1).encode()).hexdigest(),
        "- Report Source: fixture/report.json",
        "- Report Source SHA256: " + source_sha256,
    ]).replace("receipt.json", "receipt.json"))
    validate(artifact, artifact_label="debug", repo_root=tmp_path)
    source.write_bytes(b"changed report")
    with pytest.raises(EvidenceValidationError, match="stale or tampered"):
        validate(artifact, artifact_label="debug", repo_root=tmp_path)


def test_report_identity_must_bind_source_digest() -> None:
    with pytest.raises(EvidenceValidationError, match="must equal Report Source"):
        validate(
            _artifact(_record()).replace(
                "Report Identity: review:2026-08-25#sha256:" + "a" * 64,
                "Report Identity: review:2026-08-25#sha256:" + "c" * 64,
            ),
            artifact_label="debug",
        )


def test_external_source_without_repo_root_is_non_claim() -> None:
    with pytest.raises(EvidenceValidationError, match="external Report Source"):
        validate(
            _artifact(_record()).replace("fixture/report.json", "external/report.json"),
            artifact_label="debug",
        )
    validate(
        _artifact(_record(disposition="unproven", proof="static scan only")).replace(
            "fixture/report.json", "external/report.json"
        ),
        artifact_label="debug",
    )


@pytest.mark.parametrize(
    ("skill", "heading"),
    (("critique", "## Evidence Disposition"), ("debug", "## Adversarial Verification")),
)
def test_evidence_led_scaffolds_bind_template_and_validator(skill: str, heading: str) -> None:
    script = REPO_ROOT / "skills" / "public" / skill / "scripts" / f"scaffold_{skill}_artifact.py"
    module = load_script_module(f"scaffold_{skill}_artifact_under_test", script)
    result = run_loaded_script_main(
        script.name,
        module,
        "--repo-root",
        str(REPO_ROOT),
        "--evidence-led",
        "--subject",
        "evidence-test",
    )
    assert result.returncode == 0, result.stderr
    assert "evidence_mode: true" in result.stdout
    assert "--evidence-led" in result.stdout
    assert heading in result.stdout
