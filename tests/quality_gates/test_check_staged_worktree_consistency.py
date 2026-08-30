"""Tests for the staged-vs-worktree consistency pre-commit gate (audit row A6).

Two fail-open defects this file pins:

1. A path staged and then DELETED on disk used to exit 0. The unstaged-side
   query filtered on ``ACM``, which excludes ``D`` -- and a deleted file is
   exactly the case worktree-walking validators skip entirely, so the staged
   blob would commit having been checked by nothing.
2. ``CHARNESS_ALLOW_PARTIAL_STAGE=0`` -- the spelling an operator uses to turn
   the bypass OFF -- used to turn it ON, because the value was only tested for
   truthiness as a string.

The gate must still pass a clean full stage, a fully staged deletion, and an
unstaged-only deletion.
"""
from __future__ import annotations

import importlib
import shutil
from pathlib import Path

import pytest

from tests.seed_cache import get_or_build

from .seeding_support import git, init_git_repo

cswc = importlib.import_module("scripts.check_staged_worktree_consistency")


def _build_repo_seed(seed_root: Path) -> None:
    repo = init_git_repo(seed_root)
    (repo / "f.txt").write_text("v1\n", encoding="utf-8")
    (repo / "g.txt").write_text("g1\n", encoding="utf-8")
    git(repo, "add", "f.txt", "g.txt")
    git(repo, "commit", "-qm", "init")


def _repo(tmp_path: Path) -> Path:
    seed = get_or_build("staged-worktree-consistency-repo-seed", _build_repo_seed) / "repo"
    repo = tmp_path / "repo"
    shutil.copytree(seed, repo)
    return repo


def test_staged_then_deleted_on_disk_is_flagged(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()  # index holds v2; worktree holds nothing
    assert cswc.find_stale_staged(repo) == ["f.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1


def test_staged_then_edited_is_flagged(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").write_text("v3\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "  ", "FALSE"])
def test_falsy_env_values_do_not_enable_the_bypass(
    tmp_path: Path, monkeypatch, value: str
) -> None:
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    monkeypatch.setenv(cswc.ALLOW_ENV, value)
    assert cswc.allow_partial_stage() is False
    assert cswc.main(["--repo-root", str(repo)]) == 1


@pytest.mark.parametrize("value", ["1", "true", "YES", " on "])
def test_truthy_env_values_enable_the_bypass(
    tmp_path: Path, monkeypatch, value: str
) -> None:
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").write_text("v3\n", encoding="utf-8")
    monkeypatch.setenv(cswc.ALLOW_ENV, value)
    assert cswc.allow_partial_stage() is True
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_clean_full_stage_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")  # index == worktree
    assert cswc.find_stale_staged(repo) == []
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_fully_staged_deletion_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "f.txt")  # deletion staged AND applied on disk
    assert cswc.find_stale_staged(repo) == []


def test_unstaged_only_deletion_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "g.txt").unlink()  # nothing staged for g.txt
    assert cswc.find_stale_staged(repo) == []


def test_staged_then_typechanged_on_disk_is_flagged(tmp_path: Path, monkeypatch) -> None:
    """A status letter allowlist is the wrong shape for an intersection question.

    The first repair widened `--diff-filter` from `ACM` to `ACMRD`, closing the
    deletion case one letter at a time and leaving `T` (typechange) hidden by the
    same mechanism: stage an edit, then replace the file with a symlink, and the
    unstaged side reports `T`, which `ACMRD` drops. The gate then passed a staged
    blob that no worktree-walking validator ever inspected.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    (repo / "f.txt").symlink_to("/etc/hostname")

    assert cswc.find_stale_staged(repo) == ["f.txt"]


def test_a_git_failure_is_unestablished_not_clean(tmp_path: Path, monkeypatch, capsys) -> None:
    """The gate's whole scope comes from two git queries. An empty answer from a
    failed git is indistinguishable from "nothing staged", so it must refuse.

    Pinned at the CLI, not just the library: `find_stale_staged` raising is worth
    nothing if `main` were later "hardened" to swallow it back into exit 0.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()

    with pytest.raises(RuntimeError):
        cswc.find_stale_staged(not_a_repo)

    assert cswc.main(["--repo-root", str(not_a_repo)]) == 1
    err = capsys.readouterr().err
    assert "UNESTABLISHED" in err
    assert "safe.directory" in err  # the remedy, not a bare traceback


