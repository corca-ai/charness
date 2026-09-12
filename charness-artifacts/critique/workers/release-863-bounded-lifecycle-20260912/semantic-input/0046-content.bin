from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.runtime_scratch import (
    OWNER_RECEIPT_NAME,
    ScratchError,
    _repo_identity,
    gc_scratch_roots,
    inspect_scratch_roots,
    owned_scratch,
    recover_scratch_roots,
)


def test_foreign_repo_owner_is_never_gc_eligible(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    foreign = tmp_path / "foreign"
    subprocess.run(["git", "init", "-q", str(foreign)], check=True)
    owner = owned_scratch(repo, "foreign", run_id="retained", runtime_root_path=runtime)
    owner.open()
    owner.retain()
    owner.close()

    report = inspect_scratch_roots(foreign, runtime_root_path=runtime)
    item = report["roots"][0]
    assert item["repo_matches"] is False
    assert "repo-mismatch" in item["disposition"]
    gc = gc_scratch_roots(foreign, runtime_root_path=runtime, dry_run=False)
    assert gc["roots"][0]["disposition"].startswith("refuse-repo-mismatch")
    assert Path(item["path"]).exists()


def test_worktree_inventory_failure_is_a_safety_stop(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "inventory", run_id="failed", runtime_root_path=runtime)
    owner.open()
    owner.retain()
    owner.close()

    import scripts.runtime_scratch as core

    def fail(_repo):
        raise ScratchError("inventory unavailable")

    monkeypatch.setattr(core, "_registered_worktrees", fail)
    report = inspect_scratch_roots(repo, runtime_root_path=runtime)
    assert report["ok"] is False
    assert report["roots"][0]["disposition"].startswith("refuse-worktree-inventory-error")
    assert gc_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)["reclaimed_entries"] == 0


def test_expired_dead_owner_can_be_recovered_without_deleting_evidence(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "orphan", run_id="dead", runtime_root_path=runtime)
    path = owner.open()
    owner._close_lock()
    receipt = json.loads((path / OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))
    receipt.update({"pid": 0, "expires_at": "2020-01-01T00:00:00Z", "state": "active"})
    (path / OWNER_RECEIPT_NAME).write_text(json.dumps(receipt), encoding="utf-8")

    inspected = inspect_scratch_roots(repo, runtime_root_path=runtime)
    assert inspected["roots"][0]["orphaned"] is True
    preview = recover_scratch_roots(repo, runtime_root_path=runtime)
    assert preview["roots"][0]["disposition"] == "would-recover-orphan"
    recovered = recover_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)
    assert recovered["recovered"] == 1
    saved = json.loads((path / OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))
    assert saved["state"] == "failed"
    assert path.exists()

    retry = owned_scratch(repo, "orphan", run_id="dead", runtime_root_path=runtime)
    assert retry.reopen_existing() == path
    retry.close(state="succeeded", remove_retained=True)
    assert not path.exists()


def test_repo_local_scratch_recovery_is_not_mistaken_for_a_registered_worktree(tmp_path: Path) -> None:
    repo, _runtime = _paths(tmp_path)
    runtime = repo / ".charness"
    owner = owned_scratch(repo, "local", run_id="dead", runtime_root_path=runtime)
    path = owner.open()
    owner._close_lock()
    receipt_path = path / OWNER_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt.update({"pid": 0, "expires_at": "2020-01-01T00:00:00Z", "state": "active"})
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    inspected = inspect_scratch_roots(repo, runtime_root_path=runtime)
    assert inspected["roots"][0]["registered_worktree"] is False
    assert inspected["roots"][0]["orphaned"] is True
    recovered = recover_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)
    assert recovered["recovered"] == 1


