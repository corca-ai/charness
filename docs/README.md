# Charness Docs Index

Every page under `docs/` reachable from one place, grouped by the question it
answers. This exists because the tree had no entry point: seven pages were
reachable only by already knowing their filename, which is how a doc stops being
read without anyone deciding to retire it.

Each entry says what its page OWNS, so you can pick the one surface that decides
your question instead of opening four that mention it.

## Start Here

- [Design north star](./design-north-star.md) — the governing standard every
  other page defers to: brief a capable judge, keep teeth only where a wrong
  answer escapes. When a doc below conflicts with it, it is the doc that is wrong.
- [Harness composition](./harness-composition.md) — the short boundary map of how
  repo-owned surfaces, skills, and adapters fit together. Read it before adding a
  surface, to find out whether one already owns your concern.
- [Handoff](./handoff.md) — the live continuation pointer. It names the next
  pickup and nothing else; it is state, not history.
- [Workflow routes](./workflow-routes.md) — the route and procedure examples that
  would make the README too long, kept where they can be followed step by step.

## Working In This Repo

- [Operating contract](./conventions/operating-contract.md) — commit discipline,
  session rules, artifact inclusion, and the mandatory critique closeout.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  mutate/sync/verify order, generated surfaces, and change discipline that a code
  change has to satisfy.
- [Authoring preflight](./conventions/authoring-preflight.md) — how to learn a
  gated surface's constraints BEFORE authoring into it, rather than by failing one
  gate at a time.
- [Validator timing layers](./conventions/validator-timing-layers.md) — why one
  portable validator runs at several cheap timings, and how to place a new one.
- See [surface-driven adapter triggers](./conventions/surface-driven-adapter-triggers.md)
  for how a skill decides whether the current change touched a surface it cares
  about, without each skill inventing its own answer.
- [Provenance placement](./conventions/provenance-placement.md) — where the
  timeless rule goes and where the story of why it exists goes, so contracts stay
  readable as contracts.
- [Development paths](./development.md) — the development-only and proof-only
  flows, kept out of the operator-facing surfaces.
- [Worktree prepare, doctor, and audit](./worktree-prepare.md) — the five
  subcommands that keep mutate-phase work honest.

## Architecture And Control Plane

- [Control plane contract](./control-plane.md) — how external tools are declared,
  detected, and reported on.
- [Runtime capability contract](./runtime-capability-contract.md) — how charness
  reasons about external access it may or may not have at runtime.
- [Capability resolution](./capability-resolution.md) — how a repo says which
  capabilities it has locally, instead of every skill guessing.
- [External integrations policy](./external-integrations.md) — the boundary for
  integrations and provider-specific capability surfaces.
- [Gather provider ownership](./gather-provider-ownership.md) — which side of the
  public/credentialed line each gather provider sits on.
- [Agent task envelope](./agent-task-envelope.md) — the small repo-local contract
  for work passed between agents, or from an agent back to an operator.
- [Host packaging contract](./host-packaging.md) — how the harness is exported to
  a host, and what a consuming repo actually receives.
- [Artifact policy](./artifact-policy.md) — where each kind of durable artifact
  lives, and which of them are repo state.

## Skills, Validation, And Proof

- [Public skill validation tiers](./public-skill-validation.md) — the
  deeper-validation policy for public skills, and what each tier proves.
- [Public skill dogfood](./public-skill-dogfood.md) — the consumer-dogfood state,
  and where its machine-readable source lives.
- [Support skill policy](./support-skill-policy.md) — when a support skill is the
  right shape and when it is not.
- The [prescribed skill closeout contract](./prescribed-skill-closeout-contract.md)
  names the closeout floors a prescribed skill path must satisfy before it may
  claim it finished.
- The [narrative and announcement boundary](./narrative-announcement-boundary.md)
  splits the durable narrative from the human-facing announcement, after the two
  drifted into each other.
- [Proof-semantics adapter](./proof-semantics-adapter.md) — the portable
  residual/disposition ledger and the vocabulary its verdicts use.
- [README proof ledger](./readme-proof.md) — every reader-facing README claim
  mapped to the proof that backs it, so a marketing sentence cannot outrun its
  evidence.
- [Duplicate detection strategy](./duplicate-detection-strategy.md) — the intended
  posture for duplicate detection, and what its baselines do and do not assert.
- [Docs graph checks](./docs-graph-checks.md) — a measured matrix of which
  question `check_doc_links.py` answers and which one `awiki lint` answers, since
  neither is a superset of the other and the gap between them hid seven orphans.
- [Prompt mutation policy](./prompt-mutation-policy.md) — the owner surface for
  the prompt-mutation pipeline and what its verdicts mean.

## Operator Surfaces

- [Operator acceptance](./operator-acceptance.md) — the roadmap translated into
  acceptance runs an operator owns and can execute.
- [Progressive operator path](./operator-progressive-path.md) — the capability a
  repo expects at each horizon, each item grounded in an observed source.
- [Product success criteria and metrics](./product-success-metrics.md) — the
  success baseline the current product decisions were made against.
- [CLI reference](./generated/cli-reference.md) — generated from the CLI's own
  help output; edit the CLI, not this page.

## Living Records

These are working records rather than contracts: they carry decisions in flight,
and they go stale on purpose rather than being maintained forever.

- [Deferred decisions](./deferred-decisions.md) — the canonical closure surface
  for deferred product-boundary decisions. Check here before re-litigating one.
- [North-star overhaul roadmap](./north-star-overhaul-roadmap.md) — the plan of
  record for realigning the harness to the north star.
- [Support tool follow-up](./support-tool-followup.md) — the workstream that
  follows the support-skill work.
- [Testability and test-DSL initiative](./testability-dsl-initiative.md) — the
  working record of the test-quality effort.
- [Retro self-improvement spec](./retro-self-improvement-spec.md) — how durable
  retrospective memory should stop depending on explicit human upkeep.
- [Handoff chunked routing](./handoff-chunked-routing.md) — the implementation
  contract for the handoff chunker, including its declared trigger rule.
- [AI/ML engineering patterns](./ai-ml-engineering-patterns.md) — the researched
  investigation behind the engineering patterns this repo adopted.
