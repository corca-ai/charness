# Issue-Native Achieve Planning And Approval Contract

> Status: draft dogfood contract
> Source of truth: operator-confirmed decisions in the active goal

This contract governs the current dogfood run before any implementation is
authorized. It preserves design work locally, uses critique to improve the
target system, and places the implementation decision after a complete briefing.

## Lifecycle

### 1. Research

Inspect current code, domain concepts, architecture, docs, adapters, tests,
tracker history, and prior decisions. Separate verified facts, assumptions,
problems, and choices. Do not ask questions whose answers are discoverable.

### 2. Accumulate The Full Goal Draft

Maintain one full local draft covering the current system, target system,
boundaries, decisions, verification, docs impact, and candidate child graph.
After approval preserve it as the planning snapshot; do not replace it with a
minimal receipt or use it as the execution progress log.

### 3. Bounded Decision Interview

Resolve `interview.max_questions` from the adapter, default 15. The ceiling
covers substantive questions across initial shaping and both critique rounds.
Ask dependency-ordered questions with options, option-specific tradeoffs, a
recommendation, and a reason. Stop early when consequential ambiguity is gone.
If the cap is exhausted first, stop planning rather than silently choosing.

### 4. Critique Round 1

Review problem framing, diagnosis, domain model, ownership, architecture,
compatibility pressure, and user value. Use distinct fresh-eye angles plus a
counterweight pass. Apply obvious findings; send consequential choices to the
bounded decision queue.

### 5. To-Be Docs And Child Specs

Write conditional to-be docs that describe concepts, responsibilities,
dependencies, state transitions, cutover/removal, recovery, and closeout. Draft each
child as an independently executable and verifiable capability spec. The graph
must compose into the documented architecture.

### 6. Critique And Adversarial Verification Round 2

Review the repaired goal, to-be docs, proposed child graph, and transition plan
together. Vary failure axes such as unavailable providers, stale identities,
partial mutations, fallback, deferral, closeout, legacy-path removal, and installed
layout. Verify that round-1 repairs did not carry the same defect class.

### 7. Final Alignment Audit

Compare current system, target system, goal, docs, and every child. Judge
conceptual coherence, ownership, dependency direction, removal of accidental
seams, graph completeness, and cold-reader legibility. Size of the delta is not
the criterion. Any consequential ambiguity returns to the decision queue.

### 8. Operator Briefing

Explain the purpose, current failure, target model/architecture, why it is more
coherent, cutover/removal, child order, proof, risks, non-goals, non-claims, and
question-budget state. Ask explicitly whether to finalize/reconcile GitHub and
begin implementation.

### 9. Approval Gate

Without an explicit yes, stop in reviewed-planning state. Do not create or
restructure the final GitHub graph, implement, commit, push, or close issues.

### 10. Freeze And Establish The Tracker

After approval, retain the full draft and create or reconcile one GitHub parent
plus every known independently closable child. Use real provider sub-issue
relationships and exact readback. Existing provisional objects are inputs to
reconciliation, not automatic authority.

### 11. Execute Through Children

One agent updates the parent by default. Child state carries routine progress;
the parent body changes only when shared intent, scope, policy, dependency, or
completion semantics change. Add later concrete independent discoveries lazily.

### 12. Complete The System

Prove each child, reconcile conditional docs to the built current system, and
run final whole-system/fresh-eye closeout. A parent cannot close with linked open
children. Move a genuinely deferred child to a successor parent with reason,
then verify the parent close through the provider.

## Obvious Versus Consequential Findings

An obvious finding follows directly from verified facts and settled principles,
is reversible, and introduces no new tradeoff. Apply it and record the reason.

A consequential finding changes scope, domain concepts, ownership, architecture,
compatibility, external effects, proof level, or completion semantics. Present
options, tradeoffs, a recommendation, and the recommendation reason to the
operator before proceeding.

## Draft, Docs, And GitHub Roles

- Full local goal: planning and decision snapshot.
- Goal Binding sidecar: wholly immutable approval/draft/parent/initial-graph
  integrity evidence; never the user-facing `/goal` target, an observation
  attachment point, or an execution-state mirror.
- Provider observations: separate immutable attempt/readback evidence referenced
  by parent metadata; never a second progress ledger.
- `docs/`: conditional target-system description before approval; honest
  current-system description at completion.
- GitHub parent: approved execution contract and sparse shared changes.
- GitHub children: independently executable/verifiable work and routine state.
- Provider readback: relationship and mutation evidence, never inferred from
  Markdown links.

After approval the user activates the run as `/goal #<parent-number>`.
`achieve` resolves the number in the current repository through `issue`, reads
the parent, validates its Goal Draft/Goal Binding pointers and current verified
membership, then selects only an executable fresh-premise child before work.

## Current Dogfood Exception

The active run already has provisional parent #724, children #725–#727, linked
backlog issues, and uncommitted prototype code. Preserve them without further
mutation during planning. Treat them as evidence to critique, not as approval or
the target architecture.

After briefing approval only, the already-linked provider child #726 implements
and locally proves the minimum graph primitives needed to escape the self-hosting
cycle. Those primitives reconcile the full approved #724 graph and record a
visible `pending-target-roundtrip` bootstrap observation. GitHub then owns
routine progress, but generic `/goal #724` pickup remains blocked. After all
four system capabilities are complete, their target command surface re-verifies
the same graph and replaces the bootstrap marker with verified establishment.
No other run, child, adapter, or fallback inherits this one-time exception.
