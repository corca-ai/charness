from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _run_inspect(repo: Path) -> dict[str, object]:
    result = run_script("skills/public/init-repo/scripts/inspect_repo.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _seed_normalize_repo(repo: Path, agents_text: str) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def test_init_repo_inspect_repo_flags_targeted_missing_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "PARTIAL"
    assert payload["partial_kind"] == "targeted_missing_surface"
    assert payload["missing_surfaces"] == ["operator_acceptance"]


def test_init_repo_inspect_repo_matches_default_surfaces_case_insensitively(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/ROADMAP.md"


def test_init_repo_inspect_repo_honors_adapter_surface_overrides(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "master-plan.md").write_text("# Plan\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: docs/master-plan.md", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/master-plan.md"
    assert payload["surfaces"]["roadmap"]["source"] == "adapter"


def test_init_repo_inspect_repo_excludes_acknowledged_missing_core_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: null", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["kind"] == "acknowledged_missing"


def test_init_repo_render_skill_routing_defaults_to_compact_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_script("skills/public/init-repo/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["skill_routing_mode_source"] == "default"
    assert "find-skills" in payload["public_skills"]
    assert payload["listed_skill_ids"] == ["find-skills"]
    assert "call the shared/public charness skill `find-skills` once at startup before broader exploration" in payload["markdown"]
    assert "default map of installed public skills, support skills, synced support surfaces, and integrations" in payload["markdown"]
    assert "choose the durable work skill that best matches the request" in payload["markdown"]
    assert "release-note style summary or chat-ready human update" not in payload["markdown"]


def test_init_repo_render_skill_routing_suggests_add_block_for_mature_agents(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_script("skills/public/init-repo/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def _seed_source_guard_repo(repo: Path, adapter_lines: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nA sentence that is guarded.\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | A sentence that is guarded. |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".agents" / "init-repo-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")


def test_init_repo_inspect_warns_for_column_wrap_fixed_source_guards(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: column"])

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "requires_override"
    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["warnings"][0]["type"] == "column_wrap_fixed_guard_requires_override"


def test_init_repo_inspect_accepts_column_wrap_when_matcher_normalizes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(
        repo,
        [
            "version: 1",
            "repo: repo",
            "prose_wrap_policy: column",
            "source_guard_matcher:",
            "  normalize_whitespace: true",
        ],
    )

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "ok"
    assert payload["prose_wrap"]["matcher_normalizes_whitespace"] is True


def test_init_repo_inspect_reports_malformed_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "init-repo-adapter.yaml").write_text("- not-a-dict\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["adapter"]["found"] is True
    assert payload["adapter"]["valid"] is False
    assert payload["adapter"]["warnings"][0]["type"] == "adapter_root_not_mapping"


def test_init_repo_inspect_reports_retro_memory_agents_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nCustom local routing.\n")
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "recent-lessons.md").write_text(
        "# Recent Lessons\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert normalization["status"] == "needs_normalization"
    assert normalization["retro_memory"]["enabled"] is True
    assert normalization["retro_memory"]["summary_exists"] is True
    assert normalization["retro_memory"]["adapter_exists"] is False
    assert normalization["retro_memory"]["agents_mentions_summary"] is False
    assert "agents_missing_retro_recent_lessons_memory" in finding_types
    assert "retro_summary_without_adapter" in finding_types


def test_init_repo_inspect_reports_fresh_eye_delegation_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "Run fresh-eye review only after explicit consent.",
                "If spawning is unavailable, use a local fallback.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert normalization["fresh_eye_review"]["stop_gate_detected"] is True
    assert "already delegated" in normalization["fresh_eye_review"]["missing_required_snippets"]
    assert "explicit consent" in normalization["fresh_eye_review"]["stale_markers"]
    assert "local fallback" in normalization["fresh_eye_review"]["stale_markers"]
    assert "fresh_eye_delegation_rule_drift" in finding_types
    assert "fresh_eye_review_still_requires_consent_or_fallback" in finding_types
    recommendation_ids = [item["id"] for item in normalization["recommendations"]]
    assert "fresh_eye_delegation_rule_drift" in recommendation_ids


def test_init_repo_inspect_requires_decision_for_custom_skill_routing_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")

    payload = _run_inspect(repo)

    skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert skill_routing["has_skill_routing"] is True
    assert skill_routing["matches_compact_block"] is False
    assert skill_routing["recommended_action"] == "review_existing_skill_routing"
    assert skill_routing["decision_needed"] == "leave_as_is_or_replace_with_compact_block"
    assert "skill_routing_block_custom_or_drifted" in finding_types


def test_init_repo_inspect_emits_policy_source_recommendation_without_agents_marker(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-policy.md").write_text(
        "# Review Policy\n\nTask-completing init-repo and quality runs need bounded fresh-eye review.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "defaults_version: issue-64",
                "policy_sources:",
                "  - id: review-policy",
                "    path: docs/review-policy.md",
                "    evidence_terms:",
                "      - bounded fresh-eye review",
                "recommendation_sets:",
                "  enabled:",
                "    - agents.delegated_review_policy",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    recommendations = payload["recommendations"]
    assert recommendations[0]["id"] == "agents.delegated_review_policy"
    assert recommendations[0]["priority"] == "review_required"
    assert recommendations[0]["enforcement_tier"] == "NON_AUTOMATABLE"
    assert "AGENTS.md lacks delegated-review host restriction wording" in recommendations[0]["evidence"]
    assert recommendations[0]["acknowledgement"] == {
        "status": "unacknowledged",
        "adapter_path": str(repo / ".agents" / "init-repo-adapter.yaml"),
    }
    policy = payload["agent_docs"]["normalization"]["recommendation_policy"]
    assert policy["defaults_version"] == "issue-64"
    assert policy["policy_source_count"] == 1


def test_init_repo_inspect_acknowledgement_suppresses_only_named_recommendation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-policy.md").write_text(
        "# Review Policy\n\nTask-completing quality runs require premortem review.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "policy_sources:",
                "  - id: review-policy",
                "    path: docs/review-policy.md",
                "recommendation_sets:",
                "  acknowledged:",
                "    - skill_routing_block_custom_or_drifted",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    recommendation_ids = [item["id"] for item in payload["recommendations"]]
    assert "skill_routing_block_custom_or_drifted" not in finding_types
    assert "skill_routing_block_custom_or_drifted" not in recommendation_ids
    assert recommendation_ids == ["agents.delegated_review_policy"]
    assert payload["agent_docs"]["normalization"]["status"] == "needs_normalization"


def test_init_repo_inspect_recomputes_status_when_all_contextual_findings_are_acknowledged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "recommendation_sets:",
                "  acknowledged:",
                "    - skill_routing_block_custom_or_drifted",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    assert normalization["findings"] == []
    assert normalization["recommendations"] == []
    assert normalization["status"] == "ok"


def test_init_repo_inspect_dedupes_policy_source_recommendations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-a.md").write_text("fresh-eye review required\n", encoding="utf-8")
    (repo / "docs" / "review-b.md").write_text("premortem required\n", encoding="utf-8")
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "policy_sources:",
                "  - id: review-a",
                "    path: docs/review-a.md",
                "  - id: review-b",
                "    path: docs/review-b.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    recommendations = payload["recommendations"]
    assert [item["id"] for item in recommendations] == ["agents.delegated_review_policy"]
    assert any("docs/review-a.md" in item for item in recommendations[0]["evidence"])
    assert any("docs/review-b.md" in item for item in recommendations[0]["evidence"])
