"""Post-review regression coverage for the current release slice.

These tests exercise the refusal and recovery branches that the incremental
changed-line gate named after the v6.5.0 review.  They are intentionally
in-process: a subprocess exit code is not evidence that the producer line was
executed by the focused coverage run.

The literal source paths below are part of the focused mapper's dependency
contract.  Keep them next to the imports when a producer is moved.
"""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from scripts import adversarial_evidence as adversarial
from scripts import capability_catalog_resolver as catalog_resolver
from scripts import critique_packet_lib as critique_packet
from scripts import reviewed_input_identity as reviewed_identity
from scripts import reviewed_input_verification as reviewed_verification
from scripts import staged_commit_gate_plan_helpers as staged_helpers

ROOT = Path(__file__).resolve().parents[1]

_MUTATION_SOURCES = (
    "charness",
    "scripts/adversarial_evidence.py",
    "scripts/capability_catalog_resolver.py",
    "scripts/critique_packet_lib.py",
    "scripts/reviewed_input_identity.py",
    "scripts/staged_commit_gate_plan_helpers.py",
    "skills/public/critique/scripts/prepare_packet.py",
    "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "skills/public/quality/scripts/dup_family_lineage.py",
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "skills/public/quality/scripts/check_provenance_contract.py",
    "skills/public/setup/scripts/inspect_repo.py",
)


