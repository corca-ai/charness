"""Behavior pins for the checkout-facts seams whose degraded arms had no executed
test when the v8.0.2 release lane measured them.

Most of what is pinned here is a "the environment did not cooperate" arm -- an
unreadable administration file, a process whose working directory was removed
underneath it, a status Git refused to produce -- where the arm decides whether
a caller gets a verdict or a traceback out of a gate. Some are ordinary parsing
and routing paths that happened to be uncovered. A test here aims to name an
operator-visible consequence rather than the line it executes.

Its companion, `test_batch8.py`, covers the other half of the same release
measurement: the layout a packaged script actually runs in, plus the task-run,
reviewed-input, and release surfaces that consume these facts.

On test doubles, and why this paragraph does not characterise them. Some arms
here are reproduced from real environment state; some are reached with a double.
Three consecutive review rounds caught this docstring getting that summary wrong,
each time in the direction of claiming more than the file delivers: first that
the `Path.resolve` cases were the only doubles, then omitting the
`FactsCheckout` seam, then asserting no real state could reach a doubled arm --
while `test_batch8.py` reproduces one of those very conditions (`git` absent from
`PATH`) for real. A summary that has been wrong three times is not worth a
fourth attempt.

So: read the test. Each one states the method it used and why that method, and
that statement is the one to trust. `monkeypatch.setattr`, `FactsCheckout`, and
`monkeypatch.setenv` are where the doubles live if you want to find them
yourself.
"""

from __future__ import annotations

import errno
import os
import subprocess
from pathlib import Path

import pytest

from scripts import (
    changed_line_run_trust,
    check_prose_pin,
    checkout_view,
    mutation_changed_files_lib,
    premise_preflight_lib,
    surfaces_lib,
    task_run_state,
    worktree_cleanup_lib,
)
from scripts import check_staged_worktree_consistency as staged_consistency
from scripts import classify_t_signal as t_signal
from scripts import git_checkout as checkout
from scripts import git_status_snapshot as status_snapshot
from scripts import premise_git_snapshot as premise_snapshot
from scripts import worktree_doctor_checks as worktree_checks
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]

DUP_RATCHET_GIT = load_script_module(
    "dup_ratchet_git_batch7", ROOT / "skills/public/quality/scripts/dup_ratchet_git.py"
)


def _install_git_dir(
    repo: Path, *, head: str = "ref: refs/heads/main\n", broken_config: bool = False
) -> Path:
    """A `.git` directory with the signature `git_dir_at` requires, no Git run.

    `broken_config` additionally writes a config Git itself rejects, which is how
    a tree can pass the on-disk discovery preflight and still fail in Git.
    """
    git_dir = repo / ".git"
    (git_dir / "objects").mkdir(parents=True)
    (git_dir / "refs" / "heads").mkdir(parents=True)
    (git_dir / "HEAD").write_text(head, encoding="utf-8")
    if broken_config:
        (git_dir / "config").write_text("[core\n  unterminated section\n", encoding="utf-8")
    return git_dir


# --- scripts/git_checkout: reading Git's own files ------------------------------


def test_an_unreadable_gitfile_names_no_git_dir_instead_of_raising(tmp_path: Path) -> None:
    """A `.git` FILE the process cannot read yields "no administration directory",
    not a `PermissionError` out of a callers' preflight.

    This projection is the first thing several gates ask, before they decide
    whether to spawn Git at all. Letting the read escape would replace a
    `not a checkout` verdict with a traceback from inside the gate, in the one
    environment (a worktree owned by another user) where the operator most needs
    to be told which repository was refused.
    """
    repo = tmp_path / "unreadable"
    repo.mkdir()
    marker = repo / ".git"
    marker.write_text("gitdir: /somewhere/real\n", encoding="utf-8")
    marker.chmod(0o000)
    try:
        assert checkout.git_dir_at(repo) is None
        assert checkout.local_checkout(repo) is False
    finally:
        marker.chmod(0o600)


