from __future__ import annotations

import json
from pathlib import Path

from scripts.setup_agent_docs_lib import (
    FINDING_RECOMMENDATION_PRIORITIES,
    RECOMMENDATION_FINDING_TYPES,
    detect_agent_docs,
    finding_recommendation,
    sort_recommendations,
)

from .support import ROOT

COMPACT_SUBAGENT_BLOCK = "\n".join(
    [
        "# Agents",
        "",
        "## Subagent Delegation",
        "",
        "- Repo-mandated bounded fresh-eye subagent reviews are a standing delegation request. Canonical scopes: task-completing `setup`, `quality`, `critique`, `release`, and GitHub `issue` resolution/closeout review runs. Report a host block explicitly; same-agent substitutes are forbidden.",
        "- When a skill or repo adapter owns a subagent review, follow that adapter's reviewer tier and concrete spawn fields instead of inheriting the parent turn's host defaults.",
        "",
    ]
)

# The `## Skill Routing` block that marks a repo charness-managed. The subagent-model
# check only fires for a managed repo, so both polarity fixtures below need it.
CHARNESS_MANAGED_SKILL_ROUTING = "\n".join(
    [
        "# Agents",
        "",
        "## Skill Routing",
        "",
        "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
        "Run the read-only `charness catalog list` only when hidden availability is unclear.",
        "External URL sources route through gather before deciding.",
        "Validation work goes through quality first.",
        "A SessionStart hook is context-only, not a classifier.",
        "",
    ]
)

# The superseded Codex-specific block, kept as a NEGATIVE fixture. Commit 353fa4a5
# removed it from AGENTS.md because a host-specific model id does not belong in the
# contract; a doc still carrying only this must NOT satisfy the per-host check, or the
# validator would bless exactly the shape the contract now forbids.
SUPERSEDED_CODEX_PROFILE_POLICY = "\n".join(
    [
        "Charness-spawned subagents use Codex MultiAgent V2.",
        "Every Charness-spawned agent uses gpt-5.6-terra with medium reasoning effort.",
        'Use fork_turns: "none" because fork_turns: "all" rejects those overrides.',
    ]
)

# What the contract asserts today, and what the check now requires.
SUBAGENT_MODEL_POLICY = "\n".join(
    [
        "",
        "## Subagent Delegation",
        "",
        "**Subagent model/effort defaults are per-host, not one global value.**",
        "Use the host's own subagent controls, inheriting the session model by default.",
        "A host-specific model or flag request belongs in that host's adapter or preset, not here.",
    ]
)


def _run_inspect(repo: Path) -> dict[str, object]:
    agent_docs = detect_agent_docs(repo)
    findings = [
        finding
        for finding in agent_docs["normalization"]["findings"]
        if isinstance(finding, dict)
    ]
    recommendations = sort_recommendations(
        [
            finding_recommendation(
                finding,
                priority=FINDING_RECOMMENDATION_PRIORITIES.get(str(finding.get("type")), "advisory"),
            )
            for finding in findings
            if finding.get("type") in RECOMMENDATION_FINDING_TYPES
        ]
    )
    agent_docs["normalization"]["recommendations"] = recommendations
    return {"agent_docs": json.loads(json.dumps(agent_docs))}


def _seed_repo(repo: Path) -> None:
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK + SUPERSEDED_CODEX_PROFILE_POLICY, encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def test_setup_inspect_flags_missing_critique_adapter_for_fresh_eye_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_by_id = {item["id"]: item for item in normalization["recommendations"]}
    critique_adapter = normalization["critique_adapter"]
    assert critique_adapter["found"] is False
    assert "critique_adapter_missing_for_fresh_eye_review" in finding_types
    recommendation = recommendation_by_id["critique_adapter_missing_for_fresh_eye_review"]
    assert recommendation["target"] == ".agents/critique-adapter.yaml"
    assert recommendation["priority"] == "review_required"


def test_setup_inspect_reports_missing_charness_dynamic_and_codex_profile_policies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Run the read-only `charness catalog list` only when hidden availability is unclear.",
                "External URL sources route through gather before deciding.",
                "Validation work goes through quality first.",
                "A SessionStart hook is context-only, not a classifier.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["agent_docs"]["normalization"]["charness_subagent_policy"]["charness_managed"] is True
    findings = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    recommendations = {
        item["id"]: item for item in payload["agent_docs"]["normalization"]["recommendations"]
    }
    assert "agents_missing_charness_dynamic_workflow_policy" in findings
    assert "agents_missing_subagent_model_policy" in findings
    assert recommendations["agents_missing_charness_dynamic_workflow_policy"]["priority"] == "review_required"
    assert recommendations["agents_missing_subagent_model_policy"]["priority"] == "review_required"