def _load_script(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


critique_runner = import_repo_module(
    ROOT / "skills/public/critique/scripts/prepare_packet.py",
    "skills.public.critique.scripts.prepare_packet",
)
debug_persist = import_repo_module(
    ROOT / "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills.public.debug.scripts.persist_debug_artifact",
)
dup_check = _load_script(
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "release_dup_check_under_test",
)
dup_lineage = _load_script(
    "skills/public/quality/scripts/dup_family_lineage.py",
    "release_dup_lineage_under_test",
)
dup_baseline = _load_script(
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "release_dup_baseline_under_test",
)
provenance_check = _load_script(
    "skills/public/quality/scripts/check_provenance_contract.py",
    "release_provenance_check_under_test",
)
setup_inspect = import_repo_module(
    ROOT / "skills/public/setup/scripts/inspect_repo.py",
    "skills.public.setup.scripts.inspect_repo",
)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _valid_record(
    finding: str = "F1",
    *,
    disposition: str = "unproven",
    proof: str = "static scan only",
    handoff: str = "none",
    next_move: str = "none",
    receipt: str = "none",
    receipt_sha: str = "none",
) -> str:
    return (
        f"- Finding: {finding} | source: review.md | expected: consumer refuses input "
        f"| stimulus: remove input | disposition: {disposition} | observed: refused "
        f"| proof: {proof} | handoff: {handoff} | next move: {next_move} "
        f"| receipt: {receipt} | receipt sha256: {receipt_sha}"
    )


def _evidence_metadata(**overrides: str) -> str:
    values = {
        "Report Identity": "review:fixture#sha256:" + "a" * 64,
        "Reported Findings": "1",
        "Dispositioned Findings": "F1",
        "Missing Findings": "none",
        "Evidence Digest": "sha256:" + "b" * 64,
        "Report Source": "report.json",
        "Report Source SHA256": "a" * 64,
    }
    values.update(overrides)
    return "\n".join(f"- {key}: {value}" for key, value in values.items())


def _evidence_text(record: str, metadata: str | None = None) -> str:
    return "\n".join(
        [
            "## Evidence Disposition",
            metadata or _evidence_metadata(),
            "## Adversarial Verification",
            record,
        ]
    )


def test_adversarial_evidence_rejects_malformed_receipts_and_metadata(tmp_path: Path) -> None:
    assert adversarial._section("## Other\nvalue", "## Evidence Disposition") == []
    assert adversarial._field_value(["- Other: value"], "Missing") is None
    assert adversarial._record("not a finding") == {}
    assert adversarial._record("- Finding: F1 | malformed item | disposition: unproven")

    with pytest.raises(adversarial.EvidenceValidationError, match="receipt must be repo-relative"):
        adversarial._receipt_candidate(
            tmp_path, "../receipt.json", "a" * 64, artifact_label="fixture", index=1
        )
    with pytest.raises(adversarial.EvidenceValidationError, match="receipt sha256 is invalid"):
        adversarial._receipt_candidate(tmp_path, "receipt.json", "bad", artifact_label="fixture", index=1)

    outside = tmp_path.parent / "release-evidence-outside.json"
    outside.write_text("{}", encoding="utf-8")
    (tmp_path / "receipt-link.json").symlink_to(outside)
    with pytest.raises(adversarial.EvidenceValidationError, match="receipt escapes repo root"):
        adversarial._receipt_candidate(
            tmp_path, "receipt-link.json", _sha(b"{}"), artifact_label="fixture", index=1
        )

    receipt = tmp_path / "receipt.json"
    receipt.write_text("{}", encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="stale or tampered"):
        adversarial._receipt_candidate(
            tmp_path, "receipt.json", "a" * 64, artifact_label="fixture", index=1
        )

    record = {
        "finding": "F1",
        "source": "review.md",
        "expected": "consumer refuses input",
        "stimulus": "remove input",
        "disposition": "reproduced",
        "observed": "refused",
    }
    invalid_receipt = tmp_path / "invalid.json"
    invalid_receipt.write_text("not-json", encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="not valid JSON"):
        adversarial._validate_receipt_payload(
            invalid_receipt, record, artifact_label="fixture", index=1
        )
    invalid_receipt.write_text("[]", encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="schema is invalid"):
        adversarial._validate_receipt_payload(
            invalid_receipt, record, artifact_label="fixture", index=1
        )
    payload = {"schema": adversarial.RECEIPT_SCHEMA, **record}
    payload.update({"command": "pytest", "fixture": "fixture", "final_consumer": "consumer"})
    invalid_receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="does not bind expected"):
        adversarial._validate_receipt_payload(
            invalid_receipt,
            {**record, "expected": "different"},
            artifact_label="fixture",
            index=1,
        )
    payload["fixture"] = ""
    invalid_receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="missing fixture"):
        adversarial._validate_receipt_payload(
            invalid_receipt, record, artifact_label="fixture", index=1
        )
    payload["fixture"] = "fixture"
    payload["executed"] = False
    payload["final_consumer_observed"] = True
    invalid_receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="executed final-consumer"):
        adversarial._validate_receipt_payload(
            invalid_receipt, record, artifact_label="fixture", index=1
        )
    payload["executed"] = True
    payload["returncode"] = "0"
    invalid_receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(adversarial.EvidenceValidationError, match="returncode must be an integer"):
        adversarial._validate_receipt_payload(
            invalid_receipt, record, artifact_label="fixture", index=1
        )


