from __future__ import annotations

from pathlib import Path

import scripts.setup_host_docs_lib as host_docs
from scripts.setup_agent_docs_lib import (
    FINDING_RECOMMENDATION_PRIORITIES,
    RECOMMENDATION_FINDING_TYPES,
    detect_agent_docs,
)
from scripts.setup_commit_discipline_lib import (
    commit_discipline_present,
    detect_commit_discipline_policy,
)
from scripts.setup_host_docs_lib import render_agents_template

_SKILL_ROUTING_BLOCK = (
    "## Skill Routing\n\n"
    "- At session startup, use installed skill metadata/model judgment; run `charness catalog list --repo-root .` only for hidden availability.\n"
)
_COMMIT_DISCIPLINE_BLOCK = (
    "## Commit Discipline\n\n"
    "- Commit meaningful work slices as they finish; keep each commit scoped.\n"
    "- Treat meaningful `charness-artifacts/` changes as repo state and commit them.\n"
    "- Do not report a task-completing goal as done while meaningful work remains "
    "uncommitted unless deferral is explicit.\n"
)
_ARTIFACT_ONLY_BLOCK = (
    "Treat `charness-artifacts/` as repo state, not scratch.\n"
    "Commit meaningful durable artifact changes with the work they support.\n"
    "Current-pointer helpers should be no-op when their canonical content has not changed.\n"
)


def _agents(*blocks: str) -> str:
    return "\n".join(["# Agents", "", *(block.strip() for block in blocks), ""])


def _detect(repo: Path, agents_text: str) -> dict[str, object]:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    return detect_agent_docs(repo, skill_routing_payload=None)["normalization"]


def test_greenfield_template_seeds_only_the_commit_discipline_contract() -> None:
    agents_text = render_agents_template(skill_routing_markdown=_SKILL_ROUTING_BLOCK)
    normalized = " ".join(agents_text.split())

    assert "## Commit Discipline" in agents_text
    assert "Commit meaningful work slices as they finish" in normalized
    assert "meaningful `charness-artifacts/` changes as repo state" in normalized
    assert "remains uncommitted, unless the deferral is" in normalized
    assert commit_discipline_present(agents_text) is True
    assert "## Subagent Delegation" not in agents_text
    assert "## Dynamic Workflows" not in agents_text


def test_greenfield_template_commit_fragment_is_the_single_writer_asset() -> None:
    template_dir = Path(host_docs.__file__).resolve().parent / "templates"
    assert (template_dir / "agents_commit_discipline.txt").read_text(encoding="utf-8") == host_docs.COMMIT_DISCIPLINE
    assert not (template_dir / "agents_subagent_delegation.txt").exists()


def test_greenfield_template_passes_commit_inspection(tmp_path: Path) -> None:
    normalization = _detect(
        tmp_path / "repo",
        render_agents_template(skill_routing_markdown=_SKILL_ROUTING_BLOCK),
    )

    assert normalization["commit_discipline"]["has_goal_routing"] is True
    assert normalization["commit_discipline"]["commit_discipline_present"] is True
    assert "commit_discipline_drift" not in {
        finding["type"] for finding in normalization["findings"]
    }


def test_inspect_flags_goal_routing_without_commit_discipline(tmp_path: Path) -> None:
    normalization = _detect(tmp_path / "repo", _agents(_SKILL_ROUTING_BLOCK))

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["has_goal_routing"] is True
    assert commit_discipline["commit_discipline_present"] is False
    assert "commit_discipline_drift" in finding_types
    assert "commit_discipline_drift" in RECOMMENDATION_FINDING_TYPES
    assert FINDING_RECOMMENDATION_PRIORITIES["commit_discipline_drift"] == "review_required"


def test_inspect_distinguishes_artifact_policy_from_slice_commit_policy(tmp_path: Path) -> None:
    normalization = _detect(tmp_path / "repo", _agents(_SKILL_ROUTING_BLOCK, _ARTIFACT_ONLY_BLOCK))

    assert normalization["commit_discipline"]["commit_discipline_present"] is False
    assert "commit_discipline_drift" in {
        finding["type"] for finding in normalization["findings"]
    }


def test_inspect_accepts_both_commit_discipline_halves(tmp_path: Path) -> None:
    normalization = _detect(tmp_path / "repo", _agents(_SKILL_ROUTING_BLOCK, _COMMIT_DISCIPLINE_BLOCK))

    assert normalization["commit_discipline"]["commit_discipline_present"] is True
    assert "commit_discipline_drift" not in {
        finding["type"] for finding in normalization["findings"]
    }


def test_commit_discipline_detector_requires_both_halves() -> None:
    slice_only = "Commit meaningful work slices as they finish; keep each commit scoped."
    not_done_only = "Do not report a goal as done while meaningful work remains uncommitted."
    assert commit_discipline_present(slice_only) is False
    assert commit_discipline_present(not_done_only) is False
    assert commit_discipline_present(slice_only + " " + not_done_only) is True


def test_detector_finding_message_names_both_policies() -> None:
    _, findings = detect_commit_discipline_policy(_agents(_SKILL_ROUTING_BLOCK))

    assert len(findings) == 1
    message = findings[0]["message"].lower()
    assert "slices as they finish" in message
    assert "uncommitted" in message