def test_orphan_recovery_restores_a_crashed_hold_out_move(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    source = repo / "in-progress.md"
    source.write_text("TODO\n", encoding="utf-8")
    owner = owned_scratch(repo, "hold-out", run_id="dead", runtime_root_path=runtime)
    path = owner.open()
    staged = path / "0-in-progress.md"
    source.rename(staged)
    owner.update(
        hold_out_paths=[{"source": "in-progress.md", "staged": "0-in-progress.md", "state": "moved"}]
    )
    owner._close_lock()
    receipt_path = path / OWNER_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt.update({"pid": 0, "expires_at": "2020-01-01T00:00:00Z", "state": "active"})
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    recovered = recover_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)
    assert recovered["recovered"] == 1
    assert source.read_text(encoding="utf-8") == "TODO\n"
    saved = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert saved["hold_out_recovery"]["status"] == "restored"


def test_retained_owner_can_be_reopened_and_removed_after_recovery(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "retry", run_id="same", runtime_root_path=runtime)
    path = owner.open()
    owner.retain_with(recovery_command="retry")
    owner.close()
    receipt_path = path / OWNER_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["recovery_command"] == "retry"
    receipt["pid"] = 0
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    reopened = owned_scratch(repo, "retry", run_id="same", runtime_root_path=runtime)
    assert reopened.reopen_existing() == path
    reopened.close(state="succeeded", remove_retained=True)
    assert not path.exists()


def test_owner_receipt_failure_rolls_back_to_retryable_retained_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "receipt-failure", run_id="retryable", runtime_root_path=runtime)

    import scripts.runtime_scratch as core

    original = core._write_json
    calls = 0

    def fail_first_receipt(path: Path, payload: dict) -> None:
        nonlocal calls
        if path.name == OWNER_RECEIPT_NAME and calls == 0:
            calls += 1
            raise OSError("receipt write failed")
        original(path, payload)

    monkeypatch.setattr(core, "_write_json", fail_first_receipt)
    with pytest.raises(OSError, match="receipt write failed"):
        owner.open()

    receipt_path = owner.path / OWNER_RECEIPT_NAME
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["state"] == "failed"
    assert receipt["retention"] == "retained-evidence"
    assert receipt["owner_open_error"] == "receipt write failed"

    receipt["pid"] = 0
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    retry = owned_scratch(repo, "receipt-failure", run_id="retryable", runtime_root_path=runtime)
    assert retry.reopen_existing() == owner.path
    retry.close(state="succeeded", remove_retained=True)
    assert not owner.path.exists()


