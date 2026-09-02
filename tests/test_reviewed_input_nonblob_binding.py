"""What a reviewed path binds when its content is NOT file bytes.

Split from `test_reviewed_input_identity_binding.py`, which owns what enters the
identity digest and when a binding goes stale for ordinary files. These own the
two path kinds that answer "what did I read" with something else: a SUBMODULE,
whose content is a commit id, and a CURRENT POINTER, whose content is the record
it selects. Both were unbindable in either substrate before 2026-08-30, and the
repairs produced most of that day's reviewer findings, so their controls are
kept together where the next reader will look for them.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.review.critique_packet_lib import build_reviewed_input_identity
from scripts.review.reviewed_input_verification import verify_reviewed_input_identity

pytestmark = pytest.mark.boundary_contract(
    reason="exercise reviewed-input identity against real Git submodule boundaries"
)


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _init_identity_repo(repo: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    install_committed_repo(
        repo, {"reviewed.txt": "base\n", "unrelated.txt": "base\n"}, message="initial"
    )


def test_a_refreshed_current_pointer_is_bound_by_its_link_payload(tmp_path: Path) -> None:
    """Filing a record and refreshing its `latest.md` pointer must stay reviewable.

    The documented flow after writing any dated record is
    `refresh_current_pointer.py --execute`, which repoints a `latest.md` SYMLINK.
    That left a modified symlink in the change set, and the sweep fed it to
    `_checked_path`, which refuses symlinks by design — so every session that
    filed a record was unreviewable until it committed.

    The pointer is BOUND rather than excluded. An earlier cut dropped it from the
    sweep, and a fresh-eye review blocked on that: `auto_excluded_paths` sits in
    `PROVENANCE_FIELDS` and is never digested, so retargeting the pointer left the
    identity unchanged and an approved verdict silently followed the move.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "2026-08-30-record.md").write_text("# Record\n", encoding="utf-8")
    (records / "2026-08-29-older.md").write_text("# Older\n", encoding="utf-8")
    (records / "latest.md").symlink_to("2026-08-30-record.md")

    identity = build_reviewed_input_identity(repo_root=tmp_path)

    assert identity["status"] == "captured"
    pointer = "charness-artifacts/quality/latest.md"
    assert pointer in identity["reviewed_paths"]
    assert pointer not in identity["auto_excluded_paths"]
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")


def test_retargeting_the_current_pointer_stales_the_verdict(tmp_path: Path) -> None:
    """The discriminator the fresh-eye review demanded.

    Binding the link payload is only worth more than excluding it if a retarget
    actually moves the digest. It is the selection that carries meaning here, so
    pointing at a different record must not read as an unchanged input.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "a.md").write_text("# A\n", encoding="utf-8")
    (records / "b.md").write_text("# B\n", encoding="utf-8")
    (records / "latest.md").symlink_to("a.md")
    identity = build_reviewed_input_identity(repo_root=tmp_path)
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")

    (records / "latest.md").unlink()
    (records / "latest.md").symlink_to("b.md")

    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_the_current_pointer_filename_matches_its_owning_module(tmp_path: Path) -> None:
    """The restated constant must not drift from `artifact_naming_lib`."""
    from scripts.artifact_naming_lib import CURRENT_POINTER_FILENAME as OWNED
    from scripts.review.reviewed_input_identity import CURRENT_POINTER_FILENAME as RESTATED

    assert RESTATED == OWNED


def _submodule_repo(tmp_path: Path) -> Path:
    from tests.quality_gates.repo_shapes import install_submodule_repo

    repo, _upstream = install_submodule_repo(tmp_path / "repo")
    return repo


def test_a_working_tree_submodule_binds_its_commit_not_the_index_stage(tmp_path: Path) -> None:
    """`ls-files -s` prints `<mode> <object> <stage>`; `ls-tree` prints `<mode> <type> <object>`.

    Reading field 2 from both bound the STAGE NUMBER — the constant `0` — for
    every working-tree submodule, so no submodule change could stale an identity.
    The earlier test asserted only `captured` and never that the digest tracked
    the commit, which is why it passed over a constant.
    """
    repo = _submodule_repo(tmp_path)
    recorded = subprocess.run(
        ["git", "-C", "sub", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()

    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=[".gitmodules", "sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + recorded.encode()).hexdigest()
    assert entry["content_sha256"] != hashlib.sha256(b"gitlink\0" + b"0").hexdigest()


def test_a_removed_submodule_binds_its_preimage_commit(tmp_path: Path) -> None:
    """`git show <ref>:<path>` cannot read a gitlink, so a REMOVED submodule fell
    through both the deletion fallback and the gitlink binder and refused."""
    repo = _submodule_repo(tmp_path)
    before = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", "sub"], cwd=repo, capture_output=True, text=True
    ).stdout.split()[2]
    _run_git(repo, "rm", "-q", "-f", "sub")
    _run_git(repo, "commit", "-m", "drop the submodule")

    identity = build_reviewed_input_identity(repo_root=repo, changed_ref="HEAD")

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["disposition"] == "deleted"
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + before.encode()).hexdigest()


def test_editing_the_record_a_pointer_selects_stales_the_verdict(tmp_path: Path) -> None:
    """Binding only `readlink` caught a retarget but not a rewrite in place.

    A pointer whose selected record is edited selects different bytes for every
    consumer while reading as unchanged, so the target's content is bound too.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "a.md").write_text("# A\n", encoding="utf-8")
    (records / "b.md").write_text("# B\n", encoding="utf-8")
    (records / "latest.md").symlink_to("a.md")
    identity = build_reviewed_input_identity(repo_root=tmp_path)
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")

    (records / "a.md").write_text("# A, rewritten\n", encoding="utf-8")

    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_a_current_pointer_escaping_the_repo_root_is_refused(tmp_path: Path) -> None:
    """Skipping `_checked_path` for pointers also skipped its boundary check."""
    _init_identity_repo(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret.md").write_text("secret\n", encoding="utf-8")
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "latest.md").symlink_to(outside / "secret.md")

    with pytest.raises(ValueError, match="resolving outside repo root"):
        build_reviewed_input_identity(repo_root=tmp_path)


