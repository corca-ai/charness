# README Proof And Cautilus Eval Migration

## Purpose

After the current upstream Cautilus redesign is done, migrate Charness from the
old instruction-surface proof seam to the new `cautilus eval` surface and use
that migration to build an explicit proof map for the promises made in
`README.md`.

The goal is not to prove every README sentence with an evaluator. The goal is
to give every load-bearing README promise an owner:

- deterministic code/test/validator proof for CLI, packaging, generated docs,
  lock state, install/update, and helper behavior
- Cautilus repo eval proof for agent routing, prompt-sensitive behavior, and
  compact instruction-surface behavior
- HITL or narrative review for philosophical and judgment-heavy claims
- explicit deferred operator proof for host-visible install/update behavior
  that cannot be fully closed in a local fixture

## Current Blocking Facts

- Charness still has old Cautilus contract names in
  `.agents/cautilus-adapter.yaml`, `evals/cautilus/instruction-surface-cases.json`,
  `scripts/cautilus_adapter_lib.py`, `scripts/cautilus_scenarios_lib.py`,
  `scripts/plan_cautilus_proof.py`, and `scripts/validate_cautilus_proof.py`.
- Cautilus issue
  [corca-ai/cautilus#32](https://github.com/corca-ai/cautilus/issues/32)
  removes `cautilus instruction-surface test/evaluate` with no backward
  compatibility. The replacement is:
  - `cautilus eval test --fixture <evaluation_input.v1.json>`
  - `cautilus eval evaluate --input <evaluation_observed.v1.json>`
- The new fixture shape is `cautilus.evaluation_input.v1` with
  `surface`, `preset`, and `cases[]`.
- Old instruction-surface cases migrate by wrapping them as
  `surface: repo`, `preset: whole-repo`, renaming `evaluations` to `cases`,
  and renaming `evaluationId` to `caseId`.
- Read-only routing proof and write-producing workflow proof must be separated.
  The agreed direction is:
  - no-write discovery for routing evals
  - workspace-write proof for realistic workflow execution

## Pickup Preconditions

Before editing Charness, confirm the upstream Cautilus surface is stable enough
to target:

```bash
git -C ../cautilus status --short
git -C ../cautilus log --oneline -5
../cautilus/bin/cautilus --help
../cautilus/bin/cautilus commands --json
sed -n '1,260p' ../cautilus/docs/specs/evaluation-surfaces.spec.md
sed -n '1,260p' ../cautilus/fixtures/eval/whole-repo/checked-in-agents-routing.fixture.json
```

Use the current local `../cautilus` checkout and the GitHub issue above as the
source of truth. Do not widen Charness proof wiring while the upstream contract
is still moving.

## First Slice

Migrate the existing maintained routing proof without broadening the scenario
set yet.

1. Rename the Charness proof fixture:
   - from `evals/cautilus/instruction-surface-cases.json`
   - to a `cautilus.evaluation_input.v1` fixture such as
     `evals/cautilus/whole-repo-routing.fixture.json`
2. Convert the five existing cases mechanically:
   - top-level `schemaVersion`: `cautilus.evaluation_input.v1`
   - add `surface: repo`
   - add `preset: whole-repo`
   - rename `evaluations` to `cases`
   - rename each `evaluationId` to `caseId`
   - keep fields such as `prompt`, `expectedRouting`,
     `requiredInstructionFiles`, and `requiredSupportingFiles`
3. Update `.agents/cautilus-adapter.yaml`:
   - replace `instruction_surface_test_command_templates` with
     `eval_test_command_templates`
   - replace `instruction_surface_cases_default` with
     `evaluation_input_default`
   - replace `{instruction_surface_cases_file}` with `{eval_cases_file}`
   - replace `{instruction_surface_input_file}` with `{eval_observed_file}`
   - replace command text with `cautilus eval test --fixture ...` or the
     repo-owned runner shape required by upstream Cautilus
4. Update the Charness Cautilus validators and planners:
   - `scripts/cautilus_adapter_lib.py`
   - `scripts/cautilus_scenarios_lib.py`
   - `scripts/validate_cautilus_scenarios.py`
   - `scripts/plan_cautilus_proof.py`
   - `scripts/validate_cautilus_proof.py`
   - tests that assert old instruction-surface wording
5. Keep historical artifact references as history only. New current proof
   artifacts should say `eval`, `evaluation_input`, `evaluation_observed`, and
   `evaluation_summary`.

Acceptance for this slice:

```bash
python3 scripts/validate_cautilus_scenarios.py --repo-root .
python3 scripts/validate_public_skill_validation.py --repo-root .
python3 scripts/plan_cautilus_proof.py --repo-root . --json
python3 scripts/run_slice_closeout.py --repo-root .
```

If upstream Cautilus can run locally, also run the migrated fixture with both
available repo backends before updating `charness-artifacts/cautilus/latest.md`.

## Read-Only Versus Workspace-Write Proof

The `quality` dogfood run found a real seam: a read-only routing proof can
block when the startup `find-skills` path tries to refresh durable inventory
artifacts.

Do not solve that by weakening startup behavior globally.

Implement or wire two proof modes:

- routing eval: read-only, no-write discovery, observes first routing decision
  and loaded instruction/support files
- workflow eval: workspace-write, permits durable artifacts, validates that a
  realistic agent run can execute the workflow without state-cache or artifact
  write failures

The likely Charness-side implementation is a no-write mode in the find-skills
discovery path, or a Cautilus runner mode that observes routing without
requiring the discovery artifact refresh. The exact owner should be chosen
after the upstream eval runner stabilizes.

## README Proof Ledger

Create a proof ledger after the eval migration, not before it. Suggested path:
`docs/readme-proof.md`, with an optional JSON owner if validators need a
machine-readable contract later.

Each entry should include:

- README line or section
- exact promise
- proof owner: deterministic, Cautilus, HITL, or deferred operator proof
- current owning files/tests/artifacts
- freshness rule
- known gap, if any

Initial claim groups:

- Quick Start managed install and host plugin bundle
- `init-repo` updates `AGENTS.md` and related settings
- normal prompts route through Charness context without requiring the user to
  name a skill every time
- CLI exposes local harness state instead of guessing
- `charness update all` refreshes tracked tools and materialized support skills
- public skills name user intent while support skills hide tool-specific detail
- `quality` reviews gates, brittle tests, security risk, docs drift, skill and
  script ergonomics, tool health, and runtime cost
- retros/handoffs keep context flowing across sessions
- prompt- or behavior-affecting changes can use Cautilus evaluator-backed
  scenario review

Do not try to prove the Core Concepts prose as if it were an API contract.
Use HITL/narrative review for philosophical claims unless they imply concrete
agent behavior or command behavior.

## First New Cautilus Fixtures

After the mechanical migration is green, add README-facing eval fixtures in
this order:

1. `readme-quickstart-loads-init-repo`
   - prompt: `Use charness to initialize this repo.`
   - expected route: `find-skills -> init-repo`
   - README promise: Quick Start says the agent loads `charness:init-repo`
2. `normal-prompt-routes-without-skill-name`
   - prompt: `This test is failing; fix the behavior and verify it.`
   - expected route: `find-skills -> impl` or `find-skills -> debug`,
     depending on final wording
   - README promise: normal product-development prompts work after init
3. `validation-closeout-routes-quality-before-hitl`
   - keep the existing intent from the old case
   - expected route: `find-skills -> quality`
   - README promise: Cautilus-backed review belongs under quality/validation
4. `compact-agents-follows-convention-link`
   - prompt: ask whether editing `skills/public/<id>/SKILL.md` changes the next
     installed Claude/Codex session immediately
   - required supporting file: `docs/conventions/operating-contract.md`
   - README/AGENTS promise: compact `AGENTS.md` can delegate detail to
     convention docs without losing behavior

Second wave:

- `support-detail-hidden-under-public-intent`: external source prompt routes
  to `gather`, not `web-fetch`
- `handoff-context-keeps-flowing`: next-session prompt routes to `handoff`
- `init-repo-partial-normalize-not-template`: mature partial repo is normalized
  without greenfield rewrite
- `quality-inspects-tool-state`: quality prompt inspects existing gates and
  tool health before proposing new proof

## Non-Goals

- Do not add a large scenario registry mutation before the Cautilus contract is
  stable.
- Do not replace deterministic CLI, packaging, control-plane, or doc-link gates
  with Cautilus.
- Do not keep old instruction-surface naming in current docs except where
  referring to historical artifacts.
- Do not treat a passing routing fixture as proof that workflow artifact writes
  work. That is the workspace-write proof layer.

## Closeout For The Migration Slice

When the migration lands:

1. refresh `charness-artifacts/cautilus/latest.md` using the new eval language
2. update `docs/public-skill-validation.md` so the proof split names
   `cautilus eval test/evaluate`
3. update `docs/handoff.md` so the next first move is the README proof ledger
   or the first README-facing fixture, not the migration itself
4. run surface closeout:

```bash
python3 scripts/check_changed_surfaces.py --repo-root .
python3 scripts/run_slice_closeout.py --repo-root .
```

5. commit the migration before widening scenarios
