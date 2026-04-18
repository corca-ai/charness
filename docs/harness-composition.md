# Harness Composition

This document is the short boundary map for how `charness` composes repo-owned
guidance. It does not replace the owning docs. It points to them.

## Scope

This document explains `charness`-local composition only:

- which repo surface owns which kind of rule
- which repo-owned surface wins when two local surfaces disagree
- how a turn should assemble repo context before acting

Out of scope:

- host-runtime system/developer/user message precedence
- model-provider behavior outside this repo
- detailed policy text already owned by a more specific doc

## Surface Ownership

### Public Skill Core

Surface:

- `skills/public/<skill-id>/SKILL.md`

Owns:

- when the skill should be selected
- the main workflow sequence
- output shape
- user-facing guardrails

Does not own:

- repo-local file paths
- long edge-case catalogs
- host-specific setup details
- deterministic enforcement logic

Authoritative detail lives in:

- skill references under `skills/public/<skill-id>/references/`
- repo policy docs such as [runtime-capability-contract.md](runtime-capability-contract.md),
  [external-integrations.md](external-integrations.md), and
  [deferred-decisions.md](deferred-decisions.md)
- repo-local adapters under `.agents/`

### References

Surface:

- `skills/public/<skill-id>/references/*.md`
- `skills/support/<skill-id>/references/*.md`

Owns:

- nuance
- examples
- edge handling
- deeper rationale

Does not own:

- the trigger contract
- repo-local path or bootstrap choices
- silent expansion of the public workflow

Authoritative detail lives in:

- the matching `SKILL.md` for selection and workflow
- repo docs when the rule is cross-skill or repo-wide

### Repo Policy Docs

Surface:

- [AGENTS.md](../AGENTS.md)
- `docs/*.md`

Owns:

- repo-wide operating stance
- source-of-truth policy
- closed decisions
- cross-skill rules
- durable documentation for future maintainers

Does not own:

- hidden machine state
- per-run evidence
- deterministic enforcement by itself

Authoritative detail lives in:

- [deferred-decisions.md](deferred-decisions.md) for closed product-boundary choices
- [runtime-capability-contract.md](runtime-capability-contract.md) for access-layer policy
- [external-integrations.md](external-integrations.md) for integration ownership
- [artifact-policy.md](artifact-policy.md) for durability classes
- [handoff.md](handoff.md) for the next-session pickup path

### Adapters

Surface:

- `.agents/*-adapter.yaml`
- adapter references under `skills/public/*/references/adapter-contract.md`

Owns:

- repo-local defaults
- artifact locations
- command groups
- bootstrap seams
- repo-specific workflow preferences that should stay machine-readable

Does not own:

- generic public-skill routing
- secret values
- broad repo philosophy

Authoritative detail lives in:

- the matching adapter-contract reference
- [artifact-policy.md](artifact-policy.md) for why a surface is visible,
  historical, or hidden

### Integration Manifests

Surface:

- `integrations/tools/*.json`
- `skills/support/*/capability.json`

Owns:

- external tool metadata
- access modes
- readiness checks
- version expectations
- support-skill provenance

Does not own:

- user-facing public skill workflow
- hidden runtime snapshots
- copied secret transport

Authoritative detail lives in:

- [external-integrations.md](external-integrations.md)
- [runtime-capability-contract.md](runtime-capability-contract.md)

### Validators and Scripts

Surface:

- `scripts/*.py`
- `./scripts/*.sh`
- `.githooks/*`

Owns:

- deterministic enforcement
- sync and bootstrap behavior
- health checks
- generated-surface regeneration

Does not own:

- high-level philosophy by itself
- durable explanation of why a rule exists

Authoritative detail lives in:

- the repo docs that explain the rule
- the adapter or manifest that records repo-local parameters

### Visible Artifacts

Surface:

- `charness-artifacts/**`
- [handoff.md](handoff.md)

Owns:

- current operator-visible state
- durable historical records when future readers should inspect a specific run
- summarized evidence that later sessions can reuse

Does not own:

- the generic skill contract
- machine-only runtime state

Authoritative detail lives in:

- [artifact-policy.md](artifact-policy.md)
- skill-specific adapter contracts for path conventions

### Hidden Runtime State

Surface:

- `.charness/**`

Owns:

- machine-local state
- resumable queues or task records
- runtime signals
- other high-churn state that should not be treated as portable repo truth

Does not own:

- user-visible policy
- the only copy of a human decision that future sessions must understand

Authoritative detail lives in:

- [artifact-policy.md](artifact-policy.md)
- [handoff.md](handoff.md) when the next maintainer needs a visible summary

## Precedence Inside `charness`

When repo-owned surfaces disagree, use this local precedence order:

1. Deterministic enforced behavior from scripts, validators, hooks, and tests
2. Checked-in repo-local adapter and manifest fields for paths, defaults, and
   integration metadata
3. Repo-wide policy docs and closed decision docs
4. Public skill core
5. References and examples
6. Prior artifacts and history

Interpretation:

- If a script or validator proves current behavior, do not let older prose win.
- If an adapter records the repo's artifact path, do not let a generic example
  override it.
- If a reference example conflicts with `SKILL.md`, fix the reference.
- If a prior artifact conflicts with fresh repo state, treat the artifact as
  history, not authority.

This order is intentionally repo-local. It does not redefine host runtime
instruction precedence outside `charness`.

## Context Assembly Order

Use this order when building context for a `charness` task:

1. Start from the user request and route to the likely public skill.
2. Read the repo-level operating context that can change the move:
   - [AGENTS.md](../AGENTS.md)
   - [handoff.md](handoff.md)
   - any obviously relevant repo policy doc
3. Resolve the repo-local adapter or manifest for the selected surface.
4. Read the current visible artifact or runtime state only if it is relevant to
   the task.
5. Pull in reference material for the chosen path.
6. Re-derive current truth from fresh repo state and command output before
   trusting prior artifacts.

The key split is:

- precedence answers which local source wins on conflict
- assembly answers what order to gather local context in before acting

## Examples

### `quality`

For a `quality` review:

1. route with [`skills/public/quality/SKILL.md`](../skills/public/quality/SKILL.md)
2. read [handoff.md](handoff.md) and current repo policy docs
3. resolve [`.agents/quality-adapter.yaml`](../.agents/quality-adapter.yaml)
4. inspect [../charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
   as history and current posture summary
5. run current gates and inventories

The quality artifact is useful context, but fresh gate output wins if the two
disagree.

### `gather`

For a `gather` task:

1. route with [`skills/public/gather/SKILL.md`](../skills/public/gather/SKILL.md)
2. resolve the gather adapter for the visible artifact path
3. use [runtime-capability-contract.md](runtime-capability-contract.md) and
   [external-integrations.md](external-integrations.md) for provider/access
   policy
4. persist the gathered result to the visible artifact

The gathered artifact records what was collected. It does not become the source
of truth for integration capability policy.

## Maintenance Rule

If this document starts repeating detailed policy that already exists
elsewhere, trim it back and link to the owning doc instead. This file should
stay an index and boundary map.
