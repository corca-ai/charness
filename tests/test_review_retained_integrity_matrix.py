"""Corrupt one retained or promoted boundary at a time; never upgrade it to approval."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tests.test_review_recovery_failures import (
    RECOVERY_INPUTS,
    SUPPORT,
    _retained_fixture,
)


@pytest.mark.parametrize("fault,reason", [
    ("attempt", "attempt_id does not match"),
    ("owner", "owner receipt is missing"),
    ("bytes", "report bytes do not match"),
    ("receipt", "worker receipt is missing"),
    ("receipt_identity", "worker receipt attempt_id"),
    ("ledger", "ledger has no requested"),
    ("ledger_identity", "ledger packet_identity"),
    ("packet_bytes", "packet bytes do not match"),
    ("packet", "packet is not a mapping"),
    ("verifier", "canonical retained packet verification failed"),
    ("identity", "packet has no reviewed input identity"),
    ("identity_hash", "packet identity does not match"),
    ("parent", "parent receipt identity does not match"),
    ("manifest_missing", "manifest is missing"),
    ("manifest_json", "manifest is unreadable"),
    ("entry", "malformed entry"),
    ("carrier_missing", "entry has no carrier path"),
    ("carrier_escape", "carrier escaped its run"),
    ("carrier_hash", "carrier manifest does not match"),
    ("carrier_bytes", "carrier bytes do not match"),
])
def test_retained_input_refuses_each_broken_binding(tmp_path, monkeypatch, fault, reason):
    f = _retained_fixture(tmp_path)
    read = SUPPORT.load_mapping
    manifest = f["run_dir"] / "semantic-input/manifest.json"
    packet_payload = read(f["packet"])
    owner_payload = read(f["owner_receipt"])
    overrides = {}
    unavailable = {"owner": f["owner_receipt"], "receipt": f["paths"]["receipt"], "packet": f["packet"]}
    if fault in unavailable:
        overrides[unavailable[fault]] = None
    elif fault == "attempt":
        f["attempt"] = "other"
    elif fault == "bytes":
        f["paths"]["report"].write_text("changed")
    elif fault == "receipt_identity":
        overrides[f["paths"]["receipt"]] = {**read(f["paths"]["receipt"]), "attempt_id": "other"}
    elif fault == "ledger":
        overrides[f["paths"]["ledger"]] = {"attempts": []}
    elif fault == "ledger_identity":
        ledger = read(f["paths"]["ledger"])
        ledger["attempts"][0]["packet_identity"] = "other"
        overrides[f["paths"]["ledger"]] = ledger
    elif fault == "packet_bytes":
        f["packet"].write_text("changed")
    elif fault == "verifier":
        def refuse(*args):
            raise ValueError("canonical verifier rejected bytes")
        f["packet_module"] = SimpleNamespace(read_packet=refuse)
    elif fault in {"identity", "identity_hash"}:
        packet_payload["reviewed_input_identity"] = None if fault == "identity" else {"identity_sha256": "other"}
        overrides[f["packet"]] = packet_payload
    elif fault == "parent":
        f["plan"]["scope"] = "altered unsigned plan"
    elif fault == "manifest_missing":
        manifest.unlink()
    elif fault == "manifest_json":
        manifest.write_text("{")
    elif fault == "carrier_bytes":
        f["identity_verification"] = SimpleNamespace(verify_semantic_carrier_entry=lambda *args: (False, "hash mismatch"))
    else:
        _corrupt_manifest(manifest, fault)
    monkeypatch.setattr(SUPPORT, "load_mapping", lambda p: overrides[p] if p in overrides else read(p))
    result = RECOVERY_INPUTS.validate_retained_inputs(
        tmp_path, f["plan"], f["packet"], f["paths"], attempt=f["attempt"],
        owner_receipt=f["owner_receipt"], package=f["package"], support=SUPPORT,
        packet_module=f["packet_module"], identity_verification=f["identity_verification"],
    )
    assert result["ok"] is False
    assert reason in result["reason"]
    assert read(f["owner_receipt"]) == owner_payload


def _corrupt_manifest(manifest, fault):
    payload = json.loads(manifest.read_text())
    if fault == "entry":
        payload["entries"].append(None)
    elif fault == "carrier_missing":
        payload["entries"][0].pop("carrier_path")
    elif fault == "carrier_escape":
        payload["entries"][0]["carrier_path"] = "packet.json"
    elif fault == "carrier_hash":
        payload["entries"][0]["content_sha256"] = "other"
    SUPPORT.write_json(manifest, payload)


@pytest.mark.parametrize("fault,reason", [
    ("missing", "expose every durable carrier"),
    ("validator", "worker chain validation failed"),
    ("manifest", "no complete file-integrity map"),
    ("keys", "keys do not match"),
    ("descriptor", "descriptor is malformed"),
    ("path", "path is invalid"),
    ("lifecycle", "does not match the reconstructed"),
    ("binding", "identity does not match"),
    ("approval", "disagrees with the final lifecycle"),
])
def test_promoted_chain_refuses_each_broken_binding(tmp_path, fault, reason):
    paths = {}
    final = {"approval_eligible": False}
    for key in ("report", "receipt", "ledger", "output", "summary"):
        paths[key] = key + ".json"
        SUPPORT.write_json(tmp_path / paths[key], final if key == "summary" else {})
    integrity = {
        k: {"path": p, "bytes": (tmp_path / p).stat().st_size, "sha256": SUPPORT.sha256(tmp_path / p)}
        for k, p in paths.items()
    }
    manifest = {"files": dict(paths), "file_integrity": integrity, "approval_eligible": False}
    def validate(**kwargs):
        if fault == "validator":
            raise ValueError("worker receipt mismatch")
    if fault == "missing":
        paths.pop("report")
    elif fault == "manifest":
        manifest = {}
    elif fault == "keys":
        integrity.pop("report")
    elif fault == "descriptor":
        integrity["report"] = None
    elif fault == "path":
        manifest["files"]["report"] = "../escaped.json"
    elif fault == "lifecycle":
        SUPPORT.write_json(tmp_path / paths["summary"], {"approval_eligible": True})
        integrity["summary"] = {"path": paths["summary"], "bytes": (tmp_path / paths["summary"]).stat().st_size,
                                "sha256": SUPPORT.sha256(tmp_path / paths["summary"])}
    elif fault == "approval":
        manifest["approval_eligible"] = True
    SUPPORT.write_json(tmp_path / "attempt-manifest.json", manifest)
    result = RECOVERY_INPUTS.validate_promoted_chain(
        tmp_path, paths, final, {"attempt_id": "a"}, support=SUPPORT,
        carrier_validation=SimpleNamespace(validate_delivered_worker_report=validate),
        promotion=SimpleNamespace(identity_binding=lambda *args: {"matches": fault != "binding"}),
    )
    assert result["ok"] is False
    assert reason in result["reason"]
    assert (tmp_path / "attempt-manifest.json").exists()
