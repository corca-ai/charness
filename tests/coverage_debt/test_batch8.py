"""Behavior pins for the packaged-script layout and the surfaces that consume
checkout facts -- the other half of what the v8.0.2 release lane found unproven.

Two themes, and they meet at the same seam. Several modules here are invoked BOTH
as `scripts.<name>` from the repo root and as `python3 scripts/<name>.py` (or as
`$SKILL_DIR/scripts/<name>.py`) from a host that puts only the script's own
directory on `sys.path`. In the second layout `from scripts.… import …` cannot
resolve, and a fallback arm is the only thing that binds the module's owners --
an arm in-process tests never take, because pytest has already made `scripts`
importable. The rest of the file pins the task-run, reviewed-input, and release
surfaces that read those owners, where the same "could not look" states have to
arrive as named refusals rather than tracebacks.

`test_batch7.py` is the companion: the checkout-facts owners themselves.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import (
    checkout_view,
    setup_inspect_quality_lib,
    sibling_module_loader,
    task_run,
    task_run_git,
)
from scripts import prepush_quality_receipt as receipt
from scripts.core import git_checkout as checkout
from scripts.core import git_status_snapshot as status_snapshot
from scripts.lessons import lesson_ledger_lib
from scripts.review import reviewed_input_identity as reviewed_identity
from scripts.review import reviewed_input_nonblob as reviewed_nonblob
from scripts.review import reviewed_input_worktree as reviewed_worktree
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]

TEST_DISCOVERY = load_script_module(
    "test_discovery_lib_batch8", ROOT / "skills/public/quality/scripts/test_discovery_lib.py"
)
DUP_RATCHET_GIT = load_script_module(
    "dup_ratchet_git_batch8", ROOT / "skills/public/quality/scripts/dup_ratchet_git.py"
)
ENTRYPOINT_DOCS = load_script_module(
    "inventory_entrypoint_docs_ergonomics_batch8",
    ROOT / "skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py",
)
PUBLISH_RUNTIME = load_script_module(
    "publish_release_runtime_batch8",
    ROOT / "skills/public/release/scripts/publish_release_runtime.py",
)
CLAIMS_REVIEW = load_script_module(
    "scaffold_claims_review_batch8",
    ROOT / "skills/public/release/scripts/scaffold_claims_review.py",
)
RELEASE_DELTA = load_script_module(
    "release_delta_batch8", ROOT / "skills/public/release/scripts/release_delta.py"
)
MARKDOWN_PREVIEW = load_script_module(
    "markdown_preview_lib_batch8",
    ROOT / "skills/support/markdown-preview/scripts/markdown_preview_lib.py",
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


# --- quality skill scripts: putting the repo root back on `sys.path` -------------


@pytest.mark.parametrize(
    "module",
    [
        pytest.param(TEST_DISCOVERY, id="test_discovery_lib"),
        pytest.param(DUP_RATCHET_GIT, id="dup_ratchet_git"),
        pytest.param(ENTRYPOINT_DOCS, id="inventory_entrypoint_docs_ergonomics"),
    ],
)
def test_a_skill_script_puts_the_owning_repo_root_on_sys_path(
    module: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each packaged quality script finds the repo that owns it and makes
    `scripts.` importable from there.

    These modules run as `$SKILL_DIR/scripts/<name>.py` under a host that puts
    only the script's own directory on `sys.path`. Without this climb, the very
    next line -- `from scripts.core.repo_file_listing import ...` -- raises
    `ModuleNotFoundError` and the gate cannot start. In-process tests never see
    it, because pytest has already put the repo root on `sys.path`, which is
    exactly why the bootstrap needs a test that removes it first.
    """
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(ROOT)])
    assert str(ROOT) not in sys.path

    module._ensure_scripts_package()  # type: ignore[attr-defined]

    assert sys.path[0] == str(ROOT)


