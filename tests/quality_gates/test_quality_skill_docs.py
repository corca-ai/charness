from __future__ import annotations

from pathlib import Path

import quality_label_universe

ROOT = Path(__file__).resolve().parents[2]

DISPATCH = (
    ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
).read_text(encoding="utf-8")
QUALITY_SKILL = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
QUALITY_ADAPTER_EXAMPLE = (
    ROOT / "skills" / "public" / "quality" / "adapter.example.yaml"
).read_text(encoding="utf-8")
CREATE_CLI_QUALITY_GATES = (
    ROOT / "skills" / "public" / "create-cli" / "references" / "quality-gates.md"
).read_text(encoding="utf-8")
AGENT_PRODUCTION_RUNTIME = (
    ROOT / "skills" / "public" / "quality" / "references" / "agent-production-runtime.md"
).read_text(encoding="utf-8")
AUTOMATION_PROMOTION = (
    ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
).read_text(encoding="utf-8")
CREATE_CLI_SKILL = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(
    encoding="utf-8"
)
CATALOG = (ROOT / "skills" / "public" / "quality" / "references" / "catalog.yaml").read_text(
    encoding="utf-8"
)
PUBLIC_SPEC_LAYERING = (
    ROOT / "skills" / "public" / "quality" / "references" / "public-spec-layering.md"
).read_text(encoding="utf-8")
QUALITY_LENSES = (
    ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
).read_text(encoding="utf-8")
BEHAVIOR_TESTING = (
    ROOT / "skills" / "public" / "quality" / "references" / "behavior-testing.md"
).read_text(encoding="utf-8")


def test_recommended_next_quality_moves_ranking_declares_inference_layer_interpretation() -> None:
    # Advisory-interpretation contract rollout (#322): the `Recommended Next Quality Moves`
    # ordering is an inference-layer ranking authored as prose, so the consuming
    # `quality` references declare it as such and carry the consumer-must-answer
    # requirement (both halves), while keeping verified gate results trusted.
    gate_classification = (
        ROOT / "skills" / "public" / "quality" / "references" / "gate-classification.md"
    ).read_text(encoding="utf-8")

    assert "inference-layer" in gate_classification
    assert "advisory-interpretation-contract.md" in gate_classification
    assert "interpretation question" in gate_classification
    # Verified gate results stay trusted; only the ordering is re-interpreted.
    assert "stay trusted" in gate_classification

    # Paired consumer requirement enumerates recommendation rankings as a surface.
    assert "recommendation rankings" in AUTOMATION_PROMOTION
    assert "Recommended Next Quality Moves" in AUTOMATION_PROMOTION


def test_quality_skill_carries_explicit_skill_ergonomics_lens() -> None:
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-ergonomics.md"
    ).read_text(encoding="utf-8")
    skill_quality = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-quality.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_skill_ergonomics.py" in DISPATCH
    assert "skill ergonomics" in DISPATCH
    assert "mode/option pressure" in DISPATCH
    assert "taste policing" in DISPATCH
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "model is smart" in ergonomics
    assert "`helper_owned_workflow_packet`" in ergonomics
    assert "`concept_split_references`" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "trigger overlap or undertrigger risk" in skill_quality
    assert "support-skill discoverability" in skill_quality
    assert "reference-aware contract checks" in skill_quality
    assert "overfit exact prose snippets" in skill_quality
    assert "repeated prose ritual" in skill_quality
    assert "`helper_owned_workflow_packet`" in skill_quality
    assert "`concept_split_references`" in skill_quality
    assert "growing lint suppressions" in skill_quality


def test_quality_runner_has_no_retired_usage_episode_gates() -> None:
    labels = {row["label"] for row in quality_label_universe.quality_gate_rows(ROOT) or []}

    assert "Run applicable `gate_packets` as report-first evidence" in QUALITY_SKILL
    assert "id: read-only-quality" in CATALOG
    assert "validate-usage-episodes" not in labels
    assert "report-usage-episodes" not in labels
    assert "when `.agents/usage-episodes-adapter.yaml` exists" not in QUALITY_SKILL


def test_quality_skill_makes_consumer_gate_reduction_a_primary_move() -> None:
    quality = QUALITY_SKILL.lower()

    assert quality.index("## consumer-repo health") < quality.index("## fast path")
    assert "consuming repository" in quality
    assert "existing gates, hooks, validators, wrappers, mirrors" in quality
    assert "delete or merge a duplicate" in quality
    assert "move an expensive confidence check to ci or an explicit release phase" in quality
    assert "leave an explicit non-claim" in quality
    assert "before proposing a new rule" in quality