def test_adversarial_evidence_rejects_record_and_source_shape_errors(tmp_path: Path) -> None:
    nonclaim = {
        "finding": "F1",
        "disposition": "unproven",
        "proof": "static scan only",
        "receipt": "receipt.json",
        "receipt sha256": "a" * 64,
    }
    with pytest.raises(adversarial.EvidenceValidationError, match="non-claim"):
        adversarial._validate_receipt(
            nonclaim, repo_root=None, artifact_label="fixture", index=1
        )
    static_claim = {**nonclaim, "disposition": "reproduced"}
    with pytest.raises(adversarial.EvidenceValidationError, match="executable fixture"):
        adversarial._validate_receipt(
            static_claim, repo_root=None, artifact_label="fixture", index=1
        )
    with pytest.raises(adversarial.EvidenceValidationError, match="needs a receipt"):
        adversarial._validate_receipt(
            {**static_claim, "proof": "executable fixture", "receipt": "none", "receipt sha256": "none"},
            repo_root=None,
            artifact_label="fixture",
            index=1,
        )

    for metadata, message in (
        (_evidence_metadata(**{"Evidence Digest": "bad"}), "Evidence Digest"),
        (_evidence_metadata(**{"Report Source SHA256": "bad"}), "Report Source SHA256"),
        (_evidence_metadata(**{"Report Source": "../report.json"}), "Report Source"),
        (_evidence_metadata(**{"Reported Findings": "not-an-int"}), "Reported Findings"),
        (_evidence_metadata(**{"Reported Findings": "-1"}), "cannot be negative"),
        (_evidence_metadata(**{"Report Identity": "review:fixture#sha256:" + "b" * 64}), "equal"),
    ):
        with pytest.raises(adversarial.EvidenceValidationError, match=message):
            adversarial._metadata(_evidence_text(_valid_record(), metadata), "fixture")
    with pytest.raises(adversarial.EvidenceValidationError, match="missing"):
        adversarial._metadata(
            _evidence_text(_valid_record(), "- Report Identity: review:fixture#sha256:" + "a" * 64),
            "fixture",
        )

    valid = _valid_record()
    with pytest.raises(adversarial.EvidenceValidationError, match="does not match"):
        adversarial._records(
            _evidence_text(valid), "fixture", 2, repo_root=None
        )
    for record, message in (
        (_valid_record(disposition="unknown"), "unknown disposition"),
        (_valid_record(proof="unknown"), "unknown proof"),
        (_valid_record(disposition="reproduced", proof="executable fixture", handoff="debug.md", next_move="none"), "next move"),
        (_valid_record(finding="F1") + "\n" + _valid_record(finding="F1"), "unique"),
    ):
        with pytest.raises(adversarial.EvidenceValidationError, match=message):
            adversarial._records(
                _evidence_text(record), "fixture", 1 if "\n" not in record else 2, repo_root=None
            )
    with pytest.raises(adversarial.EvidenceValidationError, match="dispositioned IDs"):
        adversarial._validate_coverage(
            {"Dispositioned Findings": "F2", "Missing Findings": "none"}, ["F1"], 1, "fixture"
        )
    with pytest.raises(adversarial.EvidenceValidationError, match="both dispositioned and missing"):
        adversarial._validate_coverage(
            {"Dispositioned Findings": "F1", "Missing Findings": "F1"}, ["F1"], 1, "fixture"
        )
    with pytest.raises(adversarial.EvidenceValidationError, match="escapes repo root"):
        adversarial._validate_source_binding(
            {"Report Source": "../outside", "Report Source SHA256": "a" * 64},
            dispositions=[], repo_root=tmp_path, artifact_label="fixture"
        )
    with pytest.raises(adversarial.EvidenceValidationError, match="does not exist"):
        adversarial._validate_source_binding(
            {"Report Source": "missing.json", "Report Source SHA256": "a" * 64},
            dispositions=[], repo_root=tmp_path, artifact_label="fixture"
        )
    adversarial.validate_or_raise("plain", artifact_label="fixture")
    with pytest.raises(RuntimeError, match="evidence-led"):
        adversarial.validate_for_artifact(
            "## Evidence Disposition", artifact_label="fixture", error_cls=RuntimeError
        )


