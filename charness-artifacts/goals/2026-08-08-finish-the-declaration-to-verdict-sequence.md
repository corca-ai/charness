# Achieve Goal: Finish the declaration-to-verdict sequence at its consumers

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-finish-the-declaration-to-verdict-sequence.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed.
- Next action: activate after confirming the predecessor's seam is still the one
  you want slices 3 and 4 built on.
- Verification cadence: cheap deterministic checks at commit boundaries;
  bounded fresh-eye proof at slice boundaries; broad/live proof at closeout.
- Gate cadence: `run_slice_closeout.py --skip-broad-pytest` per slice, and
  `./scripts/run-quality.sh --read-only` at every slice boundary — the
  predecessor learned that one the hard way; see Boundaries.
- Slice review packet: intent, changed files and owning/generated surfaces,
  expected invariants, tests/proof, non-claims, out-of-scope lines, questions.
- History boundary: keep this frame current; completed detail moves to
  `## Slice Log`.

## Goal

The predecessor
(`charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`)
repaired the ROOT and shipped it as v3.5.0. An adapter can no longer declare a
`version` no reader speaks, and a declared key now resolves to a named reader or
a typed gap, scoped to the file it was declared in.

It stopped after slice 2. Slices 3, 4 and 5 remain, and they are the CONSUMER
half of the same question — the half the root repair exists to make possible.

1. **Surface reconciliation (`#518`).** Every declared quality surface resolves
   to an executable reader or a typed gap; no declared-but-unreached surface
   renders as `clean`. This is now expressible because `adapter_key_registry`
   can resolve a declaration to a reader.
2. **Absence (`#528`).** A repo declares a sub-key ABSENT and the resolver
   honors it. Needs `declared` / `defaulted` / `absent` as three distinguishable
   states.
3. **Bundle proof and closeout.** Composition can drop what each slice proved
   alone.

## Non-Goals

- Do not arm a warn or refuse tier on `adapter_key_registry` without an explicit
  operator decision. It reports today, deliberately. D46's reasoning stands: the
  population that matters is consumer adapters this repo has never seen.
- Do not widen `associated_modules` to make a `reader-elsewhere` go away. The
  predecessor measured that trade twice; widening is how the verdict stops
  meaning anything.
- No release, tag, version bump, or Cautilus run unless separately granted.

## Boundaries

- **Premise check is a phase, not a step.** It paid off 3 for 3 in the
  predecessor INCLUDING when the premise held — it found `version: true` accepted
  at every site, and it caught that the obvious `#553` remedy would have inverted
  the bias before a line was written.
- **A slice that changes verdict logic owes round-1 AND round-2 bounded review.**
  Measured again: round 1's fix left the setup template writing a model id its
  own repaired checker flags, and the `#553` fix conferred association by module
  basename — the same collision defect one level up. Both were caught only by the
  round that read the REPAIRS.
- **Widening a scope to avoid false positives ships with a measured UPPER bound
  in the same commit.** This is the predecessor's single most transferable
  lesson. Every seed in the key registry was justified by a measurement of
  under-reporting and none by over-reporting, and that asymmetry is exactly how
  the defect recurred.
- **Run `./scripts/run-quality.sh --read-only` at each slice boundary, not just
  at the end.** In the predecessor it failed on first run and named four real
  defects — orphaned dead code, two unreachable branches, three uncovered verdict
  paths — none of which the test suite or two review rounds had surfaced.
- **Measure the whole population after every change, not just the fixture.** All
  three intermediate defects in the `#553` repair were invisible from the fixture
  and obvious from the population.
- Bounded reviewers run read-only in the shared worktree, fingerprinted
  snapshot/verify around every review, and the window is CLOSED before the parent
  starts repairing.

## User Acceptance

- Every quality surface the adapter declares resolves to an executable reader or
  a typed gap; no declared-but-unreached surface renders as `clean`.
- A repo can declare a sub-key ABSENT and the resolver honors it, distinguishably
  from `defaulted`.
- Every slice is proven green at the cadence `## Active Operating Frame` states.
  This line names no command and no boundary frequency on purpose; the frame owns that.
- The Slice Log records the premise-check verdict BEFORE each build, including
  where the premise held.
- Any new verdict state ships with a measured upper bound on its own breadth.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync before validators; `check_python_lengths.py --headroom` before adding to a
  gated file; `check_dup_ratchet.py --summary` before writing the commit message.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- Mutation-check every new verdict path and report the count from a re-run. The
  predecessor had two mutants SURVIVE first and both exposed real gaps.
- Construct the refused input; never infer a refusal from a green suite.
- For any new state, construct an input that reaches it — the predecessor proved
  `unknown` was reachable rather than vestigial only by building one.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer
  AND channel than the push exit code.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE | Status |
