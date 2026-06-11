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
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK, encoding="utf-8")
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
                "    model: gpt-5.5",
                "    reasoning_effort: high",
                "    service_tier: priority",
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
    assert critique_adapter["high_leverage_model"] == "gpt-5.5"
    assert critique_adapter["high_leverage_reasoning_effort"] == "high"
    assert "critique_adapter_codex_reasoning_effort_drift" in finding_types
    recommendation = recommendation_by_id["critique_adapter_codex_reasoning_effort_drift"]
    assert recommendation["target"] == ".agents/critique-adapter.yaml"
    assert recommendation["priority"] == "review_required"