def test_discovery_over_a_git_listing_keeps_only_listed_test_files(tmp_path: Path) -> None:
    """Pattern discovery intersects the glob walk with Git's own file listing.

    The walk alone would count build output, vendored trees, and stray copies as
    test files, inflating the standing-test-economics measurement with files the
    repository does not own. Intersecting with the listing is what makes the
    count mean "tests this repo tracks"; the ordering assertion pins that the
    result stays deterministic for a ratchet that compares runs.
    """
    repo = install_committed_repo(
        tmp_path / "repo",
        {
            ".gitignore": "build/\n",
            "tests/test_alpha.py": "def test_alpha():\n    pass\n",
            "tests/test_beta.py": "def test_beta():\n    pass\n",
            "src/app.py": "x = 1\n",
        },
    )
    (repo / "build").mkdir()
    (repo / "build" / "test_generated.py").write_text("def test_g():\n    pass\n", encoding="utf-8")

    files, provenance = TEST_DISCOVERY.resolve_test_files(repo, None)

    assert [path.relative_to(repo).as_posix() for path in files] == [
        "tests/test_alpha.py",
        "tests/test_beta.py",
    ]
    assert provenance == {
        "source": "default",
        "command_status": None,
        "degraded": False,
        "error": None,
    }


# --- scripts/prepush_quality_receipt --------------------------------------------


_SEMANTIC_RECEIPT = {
    "surface": "quality",
    "status": "pass",
    "effective_exit_code": 0,
    "unproven_subjects": [],
    "details": {"release": True, "full_queue": True},
    "measured_scope": ["release-full-superset"],
}


def _receipt_repo(tmp_path: Path) -> Path:
    return install_committed_repo(
        tmp_path / "repo",
        {
            "scripts/run-quality.sh": "#!/usr/bin/env bash\nexit 0\n",
            "plugins/charness/.claude-plugin/plugin.json": '{"version": "0.0.1"}\n',
        },
    )


def test_a_sealed_receipt_pins_the_head_and_tree_its_validation_re_reads(
    tmp_path: Path,
) -> None:
    """Seal and validate agree on the HEAD/tree pair, read the same way at both
    ends.

    This pair is the whole point of the receipt: it is what lets the pre-push
    hook say "the quality run that passed measured THESE objects". Reading HEAD
    at seal time and something else at validate time would let a commit made
    between the two slip past a receipt that still reported a pass.
    """
    repo = _receipt_repo(tmp_path)
    semantic = tmp_path / "semantic.json"
    semantic.write_text(json.dumps(_SEMANTIC_RECEIPT), encoding="utf-8")
    command = "./scripts/run-quality.sh --release --read-only"

    sealed = receipt.seal_receipt(repo, command, semantic, "plugins/charness")

    head, tree = receipt._head_and_tree(repo)
    assert (sealed["verified_head"], sealed["verified_tree"]) == (head, tree)

    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(sealed), encoding="utf-8")
    push_input = f"refs/heads/main {head} refs/heads/main {head}\n"

    assert receipt.validate_receipt(repo, receipt_path, push_input) == sealed


def test_an_incomplete_rev_parse_snapshot_is_refused_rather_than_unpacked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `rev-parse` that exits 0 with fewer than two lines is a receipt error.

    Fault-injected: a real `git rev-parse HEAD HEAD^{tree}` either prints both or
    exits non-zero. The guard still earns its place -- unpacking a one-line result
    raises `ValueError` from inside a pre-push hook, where the operator sees a
    traceback instead of the named refusal that tells them the receipt is
    unusable.
    """
    repo = _receipt_repo(tmp_path)
    monkeypatch.setattr(receipt, "_git", lambda *_args, **_kwargs: "only-one-line")

    with pytest.raises(receipt.ReceiptError, match="incomplete HEAD/tree snapshot"):
        receipt._head_and_tree(repo)


# --- skills/public/release/scripts/publish_release_runtime ----------------------


def test_a_relative_common_dir_from_git_is_read_against_the_repo_root(
    tmp_path: Path,
) -> None:
    """`git rev-parse --git-common-dir` answers `.git` in an ordinary checkout, and
    that relative answer is joined to the repo root before being used.

    The release runtime persists failure payloads under this directory. Using
    Git's relative answer as-is would write them relative to the CALLER's working
    directory, scattering release failure evidence outside the repository that
    produced it.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})

    assert PUBLISH_RUNTIME._git_common_dir_via_git(repo) == (repo / ".git").resolve()


