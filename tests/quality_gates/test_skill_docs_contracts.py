from __future__ import annotations

import json

from .support import ROOT

IMPL_SKILL = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
PLUGIN_IMPL_SKILL_PATH = ROOT / "plugins" / "charness" / "skills" / "impl" / "SKILL.md"
# Prove is a conditional evidence formatter alongside the implementation workflow.
PROVE_SKILL = (ROOT / "skills" / "public" / "prove" / "SKILL.md").read_text(encoding="utf-8")
SETUP_SKILL = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(encoding="utf-8")
PLUGIN_SETUP_SKILL_PATH = ROOT / "plugins" / "charness" / "skills" / "setup" / "SKILL.md"
QUALITY_SKILL = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
CRITIQUE_SKILL = (ROOT / "skills" / "public" / "critique" / "SKILL.md").read_text(encoding="utf-8")
DEBUG_SKILL = (ROOT / "skills" / "public" / "debug" / "SKILL.md").read_text(encoding="utf-8")
BOOTSTRAP_SEAMS = (
    ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
).read_text(encoding="utf-8")
DEFAULT_SURFACES = (
    ROOT / "skills" / "public" / "setup" / "references" / "default-surfaces.md"
).read_text(encoding="utf-8")
DISPATCH = (
    ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
).read_text(encoding="utf-8")
MAINTAINER_LOCAL_ENFORCEMENT = (
    ROOT / "skills" / "public" / "quality" / "references" / "maintainer-local-enforcement.md"
).read_text(encoding="utf-8")
QUALITY_INDEX = (ROOT / "skills" / "public" / "quality" / "references" / "index.md").read_text(
    encoding="utf-8"
)
PROMPT_ASSET_POLICY = (
    ROOT / "skills" / "public" / "quality" / "references" / "prompt-asset-policy.md"
).read_text(encoding="utf-8")
PUBLIC_SKILL_VALIDATION = (ROOT / "docs" / "public-skill-validation.md").read_text(encoding="utf-8")


def test_setup_skill_bootstraps_probe_surface_guidance() -> None:
    skill_text = SETUP_SKILL
    bootstrap_seams = BOOTSTRAP_SEAMS
    probe_reference = (
        ROOT / "skills" / "public" / "setup" / "references" / "probe-surface.md"
    ).read_text(encoding="utf-8")

    assert "probe" in skill_text and "surfaces" in skill_text
    assert "installable CLI" in bootstrap_seams
    assert "binary healthcheck" in probe_reference
    assert "machine-readable command discovery" in probe_reference
    assert "local discoverability" in probe_reference