| --- | --- | --- | --- | --- |
| 1 | Reconcile every declared quality surface to a reader or a typed gap | #518 | Expressible only now that a declaration resolves to a reader | planned |
| 2 | Let a repo declare a sub-key ABSENT and have the resolver honor it | #528 | Needs declared/defaulted/absent as three states | planned |
| 3 | Bundle proof and goal closeout, including the successor goal | (none) | Composition can drop what each slice proved alone | planned |

## Backlog Recount

- Counted: To be filled by the achieve Before-phase
- Claims: To be filled by the achieve Before-phase
- Not claimed: To be filled by the achieve Before-phase

This draft is the ONE pre-existing artifact the backlog-recount floor reaches: it is
`Status: draft` and `Created: 2026-08-08`, so it is in scope. The heading is added with
unfilled placeholders deliberately rather than back-filled with a count — the floor's
whole point is that scope gets reconciled against the tracker at shaping time, and this
goal's own `## Off-Goal Findings` already records that it was shaped WITHOUT a recount
and that a later count found 28 open issues intersecting its subject. Fill this during its
Before phase, not from here.

## Operator Decision Queue

- Decision: whether `adapter_key_registry`'s unknown/`reader-elsewhere` states
  become a WARNING for consumer repos.
  Owner: operator.
  Why deferred: the predecessor delivered the measurement and deliberately did
  not decide. `survey()` reports; nothing is armed.
  Unblock action: none outstanding — the data is in. Run
  `python3 scripts/adapter_key_registry.py --repo-root .` and decide.
  Revisit trigger: a consumer report of a silently-defaulted declaration.

## Coordination Cues

Phase-appropriate routing chosen from installed skill metadata and model
judgment. Fill during the run:

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

CONFIRMED — carried forward from the predecessor's activation, which the operator
granted and which shipped as v3.5.0.

- RESOLVED — this goal continues the predecessor's sequence at slices 3-5 and is
  measured by observable repo behavior, not by issues closed.
- RESOLVED — the warn-vs-refuse tier stays an operator decision and does not
  block activation; the measurement it needs is already delivered.
- RESOLVED — no release or push is implied by activation. Both are per-request.

## Slice Log

## Context Sources

1. `charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`
   — the predecessor. Its Slice Log is this goal's evidence base.
2. `charness-artifacts/critique/2026-08-07-issue-553-resolution-critique.md` and
   `...-release-v3.5.0-critique.md` — the two reviews that produced this goal's
   upper-bound and gate-cadence boundaries.
3. `scripts/adapter_key_registry.py` — the seam slices 1 and 2 consume.

## Interview Decisions

- Shape: continue the predecessor's sequence rather than open a new frame. Its
  ordering claim (root before consumer) was executed and held; the consumer half
  is what remains.
- The warn/refuse decision is NOT a slice here. The measurement is done; the
  decision is the operator's and blocks nothing.

## Plan Critique Findings

- Open risk, not resolved: `#518` is a large surface and the predecessor never
  scoped it. Its premise must be checked before any remedy is shaped — the
  predecessor's 3-for-3 record says the named remedy is the thing most likely to
  be wrong.
- Open risk, not resolved: `reader-elsewhere` currently includes
  under-association residue. Slice 1 consumes that seam and may need it sharper.
  Mitigation: sharpen with a measured upper bound, per this goal's boundary, or
  record why the residue is acceptable for the consumer question.

## Closeout Binding Plan

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

- `#549` (durable failure output is a habit built in one script) remains unbuilt
  and unmeasured. The predecessor's judgement stands: measure whether consumer
  hooks actually ignore the contract before building a floor.
- `#550`, `#552` were filed by the predecessor and are unclaimed here. `#551`
  was ALSO filed by it and is now closed as a duplicate of `#547` — filed 2.5
  hours earlier, same defect, same function. That is the cost of not recounting
  the backlog before filing.
- **`#530` is still OPEN and is the issue the predecessor actually spent its
  whole run fixing.** Both halves shipped in v3.5.0 and neither commit referenced
  it. It now carries a comment with the evidence. It is not closable yet: a
  typo'd key resolves to a typed state, but nothing is armed to warn on it, so
  the `valid: true, errors: []` symptom in its title is only half-answered.
  Closing needs the operator's warn/refuse decision plus the resolution-critique
  floor.
- **The backlog was NOT recounted before this goal was shaped.** It was designed
  from the predecessor's slice plan and lessons. A recount afterwards found 28
  open issues, and at least three intersect this goal's subject: `#534` (the dup
  ratchet re-blocks on already-classified families when a module split rotates
  content-addressed ids — hit and worked around during the predecessor with
  `--accept-rotation`), `#547`, and `#530` itself. Slice 1 must open by
  recounting and deciding which of the 28 this goal actually claims, rather than
  inheriting a two-issue scope that was never checked against the tracker.

## Final Verification

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
