# Inventory Dispatch

Use focused inventories only when the quality question brings the surface into
scope. Advisory inventories are prompts for review unless the repo adapter
declares a low-noise invariant and a clear structural response.

## CLI And Operator Surface

- CLI ergonomics:
  `$SKILL_DIR/scripts/inventory_cli_ergonomics.py`
- mutating operator commands:
  `$SKILL_DIR/scripts/inventory_cli_side_effect_probes.py`
- installable CLI probes and side-effect contracts:
  `references/installable-cli-probes.md`
- command docs, doctor, install/update/reset/uninstall drift:
  inspect first-touch docs and prefer deterministic command-doc drift gates
  when the CLI surface is stable

Separate help/read-only behavior, option-looking positional rejection,
dry-run/plan output, side-effect watch contracts, binary health, install
readiness, local discoverability, target lifecycle ownership, and cleanup
ownership.

## Docs And Readability

- entrypoint docs:
  `$SKILL_DIR/scripts/inventory_entrypoint_docs_ergonomics.py`
- reader-facing public specs:
  `$SKILL_DIR/scripts/inventory_public_spec_quality.py`
- rendered Markdown preview:
  `references/bootstrap-escalations.md`
- public-spec layering:
  `references/public-spec-layering.md`

Ask whether first-touch docs are concise enough, whether deeper owners are
linked instead of duplicated, and whether public executable specs duplicate
cheaper proof at the wrong layer.

## Skills

- skill ergonomics:
  `$SKILL_DIR/scripts/inventory_skill_ergonomics.py`
- public-skill dogfood:
  `$SKILL_DIR/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id <skill-id>`
- skill quality lens:
  `references/skill-quality.md`
- ergonomics policy:
  `references/skill-ergonomics.md`

Review concise core, progressive disclosure honesty, trigger overlap or
undertrigger risk, unnecessary mode/option pressure, and prose ritual that
should become a helper script. If the repo stores skills outside
`skills/public` or `skills/support`, record `skill_ergonomics_skill_paths` in
the quality adapter so the default inventory does not return an empty scan.

## Runtime And Test Economics

- standing gate verbosity:
  `$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py`
- standing test economics:
  `$SKILL_DIR/scripts/inventory_standing_test_economics.py`
- startup probes:
  `$SKILL_DIR/scripts/measure_startup_probes.py`
- runtime summaries:
  `$SKILL_DIR/scripts/render_runtime_summary.py`
- runtime budgets:
  `$SKILL_DIR/scripts/check_runtime_budget.py`
- source lines:
  `$SKILL_DIR/scripts/inventory_sloc.py`

Quiet failure output must still name the failing unit/spec/case and show a
short actual/error snippet. Slow-gate review should separate duplicated proof,
fixture economics, parallel critical path, runner isolation, transpiler or
loader startup cost, nested CLI fanout, and the small real-binary/protocol
smokes that should remain.

When a hot spot becomes the standing single dominator, define adapter-owned
`runtime_budgets` or `runtime_budget_profiles`; budgets should fail on
recent-median drift and report latest-sample spikes separately.

## Source Hygiene

- dual implementation smell:
  `$SKILL_DIR/scripts/inventory_dual_implementation.py`
- brittle source guards:
  `$SKILL_DIR/scripts/inventory_brittle_source_guards.py`
- lint suppression pressure:
  `$SKILL_DIR/scripts/inventory_lint_ignores.py`
- gitignore scan hygiene:
  `$SKILL_DIR/scripts/inventory_gitignore_scan_hygiene.py`
- Python dead-code advisory:
  `$SKILL_DIR/scripts/run_dead_code_advisory.py --repo-root .`

When dual implementation smell is real, require one honest contract: parity
harness, canonical side plus deletion/wrapper plan, or intentional divergence
backed by an assertion. Treat first-run dead-code findings as advisory until
the repo accounts for dynamic entrypoints.

Elevate source-guard pressure as a rollup: total rows, top specs, brittle
count, and next action category should be visible together. Blanket, file-level,
or retained policy-level lint ignores need provenance and revisit conditions.

## Language And Adapter Policy

- ubiquitous language:
  `$SKILL_DIR/scripts/inventory_ubiquitous_language.py`
- adapter/gate design:
  `$SKILL_DIR/scripts/inventory_adapter_gate_design.py`

Use domain-language alignment when user-facing docs, CLI names, code/config
names, or artifacts may use different words for the same concept. Keep it
advisory unless the adapter declares low-noise deprecated aliases.

Use adapter/gate design review when adapter policy, recommendation queues,
acknowledgements, migrations, or brittle gate promotion are in scope.

## Security And Supply Chain

Use `references/security-overview.md` plus the relevant package-manager
reference (`security-npm.md`, `security-pnpm.md`, or `security-uv.md`) to
separate repo-local guarantees from external advisory freshness. Treat
`gitleaks`, `secretlint`, package audits, and online supply-chain freshness as
repo-surface-driven escalations, not mandatory first-day defaults.

## Coverage And Eval Depth

- coverage floor policy:
  `references/coverage-floor-policy.md`
- coverage floor inventory:
  `references/coverage_floor_inventory.py`
- prompt/content bulk:
  `references/find_inline_prompt_bulk.py`
- prompt asset policy:
  `references/prompt-asset-policy.md`
- pytest reference validation:
  `references/validate_spec_pytest_references.py`

If the repo keeps standing coverage floors, tag seams within
`coverage_fragile_margin_pp` as `FRAGILE` instead of burying near-miss risk in
prose. `prompt_asset_roots: []` means no canonical asset root is declared; it is
not an opt-out from inline prompt/content bulk inventory when prompt-sensitive
output matters.