def test_the_common_dir_falls_back_to_git_when_the_files_decline_to_answer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under `GIT_DIR` redirection the file projection declines, and the runtime
    asks Git rather than giving up.

    The fast path is an optimisation, not the contract. If declining meant
    failing, a release run under any environment-redirected layout would lose its
    ability to persist a failure payload at exactly the moment it has one.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))

    assert PUBLISH_RUNTIME.git_common_dir(repo) == (repo / ".git").resolve()


# --- skills/public/release/scripts/scaffold_claims_review -----------------------


def test_the_claims_review_scaffold_accepts_a_tree_dirty_only_where_allowed(
    tmp_path: Path,
) -> None:
    """A prepared stop passes when its dirty paths are exactly the allowed ones,
    and is refused by NAME when anything else is dirty.

    The claims-review record asserts what a release changed. A stop carrying
    unrelated edits would fold them into that assertion invisibly, so the refusal
    has to list the offending paths -- a bare "tree is dirty" leaves the operator
    diffing by hand at the release boundary.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    (repo / "review.md").write_text("evidence\n", encoding="utf-8")

    CLAIMS_REVIEW._allowed_dirty_paths(repo, {"review.md"})

    with pytest.raises(SystemExit) as excinfo:
        CLAIMS_REVIEW._allowed_dirty_paths(repo, set())
    assert "review.md" in str(excinfo.value)


def test_a_git_status_failure_stops_the_claims_review_scaffold_with_a_reason(
    tmp_path: Path,
) -> None:
    """An unreadable status is a named `SystemExit`, not a traceback.

    This runs at the release boundary. "git status failed: <detail>" tells the
    operator the scaffold never inspected the tree; a `GitStatusError` traceback
    from three modules down reads like the scaffold itself is broken.
    """
    repo = tmp_path / "corrupt"
    _install_git_dir(repo, broken_config=True)

    with pytest.raises(SystemExit, match="git status failed"):
        CLAIMS_REVIEW._allowed_dirty_paths(repo, set())


# --- skills/public/release/scripts/release_delta --------------------------------


def test_ref_resolution_refuses_non_text_git_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ref resolution refuses bytes where it expects text, rather than parsing them.

    Fault-injected: the shared `_git` helper is used in both text and binary
    modes elsewhere in this module. If a caller ever passed the binary one here,
    `splitlines()` would yield `bytes` and the resolved "sha" would be a
    `bytes` repr carried into a release tag comparison.
    """
    monkeypatch.setattr(RELEASE_DELTA, "_git", lambda *_a, **_k: b"not text\n")

    with pytest.raises(ValueError, match="non-text ref resolution output"):
        RELEASE_DELTA._resolve_release_commits(tmp_path, "base", "head")


def test_ref_resolution_refuses_more_records_than_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """More output records than refs asked about is a refusal, not a silent slice.

    Fault-injected. The records are consumed positionally, so an extra one means
    the mapping from ref to sha is no longer trustworthy -- and this pair of shas
    becomes the base and head of the release delta a whole set of release claims
    is derived from.
    """
    monkeypatch.setattr(
        RELEASE_DELTA,
        "_git",
        lambda *_a, **_k: f"{'a' * 40} commit\n{'b' * 40} commit\n{'c' * 40} commit\n",
    )

    with pytest.raises(ValueError, match="unexpected extra ref resolution output"):
        RELEASE_DELTA._resolve_release_commits(tmp_path, "base", "head")


# --- scripts/sibling_module_loader ----------------------------------------------


