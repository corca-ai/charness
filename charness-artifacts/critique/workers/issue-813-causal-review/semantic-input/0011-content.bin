from __future__ import annotations

import builtins
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import runtime_scratch as core
from scripts import runtime_scratch_cli as cli
from scripts import runtime_scratch_promotion as promotion
from scripts import runtime_scratch_registry as registry


def _repo_and_runtime(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    runtime = tmp_path / "runtime"
    repo.mkdir()
    return repo, runtime


def _scratch_path(runtime: Path, producer: str = "producer", run_id: str = "run") -> Path:
    path = runtime / core.SCRATCH_DIR_NAME / producer / run_id
    path.mkdir(parents=True)
    return path


def _owner_payload(repo: Path, producer: str, run_id: str, **extra: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": core.SCHEMA,
        "owner": "charness",
        "producer": producer,
        "repo_root": str(repo),
        "repo_identity": core._repo_identity(repo),
        "run_id": run_id,
        "pid": 0,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2020-01-01T00:00:00Z",
        "state": "active",
        "retention": "retained-evidence",
        "expires_at": "2020-01-01T00:00:00Z",
    }
    payload.update(extra)
    return payload


def _write_owner(path: Path, payload: dict[str, object]) -> None:
    (path / core.OWNER_RECEIPT_NAME).write_text(json.dumps(payload), encoding="utf-8")


def _retained_owner(repo: Path, runtime: Path, producer: str = "retry", run_id: str = "same"):
    owner = core.owned_scratch(repo, producer, run_id=run_id, runtime_root_path=runtime)
    path = owner.open()
    owner.retain()
    owner.close()
    receipt_path = path / core.OWNER_RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["pid"] = 0
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    return owner, path, receipt_path


def _patched_registry_report(monkeypatch, roots: list[dict[str, object]]) -> None:
    monkeypatch.setattr(
        registry,
        "inspect_scratch_roots",
        lambda *_args, **_kwargs: {"roots": roots},
    )


def test_installed_bootstrap_and_direct_import_fallback(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(core.__file__).resolve().parents[1]
    import_path = [entry for entry in sys.path if entry != str(repo_root)]
    monkeypatch.setattr(sys, "path", import_path)
    original_import = builtins.__import__
    failed_once = False

    def fail_first_bootstrap_import(name, *args, **kwargs):
        nonlocal failed_once
        if name == "scripts.runtime_bootstrap" and not failed_once:
            failed_once = True
            sys.path[:] = [entry for entry in sys.path if entry != str(repo_root)]
            raise ModuleNotFoundError("simulated installed bootstrap miss", name=name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_first_bootstrap_import)
    module_name = "runtime_scratch_direct_import_probe"
    spec = importlib.util.spec_from_file_location(module_name, Path(core.__file__))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    assert failed_once is True
    assert str(repo_root) in sys.path
    repo, runtime = _repo_and_runtime(tmp_path)
    with module.owned_scratch(repo, "direct", run_id="imported", runtime_root_path=runtime) as path:
        assert path.is_dir()


def test_promotion_bootstrap_adds_missing_installed_root(monkeypatch) -> None:
    repo_root = Path(promotion.__file__).resolve().parents[1]
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(repo_root)])

    promotion._load_repo_runtime_bootstrap()

    assert sys.path[0] == str(repo_root)


@pytest.mark.parametrize(
    ("producer", "kwargs", "message"),
    [
        ("bad/name", {}, "simple owner token"),
        ("valid", {"run_id": "../escape"}, "simple owner token"),
        ("valid", {"retention": "archive"}, "unknown retention"),
        ("valid", {"retention_seconds": 0}, "retention_seconds must be positive"),
    ],
)
def test_owner_rejects_unsafe_configuration(
    tmp_path: Path, producer: str, kwargs: dict[str, object], message: str
) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)

    with pytest.raises(core.ScratchError, match=message):
        core.owned_scratch(repo, producer, runtime_root_path=runtime, **kwargs)

    assert not (runtime / core.SCRATCH_DIR_NAME).exists()