def test_a_gitfile_without_a_gitdir_line_names_no_git_dir(tmp_path: Path) -> None:
    """A `.git` file whose content is not a `gitdir:` pointer names nothing.

    A stray file called `.git` is not a worktree link. Treating "it parsed as
    text" as "it is a checkout" would send the layout projection off to whatever
    the first line happened to spell.
    """
    repo = tmp_path / "stray"
    repo.mkdir()
    (repo / ".git").write_text("this is not a worktree link\n", encoding="utf-8")

    assert checkout.git_dir_at(repo) is None
    assert checkout.local_checkout(repo) is False


def test_a_relative_gitdir_is_read_against_the_repo_root(tmp_path: Path) -> None:
    """`gitdir: ../shared/.git/worktrees/w` resolves against the worktree root.

    Git writes the pointer relative when it can. Reading it as
    process-relative would aim every linked-worktree projection at the caller's
    working directory instead of the worktree that owns the file.
    """
    repo = tmp_path / "linked"
    repo.mkdir()
    (tmp_path / "admin").mkdir()
    (repo / ".git").write_text("gitdir: ../admin\n", encoding="utf-8")

    assert checkout.git_dir_at(repo) == repo / "../admin"


def test_a_regular_file_is_neither_discoverable_nor_a_worktree_root(tmp_path: Path) -> None:
    """A path that names a FILE is not a repository root.

    Both projections take a `repo_root` argument from an operator or an adapter,
    so a path naming a file is an ordinary input mistake. It has to come back as
    "not a checkout", because the caller's next move on a `True` here is to spawn
    Git against a non-directory.
    """
    not_a_directory = tmp_path / "file.txt"
    not_a_directory.write_text("x\n", encoding="utf-8")

    assert checkout.discoverable(not_a_directory) is False
    assert checkout.worktree_root_from_files(not_a_directory) is None


def test_no_ancestor_carrying_git_means_no_worktree_root(tmp_path: Path) -> None:
    """A directory with no repository anywhere above it projects no root.

    `None` is the signal that sends a caller to `git rev-parse` (or to a
    refusal). Returning the input path as a "root" would make every git-less
    temporary directory look like a checkout of itself.
    """
    plain = tmp_path / "plain"
    plain.mkdir()

    assert checkout.worktree_root_from_files(plain) is None


def test_a_removed_working_directory_projects_nothing_rather_than_raising(
    tmp_path: Path,
) -> None:
    """When the process working directory has been REMOVED, every file
    projection over a relative root refuses instead of raising.

    This is the real condition the `except OSError` arms exist for: resolving a
    relative path calls `getcwd()`, which fails with `ENOENT` once the directory
    the process is sitting in has been deleted. Long-running gates and worktree
    cleanup are exactly the callers that can be standing in a directory another
    step just removed, and a traceback there is indistinguishable from the tool
    crashing on the repository rather than on its own footing.
    """
    doomed = tmp_path / "doomed"
    doomed.mkdir()
    previous = os.getcwd()
    os.chdir(doomed)
    try:
        doomed.rmdir()
        relative = Path("anything")

        assert checkout.discoverable(relative) is False
        assert checkout.is_bare_repository(relative) is False
        assert checkout.worktree_root_from_files(relative) is None
        assert checkout.layout_from_files(relative) is None
        assert checkout.identity_from_files(relative) is None
    finally:
        os.chdir(previous)


def test_a_detached_head_written_as_a_raw_oid_is_read_without_git(tmp_path: Path) -> None:
    """A detached `HEAD` holding an object id IS the answer; no ref to follow.

    Callers use this projection to avoid spawning `git rev-parse`. Reading only
    the `ref:` form would silently fall through to `None` for every detached
    checkout -- which is the state a bisect, a tag checkout, and most CI
    checkouts are in.
    """
    repo = tmp_path / "detached"
    repo.mkdir()
    oid = "0" * 39 + "1"
    _install_git_dir(repo, head=f"{oid}\n")

    assert checkout.head_oid_from_files(repo) == oid


def test_a_head_ref_whose_target_is_not_an_object_id_names_no_head(tmp_path: Path) -> None:
    """A ref file holding something that is not an oid yields `None`.

    `None` routes the caller to Git. Returning the file's bytes would hand a
    packed-refs placeholder, a stale editor artifact, or a truncated write to
    callers that go on to use it as a commit id.
    """
    repo = tmp_path / "malformed"
    repo.mkdir()
    git_dir = _install_git_dir(repo)
    (git_dir / "refs" / "heads" / "main").write_text("not-an-object-id\n", encoding="utf-8")

    assert checkout.head_oid_from_files(repo) is None