def test_git_being_unusable_is_unestablished_not_clean(tmp_path: Path, monkeypatch) -> None:
    """The OSError twin of the git-failure test above: `git` missing, or an
    unusable cwd, raises before a returncode exists. An empty set from that path
    is indistinguishable from "nothing staged".
    """

    def _boom(*_args, **_kwargs):
        raise FileNotFoundError("No such file or directory: 'git'")

    monkeypatch.setattr(cswc.subprocess, "run", _boom)

    with pytest.raises(RuntimeError) as excinfo:
        cswc._git_names(tmp_path, "diff", "--cached", "--name-only")
    assert "git" in str(excinfo.value)


def test_untracked_but_still_on_disk_is_flagged(tmp_path: Path, monkeypatch, capsys) -> None:
    """`git rm --cached x`, x still on disk -- the shape the intersection cannot see.

    Removing a path from the index removes its index ENTRY, so `git diff
    --name-only` (worktree vs index) stops naming it and git reports it as
    untracked instead. The staged-side and unstaged-side sets therefore never
    intersect, and the gate exited 0 while every worktree-walking gate validated
    the on-disk copy of a file the commit deletes from the tree.

    Reproduced against the live repo on 2026-07-31 with NO bypass set: the
    sibling `check_staged_reversion` also passed, because it refuses only a
    phantom whose worktree copy still equals HEAD, so editing the on-disk copy
    cleared both gates and four doc gates then printed PASS over the removal.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")  # index: deleted; disk: still there
    assert (repo / "f.txt").exists()
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def test_untracked_but_still_on_disk_is_flagged_even_when_edited(tmp_path: Path, monkeypatch) -> None:
    """The full escape: editing the on-disk copy is what cleared check_staged_reversion."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")
    (repo / "f.txt").write_text("edited after untracking\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def test_untrack_remedy_is_not_git_add_and_actually_runs(tmp_path: Path, monkeypatch, capsys) -> None:
    """The offered remedies are EXECUTED here, not string-matched.

    The first cut of this repair offered `git rm <path>` for an orphaned path.
    That path has no index entry by construction, so `git rm` exits 128 with
    `pathspec ... did not match any files` -- an operator handed a command that
    errors, by a gate that just blocked their commit. String-matching the remedy
    is the same "validated something other than what ships" class this file
    exists to prevent, so each remedy is run and the gate re-checked.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")          # orphaned
    (repo / "g.txt").write_text("g2\n", encoding="utf-8")
    git(repo, "add", "g.txt")
    (repo / "g.txt").write_text("g3\n", encoding="utf-8")  # staged then edited

    assert cswc.find_stale_staged(repo) == ["f.txt", "g.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "git add g.txt" in err
    assert "git add f.txt" not in err
    assert "git rm f.txt" not in err, "git rm cannot run on a path with no index entry"

    # Execute the offered remedies and prove they clear the gate.
    git(repo, "add", "g.txt")
    git(repo, "reset", "--", "f.txt")
    assert cswc.find_stale_staged(repo) == []


def test_rename_source_orphan_remedies_are_executed_too(tmp_path: Path, monkeypatch) -> None:
    """The other orphan shape's remedies, run rather than asserted.

    `git reset --` restores the OLD name's entry, which after a rename leaves both
    names in the commit -- correct as a mechanic, not what the operator wanted, and
    the message says so. `rm` is the remedy that matches the commit.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "mv", "f.txt", "renamed.txt")
    (repo / "f.txt").write_text("recreated\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]

    (repo / "f.txt").unlink()  # the offered `rm <path>`
    assert cswc.find_stale_staged(repo) == []


def test_rm_remedy_clears_the_orphan(tmp_path: Path, monkeypatch) -> None:
    """The other offered exit: remove it on disk too, matching what commits."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")
    assert cswc.find_stale_staged(repo) == ["f.txt"]
    (repo / "f.txt").unlink()  # the offered `rm <path>`
    assert cswc.find_stale_staged(repo) == []


def test_a_rename_whose_source_is_recreated_is_flagged(tmp_path: Path, monkeypatch) -> None:
    """Rename detection is ON by default and collapses `D old` + `A new` into one
    `R` entry whose `--name-only` output is the DESTINATION only.

    The first cut keyed the new shape on `--diff-filter=D`, so `git mv a b` with
    `a` recreated on disk reported nothing and the whole repair degenerated to the
    old intersection -- while the committed tree has no `a`, the doc gates walk the
    recreated `a`, and every gate prints PASS. This is the same escape the slice
    was opened to close, reached through a workflow (move, then regenerate) this
    repo runs routinely.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "mv", "f.txt", "renamed.txt")
    (repo / "f.txt").write_text("recreated on disk\n", encoding="utf-8")

    # The letter-based query the first cut used sees nothing here.
    import subprocess as _sp

    letters = _sp.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=D"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.split()
    assert letters == [], "rename detection collapsed the D; this is why the query changed"

    assert cswc.find_stale_staged(repo) == ["f.txt"]


