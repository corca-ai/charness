from __future__ import annotations

import json

from .support import ROOT


def test_setup_skill_bootstraps_probe_surface_guidance() -> None:
    skill_text = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    bootstrap_seams = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8")
    probe_reference = (
        ROOT / "skills" / "public" / "setup" / "references" / "probe-surface.md"
    ).read_text(encoding="utf-8")

    assert "probe surfaces" in skill_text
    assert "installable CLI" in bootstrap_seams
    assert "binary healthcheck" in probe_reference
    assert "machine-readable command discovery" in probe_reference
    assert "local discoverability" in probe_reference


def test_setup_default_surfaces_carry_early_quality_baseline() -> None:
    default_surfaces = (
        ROOT / "skills" / "public" / "setup" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8")

    assert "## Early Quality Baseline" in default_surfaces
    assert "Python: `ruff check` with `E`, `F`, `I`, and `C90`" in default_surfaces
    assert "JavaScript/TypeScript: `eslint`, a standing `complexity` rule" in default_surfaces
    assert "let `quality` own the exact gate wiring" in default_surfaces
    assert "ratcheting" in default_surfaces


def test_setup_agent_docs_carry_bounded_subagent_delegation_rule() -> None:
    skill_text = (ROOT / "skills" / "public" / "setup" / "SKILL.md").read_text(
        encoding="utf-8"
    ).lower()
    agent_docs = (
        ROOT / "skills" / "public" / "setup" / "references" / "agent-docs-policy.md"
    ).read_text(encoding="utf-8").lower()
    bootstrap_seams = (
        ROOT / "skills" / "public" / "setup" / "references" / "bootstrap-seams.md"
    ).read_text(encoding="utf-8").lower()
    default_surfaces = (
        ROOT / "skills" / "public" / "setup" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8").lower()

    assert "already delegated" in skill_text
    assert "second user message" in bootstrap_seams
    assert "same-agent pass" in bootstrap_seams
    assert "## subagent delegation" in agent_docs
    assert "explicit user delegation request" in agent_docs
    assert "already delegated" in agent_docs
    assert "by this repo contract" in agent_docs
    assert "second user message" in agent_docs
    assert "same-agent pass" in agent_docs
    assert "## subagent delegation" in default_surfaces
    assert "explicit user delegation request" in default_surfaces
    assert "already delegated by the repo" in default_surfaces
    assert "same-agent pass" in default_surfaces


def test_setup_docs_carry_charness_artifact_commit_policy() -> None:
    skill_text = (ROOT / "skills/public/setup/SKILL.md").read_text(encoding="utf-8").lower()
    agent_docs = (ROOT / "skills/public/setup/references/agent-docs-policy.md").read_text(encoding="utf-8").lower()
    bootstrap_seams = (ROOT / "skills/public/setup/references/bootstrap-seams.md").read_text(encoding="utf-8").lower()
    default_surfaces = (ROOT / "skills/public/setup/references/default-surfaces.md").read_text(encoding="utf-8").lower()
    normalization_flow = (ROOT / "skills/public/setup/references/normalization-flow.md").read_text(encoding="utf-8").lower()

    assert "bootstrap-seams.md" in skill_text
    for text in (agent_docs, bootstrap_seams, default_surfaces, normalization_flow):
        assert "charness-artifacts/" in text
        assert "repo state" in text
        assert "canonical content" in text

    assert "commit targets" in bootstrap_seams
    assert "commit targets" in agent_docs
    assert "current-pointer helpers should no-op" in agent_docs
    assert "commit targets" in default_surfaces


def test_setup_docs_seed_announcement_ready_commit_bodies() -> None:
    skill_text = (ROOT / "skills/public/setup/SKILL.md").read_text(encoding="utf-8").lower()
    agent_docs = (ROOT / "skills/public/setup/references/agent-docs-policy.md").read_text(encoding="utf-8").lower()
    bootstrap_seams = (ROOT / "skills/public/setup/references/bootstrap-seams.md").read_text(encoding="utf-8").lower()
    default_surfaces = (ROOT / "skills/public/setup/references/default-surfaces.md").read_text(encoding="utf-8").lower()

    assert "bootstrap-seams.md" in skill_text
    for text in (agent_docs, bootstrap_seams, default_surfaces):
        assert "announcement" in text
        assert "commit" in text
        assert "issue linkage" in text
        assert "human-visible value" in text
        assert "verification" in text
        assert "operator/apply notes" in text

    assert "close keywords" in agent_docs
    assert "merge commits" in default_surfaces


def test_hitl_skill_carries_review_chunk_and_state_recording_rules() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")
    chunk_contract = (
        ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md"
    ).read_text(encoding="utf-8")
    state_model = (
        ROOT / "skills" / "public" / "hitl" / "references" / "state-model.md"
    ).read_text(encoding="utf-8")
    report_mode = (
        ROOT / "skills" / "public" / "hitl" / "references" / "report-mode.md"
    ).read_text(encoding="utf-8")
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
    assert "sync live runtime state into `charness-artifacts/hitl/latest.md`" in skill_text
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


def test_impl_skill_routes_validation_and_browser_proof_explicitly() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    verification_ladder = (
        ROOT / "skills" / "public" / "impl" / "references" / "verification-ladder.md"
    ).read_text(encoding="utf-8")
    find_skills = (ROOT / "skills" / "public" / "find-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "operator reading" in skill_text
    assert "--recommendation-role validation --next-skill-id" in find_skills
    assert "say explicitly that it did not run" in skill_text
    assert "code/fixture" in skill_text
    assert "Browser-Facing Output" in verification_ladder
    assert "same-agent/manual review" in verification_ladder
    assert "operator reading test" in dispatch
    assert "before downgrading to HITL" in dispatch


def test_debug_and_quality_carry_async_and_hidden_network_field_lessons() -> None:
    debug_text = (
        ROOT / "skills" / "public" / "debug" / "SKILL.md"
    ).read_text(encoding="utf-8")
    maintainer_local = (
        ROOT
        / "skills"
        / "public"
        / "quality"
        / "references"
        / "maintainer-local-enforcement.md"
    ).read_text(encoding="utf-8")

    assert "pre-worker\n     acknowledgement" in debug_text
    assert "worker execution" in debug_text
    assert "post-worker side effects" in debug_text
    assert "earliest component that can produce observable status" in debug_text
    assert "external-repo fetch" in maintainer_local
    assert "explicit refresh,\n> update, or release action" in maintainer_local


def test_development_doc_carries_mutation_phase_barrier_rule() -> None:
    development = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")

    assert "## Mutation Phase Barriers" in development
    assert "mutate" in development
    assert "sync generated surfaces" in development
    assert "verify" in development
    assert "publish" in development
    assert "parallelism is only safe for read-only inventory" in development


def test_public_skill_validation_doc_keeps_critique_and_on_demand_boundary_visible() -> None:
    validation_doc = (ROOT / "docs" / "public-skill-validation.md").read_text(encoding="utf-8")

    assert "`critique`" in validation_doc
    assert "on-demand proof through" in validation_doc
    assert "underlying evaluator state or storage layer" in validation_doc


def test_control_plane_documents_authenticated_release_probe_contract() -> None:
    control_plane = (ROOT / "docs" / "control-plane.md").read_text(encoding="utf-8")

    assert "authenticated `gh api`" in control_plane
    assert "`GH_TOKEN` or `GITHUB_TOKEN`" in control_plane
    assert "public unauthenticated HTTP" in control_plane
    assert "`status`, `reason`, and" in control_plane
    assert "github-forbidden" in control_plane


def test_quality_skill_carries_blind_spot_policy_and_critique_refs() -> None:
    index = (
        ROOT / "skills" / "public" / "quality" / "references" / "index.md"
    ).read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    floor_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "coverage-floor-policy.md"
    ).read_text(encoding="utf-8")
    fresh_eye = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")
    prompt_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "prompt-asset-policy.md"
    ).read_text(encoding="utf-8")

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
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    automation = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    economics = (
        ROOT / "skills" / "public" / "quality" / "references" / "executable-spec-economics.md"
    ).read_text(encoding="utf-8")
    lenses = (
        ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
    ).read_text(encoding="utf-8")
    enforcement = (
        ROOT / "skills" / "public" / "quality" / "references" / "maintainer-local-enforcement.md"
    ).read_text(encoding="utf-8")

    assert "narrow an interface" in skill_text
    assert "bounded test-ratio posture" in dispatch
    assert "stale gate wiring" in enforcement
    assert "shrinking production\nsurface" in automation
    assert "changed-file router" in economics
    assert "bounded test-ratio posture" in lenses
    assert "adapter-driven local enforcement as a positive pattern" in lenses
    assert "strong positive pattern" in enforcement


def test_quality_skill_keeps_testability_tool_detail_in_reference() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    index = (
        ROOT / "skills" / "public" / "quality" / "references" / "index.md"
    ).read_text(encoding="utf-8")
    reference_text = (
        ROOT / "skills" / "public" / "quality" / "references" / "testability-and-selection.md"
    ).read_text(encoding="utf-8")
    dogfood = (ROOT / "docs" / "public-skill-dogfood.json").read_text(encoding="utf-8")

    assert "references/testability-and-selection.md" in index
    assert "testability, selection, and duplicated proof" in index
    assert "Do not claim that deterministic affected-test selection is always possible" in reference_text
    assert "cheap deterministic\ncandidate subset" in reference_text
    assert "pytest-testmon" in reference_text
    assert "Jest or Vitest" in reference_text
    assert "Pants/Bazel-style" in reference_text
    assert "manually maintained source-to-test dependency map" in reference_text
    assert "The quality core now treats testability and affected-test selection" in dogfood
    for tool_name in ("pytest-testmon", "Jest", "Vitest", "Pants", "Bazel"):
        assert tool_name not in skill_text


def test_impl_skill_carries_truth_surface_sync_guardrail() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    adapter_contract = (ROOT / "skills" / "public" / "impl" / "references" / "adapter-contract.md").read_text(encoding="utf-8")
    assert "Sync truth surfaces and re-read the contract before closeout." in skill_text
    assert "Truth Surface Sync" in skill_text
    assert "truth_surfaces" in adapter_contract
    assert "README.md" in adapter_contract


def test_impl_skill_defaults_to_autonomous_continuation() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    assert "autonomous continuation" in skill_text.lower()
    assert "continuation" in skill_text and "checkpoints" in skill_text
    assert "irreversible" in skill_text and "external side effect" in skill_text
    assert "next locally decidable slice" in skill_text
    assert "check_auto_trigger.py" in skill_text


def test_current_cautilus_guidance_uses_eval_surface() -> None:
    impl_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    public_skill_validation = (ROOT / "docs" / "public-skill-validation.md").read_text(encoding="utf-8")
    adapter_text = (ROOT / ".agents" / "cautilus-adapter.yaml").read_text(encoding="utf-8")

    assert "cautilus evaluate fixture --repo-root . --adapter-name <repo-owned-adapter>" in impl_text
    assert "cautilus evaluate observation --input <observed.json>" in impl_text
    assert "cautilus evaluate fixture --repo-root . --adapter-name <repo-owned-adapter>" in public_skill_validation
    assert "eval_test_command_templates:" in adapter_text
    assert "evaluation_input_default: evals/cautilus/whole-repo-routing.fixture.json" in adapter_text
    assert "--codex-auth-mode inherit" in adapter_text
    assert "cautilus instruction-surface test --repo-root ." not in impl_text
    assert "cautilus instruction-surface test --repo-root ." not in public_skill_validation
    assert "cautilus eval test --repo-root ." not in impl_text
    assert "cautilus eval test --repo-root ." not in public_skill_validation


def test_cautilus_guidance_does_not_use_generic_review_triggers() -> None:
    impl_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    prompt_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "prompt-asset-policy.md"
    ).read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "integrations" / "tools" / "cautilus.json").read_text(encoding="utf-8"))

    assert "generic" in impl_text
    assert "review or closeout wording must not silently launch Cautilus" in impl_text
    assert "Generic review, closeout, or \"run quality\" wording" in dispatch
    assert "generic review, closeout, or quality-gate wording" in prompt_policy
    assert "not a Cautilus execution" in prompt_policy
    assert "prompt behavior regression" in manifest["intent_triggers"]
    assert "baseline compare" in manifest["intent_triggers"]
    assert not {"review", "closeout", "검증", "리뷰"}.intersection(manifest["intent_triggers"])


