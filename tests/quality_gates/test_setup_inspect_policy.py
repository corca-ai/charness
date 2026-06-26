from __future__ import annotations

from pathlib import Path

from .support import inspect_setup_repo


def _run_inspect(repo: Path) -> dict[str, object]:
    return inspect_setup_repo(repo)


def _seed_normalize_repo(repo: Path, agents_text: str) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def test_setup_inspect_repo_flags_targeted_missing_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "PARTIAL"
    assert payload["partial_kind"] == "targeted_missing_surface"
    assert payload["missing_surfaces"] == ["operator_acceptance"]


def test_setup_inspect_repo_matches_default_surfaces_case_insensitively(tmp_path: Path) -> None:
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


def test_setup_inspect_repo_honors_adapter_surface_overrides(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "master-plan.md").write_text("# Plan\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: docs/master-plan.md", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/master-plan.md"
    assert payload["surfaces"]["roadmap"]["source"] == "adapter"


def test_setup_inspect_repo_excludes_acknowledged_missing_core_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: null", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["kind"] == "acknowledged_missing"


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
    (repo / ".agents" / "setup-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")


def test_setup_inspect_warns_for_column_wrap_fixed_source_guards(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: column"])

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "requires_override"
    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["warnings"][0]["type"] == "column_wrap_fixed_guard_requires_override"


def test_setup_inspect_accepts_column_wrap_when_matcher_normalizes(tmp_path: Path) -> None:
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


def test_setup_inspect_skips_unreadable_markdown_source_guard_specs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: semantic"])
    broken_target = tmp_path / "missing-session-log.md"
    (repo / "docs" / "session-log.md").symlink_to(broken_target)

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "ok"
    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["warnings"] == [
        {
            "type": "source_guard_markdown_unreadable",
            "path": "docs/session-log.md",
            "message": "Skipped unreadable markdown while scanning source guards: No such file or directory",
        }
    ]


def test_setup_inspect_ignores_hidden_markdown_workflow_dirs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: semantic"])
    (repo / ".cwf" / "projects").mkdir(parents=True)
    (repo / ".cwf" / "projects" / "session-log.md").symlink_to(tmp_path / "missing-session-log.md")

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["warnings"] == []


def test_setup_inspect_reports_malformed_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text("- not-a-dict\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["adapter"]["found"] is True
    assert payload["adapter"]["valid"] is False
    assert payload["adapter"]["warnings"][0]["type"] == "adapter_root_not_mapping"


def test_setup_inspect_reports_retro_memory_agents_drift(tmp_path: Path) -> None:
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


def test_setup_inspect_reports_fresh_eye_delegation_drift(tmp_path: Path) -> None:
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
    assert normalization["fresh_eye_review"]["missing_task_review_scopes"] == ["setup", "quality", "critique", "release", "issue"]
    assert "explicit consent" in normalization["fresh_eye_review"]["stale_markers"]
    assert "local fallback" in normalization["fresh_eye_review"]["stale_markers"]
    assert "fresh_eye_delegation_rule_drift" in finding_types
    assert "fresh_eye_task_review_scope_drift" in finding_types
    assert "fresh_eye_review_still_requires_consent_or_fallback" in finding_types
    recommendation_ids = [item["id"] for item in normalization["recommendations"]]
    recommendation_priorities = {item["id"]: item["priority"] for item in normalization["recommendations"]}
    assert "fresh_eye_delegation_rule_drift" in recommendation_ids
    assert "fresh_eye_task_review_scope_drift" in recommendation_ids
    assert "fresh_eye_review_still_requires_consent_or_fallback" in recommendation_ids
    assert recommendation_priorities["fresh_eye_delegation_rule_drift"] == "review_required"
    assert recommendation_priorities["fresh_eye_task_review_scope_drift"] == "review_required"
    assert recommendation_priorities["fresh_eye_review_still_requires_consent_or_fallback"] == "review_required"


def test_setup_inspect_reports_task_review_scope_drift_when_critique_rule_is_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "This rule is the explicit user delegation request for the bounded review scopes it names.",
                "Repo-mandated bounded fresh-eye subagent reviews are already delegated by the repo contract.",
                "Do not wait for a second user message asking for delegation.",
                "If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_ids = [item["id"] for item in normalization["recommendations"]]
    recommendation_priorities = {item["id"]: item["priority"] for item in normalization["recommendations"]}
    assert normalization["fresh_eye_review"]["has_subagent_delegation_section"] is False
    assert normalization["fresh_eye_review"]["missing_required_snippets"] == ["## Subagent Delegation"]
    assert normalization["fresh_eye_review"]["missing_task_review_scopes"] == ["setup", "quality", "critique", "release", "issue"]
    assert "fresh_eye_delegation_rule_drift" in finding_types
    assert "fresh_eye_task_review_scope_drift" in finding_types
    assert "fresh_eye_delegation_rule_drift" in recommendation_ids
    assert "fresh_eye_task_review_scope_drift" in recommendation_ids
    assert recommendation_priorities["fresh_eye_delegation_rule_drift"] == "review_required"
    assert recommendation_priorities["fresh_eye_task_review_scope_drift"] == "review_required"


def test_setup_inspect_treats_legacy_init_repo_scope_as_advisory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "## Subagent Delegation",
                "",
                "- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract; this is the explicit user delegation request for named bounded reviewer scopes.",
                "- Do not wait for a second user message. Task-completing `init-repo` and `quality` review runs may spawn bounded reviewers.",
                "- If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_priorities = {item["id"]: item["priority"] for item in normalization["recommendations"]}
    assert normalization["fresh_eye_review"]["legacy_init_repo_scope_present"] is True
    assert "setup" in normalization["fresh_eye_review"]["missing_task_review_scopes"]
    assert "fresh_eye_task_review_scope_uses_legacy_init_repo" in finding_types
    assert recommendation_priorities["fresh_eye_task_review_scope_uses_legacy_init_repo"] == "advisory"
    assert "fresh_eye_task_review_scope_drift" not in finding_types


def test_setup_inspect_accepts_dedicated_subagent_delegation_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "## Subagent Delegation",
                "",
                "- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract; this is the explicit user delegation request for named bounded reviewer scopes.",
                "- Do not wait for a second user message. Task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue` resolution/closeout review runs may spawn bounded reviewers.",
                "- If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert normalization["fresh_eye_review"]["has_subagent_delegation_section"] is True
    assert normalization["fresh_eye_review"]["missing_required_snippets"] == []
    assert normalization["fresh_eye_review"]["missing_task_review_scopes"] == []
    assert "fresh_eye_delegation_rule_drift" not in finding_types
    assert "fresh_eye_task_review_scope_drift" not in finding_types


_COMPACT_PRE_303_BLOCK = (
    "- Repo-mandated bounded fresh-eye subagent reviews are a standing delegation request. "
    "Canonical scopes: task-completing `setup`, `quality`, `critique`, `release`, and GitHub "
    "`issue` resolution/closeout review runs. Report a host block explicitly; same-agent "
    "substitutes are forbidden."
)
_COMPACT_ADAPTER_FIRST_RULE = (
    "- When a skill or repo adapter owns a subagent review, follow that adapter's reviewer tier "
    "and concrete spawn fields instead of inheriting the parent turn's host defaults."
)


def _compact_agents(*bullets: str) -> str:
    return "\n".join(["# Agents", "", "## Subagent Delegation", "", *bullets, ""])


def test_setup_inspect_accepts_compact_subagent_delegation_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, _compact_agents(_COMPACT_PRE_303_BLOCK, _COMPACT_ADAPTER_FIRST_RULE))

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["has_subagent_delegation_section"] is True
    assert fresh_eye["compact_contract_present"] is True
    assert fresh_eye["missing_required_snippets"] == []
    assert fresh_eye["missing_task_review_scopes"] == []
    assert "fresh_eye_delegation_rule_drift" not in finding_types
    assert "fresh_eye_task_review_scope_drift" not in finding_types


def test_setup_inspect_flags_compact_delegation_missing_adapter_first_reviewer_rule(tmp_path: Path) -> None:
    # #311: an existing compact AGENTS.md written before the #303 adapter-first
    # reviewer rule landed carries every PRE-303 required snippet (standing
    # delegation request, canonical scopes, host block, same-agent forbidden) but
    # lacks the adapter reviewer-tier language. The inspector must flag it STALE
    # (never rewrite the body) so the operator is told to backfill the rule. The
    # `_COMPACT_PRE_303_BLOCK` isolates the missing adapter-first rule as the sole
    # difference from the accepted block below.
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, _compact_agents(_COMPACT_PRE_303_BLOCK))

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["has_subagent_delegation_section"] is True
    # The pre-303 compact block is no longer accepted as a complete contract: the
    # missing adapter reviewer-tier rule fails the compact-contract check, which is
    # what surfaces the staleness drift finding.
    assert fresh_eye["compact_contract_present"] is False
    assert "fresh_eye_delegation_rule_drift" in finding_types
    recommendation_priorities = {item["id"]: item["priority"] for item in normalization["recommendations"]}
    assert recommendation_priorities["fresh_eye_delegation_rule_drift"] == "review_required"


def test_setup_inspect_accepts_compact_delegation_with_adapter_first_reviewer_rule(tmp_path: Path) -> None:
    # #311 companion: the SAME compact block, with only the adapter-first reviewer
    # rule added, must NOT falsely flag. This pins that the staleness gate keys on
    # the adapter rule specifically and does not regress an up-to-date body.
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, _compact_agents(_COMPACT_PRE_303_BLOCK, _COMPACT_ADAPTER_FIRST_RULE))

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["compact_contract_present"] is True
    assert fresh_eye["missing_required_snippets"] == []
    assert "fresh_eye_delegation_rule_drift" not in finding_types


