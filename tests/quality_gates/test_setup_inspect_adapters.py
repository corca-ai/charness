from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.setup import setup_adapter_inspect_lib
from tests.quality_gates.repo_shapes import replace_with_committed_repo

from .support import SETUP_RESOLVE_ADAPTER, inspect_setup_repo


def _make_active_worktrees(repo: Path, count: int) -> None:
    """Initialize `repo` as a git repo with `count - 1` extra worktrees attached.

    `count` is the total number of worktrees reported by `git worktree list`
    (so 2 means the main repo plus one linked worktree).
    """
    replace_with_committed_repo(repo, message="init")
    for index in range(count - 1):
        worktree_dir = repo.parent / f"{repo.name}-wt-{index}"
        subprocess.run(
            ["git", "worktree", "add", str(worktree_dir), "-b", f"branch-{index}"],
            cwd=repo,
            check=True,
            capture_output=True,
        )


def _run_inspect(repo: Path) -> dict[str, object]:
    return inspect_setup_repo(repo)


def _seed_normalize_repo(repo: Path, agents_text: str) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def _seed_minimal_repo_with_adapter(repo: Path) -> None:
    _seed_normalize_repo(repo, "# Agents\n")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: repo\n",
        encoding="utf-8",
    )


def test_setup_inspect_refuses_unsupported_adapter_before_surface_overrides(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 7\n"
        "output_dir: private-provider/output\n"
        "surfaces:\n"
        "  readme: private-provider/README.md\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["adapter"]["valid"] is False
    assert payload["adapter"]["warnings"] == [
        {"type": "invalid_adapter_version", "message": "version must be 1"}
    ]
    assert payload["surfaces"]["readme"]["path"] == "README.md"
    assert "configured_path" not in payload["surfaces"]["readme"]
    assert payload["surfaces"]["readme"]["source"] == "default"

    resolver_payload = SETUP_RESOLVE_ADAPTER.load_adapter(repo)
    assert resolver_payload["valid"] is False
    assert resolver_payload["errors"] == ["version must be 1"]
    assert resolver_payload["data"]["output_dir"] == "charness-artifacts/setup"


def test_setup_inspect_reports_present_worktree_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")
    (repo / ".agents" / "worktree-adapter.yaml").write_text("version: 1\n", encoding="utf-8")

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "lefthook"
    assert worktree_state["adapter_exists"] is True

    finding_types = {
        finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]
    }
    assert "worktree_adapter_missing_for_hook_manager" not in finding_types


def test_setup_inspect_reports_no_worktree_finding_without_hook_manager(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] is None
    assert worktree_state["hook_manager_evidence"] == []
    assert worktree_state["worktree_count"] == 0
    # Non-git tmp dir: probe must report `not_a_git_repo`, not silently 0.
    assert worktree_state["worktree_probe_status"] == "not_a_git_repo"


def test_setup_inspect_reports_active_worktrees_without_hook_manager(tmp_path: Path) -> None:
    """Multiple worktrees remain a diagnostic finding, not a setup recommendation."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    _make_active_worktrees(repo, count=3)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] is None
    assert worktree_state["worktree_count"] >= 2
    assert worktree_state["worktree_probe_status"] == "ok"
    assert worktree_state["adapter_exists"] is False

    finding_types = {
        finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]
    }
    assert "worktree_adapter_missing_for_active_worktrees" in finding_types
    assert "worktree_adapter_missing_for_hook_manager" not in finding_types


def _run_inspect_with_env(repo: Path, env: dict[str, str]) -> dict[str, object]:
    return inspect_setup_repo(repo, env=env)


def test_setup_inspect_emits_probe_unavailable_finding_when_git_is_missing(tmp_path: Path) -> None:
    """A1: probe_status not equal to ok must reach the operator surface."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    # Hide the real git by making PATH point at a bin dir without a `git` entry.
    # Combined with python_dir, python3 still resolves but `git` raises
    # FileNotFoundError → probe_status == "git_missing".
    fake_bin = tmp_path / "no-git-bin"
    fake_bin.mkdir()
    env = {"PATH": f"{fake_bin}"}

    payload = _run_inspect_with_env(repo, env)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["worktree_probe_status"] == "git_missing"
    assert worktree_state["worktree_count"] == 0

    finding_types = {
        finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]
    }
    assert "worktree_probe_unavailable" in finding_types


def test_setup_inspect_reports_probe_gap_alongside_hook_manager(tmp_path: Path) -> None:
    """A failed worktree probe and a detected hook manager remain diagnostics."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")
    fake_bin = tmp_path / "no-git-bin"
    fake_bin.mkdir()
    env = {"PATH": f"{fake_bin}"}

    payload = _run_inspect_with_env(repo, env)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["worktree_probe_status"] == "git_missing"
    finding_types = {
        finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]
    }
    assert "worktree_adapter_missing_for_hook_manager" in finding_types
    assert "worktree_probe_unavailable" in finding_types


def test_setup_inspect_reports_both_worktree_signals_without_recommendations(
    tmp_path: Path,
) -> None:
    """Hook and active-worktree signals are retained as diagnostics only."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")
    _make_active_worktrees(repo, count=3)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "lefthook"
    assert worktree_state["worktree_count"] >= 2

    finding_types = {
        finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]
    }
    assert finding_types >= {
        "worktree_adapter_missing_for_hook_manager",
        "worktree_adapter_missing_for_active_worktrees",
    }


def test_probe_active_worktrees_skips_git_spawn_on_non_repo_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-repo tmp dir must never spawn `git worktree list`.

    `git worktree list` on a non-repo also exits non-zero and lands on the
    same `not_a_git_repo` status the preflight returns, so checking only the
    return value would still pass with the spawn left in place. Forbidding
    the spawn is the only proof the filesystem preflight is load-bearing.
    """

    def _forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("git subprocess must not run for a non-repo path")

    monkeypatch.setattr(setup_adapter_inspect_lib, "run_process", _forbidden)

    count, status = setup_adapter_inspect_lib._probe_active_worktrees(tmp_path)

    assert (count, status) == (0, "not_a_git_repo")


def test_probe_active_worktrees_reports_git_missing_before_repo_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing `git` binary must still win over `not_a_git_repo`.

    `shutil.which` returning `None` short-circuits before the (also
    spawn-free) discoverability check runs, preserving the pre-existing
    priority: a missing binary was `git_missing` regardless of repo shape.
    """

    monkeypatch.setattr(setup_adapter_inspect_lib.shutil, "which", lambda _name: None)

    def _forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("git subprocess must not run when the binary is missing")

    monkeypatch.setattr(setup_adapter_inspect_lib, "run_process", _forbidden)

    count, status = setup_adapter_inspect_lib._probe_active_worktrees(tmp_path)

    assert (count, status) == (0, "git_missing")


def test_setup_inspect_reports_setup_adapter_absence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n")

    payload = _run_inspect(repo)

    init_state = payload["agent_docs"]["normalization"]["setup_adapter"]
    assert init_state["adapter_exists"] is False
    assert init_state["adapter_path"] is None


def test_setup_inspect_reports_present_setup_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)

    payload = _run_inspect(repo)

    init_state = payload["agent_docs"]["normalization"]["setup_adapter"]
    assert init_state["adapter_exists"] is True
