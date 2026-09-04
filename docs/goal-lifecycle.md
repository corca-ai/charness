# Goal Lifecycle

> Status: current
> Source of truth: the `achieve` and `issue` skills' Goal Run commands and this page
> Last verified: 2026-09-04

This page answers one question: how does Charness model a long-running goal
from planning through provider-verified completion?

The issue-native Goal Run is the implemented workflow: planning, binding,
provider establishment, exact `/goal #N` pickup, child closeout, and the
guarded parent close have each run live in this repo; the recorded runs live
under `charness-artifacts/goal-runs/`. What this page does not claim: that every
installed consumer host has exercised the same path; the installed copy is what
a consumer runs, and that proof is recorded per release, not assumed here.

## Design Center

A long-running goal has two kinds of truth that should not share one mutable
document:

- planning truth is a complete local draft that becomes immutable after approval
- execution truth is the GitHub parent/sub-issue graph observed through the
  selected issue backend

The small record between them proves identity and integrity. The parent also
owns a small mutable execution cursor so a new session can enter the next child
with one read. The cursor is navigation state, not approval provenance or a
second event ledger; explicit sync/closeout remains responsible for full graph
reconciliation.

## Domain Model

| Concept | Owns | Must not own |
| --- | --- | --- |
| Goal Draft | research, decisions, critique dispositions, target architecture, approved child design, briefing | routine progress or current child state |
| Goal Binding | immutable approval identity, exact draft hash, parent identity, and initial approved work-item manifest/digest | observations, active/blocked/completion verdicts, percentages, mutable progress |
| Goal Run | shared execution scope, dependency order, completion policy, sparse contract changes | local planning history |
| Work Item | immediately executable capability contract and routine provider state | umbrella intent or unrelated integration work |
| Provider Observation | typed evidence of preflight, mutation, readback, partial outcome, or refusal | lifecycle policy or a second durable event ledger |

The Goal Run is a real GitHub parent issue. Every Work Item is a real sub-issue;
a Markdown link or checklist is not relationship proof.

## Authority By Phase

| Phase | Authority | Condition |
| --- | --- | --- |
| shaping | mutable Goal Draft | research and bounded interview are incomplete |
| reviewed | Goal Draft plus conditional docs and child specs | both critique rounds and final alignment are complete |
| approved | frozen Goal Draft | operator approved the exact briefing and initial manifest; provider may still be unavailable |
| binding | frozen Goal Draft and immutable V1 Goal Binding | exact parent identity is established or reused |
| bound | GitHub Goal Run plus verified graph | provider readback equals the approved graph exactly |
| active | fresh parent/child provider state | user invoked `/goal #N` and pickup validation passed |
| complete | provider-verified closed parent plus terminal proof | no child remains open or silently detached |

These names describe observed conditions. The binding does not carry a mutable
`phase` or `status` field.

## Planning And Approval

`achieve` first researches code, documentation, adapters, tests, tracker state,
and durable history. It accumulates one full Goal Draft and asks only questions
whose answers are consequential and not discoverable.

The adapter controls `interview.max_questions`. The ceiling is a cap, not a
quota; identity lives in [`interview_contract.py`](../skills/public/achieve/scripts/interview_contract.py).
Exhausting it with unresolved consequential ambiguity stops planning.

Before approval, the workflow runs:

1. critique of framing, ownership, and architecture
2. conditional to-be documentation and executable child drafting
3. adversarial critique of the repaired whole
4. meticulous current-to-target alignment audit
5. briefing of purpose, target structure, execution order, and proof

Only an explicit approval of that briefing permits draft freeze or provider
mutation.

## Goal Binding

Binding, parent-metadata, and observation identity live in
[`goal_binding.py`](../skills/public/achieve/scripts/goal_binding.py) and the
`issue` Goal Run helpers. The sidecar is the draft path with `.binding.json`;
the SHA-256 of the immutable V1 file is the approval anchor. A valid binding
contains no observation, progress, or copied parent body. Provider-less
planning creates no binding. Field inventories are not recopied here.