def test_capability_resolver_admission_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]", encoding="utf-8")
    assert catalog_resolver._manifest_version(manifest) is None
    assert catalog_resolver._manifest_error(manifest) == "manifest must contain an object"
    manifest.write_text("{}", encoding="utf-8")
    assert catalog_resolver._manifest_error(manifest) == "manifest has no readable version"
    assert catalog_resolver._manifest_observation(manifest) == (
        True, None, "manifest has no readable version"
    )

    unsupported = catalog_resolver._package_expectation(
        skill_id="impl", marketplace="other", plugin="foreign"
    )
    assert unsupported["reason_code"] == "unsupported-package-expectation"

    owner = tmp_path / "owner"
    monkeypatch.setattr(catalog_resolver, "_owner_root", lambda: owner)
    (owner / "skills/public/impl").mkdir(parents=True)
    (owner / "skills/public/impl/SKILL.md").write_text("skill", encoding="utf-8")
    assert catalog_resolver._package_expectation(
        skill_id="impl", marketplace="local", plugin="charness"
    )["reason_code"] == "package-version-unavailable"
    (owner / ".codex-plugin").mkdir(parents=True)
    (owner / ".codex-plugin/plugin.json").write_text('{"version":"1"}', encoding="utf-8")
    (owner / "plugins/charness/.codex-plugin").mkdir(parents=True)
    (owner / "plugins/charness/.codex-plugin/plugin.json").write_text('{"version":"2"}', encoding="utf-8")
    assert catalog_resolver._package_expectation(
        skill_id="impl", marketplace="local", plugin="charness"
    )["reason_code"] == "package-version-mismatch"
    (owner / "plugins/charness/skills/impl").mkdir(parents=True)
    (owner / "plugins/charness/skills/impl/SKILL.md").write_text("different", encoding="utf-8")
    (owner / "plugins/charness/.codex-plugin/plugin.json").write_text('{"version":"1"}', encoding="utf-8")
    parity = catalog_resolver._package_expectation(
        skill_id="impl", marketplace="local", plugin="charness"
    )
    assert parity["reason_code"] == "source-plugin-parity-mismatch"

    assert catalog_resolver._candidate_version(Path("/SKILL.md"), "codex-versioned-cache") is None
    assert catalog_resolver._candidate_version(Path("/"), "codex-versioned-cache") is None
    (owner / ".codex-plugin/plugin.json").write_text('{"version":"1"}', encoding="utf-8")
    manifest_calls: list[Path] = []
    real_manifest_version = catalog_resolver._manifest_version

    def delayed_manifest_version(path: Path) -> str | None:
        manifest_calls.append(path)
        return None if len(manifest_calls) <= 12 else real_manifest_version(path)

    monkeypatch.setattr(catalog_resolver, "_manifest_version", delayed_manifest_version)
    assert catalog_resolver._candidate_version(
        owner / "skills/public/impl/SKILL.md", "repo-public-skill"
    ) == "1"
    monkeypatch.setattr(
        catalog_resolver,
        "_package_expectation",
        lambda **_kwargs: {"status": "mismatch", "reason_code": "package-version-mismatch"},
    )
    mismatch = catalog_resolver.resolve_skill_path(
        skill_id="impl", repo_root=tmp_path / "repo", home=tmp_path / "home",
        codex_home=tmp_path / "codex", reported_path=None,
    )
    assert mismatch["status"] == "mismatch" and mismatch["reason_code"] == "package-version-mismatch"

    candidate = tmp_path / "candidate.md"
    candidate.write_text("skill", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def raise_for_candidate(path: Path) -> bytes:
        if path == candidate:
            raise OSError("candidate vanished")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", raise_for_candidate)
    record = catalog_resolver._candidate_record(
        "reported", candidate, {"status": "ready", "version": "1", "skill_sha256": "a" * 64}
    )
    assert record["exists"] is False
    monkeypatch.setattr(Path, "read_bytes", original_read_bytes)
    unavailable = catalog_resolver._candidate_record(
        "reported", candidate, {"status": "unavailable", "reason_code": "no-expectation"}
    )
    assert unavailable["mismatch"] == "no-expectation"

    monkeypatch.setattr(
        catalog_resolver,
        "_package_expectation",
        lambda **_kwargs: {"status": "ready", "version": "1", "skill_sha256": "a" * 64},
    )
    missing = catalog_resolver.resolve_skill_path(
        skill_id="missing", repo_root=tmp_path / "repo", home=tmp_path / "home",
        codex_home=tmp_path / "codex", reported_path=None,
    )
    assert missing["status"] == "missing" and missing["reason_code"] == "skill-missing"


def test_critique_substrate_refusals_and_cli_refusal(tmp_path: Path) -> None:
    assert critique_packet.substrate_refusal(
        substrate_mode=critique_packet.SUBSTRATE_WORKING_TREE, changed_ref="HEAD"
    )["reason_code"] == "substrate-ref-mismatch"
    assert critique_packet.substrate_refusal(
        substrate_mode=critique_packet.SUBSTRATE_COMMITTED_REF, changed_ref=None
    )["reason_code"] == "substrate-ref-missing"
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "prepare_packet.py",
                "--repo-root",
                str(tmp_path),
                "--substrate-mode",
                "working-tree",
                "--changed-ref",
                "HEAD",
            ],
        )
        assert critique_runner.main() == 1
    finally:
        monkeypatch.undo()