def test_a_stem_with_no_sibling_falls_through_to_the_ordinary_import() -> None:
    """No adjacent file means the loader stops improvising and imports normally.

    The by-path load exists only to bind the file NEXT TO the caller. With no
    such file there is nothing local to prefer, so the loader must produce the
    ordinary `ModuleNotFoundError` for `scripts.<stem>` rather than a bespoke
    error -- the traceback an operator can act on names the module they typed.
    """
    with pytest.raises(ModuleNotFoundError, match="scripts.no_such_sibling_module"):
        sibling_module_loader.load_sibling("no_such_sibling_module")


# --- scripts/lesson_ledger_lib --------------------------------------------------


def test_a_committed_v8_ledger_migrates_and_is_cached_for_this_head(
    tmp_path: Path,
) -> None:
    """The previous ledger schema is accepted, given the current lesson budget and
    an empty lifecycle list, and the result is memoised per (repo, path, HEAD).

    v8 has no `lifecycle_events` and no `active_lesson_budget`. Refusing it would
    make the first v9 write in any repository impossible without hand-editing the
    committed ledger; substituting `None` for the budget would let the append
    path compare a count against nothing. The cache is keyed on HEAD, so it can
    only ever return the state that HEAD actually carries.
    """
    committed = {
        "kind": lesson_ledger_lib.KIND,
        "schema_version": lesson_ledger_lib.PREVIOUS_SCHEMA_VERSION,
        "transitions": [],
        "score_events": [],
        "lessons": [],
    }
    repo = install_committed_repo(tmp_path / "repo", {"ledger.json": json.dumps(committed) + "\n"})

    state = lesson_ledger_lib._committed_state(repo, repo / "ledger.json")

    assert state == ([], [], lesson_ledger_lib.ACTIVE_LESSON_BUDGET, [])
    # Read again: the memoised value is returned, and it is the same state.
    assert lesson_ledger_lib._committed_state(repo, repo / "ledger.json") == state


# --- scripts/task_run_git -------------------------------------------------------


@pytest.mark.boundary_contract(
    reason="target fast path is compared with real Git's rev-parse answer"
)
def test_head_comes_from_the_checkout_files_before_git_is_spawned(
    tmp_path: Path,
) -> None:
    """`rev-parse HEAD` is answered from disk when the layout is ordinary.

    The task lifecycle asks for HEAD repeatedly. Spawning Git each time is the
    cost this projection removes, so the fast path has to produce the same oid
    Git would -- asserted against Git's own answer rather than against a
    hard-coded value.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    assert task_run_git._git_output(repo, "rev-parse", "HEAD") == expected
    assert task_run_git._git_dir(repo) == (repo / ".git").resolve()


def test_the_git_root_check_falls_back_to_git_under_env_redirection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When files cannot name the worktree root, `rev-parse --show-toplevel` does.

    Refusing here would make every environment-redirected layout unusable for
    task runs, even though the root is perfectly well defined -- the file
    projection declining is not the same as the repository being unusable.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    monkeypatch.chdir(repo)

    assert task_run_git._require_git_root(repo) == repo.resolve()


def test_a_repo_root_that_is_not_its_own_identity_root_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the projected identity names a DIFFERENT root than the one requested,
    the run is refused rather than silently retargeted.

    Fault-injected: both sides are `.resolve()`d, so they agree for every real
    path. The guard is what stops a future projection change from letting
    `--repo-root <subdirectory>` proceed against the parent worktree -- a task
    run that then commits, checkpoints, and cleans up in the wrong tree.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    elsewhere = checkout.CheckoutIdentity(
        tmp_path / "other", repo / ".git", repo / ".git", "0" * 40
    )
    monkeypatch.setattr(task_run_git, "identity_from_files", lambda _root: elsewhere)

    with pytest.raises(task_run_git.TaskRunError, match="must be the Git worktree root"):
        task_run_git._repo_snapshot(repo)


# --- scripts/task_run -----------------------------------------------------------


def test_a_checkout_own_dir_that_cannot_be_resolved_is_refused_by_name(
    tmp_path: Path,
) -> None:
    """A worktree-creation payload whose own_dir will not resolve is a named
    `TaskRunError`, not a `RuntimeError` from pathlib.

    A symlink cycle at that path is real, and the payload is read at the start of
    a task run. Every caller here handles `TaskRunError` and reports it; a raw
    `RuntimeError` escapes them and takes the run down with a traceback naming
    pathlib rather than the payload field that is wrong.
    """
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.symlink_to(right)
    right.symlink_to(left)

    with pytest.raises(task_run.TaskRunError, match="unusable checkout own_dir"):
        task_run._checkout_own_dir({"_checkout": {"own_dir": str(left)}})


# --- scripts/reviewed_input_identity --------------------------------------------


@pytest.mark.boundary_contract(
    reason="target checkout-file projection is compared with real Git output"
)
def test_reviewed_identity_reads_head_from_the_checkout_files(tmp_path: Path) -> None:
    """The optional Git reader answers `rev-parse HEAD` from disk, with the same
    trailing-newline shape a real `git rev-parse` produces.

    Callers decode this and compare it against Git's output elsewhere. A
    projection that dropped the newline would make the two spellings of the same
    HEAD unequal, and reviewed-input identity would go stale on every read.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True
    ).stdout

    assert reviewed_identity._git_bytes_optional(repo, "rev-parse", "HEAD") == expected


