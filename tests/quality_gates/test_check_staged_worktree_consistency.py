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
import subprocess
import sys
from pathlib import Path

import pytest

from .repo_shapes import install_committed_repo
from .seeding_support import git

ROOT = Path(__file__).resolve().parents[2]

cswc = importlib.import_module("scripts.check_staged_worktree_consistency")


def _repo(tmp_path: Path) -> Path:
    return install_committed_repo(
        tmp_path / "repo",
        {"f.txt": "v1\n", "g.txt": "g1\n"},
        message="init",
    )


def _present(*paths: str) -> object:
    visible = set(paths)
    return lambda path: path in visible


def test_classify_stale_projects_edited_and_orphaned_from_index_sides() -> None:
    edited, orphaned = cswc.classify_stale(
        {"f.txt"}, {"f.txt"}, {"f.txt"}, present=_present("f.txt")
    )
    assert edited == {"f.txt"}
    assert orphaned == set()

    edited, orphaned = cswc.classify_stale({"f.txt"}, set(), set(), present=_present("f.txt"))
    assert edited == set()
    assert orphaned == {"f.txt"}

    edited, orphaned = cswc.classify_stale({"f.txt"}, set(), set(), present=_present())
    assert (edited, orphaned) == (set(), set())


def test_classify_stale_passes_a_clean_full_stage_and_a_fully_applied_deletion() -> None:
    edited, orphaned = cswc.classify_stale({"f.txt"}, set(), {"f.txt"}, present=_present("f.txt"))
    assert (edited, orphaned) == (set(), set())

    edited, orphaned = cswc.classify_stale({"f.txt"}, set(), set(), present=_present())
    assert (edited, orphaned) == (set(), set())

    edited, orphaned = cswc.classify_stale(set(), {"g.txt"}, {"g.txt"}, present=_present())
    assert (edited, orphaned) == (set(), set())


def test_classify_stale_case_fold_requires_the_new_spelling_to_be_staged() -> None:
    edited, orphaned = cswc.classify_stale(
        {"Foo.md", "foo.md"},
        set(),
        {"foo.md"},
        present=_present("Foo.md", "foo.md"),
    )
    assert (edited, orphaned) == (set(), set())

    edited, orphaned = cswc.classify_stale(
        {"Foo.md"},
        set(),
        set(),
        present=_present("Foo.md", "foo.md"),
    )
    assert edited == set()
    assert orphaned == {"Foo.md"}


# --- one node, one question ("what does find_stale_staged/main report over
# this constructed state"), many independent scenarios. Each scenario installs
# its own cheap cached checkout (`install_committed_repo` copies a frozen seed;
# it does not spawn git), so sequencing them here costs no more git than
# separate nodes did and drops eighteen nodes' worth of fixture/collection
# overhead to one. Every scenario keeps the label its prior test name carried
# so a failure inside `_run_stale_staged_case` still names which case broke.


