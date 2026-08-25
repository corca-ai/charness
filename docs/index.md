# Charness Documentation Index

> Status: current
> Source of truth: this index plus the linked owning page
> Last verified: 2026-08-25

This is the canonical entry point for Charness's flat documentation wiki. Each
page owns one question. New evergreen pages are flat under `docs/`; nested
directories are legacy or generated surfaces and are not moved implicitly.
Reachability is checked by `check_docs_graph.py`; link resolution is checked by
`check_doc_links.py`; neither alone proves factual freshness.

## Start Here

- [Design north star](./design-north-star.md) — governing design standard.
- [Harness composition](./harness-composition.md) — boundary map.
- [Workflow routes](./workflow-routes.md) — intent-to-skill routing.
- [Live handoff](./handoff.md) — current continuation state.
- [Development](./development.md) — repo-local development paths.
- [Compatibility index: docs/README.md](./README.md) — legacy pointer.

## Operating Contract

- [Operating contract](./conventions/operating-contract.md) — irreversible-boundary rules.
- [Implementation discipline](./conventions/implementation-discipline.md) — mutate/sync/verify order.
- [Parallel execution](./conventions/parallel-execution.md) — fan-out proof floor.
- [Authoring preflight](./conventions/authoring-preflight.md) — pre-edit constraints.
- [Validator timing layers](./conventions/validator-timing-layers.md) — gate placement.
- [Surface-driven adapter triggers](./conventions/surface-driven-adapter-triggers.md) — ownership routing.
- [Provenance placement](./conventions/provenance-placement.md) — rule/history separation.
- [Worktree prepare](./worktree-prepare.md) — isolated mutation paths.

## Architecture And Runtime

- [Control plane](./control-plane.md) — tool lifecycle and declaration.
- [Runtime capability contract](./runtime-capability-contract.md) — external access state.
- [Capability resolution](./capability-resolution.md) — repo-local capability facts.
- [External integrations](./external-integrations.md) — provider boundary.
- [Gather provider ownership](./gather-provider-ownership.md) — public/credentialed split.
- [Agent task envelope](./agent-task-envelope.md) — agent handoff contract.
- [Host packaging](./host-packaging.md) — exported install surface.
- [Artifact policy](./artifact-policy.md) — durable state ownership.

## Skills, Quality, And Proof

- [Public skill validation](./public-skill-validation.md) — validation tiers.
- [Public skill dogfood](./public-skill-dogfood.md) — consumer proof state.
- [Support skill policy](./support-skill-policy.md) — support boundary.
- [Prescribed skill closeout](./prescribed-skill-closeout-contract.md) — closeout floor.
- [Narrative and announcement boundary](./narrative-announcement-boundary.md) — story/communication split.
- [Proof semantics](./proof-semantics-adapter.md) — residual/disposition vocabulary.
- [README proof ledger](./readme-proof.md) — claim evidence.
- [Duplicate detection](./duplicate-detection-strategy.md) — ratchet posture.
- [Docs graph checks](./docs-graph-checks.md) — graph evidence limits.
- [Prompt mutation policy](./prompt-mutation-policy.md) — prompt pipeline owner.

## Operator And Product Surfaces

- [Operator acceptance](./operator-acceptance.md) — takeover checks.
- [Progressive operator path](./operator-progressive-path.md) — capability horizons.
- [Product success metrics](./product-success-metrics.md) — success baseline.
- [CLI reference (generated)](./generated/cli-reference.md) — producer-owned command output.

## Living Records

These pages are active plans or working records. When they stop being current,
move their durable rationale to `charness-artifacts/` and leave a pointer here.

- [Deferred decisions](./deferred-decisions.md) — current closure register.
- [North-star overhaul roadmap](./north-star-overhaul-roadmap.md) — active plan of record.
- [Evergreen documentation architecture](../charness-artifacts/spec/2026-08-25-docs-architecture-evergreen.md) — current classification and migration contract.
- [Support tool follow-up](./support-tool-followup.md) — active support workstream.
- [Testability DSL initiative](./testability-dsl-initiative.md) — quality work record.
- [Retro self-improvement](./retro-self-improvement-spec.md) — memory design.
- [Handoff chunked routing](./handoff-chunked-routing.md) — routing contract.
- [AI/ML engineering patterns](./ai-ml-engineering-patterns.md) — engineering research.

## Compatibility And Status

The [docs/README.md](./README.md) file is a compatibility pointer, not a second index. `handoff.md`
is live session state. `generated/` is producer-owned output. Historical
evidence and superseded plans belong under `charness-artifacts/`.