def test_staged_helper_absence_is_an_explicit_empty_gate(tmp_path: Path) -> None:
    assert staged_helpers.provenance_contract_self_test_gate(tmp_path) == []


def test_reviewed_identity_substrate_and_deletion_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(reviewed_identity.ReviewedInputError) as invalid_mode:
        reviewed_identity._substrate_mode(None, "invalid")
    assert invalid_mode.value.code == "invalid-substrate-mode"
    with pytest.raises(reviewed_identity.ReviewedInputError) as mismatch_mode:
        reviewed_identity._substrate_mode("HEAD", reviewed_identity.SUBSTRATE_WORKING_TREE)
    assert mismatch_mode.value.code == "substrate-ref-mismatch"
    with pytest.raises(reviewed_identity.ReviewedInputError) as missing_mode:
        reviewed_identity._substrate_mode(None, reviewed_identity.SUBSTRATE_COMMITTED_REF)
    assert missing_mode.value.code == "substrate-ref-missing"

    monkeypatch.setattr(
        reviewed_identity,
        "_auto_paths",
        lambda *_args: (_ for _ in ()).throw(ValueError("changed ref unavailable")),
    )
    with pytest.raises(reviewed_identity.ReviewedInputError) as unavailable:
        reviewed_identity._review_paths(
            tmp_path,
            ["file.txt"],
            "HEAD",
            reviewed_identity.SUBSTRATE_COMMITTED_REF,
            None,
            None,
        )
    assert unavailable.value.code == "changed-ref-unavailable"

    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(tmp_path / "deletion", {"gone.txt": "before\n"})
    (repo / "gone.txt").unlink()
    identity = reviewed_identity.build_reviewed_input_identity(repo_root=repo, reviewed_paths=["gone.txt"])
    assert identity["reviewed_content"][0]["content_sha256"]

    empty_repo = install_committed_repo(tmp_path / "empty", {"seed.txt": "seed\n"})
    with pytest.raises(reviewed_identity.ReviewedInputError) as null_hash:
        reviewed_identity.build_reviewed_input_identity(repo_root=empty_repo, reviewed_paths=["missing.txt"])
    assert null_hash.value.code == "null-content-hash"


