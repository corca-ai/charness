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

    normalization = payload["agent_docs"]["normalization"]
    assert normalization["critique_adapter"]["found"] is True, (
        "the adapter did not load; a green here would prove nothing about the predicate"
    )
    findings = {finding["type"] for finding in normalization["findings"]}
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


def test_the_codex_profile_check_fires_for_a_consumer_shaped_repo(tmp_path: Path) -> None:
    """A check reachable only for a directory literally named `charness` is a permanent green.

    `codex_policy_evidenced` used to be `repo_root.name == "charness"` OR a prose token that NO
    writer in this repo emits — not a template, not a renderer, not this repo's own AGENTS.md.
    Both disjuncts fail for a real consumer, so a `review_required` finding could only be
    produced by a directory-name coincidence.

    Proven by CONSTRUCTION rather than by a passing suite: the repo below is named
    `my-product`, its AGENTS.md declares no Codex policy in prose at all, and its adapter
    declares the profile the way a consumer actually would. Before the repair this produced no
    finding no matter what the adapter said.
    """
    repo = tmp_path / "my-product"
    _seed_repo(repo)
    # No prose declaration whatsoever — the adapter is the only evidence of adoption.
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK, encoding="utf-8")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "reviewer_tiers:",
                "  high-leverage:",
                "    model: gpt-5.6-terra",
                "    reasoning_effort: high",
                "    fork_turns: all",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    normalization = payload["agent_docs"]["normalization"]
    finding_types = {finding["type"] for finding in normalization["findings"]}
    assert "critique_adapter_codex_profile_drift" in finding_types, (
        "the Codex profile check is still unreachable for a repo not named `charness`"
    )
    recommendation = {item["id"]: item for item in normalization["recommendations"]}[
        "critique_adapter_codex_profile_drift"
    ]
    assert recommendation["priority"] == "review_required"
    # Name the tier that drifted, not merely the finding: this adapter declares only
    # `high-leverage`, and an earlier version fired from an absent `medium` defaulting to an
    # empty dict — so the finding could be present for the wrong reason entirely.
    drift = next(
        finding
        for finding in normalization["findings"]
        if finding["type"] == "critique_adapter_codex_profile_drift"
    )
    assert "high-leverage" in drift["message"]
    assert not drift["message"].rstrip(".").endswith("medium"), (
        "the finding names a `medium` tier this adapter does not declare; an absent tier "
        "defaulting to an empty dict is what made this check cry wolf"
    )


def test_the_directory_name_is_not_what_makes_the_codex_check_fire(tmp_path: Path) -> None:
    """The inverse, which is what makes the test above mean something.

    Renaming a directory must not change a verdict about a repo's declared policy. Two repos,
    identical in every file, differing only in the name of the directory holding them: the
    finding must be the same. Before the repair one fired and the other could not.
    """
    verdicts = {}
    for name in ("charness", "my-product"):
        repo = tmp_path / name
        _seed_repo(repo)
        (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK, encoding="utf-8")
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "critique-adapter.yaml").write_text(
            "reviewer_tiers:\n  high-leverage:\n    model: gpt-5.6-terra\n"
            "    reasoning_effort: high\n    fork_turns: all\n",
            encoding="utf-8",
        )
        findings = _run_inspect(repo)["agent_docs"]["normalization"]["findings"]
        verdicts[name] = "critique_adapter_codex_profile_drift" in {f["type"] for f in findings}

    assert verdicts["charness"] == verdicts["my-product"] is True, verdicts


def test_a_repo_that_never_adopted_the_codex_profile_is_left_alone(tmp_path: Path) -> None:
    """The other half: widening reach must not turn the check into a wolf-crier.

    A repo pinning some other model has not adopted this profile, and telling it that its tiers
    drift from a Codex default would be noise at a repo that never opted in. Adoption is
    evidenced by the profile's MODEL — in the adapter or in prose — and drift is measured on
    the other fields.
    """
    repo = tmp_path / "my-product"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK, encoding="utf-8")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "reviewer_tiers:\n  high-leverage:\n    model: claude-opus-5\n    reasoning_effort: high\n",
        encoding="utf-8",
    )

    normalization = _run_inspect(repo)["agent_docs"]["normalization"]
    # Assert the adapter LOADED. Without this, an unparseable adapter produces the same green
    # and the test would pass for a reason that has nothing to do with the predicate.
    assert normalization["critique_adapter"]["found"] is True
    findings = {finding["type"] for finding in normalization["findings"]}
    assert "critique_adapter_codex_profile_drift" not in findings

    # And a prose declaration alone is enough, with no adapter model, because a hand-written
    # AGENTS.md must keep working — the reader must not become a comparison against one
    # renderer's output.
    (repo / "AGENTS.md").write_text(
        COMPACT_SUBAGENT_BLOCK + "\nReviewers run gpt-5.6-terra at medium effort.\n",
        encoding="utf-8",
    )
    prose_findings = {
        finding["type"]
        for finding in _run_inspect(repo)["agent_docs"]["normalization"]["findings"]
    }
    assert "critique_adapter_codex_profile_drift" in prose_findings


def _drift_findings(repo: Path) -> set[str]:
    return {
        finding["type"]
        for finding in _run_inspect(repo)["agent_docs"]["normalization"]["findings"]
    }


def _seed_consumer(tmp_path: Path, tiers: str, *, agents_extra: str = "") -> Path:
    repo = tmp_path / "my-product"
    _seed_repo(repo)
    (repo / "AGENTS.md").write_text(COMPACT_SUBAGENT_BLOCK + agents_extra, encoding="utf-8")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nreviewer_tiers:\n" + tiers, encoding="utf-8"
    )
    return repo


