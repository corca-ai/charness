# charness Master Plan

This plan restructures the current Ceal-centered skill set into a portable
Corca harness product, then reconnects Ceal as one consumer of that product.

## Goals

1. Create a repo-agnostic harness product with clean package boundaries.
2. Rewrite skills so they work for any host, not just Ceal.
3. Separate public concepts from support tooling and external binaries.
4. Add validation so bootstrap quality and intent do not drift silently.
5. Reapply the harness to Ceal through adapters, presets, and prompt policy.

## Fixed Decisions

- `quality` is one public skill.
- `hitl` belongs to the collaboration profile, not the constitutional core.
- `ideation` replaces and absorbs `interview`.
- `retro-session` and `retro-weekly` are `retro` modes, not separate skills.
- `gws-cli` is not a support skill.
- external binaries should not be vendored into `charness` when they already
  have their own upstream repo or clear product boundary.
- if an external tool repo already ships a support skill, prefer consuming that
  upstream skill through an integration manifest and sync/update flow.

## Target Taxonomy

### Public skills

- `gather`
- `ideation`
- `spec`
- `impl`
- `debug`
- `retro`
- `quality`
- `announcement`
- `handoff`
- `hitl`
- `create-skill`
- `find-skills`

### Support skills

- `agent-browser`
- `web-fetch`
- `specdown`
- transitional evaluation support until workbench's successor is split cleanly

### Profiles

- `constitutional`
  - `gather`
  - `ideation`
  - `spec`
  - `impl`
  - `debug`
  - `retro`
  - `handoff`
  - `create-skill`
  - `find-skills`
- `collaboration`
  - `announcement`
  - `hitl`
- `engineering-quality`
  - `quality`
- `meta-builder`
  - builder-facing presets and authoring helpers beyond the constitutional set

### External integrations

- `agent-browser`
- `specdown`
- `crill`
- future standalone evaluation engine

## Workstreams

### Workstream 1: charness product boundary

Define the repo layout, taxonomy, ownership rules, and migration targets.

Deliverables:

- root README
- taxonomy docs
- migration map from current Ceal skills
- external integration ownership policy
- repo skeleton for future content

### Workstream 2: skill body normalization

Review every migrated skill body, remove Ceal assumptions, and rewrite around
adapter-first portability.

Deliverables:

- rewritten public skills
- rewritten support skills where needed
- adapter-core and preset guidance updated in `create-skill`
- shared authoring conventions for portable first-use bootstrap

Key principle:

- host-specific behavior belongs in adapters and presets, not in skill bodies

### Workstream 3: external integration and binary promotion

Create a stable integration layer for external tools and future standalone
binaries.

Deliverables:

- tool manifests
- install/update/doctor strategy
- support-skill sync policy for upstream skill providers
- promotion plan for workbench successor and other reusable engines

### Workstream 4: harness self-validation

Verify the harness itself before Ceal consumes it.

Deliverables:

- taxonomy validator
- support integration validator
- bootstrap scenarios
- profile/preset scenarios
- intent-regression checks for representative skills
- workbench scenarios plus HITL review passes for every public skill before
  downstream adoption

### Workstream 5: Ceal consumption layer

Reapply `charness` to Ceal through adapters, presets, seeded profiles, and
system prompt references.

Deliverables:

- Ceal profile selection policy
- Ceal adapter presets
- Ceal prompt references
- Ceal-side validation runs

## Session Order

### Session 1: taxonomy and migration foundation

Goal:

- define `charness` as a product boundary
- freeze taxonomy
- define external integration policy
- produce the migration map

Deliverables:

- `README.md`
- `docs/master-plan.md`
- `docs/external-integrations.md`
- `docs/skill-migration-map.md`
- repo skeleton directories

Exit criteria:

- public/support/profile distinctions are explicit
- external binary ownership policy is explicit
- every current Ceal skill has a planned destination

### Session 2: repo skeleton and integration manifest contract

Goal:

- create the stable repo layout and metadata contracts

Deliverables:

- directory skeleton under `skills/`, `integrations/`, `profiles/`, `presets/`,
  `evals/`, `scripts/`
- integration manifest schema
- profile schema
- minimal sync/update command design doc

Exit criteria:

- future sessions can add skills and integrations without reopening boundaries

### Session 3: `create-skill` rewrite first

Goal:

- make `create-skill` the authoring contract for every later migration

Deliverables:

- portable skill authoring rules
- shared adapter-core guidance
- reasoned proposal rules
- external integration manifest rules
- sample preset conventions

Exit criteria:

- new and migrated skills have one canonical authoring standard