def test_setup_inspect_accepts_generated_compact_subagent_delegation_block(tmp_path: Path) -> None:
    # Pin template<->inspector agreement against the ACTUAL generator output (#304).
    # `render_agents_template` line-wraps the compact block to satisfy markdown
    # line-length limits, so contract phrases straddle line breaks. The sibling
    # single-line test above never exercised that wrapping, which is exactly why
    # the wrapped default used to trip `fresh_eye_delegation_rule_drift`.
    from scripts.setup_host_docs_lib import render_agents_template

    repo = tmp_path / "repo"
    agents_text = render_agents_template(
        skill_routing_markdown="## Skill Routing\n\n- Route via find-skills."
    )
    # Guard the regression: the generated block must wrap these phrases across
    # lines so this test keeps exercising whitespace-normalized matching rather
    # than silently degrading into the contiguous single-line case.
    assert "standing delegation request" not in agents_text
    assert "host block" not in agents_text

    _seed_normalize_repo(repo, agents_text)

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["has_subagent_delegation_section"] is True
    assert fresh_eye["compact_contract_present"] is True
    assert fresh_eye["missing_required_snippets"] == []
    assert fresh_eye["missing_task_review_scopes"] == []
    assert "fresh_eye_delegation_rule_drift" not in finding_types
    assert "fresh_eye_task_review_scope_drift" not in finding_types