def test_validate_integrations_rejects_generic_cautilus_triggers() -> None:
    from scripts.validate_integrations import (
        ValidationError,
        validate_cautilus_trigger_specificity,
    )

    manifest = {
        "tool_id": "cautilus",
        "intent_triggers": ["quality review", "prompt behavior regression", "검토"],
    }
    try:
        validate_cautilus_trigger_specificity(manifest, ROOT / "integrations" / "tools" / "cautilus.json")
    except ValidationError as exc:
        assert "generic review/closeout terms" in str(exc)
        assert "quality review" in str(exc)
        assert "검토" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected generic cautilus trigger rejection")


def test_validate_integrations_rejects_unsafe_agent_browser_check_commands() -> None:
    from scripts.validate_integrations import (
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
        validate_agent_browser_check_commands(manifest, ROOT / "integrations" / "tools" / "agent-browser.json")
    except ValidationError as exc:
        assert "unsafe agent-browser probe" in str(exc)
        assert "timeout 5 agent-browser open https://example.com" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected unsafe agent-browser check command rejection")


def test_validate_integrations_rejects_unsafe_support_readiness_commands() -> None:
    from scripts.validate_integrations import (
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
        validate_agent_browser_readiness_commands(capability, ROOT / "skills" / "support" / "demo" / "capability.json")
    except ValidationError as exc:
        assert "unsafe agent-browser probe" in str(exc)
        assert "readiness_checks[0].commands[0]" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected unsafe support readiness command rejection")
