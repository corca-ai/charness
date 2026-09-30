"""Refusals owned by `scripts/task_run/task_run_git.py`.

Split out of `test_task_run.py` when that file crossed its 800 code-line limit.
The cohesive boundary is the module under test: every case here drives
`task_run_git` directly and asserts the typed refusal and the human-actionable
detail it carries, rather than the lane wiring the sibling file covers.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.task_run import task_run, task_run_evidence, task_run_git
from tests.module_eviction import evict_module, evict_new_modules
from tests.script_loader import load_script_module

from .test_task_run_fixtures import _git, _repo


def test_git_output_refusal_preserves_the_human_actionable_detail(
    monkeypatch, tmp_path: Path
) -> None:
    cases = (
        ("fatal: bad revision\n", "ignored\n", "fatal: bad revision"),
        ("", "git said no\n", "git said no"),
        ("", "", "git command failed"),
    )
    for stderr, stdout, detail in cases:
        monkeypatch.setattr(
            task_run_git,
            "_git",
            lambda *_args, stderr=stderr, stdout=stdout: subprocess.CompletedProcess(
                ["git"], 1, stdout=stdout, stderr=stderr
            ),
        )
        with pytest.raises(task_run.TaskRunError, match=f"git status failed: {detail}"):
            task_run_git._git_output(tmp_path, "status")


def test_require_git_root_refuses_a_subdirectory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    subdirectory = repo / "subdirectory"
    subdirectory.mkdir()

    with pytest.raises(task_run.TaskRunError, match="must be the Git worktree root"):
        task_run_git._require_git_root(subdirectory)


def test_repo_snapshot_batches_identity_topology_and_head(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    calls: list[tuple[str, ...]] = []
    original_git = task_run_git._git

    def traced_git(root: Path, *args: str):
        calls.append(args)
        return original_git(root, *args)

    monkeypatch.setattr(task_run_git, "_git", traced_git)
    snapshot = task_run_git._repo_snapshot(repo)

    assert snapshot["repo_root"] == repo.resolve()
    assert snapshot["git_common_dir"] == (repo / ".git").resolve()
    assert snapshot["git_dir"] == (repo / ".git").resolve()
    assert len(snapshot["head"]) == 40
    assert calls == []


@pytest.mark.parametrize(
    ("base", "message"),
    [
        ("", "--base is required and must resolve to a commit"),
        ("missing-base", "ref is not resolvable: missing-base"),
    ],
)
def test_base_resolution_refuses_missing_commit(tmp_path: Path, base: str, message: str) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(task_run.TaskRunError, match=message):
        task_run_git._resolve_base_sha(repo, base)


def test_git_administration_paths_require_directories(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_git, "layout_from_files", lambda *_args: None)
    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "missing-common\n")
    with pytest.raises(task_run.TaskRunError, match="Git common directory is not a directory"):
        task_run_git._git_common_dir(repo)

    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: ".git\n")
    assert task_run_git._git_dir(repo) == (repo / ".git").resolve()

    monkeypatch.setattr(task_run_git, "_git_output", lambda *_args: "missing-git\n")
    with pytest.raises(task_run.TaskRunError, match="Git directory is not a directory"):
        task_run_git._git_dir(repo)


def test_branch_validation_refuses_syntactically_invalid_names(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(task_run.TaskRunError, match="not a valid named branch"):
        task_run_git._validate_branch(repo, "bad..branch")


def test_branch_validation_refuses_git_illegal_spellings_locally(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    for branch in ("valid-ish//branch", "topic.lock", "foo.lock/bar"):
        with pytest.raises(task_run.TaskRunError, match="not a valid named branch"):
            task_run_git._validate_branch(repo, branch)


def test_worktree_validation_refuses_inside_and_existing_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inside = repo / "nested"
    with pytest.raises(task_run.TaskRunError, match="must be outside the repository"):
        task_run_git._validate_worktree_path(repo, inside)

    existing = tmp_path / "existing-worktree"
    existing.mkdir()
    with pytest.raises(task_run.TaskRunError, match="worktree path already exists"):
        task_run_git._validate_worktree_path(repo, existing)


def test_collect_populations_refuses_malformed_and_tracks_rename_destination(
    tmp_path: Path,
) -> None:
    from scripts.core.git_status_snapshot import GitStatusError
    from scripts.core.git_status_snapshot import parse as parse_status
    from scripts.worktree.checkout_view import FactsCheckout

    class _Broken:
        repo_root = tmp_path

        def status(self, **_kwargs):
            raise GitStatusError("unexpected git status record")

        def list_files(self, **_kwargs):
            return None

    with pytest.raises(task_run.TaskRunError, match="unexpected git status record"):
        task_run_git._collect_populations(tmp_path, checkout=_Broken())

    view = FactsCheckout(
        tmp_path,
        status=parse_status(b"2 R. N... 100644 100644 100644 abc abc R100 new.py\0old.py\0"),
    )
    assert task_run_git._collect_populations(tmp_path, checkout=view) == {
        "tracked": ["new.py", "old.py"],
        "untracked": [],
        "ignored": [],
    }


def test_terminal_population_snapshot_keeps_head_branch_and_rename_paths(
    tmp_path: Path,
) -> None:
    from scripts.core.git_status_snapshot import parse as parse_status
    from scripts.worktree.checkout_view import FactsCheckout

    view = FactsCheckout(
        tmp_path,
        status=parse_status(
            (
                b"# branch.oid " + b"a" * 40 + b"\0"
                b"# branch.head lane/task-run\0"
                b"# branch.upstream origin/main\0"
                b"2 R. N... 100644 100644 100644 abc abc R100 renamed.py\0old.py\0"
                b"? new.py\0! .cache\0"
            )
        ),
    )

    populations, head, branch = task_run_git._collect_populations_with_metadata(
        tmp_path, checkout=view
    )

    assert head == "a" * 40
    assert branch == "lane/task-run"
    assert populations == {
        "tracked": ["old.py", "renamed.py"],
        "untracked": ["new.py"],
        "ignored": [".cache"],
    }


def test_parent_progress_refuses_a_status_snapshot_without_head(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(
        task_run_evidence,
        "_collect_populations_with_metadata",
        lambda _repo: ({"tracked": [], "untracked": [], "ignored": []}, None, None),
    )

    with pytest.raises(task_run.TaskRunError, match="did not report a valid HEAD"):
        task_run_evidence._parent_progress(
            parent_root=repo,
            parent_before={"tracked": [], "untracked": [], "ignored": []},
            parent_before_head="a" * 40,
            specs=[],
        )


def _fallback_repo(monkeypatch, tmp_path: Path) -> Path:
    """Force `_repo_snapshot` onto its `rev-parse` fallback (#825)."""
    repo = _repo(tmp_path)
    monkeypatch.setattr(task_run_git, "identity_from_files", lambda *_args: None)
    return repo


def test_repo_snapshot_fallback_reads_absolute_admin_dirs(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _fallback_repo(monkeypatch, tmp_path)
    requested = repo.resolve()
    head = "b" * 40
    monkeypatch.setattr(
        task_run_git,
        "_git_output",
        lambda *_args: f"{requested}\n{requested / '.git'}\n{requested / '.git'}\n{head}\n",
    )

    snapshot = task_run_git._repo_snapshot(repo)

    assert snapshot == {
        "repo_root": requested,
        "git_common_dir": (requested / ".git").resolve(),
        "git_dir": (requested / ".git").resolve(),
        "head": head,
    }


def test_repo_snapshot_fallback_joins_relative_admin_dirs(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _fallback_repo(monkeypatch, tmp_path)
    requested = repo.resolve()
    head = "c" * 40
    monkeypatch.setattr(
        task_run_git, "_git_output", lambda *_args: f"{requested}\n.\n.git\n{head}\n"
    )

    snapshot = task_run_git._repo_snapshot(repo)

    assert snapshot["repo_root"] == requested
    assert snapshot["git_common_dir"] == requested
    assert snapshot["git_dir"] == (requested / ".git").resolve()
    assert snapshot["head"] == head


@pytest.mark.parametrize(
    ("output", "message"),
    [
        ("only\ntwo\n", "git rev-parse returned an incomplete repository snapshot"),
        (
            f"{Path('/elsewhere')}\n{Path('/elsewhere/.git')}\n{Path('/elsewhere/.git')}\n{'d' * 40}\n",
            "must be the Git worktree root, not a subdirectory",
        ),
        (
            "TOP\nTOP-missing-common\nTOP/.git\n" + "e" * 40 + "\n",
            "Git common directory is not a directory",
        ),
        (
            "TOP\nTOP/.git\nTOP-missing-git\n" + "f" * 40 + "\n",
            "Git directory is not a directory",
        ),
    ],
)
def test_repo_snapshot_fallback_refuses_unusable_layouts(
    tmp_path: Path, monkeypatch, output: str, message: str
) -> None:
    repo = _fallback_repo(monkeypatch, tmp_path)
    requested = repo.resolve()
    monkeypatch.setattr(
        task_run_git,
        "_git_output",
        lambda *_args: output.replace("TOP", str(requested)),
    )

    with pytest.raises(task_run.TaskRunError, match=message):
        task_run_git._repo_snapshot(repo)


class _RefuseSubprocessGuardOnce:
    """Refuses the first `scripts.core.subprocess_guard` import, then stands down."""

    def __init__(self) -> None:
        self.fired = False

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts.core.subprocess_guard" and not self.fired:
            self.fired = True
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_task_run_git_binds_its_owners_without_the_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The flat-layout fallback still binds the real subprocess guard (#825)."""
    import scripts.core.git_checkout  # noqa: F401
    import scripts.core.git_status_snapshot  # noqa: F401
    import scripts.worktree.checkout_view  # noqa: F401

    root = Path(__file__).resolve().parents[2]
    refuser = _RefuseSubprocessGuardOnce()
    monkeypatch.setattr(sys, "meta_path", [refuser] + sys.meta_path)
    evict_module(monkeypatch, "scripts.core.subprocess_guard")
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(root)])
    before = set(sys.modules)
    try:
        module = load_script_module(
            "task_run_git_flat_825",
            root / "scripts/task_run/task_run_git.py",
        )

        assert refuser.fired
        assert module.run_process.__module__ == "scripts.core.subprocess_guard"
        assert str(root) in sys.path
    finally:
        evict_new_modules(before)


def test_changed_paths_unions_diff_and_untracked_paths(tmp_path: Path) -> None:
    """Changed paths are the sorted tracked diff plus untracked files (#825)."""
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "untracked.py").write_text("VALUE = 3\n", encoding="utf-8")

    assert task_run_git._changed_paths(repo, base_sha) == ["module.py", "untracked.py"]
