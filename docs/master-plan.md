# charness Master Plan

`charness` is now the portable Corca harness product. Migration from earlier
repo-specific skill layouts is complete; this plan tracks the current product
boundary, operating model, and next priorities.

## Goals

1. Keep `charness` host-neutral and repo-owned.
2. Ship one coherent plugin bundle for Claude and Codex from shared artifacts.
3. Keep public skills, support skills, profiles, presets, and integrations
   cleanly separated.
4. Prefer deterministic repo-owned validation for structure and bootstrap, and
   add deeper evaluation only where the semantic drift cost justifies it.
5. Make downstream consumption explicit through adapters, presets, packaging,
   and install surfaces rather than hidden local conventions.

## Fixed Decisions

- `quality` is one public skill.
- `hitl` stays a collaboration-layer public skill.
- `retro` stays one public skill with modes rather than split skills.
- `narrative` is the public skill for source-of-truth alignment plus
  audience-facing briefs.
- `announcement` stays the delivery-facing communication skill and is not the
  home for document-alignment logic.
- external binaries should not be vendored into `charness` when they already
  have their own upstream repo or clear product boundary.
- if an external tool repo already ships a support skill, prefer consuming that
  upstream surface through an integration manifest and sync/update flow.
- support-owned runtime helpers that `charness` expects consumers to use
  directly should live in `skills/support/`, not as implied plugin dependencies.
- Claude and Codex install surfaces should be generated from shared repo
  artifacts rather than maintained as two independent trees.
- `charness` should assume isolated agent runtimes are normal, so capability
  grants, authenticated binaries, and explicit readiness checks are preferred
  over direct secret-file assumptions.

## Current Taxonomy

### Public Skills

- `gather`
- `ideation`
- `spec`
- `impl`
- `debug`
- `retro`
- `quality`
- `narrative`
- `announcement`
- `handoff`
- `hitl`
- `create-skill`
- `find-skills`
- `release`

### Support Skills

- `gather-slack`
- `gather-notion`
- generated upstream support references only when needed as maintainer-local
  machine state, not as shipped public install surface

### Profiles

- `constitutional`
- `collaboration`
- `engineering-quality`
- `meta-builder`

### External Integrations

- `agent-browser`
- `specdown`
- `crill`
- `cautilus`
- `gws-cli`

## Current Product Boundary

### Source of Truth

- shared packaging manifest: `packaging/charness.json`
- checked-in plugin bundle: `plugins/charness/`
- root marketplace pointers:
  - `.claude-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
- canonical repo quality gate: `./scripts/run-quality.sh`

### Plugin Install Model

- the repo installs as one plugin bundle
- public skills are flattened for host discovery under `plugins/charness/skills`
- support assets ship alongside them under `plugins/charness/support`
- host-specific manifests are generated from shared packaging metadata

### Validation Model

- deterministic repo-owned validation is the baseline for every shipped surface
- `public-skill-validation.md` defines which public skills are
  `HITL recommended` versus `evaluator-required`
- maintained evaluator scenarios now flow through `cautilus`, not a legacy
  internal evaluator id

## Current Priorities

### 1. Fresh-Machine Install Proof

Confirm the shipped bundle is discoverable and usable as a real plugin install
surface on Claude and Codex, not only as a local checkout with helper symlinks.

### 2. Maintained Evaluator Wiring

Turn the current `cautilus` contract from smoke coverage into maintained
scenario coverage for the `evaluator-required` public skills.

### 3. Support Runtime Maturity

Keep tightening support-owned provider runtimes, readiness probes, and
installed-surface helper behavior so shipped support assets behave the same in
source checkout and installed plugin contexts.

### 4. Downstream Preset Reality

Exercise the first real downstream organization-scoped preset and keep the
preset contract honest before hidden host policy creeps back into public skill
bodies.

## Near-Term Exit Criteria

- Claude and Codex both discover the shipped plugin bundle from the intended
  install surface.
- at least one maintained `cautilus` scenario exists for an
  `evaluator-required` skill
- support-owned runtimes prove they work from the installed plugin tree, not
  only from the source repo
- repo docs no longer depend on legacy migration names or retired skill ids