def test_setup_pins_live_spawn_first_execution_contract() -> None:
    """Setup emits the repo-level execution contract; Achieve stays planning-only."""
    setup = SETUP_SKILL.lower()

    assert "live host" in setup
    assert "spawn" in setup and "api" in setup
    assert "task run" in setup
    assert "isolation" in setup
    assert "may route" not in setup
    assert (
        PLUGIN_SETUP_SKILL_PATH.read_bytes()
        == (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_bytes()
    )


def test_setup_skill_describes_the_minimal_flat_wiki_profile() -> None:
    skill_text = SETUP_SKILL.lower()
    defaults = DEFAULT_SURFACES.lower()
    normalization = (
        (ROOT / "skills/public/setup/references/normalization-flow.md")
        .read_text(encoding="utf-8")
        .lower()
    )

    for text in (defaults, normalization):
        assert "docs/index.md" in text
        assert "flat" in text and "wiki" in text
        assert "explicit" in text and "approval" in text
        assert "quality" in text
    assert "default" in defaults
    assert "documentation index" in skill_text
    assert "approval" in skill_text
    assert "compact --execute" in skill_text
    assert "`quality` owns" in defaults


def test_quality_skill_consumes_setup_state_without_claiming_green() -> None:
    quality = QUALITY_SKILL.lower()

    assert "setup" in quality and "quality snapshot" in quality
    assert "configured" in quality and "plan-only" in quality
    assert "does not mean the repo is green" in quality
    assert "`quality` owns" in quality
    assert "adapter" in quality and "ratchets" in quality
    assert "staged/related-file" in quality
    assert "without approval" in quality


def test_setup_default_surfaces_keep_optional_workflows_out_of_the_core() -> None:
    default_surfaces = DEFAULT_SURFACES

    assert "## Conditional surfaces" in default_surfaces
    assert "## Ownership boundaries" in default_surfaces
    assert "`quality` owns exact gates" in default_surfaces
    assert "## Early Quality Baseline" not in default_surfaces


def test_setup_does_not_duplicate_artifact_commit_policy() -> None:
    skill_text = SETUP_SKILL.lower()
    bootstrap_seams = BOOTSTRAP_SEAMS.lower()
    default_surfaces = DEFAULT_SURFACES.lower()
    normalization_flow = (
        (ROOT / "skills/public/setup/references/normalization-flow.md")
        .read_text(encoding="utf-8")
        .lower()
    )

    assert "bootstrap-seams.md" in skill_text
    assert "bootstrap-seams.md" in skill_text
    assert "charness-artifacts/" in default_surfaces
    assert "repo state" not in bootstrap_seams
    assert "commit targets" not in bootstrap_seams
    assert "commit targets" not in normalization_flow


def test_setup_does_not_duplicate_announcement_or_review_contracts() -> None:
    skill_text = SETUP_SKILL.lower()
    bootstrap_seams = BOOTSTRAP_SEAMS.lower()
    default_surfaces = DEFAULT_SURFACES.lower()

    assert "bootstrap-seams.md" in skill_text
    assert "announcement" not in bootstrap_seams
    assert "issue linkage" not in default_surfaces
    assert "Subagent Delegation" not in default_surfaces


def test_hitl_skill_carries_review_chunk_and_state_recording_rules() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")
    chunk_contract = (
        ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md"
    ).read_text(encoding="utf-8")
    state_model = (ROOT / "skills" / "public" / "hitl" / "references" / "state-model.md").read_text(
        encoding="utf-8"
    )
    report_mode = (ROOT / "skills" / "public" / "hitl" / "references" / "report-mode.md").read_text(
        encoding="utf-8"
    )
    adapter_contract = (
        ROOT / "skills" / "public" / "hitl" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")

    assert "Apply Phase" in skill_text
    assert "Never edit the target file mid-chunk" in skill_text
    assert "Do not edit the target file while the review loop is in progress" in skill_text
    assert "display-only pseudo-tags" in skill_text
    assert "explain dense generated tables" in skill_text
    assert "Do not persist suggested decisions as human approval" in skill_text
    assert "Accepted Working Text" in skill_text
    assert "last_presented_chunk_id" in skill_text
    assert "active_rules_applied" in skill_text
    assert "target_cursor_checked" in skill_text
    assert (
        "sync live runtime state into `<repo-root>/charness-artifacts/hitl/latest.md`" in skill_text
    )
    assert "durable artifact freshness check" in skill_text
    assert "check_review_state.py" in skill_text
    assert "Active Rules Applied" in skill_text
    assert "Target/Cursor\nChecked" in skill_text
    assert "applied_rewrite_review_status" in skill_text
    assert "rewritten chunk excerpt" in skill_text
    assert "working text or session" in skill_text
    assert "accept-or-revise" in skill_text
    assert "Full Target Review" in skill_text
    assert "full_target_review" in skill_text
    assert "whole-target acceptance" in skill_text
    assert "Tables and matrices are not the primary review surface" in report_mode
    assert "suggestion_display_only: true" in report_mode
    assert "explicit apply instruction" in adapter_contract
    assert "accepted-chunk-or-final-apply-boundary" in adapter_contract
    assert "Runtime-To-Artifact Sync" in adapter_contract
    assert "runtime changed after the durable\nartifact sync" in adapter_contract
    assert "accepted-rules metadata" in adapter_contract
    assert "approval state" in adapter_contract
    assert "explicit next chunk to present" in adapter_contract
    assert "<bash>" in chunk_contract
    assert "not instructions to\nedit the target document" in chunk_contract
    assert "Minimum applied-rewrite surface" in chunk_contract
    assert "verification results only as secondary information" in chunk_contract
    assert "Active Pre-Edit Constraints" in (
        ROOT / "skills" / "public" / "hitl" / "references" / "rule-propagation.md"
    ).read_text(encoding="utf-8")
    assert "Accepted working text" in state_model
    assert "accepted_rules" in state_model
    assert "active_rules_applied" in state_model
    assert "target_cursor_checked" in state_model
    assert "target_cursor_check_result" in state_model
    assert "chunk id, queue item, line" in state_model
    assert "applied_rewrite_review_status" in state_model
    assert "pending_rewrite_chunk_id" in state_model
    assert "Only after that judgment is recorded" in state_model
    assert "full_target_review_status" in state_model
    assert "needs_another_pass" in state_model
    assert "persist accepted decisions before advancing the cursor" in state_model
    assert "HITL runtime sync metadata block" in state_model
    assert "applied rewrite is\nstill pending human judgment" in state_model


def test_prove_skill_keeps_claim_proof_and_owner_routing_explicit() -> None:
    skill_text = PROVE_SKILL
    normalized_skill = " ".join(skill_text.split())
    dispatch = DISPATCH
    verification_ladder = (
        ROOT / "skills" / "public" / "prove" / "references" / "verification-ladder.md"
    ).read_text(encoding="utf-8")

    assert (
        "Use Prove only when the user, current contract, or boundary owner explicitly selects it."
        in normalized_skill
    )
    assert "ordinary reversible implementation" in skill_text
    assert "Identify the claim." in skill_text
    assert "narrowest strongest evidence." in skill_text
    assert "actual truth surfaces." in skill_text
    assert "evidence and non-claims." in skill_text
    for owner in ("quality", "hotl", "issue", "release", "critique"):
        assert f"`{owner}`" in skill_text
    assert "hidden availability" in verification_ladder
    assert "Browser-Facing Output" in verification_ladder
    assert "metadata/model judgment" in verification_ladder
    assert "operator reading test" in dispatch
    assert "automatic" not in skill_text
    assert "universal" not in skill_text


def test_debug_and_quality_carry_async_and_hidden_network_field_lessons() -> None:
    debug_text = (ROOT / "skills" / "public" / "debug" / "SKILL.md").read_text(encoding="utf-8")
    maintainer_local = MAINTAINER_LOCAL_ENFORCEMENT

    assert "pre-worker\n     acknowledgement" in debug_text
    assert "worker execution" in debug_text
    assert "post-worker side effects" in debug_text
    assert "earliest component that can produce observable status" in debug_text
    assert "external-repo fetch" in maintainer_local
    assert "explicit refresh,\n> update, or release action" in maintainer_local


def test_critique_and_debug_share_the_evidence_led_adversarial_route() -> None:
    critique_reference = (
        ROOT / "skills" / "public" / "critique" / "references" / "adversarial-evidence-review.md"
    )
    pattern_reference = ROOT / "skills" / "public" / "debug" / "references" / "pattern-ladder.md"
    plugin_root = ROOT / "plugins" / "charness" / "skills"

    assert "## Evidence-Led Mode" in CRITIQUE_SKILL
    assert "Do not treat the counterweight pass as adversarial evidence" in CRITIQUE_SKILL
    assert "## Reported-Finding Mode" in DEBUG_SKILL
    assert "## Pattern Ladder" in DEBUG_SKILL
    assert "`reproduced`, `disconfirmed`, `unproven`, or `not-applicable`" in DEBUG_SKILL
    assert critique_reference.is_file()
    assert pattern_reference.is_file()
    assert "Finding: <stable id>" in critique_reference.read_text(encoding="utf-8")
    assert "Evidence Digest: sha256:<64 lowercase hex>" in critique_reference.read_text(
        encoding="utf-8"
    )
    assert "receipt sha256: <64 lowercase hex or `none`>" in critique_reference.read_text(
        encoding="utf-8"
    )
    assert "charness.adversarial-evidence.receipt.v1" in critique_reference.read_text(
        encoding="utf-8"
    )
    assert "Report Source SHA256" in critique_reference.read_text(encoding="utf-8")
    assert "- Finding: <stable id> | source:" in critique_reference.read_text(encoding="utf-8")
    assert (
        "Level: observed failure | local pattern | interface sibling | pattern of patterns"
        in pattern_reference.read_text(encoding="utf-8")
    )

    assert (plugin_root / "critique" / "SKILL.md").read_bytes() == CRITIQUE_SKILL.encode()
    assert (plugin_root / "debug" / "SKILL.md").read_bytes() == DEBUG_SKILL.encode()
    assert (
        plugin_root / "critique" / "references" / "adversarial-evidence-review.md"
    ).read_bytes() == critique_reference.read_bytes()
    assert (
        plugin_root / "debug" / "references" / "pattern-ladder.md"
    ).read_bytes() == pattern_reference.read_bytes()
    assert (
        (
            ROOT
            / "skills"
            / "public"
            / "debug"
            / ".."
            / "critique"
            / "references"
            / "adversarial-evidence-review.md"
        )
        .resolve()
        .is_file()
    )
    assert (
        (
            plugin_root
            / "debug"
            / ".."
            / "critique"
            / "references"
            / "adversarial-evidence-review.md"
        )
        .resolve()
        .is_file()
    )
    assert "Use `critique` first" in critique_reference.read_text(encoding="utf-8")


def test_development_doc_carries_mutation_phase_barrier_rule() -> None:
    development = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")

    assert "## Mutation phase barriers" in development
    assert "mutate" in development
    assert "sync generated surfaces" in development
    assert "verify" in development
    assert "publish" in development
    assert "Read-only inventory may run in parallel" in development


def test_public_skill_validation_doc_keeps_critique_and_on_demand_boundary_visible() -> None:
    validation_doc = PUBLIC_SKILL_VALIDATION

    assert "`critique`" in validation_doc
    assert "on-demand through an explicit bounded human review" in validation_doc
    assert "consumer-owned\nevaluator" in validation_doc


def test_control_plane_documents_authenticated_release_probe_contract() -> None:
    control_plane = (ROOT / "docs" / "control-plane.md").read_text(encoding="utf-8")

    assert "authenticated `gh api`" in control_plane
    assert "`GH_TOKEN` or `GITHUB_TOKEN`" in control_plane
    assert "public unauthenticated HTTP" in control_plane
    assert "`status`, `reason`, and" in control_plane
    assert "github-forbidden" in control_plane


def test_quality_skill_carries_blind_spot_policy_and_critique_refs() -> None:
    index = QUALITY_INDEX
    dispatch = DISPATCH
    adapter_contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    floor_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "coverage-floor-policy.md"
    ).read_text(encoding="utf-8")
    fresh_eye = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")
    prompt_policy = PROMPT_ASSET_POLICY

    assert "quality-lenses.md" in index
    assert "prompt/content bulk" in dispatch
    assert "progressive-disclosure map" in index
    assert "coverage_floor_policy" in adapter_contract
    assert "spec_pytest_reference_format" in adapter_contract
    assert "public_spec_section_exemptions" in adapter_contract
    assert "public_spec_implementation_ref_density_floor" in adapter_contract
    assert "public_spec_pointer_proof_markers" in adapter_contract
    assert "prompt_asset_policy" in adapter_contract
    assert "gate_script_pattern" in floor_policy
    assert "warn band" in floor_policy
    assert "canonical fresh-eye review" in fresh_eye
    assert "source_globs" in prompt_policy
    assert "prompt/content bulk" in prompt_policy
    assert "find_inline_prompt_bulk.py" in prompt_policy


def test_quality_skill_carries_code_reduction_and_ratio_patterns() -> None:
    skill_text = QUALITY_SKILL
    dispatch = DISPATCH
    automation = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    economics = (
        ROOT / "skills" / "public" / "quality" / "references" / "executable-spec-economics.md"
    ).read_text(encoding="utf-8")
    lenses = (
        ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
    ).read_text(encoding="utf-8")
    enforcement = MAINTAINER_LOCAL_ENFORCEMENT

    assert "narrow an interface" in skill_text
    assert "bounded test-ratio posture" in dispatch
    assert "stale gate wiring" in enforcement
    assert "shrinking production\nsurface" in automation
    assert "changed-file router" in economics
    assert "bounded test-ratio posture" in lenses
    assert "adapter-driven local enforcement as a positive pattern" in lenses
    assert "strong positive pattern" in enforcement


def test_quality_skill_keeps_testability_tool_detail_in_reference() -> None:
    skill_text = QUALITY_SKILL
    index = QUALITY_INDEX
    reference_text = (
        ROOT / "skills" / "public" / "quality" / "references" / "testability-and-selection.md"
    ).read_text(encoding="utf-8")
    dogfood = json.loads((ROOT / "docs" / "public-skill-dogfood.json").read_text(encoding="utf-8"))

    assert "references/testability-and-selection.md" in index
    assert "testability, selection, and duplicated proof" in index
    assert (
        "Do not claim that deterministic affected-test selection is always possible"
        in reference_text
    )
    assert "cheap deterministic\ncandidate subset" in reference_text
    assert "pytest-testmon" in reference_text
    assert "Jest or Vitest" in reference_text
    assert "Pants/Bazel-style" in reference_text
    assert "manually maintained source-to-test dependency map" in reference_text
    quality_case = next(case for case in dogfood["cases"] if case["skill_id"] == "quality")
    assert any("consumer prompt" in item for item in quality_case["acceptance_evidence"])
    for tool_name in ("pytest-testmon", "Jest", "Vitest", "Pants", "Bazel"):
        assert tool_name not in skill_text


def test_prove_skill_carries_truth_surface_sync_guardrail() -> None:
    skill_text = PROVE_SKILL
    adapter_contract = (
        ROOT / "skills" / "public" / "impl" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    assert "Sync actual truth surfaces." in skill_text
    assert "source-of-truth docs" in skill_text
    assert "truth_surfaces" in adapter_contract
    assert "README.md" in adapter_contract


def test_impl_skill_defaults_to_autonomous_continuation() -> None:
    skill_text = IMPL_SKILL
    normalized_skill = " ".join(skill_text.split())
    assert "autonomous continuation" in skill_text.lower()
    assert "continuation" in skill_text and "checkpoints" in skill_text
    assert "irreversible" in skill_text and "external side effect" in skill_text
    assert "focused tests for the changed module or user flow" in skill_text
    assert (
        "Use `prove` when the user or the boundary explicitly requires its evidence format"
        in normalized_skill
    )


def test_impl_keeps_optional_proof_conditional() -> None:
    skill_text = IMPL_SKILL
    assert "No separate session-start hook" in skill_text
    assert "risk-interrupt planner" in skill_text
    assert "Additional proof is conditional" in skill_text
    assert "does not require a fresh-eye review" in skill_text
    assert "changed-line proof" in skill_text


def test_impl_source_and_materialized_plugin_export_are_byte_identical() -> None:
    assert (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_bytes() == (
        PLUGIN_IMPL_SKILL_PATH.read_bytes()
    )


def test_validate_integrations_rejects_unsafe_agent_browser_check_commands() -> None:
    from tools.validate_integrations import (
        ValidationError,
        validate_agent_browser_check_commands,
    )

    manifest = {
        "tool_id": "agent-browser",
        "checks": {
            "detect": {"commands": ["agent-browser --version"]},
            "healthcheck": {"commands": ["timeout 5 agent-browser open https://example.com"]},
        },
    }
    try:
        validate_agent_browser_check_commands(
            manifest, ROOT / "integrations" / "tools" / "agent-browser.json"
        )
    except ValidationError as exc:
        assert "unsafe agent-browser probe" in str(exc)
        assert "timeout 5 agent-browser open https://example.com" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected unsafe agent-browser check command rejection")


def test_validate_integrations_rejects_unsafe_support_readiness_commands() -> None:
    from tools.validate_integrations import (
        ValidationError,
        validate_agent_browser_readiness_commands,
    )

    capability = {
        "capability_id": "demo",
        "readiness_checks": [
            {
                "check_id": "demo-browser-ready",
                "summary": "Demo browser runtime is ready.",
                "commands": ["bash -lc 'agent-browser open https://example.com'"],
            }
        ],
    }
    try:
        validate_agent_browser_readiness_commands(
            capability, ROOT / "skills" / "support" / "demo" / "capability.json"
        )
    except ValidationError as exc:
        assert "unsafe agent-browser probe" in str(exc)
        assert "readiness_checks[0].commands[0]" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected unsafe support readiness command rejection")