def test_setup_inspect_ignores_ordinary_charness_mentions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(
        "# Agents\n\nInstall Charness when its public skills are useful.\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    findings = {finding["type"] for finding in normalization["findings"]}
    assert normalization["charness_subagent_policy"]["charness_managed"] is False
    assert "agents_missing_charness_dynamic_workflow_policy" not in findings
    assert "agents_missing_subagent_model_policy" not in findings


def test_setup_inspect_recognizes_live_charness_policy_with_inline_code() -> None:
    payload = _run_inspect(ROOT)

    normalization = payload["agent_docs"]["normalization"]
    findings = {finding["type"] for finding in normalization["findings"]}
    assert normalization["charness_subagent_policy"] == {
        "charness_managed": True,
        "dynamic_workflow_complete": True,
        "subagent_model_policy_complete": True,
    }
    assert "agents_missing_charness_dynamic_workflow_policy" not in findings
    assert "agents_missing_subagent_model_policy" not in findings


def test_the_superseded_codex_block_alone_does_not_satisfy_the_per_host_check(tmp_path: Path) -> None:
    """Direction, not presence.

    The check used to REQUIRE the Codex model-id tokens; commit 353fa4a5 deleted that
    block from AGENTS.md because a host-specific model id does not belong in the
    contract, and the validator was not moved with it -- so it demanded exactly what the
    contract had just forbidden, and main went red.

    These two cases pin the repaired direction by constructing both inputs: a doc
    carrying ONLY the superseded Codex block must NOT satisfy the check, and a doc
    carrying the per-host policy must. A presence-only assertion would be satisfied by a
    validator that had the polarity backwards.
    """
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(
        CHARNESS_MANAGED_SKILL_ROUTING + SUPERSEDED_CODEX_PROFILE_POLICY, encoding="utf-8"
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]

    assert normalization["charness_subagent_policy"]["subagent_model_policy_complete"] is False
    assert "agents_missing_subagent_model_policy" in {
        finding["type"] for finding in normalization["findings"]
    }


def test_the_per_host_subagent_model_policy_satisfies_the_check(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(
        CHARNESS_MANAGED_SKILL_ROUTING + SUBAGENT_MODEL_POLICY, encoding="utf-8"
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]

    assert normalization["charness_subagent_policy"]["subagent_model_policy_complete"] is True
    assert "agents_missing_subagent_model_policy" not in {
        finding["type"] for finding in normalization["findings"]
    }


def test_the_policy_phrases_do_not_count_from_outside_the_subagent_section(tmp_path: Path) -> None:
    """Scope, not just presence.

    Read document-wide, the three required phrases could be scattered across unrelated
    sections -- a changelog line, a doc-comment, a quoted note -- and satisfy the check
    while `## Subagent Delegation` said nothing about subagent models. Without this case
    the scoping is unproven: every other fixture puts the phrases inside the section, so
    a whole-document check passes all of them.
    """
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(
        CHARNESS_MANAGED_SKILL_ROUTING
        + "\n## Subagent Delegation\n\n- Spawn bounded reviewers when the contract calls for them.\n"
        + "\n## Notes\n\n"
        + "- Historical: subagent model/effort defaults are per-host was added, moving the\n"
        + "  model id into that host's adapter or preset and inheriting the session model.\n",
        encoding="utf-8",
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]

    assert normalization["charness_subagent_policy"]["subagent_model_policy_complete"] is False
    assert "agents_missing_subagent_model_policy" in {
        finding["type"] for finding in normalization["findings"]
    }


def test_setup_inspect_does_not_treat_generic_gpt_adapter_as_codex_policy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK, encoding="utf-8")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "reviewer_tiers:\n  high-leverage:\n    model: gpt-generic\n    reasoning_effort: high\n",
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    findings = {finding["type"] for finding in payload["agent_docs"]["normalization"]["findings"]}
    assert "critique_adapter_codex_profile_drift" not in findings


def test_setup_inspect_flags_codex_critique_adapter_reasoning_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/critique",
                "reviewer_tiers:",
                "  high-leverage:",
                "    model: gpt-5.6-terra",
                "    reasoning_effort: high",
                "    service_tier: priority",
                "    fork_turns: all",
                "  medium:",
                "    model: gpt-5.5",
                "    reasoning_effort: medium",
                "    fork_turns: all",
                "packet_sections: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    recommendation_by_id = {item["id"]: item for item in normalization["recommendations"]}
    critique_adapter = normalization["critique_adapter"]
    assert critique_adapter["found"] is True
    assert critique_adapter["high_leverage_model"] == "gpt-5.6-terra"
    assert critique_adapter["high_leverage_reasoning_effort"] == "high"
    assert critique_adapter["medium_model"] == "gpt-5.5"
    assert critique_adapter["medium_reasoning_effort"] == "medium"
    assert "critique_adapter_codex_profile_drift" in finding_types
    recommendation = recommendation_by_id["critique_adapter_codex_profile_drift"]
    assert recommendation["target"] == ".agents/critique-adapter.yaml"
    assert recommendation["priority"] == "review_required"
