from __future__ import annotations

from pathlib import Path

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

# #317: setup seeds a compact meaningful-slice commit-discipline block in a
# greenfield AGENTS.md, and the inspector flags an AGENTS.md that has Charness
# goal/skill routing but no commit-discipline rule (same tell-don't-rewrite
# pattern as #311). These tests pin BOTH the seed and the stale detection, and
# guard the never-rewrite-existing-body contract. The inspection chain is driven
# in-process (detect_agent_docs + the detector + the wiring constants) so the
# tests prove the finding/recommendation path without a subprocess boundary.

_SKILL_ROUTING_BLOCK = (
    "## Skill Routing\n\n"
    "- At session startup, call `find-skills` once before broader exploration.\n"
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


def test_greenfield_template_seeds_commit_discipline_block() -> None:
    # Acceptance (1): a freshly-seeded AGENTS.md contains the compact
    # commit-discipline block. Pin against the ACTUAL generator output, including
    # both halves of the two-policy rule the issue names.
    agents_text = render_agents_template(skill_routing_markdown=_SKILL_ROUTING_BLOCK)
    normalized = " ".join(agents_text.split())

    assert "## Commit Discipline" in agents_text
    # (ii) meaningful implementation/workflow slices are committed as they finish.
    assert "Commit meaningful work slices as they finish" in normalized
    assert "keep each commit scoped" in normalized
    # (i) meaningful charness-artifacts/ changes are repo state and commit targets.
    assert "meaningful `charness-artifacts/` changes as repo state" in normalized
    # Do-not-report-done-while-uncommitted, with explicit-deferral carve-out.
    assert "remains uncommitted, unless the deferral is" in normalized
    # The two policies are explicitly distinguished, not collapsed into one.
    assert "The two policies differ" in normalized
    # The generated block must satisfy the inspector's own detector so setup does
    # not seed a body that immediately re-flags as stale.
    assert commit_discipline_present(agents_text) is True


def test_greenfield_template_passes_inspector(tmp_path: Path) -> None:
    agents_text = render_agents_template(skill_routing_markdown=_SKILL_ROUTING_BLOCK)
    normalization = _detect(tmp_path / "repo", agents_text)

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["has_goal_routing"] is True
    assert commit_discipline["commit_discipline_present"] is True
    assert "commit_discipline_drift" not in finding_types


def test_inspect_flags_goal_routing_without_commit_discipline(tmp_path: Path) -> None:
    # Acceptance (2): an AGENTS.md that carries Charness goal/skill routing but no
    # commit-discipline rule is flagged STALE (never rewritten) so the operator is
    # told to backfill the rule. This is the open-ax-day symptom #317 records.
    repo = tmp_path / "repo"
    body = _agents(_SKILL_ROUTING_BLOCK)
    normalization = _detect(repo, body)

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["has_goal_routing"] is True
    assert commit_discipline["commit_discipline_present"] is False
    assert "commit_discipline_drift" in finding_types
    # The drift surfaces as a review_required recommendation, not an advisory.
    assert "commit_discipline_drift" in RECOMMENDATION_FINDING_TYPES
    assert FINDING_RECOMMENDATION_PRIORITIES["commit_discipline_drift"] == "review_required"
    # Acceptance (3): the existing body is NOT rewritten by inspection.
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == body


def test_inspect_flags_artifact_only_body_for_missing_slice_rule(tmp_path: Path) -> None:
    # The two related policies must be distinguished: a body that only repeats the
    # charness-artifacts/ commit-target policy still lacks the meaningful-slice
    # rule, so commit-discipline drift must still fire when goal routing is present.
    normalization = _detect(tmp_path / "repo", _agents(_SKILL_ROUTING_BLOCK, _ARTIFACT_ONLY_BLOCK))

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["commit_discipline_present"] is False
    assert "commit_discipline_drift" in finding_types


def test_inspect_accepts_goal_routing_with_commit_discipline(tmp_path: Path) -> None:
    # Companion to the stale case: the SAME goal-routed body with the commit
    # discipline rule added must NOT falsely flag. Pins that the gate keys on the
    # commit-discipline rule specifically and does not regress an up-to-date body.
    normalization = _detect(tmp_path / "repo", _agents(_SKILL_ROUTING_BLOCK, _COMMIT_DISCIPLINE_BLOCK))

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["has_goal_routing"] is True
    assert commit_discipline["commit_discipline_present"] is True
    assert "commit_discipline_drift" not in finding_types


def test_inspect_skips_commit_discipline_without_goal_routing(tmp_path: Path) -> None:
    # Tell-don't-rewrite is scoped to Charness goal/skill-routed repos: a plain
    # AGENTS.md with no Charness routing markers must not be flagged, so the gate
    # does not nag non-Charness consumer repos.
    normalization = _detect(tmp_path / "repo", _agents("Existing operating policy with no Charness routing."))

    commit_discipline = normalization["commit_discipline"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert commit_discipline["has_goal_routing"] is False
    assert "commit_discipline_drift" not in finding_types


def test_commit_discipline_detector_requires_both_halves() -> None:
    # Unit guard: the detector must require BOTH a slice rule and a
    # not-done-while-uncommitted rule. A body with only one half is not present,
    # so a partial paste does not silently pass the inspector.
    slice_only = "Commit meaningful work slices as they finish; keep each commit scoped."
    not_done_only = "Do not report a goal as done while meaningful work remains uncommitted."
    assert commit_discipline_present(slice_only) is False
    assert commit_discipline_present(not_done_only) is False
    assert commit_discipline_present(slice_only + " " + not_done_only) is True


def test_detector_finding_message_names_both_policies() -> None:
    # The finding message must teach the operator the two distinct policies, not
    # just say "add commit discipline".
    _, findings = detect_commit_discipline_policy(_agents(_SKILL_ROUTING_BLOCK))
    assert len(findings) == 1
    message = findings[0]["message"].lower()
    assert "slices as they finish" in message
    assert "uncommitted" in message
    assert findings[0]["recommended_action"] == "add_meaningful_slice_commit_discipline_to_agents"