def test_invalid_receipts_are_unreadable_and_refused(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    missing = tmp_path / "missing-owner.json"
    assert core._read_owner(missing) is None

    path = _scratch_path(runtime, "corrupt", "receipt")
    (path / core.OWNER_RECEIPT_NAME).write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(core, "_registered_worktrees", lambda _repo: [])

    report = registry.inspect_scratch_roots(core, repo, runtime_root_path=runtime)

    assert report["roots"][0]["status"] == "unknown"
    assert report["roots"][0]["disposition"] == "refuse-unknown-owner"


def test_inventory_handles_missing_roots_links_limits_and_stat_errors(
    tmp_path: Path, monkeypatch
) -> None:
    missing = tmp_path / "does-not-exist"
    assert core._tree_inventory(missing, max_entries=10) == (0, 0, False)

    root = tmp_path / "inventory"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (nested / "payload").write_bytes(b"payload")
    (root / "link").symlink_to(nested, target_is_directory=True)

    entries, size, truncated = core._tree_inventory(root, max_entries=10)
    assert (entries, size, truncated) == (3, len(b"payload"), False)
    assert core._tree_inventory(root, max_entries=0)[2] is True

    class BrokenFile:
        path = str(root / "broken")

        def is_symlink(self) -> bool:
            return False

        def is_dir(self, *, follow_symlinks: bool = False) -> bool:
            return False

        def is_file(self, *, follow_symlinks: bool = False) -> bool:
            return True

        def stat(self, *, follow_symlinks: bool = False):
            raise OSError("stat raced with removal")

    original_scandir = core.os.scandir

    def injected_scandir(current):
        if Path(current) == root:
            return [BrokenFile()]
        return original_scandir(current)

    with monkeypatch.context() as patch:
        patch.setattr(core.os, "scandir", injected_scandir)
        assert core._tree_inventory(root, max_entries=10) == (1, 0, True)


def test_lock_probe_refuses_unreadable_lock_and_supports_no_fcntl(tmp_path: Path, monkeypatch) -> None:
    lock_path = tmp_path / "owner.lock"
    lock_path.write_text("pid=1\n", encoding="utf-8")
    original_open = core.Path.open

    def fail_lock_open(path, *args, **kwargs):
        if path == lock_path:
            raise OSError("lock disappeared")
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(core.Path, "open", fail_lock_open)
        assert core._lock_is_active(lock_path) is True

    with monkeypatch.context() as patch:
        patch.setattr(core, "fcntl", None)
        assert core._lock_is_active(lock_path) is False


@pytest.mark.parametrize("outcome, expected", [("dead", False), ("denied", True), ("error", False), ("alive", True)])
def test_pid_probe_maps_process_liveness_errors(
    monkeypatch, outcome: str, expected: bool
) -> None:
    def injected_kill(pid: int, signal_number: int) -> None:
        assert (pid, signal_number) == (42, 0)
        if outcome == "dead":
            raise ProcessLookupError
        if outcome == "denied":
            raise PermissionError
        if outcome == "error":
            raise OSError("process probe failed")

    monkeypatch.setattr(core.os, "kill", injected_kill)

    assert core._pid_is_alive(42) is expected


def test_worktree_probe_translates_failures_and_parses_success(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    def unavailable(*_args, **_kwargs):
        raise OSError("git is unavailable")

    monkeypatch.setattr(core, "run_process", unavailable)
    with pytest.raises(core.ScratchError, match="cannot inspect registered worktrees: git is unavailable"):
        core._registered_worktrees(repo)

    monkeypatch.setattr(
        core,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stderr="permission denied\n", stdout=""),
    )
    with pytest.raises(core.ScratchError, match="permission denied"):
        core._registered_worktrees(repo)

    monkeypatch.setattr(
        core,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stderr="", stdout="git failed\n"),
    )
    with pytest.raises(core.ScratchError, match="git failed"):
        core._registered_worktrees(repo)

    nested = repo / "nested"
    monkeypatch.setattr(
        core,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stderr="",
            stdout=f"worktree {repo}\nworktree {nested}\n",
        ),
    )
    assert core._registered_worktrees(repo) == [repo.resolve(), nested.resolve()]


