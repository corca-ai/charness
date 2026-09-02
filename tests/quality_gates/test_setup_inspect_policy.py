from __future__ import annotations

from pathlib import Path

import pytest

from scripts.setup import setup_inspect_quality_lib

from .support import inspect_setup_repo
from .support import seed_normalize_repo as _seed_normalize_repo


def _run_inspect(repo: Path) -> dict[str, object]:
    return inspect_setup_repo(repo)


def test_setup_inspect_reports_core_and_conditional_surfaces(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "PARTIAL"
    assert payload["partial_kind"] == "targeted_missing_surface"
    assert payload["missing_surfaces"] == ["docs_index"]
    assert (
        payload["conditional_surfaces"]["roadmap"]["applicability"]
        == "unproven — operator decision"
    )
    assert payload["conditional_surfaces"]["operator_acceptance"]["activation"] == (
        "a real install, deployment, or takeover path exists"
    )


def test_setup_inspect_exposes_plan_without_making_policy_claims(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "package.json").write_text(
        '{"name":"demo","scripts":{"lint":"eslint ."},"devDependencies":{"eslint":"1.0.0"}}\n',
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["profile"]["id"] == "flat-wiki"
    assert payload["profile"]["approval_required"] is True
    assert payload["profile"]["plan_only"] is True
    assert payload["quality_setup"]["owner_skill"] == "quality"
    normalization = payload["agent_docs"]["normalization"]
    assert "fresh_eye_review" not in normalization
    assert "critique_adapter" not in normalization
    assert "charness_subagent_policy" not in normalization
    assert "recommendation_policy" not in normalization
    assert "agents.delegated_review_policy" not in str(payload)


def test_setup_inspect_preserves_existing_hook_manager(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".husky").mkdir(parents=True)
    (repo / ".husky" / "pre-commit").write_text("#!/bin/sh\nnpm test\n", encoding="utf-8")

    payload = _run_inspect(repo)

    tooling = payload["quality_setup"]["tooling"]
    assert tooling["hook_manager"] == "husky"
    assert tooling["hook_policy"]["existing_manager_action"] == "preserve-and-integrate"


def test_setup_inspect_keeps_setup_mutation_approval_enabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: demo\napproval_required: false\n", encoding="utf-8"
    )

    payload = _run_inspect(repo)

    assert payload["adapter"]["valid"] is False
    assert payload["profile"]["approval_required"] is True
    assert any(
        "approval_required must remain true" in item["message"]
        for item in payload["adapter"]["warnings"]
    )


def test_setup_inspect_binds_docs_inventory_to_plan_identity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "nested").mkdir(parents=True)
    topic = repo / "docs" / "nested" / "topic.md"
    topic.write_text("# Topic\n", encoding="utf-8")

    first = _run_inspect(repo)
    assert "docs/nested/topic.md" in first["docs_inventory"]["nested_paths"]
    topic.write_text("# Changed\n", encoding="utf-8")
    second = _run_inspect(repo)

    assert first["approval_plan"]["identity"] != second["approval_plan"]["identity"]


def test_setup_inspect_fails_closed_on_unknown_profile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noperating_surface_profile: mystery\n", encoding="utf-8"
    )

    payload = _run_inspect(repo)

    assert payload["adapter"]["valid"] is False
    assert payload["profile"]["id"] == "flat-wiki"


def test_setup_inspect_matches_default_surfaces_case_insensitively(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / "docs" / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/ROADMAP.md"


def test_setup_inspect_honors_surface_override(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / "docs" / "master-plan.md").write_text("# Plan\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: repo\nsurfaces:\n  roadmap: docs/master-plan.md\n", encoding="utf-8"
    )

    payload = _run_inspect(repo)

    assert payload["surfaces"]["roadmap"]["path"] == "docs/master-plan.md"
    assert payload["surfaces"]["roadmap"]["source"] == "adapter"


def test_setup_inspect_reports_source_guard_wrap_conflict(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nA guarded sentence.\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "# Spec\n\n| path | matcher | pattern |\n| --- | --- | --- |\n"
        "| README.md | fixed | A guarded sentence. |\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "version: 1\nrepo: repo\nprose_wrap_policy: column\n", encoding="utf-8"
    )

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "requires_override"
    assert payload["prose_wrap"]["source_guard_count"] == 1


def test_setup_inspect_reports_retro_memory_without_enforcing_root_prose(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nCustom local routing.\n")
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "recent-lessons.md").write_text(
        "# Recent Lessons\n", encoding="utf-8"
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]

    assert normalization["retro_memory"]["enabled"] is True
    assert normalization["retro_memory"]["policy_owner"] == "retro"
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert "agents_missing_retro_recent_lessons_memory" not in finding_types
    assert "retro_summary_without_adapter" not in finding_types


def test_detect_hook_policy_skips_git_spawn_on_non_repo_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-repo tmp dir must never spawn `git config`, not merely return None.

    Asserting only the return value would still pass with the spawn in place
    (a non-repo `git config --get` also yields an unset-looking empty
    string). Forbidding the spawn outright is the only way to prove the
    filesystem preflight actually short-circuits it.
    """

    def _forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("git subprocess must not run for a non-repo path")

    monkeypatch.setattr(setup_inspect_quality_lib, "run_process", _forbidden)

    result = setup_inspect_quality_lib._detect_hook_policy(tmp_path, {})

    assert result["hook_manager"] is None
    assert result["hook_policy"]["existing_manager_action"] == "propose-lefthook"


def test_setup_inspect_does_not_recreate_removed_root_policies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nUse local judgment.\n")
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        "# Quality Review\n", encoding="utf-8"
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}

    assert "charness_artifacts_commit_policy_drift" not in finding_types