def _paths(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    runtime = tmp_path / "runtime"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    return repo, runtime


def test_owned_scratch_writes_receipt_and_cleans_success_and_failure(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    with owned_scratch(repo, "quality-engine", run_id="success", runtime_root_path=runtime) as path:
        receipt = json.loads((path / OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))
        assert receipt["schema"] == "charness.runtime-scratch-owner/v1"
        assert receipt["producer"] == "quality-engine"
        assert receipt["state"] == "active"
        assert path.is_relative_to(runtime / "scratch")
    assert not (runtime / "scratch" / "quality-engine" / "success").exists()

    failed = owned_scratch(repo, "quality-engine", run_id="failure", runtime_root_path=runtime)
    with pytest.raises(RuntimeError, match="boom"):
        with failed:
            raise RuntimeError("boom")
    assert not (runtime / "scratch" / "quality-engine" / "failure").exists()


def test_inspection_reports_active_owner_and_exact_inventory(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "probe", run_id="live", runtime_root_path=runtime)
    path = owner.open()
    (path / "payload.bin").write_bytes(b"1234")
    report = inspect_scratch_roots(repo, runtime_root_path=runtime)
    item = report["roots"][0]
    assert item["producer"] == "probe"
    assert item["entries"] == 3  # receipt, lock, and payload
    assert item["bytes"] == 4 + len((path / OWNER_RECEIPT_NAME).read_bytes()) + len((path / ".charness-owner.lock").read_bytes())
    assert item["active_lock"] is True
    assert item["disposition"] == "refuse-active,non-terminal,unexpired"
    owner.close()


def test_complete_evidence_is_atomically_promoted_and_partial_is_refused(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    destination = tmp_path / "proof" / "result.json"
    owner = owned_scratch(repo, "proof", run_id="complete", runtime_root_path=runtime)
    with owner as path:
        source = path / "result.json"
        source.write_text('{"status":"pass"}\n', encoding="utf-8")
        receipt = owner.promote_file(source, destination)
    assert destination.read_text(encoding="utf-8") == '{"status":"pass"}\n'
    assert json.loads(receipt.read_text(encoding="utf-8"))["state"] == "retained"
    assert not (runtime / "scratch" / "proof" / "complete").exists()

    incomplete = owned_scratch(repo, "proof", run_id="partial", runtime_root_path=runtime)
    with incomplete as path:
        source = path / "partial.json"
        source.write_text("partial\n", encoding="utf-8")
        with pytest.raises(ScratchError, match="incomplete"):
            incomplete.promote_file(source, tmp_path / "proof" / "partial.json", complete=False)


def test_failed_promotion_retains_source_for_retry(tmp_path: Path, monkeypatch) -> None:
    import scripts.runtime_scratch as core

    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "proof", run_id="sidecar-failure", runtime_root_path=runtime)
    path = owner.open()
    source = path / "result.json"
    source.write_text('{"status":"pass"}\n', encoding="utf-8")
    owner.update(
        recovery_command="python3 -m retry",
        packet_sha256="packet-identity",
        promotion_diagnostic="sidecar will be retried",
    )
    original = core._write_json

    def fail_sidecar(target: Path, payload: dict) -> None:
        if target.name.endswith(".charness-receipt.json"):
            raise OSError("sidecar unavailable")
        original(target, payload)

    monkeypatch.setattr(core, "_write_json", fail_sidecar)
    with pytest.raises(OSError, match="sidecar unavailable"):
        owner.promote_file(source, tmp_path / "proof" / "result.json")
    owner.close(state="failed")

    assert source.is_file()
    assert path.is_dir()
    receipt = json.loads((path / OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))
    assert receipt["recovery_command"] == "python3 -m retry"
    assert receipt["packet_sha256"] == "packet-identity"
    assert receipt["promotion_diagnostic"] == "sidecar will be retried"
    assert "promotion_error" in receipt


def test_gc_refuses_a_forged_or_mismatched_owner_identity(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(repo, "proof", run_id="forged", runtime_root_path=runtime)
    path = owner.open()
    owner.retain()
    owner.close()
    receipt_path = path / OWNER_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt.update({"owner": "foreign", "producer": "other", "run_id": "other"})
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    report = inspect_scratch_roots(repo, runtime_root_path=runtime)
    assert report["roots"][0]["status"] == "unknown"
    assert report["roots"][0]["disposition"] == "refuse-owner-identity"
    gc = gc_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)
    assert gc["reclaimed_entries"] == 0
    assert path.exists()


def test_gc_is_dry_run_by_default_and_removes_only_expired_scratch(tmp_path: Path) -> None:
    repo, runtime = _paths(tmp_path)
    owner = owned_scratch(
        repo,
        "gc-producer",
        run_id="expired",
        runtime_root_path=runtime,
        retention_seconds=1,
    )
    path = owner.open()
    (path / "old.txt").write_text("old\n", encoding="utf-8")
    owner.close()

    # Recreate a terminal owner manually so the test models a finished run that
    # survived its process, rather than a live context manager.
    receipt_path = path / OWNER_RECEIPT_NAME
    path.mkdir(parents=True)
    receipt = {
        "schema": "charness.runtime-scratch-owner/v1",
        "owner": "charness",
        "producer": "gc-producer",
        "repo_root": str(repo),
        "repo_identity": _repo_identity(repo),
        "run_id": "expired",
        "pid": 0,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2020-01-01T00:00:00Z",
        "state": "succeeded",
        "retention": "scratch",
        "expires_at": "2020-01-01T00:00:00Z",
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    (path / "old.txt").write_text("old\n", encoding="utf-8")

    preview = gc_scratch_roots(repo, runtime_root_path=runtime)
    assert preview["dry_run"] is True
    assert preview["roots"][0]["disposition"] == "would-remove"
    assert path.exists()

    executed = gc_scratch_roots(repo, runtime_root_path=runtime, dry_run=False)
    assert executed["reclaimed_entries"] == 2
    assert executed["reclaimed_bytes"] > 0
    assert executed["roots"][0]["disposition"] == "removed"
    assert not path.exists()