def test_a_plain_rename_still_passes(tmp_path: Path, monkeypatch) -> None:
    """Control for the test above: an ordinary rename must NOT be refused."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "mv", "f.txt", "renamed.txt")  # source gone from disk, as normal
    assert cswc.find_stale_staged(repo) == []


def test_a_dangling_symlink_at_an_orphaned_path_is_flagged(tmp_path: Path, monkeypatch) -> None:
    """`exists()` follows symlinks, so a broken one read as `gone` and failed open.

    A worktree walker still trips over the entry, which is what the predicate is
    actually asking about.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")
    (repo / "f.txt").unlink()
    (repo / "f.txt").symlink_to(repo / "nonexistent-target")
    assert not (repo / "f.txt").exists()      # the old predicate said "gone"
    assert (repo / "f.txt").is_symlink()      # a walker still sees it
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def test_a_non_ascii_orphaned_path_is_flagged(tmp_path: Path, monkeypatch) -> None:
    """`core.quotePath` is ON by git default and renders a non-ASCII path as the
    literal characters `"docs/\\303\\251.md"`, which no filesystem test matches.

    `-z` makes git emit raw bytes and stop C-quoting. Forced ON here so the test
    fails against a `text=True` reader regardless of the developer's git config.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    name = "é.md"
    (repo / name).write_text("x\n", encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-qm", "non-ascii")
    git(repo, "config", "core.quotePath", "true")
    git(repo, "rm", "-q", "--cached", name)
    assert cswc.find_stale_staged(repo) == [name]


def test_orphan_remedy_enumeration_is_capped(tmp_path: Path, monkeypatch, capsys) -> None:
    """`git rm -r --cached <dir>` can orphan thousands of paths; an uncapped list
    buries the bypass line printed after it."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    vendored = repo / "vendored"
    vendored.mkdir()
    for index in range(25):
        (vendored / f"f{index}.txt").write_text("x\n", encoding="utf-8")
    git(repo, "add", "vendored")
    git(repo, "commit", "-qm", "vendored")
    git(repo, "rm", "-rq", "--cached", "vendored")

    assert len(cswc.find_stale_staged(repo)) == 25
    assert cswc.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "and 15 more path(s) in the same state" in err
    # The count, not just the trailer: a regression that enumerates all 25 pairs
    # AND appends the "... and 15 more" line would satisfy the trailer assertion
    # while the harm the cap exists to prevent is fully present.
    assert err.count("\n  rm ") == 10
    assert err.rstrip().endswith("commit.)")