def test_working_tree_content_without_a_status_snapshot_is_refused(
    tmp_path: Path,
) -> None:
    """Building working-tree content with no status snapshot raises rather than
    assuming nothing is untracked.

    The snapshot is the ONLY source of the untracked set. Defaulting to empty
    would silently drop every declared-untracked entry from the identity, so a
    reviewed file that exists only in the working tree would verify as current
    after being deleted.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})

    with pytest.raises(ValueError, match="working-tree content requires a status snapshot"):
        reviewed_identity._content_components(
            repo,
            [],
            "0" * 40,
            reviewed_identity.SUBSTRATE_WORKING_TREE,
            status_snapshot=None,
        )


def test_a_committed_ref_substrate_outside_a_checkout_reports_unavailable(
    tmp_path: Path,
) -> None:
    """Off the ordinary checkout fast path, Git is asked whether this is a work
    tree at all -- and a refusal becomes an `unavailable` identity, not a crash.

    The committed-ref substrate does not read a status snapshot, so nothing else
    in this path would notice a non-repository. Reporting `unavailable` is what
    lets a consumer distinguish "no identity could be built" from "identity built
    and nothing was reviewed".
    """
    plain = tmp_path / "plain"
    plain.mkdir()

    identity = reviewed_identity.build_reviewed_input_identity(
        repo_root=plain, reviewed_paths=["a.py"], changed_ref="HEAD~1..HEAD"
    )

    assert identity["status"] == "unavailable"
    assert identity["reason"].strip()


# --- scripts/reviewed_input_nonblob ---------------------------------------------


def test_a_missing_git_binary_propagates_instead_of_reading_as_no_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With `git` absent from `PATH` but the directory present, the failure
    propagates; only an ABSENT directory reads as "nothing to consult".

    Swallowing this would bind the stale index value for a submodule whose
    checkout has actually moved, and verification would repeat the same fallback
    and agree -- a failure converted into a passing verdict, which is the exact
    class this module exists to close.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))

    with pytest.raises(FileNotFoundError):
        reviewed_nonblob._git_bytes_optional(repo, "rev-parse", "HEAD")

    assert reviewed_nonblob._git_bytes_optional(tmp_path / "absent", "status") is None


def test_a_truncated_toplevel_head_read_falls_back_to_the_index_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A submodule probe that does not return BOTH the toplevel and HEAD is
    unusable, so the index record stays the answer.

    Fault-injected. The two lines are read positionally, and the toplevel check
    is the thing that stops the SUPERPROJECT's HEAD from being bound as the
    submodule's. A one-line answer with no toplevel to compare must not be
    trusted for the line that remains.
    """
    monkeypatch.setattr(reviewed_nonblob, "_git_bytes_optional", lambda *_a, **_k: b"only-one\n")

    assert reviewed_nonblob._checked_out_gitlink_commit("sub", tmp_path) is None