_PERFECT_HIGH = "  high-leverage:\n    model: gpt-5.6-terra\n    reasoning_effort: medium\n    fork_turns: none\n"


def test_a_repo_declaring_one_correct_tier_is_not_told_it_drifted(tmp_path: Path) -> None:
    """Drift is measured over DECLARED tiers, not over a fixed pair defaulting to empty.

    A first version compared against the literal `high-leverage`/`medium` pair, each defaulting
    to `{}` when absent — so a consumer declaring ONE correct tier drifted against an empty
    dict whose every field is `None != expected`, producing a `review_required` finding naming
    a tier it does not have. That is the wolf-cry this repair set out to avoid, made newly
    reachable for consumers by removing the directory-name gate that had hidden it.
    """
    repo = _seed_consumer(tmp_path, _PERFECT_HIGH)
    adapter = _run_inspect(repo)["agent_docs"]["normalization"]["critique_adapter"]
    assert adapter["found"] is True, "the adapter did not load; a green here would prove nothing"
    assert "critique_adapter_codex_profile_drift" not in _drift_findings(repo)


def test_one_tier_on_the_profile_and_another_off_it_is_the_case_this_check_exists_for(
    tmp_path: Path,
) -> None:
    """The mixed case: upgrade one tier, forget the other.

    A repair briefly excluded `model` from the measured fields on a circularity worry — that
    the field evidencing adoption should not also be reported as drifted. It does not survive
    contact: a tier naming the model is by definition not drifted on it, so including the field
    costs that tier nothing, while excluding it silently dropped exactly this shape.
    """
    off_model = "  medium:\n    model: gpt-5.5\n    reasoning_effort: medium\n    fork_turns: none\n"
    repo = _seed_consumer(tmp_path, _PERFECT_HIGH + off_model)
    assert "critique_adapter_codex_profile_drift" in _drift_findings(repo)

    both_right = "  medium:\n    model: gpt-5.6-terra\n    reasoning_effort: medium\n    fork_turns: none\n"
    clean = _seed_consumer(tmp_path / "clean", _PERFECT_HIGH + both_right)
    clean_normalization = _run_inspect(clean)["agent_docs"]["normalization"]
    assert clean_normalization["critique_adapter"]["found"] is True
    assert "critique_adapter_codex_profile_drift" not in {
        finding["type"] for finding in clean_normalization["findings"]
    }


def test_a_prose_declaration_makes_a_wholly_off_profile_adapter_reportable(tmp_path: Path) -> None:
    """And the boundary beside it, which is a NON-claim rather than a gap left unsaid.

    With a prose declaration, a repo whose every tier left the profile is reported — the repo
    said it runs this profile and its adapter says otherwise. WITHOUT one, that same adapter is
    silent, because it reads identically to a repo that chose another model deliberately, and
    nothing else in this module covers that case either.
    """
    off = "  high-leverage:\n    model: gpt-5.5\n    reasoning_effort: medium\n    fork_turns: none\n"
    declared = _seed_consumer(
        tmp_path, off, agents_extra="\nReviewers run gpt-5.6-terra at medium effort.\n"
    )
    assert "critique_adapter_codex_profile_drift" in _drift_findings(declared)

    silent = _seed_consumer(tmp_path / "silent", off)
    silent_normalization = _run_inspect(silent)["agent_docs"]["normalization"]
    assert silent_normalization["critique_adapter"]["found"] is True, (
        "the adapter did not load; a green here would prove nothing about the predicate"
    )
    assert "critique_adapter_codex_profile_drift" not in {
        finding["type"] for finding in silent_normalization["findings"]
    }


def test_a_repo_that_renamed_its_tiers_is_measured_not_silently_green(tmp_path: Path) -> None:
    """Adoption iterates every tier, so measurement must too.

    Two rounds moved this line in opposite directions and both were wrong. Measuring the fixed
    `high-leverage`/`medium` pair told a one-tier repo it drifted on a tier it does not have;
    narrowing to that pair's truthiness then left a repo with a RENAMED tier evidencing
    adoption and measuring NOTHING — a permanent green for a repo the adoption predicate
    deliberately supports, which is this check's original defect reproduced inside its repair.
    (`critique_adapter_lib` only warns on an unknown tier name; it still loads it.)
    """
    repo = _seed_consumer(
        tmp_path,
        "  deep:\n    model: gpt-5.6-terra\n    reasoning_effort: high\n    fork_turns: all\n",
    )
    normalization = _run_inspect(repo)["agent_docs"]["normalization"]
    assert normalization["critique_adapter"]["found"] is True
    drift = next(
        finding
        for finding in normalization["findings"]
        if finding["type"] == "critique_adapter_codex_profile_drift"
    )
    assert "deep" in drift["message"]


def test_the_drift_message_names_the_fields_that_drifted_not_only_the_tier(tmp_path: Path) -> None:
    """An operator has to know WHICH way a tier drifted; the responses differ.

    The finding computed the offending fields and then reported only tier names, so
    "medium left the profile entirely" and "medium has `fork_turns: all`" read identically —
    and the first became newly reportable in this same slice.
    """
    off_model = "  medium:\n    model: gpt-5.5\n    reasoning_effort: medium\n    fork_turns: none\n"
    repo = _seed_consumer(tmp_path, _PERFECT_HIGH + off_model)
    drift = next(
        finding
        for finding in _run_inspect(repo)["agent_docs"]["normalization"]["findings"]
        if finding["type"] == "critique_adapter_codex_profile_drift"
    )
    assert "medium" in drift["message"]
    assert "model" in drift["message"] and "gpt-5.5" in drift["message"]
    # And a tier that is fine is not named at all.
    assert "high-leverage" not in drift["message"]
