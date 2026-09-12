"""Missing prior evidence must remain a refusal, never an implicit fresh approval."""
from __future__ import annotations

import json

import pytest

from scripts.review.reviewed_input_identity import build_reviewed_input_identity
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.test_review_followup_failures import FOLLOWUP, PROVENANCE, _prior_review


@pytest.mark.parametrize("loader", ["_load_context_module", "_load_selection_module", "_load_provenance_module", "_load_identity_verification"])
def test_followup_refuses_unavailable_helper_loaders(monkeypatch, loader):
    monkeypatch.setattr(FOLLOWUP.importlib.util, "spec_from_file_location", lambda *a: None)
    with pytest.raises(ImportError):
        getattr(FOLLOWUP, loader)()


def test_prior_packet_absence_is_distinct_from_wrong_kind(tmp_path):
    source = tmp_path / "result.json"
    assert FOLLOWUP._packet_for_prior(tmp_path, source, {}) == (None, None)
    assert FOLLOWUP._packet_for_prior(tmp_path, source, {"packet_path": "absent.json"}) == (None, None)
    (tmp_path / "packet.json").write_text("{}")
    with pytest.raises(FOLLOWUP.FollowupError, match="wrong kind"):
        FOLLOWUP._packet_for_prior(tmp_path, source, {"packet_path": "packet.json"})


@pytest.mark.parametrize("fault,code", [
    ("missing", "prior-semantic-input-unavailable"), ("paths", "prior-semantic-input-mismatch"),
    ("entry", "prior-semantic-input-invalid"), ("carrier", "prior-semantic-input-unavailable"),
    ("hash", "prior-semantic-input-tampered"),
])
def test_prior_semantic_evidence_refuses_incomplete_or_tampered_bytes(tmp_path, fault, code):
    root = tmp_path / "semantic-input"
    root.mkdir()
    carrier = root / "content.bin"
    carrier.write_text("source")
    entry = {"path": "a.py", "carrier_path": "content.bin", "content_sha256": "a"}
    entries = [entry]
    if fault == "paths":
        entries = []
    elif fault == "entry":
        entries.insert(0, None)
    elif fault == "carrier":
        carrier.unlink()
    elif fault == "hash":
        entry["content_sha256"] = "b"
    if fault != "missing":
        (root / "manifest.json").write_text(json.dumps({"entries": entries}))
    with pytest.raises(FOLLOWUP.FollowupError) as caught:
        FOLLOWUP._verify_prior_semantic_carriers(root=tmp_path, source=tmp_path / "result.json",
            identity={"reviewed_content": [{"path": "a.py", "content_sha256": "a"}]})
    assert caught.value.code == code


@pytest.mark.parametrize("fault,code", [("identity", "prior-identity-mismatch"), ("status", "prior-identity-unavailable"),
                                        ("packet_verifier", "prior-packet-invalid"), ("identity_verifier", "prior-identity-invalid")])
def test_prior_packet_binding_refuses_failed_identity_checks(tmp_path, monkeypatch, fault, code):
    path = tmp_path / "packet.json"
    path.write_text("{}")
    identity = {"status": "captured", "identity_sha256": "i"}
    if fault == "identity":
        identity["identity_sha256"] = "other"
    if fault == "status":
        identity["status"] = "unavailable"
    monkeypatch.setattr(FOLLOWUP.IDENTITY_VERIFICATION, "verify_packet_binding", lambda **k: (fault != "packet_verifier", "bad packet"))
    monkeypatch.setattr(FOLLOWUP.IDENTITY_VERIFICATION, "verify_recorded_reviewed_input_identity", lambda *a: (False, "bad identity"))
    with pytest.raises(FOLLOWUP.FollowupError) as caught:
        FOLLOWUP._verify_prior_packet_binding(root=tmp_path, source=tmp_path / "result.json",
            raw={"packet_sha256": FOLLOWUP._sha256(path), "reviewed_input_identity_sha256": "i"}, plan={},
            packet={"reviewed_input_identity": identity}, packet_path=path)
    assert caught.value.code == code


def test_retained_source_rejects_parent_directory_symlink_escape(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "result.json").write_text("{}")
    (root / "linked").symlink_to(outside, target_is_directory=True)
    assert PROVENANCE._retained_source(root, "linked/result.json") is None


def test_followup_context_reports_omitted_prior_findings(tmp_path, monkeypatch):
    repo = install_committed_repo(tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"})
    source, _ = _prior_review(repo)
    (repo / "a.py").write_text("VALUE = 3\n")
    monkeypatch.setattr(FOLLOWUP, "_compact_findings", lambda findings: ([], ["omitted-1"], True))
    paths, context = FOLLOWUP.build_followup(repo_root=repo, source_value=source, explicit_paths=None,
                                            build_identity=build_reviewed_input_identity)
    assert paths == ["a.py"]
    assert context["context_truncated"] is True
    assert context["omitted_finding_ids"] == ["omitted-1"]
