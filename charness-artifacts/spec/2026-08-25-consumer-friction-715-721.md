# Consumer Friction 715–721 — Implementation Contract

Date: 2026-08-25
Status: implementation in progress

## Problem

External workers and proof surfaces can produce a plausible result without a
verifiable join between the selected implementation, the mutable owner, the
review substrate, the delivery attempt, and the artifact producer. Issues
#715–#721 are instances of that same boundary failure.

## Current Slice

Build a shared, typed execution-provenance contract and repair the seven
consumer-friction boundaries without changing the approval owner or silently
weakening an existing gate.

The existing task/worker envelope remains the durable owner. No parallel
global lane or second reviewer ledger is introduced.

## Fixed Decisions

- A reported or installed skill path is admissible only after version and
  content identity are checked against the current source/plugin expectation.
- Uncommitted review inputs default to a working-tree substrate. Historical
  refs/ranges must be explicit and must match the reviewed path set.
- The parent task owns global lesson-session and delivery-ledger mutation;
  workers write lane-local receipts and findings only.
- Retry is a state transition, not a generic rerun. Active attempts, foreign
  predecessors, and incoherent retry counts are refused.
- Canonical producers own artifact shape. Broad validators remain consumers
  and auditors, not authoring interfaces.
- Duplicate-family fingerprint rotation proposes a rebind; it never silently
  transfers prior judgment.
- Source and packaged/plugin copies must remain byte-identical where the repo
  packaging contract requires parity.

## Probe Questions

- Which existing task envelope fields can carry the run identity without
  creating a second durable state model?
- Which host-observed facts can the Ceal Codex/Claude wrappers provide, and
  which selection facts must be verified by Charness at runtime?
- Can each repaired proof surface expose a representative changed/new input
  through its final consumer rather than only through helper tests?

## Deferred Decisions

- Live credential, network, provider, Cautilus, installed-machine, push,
  release, and GitHub mutation proof.
- A host-attested freshness window beyond same-attempt ordering.
- Automatic semantic duplicate-family rebind without explicit disposition.

## Non-Goals

- Reopening or changing the already closed issues #689, #690, #691, #713, or
  #714.
- Replacing `../ceal` launch mechanics or embedding absolute host paths in the
  repository.
- Treating a retry, a green doctor result, or a source-only test as consumer
  adoption proof.

## Success Criteria

1. A stale, missing, or same-version-but-different skill is refused before the
   worker action, with a typed recovery instruction and an observable identity
   record.
2. A critique packet cannot claim `current` when its declared substrate and
   reviewed paths refer to different inputs.
3. Parallel workers cannot mutate the parent lesson ledger or parent delivery
   state directly.
4. Invalid reviewer retry lineage and invalid/tampered receipts remain
   recoverable without terminalizing a false success.
5. Goal closeout parsing and debug artifact authoring have one typed producer
   each, consumed by their existing validators.
6. Duplicate-family rotation is represented as an explicit proposal and the
   mixed replay distinguishes rotation, membership change, and genuine new
   duplication.

## Acceptance Checks

- Focused regression tests for each issue and adversarial negative cases.
- Source/plugin parity checks for every affected packaged surface.
- One final-consumer execution for skill selection, packet verification,
  delivery collection, goal validation, debug indexing, and duplicate ratchet.
- `bash .githooks/pre-commit`, targeted changed-line proof where available,
  and the strongest applicable quality gate.
- A fresh-eye review for each proof-surface or irreversible-boundary change;
  verdict-logic repairs receive the required second round.
- Closeout records retain explicit non-claims for unavailable host/provider
  proof.

## Slice Ownership

- Lane A: #715 + #718 (skill admission and packet substrate).
- Lane B: #716 + #719 (parent ownership and delivery retry lineage).
- Lane C: #717 + #721 (typed proof-surface producers).
- Parent integration: #720, cross-lane provenance join, final consumer proof,
  and closeout reconciliation.
