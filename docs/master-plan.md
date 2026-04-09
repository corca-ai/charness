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
- `charness` remains the host-neutral source of truth; Claude and Codex plugin
  layouts should be generated from shared repo artifacts instead of maintained
  as two independent trees.

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
- host-compatible packaging contract for Claude plugin and Codex plugin layouts
- generator or export path that maps shared repo artifacts into host-specific
  plugin manifests and distribution directories

### Workstream 4: harness self-validation

Verify the harness itself before Ceal consumes it.

Deliverables:

- taxonomy validator
- support integration validator
- bootstrap scenarios
- profile/preset scenarios
- intent-regression checks for representative skills
- public skill validation-tier policy
- scenario-based evaluation for `evaluator-required` public skills plus HITL
  review where the tier policy says it matters before downstream adoption
- packaging compatibility checks for host-specific plugin exports

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

### Session 9: repo dogfood review

Goal:

- run the new core skill cluster against `charness` itself before moving on

Deliverables:

- repo review pass covering lint/test/setup reality
- concept and contract review against current public skills
- security and supply-chain review notes
- follow-up fixes or issue list for discovered gaps

Exit criteria:

- `charness` has one explicit self-review pass using its own evolving workflow
- quality findings are visible before collaboration-layer work begins

### Session 10: collaboration layer

Goal:

- normalize `announcement` and `hitl`

Deliverables:

- portable `announcement`
- portable `hitl`
- delivery/report seams made adapter-driven

Exit criteria:

- collaboration skills are host-neutral and only specialized by adapters

### Session 11: `find-skills` and support-skill policy

Goal:

- align discovery/install flows with the new harness packaging model

Deliverables:

- `find-skills` rewrite if needed
- support-skill consumption rules
- upstream sync policy documented in repo scripts/docs

Exit criteria:

- users can discover both native public skills and external integrated tools

### Session 12: external integration manifests and sync tooling

Goal:

- implement the control plane for upstream support skills and external binaries

Deliverables:

- manifests for `agent-browser`, `specdown`, `crill`, and evaluation successor
- `sync`, `update`, and `doctor` command design or initial implementation
- support sync default strategy and lock-shaping contract

Exit criteria:

- integrated tools can be installed, checked, and updated consistently
- support sync behavior is explicit enough that later host packaging does not
  need to guess local wrapper or lock semantics

### Session 13: harness self-validation

Goal:

- validate `charness` before downstream adoption

Deliverables:

- bootstrap fixtures
- profile fixtures
- external integration checks
- representative skill intent checks
- public skill validation tier matrix
- scenario-based evaluation for `evaluator-required` skills
- HITL review pass for `HITL recommended` skills
- explicit next-step queue for human-only review surfaces

Exit criteria:

- the harness can prove its own bootstrap and upgrade flows
- every public skill has at least one maintained validation path that matches
  its declared tier

### Session 14: host-compatible packaging and distribution

Goal:

- make `charness` installable on Claude-style and Codex-style plugin surfaces
  without forking the source of truth

Deliverables:

- packaging contract that maps shared repo artifacts into Claude plugin and
  Codex plugin layouts
- generated plugin manifests for both hosts from one shared source
- repo or personal marketplace guidance for Codex and install guidance for
  Claude
- packaging fixtures or validation checks that prove exported layouts stay in
  sync with the neutral source

Exit criteria:

- host-specific plugin packaging is generated rather than hand-maintained
- packaging work builds on stable support/control-plane contracts instead of
  duplicating them per host

### Session 15: Ceal profile and preset application

Goal:

- make Ceal consume `charness` cleanly

Deliverables:

- Ceal profile selection
- Ceal presets and adapters
- Ceal prompt references
- Ceal install/update strategy

Exit criteria:

- Ceal customization lives in Ceal, not in shared skill bodies

### Session 16: Ceal self-validation

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
- treat tier-appropriate deeper validation as part of each public skill's
  finishing contract, not as optional cleanup

### Risk: host packaging creates a second source of truth

Mitigation:

- keep `charness` artifacts host-neutral by default
- generate Claude/Codex plugin layouts from shared manifests and skill content
- finish support-sync and lock semantics before broad host packaging work

## First Session Status

Session 1 is complete when the documents named above exist and future migration
work can follow them without reopening the product boundary question.
