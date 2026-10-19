"""Refusal and cleanup branches of linked-worktree reviewer promotion."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from tests.script_main import load_script_module
from tests.test_review_recovery_failures import PROMOTION, SCRIPT_ROOT, SUPPORT

PRIMARY = load_script_module(
    "review_primary_promotion_under_test", SCRIPT_ROOT / "run_review_primary_promotion.py"
)
STORAGE = PROMOTION.STORAGE
REPORTS = Path("charness-artifacts/critique/workers")


def _refused(code: str, call, *args, **kwargs) -> SUPPORT.RunReviewError:
    with pytest.raises(SUPPORT.RunReviewError) as caught:
        call(*args, **kwargs)
    assert caught.value.code == code
    return caught.value


def _layouts(monkeypatch, root: Path, primary: Path, audit: dict, *, primary_layout=True):
    """Make `root` a linked checkout of a shared repository without spawning git."""
    layouts = {
        root.resolve(): NS(git_dir=root / "gitdir", common_dir=primary / ".git"),
    }
    if primary_layout:
        layouts[primary.resolve()] = NS(git_dir=primary / ".git", common_dir=primary / ".git")
    monkeypatch.setattr("scripts.core.git_checkout.layout_from_files", lambda path: layouts.get(path))
    monkeypatch.setattr("scripts.worktree.worktree_audit_lib.run_audit", lambda _root: audit)


def test_a_plain_checkout_is_its_own_primary(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.core.git_checkout.layout_from_files", lambda _path: None)
    assert PRIMARY._primary_worktree(SUPPORT, tmp_path) == tmp_path.resolve()


def test_a_linked_checkout_without_a_resolvable_primary_is_refused(tmp_path, monkeypatch):
    root, primary = tmp_path / "linked", tmp_path / "primary"
    root.mkdir()
    primary.mkdir()
    _layouts(monkeypatch, root, primary, {})
    refused = _refused("promotion-primary-unavailable", PRIMARY._primary_worktree, SUPPORT, root)
    assert "could not resolve the primary worktree" in str(refused)


def test_a_primary_that_is_not_the_shared_repository_is_refused(tmp_path, monkeypatch):
    root, primary, stranger = tmp_path / "linked", tmp_path / "primary", tmp_path / "stranger"
    for path in (root, primary, stranger):
        path.mkdir()
    _layouts(monkeypatch, root, primary, {"primary_worktree": str(stranger)})
    refused = _refused("promotion-primary-unavailable", PRIMARY._primary_worktree, SUPPORT, root)
    assert refused.details == {"primary_worktree": str(stranger.resolve())}
    _layouts(monkeypatch, root, primary, {"primary_worktree": str(root)})
    _refused("promotion-primary-unavailable", PRIMARY._primary_worktree, SUPPORT, root)
    _layouts(monkeypatch, root, primary, {"primary_worktree": str(primary)})
    assert PRIMARY._primary_worktree(SUPPORT, root) == primary.resolve()


def test_tree_listing_refuses_symlinks_and_special_files(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "kept.json").write_text("{}")
    assert list(PRIMARY._tree_files(SUPPORT, tree)) == ["kept.json"]
    os.mkfifo(tree / "pipe")
    _refused("stale-artifact-refused", PRIMARY._tree_files, SUPPORT, tree)
    (tree / "pipe").unlink()
    (tree / "link").symlink_to(tree / "kept.json")
    _refused("stale-artifact-refused", PRIMARY._tree_files, SUPPORT, tree)


def test_verifying_a_primary_attempt_refuses_every_divergence(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    (source / "result.json").write_text("new")
    _refused("stale-artifact-refused", PRIMARY._verify_tree, SUPPORT, source, destination)
    destination.mkdir()
    _refused("stale-artifact-refused", PRIMARY._verify_tree, SUPPORT, source, destination)
    (destination / "result.json").write_text("old")
    _refused("stale-artifact-refused", PRIMARY._verify_tree, SUPPORT, source, destination)
    (destination / "result.json").write_text("new")
    PRIMARY._verify_tree(SUPPORT, source, destination)


def test_copying_an_attempt_refuses_a_file_where_the_directory_belongs(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    destination.write_text("not a directory")
    _refused("stale-artifact-refused", PRIMARY._copy_or_verify_tree, SUPPORT, STORAGE, source, destination)


def test_copying_an_attempt_accepts_an_identical_prior_promotion(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    for tree in (source, destination):
        tree.mkdir()
        (tree / "result.json").write_text("same")
    PRIMARY._copy_or_verify_tree(SUPPORT, STORAGE, source, destination)


def test_an_attempt_without_a_manifest_leaves_no_partial_primary_bytes(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    (source / "result.json").write_text("bytes")
    _refused("promotion-readback-failed", PRIMARY._copy_or_verify_tree, SUPPORT, STORAGE, source, destination)
    assert not destination.exists()


def test_a_failed_copy_removes_the_directory_it_created_and_reraises(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    (source / "result.json").write_text("bytes")
    (source / "attempt-manifest.json").write_text("{}")

    def broken_copy(_source, _destination):
        raise OSError("disk full")

    with pytest.raises(OSError, match="disk full"):
        PRIMARY._copy_or_verify_tree(SUPPORT, NS(copy_or_verify=broken_copy), source, destination)
    assert not destination.exists()


def test_a_destination_outside_the_primary_worktree_is_refused(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    inside = PRIMARY._primary_destination(SUPPORT, primary, Path("a/b"), label="packet")
    assert inside == primary / "a/b"
    refused = _refused("path-invalid", PRIMARY._primary_destination, SUPPORT, primary, Path("../x"), label="packet")
    assert "packet escaped the primary worktree" in str(refused)


def _closure(tmp_path: Path, monkeypatch, *, packet_relative="charness-artifacts/critique/p.json"):
    root, primary = tmp_path / "linked", tmp_path / "primary"
    packet = root / packet_relative
    attempt = root / REPORTS / "a"
    attempt.mkdir(parents=True)
    (attempt / "result.json").write_text("proof")
    (attempt / "attempt-manifest.json").write_text("{}")
    packet.parent.mkdir(parents=True, exist_ok=True)
    packet.write_text("packet")
    (primary / REPORTS).mkdir(parents=True)
    (primary / packet_relative).parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(PRIMARY, "_primary_worktree", lambda _support, _root: primary.resolve())
    return root, primary, packet


def _promote(root: Path, packet: Path | None, storage=STORAGE):
    return PRIMARY.promote_finalized_closure(SUPPORT, storage, REPORTS, root, "a", {"packet": packet})


def test_a_checkout_that_is_its_own_primary_promotes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(PRIMARY, "_primary_worktree", lambda _support, root: root)
    assert _promote(tmp_path, None) == {"status": "current-worktree", "root": str(tmp_path.resolve())}


def test_promotion_refuses_an_unavailable_attempt_or_packet(tmp_path, monkeypatch):
    root, _primary, packet = _closure(tmp_path, monkeypatch)
    _refused("promotion-readback-failed", _promote, tmp_path / "elsewhere", packet)
    _refused("promotion-readback-failed", _promote, root, None)
    _refused("promotion-readback-failed", _promote, root, root / "missing.json")


def test_promotion_refuses_a_packet_that_escaped_the_linked_checkout(tmp_path, monkeypatch):
    root, _primary, _packet = _closure(tmp_path, monkeypatch)
    outside = tmp_path / "outside.json"
    outside.write_text("packet")
    _refused("path-invalid", _promote, root, outside)


def test_a_packet_outside_the_critique_owner_must_already_exist_in_the_primary(tmp_path, monkeypatch):
    root, primary, packet = _closure(tmp_path, monkeypatch, packet_relative="docs/p.json")
    _refused("promotion-primary-refused", _promote, root, packet)
    (primary / "docs/p.json").write_text("different")
    _refused("promotion-primary-refused", _promote, root, packet)
    (primary / "docs/p.json").write_text("packet")
    assert _promote(root, packet)["status"] == "promoted-to-primary"
    assert (primary / REPORTS / "a/result.json").read_text() == "proof"


def test_promotion_refuses_a_primary_packet_that_changes_during_read_back(tmp_path, monkeypatch):
    root, primary, packet = _closure(tmp_path, monkeypatch)
    real = STORAGE.copy_or_verify

    def lossy(source, destination):
        real(source, destination)
        if destination == primary / "charness-artifacts/critique/p.json":
            destination.write_text("tampered")

    _refused("promotion-readback-failed", _promote, root, packet, NS(copy_or_verify=lossy))