def _case_staged_then_deleted_on_disk(repo: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()  # index holds v2; worktree holds nothing
    assert cswc.find_stale_staged(repo) == ["f.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1


def _case_staged_then_edited(repo: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").write_text("v3\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_falsy_bypass_still_runs_the_gate(repo: Path, monkeypatch) -> None:
    """`CHARNESS_ALLOW_PARTIAL_STAGE=0` must not read as truthy-enabled."""
    monkeypatch.setenv(cswc.ALLOW_ENV, "0")
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    assert cswc.main(["--repo-root", str(repo)]) == 1


def _case_clean_full_stage_passes(repo: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")  # index == worktree
    assert cswc.find_stale_staged(repo) == []
    assert cswc.main(["--repo-root", str(repo)]) == 0


def _case_fully_staged_deletion_passes(repo: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    git(repo, "rm", "-q", "f.txt")  # deletion staged AND applied on disk
    assert cswc.find_stale_staged(repo) == []


def _case_unstaged_only_deletion_passes(repo: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "g.txt").unlink()  # nothing staged for g.txt
    assert cswc.find_stale_staged(repo) == []


def _case_staged_then_typechanged_on_disk(repo: Path, monkeypatch) -> None:
    """A status letter allowlist is the wrong shape for an intersection question.

    The first repair widened `--diff-filter` from `ACM` to `ACMRD`, closing the
    deletion case one letter at a time and leaving `T` (typechange) hidden by the
    same mechanism: stage an edit, then replace the file with a symlink, and the
    unstaged side reports `T`, which `ACMRD` drops. The gate then passed a staged
    blob that no worktree-walking validator ever inspected.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    (repo / "f.txt").symlink_to("/etc/hostname")
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_untracked_but_still_on_disk(repo: Path, monkeypatch) -> None:
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
    git(repo, "rm", "-q", "--cached", "f.txt")  # index: deleted; disk: still there
    assert (repo / "f.txt").exists()
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_untracked_but_still_on_disk_edited(repo: Path, monkeypatch) -> None:
    """The full escape: editing the on-disk copy is what cleared check_staged_reversion."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    git(repo, "rm", "-q", "--cached", "f.txt")
    (repo / "f.txt").write_text("edited after untracking\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_ignored_orphan_is_visible(repo: Path, monkeypatch) -> None:
    """The staged deletion record remains even when the on-disk copy is ignored."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / ".gitignore").write_text("f.txt\n", encoding="utf-8")
    git(repo, "add", ".gitignore")
    git(repo, "commit", "-qm", "ignore tracked fixture")
    git(repo, "rm", "-q", "--cached", "f.txt")
    assert (repo / "f.txt").exists()
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_rename_source_recreated_is_flagged(repo: Path, monkeypatch) -> None:
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
    git(repo, "mv", "f.txt", "renamed.txt")
    (repo / "f.txt").write_text("recreated on disk\n", encoding="utf-8")

    # The letter-based query the first cut used sees nothing here.
    letters = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=D"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert letters == [], "rename detection collapsed the D; this is why the query changed"

    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_plain_rename_still_passes(repo: Path, monkeypatch) -> None:
    """Control for the rename-recreated case above: an ordinary rename must NOT be refused."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    git(repo, "mv", "f.txt", "renamed.txt")  # source gone from disk, as normal
    assert cswc.find_stale_staged(repo) == []


def _case_dangling_symlink_at_orphaned_path(repo: Path, monkeypatch) -> None:
    """`exists()` follows symlinks, so a broken one read as `gone` and failed open.

    A worktree walker still trips over the entry, which is what the predicate is
    actually asking about.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    git(repo, "rm", "-q", "--cached", "f.txt")
    (repo / "f.txt").unlink()
    (repo / "f.txt").symlink_to(repo / "nonexistent-target")
    assert not (repo / "f.txt").exists()  # the old predicate said "gone"
    assert (repo / "f.txt").is_symlink()  # a walker still sees it
    assert cswc.find_stale_staged(repo) == ["f.txt"]


def _case_non_ascii_orphaned_path(repo: Path, monkeypatch) -> None:
    """`core.quotePath` is ON by git default and renders a non-ASCII path as the
    literal characters `"docs/\\303\\251.md"`, which no filesystem test matches.

    `-z` makes git emit raw bytes and stop C-quoting. Forced ON here so the test
    fails against a `text=True` reader regardless of the developer's git config.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    name = "é.md"
    (repo / name).write_text("x\n", encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-qm", "non-ascii")
    git(repo, "config", "core.quotePath", "true")
    git(repo, "rm", "-q", "--cached", name)
    assert cswc.find_stale_staged(repo) == [name]


def _case_non_utf8_filename(repo: Path, monkeypatch) -> None:
    """The `surrogateescape` half of the byte-reading repair, pinned.

    The non-ASCII case above covers `-z`/`core.quotePath`; this one covers the
    decode. A latin-1 byte sequence is not valid UTF-8, so a strict decode raises
    UnicodeDecodeError -- which is a ValueError, not an OSError, so it would
    escape both handlers and take the hook down with a traceback instead of the
    UNESTABLISHED verdict.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    raw = b"latin\xff.md"
    name = raw.decode("utf-8", errors="surrogateescape")
    (repo / name).write_bytes(b"x\n")
    git(repo, "add", "--", name)
    git(repo, "commit", "-qm", "non-utf8 name")
    git(repo, "rm", "-q", "--cached", "--", name)
    assert cswc.find_stale_staged(repo) == [name]


def _case_only_respelling_is_not_an_orphan(repo: Path, monkeypatch) -> None:
    """On a case-insensitive filesystem `Foo.md` -> `foo.md` stages a deletion of
    the old spelling while `lexists` resolves it to the NEW file, so the gate would
    refuse a legitimate rename -- and both offered remedies would be harmful there.

    NOT a case-insensitive-filesystem test: this suite runs on Linux, so the state
    is constructed directly (old spelling staged-deleted, new spelling tracked, old
    spelling present on disk) to pin the case-folded exemption itself. What runs on
    macOS/Windows is the same predicate over a state their filesystem produces.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "Foo.md").write_text("v1\n", encoding="utf-8")
    git(repo, "add", "Foo.md")
    git(repo, "commit", "-qm", "add Foo.md")
    git(repo, "mv", "Foo.md", "foo.md")
    (repo / "Foo.md").write_text("v1\n", encoding="utf-8")  # what a case-insensitive FS shows
    assert cswc.find_stale_staged(repo) == []


def _case_folded_exemption_does_not_fire_on_unrelated_path(repo: Path, monkeypatch) -> None:
    """Round-2 finding: the case-only-rename exemption was a fail-open.

    Folding over the whole tracked set made the exemption fire on coincidence.
    With `Foo.md` and `foo.md` both tracked -- legal on Linux, where this hook
    runs -- untracking `Foo.md` while it stays on disk returned `[]`. The evidence
    of a re-spelling is that the new spelling is also STAGED, so the fold is over
    `staged & tracked`.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "Foo.md").write_text("upper\n", encoding="utf-8")
    (repo / "foo.md").write_text("lower\n", encoding="utf-8")
    git(repo, "add", "Foo.md", "foo.md")
    git(repo, "commit", "-qm", "both spellings tracked")
    git(repo, "rm", "-q", "--cached", "Foo.md")  # untrack ONE of them
    assert (repo / "Foo.md").exists()
    assert cswc.find_stale_staged(repo) == ["Foo.md"]


def _case_intent_to_add_rename_does_not_hide_deletion(repo: Path, monkeypatch) -> None:
    """Round-2 finding: `--no-renames` was on the staged read only.

    Index-vs-worktree rename detection collapses `D a` + `A b` into one `R` entry
    printing only the destination when the destination is an intent-to-add entry
    -- which is what `git add -p` creates for a new file. `a` then dropped out of
    the unstaged set, out of the intersection, and the ORIGINAL shape-1 defect
    (staged, then deleted on disk) was reachable again.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    (repo / "f.txt").write_text("v2 staged\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    (repo / "moved.txt").write_text("v2 staged\n", encoding="utf-8")
    git(repo, "add", "-N", "moved.txt")
    (repo / "f.txt").unlink()

    collapsed = subprocess.run(
        ["git", "diff", "--name-only"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.split()
    assert "f.txt" not in collapsed, (
        "rename detection hid it; this is why --no-renames is on both reads"
    )

    assert "f.txt" in cswc.find_stale_staged(repo)


_STALE_STAGED_CASES = {
    "staged-then-deleted-on-disk": _case_staged_then_deleted_on_disk,
    "staged-then-edited": _case_staged_then_edited,
    "falsy-bypass-still-runs-the-gate": _case_falsy_bypass_still_runs_the_gate,
    "clean-full-stage-passes": _case_clean_full_stage_passes,
    "fully-staged-deletion-passes": _case_fully_staged_deletion_passes,
    "unstaged-only-deletion-passes": _case_unstaged_only_deletion_passes,
    "staged-then-typechanged-on-disk": _case_staged_then_typechanged_on_disk,
    "untracked-but-still-on-disk": _case_untracked_but_still_on_disk,
    "untracked-but-still-on-disk-edited": _case_untracked_but_still_on_disk_edited,
    "ignored-orphan-is-visible": _case_ignored_orphan_is_visible,
    "rename-source-recreated-is-flagged": _case_rename_source_recreated_is_flagged,
    "plain-rename-still-passes": _case_plain_rename_still_passes,
    "dangling-symlink-at-orphaned-path": _case_dangling_symlink_at_orphaned_path,
    "non-ascii-orphaned-path": _case_non_ascii_orphaned_path,
    "non-utf8-filename": _case_non_utf8_filename,
    "case-only-respelling-is-not-an-orphan": _case_only_respelling_is_not_an_orphan,
    "case-folded-exemption-does-not-fire-on-unrelated-path": _case_folded_exemption_does_not_fire_on_unrelated_path,
    "intent-to-add-rename-does-not-hide-deletion": _case_intent_to_add_rename_does_not_hide_deletion,
}


@pytest.mark.boundary_contract(reason="real Git constructs and inspects staged rename/index states")
def test_stale_staged_classification_cases(tmp_path: Path, monkeypatch) -> None:
    """Eighteen independent `find_stale_staged`/`main` scenarios, one node.

    Each case below used to be its own test function; the docstring on each
    `_case_*` helper is that former test's rationale, kept next to the scenario
    it explains. A failure names the exact `_case_*` function in its traceback,
    so which former test broke is never ambiguous. Cases install their own
    checkout (a cached-seed copy, not a git spawn) and do not share state with
    each other.
    """
    for label, case in _STALE_STAGED_CASES.items():
        repo = _repo(tmp_path / label)
        case(repo, monkeypatch)


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


def test_env_values_that_enable_or_disable_the_bypass(monkeypatch) -> None:
    for value in ("0", "false", "no", "off", "", "  ", "FALSE"):
        monkeypatch.setenv(cswc.ALLOW_ENV, value)
        assert cswc.allow_partial_stage() is False, repr(value)
    for value in ("1", "true", "YES", " on "):
        monkeypatch.setenv(cswc.ALLOW_ENV, value)
        assert cswc.allow_partial_stage() is True, repr(value)
    assert cswc.main(["--repo-root", "/nonexistent"]) == 0


def test_untrack_remedy_is_not_git_add_and_actually_runs(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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
    git(repo, "rm", "-q", "--cached", "f.txt")  # orphaned
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


def test_orphan_remedy_enumeration_is_capped(tmp_path: Path, monkeypatch, capsys) -> None:
    """`git rm -r --cached <dir>` can orphan thousands of paths; an uncapped list
    buries the bypass line printed after it."""
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    paths = {f"vendored/f{index}.txt" for index in range(25)}
    monkeypatch.setattr(cswc, "_classify_stale", lambda _repo: (set(), paths))

    assert cswc.main(["--repo-root", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "and 15 more path(s) in the same state" in err
    # The count, not just the trailer: a regression that enumerates all 25 pairs
    # AND appends the "... and 15 more" line would satisfy the trailer assertion
    # while the harm the cap exists to prevent is fully present.
    assert err.count("\n  rm ") == 10
    assert err.rstrip().endswith("commit.)")


def test_classification_uses_one_status_snapshot(tmp_path: Path, monkeypatch) -> None:
    calls: list[list[str]] = []

    def _status(command, **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "1 MM x x x x x x f.txt\0", "")

    monkeypatch.setattr(cswc, "run_process", _status)

    assert cswc._classify_stale(tmp_path) == ({"f.txt"}, set())
    assert calls == [["git", *cswc._STAGED_STATUS_ARGS]]


# --- one node: `_status_paths` reading a mocked `subprocess.run` output and
# refusing rather than reading a bad or absent status as clean. Each case
# swaps in one bad `subprocess.run` and expects a RuntimeError; the specific
# match text (or its absence) is the discriminator between cases.


def _status_case_git_missing(monkeypatch) -> None:
    """The OSError twin of a nonzero git exit: `git` missing, or an unusable cwd,
    raises before a returncode exists. An empty set from that path is
    indistinguishable from "nothing staged"."""

    def _boom(*_args, **_kwargs):
        raise FileNotFoundError("No such file or directory: 'git'")

    monkeypatch.setattr(cswc, "run_process", _boom)
    with pytest.raises(RuntimeError) as excinfo:
        cswc._status_paths(Path("/unused"))
    assert "git" in str(excinfo.value)


def _status_case_unexpected_rename_record(monkeypatch) -> None:
    monkeypatch.setattr(
        cswc,
        "run_process",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, "2 R. x x x x x x R100 new.txt\0old.txt\0", ""
        ),
    )
    with pytest.raises(RuntimeError, match="rename despite --no-renames"):
        cswc._status_paths(Path("/unused"))


def _status_case_malformed_records(monkeypatch) -> None:
    for stdout in (
        "1 .. x x x x x x f.txt\0",
        "1 Z. x x x x x x f.txt\0",
        "? stray.txt\0",
        "! ignored.txt\0",
    ):
        monkeypatch.setattr(
            cswc,
            "run_process",
            lambda *_args, captured=stdout, **_kwargs: subprocess.CompletedProcess(
                [], 0, captured, ""
            ),
        )
        with pytest.raises(RuntimeError):
            cswc._status_paths(Path("/unused"))


def test_status_snapshot_never_reads_a_bad_status_as_clean(tmp_path: Path, monkeypatch) -> None:
    """`_status_paths` must refuse rather than turn a failure into an empty,
    clean-looking result, whichever way the read fails: git entirely absent, a
    well-formed record the parser cannot trust, or outright malformed lines."""
    _status_case_git_missing(monkeypatch)
    _status_case_unexpected_rename_record(monkeypatch)
    _status_case_malformed_records(monkeypatch)


def test_an_unreadable_path_is_treated_as_present(tmp_path: Path, monkeypatch) -> None:
    """`_on_disk` fails toward PRESENT, because the predicate only ever refuses.

    Guessing "absent" on an OSError (a name too long, a permission on a parent)
    would fail open on exactly the paths hardest to inspect.
    """

    def _raise(_self):
        raise OSError("cannot stat")

    monkeypatch.setattr(Path, "is_symlink", _raise)
    assert cswc._on_disk(tmp_path, "f.txt") is True


@pytest.mark.boundary_contract(
    reason=(
        "__main__ dispatch smoke: the scheduled ARGV puts only scripts/ on sys.path, "
        "so each gate must be runnable as a program without the test runner's package path"
    )
)
@pytest.mark.parametrize(
    "script",
    [
        "check_staged_worktree_consistency.py",
        "check_staged_reversion.py",
        "check_staged_router_change.py",
    ],
)
def test_index_hygiene_gates_import_through_their_scheduled_argv(script: str) -> None:
    """`python3 scripts/<gate>.py --repo-root .` must not die at import.

    That argv is what `staged_commit_gate_plan_helpers.index_hygiene_gates` builds,
    and it puts `<repo>/scripts` on `sys.path` WITHOUT the repo root. This gate
    imported `scripts.git_status_snapshot`, which imports `scripts.git_checkout` in
    turn, so it raised `ModuleNotFoundError: No module named 'scripts'` and could
    not run at all -- while every test passed, because tests import it in-process.
    """
    result = subprocess.run(
        [sys.executable, f"scripts/{script}", "--repo-root", "."],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert "ModuleNotFoundError" not in result.stderr, result.stderr