def test_owner_open_is_idempotent_and_rejects_collisions(tmp_path: Path) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "collision", run_id="same", runtime_root_path=runtime)
    path = owner.open()

    assert owner.open() == path
    collision = core.owned_scratch(repo, "collision", run_id="same", runtime_root_path=runtime)
    with pytest.raises(core.ScratchError, match="already exists"):
        collision.open()

    owner.close()


def test_open_receipt_failure_removes_unidentifiable_root(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "receipt-rollback", run_id="missing", runtime_root_path=runtime)

    def fail_receipts(*_args, **_kwargs):
        raise OSError("receipt storage unavailable")

    monkeypatch.setattr(core, "_write_json", fail_receipts)
    with pytest.raises(OSError, match="receipt storage unavailable"):
        owner.open()

    assert not owner.path.exists()
    assert owner._opened is False


def test_lifecycle_guards_and_terminal_state_validation(tmp_path: Path) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "guards", run_id="before-open", runtime_root_path=runtime)

    owner._close_lock()
    owner.close()
    with pytest.raises(core.ScratchError, match="before it is opened"):
        owner.retain()
    with pytest.raises(core.ScratchError, match="before it is opened"):
        owner.retain_with(retry="later")
    with pytest.raises(core.ScratchError, match="before it is opened"):
        owner.update(status="not-open")

    opened = core.owned_scratch(repo, "guards", run_id="invalid-state", runtime_root_path=runtime)
    opened.open()
    with pytest.raises(core.ScratchError, match="invalid terminal scratch state"):
        opened.close(state="unknown")
    opened.close()


def test_failed_promotion_retains_retry_metadata(tmp_path: Path) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "promotion", run_id="failed", runtime_root_path=runtime)
    path = owner.open()
    owner._promoted = True

    owner.retain_failed_promotion(retry_command="retry --run failed")
    receipt = json.loads((path / core.OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))

    assert owner._promoted is False
    assert receipt["state"] == "retained"
    assert receipt["retention"] == "retained-evidence"
    assert receipt["retry_command"] == "retry --run failed"
    owner.close(state="failed", remove_retained=True)
    assert not path.exists()


def test_promotion_refuses_unopened_invalid_source_and_internal_destination(tmp_path: Path) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "promotion-refuse", run_id="checks", runtime_root_path=runtime)

    with pytest.raises(core.ScratchError, match="before the scratch root is opened"):
        owner.promote_file(tmp_path / "missing", tmp_path / "durable.json")

    path = owner.open()
    source = path / "evidence.json"
    source.write_text("evidence\n", encoding="utf-8")
    with pytest.raises(core.ScratchError, match="must be a file inside"):
        owner.promote_file(tmp_path / "outside", tmp_path / "durable.json")
    with pytest.raises(core.ScratchError, match="must be outside"):
        owner.promote_file(source, path / "durable.json")

    owner.close()


def test_promotion_readback_mismatch_retains_source_for_retry(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "promotion-retry", run_id="readback", runtime_root_path=runtime)
    path = owner.open()
    source = path / "evidence.json"
    destination = tmp_path / "durable" / "evidence.json"
    source.write_text("evidence\n", encoding="utf-8")

    monkeypatch.setattr(promotion, "_read_owner", lambda _path: {})
    with pytest.raises(core.ScratchError, match="read-back verification"):
        promotion.promote_file(owner, source, destination)

    assert source.is_file()
    assert destination.read_text(encoding="utf-8") == "evidence\n"
    receipt = json.loads((path / core.OWNER_RECEIPT_NAME).read_text(encoding="utf-8"))
    assert "read-back verification" in receipt["promotion_error"]
    owner.close(state="failed", remove_retained=True)


