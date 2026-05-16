from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_quality_skill_carries_explicit_skill_ergonomics_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-ergonomics.md"
    ).read_text(encoding="utf-8")
    skill_quality = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-quality.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_skill_ergonomics.py" in skill_text
    assert "skill ergonomics" in skill_text
    assert "mode/option pressure" in skill_text
    assert "taste policing" in skill_text
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


def test_quality_skill_carries_lint_ignore_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    lint_ignore = (
        ROOT / "skills" / "public" / "quality" / "references" / "lint-ignore-discipline.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_lint_ignores.py" in skill_text
    assert "lint suppressions start to accumulate" in skill_text
    assert "lint suppression pressure" in skill_text
    assert "growing lint suppressions" in skill_text
    assert "retained policy-level ignores" in skill_text
    assert "concrete revisit conditions" in skill_text
    assert "inventory_lint_ignores.py" in lint_ignore
    assert "Treat these as prompts, not automatic failures." in lint_ignore
    assert "structural seam" in lint_ignore
    assert "source of policy truth" in lint_ignore
    assert "reviewed commit hash or review date" in lint_ignore
    assert "generated `latest.md` artifacts" in lint_ignore


def test_quality_skill_carries_entrypoint_docs_ergonomics_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "entrypoint-docs-ergonomics.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py" in skill_text
    assert "entrypoint-doc ergonomics" in skill_text
    assert "smart agent/operator can infer safely" in skill_text
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "Command Docs Drift Gate" in ergonomics
    assert ".agents/command-docs.yaml" in ergonomics
    assert "required help anchors" in ergonomics
    assert "doc-set dogma" in skill_text


def test_quality_skill_carries_cli_ergonomics_smells_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    cli_smells = (
        ROOT / "skills" / "public" / "quality" / "references" / "cli-ergonomics-smells.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_ergonomics.py" in skill_text
    assert "flat help-list" in skill_text
    assert "multiple archetype schema namespaces" in skill_text
    assert "Flat `--help` Lists" in cli_smells
    assert "Cross-Archetype Schema Leakage" in cli_smells
    assert "command-archetypes.json" in cli_smells


def test_quality_and_create_cli_carry_side_effect_probe_lens() -> None:
    quality_skill = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    cli_probes = (
        ROOT / "skills" / "public" / "quality" / "references" / "installable-cli-probes.md"
    ).read_text(encoding="utf-8")
    create_cli = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(encoding="utf-8")
    quality_gates = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_side_effect_probes.py" in quality_skill
    assert "option-looking positional rejection" in quality_skill
    assert "mutating subcommand help probes" in cli_probes
    assert "side-effect seams" in cli_probes
    assert "option-looking" in create_cli
    assert "side-effect probe fixtures" in create_cli
    assert "dry-run or plan probes" in quality_gates
    assert "subprocess runners" in quality_gates


def test_quality_skill_carries_public_spec_layering_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    layering = (
        ROOT / "skills" / "public" / "quality" / "references" / "public-spec-layering.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_public_spec_quality.py" in skill_text
    assert "duplicated at the wrong layer" in skill_text
    assert "proof layering" in layering
    assert "reader-facing claims plus cheap local proof" in layering
    assert "what is now duplicated at the wrong layer" in layering
    assert "move_down" in layering
    assert "delete_or_merge" in layering
    assert "keep_if_integration_value" in layering


def test_quality_skill_prefers_structure_over_heuristic_chasing() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
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
    assert "routing default, not a veto against good deterministic enforcement" in skill_text
    assert "standing threshold gates such as coverage floors, runtime budgets" in skill_text
    assert "Pytest Economics" in skill_text
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
    quality_skill = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    create_cli_quality = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
    ).read_text(encoding="utf-8")

    assert "For Python, default to `ruff check` as the standing lint path" in quality_skill
    assert "choose exactly one type checker (`mypy` or `pyright`)" in quality_skill
    assert "For JavaScript/TypeScript, default to `eslint`" in quality_skill
    assert "`complexity` rule" in quality_skill
    assert "Python CLI: `ruff check` with `C90` enabled" in create_cli_quality
    assert "JavaScript/TypeScript CLI: `eslint` with a standing `complexity` rule" in create_cli_quality


def test_quality_skill_carries_standing_gate_verbosity_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    verbosity = (
        ROOT / "skills" / "public" / "quality" / "references" / "standing-gate-verbosity.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py" in skill_text
    assert "$SKILL_DIR/scripts/inventory_standing_test_economics.py" in skill_text
    assert "file/process/startup cost" in skill_text
    assert "runner isolation/process mode" in skill_text
    assert "verbose-on-demand escape hatch" in skill_text
    assert "quiet failure output must still name the" in skill_text
    assert "top-N runtime hot spots" in skill_text
    assert "serial fallback" in skill_text
    assert "standing-gate-verbosity.md" in skill_text
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
    assert "runtime_budget_profiles" in skill_text
    assert "CHARNESS_RUNTIME_PROFILE" in verbosity
    assert "local-linux-x86_64-8cpu" in verbosity
    assert "fixture-economics" in verbosity
    assert "parallel-critical-path" in verbosity
    assert "duplicated-proof" in verbosity


def test_quality_skill_carries_agent_production_runtime_lens() -> None:
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
    runtime_words = " ".join(runtime.split())
    dispatch_words = " ".join(dispatch.split())

    assert "agent production runtime risk" in skill_text
    assert "`references/agent-production-runtime.md`" in skill_text
    assert "production LLM or agent runtime" in runtime
    assert "a model/API client in a serving path" in runtime
    assert "model routing, fallback, or provider configuration" in runtime
    assert "streaming response endpoints or event processors" in runtime
    assert "tool/action queues driven by model output" in runtime
    assert "runtime telemetry for model calls, tokens, retries, costs, or fallbacks" in runtime
    assert (
        "product docs or operator runbooks only when paired with serving-path code, "
        "runtime configuration, telemetry, or concrete incident/runtime evidence"
        in runtime_words
    )
    assert "without corroborating runtime evidence" in runtime
    assert "docs-only\nagent product descriptions" in runtime
    assert "not\nproduction runtime evidence until paired with a concrete runtime seam" in runtime
    assert "Do not build an Anthropic-specific wrapper" in runtime
    assert "Cache And Cost Economics" in runtime
    assert "Overload And Fallback Policy" in runtime
    assert "Retry And Idempotency" in runtime
    assert "Streaming Stall Recovery" in runtime
    assert "Model Routing Economics" in runtime
    assert "Use `skill-experiment` only when the\nruntime under review is itself a Charness skill" in runtime
    assert "provider roundtrip" in runtime
    assert "explicit non-applicability" in lenses
    assert "## Agent Production Runtime" in dispatch
    assert "docs-only agent product descriptions" in dispatch
    assert (
        "product docs/runbooks paired with serving-path code, runtime configuration, "
        "telemetry, or concrete incident/runtime evidence"
        in dispatch_words
    )
    assert "deterministic proof, behavior-proof recommendation" in dispatch
    assert "product-policy decision" in dispatch
    assert "agent-production-runtime.md" in behavior


def test_quality_skill_routes_spec_markdown_to_specdown_report() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    markdown_preview = (ROOT / "skills" / "support" / "markdown-preview" / "SKILL.md").read_text(encoding="utf-8")
    runtime_contract = (
        ROOT / "skills" / "support" / "markdown-preview" / "references" / "runtime-contract.md"
    ).read_text(encoding="utf-8")

    assert "ordinary Markdown uses the markdown preview seam" in skill_text
    assert "rendered Specdown report" in skill_text
    assert "not a rule that every Markdown review must use `glow`" in markdown_preview
    assert "Executable `*.spec.md` documents" in runtime_contract


def test_quality_skill_carries_source_guard_rollup_guidance() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    layering = (
        ROOT / "skills" / "public" / "quality" / "references" / "public-spec-layering.md"
    ).read_text(encoding="utf-8")

    assert "total source-guard rows" in skill_text
    assert "next" in skill_text and "action category" in skill_text
    assert "classify_source_guards" in layering
    assert "replace_with_contract_check" in layering
    assert "top specs by source-guard pressure" in layering


def test_quality_and_create_cli_carry_command_docs_drift_pattern() -> None:
    quality_skill = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
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

    assert "command-docs drift gate" in quality_skill
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