def test_generated_agents_carries_adapter_first_reviewer_rule(tmp_path: Path) -> None:
    # #303: setup-generated AGENTS.md must carry an adapter-first subagent
    # reviewer rule (follow the adapter's tier + concrete spawn fields, not
    # inherited host defaults), without weakening standing-delegation language,
    # and without asserting a global `medium` tier.
    from scripts.setup_host_docs_lib import render_agents_template

    repo = tmp_path / "repo"
    agents_text = render_agents_template(
        skill_routing_markdown="## Skill Routing\n\n- Route via find-skills."
    )
    normalized = " ".join(agents_text.split())

    # Adapter-first rule present.
    assert "follow that adapter's reviewer tier" in normalized
    assert "instead of inheriting the parent" in normalized
    assert "stop and report the concrete signal" in normalized
    # `medium` is named only as the conditional Codex critique default, never as
    # a global claim — the rule must explicitly disclaim "every subagent".
    assert "unless it says otherwise" in normalized
    assert "not a claim that every subagent is medium" in normalized
    # Standing-delegation language remains intact.
    assert "standing delegation request" in normalized
    assert "same-agent substitutes are forbidden" in normalized

    # The new rule must not regress the inspector: still compact-contract-clean.
    _seed_normalize_repo(repo, agents_text)
    payload = _run_inspect(repo)
    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["compact_contract_present"] is True
    assert fresh_eye["weakening_caveats_detected"] == []
    assert "fresh_eye_delegation_rule_drift" not in finding_types
    assert "fresh_eye_delegation_caveat_weakens_contract" not in finding_types


def test_setup_inspect_rejects_compact_delegation_that_allows_same_agent_substitute(tmp_path: Path) -> None:
    # Same-agent ALLOWED block carries the adapter-first rule, so the only failing
    # condition is the same-agent-forbidden check (not the #311 adapter snippet).
    allows_same_agent = _COMPACT_PRE_303_BLOCK.replace(
        "same-agent substitutes are forbidden.", "same-agent substitutes are allowed."
    )
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, _compact_agents(allows_same_agent, _COMPACT_ADAPTER_FIRST_RULE))

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    fresh_eye = normalization["fresh_eye_review"]
    assert fresh_eye["compact_contract_present"] is False
    assert "same-agent pass" in fresh_eye["missing_required_snippets"]
    assert "fresh_eye_delegation_rule_drift" in finding_types