def test_quality_skill_declares_the_consumer_boundary_and_example_universes() -> None:
    quality = QUALITY_SKILL.lower()

    assert "first consumer declaration" in quality
    assert "`universes:`" in quality
    for repo_only_class in (
        "packaging",
        "export",
        "skill contracts",
        "presets",
        "profiles",
        "integrations",
        "pointer freshness",
    ):
        assert repo_only_class in quality
    assert "authoring repository's `tools/`" in quality

    assert "universes:" in QUALITY_ADAPTER_EXAMPLE
    assert "- src/*.py" in QUALITY_ADAPTER_EXAMPLE
    assert "- src/**/*.py" in QUALITY_ADAPTER_EXAMPLE
    for charness_only_key in (
        "preset_id:",
        "adapter_review_sources:",
        "acknowledged_recommendations:",
        "gate_design_review_globs:",
        "skill_ergonomics_gate_rules:",
        "runtime_profile_default:",
        "mutation_testing:",
    ):
        assert charness_only_key not in QUALITY_ADAPTER_EXAMPLE


def test_quality_skill_carries_lint_ignore_lens() -> None:
    lint_ignore = (
        ROOT / "skills" / "public" / "quality" / "references" / "lint-ignore-discipline.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_lint_ignores.py" in DISPATCH
    assert "lint suppressions start to accumulate" in DISPATCH
    assert "lint suppression pressure" in DISPATCH
    assert "growing lint suppressions" in DISPATCH
    assert "retained policy-level ignores" in DISPATCH
    assert "concrete revisit conditions" in DISPATCH
    assert "inventory_lint_ignores.py" in lint_ignore
    assert "Treat these as prompts, not automatic failures." in lint_ignore
    assert "structural seam" in lint_ignore
    assert "source of policy truth" in lint_ignore
    assert "reviewed commit hash or review date" in lint_ignore
    assert "generated `latest.md` artifacts" in lint_ignore


def test_quality_skill_carries_entrypoint_docs_ergonomics_lens() -> None:
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "entrypoint-docs-ergonomics.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py" in DISPATCH
    assert "entrypoint-doc ergonomics" in DISPATCH
    assert "smart agent/operator can infer safely" in DISPATCH
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "Command Docs Drift Gate" in ergonomics
    assert ".agents/command-docs.yaml" in ergonomics
    assert "required help anchors" in ergonomics
    assert "doc-set dogma" in DISPATCH


def test_quality_skill_carries_cli_ergonomics_smells_lens() -> None:
    cli_smells = (
        ROOT / "skills" / "public" / "quality" / "references" / "cli-ergonomics-smells.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_ergonomics.py" in DISPATCH
    assert "flat help-list" in DISPATCH
    assert "multiple archetype schema namespaces" in DISPATCH
    assert "Flat `--help` Lists" in cli_smells
    assert "Cross-Archetype Schema Leakage" in cli_smells
    assert "command-archetypes.json" in cli_smells


def test_quality_and_create_cli_carry_side_effect_probe_lens() -> None:
    cli_probes = (
        ROOT / "skills" / "public" / "quality" / "references" / "installable-cli-probes.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_cli_side_effect_probes.py" in DISPATCH
    assert "option-looking positional rejection" in DISPATCH
    assert "mutating subcommand help probes" in cli_probes
    assert "side-effect seams" in cli_probes
    assert "option-looking" in CREATE_CLI_SKILL
    assert "side-effect probe fixtures" in CREATE_CLI_SKILL
    assert "dry-run or plan probes" in CREATE_CLI_QUALITY_GATES
    assert "subprocess runners" in CREATE_CLI_QUALITY_GATES


def test_quality_skill_carries_public_spec_layering_lens() -> None:
    assert "$SKILL_DIR/scripts/inventory_public_spec_quality.py" in DISPATCH
    assert "duplicated at the wrong layer" in DISPATCH
    assert "proof layering" in PUBLIC_SPEC_LAYERING
    assert "reader-facing claims plus cheap local proof" in PUBLIC_SPEC_LAYERING
    assert "what is now duplicated at the wrong layer" in PUBLIC_SPEC_LAYERING
    assert "move_down" in PUBLIC_SPEC_LAYERING
    assert "delete_or_merge" in PUBLIC_SPEC_LAYERING
    assert "keep_if_integration_value" in PUBLIC_SPEC_LAYERING


def test_quality_skill_prefers_structure_over_heuristic_chasing() -> None:
    scaffold = (
        ROOT / "skills" / "public" / "quality" / "scripts" / "scaffold_quality_artifact.py"
    ).read_text(encoding="utf-8")
    fresh_eye = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")

    assert "smell sensors" in QUALITY_SKILL
    assert "SECTIONS = (" in scaffold
    assert "## Current Gates" in scaffold
    assert "gate_packets" in QUALITY_SKILL
    assert (
        "delete, merge, split ownership, extract a helper, or narrow an interface" in QUALITY_SKILL
    )
    assert "Length, duplicate, and pressure heuristics are smell sensors" in QUALITY_SKILL
    assert "routing default, not a veto against good deterministic enforcement" in DISPATCH
    assert "standing threshold gates such as coverage floors, runtime budgets" in DISPATCH
    assert "Pytest Economics" in DISPATCH
    assert "what structural simplification is missing" in QUALITY_LENSES
    assert "canonical routing lives in `SKILL.md`" in QUALITY_LENSES
    assert "do not over-apply this caution to standing threshold gates" in QUALITY_LENSES
    assert "gate-last posture" in QUALITY_LENSES
    assert "follow the canonical routing in `SKILL.md` first" in AUTOMATION_PROMOTION
    assert "tie-breaker, not a veto" in AUTOMATION_PROMOTION
    assert "false positives are low enough" in AUTOMATION_PROMOTION
    assert "smell sensors first" in AUTOMATION_PROMOTION
    assert "canonical fresh-eye review" in fresh_eye


def test_quality_skill_and_create_cli_carry_language_lint_defaults() -> None:
    assert "For Python, default to `ruff check` as the standing lint path" in DISPATCH
    assert "choose exactly one type checker (`mypy` or `pyright`)" in DISPATCH
    assert "For JavaScript/TypeScript, default to `eslint`" in DISPATCH
    assert "`complexity` rule" in DISPATCH
    assert "Python CLI: `ruff check` with `C90` enabled" in CREATE_CLI_QUALITY_GATES
    assert (
        "JavaScript/TypeScript CLI: `eslint` with a standing `complexity` rule"
        in CREATE_CLI_QUALITY_GATES
    )


def test_quality_skill_carries_standing_gate_verbosity_lens() -> None:
    verbosity = (
        ROOT / "skills" / "public" / "quality" / "references" / "standing-gate-verbosity.md"
    ).read_text(encoding="utf-8")

    assert "$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py" in DISPATCH
    assert "$SKILL_DIR/scripts/inventory_standing_test_economics.py" in DISPATCH
    assert "$SKILL_DIR/scripts/inventory_structural_waste.py" in DISPATCH
    assert "file/process/startup cost" in DISPATCH
    assert "runner isolation/process mode" in DISPATCH
    assert "duplicate broad discovery/collection" in DISPATCH
    assert "broad scanner prefiltering" in DISPATCH
    assert "verbose-on-demand escape hatch" in DISPATCH
    assert "quiet failure output must still name the" in DISPATCH
    assert "top-N runtime hot spots" in DISPATCH
    assert "serial fallback" in DISPATCH
    assert "standing-gate-verbosity.md" in DISPATCH
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
    assert "fresh-eye-subagent-review.md" in QUALITY_SKILL
    assert "runtime_budget_profiles" in DISPATCH
    assert "CHARNESS_RUNTIME_PROFILE" in verbosity
    assert "local-linux-x86_64-8cpu" in verbosity
    assert "fixture-economics" in verbosity
    assert "parallel-critical-path" in verbosity
    assert "duplicated-proof" in verbosity


def test_quality_skill_carries_agent_production_runtime_lens_core_anchor() -> None:
    assert "runtime risk" in QUALITY_SKILL
    assert "agent-production-runtime.md" in CATALOG
    assert "production agent runtime" in CATALOG
    assert "`references/agent-production-runtime.md`" in DISPATCH
    assert "production LLM or agent runtime" in AGENT_PRODUCTION_RUNTIME
    assert "Do not build an Anthropic-specific wrapper" in AGENT_PRODUCTION_RUNTIME
    assert "Cache And Cost Economics" in AGENT_PRODUCTION_RUNTIME
    assert "Overload And Fallback Policy" in AGENT_PRODUCTION_RUNTIME
    assert "Retry And Idempotency" in AGENT_PRODUCTION_RUNTIME
    assert "Streaming Stall Recovery" in AGENT_PRODUCTION_RUNTIME
    assert "Model Routing Economics" in AGENT_PRODUCTION_RUNTIME
    assert "provider roundtrip" in AGENT_PRODUCTION_RUNTIME
    assert "explicit non-applicability" in QUALITY_LENSES
    assert "agent-production-runtime.md" in BEHAVIOR_TESTING


def test_quality_agent_runtime_lens_keeps_positive_runtime_triggers() -> None:
    assert "a model/API client in a serving path" in AGENT_PRODUCTION_RUNTIME
    assert "model routing, fallback, or provider configuration" in AGENT_PRODUCTION_RUNTIME
    assert "streaming response endpoints or event processors" in AGENT_PRODUCTION_RUNTIME
    assert "tool/action queues driven by model output" in AGENT_PRODUCTION_RUNTIME
    assert (
        "runtime telemetry for model calls, tokens, retries, costs, or fallbacks"
        in AGENT_PRODUCTION_RUNTIME
    )


def test_quality_agent_runtime_lens_requires_runtime_evidence_for_docs() -> None:
    runtime_words = " ".join(AGENT_PRODUCTION_RUNTIME.split())

    assert (
        "user-facing agent product docs only when paired with serving-path code, "
        "runtime configuration, telemetry, or concrete incident/runtime evidence" in runtime_words
    )
    assert (
        "operator runbooks that describe an actual incident or runtime procedure"
        in AGENT_PRODUCTION_RUNTIME
    )
    assert "without corroborating runtime evidence" in AGENT_PRODUCTION_RUNTIME
    assert "docs-only\nagent product descriptions" in AGENT_PRODUCTION_RUNTIME
    assert (
        "not\nproduction runtime evidence until paired with a concrete runtime seam"
        in AGENT_PRODUCTION_RUNTIME
    )


def test_quality_agent_runtime_dispatch_mirrors_canonical_boundary() -> None:
    dispatch_words = " ".join(DISPATCH.split())

    assert "## Agent Production Runtime" in DISPATCH
    assert "mirrors the canonical boundary in `agent-production-runtime.md`" in DISPATCH
    assert "docs-only agent product descriptions" in dispatch_words
    assert (
        "product docs paired with serving-path code, runtime configuration, telemetry, "
        "or concrete incident/runtime evidence" in dispatch_words
    )
    assert "operator runbooks that describe an actual incident or runtime procedure" in DISPATCH
    assert "deterministic proof, behavior-proof recommendation" in DISPATCH
    assert "product-policy decision" in DISPATCH


def test_quality_skill_routes_spec_markdown_to_specdown_report() -> None:
    markdown_preview = (ROOT / "skills" / "support" / "markdown-preview" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    runtime_contract = (
        ROOT / "skills" / "support" / "markdown-preview" / "references" / "runtime-contract.md"
    ).read_text(encoding="utf-8")

    assert "ordinary Markdown uses the markdown preview seam" in DISPATCH
    assert "rendered Specdown report" in DISPATCH
    assert "not a rule that every Markdown review must use `glow`" in markdown_preview
    assert "Executable `*.spec.md` documents" in runtime_contract


def test_quality_skill_carries_source_guard_rollup_guidance() -> None:
    assert "total source-guard rows" in DISPATCH
    assert "next" in DISPATCH and "action category" in DISPATCH
    assert "classify_source_guards" in PUBLIC_SPEC_LAYERING
    assert "replace_with_contract_check" in PUBLIC_SPEC_LAYERING
    assert "top specs by source-guard pressure" in PUBLIC_SPEC_LAYERING


def test_quality_and_create_cli_carry_command_docs_drift_pattern() -> None:
    adapter_contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")

    assert "command-docs drift gate" in DISPATCH
    assert "stable CLI command docs" in AUTOMATION_PROMOTION
    assert ".agents/command-docs.yaml" in adapter_contract
    assert "runner-specific section labels" in adapter_contract
    assert "Standing Test Economics" in adapter_contract
    assert "command-docs drift gate" in CREATE_CLI_SKILL
    assert "repo-local command-docs contract" in CREATE_CLI_QUALITY_GATES


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
    external = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "external-capability-clis.md"
    ).read_text(encoding="utf-8")

    assert "external capability boundary" in CREATE_CLI_SKILL
    assert "host-side" in CREATE_CLI_SKILL
    assert "redaction tests" in CREATE_CLI_SKILL
    assert "missing_setup" in external
    assert "needs_credentials" in external
    assert "allowed_methods" in external
    assert "allowed_path_prefixes" in external
    assert "host-only executor boundary" in external
    assert "raw request bodies" in CREATE_CLI_QUALITY_GATES


def _workflow_step(text: str, number: int) -> str:
    """One numbered workflow step, sliced by its own number.

    Scoped to a single step because that is the unit an agent executes: a flag
    named three steps from the script that accepts it is not the same defect as
    one named beside it. Sliced by NUMBER rather than by searching for the flag,
    because `--intent record` also appears correctly in the Bootstrap fence at
    the top of the file -- searching would have anchored on that and silently
    measured the wrong region.
    """
    start = text.index(f"\n{number}. ")
    end = text.index(f"\n{number + 1}. ", start)
    return text[start:end]


def test_the_step_that_instructs_intent_names_the_script_that_accepts_it() -> None:
    """#538: step 8 instructed `--intent record` while naming only the scaffold.

    `scaffold_quality_artifact.py` exits 2 on `--intent` and emits neither
    `refresh_current_pointer_command` nor `update_current_pointer_after_write`;
    all three belong to `resolve_quality_artifact.py`, which the step never named.

    Pinned by co-occurrence inside ONE step rather than by a repo-wide
    doc-key-to-helper gate. That gate was prototyped against every public
    SKILL.md and fired 25 times for ~2 real defects — `git status --short`,
    `rg --files`, and subcommand flags dominate the signal — so it would have
    been a wolf-crier over a class the sibling sweep measured at one instance in
    seventeen skills.
    """
    step = _workflow_step(QUALITY_SKILL, 8)

    assert "resolve_quality_artifact.py" in step, (
        "the step instructing --intent must name the script that accepts it"
    )
    for owned in (
        "--intent record",
        "--intent current",
        "refresh_current_pointer_command",
        "update_current_pointer_after_write",
    ):
        assert owned in step, f"{owned} left the step it is documented in"


def test_the_step_names_the_fact_that_decides_whether_the_write_path_is_safe() -> None:
    """Re-aimed, deliberately: the producer changed under the sentence this pinned.

    The old anchors (`overwrites`, `previous`, `latest.md`) bound a warning that the scaffold's
    `write_artifact_path` IS the previous review's file. That stopped being true when the
    scaffold started resolving by subject and routing off any record it cannot confirm is this
    review's, so keeping the anchors would have pinned prose that is now false — the failure
    mode this guard exists to prevent, one level up.

    What replaces it is the fact an author must now read, and the two states that are NOT a
    green light. `unknown` is the one that matters: the target carries no dated filename to
    check, which is the `latest.md`-as-a-regular-file layout the old anchor covered.
    """
    step = _workflow_step(QUALITY_SKILL, 8)

    assert "write_artifact_subject_match" in step
    # `undeclared` is NOT required here: round 2 showed `quality`'s invocation key is never
    # None (its date channel is always known), so a guard demanding that state would pin prose
    # about a payload the producer cannot emit — the same defect one level up.
    for state in ("`match`", "`unknown`", "`routed`"):
        assert state in step, f"{state} is a state this producer can emit and an author must act on"
    assert "refused_write_artifact_path" in step, (
        "the payload names the record it declined; prose that omits it leaves the author "
        "unable to find the review they expected to be writing"
    )
    assert "never silently replace it" in step


def test_the_scaffold_is_never_the_thing_step_eight_says_to_write_to() -> None:
    """Polarity, not just presence — the gap the resolution critique found.

    The two assertions above are satisfied by any step that merely CONTAINS the
    right script and the right words. A compaction that flips the instruction --
    "write the scaffold payload's `write_artifact_path`; the resolver is for a
    rolling summary" -- reintroduces the whole defect with both of them green.
    So bind the direction: the sentence naming the scaffold's write path must
    forbid it, and the sentence telling you to write must name the resolver.
    """
    step = _workflow_step(QUALITY_SKILL, 8)

    scaffold_clause = next(part for part in step.split(".") if "scaffold payload" in part)
    assert "Do NOT" in scaffold_clause, (
        "the clause naming the scaffold's write path must forbid trusting it unconditionally, "
        f"not merely mention it: {scaffold_clause.strip()!r}"
    )
    # The condition has to live in the same clause as the prohibition. Split apart, a
    # compaction keeps the `Do NOT` and drops what lifts it — or keeps "read the match value"
    # and drops the prohibition, which is the polarity flip this test exists for.
    assert "write_artifact_subject_match" in scaffold_clause, (
        f"the prohibition must name the fact that lifts it: {scaffold_clause.strip()!r}"
    )
    assert "only `match`" in step, "the step must say which single state permits the write"
