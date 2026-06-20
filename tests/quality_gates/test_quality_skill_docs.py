from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_recommended_next_gates_ranking_declares_inference_layer_interpretation() -> None:
    # Advisory-interpretation contract rollout (#322): the `Recommended Next Gates`
    # ordering is an inference-layer ranking authored as prose, so the consuming
    # `quality` references declare it as such and carry the consumer-must-answer
    # requirement (both halves), while keeping verified gate results trusted.
    gate_classification = (
        ROOT / "skills" / "public" / "quality" / "references" / "gate-classification.md"
    ).read_text(encoding="utf-8")
    automation_promotion = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")

    assert "inference-layer" in gate_classification
    assert "advisory-interpretation-contract.md" in gate_classification
    assert "interpretation question" in gate_classification
    # Verified gate results stay trusted; only the ordering is re-interpreted.
    assert "stay trusted" in gate_classification

    # Paired consumer requirement enumerates recommendation rankings as a surface.
    assert "recommendation rankings" in automation_promotion
    assert "Recommended Next Gates" in automation_promotion


def test_quality_skill_carries_explicit_skill_ergonomics_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-ergonomics.md"
    ).read_text(encoding="utf-8")
    skill_quality = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-quality.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_skill_ergonomics.py" in dispatch
    assert "skill ergonomics" in dispatch
    assert "mode/option pressure" in dispatch
    assert "taste policing" in dispatch
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "model is smart" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "trigger overlap or undertrigger risk" in skill_quality
    assert "support-skill discoverability" in skill_quality
    assert "reference-aware contract checks" in skill_quality
    assert "overfit exact prose snippets" in skill_quality
    assert "repeated prose ritual" in skill_quality
    assert "growing lint suppressions" in skill_quality


def test_quality_skill_runs_usage_episode_validator_even_without_adapter() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")

    assert "resolve and run the Charness package-root validator `validate_usage_episodes.py`" in skill_text
    assert "and report `report_usage_episodes.py`" in skill_text
    assert "when `.agents/usage-episodes-adapter.yaml` exists" not in skill_text
    assert "`no_adapter`, `disabled`, and `no_records` are skipped warnings" in skill_text
    assert "not product-success proof or failures" in skill_text


