# Charness documentation

> Status: current
> Source of truth: this index plus the linked owning page
> Last verified: 2026-08-27

This is the flat documentation wiki. Start with the smallest page that answers
the current question; dated evidence, proposals, and retrospectives belong in
[`charness-artifacts/`](../charness-artifacts/). [`check-docs.sh`](../scripts/check-docs.sh)
is the composite docs receipt.

## Orientation

- [Documentation principles](./documentation-principles.md) — how current docs are written.
- [Design north star](./design-north-star.md) — the governing product/workflow standard.
- [Workflow routes](./workflow-routes.md) — map intent to a public skill.
- [Goal lifecycle](./goal-lifecycle.md) — active goal ownership and continuation.
- [Development](./development.md) — local development and dogfood paths.
- [docs/README.md](./README.md) — compatibility pointer for old links.

## Operating contracts

- [Operating contract](./operating-contract.md) — boundaries, artifacts, and closeout.
- [Implementation discipline](./implementation-discipline.md) — mutate, sync, verify, publish.
- [Worktree prepare](./worktree-prepare.md) — isolated mutation setup.
- [Agent task envelope](./agent-task-envelope.md) — bounded task execution.
- [Parallel execution](./parallel-execution.md) — fan-out and shared-state rules.
- [Authoring preflight](./authoring-preflight.md) — checks before editing contracts.
- [Validator timing layers](./validator-timing-layers.md) — where checks belong.
- [Surface-driven adapter triggers](./surface-driven-adapter-triggers.md) — ownership routing.
- [Provenance placement](./provenance-placement.md) — current rule versus history.

## Architecture and runtime

- [Harness composition](./harness-composition.md) — component boundaries.
- [Control plane](./control-plane.md) — tool lifecycle and declaration.
- [Runtime capability contract](./runtime-capability-contract.md) — external access state.
- [Capability resolution](./capability-resolution.md) — repo-local capability facts.
- [External integrations](./external-integrations.md) — provider boundary.
- [Gather provider ownership](./gather-provider-ownership.md) — public/credentialed split.
- [Host packaging](./host-packaging.md) — exported install layout.
- [Artifact policy](./artifact-policy.md) — durable state ownership.

## Skills, quality, and proof

- [Public skill validation](./public-skill-validation.md) — validation tiers.
- [Public skill dogfood](./public-skill-dogfood.md) — consumer proof state.
- [Support skill policy](./support-skill-policy.md) — support boundary.
- [Prescribed skill closeout](./prescribed-skill-closeout-contract.md) — closeout floor.
- [Narrative and announcement boundary](./narrative-announcement-boundary.md) — story/communication split.
- [Proof semantics](./proof-semantics-adapter.md) — verdict and non-claim vocabulary.
- [README proof ledger](./readme-proof.md) — claim evidence.
- [Duplicate detection](./duplicate-detection-strategy.md) — duplication checks.
- [Docs graph checks](./docs-graph-checks.md) — reachability evidence and limits.
- [Prompt mutation policy](./prompt-mutation-policy.md) — prompt pipeline owner.

## Operator and product surfaces

- [Operator acceptance](./operator-acceptance.md) — takeover checks.
- [Progressive operator path](./operator-progressive-path.md) — capability horizons.
- [CLI reference](./cli-reference.md) — generated command reference.

## Current records

- [Deferred decisions](./deferred-decisions.md) — open decision register.
- [North-star overhaul roadmap](./north-star-overhaul-roadmap.md) — active roadmap.
- [Evergreen documentation architecture](../charness-artifacts/spec/2026-08-25-docs-architecture-evergreen.md) — migration contract.
- [Support tool follow-up](./support-tool-followup.md) — support workstream.
- [Testability DSL initiative](./testability-dsl-initiative.md) — quality work record.
- [Retro self-improvement](./retro-self-improvement-spec.md) — memory design.
- [AI/ML engineering patterns](./ai-ml-engineering-patterns.md) — engineering research.