_SUBAGENT_DELEGATION_AFFIRMATIVE = (
    "- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract; this is the explicit user delegation request for named bounded reviewer scopes.",
    "- Do not wait for a second user message. Task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue` resolution/closeout review runs may spawn bounded reviewers.",
    "- If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.",
)


def _agents_with_delegation_section(*, heading: str = "## Subagent Delegation", caveats: tuple[str, ...] = (), trailing: tuple[str, ...] = ()) -> str:
    body = ["# Agents", "", heading, "", *_SUBAGENT_DELEGATION_AFFIRMATIVE, *caveats, ""]
    if trailing:
        body.extend([*trailing, ""])
    return "\n".join(body)


def test_setup_inspect_flags_weakening_caveat_inside_subagent_delegation_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    caveat = "- If a higher-priority host, tool, or developer policy requires explicit user delegation, follow that stricter rule before spawning."
    _seed_normalize_repo(repo, _agents_with_delegation_section(caveats=(caveat,)))

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    fresh_eye = normalization["fresh_eye_review"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_priorities = {item["id"]: item["priority"] for item in normalization["recommendations"]}
    assert fresh_eye["missing_required_snippets"] == []
    assert "higher-priority host" in fresh_eye["weakening_caveats_detected"]
    assert "follow that stricter rule" in fresh_eye["weakening_caveats_detected"]
    assert "fresh_eye_delegation_caveat_weakens_contract" in finding_types
    assert recommendation_priorities["fresh_eye_delegation_caveat_weakens_contract"] == "advisory"
    assert "fresh_eye_delegation_rule_drift" not in finding_types
    assert "fresh_eye_task_review_scope_drift" not in finding_types


def test_setup_inspect_flags_weakening_caveat_with_mixed_case_heading(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    caveat = "- If a higher-priority host policy requires explicit user delegation, follow that stricter rule before spawning."
    _seed_normalize_repo(repo, _agents_with_delegation_section(heading="## Subagent delegation", caveats=(caveat,)))

    payload = _run_inspect(repo)

    fresh_eye = payload["agent_docs"]["normalization"]["fresh_eye_review"]
    finding_types = {f["type"] for f in payload["agent_docs"]["normalization"]["findings"]}
    assert fresh_eye["has_subagent_delegation_section"] is True
    assert "higher-priority host" in fresh_eye["weakening_caveats_detected"]
    assert "fresh_eye_delegation_caveat_weakens_contract" in finding_types


def test_setup_inspect_does_not_flag_caveat_phrase_outside_subagent_delegation_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    trailing = (
        "## Notes On Multi-Host Operation",
        "",
        "- We sometimes coordinate with a higher-priority host policy in adjacent repos; that does not change this repo's standing delegation contract.",
    )
    _seed_normalize_repo(repo, _agents_with_delegation_section(trailing=trailing))

    payload = _run_inspect(repo)

    fresh_eye = payload["agent_docs"]["normalization"]["fresh_eye_review"]
    finding_types = {f["type"] for f in payload["agent_docs"]["normalization"]["findings"]}
    assert fresh_eye["weakening_caveats_detected"] == []
    assert "fresh_eye_delegation_caveat_weakens_contract" not in finding_types


def test_setup_inspect_reports_charness_artifacts_commit_policy_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        "# Quality Review\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_ids = [item["id"] for item in payload["recommendations"]]
    recommendation_priorities = {item["id"]: item["priority"] for item in payload["recommendations"]}
    assert normalization["charness_artifacts"]["uses_charness_artifacts"] is True
    assert "repo state" in normalization["charness_artifacts"]["missing_required_snippets"]
    assert "canonical content" in normalization["charness_artifacts"]["missing_required_snippets"]
    assert "charness_artifacts_commit_policy_drift" in finding_types
    assert "charness_artifacts_commit_policy_drift" in recommendation_ids
    assert recommendation_priorities["charness_artifacts_commit_policy_drift"] == "review_required"


def test_setup_inspect_detects_charness_artifacts_from_adapter_output_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/setup",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    recommendation_ids = [item["id"] for item in payload["recommendations"]]
    recommendation_priorities = {item["id"]: item["priority"] for item in payload["recommendations"]}
    assert normalization["charness_artifacts"]["uses_charness_artifacts"] is True
    assert "charness_artifacts_commit_policy_drift" in recommendation_ids
    assert recommendation_priorities["charness_artifacts_commit_policy_drift"] == "review_required"


def test_setup_inspect_accepts_charness_artifacts_commit_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "Treat `charness-artifacts/` as repo state, not scratch.",
                "Current-pointer helpers should be no-op when their canonical content has not changed.",
                "",
            ]
        ),
    )
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        "# Quality Review\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert normalization["charness_artifacts"]["uses_charness_artifacts"] is True
    assert normalization["charness_artifacts"]["missing_required_snippets"] == []
    assert "charness_artifacts_commit_policy_drift" not in finding_types