def test_moving_a_submodule_head_without_staging_stales_the_verdict(tmp_path: Path) -> None:
    """A reviewer reads the working tree, so bind what is CHECKED OUT.

    Binding the index entry meant moving the submodule's HEAD without staging it
    left the identity unchanged, and a changed reviewed input verified as
    current. The working-tree substrate drops staged/unstaged patch hashes from
    its digest, so no other field could compensate.
    """
    repo = _submodule_repo(tmp_path)
    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=[".gitmodules", "sub"])
    assert verify_reviewed_input_identity(repo, identity) == (True, "current")

    upstream = tmp_path / "upstream"
    (upstream / "f.txt").write_text("v2\n", encoding="utf-8")
    _run_git(upstream, "commit", "-am", "v2")
    _run_git(repo / "sub", "fetch", "-q", "origin")
    _run_git(repo / "sub", "checkout", "-q", "FETCH_HEAD")

    ok, reason = verify_reviewed_input_identity(repo, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_an_uninitialised_submodule_does_not_bind_the_superproject_head(tmp_path: Path) -> None:
    """Git repository discovery walks UPWARD.

    `git -C <uninitialised-submodule> rev-parse HEAD` returns the SUPERPROJECT's
    HEAD, so the previous round's checked-out-HEAD repair bound an unrelated
    commit as if it were the submodule's. An uninitialised submodule has nothing
    checked out to read, which is exactly when the index entry is honest.
    """
    origin = _submodule_repo(tmp_path)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "clone", "-q", str(origin), str(clone)],
        check=True,
        capture_output=True,
    )
    assert not (clone / "sub" / ".git").exists(), "fixture must leave the submodule uninitialised"
    index_entry = subprocess.run(
        ["git", "ls-files", "-s", "--", "sub"], cwd=clone, capture_output=True, text=True
    ).stdout.split()[1]
    superproject = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=clone, capture_output=True, text=True
    ).stdout.strip()

    identity = build_reviewed_input_identity(repo_root=clone, reviewed_paths=[".gitmodules", "sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert (
        entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + index_entry.encode()).hexdigest()
    )
    assert (
        entry["content_sha256"] != hashlib.sha256(b"gitlink\0" + superproject.encode()).hexdigest()
    )