## Parent Metadata

The Goal Run body contains one machine-managed `<!-- charness-goal-run:v1` block.
`update-body` preserves that identity and cursor; provider edit history owns
reversible prose. Duplicate, malformed, or identity-mutated blocks refuse
before provider mutation. Schema identity is in [`goal_binding.py`](../skills/public/achieve/scripts/goal_binding.py).

## Activation And Pickup

The user-facing command is intentionally only:

```text
/goal #724
```

Issue-native pickup accepts only trimmed objective text matching
`^/goal[ ]+#[1-9][0-9]*$`. The host stores ordinary objective text. `achieve`
resolves the repository from an
explicit adapter identity or one unambiguous provider-compatible Git remote;
it never fabricates `<default-org>/<cwd-basename>`. It then asks the
adapter-resolved `issue` backend to read the exact `(repository, number)` and:

1. reads the parent and its managed metadata
2. reads and validates the Goal Binding and frozen Goal Draft
3. verifies parent ↔ binding ↔ draft identity
4. validates the establishment observation
5. reads the parent's managed progress cursor
6. enters the cursor's next executable child

The sidecar path is never entered by the user and no host-specific binding-file
parser is required.

The cursor is produced by bootstrap or explicit progress sync from the full
reconciler. It records an already-validated open child; pickup does not read
all child bodies or recompute dependency order. The binding retains rank and
dependency provenance for sync and closeout.

Pickup refuses with an actionable type for malformed objective, unresolved or
ambiguous repository, non-Goal-Run issue, invalid metadata, missing/mismatched
draft or binding, unestablished/invalid graph, missing/stale parent progress,
no next child, or closed parent. It never falls through to a local execution-
state fallback or a hidden full graph scan.

## Provider Operations

`issue` owns provider mechanics; `achieve` owns lifecycle policy and order.
Required operations, observation outcomes, and module seams live in the `issue`
Goal Run scripts and [issue-backend.md](../skills/public/issue/references/issue-backend.md).
Every mutation returns a typed Provider Observation. `no write` is legal only
before provider invocation. Command absence is not permission to improvise.

## Reconciliation And Recovery

Graph establishment is resumable, not transactional. Observation outcome
identity lives in the Goal Run observation schema; do not recopy the
claim/next-action table here. Create-or-reuse uses a stable Work Item key. If an
invoked create has no discoverable identity, stop; never retry create blindly.
Planning-only fallback (when the adapter allows it) creates neither parent nor
binding. After establishment the GitHub parent owns current graph membership;
the immutable binding remains the initial approved baseline.

## Execution And Closeout

Closing a child is provider progress, not behavioral proof. Only the
dedicated close operation may close the parent; it performs distinct
post-close provider readback and never re-closes an already-closed parent.
Generic update refuses to strip Goal Run metadata; generic close refuses
before any comment or provider write. Failed exact readback is `unverified`,
never completion. Partial outcomes live in the `achieve`/`issue` close helpers.

## Ownership And Portability

- `achieve`: Goal Draft/Binding producer; research/interview, critique
  orchestration, approval, graph policy/order, pickup, child selection, and
  closeout policy
- `issue`: provider identity, readiness, mutation, relationship, state, and
  guarded-close operations plus Provider Observation serialization
- Work Item capability owner: executable/verifiable child body; GitHub owns
  mutable state; implementing agent and guarded close consume it
- adapter: question ceiling, selected issue backend, repository resolution, and
  explicit planning-only fallback policy
- host: ordinary `/goal` objective persistence only
- `docs/`: evergreen vocabulary, authority, and operator path
- generated plugin placement: synchronized export of canonical skill sources,
  never an independent implementation

GitHub is an external declared capability. Local tests can prove schema,
planning, refusals, and fake-backend behavior; only provider roundtrip proves a
real graph mutation.

Legacy goal artifacts under `charness-artifacts/goals/` are planning provenance only; they are not migrated, activated, or accepted as runtime state.