def test_a_case_only_respelling_is_not_an_orphan(tmp_path: Path, monkeypatch) -> None:
    """On a case-insensitive filesystem `Foo.md` -> `foo.md` stages a deletion of
    the old spelling while `lexists` resolves it to the NEW file, so the gate would
    refuse a legitimate rename -- and both offered remedies would be harmful there.

    NOT a case-insensitive-filesystem test: this suite runs on Linux, so the state
    is constructed directly (old spelling staged-deleted, new spelling tracked, old
    spelling present on disk) to pin the case-folded exemption itself. What runs on
    macOS/Windows is the same predicate over a state their filesystem produces.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "Foo.md").write_text("v1\n", encoding="utf-8")
    git(repo, "add", "Foo.md")
    git(repo, "commit", "-qm", "add Foo.md")
    git(repo, "mv", "Foo.md", "foo.md")
    (repo / "Foo.md").write_text("v1\n", encoding="utf-8")  # what a case-insensitive FS shows

    assert "foo.md" in cswc._git_names(repo, "ls-files")
    assert cswc.find_stale_staged(repo) == []


def test_case_folded_exemption_does_not_fire_on_an_unrelated_tracked_path(
    tmp_path: Path, monkeypatch
) -> None:
    """Round-2 finding: the case-only-rename exemption was a fail-open.

    Folding over the whole tracked set made the exemption fire on coincidence.
    With `Foo.md` and `foo.md` both tracked -- legal on Linux, where this hook
    runs -- untracking `Foo.md` while it stays on disk returned `[]`. The evidence
    of a re-spelling is that the new spelling is also STAGED, so the fold is over
    `staged & tracked`.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "Foo.md").write_text("upper\n", encoding="utf-8")
    (repo / "foo.md").write_text("lower\n", encoding="utf-8")
    git(repo, "add", "Foo.md", "foo.md")
    git(repo, "commit", "-qm", "both spellings tracked")
    git(repo, "rm", "-q", "--cached", "Foo.md")  # untrack ONE of them

    assert (repo / "Foo.md").exists()
    assert cswc.find_stale_staged(repo) == ["Foo.md"]


def test_intent_to_add_rename_does_not_hide_a_staged_then_deleted_path(
    tmp_path: Path, monkeypatch
) -> None:
    """Round-2 finding: `--no-renames` was on the staged read only.

    Index-vs-worktree rename detection collapses `D a` + `A b` into one `R` entry
    printing only the destination when the destination is an intent-to-add entry
    -- which is what `git add -p` creates for a new file. `a` then dropped out of
    the unstaged set, out of the intersection, and the ORIGINAL shape-1 defect
    (staged, then deleted on disk) was reachable again.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2 staged\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "moved.txt").write_text("v2 staged\n", encoding="utf-8")
    git(repo, "add", "-N", "moved.txt")
    (repo / "f.txt").unlink()

    import subprocess as _sp

    collapsed = _sp.run(
        ["git", "diff", "--name-only"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.split()
    assert "f.txt" not in collapsed, "rename detection hid it; this is why --no-renames is on both reads"

    assert "f.txt" in cswc.find_stale_staged(repo)


def test_git_names_refuses_a_pathspec_rather_than_matching_nothing(tmp_path: Path) -> None:
    """`-z` is inserted after the subcommand, and a pathspec caller is refused.

    A trailing `-z` after a `--` would be read as a pathspec: the query matches
    nothing, exits 0, and returns an empty set -- a clean verdict over a scope
    that was never read, which is the failure `_git_names` exists to refuse.
    """
    repo = _repo(tmp_path)
    with pytest.raises(RuntimeError, match="pathspec"):
        cswc._git_names(repo, "ls-files", "--", "f.txt")


def test_a_non_utf8_filename_does_not_take_the_gate_down(tmp_path: Path, monkeypatch) -> None:
    """The `surrogateescape` half of the byte-reading repair, pinned.

    The non-ASCII test covers `-z`/`core.quotePath`; this one covers the decode.
    A latin-1 byte sequence is not valid UTF-8, so a strict decode raises
    UnicodeDecodeError -- which is a ValueError, not an OSError, so it would
    escape both handlers and take the hook down with a traceback instead of the
    UNESTABLISHED verdict.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    raw = b"latin\xff.md"
    name = raw.decode("utf-8", errors="surrogateescape")
    (repo / name).write_bytes(b"x\n")
    git(repo, "add", "--", name)
    git(repo, "commit", "-qm", "non-utf8 name")
    git(repo, "rm", "-q", "--cached", "--", name)

    assert cswc.find_stale_staged(repo) == [name]


def test_an_unreadable_path_is_treated_as_present(tmp_path: Path, monkeypatch) -> None:
    """`_on_disk` fails toward PRESENT, because the predicate only ever refuses.

    Guessing "absent" on an OSError (a name too long, a permission on a parent)
    would fail open on exactly the paths hardest to inspect.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    git(repo, "rm", "-q", "--cached", "f.txt")
    (repo / "f.txt").unlink()

    def _raise(_self):
        raise OSError("cannot stat")

    monkeypatch.setattr(Path, "is_symlink", _raise)
    assert cswc._on_disk(repo, "f.txt") is True
    assert cswc.find_stale_staged(repo) == ["f.txt"]
