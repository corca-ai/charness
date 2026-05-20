from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .support import run_script


def _make_active_worktrees(repo: Path, count: int) -> None:
    """Initialize `repo` as a git repo with `count - 1` extra worktrees attached.

    `count` is the total number of worktrees reported by `git worktree list`
    (so 2 means the main repo plus one linked worktree).
    """
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@e", "-c", "user.name=t", "commit", "--allow-empty", "-m", "init", "-q"],
        cwd=repo,
        check=True,
    )
    for index in range(count - 1):
        worktree_dir = repo.parent / f"{repo.name}-wt-{index}"
        subprocess.run(
            ["git", "worktree", "add", str(worktree_dir), "-b", f"branch-{index}"],
            cwd=repo,
            check=True,
            capture_output=True,
        )


def _run_inspect(repo: Path) -> dict[str, object]:
    result = run_script("skills/public/setup/scripts/inspect_repo.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _seed_normalize_repo(repo: Path, agents_text: str) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def _seed_minimal_repo_with_adapter(repo: Path) -> None:
    _seed_normalize_repo(repo, "# Agents\n")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: repo\n",
        encoding="utf-8",
    )


def test_setup_inspect_recommends_seed_worktree_adapter_for_lefthook(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "lefthook"
    assert worktree_state["hook_manager_evidence"] == ["lefthook.yml"]
    assert worktree_state["adapter_exists"] is False
    assert worktree_state["adapter_path"] == ".agents/worktree-adapter.yaml"
    assert "seed_worktree_adapter.py" in worktree_state["seed_command"]

    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert "worktree_adapter_missing_for_hook_manager" in finding_types

    rec_index = {item["id"]: item for item in payload["recommendations"]}
    assert "worktree_adapter_missing_for_hook_manager" in rec_index
    rec = rec_index["worktree_adapter_missing_for_hook_manager"]
    assert rec["target"] == ".agents/worktree-adapter.yaml"
    assert rec["kind"] == "seed_artifact"
    assert rec["priority"] == "medium"
    assert rec["enforcement_tier"] == "AUTOMATABLE"
    assert "seed_worktree_adapter.py" in rec["suggested_action"]
    assert any("hook manager detected: lefthook" in item for item in rec["evidence"])


def test_setup_inspect_recommends_seed_worktree_adapter_for_husky(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / ".husky").mkdir(parents=True)
    (repo / ".husky" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "husky"
    assert worktree_state["hook_manager_evidence"] == [".husky/"]
    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "worktree_adapter_missing_for_hook_manager" in rec_ids


def test_setup_inspect_recommends_seed_worktree_adapter_for_simple_git_hooks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "package.json").write_text(
        json.dumps({"name": "demo", "simple-git-hooks": {"pre-commit": "echo demo"}}),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "simple-git-hooks"
    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "worktree_adapter_missing_for_hook_manager" in rec_ids


def test_setup_inspect_skips_worktree_adapter_recommendation_when_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")
    (repo / ".agents" / "worktree-adapter.yaml").write_text("version: 1\n", encoding="utf-8")

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "lefthook"
    assert worktree_state["adapter_exists"] is True

    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert "worktree_adapter_missing_for_hook_manager" not in finding_types
    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "worktree_adapter_missing_for_hook_manager" not in rec_ids


def test_setup_inspect_skips_worktree_adapter_recommendation_when_no_hook_manager(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] is None
    assert worktree_state["hook_manager_evidence"] == []
    assert worktree_state["worktree_count"] == 0
    # Non-git tmp dir: probe must report `not_a_git_repo`, not silently 0.
    assert worktree_state["worktree_probe_status"] == "not_a_git_repo"

    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "worktree_adapter_missing_for_hook_manager" not in rec_ids
    assert "worktree_adapter_missing_for_active_worktrees" not in rec_ids


def test_setup_inspect_recommends_seed_worktree_adapter_for_active_worktrees_without_hook_manager(tmp_path: Path) -> None:
    """#180: cautilus shape — multiple worktrees but no Node hook manager."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    _make_active_worktrees(repo, count=3)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] is None
    assert worktree_state["worktree_count"] >= 2
    assert worktree_state["worktree_probe_status"] == "ok"
    assert worktree_state["adapter_exists"] is False

    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert "worktree_adapter_missing_for_active_worktrees" in finding_types
    assert "worktree_adapter_missing_for_hook_manager" not in finding_types

    rec_index = {item["id"]: item for item in payload["recommendations"]}
    assert "worktree_adapter_missing_for_active_worktrees" in rec_index
    rec = rec_index["worktree_adapter_missing_for_active_worktrees"]
    assert rec["priority"] == "advisory"
    assert rec["target"] == ".agents/worktree-adapter.yaml"
    assert "seed_worktree_adapter.py" in rec["suggested_action"]


def test_setup_inspect_prefers_hook_manager_recommendation_when_both_signals_fire(tmp_path: Path) -> None:
    """When hook manager AND active worktrees both apply, emit one medium-priority rec."""
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")
    _make_active_worktrees(repo, count=3)

    payload = _run_inspect(repo)

    worktree_state = payload["agent_docs"]["normalization"]["worktree_adapter"]
    assert worktree_state["hook_manager_detected"] == "lefthook"
    assert worktree_state["worktree_count"] >= 2

    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "worktree_adapter_missing_for_hook_manager" in rec_ids
    # Only one recommendation, not both.
    assert "worktree_adapter_missing_for_active_worktrees" not in rec_ids


def test_setup_inspect_promotes_setup_adapter_absence_to_recommendation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n")

    payload = _run_inspect(repo)

    init_state = payload["agent_docs"]["normalization"]["setup_adapter"]
    assert init_state["adapter_exists"] is False
    assert init_state["adapter_path"] is None

    rec_index = {item["id"]: item for item in payload["recommendations"]}
    assert "setup_adapter_missing" in rec_index
    rec = rec_index["setup_adapter_missing"]
    assert rec["target"] == ".agents/setup-adapter.yaml"
    assert rec["priority"] == "advisory"
    assert rec["kind"] == "seed_artifact"
    assert "preset provenance" in rec["suggested_action"]


def test_setup_inspect_omits_setup_adapter_recommendation_when_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_minimal_repo_with_adapter(repo)

    payload = _run_inspect(repo)

    init_state = payload["agent_docs"]["normalization"]["setup_adapter"]
    assert init_state["adapter_exists"] is True
    rec_ids = [item["id"] for item in payload["recommendations"]]
    assert "setup_adapter_missing" not in rec_ids