def test_a_submodule_removed_from_disk_does_not_crash_identity_construction(
    tmp_path: Path,
) -> None:
    """`subprocess.run(cwd=...)` raises when the directory is gone.

    A function named `_optional` must not do that to its caller. A submodule
    deleted from disk while its gitlink stayed in the index raised
    `FileNotFoundError` out of identity construction instead of falling through
    to the index entry — the very pre-image the removed-submodule support exists
    to bind.
    """
    origin = _submodule_repo(tmp_path)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "clone", "-q", str(origin), str(clone)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "-q"],
        cwd=clone,
        check=True,
        capture_output=True,
    )
    index_entry = subprocess.run(
        ["git", "ls-files", "-s", "--", "sub"], cwd=clone, capture_output=True, text=True
    ).stdout.split()[1]
    shutil.rmtree(clone / "sub")

    # Nothing about the removed submodule changes before the re-verify below,
    identity = build_reviewed_input_identity(repo_root=clone, reviewed_paths=["sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert (
        entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + index_entry.encode()).hexdigest()
    )
    # An index gitlink survives its checkout being deleted, so binding it without
    # a disposition marked a REMOVED submodule undeleted, and restoring the
    # checkout then left that verdict `current`.
    assert entry["disposition"] == "deleted"
    assert verify_reviewed_input_identity(clone, identity) == (True, "current")


