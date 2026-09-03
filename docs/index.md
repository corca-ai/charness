# Charness documentation

> Status: current
> Source of truth: this index plus the linked owning page
> Last verified: 2026-09-02

This is the flat documentation wiki. Start with the smallest page that answers
the current question. [`check-docs.sh`](../scripts/check-docs.sh) is the
composite docs receipt.

## Orientation

- [README](../README.md) — user guide for installing and using Charness.
- [Documentation principles](./documentation-principles.md) — how current docs are written.
- [Design north star](./design-north-star.md) — the governing product/workflow standard.
- [Workflow routes](./workflow-routes.md) — map intent to a public skill.
- [Goal lifecycle](./goal-lifecycle.md) — active goal ownership and continuation.
- [Development](./development.md) — local development and dogfood paths.

## Operating contracts

- [Operating contract](./operating-contract.md) — boundaries, artifacts, and closeout.
- [Implementation discipline](./implementation-discipline.md) — mutate, sync, verify, publish.
- [Worktree prepare](./worktree-prepare.md) — isolated mutation setup.
- [Agent task runs](./agent-task-runs.md) — bounded task execution.
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
- [Export boundary](./export-boundary.md) — shipped root trees and the repo-only `tools/` rule.
- [Artifact policy](./artifact-policy.md) — durable state ownership.

## Skills, quality, and proof

- [Public skill validation](./public-skill-validation.md) — validation tiers.
- [Public skill dogfood](./public-skill-dogfood.md) — consumer proof state.
- [Support skill policy](./support-skill-policy.md) — support boundary.
- [Prescribed skill closeout](./prescribed-skill-closeout-contract.md) — closeout floor.
- [Narrative and announcement boundary](./narrative-announcement-boundary.md) — story/communication split.
- [Proof semantics](./proof-semantics-adapter.md) — verdict and non-claim vocabulary.
- [Docs graph checks](./docs-graph-checks.md) — reachability evidence and limits.

## Operator and product surfaces

- [Operator acceptance](./operator-acceptance.md) — takeover checks.
- [Progressive operator path](./operator-progressive-path.md) — capability horizons.
- [CLI reference](./cli-reference.md) — generated command reference.

## Current contracts

- [Deferred decisions](./deferred-decisions.md) — open decision register.