def test_reviewed_identity_reconstruction_and_packet_binding_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = {
        "status": "captured",
        "algorithm": reviewed_identity.ALGORITHM,
        "reviewed_paths": ["input.json"],
        "mode": reviewed_identity.SUBSTRATE_WORKING_TREE,
        "substrate_mode": reviewed_identity.SUBSTRATE_WORKING_TREE,
        "changed_ref": None,
        "identity_sha256": "a" * 64,
    }
    assert reviewed_verification.verify_reviewed_input_identity(
        tmp_path, {**base, "mode": "bad", "substrate_mode": "bad"}
    )[0] is False
    assert reviewed_verification.verify_reviewed_input_identity(
        tmp_path, {**base, "mode": reviewed_identity.SUBSTRATE_COMMITTED_REF, "substrate_mode": reviewed_identity.SUBSTRATE_COMMITTED_REF}
    )[1].startswith("reviewed input identity substrate mode")

    monkeypatch.setattr(
        reviewed_identity,
        "build_reviewed_input_identity",
        lambda **_kwargs: (_ for _ in ()).throw(reviewed_identity.ReviewedInputError("fixture", "fixture error")),
    )
    assert reviewed_verification.verify_reviewed_input_identity(tmp_path, base) == (False, "fixture: fixture error")
    monkeypatch.setattr(
        reviewed_identity,
        "build_reviewed_input_identity",
        lambda **_kwargs: {
            "reviewed_content": [{"content_sha256": "bad"}],
            "reviewed_patch_sha256": "a" * 64,
            "staged_patch_sha256": "a" * 64,
            "unstaged_patch_sha256": "a" * 64,
            "identity_sha256": "a" * 64,
        },
    )
    assert reviewed_verification.verify_reviewed_input_identity(tmp_path, base)[1].endswith("invalid content hash")
    monkeypatch.setattr(
        reviewed_identity,
        "build_reviewed_input_identity",
        lambda **_kwargs: {
            "reviewed_content": [{"content_sha256": "a" * 64}],
            "reviewed_patch_sha256": "bad",
            "staged_patch_sha256": "a" * 64,
            "unstaged_patch_sha256": "a" * 64,
            "identity_sha256": "a" * 64,
        },
    )
    assert reviewed_verification.verify_reviewed_input_identity(tmp_path, base)[1].endswith("reviewed_patch_sha256")
    monkeypatch.undo()

    packet = tmp_path / "packet.json"
    packet_payload = {
        "kind": "fixture",
        "substrate_mode": reviewed_identity.SUBSTRATE_WORKING_TREE,
        "changed_ref": None,
        "reviewed_input_identity": {
            "identity_sha256": "bad",
            "substrate_mode": reviewed_identity.SUBSTRATE_WORKING_TREE,
            "changed_ref": None,
        },
    }
    packet.write_text(json.dumps(packet_payload), encoding="utf-8")
    packet_sha = _sha(packet.read_bytes())
    symlink = tmp_path / "packet-link.json"
    symlink.symlink_to(packet)
    assert reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet-link.json",
        packet_sha256=packet_sha,
        identity_sha256="bad",
        expected_kind="fixture",
        check_current=False,
    )[1] == "reviewed packet path must not be a symlink"
    outside = tmp_path.parent / "packet-outside"
    outside.mkdir()
    (outside / "packet.json").write_bytes(packet.read_bytes())
    (tmp_path / "packet-dir").symlink_to(outside, target_is_directory=True)
    assert reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet-dir/packet.json",
        packet_sha256=packet_sha,
        identity_sha256="bad",
        expected_kind="fixture",
        check_current=False,
    )[1] == "reviewed packet path resolves outside repo root"
    assert reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet.json",
        packet_sha256=packet_sha,
        identity_sha256="bad",
        expected_kind="fixture",
        check_current=False,
    )[1] == "identity sha256 is null or invalid"

    committed_packet = dict(packet_payload, substrate_mode=reviewed_identity.SUBSTRATE_COMMITTED_REF, changed_ref="HEAD")
    committed_packet["reviewed_input_identity"] = dict(packet_payload["reviewed_input_identity"], substrate_mode=reviewed_identity.SUBSTRATE_COMMITTED_REF, changed_ref="HEAD", identity_sha256="a" * 64)
    packet.write_text(json.dumps(committed_packet), encoding="utf-8")
    committed_sha = _sha(packet.read_bytes())
    mismatch = reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet.json",
        packet_sha256=committed_sha,
        identity_sha256="a" * 64,
        expected_kind="fixture",
        check_current=False,
    )
    assert mismatch[1] != "packet and reviewed input identity substrate modes do not match"
    committed_packet["substrate_mode"] = reviewed_identity.SUBSTRATE_WORKING_TREE
    packet.write_text(json.dumps(committed_packet), encoding="utf-8")
    assert reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet.json",
        packet_sha256=_sha(packet.read_bytes()),
        identity_sha256="a" * 64,
        expected_kind="fixture",
        check_current=False,
    )[1] == "packet and reviewed input identity substrate modes do not match"
    committed_packet["substrate_mode"] = reviewed_identity.SUBSTRATE_COMMITTED_REF
    committed_packet["reviewed_input_identity"]["changed_ref"] = "OTHER"
    packet.write_text(json.dumps(committed_packet), encoding="utf-8")
    assert reviewed_verification.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="packet.json",
        packet_sha256=_sha(packet.read_bytes()),
        identity_sha256="a" * 64,
        expected_kind="fixture",
        check_current=False,
    )[1] == "packet and reviewed input identity changed_ref values do not match"