def test_an_unreadable_pointer_target_refuses_instead_of_hashing_a_constant(
    tmp_path: Path,
) -> None:
    """A read FAILURE is not a state.

    Substituting a stable `unreadable` marker let capture and verification agree
    on bytes neither could read, so an unreadable record verified as `current` —
    the same failure-as-passing-verdict shape as swallowing every OSError around
    a submodule checkout.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    target = records / "record.md"
    target.write_text("# Record\n", encoding="utf-8")
    (records / "latest.md").symlink_to("record.md")
    target.chmod(0o000)
    try:
        with pytest.raises(OSError):
            build_reviewed_input_identity(repo_root=tmp_path)
    finally:
        target.chmod(0o644)


def test_a_non_absence_oserror_is_not_treated_as_a_missing_checkout(
    tmp_path: Path, monkeypatch
) -> None:
    """The axis-varying control the absent-directory test could not supply.

    A blanket `except OSError` let a `PermissionError` over a PRESENT submodule
    read as "no checkout to consult" and bind the stale index value. The
    submodule's HEAD is genuinely moved off the index here and the PUBLIC
    consumer is invoked, so this exercises the false-`current` scenario itself
    rather than only proving that an exception escapes a private helper.
    """
    from scripts.review import reviewed_input_nonblob as nonblob

    repo = _submodule_repo(tmp_path)
    upstream = tmp_path / "upstream"
    (upstream / "f.txt").write_text("v2\n", encoding="utf-8")
    _run_git(upstream, "commit", "-am", "v2")
    _run_git(repo / "sub", "fetch", "-q", "origin")
    _run_git(repo / "sub", "checkout", "-q", "FETCH_HEAD")
    # The checkout now differs from the index, so falling back to the index
    # would bind a value no longer checked out -- the false `current`.
    assert (
        subprocess.run(
            ["git", "-C", "sub", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        != subprocess.run(
            ["git", "ls-files", "-s", "--", "sub"], cwd=repo, capture_output=True, text=True
        ).stdout.split()[1]
    )

    real_run = nonblob.run_process

    def deny_inside_submodule(*args, **kwargs):
        cwd = str(kwargs.get("cwd", ""))
        if cwd.endswith("sub"):
            raise PermissionError(13, "permission denied")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(nonblob, "run_process", deny_inside_submodule)

    with pytest.raises(PermissionError):
        build_reviewed_input_identity(repo_root=repo, reviewed_paths=[".gitmodules", "sub"])


def test_a_gitlink_path_replaced_by_an_external_symlink_refuses(tmp_path: Path) -> None:
    """`_review_paths` skips `_checked_path` whenever a gitlink is recognised.

    Recognising one therefore removed the symlink and repo-root checks, and the
    toplevel comparison could not restore them: it resolves BOTH sides, so a link
    to an external repository matches itself. Git also ran with its cwd inside
    that external repository before anything refused. The recogniser now declines
    a symlinked path outright and hands it back to the owner of this boundary.
    """
    external = tmp_path / "external"
    external.mkdir()
    _run_git(external, "init")
    (external / "f.txt").write_text("external\n", encoding="utf-8")
    _run_git(external, "add", "-A")
    _run_git(external, "commit", "-m", "external")
    external_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=external, capture_output=True, text=True
    ).stdout.strip()

    repo = _submodule_repo(tmp_path)
    shutil.rmtree(repo / "sub")
    (repo / "sub").symlink_to(external)

    from scripts.review import reviewed_input_nonblob as nonblob

    assert nonblob._gitlink_commit(repo, "sub", None) is None
    with pytest.raises(ValueError, match="is a symlink; declare the target file explicitly"):
        build_reviewed_input_identity(repo_root=repo, reviewed_paths=["sub"])
    # The discriminator: the external HEAD must appear nowhere in a captured identity.
    assert (
        external_head
        != subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
    )


def test_a_dirty_submodule_refuses_rather_than_binding_only_its_head(tmp_path: Path) -> None:
    """Edits inside a submodule do not move its HEAD.

    Binding only the commit reported `current` over content a reviewer had read
    and the identity had never covered, and the working-tree substrate drops the
    patch hashes so nothing else carried it. Binding a submodule's full working
    state means recursing into it; refusing says plainly that this substrate
    cannot describe what was read.
    """
    repo = _submodule_repo(tmp_path)
    # The submodule is still clean and unmoved between build and this immediate
    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=["sub"])
    assert verify_reviewed_input_identity(repo, identity) == (True, "current")

    (repo / "sub" / "f.txt").write_text("edited inside the submodule\n", encoding="utf-8")

    with pytest.raises(ValueError, match="submodule with uncommitted changes"):
        build_reviewed_input_identity(repo_root=repo, reviewed_paths=["sub"])


def test_a_staged_submodule_removal_is_deleted_even_with_its_checkout_retained(
    tmp_path: Path,
) -> None:
    """`git rm --cached` drops the index entry and leaves the checkout on disk.

    Recognising a gitlink only from the index sent that state to the
    ordinary-directory refusal, which never reached the HEAD pre-image binder;
    and marking deletion on disk-absence alone would still have called it
    present. Each signal carries a removal the other cannot.
    """
    repo = _submodule_repo(tmp_path)
    head_gitlink = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", "sub"], cwd=repo, capture_output=True, text=True
    ).stdout.split()[2]
    _run_git(repo, "rm", "-q", "--cached", "sub")
    assert (repo / "sub").is_dir(), "fixture must retain the checkout"

    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=["sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["disposition"] == "deleted"
    assert (
        entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + head_gitlink.encode()).hexdigest()
    )


def test_a_failed_cleanliness_check_refuses_rather_than_reading_as_clean(
    tmp_path: Path, monkeypatch
) -> None:
    """A failed check is not a clean checkout.

    `_git_bytes_optional` returns None on failure, and reading that as clean is
    the same failure-into-passing-verdict shape this module keeps closing — the
    second time in this one function, after a blanket `except OSError` did it
    around the HEAD lookup.
    """
    from scripts.review import reviewed_input_nonblob as nonblob

    repo = _submodule_repo(tmp_path)
    real_run = nonblob.run_process

    def fail_status(command, **kwargs):
        # A NONZERO EXIT, not a raised OSError: the narrowed catch propagates a
        # raise, so `None` -- the value that used to read as clean -- is only
        # produced by git running and failing.
        if "status" in command:
            return subprocess.CompletedProcess(command, 1, "", "fatal: cannot read the index")
        return real_run(command, **kwargs)

    monkeypatch.setattr(nonblob, "run_process", fail_status)

    with pytest.raises(ValueError, match="cleanliness could not be established"):
        nonblob._gitlink_commit(repo, "sub", None)


def test_a_pointer_naming_a_directory_refuses(tmp_path: Path) -> None:
    """A directory is neither a record nor an absence.

    Treating it as `absent` gave a stable digest while everything inside could
    change, so the pointer selected different content under an unchanged verdict.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    (records / "adir").mkdir(parents=True)
    (records / "adir" / "inner.md").write_text("x\n", encoding="utf-8")
    (records / "latest.md").symlink_to("adir")

    with pytest.raises(ValueError, match="naming a directory"):
        build_reviewed_input_identity(repo_root=tmp_path)


def test_a_pointer_naming_nothing_is_still_bound_as_absent(tmp_path: Path) -> None:
    """The discriminator: selecting no record is a real, stable state."""
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "latest.md").symlink_to("gone.md")

    identity = build_reviewed_input_identity(repo_root=tmp_path)

    assert "charness-artifacts/quality/latest.md" in identity["reviewed_paths"]
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")