def test_promotion_preserves_source_when_failure_receipt_cannot_be_written(
    tmp_path: Path, monkeypatch
) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    owner = core.owned_scratch(repo, "promotion-retry", run_id="receipt", runtime_root_path=runtime)
    path = owner.open()
    source = path / "evidence.json"
    destination = tmp_path / "durable" / "evidence.json"
    source.write_text("evidence\n", encoding="utf-8")

    def fail_receipt(*_args, **_kwargs):
        raise OSError("owner receipt unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(promotion._scratch, "_write_json", fail_receipt)
        with pytest.raises(OSError, match="owner receipt unavailable"):
            promotion.promote_file(owner, source, destination)

    assert source.is_file()
    assert destination.is_file()
    assert owner._promoted is False
    owner.close(state="failed", remove_retained=True)


def test_reopen_existing_is_idempotent_after_identity_checked_retry(tmp_path: Path) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    _owner, path, receipt_path = _retained_owner(repo, runtime)
    retry = core.owned_scratch(repo, "retry", run_id="same", runtime_root_path=runtime)

    assert retry.reopen_existing() == path
    assert retry.reopen_existing() == path
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["state"] == "active"
    assert receipt["recovery_of"] == "same"
    retry.close(state="succeeded", remove_retained=True)
    assert not path.exists()


@pytest.mark.parametrize("mutation, message", [
    ("missing-receipt", "unknown scratch owner"),
    ("repo-mismatch", "another repository"),
    ("owner-mismatch", "different owner identity"),
    ("terminal", "not retained retry evidence"),
    ("live", "owner process is alive"),
])
def test_reopen_existing_refuses_untrusted_retry_inputs(
    tmp_path: Path, mutation: str, message: str
) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    _owner, path, receipt_path = _retained_owner(repo, runtime, producer="refuse", run_id=mutation)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if mutation == "missing-receipt":
        receipt_path.unlink()
    elif mutation == "repo-mismatch":
        receipt["repo_identity"] = "foreign-repository"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    elif mutation == "owner-mismatch":
        receipt["producer"] = "other-producer"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    elif mutation == "terminal":
        receipt["state"] = "succeeded"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    else:
        receipt["pid"] = 1
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    retry = core.owned_scratch(repo, "refuse", run_id=mutation, runtime_root_path=runtime)
    if mutation == "live":
        original_pid_probe = core._pid_is_alive
        try:
            core._pid_is_alive = lambda value: value == 1
            with pytest.raises(core.ScratchError, match=message):
                retry.reopen_existing()
        finally:
            core._pid_is_alive = original_pid_probe
    else:
        with pytest.raises(core.ScratchError, match=message):
            retry.reopen_existing()
    assert path.exists()
    shutil.rmtree(path)


def test_reopen_existing_refuses_lock_race_and_closes_handle(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    _owner, path, _receipt_path = _retained_owner(repo, runtime, producer="busy", run_id="lock")
    retry = core.owned_scratch(repo, "busy", run_id="lock", runtime_root_path=runtime)

    class BusyFcntl:
        LOCK_EX = core.fcntl.LOCK_EX
        LOCK_NB = core.fcntl.LOCK_NB

        @staticmethod
        def flock(*_args, **_kwargs):
            raise BlockingIOError("owner lock is held")

    monkeypatch.setattr(core, "fcntl", BusyFcntl)
    with pytest.raises(core.ScratchError, match="refusing to reopen active scratch root"):
        retry.reopen_existing()

    assert retry._lock is None
    shutil.rmtree(path)


def test_registry_refuses_unknown_owner_and_skips_non_directory_children(
    tmp_path: Path, monkeypatch
) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    scratch = runtime / core.SCRATCH_DIR_NAME
    scratch.mkdir(parents=True)
    (scratch / "not-a-producer").write_text("ignored", encoding="utf-8")
    ignored_target = scratch / "ignored-target"
    ignored_target.mkdir()
    (scratch / "ignored-link").symlink_to(ignored_target, target_is_directory=True)
    path = _scratch_path(runtime, "unknown", "run")
    (path / core.OWNER_RECEIPT_NAME).write_text("{bad", encoding="utf-8")
    monkeypatch.setattr(core, "_registered_worktrees", lambda _repo: [])

    report = registry.inspect_scratch_roots(core, repo, runtime_root_path=runtime)

    assert report["root_count"] == 1
    assert report["roots"][0]["disposition"] == "refuse-unknown-owner"


def test_registry_status_refuses_invalid_expiry_and_registered_worktree(tmp_path: Path) -> None:
    repo, _runtime = _repo_and_runtime(tmp_path)
    path = tmp_path / "producer" / "run"
    path.mkdir(parents=True)
    owner = _owner_payload(
        repo,
        "producer",
        "run",
        retention="scratch",
        expires_at="not-a-timestamp",
    )

    item = registry._root_status(
        core,
        path,
        owner,
        repo_root=repo,
        max_entries=100,
        worktrees=[path],
        worktree_inventory_ok=True,
        now=datetime.now(timezone.utc),
    )

    assert item["registered_worktree"] is True
    assert "registered-worktree" in item["disposition"]
    assert "unexpired" in item["disposition"]

    foreign = dict(owner, repo_identity="foreign-repository")
    foreign_item = registry._root_status(
        core,
        path,
        foreign,
        repo_root=repo,
        max_entries=100,
        worktrees=[],
        worktree_inventory_ok=False,
        now=datetime.now(timezone.utc),
    )

    assert "repo-mismatch" in foreign_item["disposition"]
    assert "worktree-inventory-error" in foreign_item["disposition"]

    original_pid_probe = core._pid_is_alive
    try:
        core._pid_is_alive = lambda _pid: True
        active_item = registry._root_status(
            core,
            path,
            owner,
            repo_root=repo,
            max_entries=100,
            worktrees=[],
            worktree_inventory_ok=True,
            now=datetime.now(timezone.utc),
        )
    finally:
        core._pid_is_alive = original_pid_probe

    assert "active" in active_item["disposition"]


def test_gc_refuses_path_changed_after_eligibility(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    missing = runtime / "scratch" / "race" / "gone"
    roots = [{"path": str(missing), "disposition": "eligible", "entries": 2, "bytes": 8}]
    _patched_registry_report(monkeypatch, roots)

    report = registry.gc_scratch_roots(
        core, repo, runtime_root_path=runtime, dry_run=False
    )

    assert report["reclaimed_entries"] == 0
    assert report["reclaimed_bytes"] == 0
    assert report["roots"][0]["disposition"] == "refuse-path-changed"


def test_recovery_skips_non_orphans_and_refuses_path_changes(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    missing = runtime / "scratch" / "race" / "gone"
    roots = [
        {"path": str(runtime / "scratch" / "quiet" / "run"), "orphaned": False},
        {"path": str(missing), "orphaned": True},
    ]
    _patched_registry_report(monkeypatch, roots)

    report = registry.recover_scratch_roots(
        core, repo, runtime_root_path=runtime, dry_run=False
    )

    assert report["recovered"] == 0
    assert report["roots"][1]["disposition"] == "refuse-path-changed"

    preview_roots = [{"path": str(missing), "orphaned": True}]
    _patched_registry_report(monkeypatch, preview_roots)
    preview = registry.recover_scratch_roots(core, repo, runtime_root_path=runtime)
    assert preview["roots"][0]["disposition"] == "would-recover-orphan"


def test_recovery_refuses_owner_changed_on_second_read(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    path = _scratch_path(runtime, "changed", "run")
    roots = [{"path": str(path), "orphaned": True}]
    _patched_registry_report(monkeypatch, roots)
    monkeypatch.setattr(core, "_read_owner", lambda _path: None)

    report = registry.recover_scratch_roots(core, repo, runtime_root_path=runtime, dry_run=False)

    assert report["roots"][0]["disposition"] == "refuse-owner-changed"


def test_recovery_refuses_owner_that_becomes_active(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    path = _scratch_path(runtime, "active", "run")
    roots = [{"path": str(path), "orphaned": True}]
    _patched_registry_report(monkeypatch, roots)
    monkeypatch.setattr(core, "_read_owner", lambda _path: _owner_payload(repo, "active", "run"))
    monkeypatch.setattr(core, "_lock_is_active", lambda _path: True)

    report = registry.recover_scratch_roots(core, repo, runtime_root_path=runtime, dry_run=False)

    assert report["roots"][0]["disposition"] == "refuse-owner-active"


def test_recovery_refuses_repo_identity_change(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    path = _scratch_path(runtime, "foreign", "run")
    roots = [{"path": str(path), "orphaned": True}]
    _patched_registry_report(monkeypatch, roots)
    monkeypatch.setattr(
        core,
        "_read_owner",
        lambda _path: _owner_payload(repo, "foreign", "run", repo_identity="foreign"),
    )
    monkeypatch.setattr(core, "_lock_is_active", lambda _path: False)
    monkeypatch.setattr(core, "_pid_is_alive", lambda _pid: False)

    report = registry.recover_scratch_roots(core, repo, runtime_root_path=runtime, dry_run=False)

    assert report["roots"][0]["disposition"] == "refuse-repo-mismatch"


def test_recovery_refuses_hold_out_restore_failure(tmp_path: Path, monkeypatch) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    path = _scratch_path(runtime, "hold-out", "run")
    roots = [{"path": str(path), "orphaned": True}]
    _patched_registry_report(monkeypatch, roots)
    monkeypatch.setattr(core, "_read_owner", lambda _path: _owner_payload(repo, "hold-out", "run"))
    monkeypatch.setattr(core, "_lock_is_active", lambda _path: False)
    monkeypatch.setattr(core, "_pid_is_alive", lambda _pid: False)
    monkeypatch.setattr(
        registry,
        "_restore_hold_out_paths",
        lambda *_args, **_kwargs: {"status": "refused", "reason": "ambiguous move"},
    )

    report = registry.recover_scratch_roots(core, repo, runtime_root_path=runtime, dry_run=False)

    assert report["roots"][0]["disposition"] == "refuse-hold-out-restore"
    assert report["roots"][0]["hold_out_recovery"]["reason"] == "ambiguous move"


@pytest.mark.parametrize(
    ("raw_entries", "reason"),
    [
        ("not-a-list", "not a list"),
        ([None], "not an object"),
        ([{"source": "only-source"}], "no source and staged paths"),
        ([{"source": "../escape", "staged": "payload"}], "escaped its owner boundary"),
    ],
)
def test_hold_out_restore_validates_mapping_shape(
    tmp_path: Path, raw_entries: object, reason: str
) -> None:
    repo, _runtime = _repo_and_runtime(tmp_path)
    owner_path = tmp_path / "runtime" / "scratch" / "producer" / "run"
    owner_path.mkdir(parents=True)

    result = registry._restore_hold_out_paths(
        core, repo, owner_path, {"hold_out_paths": raw_entries}
    )

    assert result["status"] == "refused"
    assert reason in result["reason"]


def test_hold_out_restore_refuses_when_both_paths_exist(tmp_path: Path) -> None:
    repo, _runtime = _repo_and_runtime(tmp_path)
    owner_path = tmp_path / "runtime" / "scratch" / "producer" / "run"
    owner_path.mkdir(parents=True)
    source = repo / "result.txt"
    staged = owner_path / "result.txt"
    source.write_text("original", encoding="utf-8")
    staged.write_text("staged", encoding="utf-8")

    result = registry._restore_hold_out_paths(
        core,
        repo,
        owner_path,
        {"hold_out_paths": [{"source": "result.txt", "staged": "result.txt"}]},
    )

    assert result["status"] == "refused"
    assert "both exist" in result["reason"]
    assert source.read_text(encoding="utf-8") == "original"
    assert staged.read_text(encoding="utf-8") == "staged"


def test_hold_out_restore_records_restored_and_untouched_states(tmp_path: Path) -> None:
    repo, _runtime = _repo_and_runtime(tmp_path)
    owner_path = tmp_path / "runtime" / "scratch" / "producer" / "run"
    owner_path.mkdir(parents=True)
    staged = owner_path / "staged" / "new.txt"
    staged.parent.mkdir()
    staged.write_text("new", encoding="utf-8")
    (repo / "already.txt").write_text("already", encoding="utf-8")
    owner = {
        "hold_out_paths": [
            {"source": "nested/new.txt", "staged": "staged/new.txt"},
            {"source": "already.txt", "staged": "absent.txt"},
            {"source": "not-moved.txt", "staged": "also-absent.txt"},
        ]
    }

    result = registry._restore_hold_out_paths(core, repo, owner_path, owner)

    assert result == {
        "status": "restored",
        "restored": ["nested/new.txt"],
        "untouched": ["already.txt", "not-moved.txt"],
    }
    assert (repo / "nested" / "new.txt").read_text(encoding="utf-8") == "new"
    assert [entry["state"] for entry in owner["hold_out_paths"]] == [
        "restored",
        "already-restored",
        "not-moved",
    ]


def test_safe_relative_path_refuses_absolute_and_escape_paths(tmp_path: Path) -> None:
    repo, _runtime = _repo_and_runtime(tmp_path)

    assert registry._safe_relative_path(repo, "/tmp/absolute") is None
    assert registry._safe_relative_path(repo, "../outside") is None


@pytest.mark.parametrize("argument", [("--max-roots", "0"), ("--max-entries", "0")])
def test_cli_rejects_nonpositive_limits(argument: tuple[str, str]) -> None:
    with pytest.raises(SystemExit, match="must be positive"):
        cli.main(object(), ["inspect", *argument])


def test_cli_dispatches_commands_with_injected_core_and_yaml() -> None:
    calls: list[tuple[str, Path, dict[str, object]]] = []
    emitted: list[dict[str, object]] = []

    def record(command: str, payload: dict[str, object]):
        def handler(repo: Path, **options: object) -> dict[str, object]:
            calls.append((command, repo, options))
            return payload

        return handler

    yaml_output = SimpleNamespace(emit_yaml=emitted.append)
    fake_core = SimpleNamespace(
        inspect_scratch_roots=record("inspect", {"command": "inspect"}),
        gc_scratch_roots=record("gc", {"command": "gc"}),
        recover_scratch_roots=record("recover", {"command": "recover"}),
        import_repo_module=lambda *_args: yaml_output,
    )
    repo = Path("/fixture/repo")
    runtime = Path("/fixture/runtime")

    for command in ("inspect", "gc", "recover"):
        assert cli.main(
            fake_core,
            [
                command,
                "--repo-root",
                str(repo),
                "--runtime-root",
                str(runtime),
                "--max-roots",
                "3",
                "--max-entries",
                "7",
                "--execute",
            ],
        ) == 0

    assert [call[0] for call in calls] == ["inspect", "gc", "recover"]
    assert all(call[1] == repo for call in calls)
    assert calls[0][2] == {"runtime_root_path": runtime, "max_roots": 3, "max_entries": 7}
    assert calls[1][2]["dry_run"] is False
    assert calls[2][2]["dry_run"] is False
    assert emitted == [{"command": command} for command in ("inspect", "gc", "recover")]


def test_runtime_scratch_main_runs_cli_in_process(tmp_path: Path, monkeypatch, capsys) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    monkeypatch.setattr(core, "_registered_worktrees", lambda _repo: [])

    assert core.main(
        [
            "inspect",
            "--repo-root",
            str(repo),
            "--runtime-root",
            str(runtime),
        ]
    ) == 0

    assert "charness.runtime-scratch-inspection/v1" in capsys.readouterr().out


def test_direct_script_entrypoint_runs_inspection_with_injected_process_probe(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo, runtime = _repo_and_runtime(tmp_path)
    from scripts.core import subprocess_guard

    monkeypatch.setattr(
        subprocess_guard,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "runtime_scratch.py",
            "inspect",
            "--repo-root",
            str(repo),
            "--runtime-root",
            str(runtime),
        ],
    )
    spec = importlib.util.spec_from_file_location("__main__", Path(core.__file__))
    assert spec is not None and spec.loader is not None
    direct = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "__main__", direct)

    with pytest.raises(SystemExit) as exit_info:
        spec.loader.exec_module(direct)

    assert exit_info.value.code == 0
    assert "charness.runtime-scratch-inspection/v1" in capsys.readouterr().out
