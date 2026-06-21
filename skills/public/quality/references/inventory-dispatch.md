# Inventory Dispatch

Use focused inventories only when the quality question brings the surface into
scope. Advisory inventories are prompts for review unless the repo adapter
declares a low-noise invariant and a clear structural response.

Inventories named in the quality artifact's `## Commands Run` must engage with at
least two distinct declared non-headline fields (one is enough when only one is
declared); the `validate-inventory-consumption` phase fails closeout when the
artifact summarizes a cited inventory by headline only, and
`validate-inventory-consumption-declaration` plus
`check-inventory-declaration-coverage` keep the declaration drift-free and
complete (declaration: `references/inventory-consumer-fields.json`).

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
ownership. Review covers flat help-list crowding, mutating subcommand probes,
multiple archetype schema namespaces, and the command-docs drift gate.

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
cheaper proof at the wrong layer. Review covers entrypoint-doc ergonomics (a
smart agent/operator can infer safely, no doc-set dogma), what proof is
duplicated at the wrong layer, ordinary Markdown uses the markdown preview seam,
and executable specs use the rendered Specdown report.

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
undertrigger risk, unnecessary mode/option pressure, taste policing, and prose
ritual that should become a helper script. When public-skill or durable artifact
behavior is in scope, scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`.
If the repo stores skills outside `skills/public` or `skills/support`, record
`skill_ergonomics_skill_paths` in the quality adapter so the default inventory
does not return an empty scan.

## Runtime And Test Economics

- standing gate verbosity:
  `$SKILL_DIR/scripts/inventory_standing_gate_verbosity.py`
- standing test economics:
  `$SKILL_DIR/scripts/inventory_standing_test_economics.py`
- executable-spec runtime and dup economics:
  `references/executable-spec-economics.md`
- duplicate discovery and broad scanner waste:
  `$SKILL_DIR/scripts/inventory_structural_waste.py`
- release-only sentinel coverage:
  `$SKILL_DIR/scripts/inventory_release_only_sentinels.py`
  (use `--path` for selected slow/release-only files; the default all-tests
  scan is intentionally broad and advisory-noisy)
- startup probes:
  `$SKILL_DIR/scripts/measure_startup_probes.py`
- runtime summaries:
  `$SKILL_DIR/scripts/render_runtime_summary.py`
- runtime budgets:
  `$SKILL_DIR/scripts/check_runtime_budget.py`
- source lines:
  `$SKILL_DIR/scripts/inventory_sloc.py`
- testability and affected-test selection:
  `references/testability-and-selection.md`
- local-gate speed vs CI recoverability:
  `$SKILL_DIR/scripts/inventory_ci_recoverable_gates.py`
  (`references/ci-recoverable-gate-triage.md` — the counterweight that flags only
  the costly local gates CI fully re-runs as move-off-local candidates; the rest
  stay `keep-local`)

Quiet failure output must still name the failing unit/spec/case and show a
short actual/error snippet. Slow-gate review should separate duplicated proof,
duplicate broad discovery or collection, missing cheap prefilters before broad
parser scans, fixture economics, parallel critical path, runner isolation,
transpiler or loader startup cost, nested CLI fanout, and the small
real-binary/protocol smokes that should remain.

When slow tests or mutation tests expose poor affected-test selection, ask
whether the code shape makes a fast subset predictable before recommending a
coverage-observing selector or another cache. Observation tools can accelerate
feedback, but they should not become the only map from a small behavior change
to the tests that prove it.

When a hot spot becomes the standing single dominator, define adapter-owned
`runtime_budgets` or `runtime_budget_profiles`; budgets should fail on
recent-median drift and report latest-sample spikes separately.

Runtime review covers file/process/startup cost, runner isolation/process mode,
duplicate broad discovery/collection, broad scanner prefiltering, the
verbose-on-demand escape hatch (quiet failure output must still name the failing
unit), top-N runtime hot spots, serial fallback vs `runtime_budget_profiles`,
Pytest Economics, and bounded test-ratio posture; see `standing-gate-verbosity.md`.

## Agent Production Runtime

- production LLM or agent runtime review:
  `references/agent-production-runtime.md`
- behavior-proof recommendation:
  `references/behavior-testing.md`
- structured recommend-only behavior finding:
  `$SKILL_DIR/scripts/recommend_behavior_test.py`
- external provider proof level:
  `../../../shared/references/external-capability-proof-ladder.md`

Use this dispatch path only when repo evidence shows production runtime signs:
a model/API client in a serving path, model routing or fallback config,
streaming endpoint, tool/action queue, runtime telemetry for model calls,
tokens, retries, costs, and fallbacks, product docs paired with serving-path
code, runtime configuration, telemetry, or concrete incident/runtime evidence,
or operator runbooks that describe an actual incident or runtime procedure. This
summary mirrors the canonical boundary in `agent-production-runtime.md`. Do not
trigger it from eval fixtures, skill docs, prompt examples, docs-only agent
product descriptions, harness-only agent orchestration, or offline benchmark
scaffolding alone.

Review cache/cost economics, overload fallback, retry idempotency, streaming
stall recovery, model routing economics, and telemetry as evidence questions.
Classify each gap as deterministic proof, behavior-proof recommendation, or
product-policy decision before proposing new gates.

For evaluator-backed behavior closeout, prompt regression, baseline compare, or
operator reading test, use `quality` before downgrading to HITL.
Generic review, closeout, or "run quality" wording is not enough to run an evaluator.
For external/runtime capability slices, treat readiness-only proof (`surface`,
`worker_queued`, healthcheck-style `host_decision`) as `Weak` until at least one
`provider_roundtrip` is observed
(`../../../shared/references/external-capability-proof-ladder.md`).

## Source Hygiene

- dual implementation smell:
  `$SKILL_DIR/scripts/inventory_dual_implementation.py`
  (`references/dual-implementation-parity.md` — the shared-schema /
  exported-both / no-parity-harness signals, the three honest contracts, and the
  weak-contract classification behind the advisory)
- brittle source guards:
  `$SKILL_DIR/scripts/inventory_brittle_source_guards.py`
  (`references/brittle-source-guards.md` — the brittle / at_risk /
  normalization_needed taxonomy, Recommendation Order, and policy-without-tool rule)
- lint suppression pressure:
  `$SKILL_DIR/scripts/inventory_lint_ignores.py`
  (`references/lint-ignore-discipline.md` — suppression pressure points, the
  keep-it-narrow-and-cheaper-than-the-deferred-fix rule, and Retained Policy Ignores)
- gitignore scan hygiene:
  `$SKILL_DIR/scripts/inventory_gitignore_scan_hygiene.py`
- Python dead-code advisory:
  `$SKILL_DIR/scripts/run_dead_code_advisory.py --repo-root .`
- code clone-family advisory:
  `$SKILL_DIR/scripts/inventory_nose_clones.py --repo-root .`
  (`--exclude <glob>` is repeatable for focused review; `--ignore-file <file>`
  applies a structured nose ignore file)

When dual implementation smell is real, require one honest contract: parity
harness, canonical side plus deletion/wrapper plan, or intentional divergence
backed by an assertion. Treat first-run dead-code findings as advisory until
the repo accounts for dynamic entrypoints. For JavaScript/TypeScript, default to
`knip` as the unused files/exports/dependencies advisory detector and keep it
advisory until the repo proves low-noise findings and a clear cleanup action.

### Clone Families As Structural Signals

Clone-family advisories are structural signals, never a number to drive down.
Do not use `total_dup_lines` or family counts as a reduction target, and do
not read them as a cross-version trend: scanner upgrades change the surface
model and ranking, so re-baseline per scanner version instead of treating a
larger number as a regression. Answer the advisory's declared interpretation
question per family, then map each reviewed family to one structural
response:

- **Intentional duplication** (portability or bootstrap fences): keep the
  copies, and machine-own their consistency — a canonical block plus a
  consistency gate with a fix mode, or a generator that stamps the copies. A
  fence without a consistency guard is an unverified claim, and silent
  divergence among "intentional" copies is how the fence rots.
- **Extract candidate** (byte-identical members with a plausible owning
  module): extract only when the owner is nameable and the abstraction cost
  is below the payoff; prefer many-member small families over two-member
  large ones.
- **Generated-surface candidate** (copies exist because one source should be
  stamped into many places): move ownership to the generator or sync
  machinery and gate drift there, instead of editing the copies.
- **Design-shaped family** (many members, low shared-line ratio): treat it as
  a design question and route it through a spec/design pass before any
  extraction attempt.

Record the chosen response — or an explicit keep-with-fence — per reviewed
family in the quality artifact, so the next scan consumes dispositions
instead of rediscovering the same families. Review extractable non-bootstrap
families first, and do not refactor every reported family just because the
advisory scanner can see it.

Before any structural cleanup edit driven by these signals, fill the
per-candidate scorecard in
[quality-signal-scorecard](./quality-signal-scorecard.md): it forces the
behavior-value, ownership, blast-radius, and stop-condition judgments that no
advisory number can make, and it rejects metric-only cleanup rationale.

Elevate source-guard pressure as a rollup: total source-guard rows, top specs,
brittle count, and next action category should be visible together.

Watch how lint suppressions start to accumulate: lint suppression pressure,
growing lint suppressions, and retained policy-level ignores each need
free safety oracle checks, provenance, and concrete revisit conditions. Blanket,
file-level, or retained policy-level lint ignores need provenance and revisit
conditions.

Boundary-bypass ratchets use `references/boundary-bypass-ratchet.md`; duplicate
ratchets use `references/dup-ratchet.md` (the boy-scout duplicate ratchet
`$SKILL_DIR/scripts/check_dup_ratchet.py`): `quality` owns the portable
payload/policy and exemption contract; consumer repos own stack-specific probes,
scope, and artifacts.

## Language And Adapter Policy

- ubiquitous language:
  `$SKILL_DIR/scripts/inventory_ubiquitous_language.py`
- adapter/gate design:
  `$SKILL_DIR/scripts/inventory_adapter_gate_design.py`

Use domain-language alignment when user-facing docs, CLI names, code/config
names, or artifacts may use different words for the same concept. Keep it
advisory unless the adapter declares low-noise deprecated aliases.

Use adapter/gate design review when adapter policy, recommendation queues,
acknowledgements, migrations, or brittle gate promotion are in scope; see
`references/adapter-gate-review.md` for the finding_class / enforcement_tier
glossary and the Template-First doctrine.

Language baselines stay explicit.
For Python, default to `ruff check` as the standing lint path, include `C90`,
and choose exactly one type checker (`mypy` or `pyright`).
For JavaScript/TypeScript, default to `eslint`, use `tsc --noEmit` when
TypeScript is present, and turn on a `complexity` rule.
This is a routing default, not a veto against good deterministic enforcement;
do not over-apply it to standing threshold gates such as coverage floors, runtime budgets,
or other already-honest enforced limits.

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
prose. `prompt_asset_roots: []` only means no canonical asset root is declared; it
is not an opt-out from inline prompt/content bulk inventory when prompt-sensitive
output matters.