def test_a_gitlink_reached_through_a_symlinked_parent_is_not_read_as_a_gitlink(
    tmp_path: Path,
) -> None:
    """A path whose PARENT is a symlink out of the repository is handed back for
    the ordinary path refusal instead of being probed as a submodule.

    The symlink check covers the last component only. Without the containment
    check, `git` would run with its working directory inside an EXTERNAL
    repository and bind that repository's HEAD into this repo's reviewed-input
    identity.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    outside = tmp_path / "outside"
    (outside / "sub").mkdir(parents=True)
    (repo / "link").symlink_to(outside)

    # An index entry that DOES record a gitlink, so the containment check -- not an
    # absent entry -- is what decides the answer.
    assert reviewed_nonblob._gitlink_commit(repo, "link/sub", None, index_commit="a" * 40) is None


# --- scripts/reviewed_input_worktree --------------------------------------------


def test_a_supplied_checkout_view_is_the_status_source(tmp_path: Path) -> None:
    """When a checkout view is supplied, its snapshot is used -- and a view with
    no snapshot refuses as a `ValueError`, not a `GitStatusError`.

    The view exists so one Git observation can be shared across the several
    readers in an identity build. Falling back to a fresh `git status` when the
    view cannot answer would reintroduce the split-observation the view removes,
    and letting `GitStatusError` out would escape callers that catch `ValueError`.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    real = status_snapshot.capture(repo)

    snapshot = reviewed_worktree.capture(
        repo, checkout=checkout_view.FactsCheckout(repo, status=real)
    )
    assert snapshot.branch_oid == real.head_oid

    with pytest.raises(ValueError, match="no status snapshot"):
        reviewed_worktree.capture(repo, checkout=checkout_view.FactsCheckout(repo, status=None))


def test_content_digest_over_a_removed_working_directory_reports_absence(
    tmp_path: Path,
) -> None:
    """When the path check itself fails and nothing is there to probe, the digest
    is `None` -- absence -- rather than a `NameError`.

    Produced for real by removing the process working directory, which makes
    resolving a relative repo root fail INSIDE the path check, before the
    candidate is bound. Probing the original `path` rather than the unbound
    candidate is the whole point: an earlier version referenced the candidate
    here and turned an `OSError` into a `NameError`.
    """
    doomed = tmp_path / "doomed"
    doomed.mkdir()
    previous = os.getcwd()
    os.chdir(doomed)
    try:
        doomed.rmdir()

        assert reviewed_worktree.content_sha256(Path("relative"), "a.py") is None
    finally:
        os.chdir(previous)


# --- scripts/setup_inspect_quality_lib ------------------------------------------