def test_an_empty_commondir_file_yields_no_layout(tmp_path: Path) -> None:
    """A truncated `commondir` is an unusable layout, not an empty common dir.

    `commondir` is what a linked worktree uses to find the shared object store.
    A zero-byte one (an interrupted `git worktree add`) has to come back as
    "no layout" so the caller falls back to Git, rather than as a layout whose
    common directory is the empty path.
    """
    repo = tmp_path / "truncated"
    repo.mkdir()
    git_dir = _install_git_dir(repo)
    (git_dir / "commondir").write_text("", encoding="utf-8")

    assert checkout._common_dir_for(git_dir) is None
    assert checkout.layout_from_files(repo) is None


def test_an_unresolvable_administration_path_yields_no_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When an administration directory cannot be RESOLVED, the projection
    refuses; it does not let the error reach the caller.

    Fault-injected on purpose: after the caller has made the path absolute,
    CPython 3.10's non-strict `resolve()` swallows every filesystem error except
    a symlink loop, which it re-raises as `RuntimeError`. So no real directory
    state reaches this arm, and the choice is between injecting the failure here
    or deleting a guard that keeps an `ELOOP`-adjacent administration path from
    surfacing as a traceback inside a release gate.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    git_dir = _install_git_dir(repo)
    real_resolve = Path.resolve

    def refusing_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if self == git_dir:
            raise OSError(errno.ELOOP, "Too many levels of symbolic links")
        return real_resolve(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "resolve", refusing_resolve)

    assert checkout.layout_from_files(repo) is None


def test_an_unresolvable_common_dir_yields_no_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same refusal one level in: a `commondir` naming a path that will not
    resolve is no common directory at all.

    Fault-injected for the reason above. The arm matters because the common
    directory is where the shared object store lives: reporting an unresolved
    one as a layout would send a caller's object lookups at a path Git itself
    could not follow.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    git_dir = _install_git_dir(repo)
    shared = tmp_path / "shared"
    shared.mkdir()
    (git_dir / "commondir").write_text(f"{shared}\n", encoding="utf-8")
    real_resolve = Path.resolve

    def refusing_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if self == shared:
            raise OSError(errno.ELOOP, "Too many levels of symbolic links")
        return real_resolve(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "resolve", refusing_resolve)

    assert checkout._common_dir_for(git_dir) is None
    assert checkout.layout_from_files(repo) is None


def test_git_env_redirection_refuses_every_file_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With `GIT_DIR` set, on-disk files no longer describe the checkout Git
    would use, so the file projections decline rather than answer from them.

    Declining is what makes the fast path safe: a caller that skipped
    `git rev-parse` because these helpers answered would otherwise be reading a
    DIFFERENT repository than the one the environment redirects Git to.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _install_git_dir(repo)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "elsewhere"))

    assert checkout.worktree_root_from_files(repo) is None
    assert checkout.identity_from_files(repo) is None