def test_setup_inspect_requires_decision_for_custom_skill_routing_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")

    payload = _run_inspect(repo)

    skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    recommendation_priorities = {item["id"]: item["priority"] for item in payload["recommendations"]}
    assert skill_routing["has_skill_routing"] is True
    assert skill_routing["matches_compact_block"] is False
    assert skill_routing["recommended_action"] == "review_existing_skill_routing"
    assert skill_routing["decision_needed"] == "leave_as_is_or_replace_with_compact_block"
    assert "skill_routing_block_custom_or_drifted" in finding_types
    assert recommendation_priorities["skill_routing_block_custom_or_drifted"] == "review_required"


def test_setup_inspect_accepts_compact_discovery_first_skill_routing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "- At session startup, call `find-skills` once to discover capability routing before broader exploration.",
                "- Then choose the installed durable work skill that best matches the task.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert skill_routing["matches_compact_block"] is False
    assert skill_routing["accepts_compact_discovery_first"] is True
    assert skill_routing["find_skills_available"] is True
    assert skill_routing["decision_needed"] is None
    assert "skill_routing_block_custom_or_drifted" not in finding_types


def test_setup_inspect_rejects_custom_routing_that_mentions_optional_find_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "- At startup, use custom routing first; find-skills is optional for capability notes.",
                "- Preserve local routing choices over generated discovery output.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert skill_routing["accepts_compact_discovery_first"] is False
    assert skill_routing["decision_needed"] == "leave_as_is_or_replace_with_compact_block"
    assert "skill_routing_block_custom_or_drifted" in finding_types


def test_setup_inspect_rejects_cross_line_compact_routing_keyword_cooccurrence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(
        repo,
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "- At startup, run custom routing once before broader exploration.",
                "- find-skills is optional for capability notes.",
                "",
            ]
        ),
    )

    payload = _run_inspect(repo)

    skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
    finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert skill_routing["accepts_compact_discovery_first"] is False
    assert "skill_routing_block_custom_or_drifted" in finding_types


def test_setup_inspect_rejects_same_line_bad_compact_routing(tmp_path: Path) -> None:
    bad_lines = (
        "- At startup, run custom routing once before broader exploration; find-skills is optional for capability notes.",
        "- At session startup, do not run find-skills once for capability routing before broader exploration.",
    )
    for index, line in enumerate(bad_lines):
        repo = tmp_path / f"repo-{index}"
        _seed_normalize_repo(repo, "\n".join(["# Agents", "", "## Skill Routing", "", line, ""]))
        payload = _run_inspect(repo)
        skill_routing = payload["agent_docs"]["normalization"]["skill_routing"]
        finding_types = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
        assert skill_routing["accepts_compact_discovery_first"] is False
        assert "skill_routing_block_custom_or_drifted" in finding_types


def test_setup_inspect_emits_policy_source_recommendation_without_agents_marker(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-policy.md").write_text(
        "# Review Policy\n\nTask-completing setup, quality, critique, release, and issue runs need bounded fresh-eye review.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "setup-adapter.yaml").write_text(
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
        "adapter_path": str(repo / ".agents" / "setup-adapter.yaml"),
    }
    policy = payload["agent_docs"]["normalization"]["recommendation_policy"]
    assert policy["defaults_version"] == "issue-64"
    assert policy["policy_source_count"] == 1


def test_setup_inspect_acknowledgement_suppresses_only_named_recommendation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-policy.md").write_text(
        "# Review Policy\n\nTask-completing quality runs require critique review.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "setup-adapter.yaml").write_text(
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


def test_setup_inspect_recomputes_status_when_all_contextual_findings_are_acknowledged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\n## Skill Routing\n\nUse local judgment.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "setup-adapter.yaml").write_text(
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


def test_setup_inspect_dedupes_policy_source_recommendations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_normalize_repo(repo, "# Agents\n\nExisting operating policy.\n")
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs" / "review-a.md").write_text("fresh-eye review required\n", encoding="utf-8")
    (repo / "docs" / "review-b.md").write_text("critique required\n", encoding="utf-8")
    (repo / ".agents" / "setup-adapter.yaml").write_text(
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