def test_a_hook_path_probe_that_will_not_run_leaves_the_policy_unconfigured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the `core.hooksPath` probe cannot run or times out, the inspection
    reports no configured hook path rather than failing.

    Fault-injected on the probe's own two-second timeout. `setup` inspection is
    advisory: one unavailable Git probe must not take down the whole repository
    snapshot the operator is being shown before they approve anything.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    real_run = setup_inspect_quality_lib.run_process

    def refuse_git_config(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and list(argv[:2]) == ["git", "config"]:
            return subprocess.CompletedProcess(list(argv), 124, "", "timed out after 2s")
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(setup_inspect_quality_lib, "run_process", refuse_git_config)

    policy = setup_inspect_quality_lib._detect_hook_policy(repo, {})

    assert policy["hook_manager"] is None


# --- skills/support/markdown-preview/scripts/markdown_preview_lib ---------------


def test_an_unreadable_status_leaves_the_preview_scope_as_configured(
    tmp_path: Path,
) -> None:
    """With no readable status, the preview reports no changed paths AND says so.

    Silently returning an empty changed set would let the preview claim it scoped
    to "what changed" while having scoped to nothing. The accompanying note is
    what tells the reader the configured scope was used as-is.
    """
    plain = tmp_path / "plain"
    plain.mkdir()

    changed, notes = MARKDOWN_PREVIEW._changed_markdown_paths(plain)

    assert changed == set()
    assert notes and "configured scope as-is" in notes[0]


# --- running a root script rather than importing the package --------------------
#
# Every module below is invoked BOTH ways: as `scripts.<name>` from the repo root,
# and as `python3 scripts/<name>.py` (or as a skill script) from a host that puts
# only `scripts/` on `sys.path`. In the second layout `from scripts.… import …`
# cannot resolve, and the fallback arm is the only thing that binds the module's
# owners. In-process tests never see it, because pytest has already made `scripts`
# importable -- which is why these tests take it away first, with a meta-path
# finder rather than a `sys.path` filter: whether `scripts` is reachable otherwise
# depends on what earlier tests imported, so the arm under test would be taken in
# one run and skipped in another.


class _BlockScriptsPackage:
    """Makes `scripts.*` -- or one named member of it -- unimportable for one test."""

    def __init__(self, only: str | None = None) -> None:
        self._only = only

    def find_spec(self, fullname, path=None, target=None):
        blocked = (
            fullname == self._only
            if self._only is not None
            else fullname == "scripts" or fullname.startswith("scripts.")
        )
        if blocked:
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def _without_the_scripts_package(
    monkeypatch: pytest.MonkeyPatch, *, only: str | None = None
) -> None:
    monkeypatch.setattr(sys, "meta_path", [_BlockScriptsPackage(only)] + sys.meta_path)
    for name in [name for name in sys.modules if name == "scripts" or name.startswith("scripts.")]:
        monkeypatch.delitem(sys.modules, name)
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))


@pytest.mark.parametrize(
    ("script", "bound", "flat_module"),
    [
        ("scripts/core/helper_provenance_lib.py", "env_bypass_enabled", "env_bypass"),
        ("tools/check_current_pointer_writes.py", "RepoFileSnapshot", "repo_file_listing"),
        ("scripts/gates/check_symbol_residue.py", "RepoFileSnapshot", "repo_file_listing"),
        ("scripts/gates_support/dup_ratchet_edit_advisory.py", "head_oid_from_files", "git_checkout"),
    ],
)
def test_a_root_script_binds_its_owners_flat_when_the_package_is_unreachable(
    script: str, bound: str, flat_module: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each of these modules still imports, and still binds a real owner, in the
    layout its own argv produces.

    Asserted on what the module BOUND -- the owner's flat module name -- rather
    than on whether `scripts` happens to be importable in this interpreter. The
    weaker check passes in isolation and fails in the full suite, because another
    test having left the package reachable is not a fact about the layout under
    test.
    """
    blocked = None
    if script.endswith("check_symbol_residue.py"):
        blocked = "scripts.core.repo_file_listing"
    elif script.endswith("dup_ratchet_edit_advisory.py"):
        blocked = "scripts.core.git_checkout"
    _without_the_scripts_package(monkeypatch, only=blocked)
    before = set(sys.modules)
    try:
        module = load_script_module(f"{Path(script).stem}_flat_batch7", ROOT / script)

        assert getattr(module, bound).__module__ == flat_module
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]


def test_the_identity_builder_binds_the_sibling_loader_flat(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The identity builder's own sibling-loader import has a flat fallback, and
    taking it still yields the real loader.

    Scoped to `scripts.core.sibling_module_loader` alone, because that is the import
    the dual path guards. This module reaches other owners THROUGH the loader
    (which resolves them by path), so blocking the whole package would refuse a
    later unconditional package import in a transitive owner -- a different
    module's contract, and not the arm under test.

    Binding nothing here is not a soft failure: `_load_sibling` is what supplies
    the checkout, path-selection, range, worktree, and non-blob owners three
    lines down, so a broken fallback is an import-time crash of the whole
    reviewed-input identity surface.
    """
    _without_the_scripts_package(monkeypatch, only="scripts.core.sibling_module_loader")
    before = set(sys.modules)
    try:
        module = load_script_module(
            "reviewed_input_identity_flat_batch7", ROOT / "scripts/review/reviewed_input_identity.py"
        )

        assert module._load_sibling.__module__ == "sibling_module_loader"
        repo = tmp_path / "repo"
        git_dir = repo / ".git"
        (git_dir / "objects").mkdir(parents=True)
        (git_dir / "refs").mkdir()
        (git_dir / "HEAD").write_text("a" * 40, encoding="ascii")
        assert module._checkout.head_oid_from_files(repo) == "a" * 40
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]


