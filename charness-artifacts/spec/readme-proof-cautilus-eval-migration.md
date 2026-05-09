# README Proof And Cautilus Eval Migration

## Purpose

After the current upstream Cautilus redesign is done, migrate Charness from the
old instruction-surface proof seam to the new `cautilus eval` surface and use
that migration to build an explicit proof map for the promises made in
`README.md`.

Status 2026-04-28: the first migration slice is landed. Charness now uses
`evals/cautilus/whole-repo-routing.fixture.json`,
`.agents/cautilus-adapter.yaml` `evaluation_input_default` /
`eval_test_command_templates`, and `cautilus eval test`; current proof is
recorded in `charness-artifacts/cautilus/latest.md`. The README proof ledger
is now owned by [docs/readme-proof.md](../../docs/readme-proof.md).

Status 2026-05-07: the no-write side of the read-only versus workspace-write
proof split is landed as the `find-skills --read-only` flag (see the
`Read-Only Versus Workspace-Write Proof` section below). The remaining next
move is the workspace-write workflow proof carrier and the actual routing eval
wiring once the Cautilus adapter is re-enabled.

The goal is not to prove every README sentence with an evaluator. The goal is
to give every load-bearing README promise an owner:

- deterministic code/test/validator proof for CLI, packaging, generated docs,
  lock state, install/update, and helper behavior
- Cautilus repo eval proof for agent routing, prompt-sensitive behavior, and
  compact instruction-surface behavior
- HITL or narrative review for philosophical and judgment-heavy claims
- explicit deferred operator proof for host-visible install/update behavior
  that cannot be fully closed in a local fixture

## Original Blocking Facts

- Charness used to have old Cautilus contract names in
  `.agents/cautilus-adapter.yaml`, the maintained whole-repo routing fixture,
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

Status: landed 2026-04-28. The existing maintained routing proof migrated
without broadening the scenario set.

1. Rename the Charness proof fixture:
   - from the old instruction-surface case file
   - to `evals/cautilus/whole-repo-routing.fixture.json`
2. Convert the five existing cases mechanically:
   - top-level `schemaVersion`: `cautilus.evaluation_input.v1`
   - add `surface: repo`
   - add `preset: whole-repo`
   - rename `evaluations` to `cases`
   - rename each `evaluationId` to `caseId`
   - keep fields such as `prompt`, `expectedRouting`,
     `requiredInstructionFiles`, and `requiredSupportingFiles`
3. Update `.agents/cautilus-adapter.yaml`:
   - use `eval_test_command_templates`
   - use `evaluation_input_default`
   - use `{eval_cases_file}` and `{eval_observed_file}`
   - use command text with `cautilus eval test --fixture ...` or the repo-owned
     runner shape required by upstream Cautilus
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

Status:

- No-write seam landed on the Charness side as
  `python3 skills/public/find-skills/scripts/list_capabilities.py --read-only`,
  documented in [skills/public/find-skills/SKILL.md](../../skills/public/find-skills/SKILL.md)
  Bootstrap. The flag emits the inventory payload to stdout, sets
  `artifacts.mode = "read-only"`, and skips the durable artifact write so a
  read-only sandbox can still complete the routing decision. Default behaviour
  is unchanged; callers must opt in.
- Workspace-write workflow proof carrier is still a follow-up. The next slice
  should pick a dogfood that runs the agent in `--sandbox workspace-write` and
  proves the durable artifact and any related state-cache writes complete
  cleanly. Routing-side wiring of the new flag waits until the Cautilus adapter
  is re-enabled and the upstream eval runner is stable.

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
- `setup` updates `AGENTS.md` and related settings
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

1. `readme-quickstart-loads-setup`
   - prompt: `Use charness to initialize this repo.`
   - expected route: `find-skills -> setup`
   - README promise: Quick Start says the agent loads `charness:setup`
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
- `setup-partial-normalize-not-template`: mature partial repo is normalized
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
