"""Retry joins preserve partial evidence and refuse altered durable metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from scripts.worktree import worktree_cleanup_lib
from tests.charness_cli.worktree_fixtures import copy_worktree_seed
from tests.quality_gates.seeding_support import git as fixture_git
from tests.script_main import load_script_module
from tests.test_review_promotion_failures import (
    CARRIER,
    HOLD_OUT,
    PROMOTION,
    RUN_REVIEW,
    SCRIPT_ROOT,
    STORAGE,
    SUPPORT,
)


@pytest.fixture(autouse=True)
def stable_support_identity(monkeypatch):
    monkeypatch.setattr(PROMOTION, "_support", lambda: SUPPORT)
    monkeypatch.setattr(PROMOTION, "SUPPORT", SUPPORT)
    monkeypatch.setattr(STORAGE, "_support", lambda: SUPPORT)


def _closure_files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.mark.boundary_contract(
    reason="A real Git linked worktree and cleanup are the lifetime boundary under review."
)
def test_linked_review_closure_survives_worktree_cleanup(tmp_path: Path) -> None:
    primary = copy_worktree_seed(tmp_path, "primary")
    (primary / ".gitignore").write_text("charness-artifacts/critique/\n", encoding="utf-8")
    fixture_git(primary, "add", ".gitignore")
    fixture_git(primary, "commit", "-m", "ignore critique runtime")
    linked = tmp_path / "linked"
    fixture_git(primary, "worktree", "add", "-b", "review-closure", str(linked))

    packet_relative = Path("charness-artifacts/critique/review-closure-packet.json")
    packet = linked / packet_relative
    packet.parent.mkdir(parents=True)
    content = b"reviewed exact bytes\n"
    content_sha = hashlib.sha256(content).hexdigest()
    packet_payload = {
        "kind": "charness.critique_prepare_packet",
        "reviewed_input_identity": {
            "identity_sha256": "a" * 64,
            "reviewed_content": [
                {"path": "reviewed.txt", "content_sha256": content_sha}
            ],
        },
    }
    packet.write_text(json.dumps(packet_payload, sort_keys=True) + "\n", encoding="utf-8")
    attempt_relative = PROMOTION.DURABLE_WORKER_REPORTS / "review-closure"
    attempt = linked / attempt_relative
    semantic = attempt / "semantic-input"
    semantic.mkdir(parents=True)
    (attempt / "result.json").write_bytes(b'{"verdict":"pass"}\n')
    (semantic / "0000-content.bin").write_bytes(content)
    semantic_manifest = {
        "entries": [
            {
                "path": "reviewed.txt",
                "carrier_path": "charness-artifacts/critique/workers/review-closure/semantic-input/0000-content.bin",
                "content_sha256": content_sha,
            }
        ]
    }
    (semantic / "manifest.json").write_text(
        json.dumps(semantic_manifest, sort_keys=True) + "\n", encoding="utf-8"
    )
    (attempt / "attempt-manifest.json").write_bytes(b'{"approval_eligible":true}\n')
    expected_attempt = _closure_files(attempt)

    first = PROMOTION.PRIMARY_PROMOTION.promote_finalized_closure(
        SUPPORT,
        STORAGE,
        PROMOTION.DURABLE_WORKER_REPORTS,
        linked,
        "review-closure",
        {"packet": packet},
    )
    second = PROMOTION.PRIMARY_PROMOTION.promote_finalized_closure(
        SUPPORT,
        STORAGE,
        PROMOTION.DURABLE_WORKER_REPORTS,
        linked,
        "review-closure",
        {"packet": packet},
    )

    assert first["status"] == second["status"] == "promoted-to-primary"
    cleanup = worktree_cleanup_lib.run_cleanup(
        primary, target_path=linked, yes=True
    )
    assert cleanup["status"] == worktree_cleanup_lib.PASS, cleanup
    assert not linked.exists()
    preserved_attempt = primary / attempt_relative
    assert json.loads((primary / packet_relative).read_text()) == packet_payload
    assert _closure_files(preserved_attempt) == expected_attempt
    preserved_semantic = json.loads(
        (preserved_attempt / "semantic-input/manifest.json").read_text()
    )
    preserved_content = preserved_attempt / "semantic-input/0000-content.bin"
    assert hashlib.sha256(preserved_content.read_bytes()).hexdigest() == (
        preserved_semantic["entries"][0]["content_sha256"]
    )


@pytest.mark.parametrize("fault", ["directory", "partial_symlink", "partial_json", "partial_changed", "manifest_existing", "manifest_json", "manifest_identity"])
def test_promotion_refuses_ambiguous_retry_destinations(tmp_path, monkeypatch, fault):
    dest = tmp_path / PROMOTION.DURABLE_WORKER_REPORTS / "a"
    dest.parent.mkdir(parents=True)
    source = tmp_path / "runner.stdout"
    source.write_text("retained review")
    candidate = {"kind": "charness.bounded_review.v1", "verdict": "defer"}
    monkeypatch.setattr(STORAGE, "extract_partial_review", lambda *a, **k: (candidate, source, "valid") if fault.startswith("partial") else None)
    if fault == "directory":
        dest.symlink_to(tmp_path, target_is_directory=True)
    else:
        dest.mkdir()
        if fault == "partial_symlink":
            (dest / "partial-result.json").symlink_to(source)
        elif fault == "partial_json":
            (dest / "partial-result.json").write_text("{")
        elif fault == "partial_changed":
            SUPPORT.write_json(dest / "partial-result.json", {"verdict": "pass"})
        elif fault == "manifest_json":
            (dest / "attempt-manifest.json").write_text("{")
        elif fault.startswith("manifest"):
            SUPPORT.write_json(dest / "attempt-manifest.json", {"attempt_id": "other"})
    with pytest.raises(SUPPORT.RunReviewError, match="durable"):
        PROMOTION.promote_attempt_metadata(tmp_path, "a", {}, None, finalize=fault != "manifest_existing")
    assert source.read_text() == "retained review"


def test_retry_keeps_partial_receipt_enrichment_and_existing_partial_result(tmp_path, monkeypatch):
    receipt = tmp_path / "receipt.json"
    SUPPORT.write_json(receipt, {})
    source = tmp_path / "runner.stdout"
    source.write_text("retained review")
    candidate = {"kind": "charness.bounded_review.v1", "verdict": "defer"}
    monkeypatch.setattr(STORAGE, "extract_partial_review", lambda *a, **k: (candidate, source, "valid"))
    paths = {"receipt": receipt}
    first = PROMOTION.promote_attempt_metadata(tmp_path, "a", paths, None)
    enriched = SUPPORT.load_mapping(tmp_path / first["receipt.json"])
    assert enriched["retained_partial_output"]["approval_eligible"] is False
    second = PROMOTION.promote_attempt_metadata(tmp_path, "a", paths, None, finalize=True)
    assert SUPPORT.load_mapping(tmp_path / second["receipt.json"]) == enriched
    monkeypatch.setattr(STORAGE, "extract_partial_review", lambda *a, **k: None)
    third = PROMOTION.promote_attempt_metadata(tmp_path, "a", paths, None, finalize=True)
    manifest = SUPPORT.load_mapping(tmp_path / third["attempt-manifest.json"])
    assert manifest["partial_result"] == enriched["retained_partial_output"]
    assert manifest["approval_eligible"] is False


def test_retry_of_unparseable_unchanged_receipt_never_invents_approval(tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_bytes(b"\xff")
    first = PROMOTION.promote_attempt_metadata(tmp_path, "a", {"receipt": receipt}, None)
    second = PROMOTION.promote_attempt_metadata(tmp_path, "a", {"receipt": receipt}, None, finalize=True)
    assert (tmp_path / second["receipt.json"]).read_bytes() == b"\xff"
    assert SUPPORT.load_mapping(tmp_path / first["attempt-manifest.json"])["approval_eligible"] is False


def test_report_load_keeps_failed_report_if_partial_manifest_is_unreadable(tmp_path, monkeypatch):
    report = tmp_path / "report.yaml"
    SUPPORT.write_yaml(report, {"approval_eligible": False})
    manifest = tmp_path / "attempt-manifest.json"
    manifest.write_text("{")
    monkeypatch.setattr(PROMOTION, "promote_attempt_metadata", lambda *a, **k: {
        "worker-report.yaml": report.name, "attempt-manifest.json": manifest.name,
    })
    result = PROMOTION.load_and_promote_report(tmp_path, "a", {"report": report}, {"paths": {"report": report.name}})
    assert result == {"approval_eligible": False}


def test_loader_failure_restores_previous_support_identity(monkeypatch):
    import sys
    previous = ModuleType("previous")
    monkeypatch.setitem(sys.modules, "charness_run_review_support", previous)
    class Broken:
        def create_module(self, spec):
            return None
        def exec_module(self, module):
            raise RuntimeError("load failed")
    spec = RUN_REVIEW.importlib.util.spec_from_loader("charness_run_review_support", Broken())
    monkeypatch.setattr(RUN_REVIEW.importlib.util, "spec_from_file_location", lambda *a: spec)
    with pytest.raises(RuntimeError, match="load failed"):
        RUN_REVIEW._load_support()
    assert sys.modules["charness_run_review_support"] is previous


@pytest.mark.parametrize("fault", ["missing_contract", "loader", "unreadable_log", "input_identity", "parent_identity", "window"])
def test_partial_log_scan_preserves_only_readable_identity_bound_output(tmp_path, monkeypatch, fault):
    if fault in {"missing_contract", "loader"}:
        monkeypatch.setattr(STORAGE, "_REVIEWER_CONTRACT", None)
        if fault == "missing_contract":
            monkeypatch.setattr(STORAGE, "__file__", str(tmp_path / "storage.py"))
        else:
            monkeypatch.setattr(STORAGE.importlib.util, "spec_from_file_location", lambda *a: None)
        with pytest.raises(ImportError, match="contract"):
            STORAGE._bounded_result_shape({})
        return
    source = tmp_path / "stdout"
    candidate = {"kind": "charness.bounded_review.v1", "packet_sha256": "p", "reviewed_input_identity_sha256": "i", "parent_receipt_identity": "parent"}
    if fault == "input_identity":
        candidate["reviewed_input_identity_sha256"] = "other"
    elif fault == "parent_identity":
        candidate["parent_receipt_identity"] = "other"
    raw = json.dumps(candidate).encode()
    if fault == "window":
        monkeypatch.setattr(STORAGE, "PARTIAL_SCAN_LIMIT", 512)
        raw = raw + b" " * 2048 + raw
    source.write_bytes(raw)
    if fault == "unreadable_log":
        read = Path.read_bytes
        def fail(path):
            if path == source:
                raise OSError("unreadable")
            return read(path)
        monkeypatch.setattr(Path, "read_bytes", fail)
    monkeypatch.setattr(STORAGE, "_bounded_result_shape", lambda value: "valid")
    diagnostics = {}
    result = STORAGE.extract_partial_review({"runner_stdout": source}, None, diagnostics,
        expected_identities={"packet_sha256": "p", "reviewed_input_identity_sha256": "i", "parent_receipt_identity": "parent"})
    assert (result is not None) is (fault == "window")
    if result:
        assert result[0] == candidate
        assert diagnostics["sources"][0]["windowed"] is True


@pytest.mark.parametrize("fault", ["summary_missing", "summary_changed", "manifest_missing", "manifest_changed"])
def test_finalizer_requires_readback_before_approval(tmp_path, monkeypatch, fault):
    run = tmp_path / "run"
    semantic = run / "semantic-input"
    semantic.mkdir(parents=True)
    (semantic / "nested").mkdir()
    (semantic / "linked").symlink_to(semantic, target_is_directory=True)
    summary = tmp_path / "summary.yaml"
    manifest = tmp_path / "attempt-manifest.json"
    SUPPORT.write_json(manifest, {"approval_eligible": False})
    real_load = SUPPORT.load_mapping
    manifest_reads = 0
    def load(path):
        nonlocal manifest_reads
        if path == summary:
            if fault == "summary_missing":
                return None
            if fault == "summary_changed":
                return {"approval_eligible": True}
        if path == manifest:
            manifest_reads += 1
            if fault == "manifest_missing":
                return None
            if fault == "manifest_changed" and manifest_reads > 1:
                return {"approval_eligible": True, "unexpected": True}
        return real_load(path)
    monkeypatch.setattr(SUPPORT, "load_mapping", load)
    promotion = SimpleNamespace(
        STORAGE=STORAGE, SOURCE_KEYS={}, LOG_SOURCE_KEYS={},
        promote_attempt_metadata=lambda *a, **k: {"lifecycle.yaml": summary.name, "attempt-manifest.json": manifest.name},
        refresh_manifest_integrity=lambda *a: {},
        approval_for=lambda *a, **k: (fault == "manifest_changed", {"matches": False}),
    )
    with pytest.raises(SUPPORT.RunReviewError, match="read back|read-back|does not match"):
        CARRIER.finalize_carrier(SUPPORT, promotion, tmp_path, "a", {"run_dir": run},
            {"paths": {}}, {"approval_eligible": False}, None)
    assert real_load(manifest)["approval_eligible"] is False


def test_semantic_promotion_skips_links_and_refuses_changed_bytes_during_mode_readback(tmp_path, monkeypatch):
    run = tmp_path / "run"
    source = run / "semantic-input"
    source.mkdir(parents=True)
    (source / "nested").mkdir()
    (source / "link").symlink_to(source, target_is_directory=True)
    payload = source / "content"
    payload.write_text("original")
    payload.chmod(0o400)
    clean = STORAGE.promote_semantic_inputs(tmp_path, {"run_dir": run}, tmp_path / "clean")
    assert set(clean) == {"semantic-input/content"}
    dest = tmp_path / "dest"
    def corrupt(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("corrupted")
        path.chmod(0o600)
    monkeypatch.setattr(STORAGE, "write_or_verify", corrupt)
    with pytest.raises(SUPPORT.RunReviewError, match="mode changed"):
        STORAGE.promote_semantic_inputs(tmp_path, {"run_dir": run}, dest)
    assert payload.read_text() == "original"


def test_support_refuses_missing_verifier_and_scratch_open_failure(tmp_path, monkeypatch):
    with pytest.raises(SUPPORT.RunReviewError, match="cannot locate"):
        SUPPORT.find_reviewed_input_verification(tmp_path)
    def fail_open():
        raise OSError("disk unavailable")
    monkeypatch.setattr(SUPPORT, "owned_scratch", lambda *a, **k: SimpleNamespace(open=fail_open))
    with pytest.raises(SUPPORT.RunReviewError, match="cannot open reviewer scratch"):
        SUPPORT.new_run_owner(tmp_path, "a")


def test_holdout_direct_import_recovers_missing_repo_search_path(monkeypatch):
    import builtins
    import sys
    root = str(SCRIPT_ROOT.parents[3])
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != root])
    original = builtins.__import__
    blocked = False
    def first_import(name, *args, **kwargs):
        nonlocal blocked
        if name == "scripts.runtime_scratch" and not blocked:
            blocked = True
            raise ImportError("direct layout")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", first_import)
    module = load_script_module("holdout_search_path_probe", Path(HOLD_OUT.__file__))
    assert module.owned_scratch is not None
    assert blocked and str(module._repo_root) == root