def test_quality_skill_carries_lint_ignore_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    lint_ignore = (
        ROOT / "skills" / "public" / "quality" / "references" / "lint-ignore-discipline.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_lint_ignores.py" in dispatch
    assert "lint suppressions start to accumulate" in dispatch
    assert "lint suppression pressure" in dispatch
    assert "growing lint suppressions" in dispatch
    assert "retained policy-level ignores" in dispatch
    assert "concrete revisit conditions" in dispatch
    assert "inventory_lint_ignores.py" in lint_ignore
    assert "Treat these as prompts, not automatic failures." in lint_ignore
    assert "structural seam" in lint_ignore
    assert "source of policy truth" in lint_ignore
    assert "reviewed commit hash or review date" in lint_ignore
    assert "generated `latest.md` artifacts" in lint_ignore


def test_quality_skill_carries_entrypoint_docs_ergonomics_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "entrypoint-docs-ergonomics.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py" in dispatch
    assert "entrypoint-doc ergonomics" in dispatch
    assert "smart agent/operator can infer safely" in dispatch
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "Command Docs Drift Gate" in ergonomics
    assert ".agents/command-docs.yaml" in ergonomics
    assert "required help anchors" in ergonomics
    assert "doc-set dogma" in dispatch


def test_quality_skill_carries_cli_ergonomics_smells_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    cli_smells = (
        ROOT / "skills" / "public" / "quality" / "references" / "cli-ergonomics-smells.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_ergonomics.py" in dispatch
    assert "flat help-list" in dispatch
    assert "multiple archetype schema namespaces" in dispatch
    assert "Flat `--help` Lists" in cli_smells
    assert "Cross-Archetype Schema Leakage" in cli_smells
    assert "command-archetypes.json" in cli_smells


def test_quality_and_create_cli_carry_side_effect_probe_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    cli_probes = (
        ROOT / "skills" / "public" / "quality" / "references" / "installable-cli-probes.md"
    ).read_text(encoding="utf-8")
    create_cli = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(encoding="utf-8")
    quality_gates = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_side_effect_probes.py" in dispatch
    assert "option-looking positional rejection" in dispatch
    assert "mutating subcommand help probes" in cli_probes
    assert "side-effect seams" in cli_probes
    assert "option-looking" in create_cli
    assert "side-effect probe fixtures" in create_cli
    assert "dry-run or plan probes" in quality_gates
    assert "subprocess runners" in quality_gates


def test_quality_skill_carries_public_spec_layering_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    layering = (
        ROOT / "skills" / "public" / "quality" / "references" / "public-spec-layering.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_public_spec_quality.py" in dispatch
    assert "duplicated at the wrong layer" in dispatch
    assert "proof layering" in layering
    assert "reader-facing claims plus cheap local proof" in layering
    assert "what is now duplicated at the wrong layer" in layering
    assert "move_down" in layering
    assert "delete_or_merge" in layering
    assert "keep_if_integration_value" in layering


def test_quality_skill_prefers_structure_over_heuristic_chasing() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    lenses = (
        ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
    ).read_text(encoding="utf-8")
    automation = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    fresh_eye = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")

    assert "structural smell sensors" in skill_text
    assert "`Scope`, `Concept Risks`, `Current Gates`" in skill_text
    assert "Standing Test Economics" in skill_text
    assert "delete, merge, split ownership, extract a helper, or narrow the interface" in skill_text
    assert "Do not treat a passing length, duplicate, or pressure heuristic as the goal" in skill_text
    assert "routing default, not a veto against good deterministic enforcement" in dispatch
    assert "standing threshold gates such as coverage floors, runtime budgets" in dispatch
    assert "Pytest Economics" in dispatch
    assert "what structural simplification is missing" in lenses
    assert "canonical routing lives in `SKILL.md`" in lenses
    assert "do not over-apply this caution to standing threshold gates" in lenses
    assert "gate-last posture" in lenses
    assert "follow the canonical routing in `SKILL.md` first" in automation
    assert "tie-breaker, not a veto" in automation
    assert "false positives are low enough" in automation
    assert "smell sensors first" in automation
    assert "canonical fresh-eye review" in fresh_eye


def test_quality_skill_and_create_cli_carry_language_lint_defaults() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    create_cli_quality = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "For Python, default to `ruff check` as the standing lint path" in dispatch
    assert "choose exactly one type checker (`mypy` or `pyright`)" in dispatch
    assert "For JavaScript/TypeScript, default to `eslint`" in dispatch
    assert "`complexity` rule" in dispatch
    assert "Python CLI: `ruff check` with `C90` enabled" in create_cli_quality
    assert "JavaScript/TypeScript CLI: `eslint` with a standing `complexity` rule" in create_cli_quality


def test_quality_skill_carries_standing_gate_verbosity_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    verbosity = (
        ROOT / "skills" / "public" / "quality" / "references" / "standing-gate-verbosity.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py" in dispatch
    assert "$SKILL_DIR/scripts/inventory_standing_test_economics.py" in dispatch
    assert "$SKILL_DIR/scripts/inventory_structural_waste.py" in dispatch
    assert "file/process/startup cost" in dispatch
    assert "runner isolation/process mode" in dispatch
    assert "duplicate broad discovery/collection" in dispatch
    assert "broad scanner prefiltering" in dispatch
    assert "verbose-on-demand escape hatch" in dispatch
    assert "quiet failure output must still name the" in dispatch
    assert "top-N runtime hot spots" in dispatch
    assert "serial fallback" in dispatch
    assert "standing-gate-verbosity.md" in dispatch
    assert "Test-runner reporter" in verbosity
    assert "Orchestrator output mode" in verbosity
    assert "parallel runner is active" in verbosity
    assert "Slow Test Triage" in verbosity
    assert "runner-startup layer" in verbosity
    assert "test files * runner isolation * loader startup" in verbosity
    assert "pytest --durations" in verbosity
    assert "silent serial fallback" in verbosity
    assert "quiet defaults and failure detail" in verbosity.lower()
    assert "Failure detail" in verbosity
    assert "without forcing the operator to manually rediscover" in verbosity
    assert "after initial inventory and before broad recommendations" in skill_text
    assert "runtime_budget_profiles" in dispatch
    assert "CHARNESS_RUNTIME_PROFILE" in verbosity
    assert "local-linux-x86_64-8cpu" in verbosity
    assert "fixture-economics" in verbosity
    assert "parallel-critical-path" in verbosity
    assert "duplicated-proof" in verbosity


def test_quality_skill_carries_agent_production_runtime_lens_core_anchor() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    lenses = (
        ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
    ).read_text(encoding="utf-8")
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "skills" / "public" / "quality" / "references" / "agent-production-runtime.md"
    ).read_text(encoding="utf-8")
    behavior = (
        ROOT / "skills" / "public" / "quality" / "references" / "behavior-testing.md"
    ).read_text(encoding="utf-8")

    assert "agent production runtime risk" in skill_text
    assert "`references/agent-production-runtime.md`" in dispatch
    assert "production LLM or agent runtime" in runtime
    assert "Do not build an Anthropic-specific wrapper" in runtime
    assert "Cache And Cost Economics" in runtime
    assert "Overload And Fallback Policy" in runtime
    assert "Retry And Idempotency" in runtime
    assert "Streaming Stall Recovery" in runtime
    assert "Model Routing Economics" in runtime
    assert "provider roundtrip" in runtime
    assert "explicit non-applicability" in lenses
    assert "agent-production-runtime.md" in behavior


def test_quality_agent_runtime_lens_keeps_positive_runtime_triggers() -> None:
    runtime = (
        ROOT / "skills" / "public" / "quality" / "references" / "agent-production-runtime.md"
    ).read_text(encoding="utf-8")

    assert "a model/API client in a serving path" in runtime
    assert "model routing, fallback, or provider configuration" in runtime
    assert "streaming response endpoints or event processors" in runtime
    assert "tool/action queues driven by model output" in runtime
    assert "runtime telemetry for model calls, tokens, retries, costs, or fallbacks" in runtime


def test_quality_agent_runtime_lens_requires_runtime_evidence_for_docs() -> None:
    runtime = (
        ROOT / "skills" / "public" / "quality" / "references" / "agent-production-runtime.md"
    ).read_text(encoding="utf-8")
    runtime_words = " ".join(runtime.split())

    assert (
        "user-facing agent product docs only when paired with serving-path code, "
        "runtime configuration, telemetry, or concrete incident/runtime evidence"
        in runtime_words
    )
    assert "operator runbooks that describe an actual incident or runtime procedure" in runtime
    assert "without corroborating runtime evidence" in runtime
    assert "docs-only\nagent product descriptions" in runtime
    assert "not\nproduction runtime evidence until paired with a concrete runtime seam" in runtime


def test_quality_agent_runtime_lens_narrows_skill_experiment_mode() -> None:
    runtime = (
        ROOT / "skills" / "public" / "quality" / "references" / "agent-production-runtime.md"
    ).read_text(encoding="utf-8")

    assert "Use `skill-experiment` only when the\nruntime under review is itself a Charness skill" in runtime


def test_quality_agent_runtime_dispatch_mirrors_canonical_boundary() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    dispatch_words = " ".join(dispatch.split())

    assert "## Agent Production Runtime" in dispatch
    assert "mirrors the canonical boundary in `agent-production-runtime.md`" in dispatch
    assert "docs-only agent product descriptions" in dispatch_words
    assert (
        "product docs paired with serving-path code, runtime configuration, telemetry, "
        "or concrete incident/runtime evidence"
        in dispatch_words
    )
    assert "operator runbooks that describe an actual incident or runtime procedure" in dispatch
    assert "deterministic proof, behavior-proof recommendation" in dispatch
    assert "product-policy decision" in dispatch


def test_quality_behavior_testing_uses_cautilus_robustness_contract() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    behavior = (
        ROOT / "skills" / "public" / "quality" / "references" / "behavior-testing.md"
    ).read_text(encoding="utf-8")
    proposal = (
        ROOT / "skills" / "public" / "quality" / "references" / "proposal-flow.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/recommend_behavior_test.py" in dispatch
    assert "cautilus.robustness_request.v1" in behavior
    assert "cautilus.robustness_plan.v1" in behavior
    assert "cautilus.robustness_report.v1" in behavior
    assert "preserve_behavior" in behavior
    assert "relation status (`satisfied`, `violated`, `blocked`, `invalid`, or" in behavior
    assert "docs/contracts/robustness-evaluation.md" in behavior
    assert "Cautilus source repo" in behavior
    assert "They remain recommend-only unless the user supplies an" in proposal


def test_quality_skill_routes_spec_markdown_to_specdown_report() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    markdown_preview = (ROOT / "skills" / "support" / "markdown-preview" / "SKILL.md").read_text(encoding="utf-8")
    runtime_contract = (
        ROOT / "skills" / "support" / "markdown-preview" / "references" / "runtime-contract.md"
    ).read_text(encoding="utf-8")

    assert "ordinary Markdown uses the markdown preview seam" in dispatch
    assert "rendered Specdown report" in dispatch
    assert "not a rule that every Markdown review must use `glow`" in markdown_preview
    assert "Executable `*.spec.md` documents" in runtime_contract


def test_quality_skill_carries_source_guard_rollup_guidance() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    layering = (
        ROOT / "skills" / "public" / "quality" / "references" / "public-spec-layering.md"
    ).read_text(encoding="utf-8")

    assert "total source-guard rows" in dispatch
    assert "next" in dispatch and "action category" in dispatch
    assert "classify_source_guards" in layering
    assert "replace_with_contract_check" in layering
    assert "top specs by source-guard pressure" in layering


def test_quality_and_create_cli_carry_command_docs_drift_pattern() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    automation = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    create_cli = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(encoding="utf-8")
    create_cli_quality = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "command-docs drift gate" in dispatch
    assert "stable CLI command docs" in automation
    assert ".agents/command-docs.yaml" in adapter_contract
    assert "runner-specific section labels" in adapter_contract
    assert "Standing Test Economics" in adapter_contract
    assert "command-docs drift gate" in create_cli
    assert "repo-local command-docs contract" in create_cli_quality


def test_create_cli_and_create_skill_carry_authenticated_release_probe_pattern() -> None:
    install_update = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "install-update.md"
    ).read_text(encoding="utf-8")
    integration_seams = (
        ROOT / "skills" / "public" / "create-skill" / "references" / "integration-seams.md"
    ).read_text(encoding="utf-8")

    assert "Authenticated upstream release probe note" in install_update
    assert "authenticated provider path such as `gh api`" in install_update
    assert "`GH_TOKEN` or `GITHUB_TOKEN`" in install_update
    assert "structured `status`, `reason`, and `error` fields" in install_update
    assert "GitHub-Hosted Release Metadata" in integration_seams
    assert "use authenticated `gh api` first" in integration_seams
    assert "github-forbidden" in integration_seams


def test_create_cli_carries_external_capability_contract() -> None:
    create_cli = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(encoding="utf-8")
    external = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "external-capability-clis.md"
    ).read_text(encoding="utf-8")
    quality_gates = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "external capability boundary" in create_cli
    assert "host-side" in create_cli
    assert "redaction tests" in create_cli
    assert "missing_setup" in external
    assert "needs_credentials" in external
    assert "allowed_methods" in external
    assert "allowed_path_prefixes" in external
    assert "host-only executor boundary" in external
    assert "raw request bodies" in quality_gates