def test_a_bare_repository_has_a_layout_but_projects_no_file_identity(
    tmp_path: Path,
) -> None:
    """A bare repository yields a layout and NO identity.

    Identity carries a HEAD oid, and the HEAD projection only looks inside a
    `.git` marker, which a bare repository does not have. `None` sends the caller
    to Git; a partial identity would carry a layout beside a HEAD nobody read.
    """
    bare = tmp_path / "bare.git"
    (bare / "objects").mkdir(parents=True)
    (bare / "refs").mkdir()
    (bare / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    layout = checkout.layout_from_files(bare)
    assert layout is not None
    assert layout.git_dir == bare and layout.common_dir == bare
    assert checkout.head_oid_from_files(bare) is None
    assert checkout.identity_from_files(bare) is None


# --- scripts/premise_git_snapshot: batched vs individual object reads -----------


def test_a_commit_payload_with_no_blank_line_carries_no_parents_and_no_message() -> None:
    """A commit object whose header/body separator is absent parses to empty.

    The premise walk feeds whatever `git cat-file` handed back into this parser.
    Treating a separator-less payload as one long header would make every line of
    it look like a candidate `parent ` field, so a truncated read would inject
    parent shas that do not exist into the walk.
    """
    assert premise_snapshot._commit_parents_and_message(b"tree abc\nauthor nobody") == ([], "")


def test_a_parent_git_cannot_supply_stops_the_history_walk_with_no_verdict(
    tmp_path: Path,
) -> None:
    """When the parent chain cannot be read, the walk returns `None`, not `False`.

    `False` means "the line is not in this history"; `None` means "this history
    could not be read". The premise preflight refuses on `None` and proceeds on
    `False`, so collapsing them would let an unreadable object store read as a
    clean absence -- the shape a preflight exists to prevent.
    """
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    payload = b"tree t\nparent " + b"a" * 40 + b"\n\nsubject\n"

    assert (
        premise_snapshot.history_contains_exact_line(not_a_repo, "h" * 40, payload, "marker")
        is None
    )


def test_a_parent_that_is_not_a_commit_stops_the_walk_with_no_verdict(
    tmp_path: Path,
) -> None:
    """A parent expression that resolves to nothing (or to a non-commit) is also
    "could not read", not "not found".

    Same distinction one layer in: `git cat-file --batch` answers `missing` for an
    absent object and reports a type for a present one. Appending a blob's bytes
    to the commit queue would parse tree/blob content as commit headers.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    payload = b"tree t\nparent " + b"0" * 40 + b"\n\nsubject\n"

    assert (
        premise_snapshot.history_contains_exact_line(repo, "h" * 40, payload, "marker")
        is None
    )


def test_a_path_containing_a_newline_is_snapshotted_one_object_at_a_time(
    tmp_path: Path,
) -> None:
    """A protected path spelling a newline routes to the per-object snapshot and
    still reports modes, objects, HEAD, and the index side.

    `git cat-file --batch` is newline-delimited, so a path carrying one would
    desynchronise the batch protocol and every object after it would be read
    against the wrong expression. The individual lane exists for exactly that
    input, and it has to return the SAME shape -- a caller that got a snapshot
    missing its HEAD or index side would compare a captured tree against nothing.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})

    snapshot = premise_snapshot.inspect_captured_tree(
        repo, "HEAD", ["tracked.py"], ["absent\nname.txt"]
    )

    assert snapshot.available is True
    assert snapshot.commit_exists is True
    assert snapshot.modes["tracked.py"] == "100644"
    assert snapshot.objects["tracked.py"] == ("blob", b"base\n")
    assert snapshot.objects["absent\nname.txt"] is None
    assert snapshot.current_head_sha is not None
    assert snapshot.current_head_commit is not None
    assert snapshot.index_objects["tracked.py"] == ("blob", b"base\n")


def test_an_unreadable_head_and_index_batch_reports_every_path_as_unknown(
    tmp_path: Path,
) -> None:
    """When Git cannot answer at all, HEAD is `None` and EVERY protected path maps
    to `None` -- an explicit unknown per path, not a missing key.

    The consumer indexes this dict by path. Returning an empty dict on failure
    would raise a `KeyError` inside the preflight, and returning a partially
    populated one would let "Git never answered" read as "the index has no such
    entry", which is the drift the snapshot exists to detect.
    """
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()

    head_sha, head_commit, index_objects = premise_snapshot._head_and_index(
        not_a_repo, ["a.txt", "b.txt"]
    )

    assert head_sha is None
    assert head_commit is None
    assert index_objects == {"a.txt": None, "b.txt": None}


# --- scripts/classify_t_signal --------------------------------------------------


def test_a_repository_with_no_commit_yet_classifies_as_diff_unavailable(
    tmp_path: Path,
) -> None:
    """An unborn HEAD is "no diff to read", and naming an explicit sha in that
    same repository is "no parent".

    The two reasons route differently downstream: `diff_unavailable` says the
    classifier could not look, while the parent reasons say it looked and the
    history ends. Reporting an unborn repository as `no_parent` would claim a
    history was inspected when `git log` never produced one.
    """
    repo = tmp_path / "unborn"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    assert t_signal.classify_t_signal(repo)["skipped_reason"] == "diff_unavailable"
    assert t_signal.classify_t_signal(repo, head_sha="0" * 40)["skipped_reason"] == "no_parent"


