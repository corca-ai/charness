"""Task-run scope freezing, glob expansion, and candidate-boundary scenarios."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import checkout_view
from scripts.task_run import task_run, task_run_git, task_run_scope

from .test_task_run_fixtures import _codex, _commit, _git, _repo, _run


def test_scope_normalization_strips_repository_relative_dot_prefix() -> None:
    assert task_run_scope._normalize_scope(" ./pkg/module.py ") == "pkg/module.py"


@pytest.mark.parametrize("value", ["", "/absolute/path", "../parent", "pkg\\module.py"])
def test_scope_normalization_refuses_non_repository_relative_paths(value: str) -> None:
    with pytest.raises(task_run.TaskRunError, match="scope must be a repository-relative path"):
        task_run_scope._normalize_scope(value)


def test_normalize_scopes_requires_at_least_one_scope() -> None:
    with pytest.raises(task_run.TaskRunError, match="at least one --scope is required"):
        task_run_scope.normalize_scopes([])


def test_glob_validation_refuses_unmatched_and_invalid_character_classes() -> None:
    with pytest.raises(task_run.TaskRunError, match=r"unmatched '\]'"):
        task_run_scope._validate_glob_scope("pkg]/module.py")

    task_run_scope._validate_glob_scope("pkg/[a-z]/module.py")
    with pytest.raises(task_run.TaskRunError, match="invalid character class"):
        task_run_scope._validate_glob_scope("pkg/[]/module.py")


def test_unchanged_required_scope_is_a_failure_with_human_reason(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

    result = task_run_scope._scope_result(
        repo,
        base_sha,
        [{"path": "module.py", "kind": "exact"}],
        require_change=True,
    )

    assert result["verdict"] == task_run.FAIL
    assert result["reason"] == "the task required a change but the worktree is unchanged"


def test_generated_path_causes_identify_runtime_and_dependency_output() -> None:
    assert "runtime/cache output appeared" in task_run_scope._path_cause("__pycache__/module.pyc")
    assert "dependency/install output appeared" in task_run_scope._path_cause(
        "node_modules/package/index.js"
    )


def test_directory_scope_includes_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.py")
    _git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "add package")
    executable = _codex(tmp_path, "printf 'CHILD = 1\n' > pkg/child.py")

    payload = _run(repo, tmp_path, executable, scopes=["pkg"])

    assert payload["status"] == "completed", payload
    assert payload["scope"]["specs"] == [{"path": "pkg", "kind": "directory"}]
    assert payload["scope"]["changed_paths"] == ["pkg/child.py"]


def test_task_run_accepts_a_clean_committed_candidate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\n"
        "git add -- module.py\n"
        "git -c user.email=test@example.com -c user.name=test commit -m 'update module'",
    )

    payload = _run(repo, tmp_path, executable)

    worktree = Path(payload["worktree_path"])
    assert payload["status"] == "completed", payload
    assert payload["target_sha"] != payload["base_sha"]
    assert payload["scope"]["changed_paths"] == ["module.py"]
    assert payload["candidate"]["status"] == "validated"
    assert payload["candidate"]["useful"] is True
    assert payload["candidate"]["changed_paths"] == ["module.py"]
    assert payload["candidate"]["carrier_kind"] == "commit-only"
    assert payload["candidate"]["committed_paths"] == ["module.py"]
    assert payload["candidate"]["dirty_paths"] == []
    assert payload["candidate"]["head_sha"] == payload["target_sha"]
    assert payload["candidate"]["head_is_complete"] is True
    assert payload["candidate"]["content_digest"]
    assert payload["approval_eligibility"] == "eligible"
    assert "the typed result is approval-eligible" in payload["next_step"]
    assert _git(worktree, "status", "--short").stdout == ""


def test_worktree_only_receipt_names_untracked_bytes_as_the_complete_candidate(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'NEW = 1\\n' > new_module.py")

    payload = _run(repo, tmp_path, executable, scopes=["new_module.py"])

    candidate = payload["candidate"]
    assert payload["status"] == "completed", payload
    assert candidate["changed_paths"] == ["new_module.py"]
    assert candidate["carrier_kind"] == "worktree-only"
    assert candidate["committed_paths"] == []
    assert candidate["dirty_paths"] == ["new_module.py"]
    assert candidate["head_sha"] is None
    assert candidate["head_is_complete"] is False
    assert candidate["content_digest"]
    assert "no lane commit exists" in payload["next_step"]
    assert "not the complete candidate" in payload["next_step"]


def test_mixed_receipt_says_lane_head_is_only_a_proper_subset(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(
        tmp_path,
        "printf 'VALUE = 2\\n' > module.py\n"
        "git add -- module.py\n"
        "git -c user.email=test@example.com -c user.name=test commit -m 'update module'\n"
        "printf 'EXTRA = 1\\n' > extra.py",
    )

    payload = _run(repo, tmp_path, executable, scopes=["module.py", "extra.py"])

    candidate = payload["candidate"]
    assert payload["status"] == "completed", payload
    assert candidate["changed_paths"] == ["extra.py", "module.py"]
    assert candidate["carrier_kind"] == "commit-plus-dirty"
    assert candidate["committed_paths"] == ["module.py"]
    assert candidate["dirty_paths"] == ["extra.py"]
    assert candidate["head_sha"] == payload["target_sha"]
    assert candidate["head_is_complete"] is False
    assert candidate["content_digest"]
    assert "lane HEAD commit is a proper subset" in payload["next_step"]
    assert "approval-eligible" not in payload["next_step"]


def test_candidate_digest_detects_retained_worktree_byte_drift(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'NEW = 1\\n' > new_module.py")

    payload = _run(repo, tmp_path, executable, scopes=["new_module.py"])
    worktree = Path(payload["worktree_path"])
    original_digest = payload["candidate"]["content_digest"]
    (worktree / "new_module.py").write_bytes(b"NEW = 2\n")

    moved = task_run_git._candidate_carrier(worktree, payload["base_sha"])

    assert moved["changed_paths"] == ["new_module.py"]
    assert moved["content_digest"] != original_digest


def test_candidate_carrier_reuses_equal_head_worktree_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    git_calls: list[tuple[str, ...]] = []
    status_calls: list[dict] = []
    original_git = task_run_git._git
    original_status = checkout_view.capture_status

    def traced_git(root: Path, *args: str):
        git_calls.append(args)
        return original_git(root, *args)

    def traced_status(root, **kwargs):
        status_calls.append(kwargs)
        return original_status(root, **kwargs)

    monkeypatch.setattr(task_run_git, "_git", traced_git)
    monkeypatch.setattr(checkout_view, "capture_status", traced_status)
    monkeypatch.setattr(
        task_run_git,
        "_is_ancestor",
        lambda *_args: pytest.fail("equal HEAD and base must not spawn merge-base"),
    )

    carrier = task_run_git._candidate_carrier(repo, base)

    assert carrier["base_is_ancestor_of_head"] is True
    assert carrier["carrier_kind"] == "worktree-only"
    assert carrier["observed_head_sha"] == base
    assert git_calls == []
    assert len(status_calls) == 1
    assert status_calls[0].get("ignored") is True


def test_candidate_carrier_reuses_committed_diff_for_a_clean_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = "a" * 40
    head = "b" * 40
    diff_calls: list[tuple[str, ...]] = []

    def diff_paths(_repo: Path, *revisions: str) -> list[str]:
        diff_calls.append(revisions)
        return ["module.py"]

    monkeypatch.setattr(task_run_git, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(task_run_git, "_diff_paths", diff_paths)
    monkeypatch.setattr(
        task_run_git,
        "_collect_populations",
        lambda _repo: {"tracked": [], "untracked": [], "ignored": []},
    )

    carrier = task_run_git._candidate_carrier(tmp_path, base, head=head)

    assert carrier["carrier_kind"] == "commit-only"
    assert carrier["committed_paths"] == ["module.py"]
    assert carrier["changed_paths"] == ["module.py"]
    assert diff_calls == [(base, head)]


def test_candidate_carrier_reads_untracked_paths_once_for_a_commit_plus_dirty_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "update module", "module.py")
    (repo / "extra.py").write_text("VALUE = 3\n", encoding="utf-8")
    git_calls: list[tuple[str, ...]] = []
    status_calls: list[dict] = []
    ancestry_calls: list[tuple[Path, str, str]] = []
    original_git = task_run_git._git
    original_is_ancestor = task_run_git._is_ancestor
    original_status = checkout_view.capture_status

    def traced_git(root: Path, *args: str):
        git_calls.append(args)
        return original_git(root, *args)

    def traced_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
        ancestry_calls.append((root, ancestor, descendant))
        return original_is_ancestor(root, ancestor, descendant)

    def traced_status(root, **kwargs):
        status_calls.append(kwargs)
        return original_status(root, **kwargs)

    monkeypatch.setattr(task_run_git, "_git", traced_git)
    monkeypatch.setattr(task_run_git, "_is_ancestor", traced_is_ancestor)
    monkeypatch.setattr(checkout_view, "capture_status", traced_status)

    carrier = task_run_git._candidate_carrier(repo, base)

    assert carrier["carrier_kind"] == "commit-plus-dirty"
    assert carrier["committed_paths"] == ["module.py"]
    assert carrier["dirty_paths"] == ["extra.py"]
    assert carrier["changed_paths"] == ["extra.py", "module.py"]
    assert len(status_calls) == 1
    assert status_calls[0].get("ignored") is True
    assert ("rev-parse", "HEAD") not in git_calls
    assert len(git_calls) + len(status_calls) == 3
    assert len(ancestry_calls) == 1
    assert len(git_calls) + len(status_calls) + len(ancestry_calls) == 4


def test_candidate_carrier_keeps_base_scope_when_worktree_restores_a_committed_path(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "update module", "module.py")
    (repo / "module.py").write_text("VALUE = 1\n", encoding="utf-8")

    carrier = task_run_git._candidate_carrier(repo, base)

    assert carrier["committed_paths"] == ["module.py"]
    assert carrier["dirty_paths"] == ["module.py"]
    # The lane commit and the worktree edit cancel relative to the selected
    # base.  The current dirty status must not widen the base-relative scope.
    assert carrier["changed_paths"] == []
    assert carrier["carrier_kind"] == "commit-plus-dirty"


def test_explicit_base_scope_resolution_uses_selected_tree_for_dry_run(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    (repo / "literal[1].py").write_text("VALUE = 1\n", encoding="utf-8")
    selected_base = _commit(repo, "add selected base paths", "pkg", "literal[1].py")
    (repo / "current-only.py").write_text("CURRENT = 1\n", encoding="utf-8")
    _commit(repo, "add current-only path", "current-only.py")
    executable = _codex(tmp_path, "exit 99")

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/base-dry-run",
        base=selected_base,
        scopes=["pkg", "literal[1].py", "current-only", "*.py"],
        prompt="inspect the selected base",
        codex=str(executable),
        effort="medium",
        dry_run=True,
    )

    specs = {spec["path"]: spec for spec in payload["scope_specs"]}
    assert specs["pkg"] == {"path": "pkg", "kind": "directory"}
    assert specs["literal[1].py"] == {"path": "literal[1].py", "kind": "exact"}
    assert specs["current-only"] == {"path": "current-only", "kind": "exact"}
    assert specs["*.py"]["kind"] == "glob"
    assert "current-only.py" not in specs["*.py"]["matches"]
    assert payload["status"] == "pass"
    assert not (tmp_path / "lane").exists()


def test_task_creation_uses_the_preflight_resolved_base_sha(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    frozen_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "branch", "moving-base", frozen_sha)
    (repo / "later.py").write_text("LATER = 1\n", encoding="utf-8")
    later_sha = _commit(repo, "advance main", "later.py")
    executable = _codex(tmp_path, "printf 'VALUE = 2\n' > module.py")
    original_run_create = task_run._worktree.run_create
    observed: dict[str, str | None] = {}

    def move_ref_then_create(*args, **kwargs):
        observed["base"] = kwargs.get("base")
        _git(repo, "update-ref", "refs/heads/moving-base", later_sha)
        return original_run_create(*args, **kwargs)

    monkeypatch.setattr(task_run._worktree, "run_create", move_ref_then_create)
    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/frozen-base",
        base="moving-base",
        scopes=["module.py"],
        prompt="update the module",
        codex=str(executable),
        effort="medium",
    )

    assert payload["status"] == "completed", payload
    assert payload["base"] == "moving-base"
    assert payload["base_sha"] == frozen_sha
    assert observed["base"] == frozen_sha
    assert _git(Path(payload["worktree_path"]), "rev-parse", "HEAD").stdout.strip() == frozen_sha


def test_explicit_base_glob_does_not_use_current_parent_head(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    selected_base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "current-only.py").write_text("CURRENT = 1\n", encoding="utf-8")
    _commit(repo, "add current-only path", "current-only.py")
    executable = _codex(tmp_path, "exit 0")

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/base-glob-refusal",
        base=selected_base,
        scopes=["current-*.py"],
        prompt="inspect the selected base",
        codex=str(executable),
        effort="medium",
        dry_run=True,
    )

    assert payload["status"] == "fail"
    assert payload["phase"] == "preflight"
    assert "scope glob matched no paths" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_literal_metacharacter_file_takes_exact_precedence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "literal[1].py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "literal1.py").write_text("OTHER = 1\n", encoding="utf-8")
    _commit(repo, "add literal metacharacter paths", "literal[1].py", "literal1.py")
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > 'literal[1].py'")

    payload = _run(repo, tmp_path, executable, scopes=["literal[1].py"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [{"path": "literal[1].py", "kind": "exact"}]
    assert payload["scope"]["changed_paths"] == ["literal[1].py"]


def test_literal_metacharacter_directory_takes_directory_precedence(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg*").mkdir()
    (repo / "pkg*/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _commit(repo, "add literal metacharacter directory", "pkg*")
    executable = _codex(tmp_path, "printf 'CHILD = 1\\n' > 'pkg*/child.py'")

    payload = _run(repo, tmp_path, executable, scopes=["pkg*"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [{"path": "pkg*", "kind": "directory"}]
    assert payload["scope"]["changed_paths"] == ["pkg*/child.py"]


def test_bare_double_star_scope_includes_top_level_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "printf 'VALUE = 2\\n' > module.py")

    payload = _run(repo, tmp_path, executable, scopes=["**"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"][0]["kind"] == "glob"
    assert "module.py" in payload["scope_specs"][0]["matches"]
    assert payload["scope"]["disallowed_paths"] == []


def test_glob_scope_does_not_mix_ignored_external_symlink_into_candidate_verdict(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    (repo / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    _commit(repo, "ignore local runtime", ".gitignore")
    executable = _codex(
        tmp_path,
        "mkdir -p .venv/bin\nln -s /usr/bin/python3 .venv/bin/python3",
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["**"],
        require_change=False,
    )

    assert payload["status"] == "completed", payload
    assert payload["scope"]["verdict"] == "pass"
    assert payload["scope"]["changed_paths"] == []
    assert payload["populations"]["ignored"]["verdict"] == "warn"
    assert payload["populations"]["ignored"]["added"] == [".venv/"]


def test_glob_scope_freezes_matches_and_allows_new_matching_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.py").write_text("BASE = 1\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.py")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "add package",
    )
    executable = _codex(
        tmp_path,
        "mkdir -p pkg/sub\nprintf 'CHILD = 1\\n' > pkg/sub/child.py",
    )

    payload = _run(repo, tmp_path, executable, scopes=["pkg/**/*.py"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"] == [
        {
            "path": "pkg/**/*.py",
            "kind": "glob",
            "matches": ["pkg/base.py"],
            "match_count": 1,
            "directory_matches": [],
        }
    ]
    assert payload["scope"]["specs"][0]["matches"] == [
        "pkg/base.py",
        "pkg/sub/child.py",
    ]
    assert payload["scope"]["changed_paths"] == ["pkg/sub/child.py"]


def test_glob_scope_that_matches_a_directory_includes_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg/base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "pkg/base.txt")
    _git(
        repo,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "commit",
        "-m",
        "add package",
    )
    executable = _codex(tmp_path, "printf 'child\\n' > pkg/child.txt")

    payload = _run(repo, tmp_path, executable, scopes=["pkg*"])

    assert payload["status"] == "completed", payload
    assert payload["scope_specs"][0]["directory_matches"] == ["pkg"]
    assert payload["scope"]["changed_paths"] == ["pkg/child.txt"]


def test_new_glob_matching_directory_does_not_widen_to_descendants(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "base.py").write_text("BASE = 1\n", encoding="utf-8")
    _commit(repo, "add base match", "base.py")
    executable = _codex(
        tmp_path,
        "mkdir escape.py\nprintf 'not python\\n' > escape.py/secret.txt",
    )

    payload = _run(repo, tmp_path, executable, scopes=["*.py"])

    assert payload["status"] == "failed"
    assert payload["scope"]["disallowed_paths"] == ["escape.py/secret.txt"]
    assert payload["scope"]["specs"][0]["directory_matches"] == []


def test_zero_match_glob_fails_before_worktree_creation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    payload = _run(repo, tmp_path, executable, scopes=["missing/**/*.py"])

    assert payload["status"] == "fail"
    assert payload["phase"] == "preflight"
    assert "scope glob matched no paths" in payload["error"]
    assert not (tmp_path / "lane").exists()


def test_absent_scope_remains_exact_when_command_creates_a_directory(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "mkdir newdir\nprintf 'VALUE = 1\\n' > newdir/item.py")

    payload = _run(repo, tmp_path, executable, scopes=["newdir"])

    assert payload["status"] == "failed"
    assert payload["scope"]["specs"] == [{"path": "newdir", "kind": "exact"}]
    assert payload["scope"]["disallowed_paths"] == ["newdir/item.py"]


def _lane_tree(tmp_path, kind: str):
    """A lane worktree in one of the histories a receipt must tell apart."""
    from tests.quality_gates.repo_shapes import install_committed_repo

    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(tmp_path), *args],
            check=True, capture_output=True,
        )

    install_committed_repo(tmp_path, {"seed.txt": "s\n"}, message="base")
    base = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    if kind == "amended-base":
        (tmp_path / "seed.txt").write_text("s2\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "--amend", "-m", "amended base")
    elif kind == "descendant":
        (tmp_path / "work.py").write_text("x = 1\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "lane work")
    return base


def test_a_non_descendant_head_is_not_a_commit_carrier(tmp_path) -> None:
    """`head != base` answers "did HEAD move", not "does HEAD carry the candidate".

    A lane that amends its own base leaves a CLEAN tree at a sibling commit. The
    inequality test called that `commit-only` with `head_is_complete: true`, which
    invites the parent to cherry-pick a commit that replays against the wrong parent
    instead of carrying the validated base-to-worktree candidate.
    """
    base = _lane_tree(tmp_path, "amended-base")

    carrier = task_run_git._candidate_carrier(tmp_path, base)

    assert carrier["base_is_ancestor_of_head"] is False
    assert carrier["head_is_complete"] is False
    assert carrier["head_sha"] is None
    # ...and the sibling commit is still REPORTED, so the receipt does not read like a
    # lane that never committed at all.
    assert carrier["observed_head_sha"] != base


def test_a_descendant_head_with_a_clean_tree_is_still_the_whole_candidate(tmp_path) -> None:
    """The control: the ancestry check must not disqualify an ordinary lane commit."""
    base = _lane_tree(tmp_path, "descendant")

    carrier = task_run_git._candidate_carrier(tmp_path, base)

    assert carrier["base_is_ancestor_of_head"] is True
    assert carrier["carrier_kind"] == "commit-only"
    assert carrier["head_is_complete"] is True
    assert carrier["head_sha"] == carrier["observed_head_sha"]