### Session 4: `retro` rewrite

Goal:

- rewrite `retro` into a strong portable public skill

Why early:

- `retro` is core product philosophy and currently too thin and Ceal-shaped

Deliverables:

- public `retro` skill body
- mode model for session and weekly retro
- adapter seam for host-specific artifacts and cadence

Exit criteria:

- `retro` is useful outside Ceal without hidden Ceal assumptions

### Session 5: `ideation` design and migration

Goal:

- merge `interview` plus entity-stage thinking into one public skill

Deliverables:

- new `ideation` skill
- migration notes from `interview`
- archival/deprecation plan for `interview`
- reference notes from Ceal's `entity-stage-design` skill where its durable
  entity/stage separation helps the new concept

Exit criteria:

- `ideation` stands on its own as the discovery-to-concept skill

### Session 6: `spec` design and migration

Goal:

- create the strong spec skill using `claude-plugins/clarify` as a reference,
  but with a less procedural, more portable harness style

Deliverables:

- `spec` skill
- references for success criteria, ambiguity reduction, and handoff to impl
- adapter seams for host-specific document locations

Exit criteria:

- `spec` can produce implementation-ready success criteria from either a new
  idea or a legacy codebase change request

### Session 7: `impl`, `debug`, `handoff`, `gather`

Goal:

- normalize the stable execution cluster

Deliverables:

- portable rewrites or migrations for `impl`, `debug`, `handoff`, `gather`
- cross-skill references cleaned up

Exit criteria:

- the constitutional core is portable and internally coherent

### Session 8: `quality` design and shipped samples

Goal:

- build `quality` as one public skill with proposal behavior

Deliverables:

- `quality` skill
- shipped sample presets for TypeScript and Python
- supply-chain/security references drawing on `security-audit`
- proposal flow for missing gates

Exit criteria:

- `quality` can detect current gates, identify gaps, and recommend concrete
  setups without hardcoding one repo's stack

### Session 9: collaboration layer

Goal:

- normalize `announcement` and `hitl`

Deliverables:

- portable `announcement`
- portable `hitl`
- delivery/report seams made adapter-driven

Exit criteria:

- collaboration skills are host-neutral and only specialized by adapters

### Session 10: `find-skills` and support-skill policy

Goal:

- align discovery/install flows with the new harness packaging model

Deliverables:

- `find-skills` rewrite if needed
- support-skill consumption rules
- upstream sync policy documented in repo scripts/docs

Exit criteria:

- users can discover both native public skills and external integrated tools

### Session 11: external integration manifests and sync tooling

Goal:

- implement the control plane for upstream support skills and external binaries

Deliverables:

- manifests for `agent-browser`, `specdown`, `crill`, and evaluation successor
- `sync`, `update`, and `doctor` command design or initial implementation

Exit criteria:

- integrated tools can be installed, checked, and updated consistently

### Session 12: harness self-validation

Goal:

- validate `charness` before downstream adoption

Deliverables:

- bootstrap fixtures
- profile fixtures
- external integration checks
- representative skill intent checks
- workbench scenarios for every public skill
- HITL review pass across the public skill set

Exit criteria:

- the harness can prove its own bootstrap and upgrade flows
- every public skill has at least one maintained workbench validation path

### Session 13: Ceal profile and preset application

Goal:

- make Ceal consume `charness` cleanly

Deliverables:

- Ceal profile selection
- Ceal presets and adapters
- Ceal prompt references
- Ceal install/update strategy

Exit criteria:

- Ceal customization lives in Ceal, not in shared skill bodies

### Session 14: Ceal self-validation

Goal:

- verify Ceal gets value from the new harness stack

Deliverables:

- Ceal-side scenarios for default seeded flows
- announcement and quality adapter checks
- prompt/profile verification

Exit criteria:

- Ceal can consume the shared harness without reintroducing hidden coupling

## Risks

### Risk: taxonomy churn after migration starts

Mitigation:

- freeze public/support/profile boundaries before moving content

### Risk: external tool ownership becomes ambiguous

Mitigation:

- keep binaries out of `charness`
- track them through integration manifests only

### Risk: skill rewrites stay conceptually Ceal-shaped

Mitigation:

- review every public skill against portable-first criteria
- require adapter seams for host-specific behavior

### Risk: validation arrives too late

Mitigation:

- design validation fixtures alongside integration manifests, not after them
- treat workbench scenarios as part of each public skill's finishing contract,
  not as optional cleanup

## First Session Status

Session 1 is complete when the documents named above exist and future migration
work can follow them without reopening the product boundary question.