def test_a_truncated_or_headless_commit_record_yields_no_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `git log` record that does not carry all three NUL-separated fields, or
    carries an empty sha, resolves to no metadata.

    Fault-injected: the pinned `--format` always emits three separators for a
    real commit, so no repository state reaches these arms. They matter anyway --
    unpacking a short split would raise `ValueError` inside the classifier, and an
    empty sha would be carried into `git diff <parent>..<empty>` and silently
    diff against the working tree.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    def truncated(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, stdout="only-one-field", stderr="")

    monkeypatch.setattr(t_signal, "_run_git", truncated)
    assert t_signal._commit_metadata_snapshot(repo, None) is None

    def empty_head(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, stdout="\0parent\0message\0", stderr="")

    monkeypatch.setattr(t_signal, "_run_git", empty_head)
    assert t_signal._commit_metadata_snapshot(repo, None) is None


def test_a_history_without_the_deferred_decisions_doc_declares_no_decision_ids(
    tmp_path: Path,
) -> None:
    """A ref that does not carry the decisions document contributes no ids.

    The classifier compares the id sets at two refs to decide whether a slice
    ADDED a deferred decision. An unreadable `git show` has to contribute the
    empty set rather than propagate an error, or the first repository that has
    never had the document would make the whole classification fail instead of
    reporting no deferred-decision signal.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})

    assert t_signal._deferred_decision_ids(repo, "HEAD") == set()


# --- scripts/worktree_doctor_checks ---------------------------------------------


def test_a_git_output_path_that_cannot_be_resolved_names_no_path(tmp_path: Path) -> None:
    """A symlink cycle in Git's answer resolves to `None`, not a `RuntimeError`.

    `charness worktree doctor` reads these paths out of Git's own output and then
    reports on them. A cycle is a real thing an operator can create, and the
    doctor's job in that case is to say the path is unusable -- crashing would
    take out every OTHER check in the same run.
    """
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.symlink_to(right)
    right.symlink_to(left)

    assert worktree_checks._resolved_git_output_path(tmp_path, str(left)) is None


def test_an_empty_hookspath_setting_is_skipped_for_a_later_real_one(tmp_path: Path) -> None:
    """`hooksPath =` with no value declares nothing; the next setting still counts.

    An empty value is what a half-edited config leaves behind. Accepting it would
    make the doctor report the repository root as the hooks directory and then
    announce every file in the repo as an unexpected hook.
    """
    git_dir = _install_git_dir(tmp_path / "repo")
    (git_dir / "config").write_text(
        "[core]\n\thooksPath =\n\thooksPath = custom-hooks\n", encoding="utf-8"
    )
    layout = checkout.CheckoutLayout(git_dir, git_dir)

    assert worktree_checks._hooks_path_from_layout(tmp_path / "repo", layout) == (
        tmp_path / "repo" / "custom-hooks"
    )


def test_an_unresolvable_hooks_path_is_reported_unresolved_rather_than_dropped(
    tmp_path: Path,
) -> None:
    """When the hooks path cannot be resolved, the UNRESOLVED path is still
    reported -- the doctor names something rather than nothing.

    Produced for real by removing the process working directory, which is what
    makes resolving a relative path fail. Falling back to the literal path keeps
    the doctor's message actionable ("hooks are configured at `custom-hooks`")
    instead of silently reporting the default `hooks` directory, which would tell
    the operator their configured hooks are missing from a place they never
    configured.
    """
    repo = tmp_path / "repo"
    git_dir = _install_git_dir(repo)
    (git_dir / "config").write_text("[core]\n\thooksPath = custom-hooks\n", encoding="utf-8")
    layout = checkout.CheckoutLayout(git_dir, git_dir)
    doomed = tmp_path / "doomed"
    doomed.mkdir()
    previous = os.getcwd()
    os.chdir(doomed)
    try:
        doomed.rmdir()

        assert worktree_checks._hooks_path_from_layout(Path("relative"), layout) == Path(
            "relative/custom-hooks"
        )
    finally:
        os.chdir(previous)


# --- scripts/checkout_view ------------------------------------------------------


def test_an_unlisted_checkout_answers_unknown_rather_than_untracked(tmp_path: Path) -> None:
    """With no file listing available, tracked-ness is `None`, never `False`.

    `False` means "Git listed the tree and this path is not in it"; `None` means
    "nothing was listed". Callers gate destructive cleanup on this answer, so
    collapsing the two would let an unavailable listing read as "this path is
    untracked" and authorise the deletion the distinction exists to prevent.

    Reached through `FactsCheckout`, an injected checkout view, because the
    unavailable listing is the input under test rather than something a real
    checkout can be asked to produce on demand.
    """
    view = checkout_view.FactsCheckout(tmp_path, files=None)

    assert checkout_view.path_is_tracked(view, "anything.py") is None


def test_a_listed_path_outside_the_repo_is_skipped_not_matched(tmp_path: Path) -> None:
    """A listed path that does not live under the checkout root is passed over,
    and the scan continues to the paths that do.

    Aborting on the first outside path would make the whole tracked-ness answer
    depend on listing order. `continue` is what keeps one stray absolute entry --
    an alternate object store, a linked worktree's own listing -- from hiding
    every path after it.

    The listing is injected through `FactsCheckout`: no real `git ls-files` over
    this checkout would emit a path outside it, which is exactly why the guard is
    unreachable without a double.
    """
    view = checkout_view.FactsCheckout(
        tmp_path, files=[Path("/elsewhere/stray.py"), tmp_path / "owned.py"]
    )

    assert checkout_view.path_is_tracked(view, "owned.py") is True
    assert checkout_view.path_is_tracked(view, "absent.py") is False


# --- scripts/task_run_state -----------------------------------------------------


def _execution(**overrides: object) -> dict:
    base = {"interrupted": False, "timed_out": False, "exit_code": 0, "exec_error": None}
    base.update(overrides)
    return base


def test_a_child_that_never_produced_an_exit_code_is_a_failed_run() -> None:
    """A spawn error, or no exit code at all, is `failed` -- in BOTH derivations.

    The two derivations answer different questions about the same run (what to
    report, and whether to checkpoint the worktree), and their predicate order is
    deliberately identical. Pinning both here is what stops a run from being
    reported `completed` while its worktree is checkpointed as abnormal, which is
    the disagreement the duplication exists to prevent.
    """
    exec_error = _execution(exit_code=None, exec_error="No such file or directory")

    assert task_run_state._execution_state(exec_error, {"status": "delivered"}) == "failed"
    assert task_run_state._abnormal_exit_state(exec_error) == "failed"


def test_an_abnormal_exit_without_a_wip_commit_is_refused_not_reported() -> None:
    """An abnormal exit with no checkpoint commit raises rather than reporting a
    candidate whose work is nowhere.

    The WIP commit IS the untyped work. Emitting a `wip` candidate with no commit
    would hand the parent a record pointing at nothing, and the next step -- read
    the candidate, decide whether to keep it -- has nothing to read.
    """
    with pytest.raises(task_run_state.TaskRunError, match="missing its WIP candidate commit"):
        task_run_state._candidate_result_state(
            execution_state="timed-out",
            scope={
                "verdict": task_run_state.PASS,
                "changed_paths": ["a.py"],
                "candidate_carrier": {},
            },
            parent_progress={"blocking": False},
            candidate_commit=None,
        )


def test_a_clean_non_delivery_keeps_its_own_execution_state() -> None:
    """A run that exited cleanly, changed nothing, and delivered nothing keeps
    `non-delivery` as its reported state.

    None of the earlier arms fit: it is not `completed` (nothing was delivered),
    not a partial result (nothing changed), and not `failed` (the child exited 0
    and the scope validated). Rewriting it to `failed` would report a clean
    no-op child as a broken one.
    """
    candidate, state = task_run_state._candidate_result_state(
        execution_state="non-delivery",
        scope={"verdict": task_run_state.PASS, "changed_paths": [], "candidate_carrier": {}},
        parent_progress={"blocking": False},
    )

    assert state == "non-delivery"
    assert candidate["status"] == "absent"
    assert candidate["useful"] is False


# --- scripts/git_status_snapshot ------------------------------------------------


def test_a_non_ascii_branch_oid_is_a_named_status_error(tmp_path: Path) -> None:
    """Bytes that are not an ASCII object id in the `branch.oid` header refuse the
    whole snapshot with this module's own error type.

    Every caller here catches `GitStatusError` and degrades. Letting a
    `UnicodeDecodeError` out instead would escape those handlers, so one corrupt
    header would crash a gate rather than degrade one status read.
    """
    with pytest.raises(status_snapshot.GitStatusError, match="malformed branch OID"):
        status_snapshot.parse(b"# branch.oid \xff\xfe\x00")


def test_a_git_status_that_fails_reports_gits_own_stderr(tmp_path: Path) -> None:
    """When `git status` exits non-zero, the refusal carries Git's message.

    The discovery preflight only proves a `.git` marker LOOKS right; a corrupt
    object store passes it and then fails in Git. Raising a bare "git status
    failed" would strip the one line that tells the operator which repository is
    broken and how.
    """
    repo = tmp_path / "corrupt"
    _install_git_dir(repo, broken_config=True)

    with pytest.raises(status_snapshot.GitStatusError) as excinfo:
        status_snapshot.capture(repo)

    assert str(excinfo.value).strip()
    assert "git status failed" not in str(excinfo.value)


def test_an_unparseable_status_read_becomes_a_runtime_error_for_the_index_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The staged/worktree consistency gate converts a parse refusal into its own
    error type instead of leaking the snapshot module's.

    Fault-injected: real `git status --porcelain=v2` output always parses. The
    conversion still matters -- the gate's caller catches `RuntimeError`, so a
    leaked `GitStatusError` would take down a pre-commit hook rather than
    reporting an unreadable status.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setattr(
        staged_consistency,
        "parse_git_status",
        lambda _payload: (_ for _ in ()).throw(
            staged_consistency.GitStatusError("unexpected git status record")
        ),
    )

    with pytest.raises(RuntimeError, match="unexpected git status record"):
        staged_consistency._status_paths(repo)


def test_an_unparseable_status_read_leaves_the_dup_ratchet_with_no_changed_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The duplication ratchet answers `None`, not an empty set, when status will
    not parse.

    Fault-injected for the same reason as above. `None` and `set()` route
    differently: an empty set says "nothing is dirty" and lets the ratchet
    proceed as if the tree were clean, while `None` says the ratchet could not
    tell -- which is what keeps an unreadable status from being rebaselined over.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setattr(DUP_RATCHET_GIT, "_git_output", lambda *_a, **_k: (0, "garbage"))

    assert DUP_RATCHET_GIT._status_changed_paths(repo) is None


# --- scripts/surfaces_lib -------------------------------------------------------


def test_an_empty_changed_ref_is_refused_before_git_is_asked() -> None:
    """A blank changed ref is a surface error, not a Git invocation.

    An empty ref would reach `git diff --name-status ''`, whose answer is the
    diff against the working tree -- a DIFFERENT question, silently substituted.
    Refusing keeps an unset adapter value from producing a plausible wrong scope.
    """
    with pytest.raises(surfaces_lib.SurfaceError, match="changed ref must be non-empty"):
        surfaces_lib.collect_changed_and_deleted_paths_for_ref(Path("."), "   ")


def test_an_os_level_status_failure_is_reported_as_a_surface_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An `OSError` from the status read is converted to this module's error type.

    Reproduced, not injected: the checkout is real and discoverable, so the
    file-based preflight passes and the status read reaches `subprocess`, which
    then cannot find `git` on an emptied `PATH`. That `FileNotFoundError` would
    otherwise escape every `except SurfaceError` handler in the surfaces pipeline
    -- the handlers that turn "could not read the tree" into a reported refusal
    rather than a traceback.

    An earlier version replaced `capture_git_status` with a raising stub. It
    reached the same arm, but it also let this file's summary claim no real state
    could get here, which `test_batch8.py` disproves by emptying `PATH` for real.
    Removing the double removes the temptation.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))

    with pytest.raises(surfaces_lib.SurfaceError):
        surfaces_lib.collect_working_tree_snapshot(repo)


# --- scripts/mutation_changed_files_lib -----------------------------------------


def test_an_unreadable_status_leaves_the_changed_pool_with_its_tracked_half(
    tmp_path: Path,
) -> None:
    """When the untracked half cannot be read, the tracked diff still stands.

    Untracked membership is an ADDITION to the tracked diff. Failing the whole
    computation because status was unreadable would drop the tracked changes too,
    and the changed-line gate would then report a smaller changed set than the
    commit actually carries -- an under-report on the gate whose job is to block
    on uncovered changed lines.

    The unreadable status is injected through `FactsCheckout`, whose `status()`
    raises when it holds no snapshot; that stands in for a real `git status`
    failure, which cannot be provoked on demand over a healthy checkout.

    The base must differ from the worktree for this to prove anything. An earlier
    version compared HEAD against a clean tree, so the tracked diff was empty
    before the unreadable-status arm was ever reached and `== []` would have held
    for an implementation that returned nothing at all on that exception -- the
    precise failure this docstring claims to prevent, asserted by a test that
    could not see it.
    """
    repo = install_committed_repo(
        tmp_path / "repo", {"scripts/sample.py": "x = 1\n"}, message="base"
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    # A real tracked change over that base, so an empty answer is distinguishable
    # from a correct one.
    (repo / "scripts" / "sample.py").write_text("x = 2\n", encoding="utf-8")

    changed = mutation_changed_files_lib.changed_pool_files_vs_base(
        repo, base, checkout=checkout_view.FactsCheckout(repo, status=None)
    )

    assert changed == ["scripts/sample.py"]


# --- scripts/premise_preflight_lib ----------------------------------------------


def test_a_premise_marker_check_without_a_readable_head_refuses(tmp_path: Path) -> None:
    """With no HEAD commit read, the marker check refuses instead of reporting
    "marker not found".

    "Not found" is what the caller acts on by writing the marker. Reporting it
    for a HEAD that was never read would let a preflight append a decision on the
    strength of history nobody inspected.
    """
    snapshot = premise_snapshot.CapturedTreeSnapshot(True, True, {}, {})

    with pytest.raises(premise_preflight_lib.PremiseError) as excinfo:
        premise_preflight_lib._marker_seen(tmp_path, "P1", snapshot)
    assert excinfo.value.code == "invalid_git_state"


# --- scripts/worktree_cleanup_lib -----------------------------------------------


def test_an_unreadable_worktree_is_treated_as_dirty(tmp_path: Path) -> None:
    """A worktree whose status cannot be read counts as DIRTY, with the reason.

    Cleanup deletes what it believes is clean. "Could not tell" has to fall on
    the side that preserves the tree, and the message has to say why, or the
    operator is left with a worktree the tool silently refuses to remove.
    """
    plain = tmp_path / "plain"
    plain.mkdir()

    dirty, reason = worktree_cleanup_lib._is_dirty(plain)

    assert dirty is True
    assert reason.strip()


# --- scripts/changed_line_run_trust ---------------------------------------------


def test_a_symbolic_head_is_resolved_before_it_is_compared_with_the_live_head(
    tmp_path: Path,
) -> None:
    """A branch name is resolved to an object id before being compared with the
    worktree's live HEAD.

    The comparison decides whether coverage (collected from the live worktree)
    and the line mapping (computed against the requested head) describe the same
    tree. Comparing the literal string `main` against an object id would report
    every symbolic head as a mismatch, and the gate would refuse runs that are
    perfectly consistent.
    """
    repo = install_committed_repo(tmp_path / "repo", {"scripts/sample.py": "x = 1\n"})

    probe = changed_line_run_trust.probe_run_trust(repo, "main", {"scripts/sample.py"})

    assert probe.unestablished_kind != changed_line_run_trust.INSPECTION_FAILED
    assert probe.resolved_pair is not None
    assert probe.resolved_pair[0] == probe.resolved_pair[1]
    assert probe.contaminated == []


# --- scripts/check_prose_pin ----------------------------------------------------


def test_removed_lines_outside_a_repository_are_empty_not_an_error(
    tmp_path: Path,
) -> None:
    """With no diff available, the removed-line set is empty.

    This gate compares removed lines against pinned prose. An unreadable diff has
    to produce no removals -- inventing them would fail the pin for a repository
    the gate could not even read, and the gate runs in consumer trees that may
    not be checkouts at all.
    """
    plain = tmp_path / "plain"
    plain.mkdir()

    assert check_prose_pin.removed_lines(plain, "docs/anything.md") == []