def test_the_premise_tree_observation_lists_the_index_without_the_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The premise observer resolves its listing owner flat and still reads the
    index.

    This one degrades INSIDE a function, not at import, so a broken fallback
    would not fail loudly at startup -- the preflight would run and report an
    empty index, which reads as "no protected path is tracked" and lets a premise
    be recorded against a tree nobody listed.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    _without_the_scripts_package(monkeypatch)
    before = set(sys.modules)
    try:
        observation = load_script_module(
            "premise_tree_observation_flat_batch7", ROOT / "scripts/premise/premise_tree_observation.py"
        )

        assert observation._index_paths(repo) == {b"tracked.py"}
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]


def test_the_issue_critique_observer_reads_tracked_state_without_the_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The issue-critique observer resolves its listing owner flat and still
    distinguishes a tracked path from an untracked one.

    A fallback that bound nothing would make every path read as untracked, and
    the observer would report a checked-in critique artifact as absent at exactly
    the closeout it exists to gate.
    """
    repo = install_committed_repo(tmp_path / "repo", {"tracked.py": "base\n"})
    (repo / "loose.py").write_text("x = 1\n", encoding="utf-8")
    _without_the_scripts_package(monkeypatch)
    before = set(sys.modules)
    try:
        support = load_script_module(
            "issue_critique_observer_support_flat_batch7",
            ROOT / "skills/public/issue/scripts/issue_critique_observer_support.py",
        )

        assert support._path_is_tracked(repo, "tracked.py") is True
        assert support._path_is_tracked(repo, "loose.py") is False
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]


class _RefuseOnce:
    """Refuses ONE named import, once, then gets out of the way."""

    def __init__(self, name: str) -> None:
        self._name = name
        self.fired = False

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self._name and not self.fired:
            self.fired = True
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_the_structural_waste_scan_puts_the_repo_root_back_before_importing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the listing owner is unreachable, the scan finds the repository that
    owns this file, puts its root on `sys.path`, and retries the SAME import.

    Refused ONCE rather than by filtering `sys.path`: the arm's whole job is to
    make `scripts.core.repo_file_listing` reachable, so a finder that refuses the name
    outright would also refuse the retry, and a `sys.path` filter makes the arm's
    success depend on what other tests have already put on the path -- this test
    passed alone and failed in the full suite for exactly that reason. A one-shot
    refusal reproduces the packaged layout's failure without owning the recovery.

    The alternative to this arm is a packaged quality gate that cannot list the
    repository it is measuring.
    """
    waste = load_script_module(
        "structural_waste_lib_flat_batch8",
        ROOT / "skills/public/quality/scripts/structural_waste_lib.py",
    )
    # A COPY, so the module's own `sys.path.insert` is undone at teardown.
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.delitem(sys.modules, "scripts.core.repo_file_listing", raising=False)
    monkeypatch.setattr(
        sys, "meta_path", [_RefuseOnce("scripts.core.repo_file_listing")] + sys.meta_path
    )

    iter_repo_files = waste._iter_repo_files()

    assert callable(iter_repo_files)
    assert sys.path[0] == str(ROOT)
