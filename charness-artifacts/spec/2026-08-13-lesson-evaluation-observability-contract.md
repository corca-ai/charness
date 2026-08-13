# Lesson-Evaluation Observability Contract

Status: completed
Date: 2026-08-13

## Problem

The repository can declare lesson preview sessions and append cited scores, but
it cannot answer whether every later durable retro was explicitly reconciled. A
missing start, an unproven presentation, an intentionally scoreless session,
and an entirely skipped evaluation all collapse into silence. Human promises to
“watch the next sessions” therefore have no denominator, no durable disposition,
and no independent reconciliation surface.

## Capability Contract

For every durable retro artifact in the activated cohort, an operator can run
one read-only command and see exactly one typed lesson-evaluation disposition.
That command reconciles the retro against the declared lesson session, the
bytes whose stdout write and flush returned successfully in the start command,
and any cited score events. It reports missing starts, unproven emission,
score-count mismatches, duplicate session reuse, and unclaimed emission
receipts without treating more scores as better behavior. This is
**retro-artifact continuity**, not proof that every host session was covered or
that the start action happened before the affected work.

## Entities

- `lesson session`: the existing immutable ledger snapshot selected by a unique
  `session_id`.
- `emission receipt`: a subordinate repo-local JSON binding from one ledger
  session to one renderer/version and the UTF-8 stdout bytes for which the
  command's write and flush returned successfully; it proves neither host
  delivery, display, reading, use, nor benefit.
- `retro disposition`: one structured line in a durable retro artifact. The
  disposition is the authority for whether evaluation happened; score events
  are effects recorded after it, not a proxy for the human judgment.
- `continuity report`: a read-only reconciliation over retros, ledger sessions,
  receipts, and score events.

## Stages

1. `open`: one command declares the session, writes the selected UTF-8 bytes to
   stdout, flushes them, and then atomically persists the receipt. A stdout,
   flush, or receipt-write failure leaves the declared session conservatively
   unproven and never produces a successful receipt.
2. `work`: no lifecycle mutation is required.
3. `dispose`: the retro records one of `effect-recorded`, `no-effect`, or
   `not-evaluated`.
4. `reconcile`: a read-only command computes cohort coverage and violations.

## Current Slice

- Add the repo-local start command and emission-receipt schema.
- Add one strict retro-disposition grammar, adapter-owned scaffold affordance, and
  next-day grandfathered validator floor.
- Add a read-only continuity reporter with human and JSON output.
- Route the report through the Charness retro adapter/planner and next handoff.
- Synchronize checked-in plugin exports for changed public retro surfaces.

## Fixed Decisions

- The measurable denominator is root-level durable retro artifacts whose shared
  observed date is on or after `2026-08-14`, excluding `recent-lessons.md` and
  files recognized as retro prepare packets. The observed date is the later of
  the filename date and body `Date:` value, using
  `scripts.critique_enforcement_scope.observed_date`; a disagreement cannot buy
  grandfathering. Raw host chats and undated legacy artifacts are not called
  covered work units.
- The authoritative grammar is exactly one non-placeholder line inside exactly
  one `## Lesson Evaluation` section:
  `Lesson evaluation: <JSON object>`. JSON key order and insignificant
  whitespace do not matter, but unknown keys, duplicate lines, misplaced lines,
  and non-canonical repo-relative identities are rejected.
- The disposition axis is an explicit retro judgment, not an inference from
  score volume:
  - `effect-recorded`: the author affirms evaluation and one or more matching
    score events record observed effects;
  - `no-effect`: the author affirmatively evaluated the selected lessons and
    observed no score-worthy effect; zero score events is necessary but does
    not infer this status;
  - `not-evaluated`: the author makes no evaluation claim, with reason
    `missing-start`, `emission-unproven`, or `presentation-unproven`.
- Every object carries `status`, `session_id` (`none` only for
  `missing-start`), and nonnegative integer `score_event_count`. Only
  `not-evaluated` carries `reason`. The valid-state truth table is:

  | Status | Session | Valid receipt | Matching score count |
  | --- | --- | --- | --- |
  | `effect-recorded` | declared, unique to this retro | required | `>= 1` |
  | `no-effect` | declared, unique to this retro | required | `0` |
  | `not-evaluated` / `missing-start` | literal `none` | absent | `0` |
  | `not-evaluated` / `emission-unproven` | declared, unique to this retro | absent or invalid | `0` |
  | `not-evaluated` / `presentation-unproven` | declared, unique to this retro | required | `0` |

- The reporter verifies `score_event_count` against ledger events whose
  canonical `source_retro` and `session_id` both match. One session may be named
  by exactly one retro disposition; reuse by a second retro is
  `duplicate-session-reference`. A score on a receiptless/invalid-receipt
  session is `score-without-emission-proof`, not evidence that upgrades it.
- The schema-v3 ledger remains the sole session/snapshot identity authority.
  The receipt kind/version contains only `session_id`, the ledger
  `snapshot_sha256`, `renderer_id`, `stdout_sha256`, `stdout_byte_count`, and an
  RFC 3339 `emitted_at`, plus `receipt_sha256` over those canonical fields. The
  byte digest includes the final newline. A changed
  renderer or mismatching snapshot/digest makes the receipt invalid; it never
  rewrites ledger identity. `receipt_sha256` detects accidental/incomplete
  edits only; it is not an authenticity or adversarial-tamper proof because no
  independent secret or append-only receipt digest exists.
- An `unclaimed-emission` is a valid post-activation receipt with an
  `emitted_at` calendar date earlier than the report's `--as-of` date and no
  in-cohort retro disposition. Same-day receipts are treated as in-progress.
  Pre-activation sessions and receipts do not become current-cohort orphans.
- The process-health measures are disposition coverage, missing-start count,
  emission-unproven count, score-count mismatch, duplicate-session-reference,
  presentation-unproven count, and unclaimed-emission count. Score count, sign,
  and total are not compliance
  or quality measures. The human and JSON output label the denominator as
  `eligible durable retros`.
- The start receipt is written only after stdout write and flush return. Its
  strongest claim is `stdout-write-and-flush-returned`; it cannot establish
  delivery, display, reading, use, benefit, or before-work ordering.
- New validator logic is a proof surface and receives two bounded review rounds
  if round 1 produces repairs, per the repository operating contract.

## Probe Result

- The human report keeps one compact aggregate line for eligible durable retros,
  dispositions, each missing/unproven/mismatch/duplicate/unclaimed count, and
  total score events. Typed per-artifact violation detail stays on following
  lines; `--json` exposes the same counts and full structured violations. CLI
  snapshots pin both views, including a many-score incomplete cohort versus a
  zero-score fully disposed cohort.

## Deferred Decisions

- Automatically opening a lesson session from the host `SessionStart` hook.
  That hook is context-only today, runs for non-meaningful sessions, and must
  not dirty a repo merely because a host opened a chat.
- Counting host sessions that never produce a durable retro. A future
  machine-local session-capture denominator may expose these without changing
  the checked-in repo on every session. Trigger: a repo-local observer can
  distinguish meaningful work from incidental host opens without treating chat
  count as work quality.
- Comparative score-policy tuning and generated-digest ranking changes remain
  governed by their existing evidence goal.

## Non-Goals

- Do not claim that command stdout was read, used, or beneficial.
- Do not claim that the receipt proves the command ran before affected work.
- Do not force a score merely to make the report look healthy.
- Do not mutate the lesson-ledger schema in this slice.
- Do not make a missing optional host hook block session startup.
- Do not backfill dispositions or scores for pre-activation retros.

## Deliberately Not Doing

- No `presentation_events` in the lesson ledger: the receipt is evidence about
  command emission, not lesson identity or score replay.
- No “every host session” denominator until a machine-local observer can
  distinguish meaningful work without repo writes.
- No success percentage based on evaluated sessions; `no-effect` is a complete
  disposition and `not-evaluated` is an honest visible miss.

## Constraints

- Floor-Addition Restraint: `keep` — this is a new next-day blocking retro
  floor, but the durable audit at
  `charness-artifacts/retro/2026-08-13-session-retro.md` lines 242-267 records
  that the mechanism was not continuously operated: the #615 slice produced no
  declaration or score until the audit, while prior reminder prose could not
  distinguish that skip from an honest negative disposition. The user then
  deliberately withheld a reminder to test the same decay. The scaffold
  describes the form before validation, the old corpus is grandfathered, and
  the floor checks shape only rather than judging lesson quality.
- Existing schema-v3 ledger replay and score containment remain unchanged.
- Receipt paths and identifiers are repo-relative, path-safe, and atomically
  written; raw host transcript or rendered lesson text is not stored.
- Existing retros validate unchanged. Enforcement begins the day after this
  contract lands, matching established grandfathering practice.
- The reporter exits nonzero on continuity violations and zero on a complete
  cohort; `--json` preserves structured counts and violation identifiers.

## Success Criteria

- A future retro with no disposition is refused, while the existing corpus is
  grandfathered.
- One start command writes and flushes the deterministic list and leaves a
  subordinate receipt bound to the ledger snapshot, renderer, and exact bytes;
  broken stdout or receipt persistence never creates a successful receipt.
- Valid `effect-recorded` and affirmative `no-effect` retros reconcile cleanly.
- Missing disposition, missing start, emission or presentation unproven, wrong score count,
  foreign session, duplicate session reference, score without emission proof,
  inconsistent receipt, and overdue unclaimed emission each produce distinct stable
  violation identifiers.
- An operator can distinguish “all work units disposed” from “many scores” in
  one compact report.

## Acceptance Checks

- Verification type: unit — disposition parser accepts only the exact section,
  label, three statuses, and truth-table field constraints; duplicate,
  misplaced, placeholder, unknown-key, and alternate-path forms are rejected.
- Verification type: unit — activation fixtures cover the day before, the exact
  activation day, filename/body disagreement, undated legacy exclusion, and
  pre-activation session/receipt exclusion through the shared date observer.
- Verification type: integration — start command writes ledger session + exact
  stdout receipt; byte-changing renderer, digest/snapshot tamper, broken pipe,
  and injected receipt-write failure are detected and never produce a false
  successful receipt.
- Verification type: integration — seeded retro/ledger/receipt cohorts exercise
  every status × receipt × score-count row plus missing disposition, foreign
  session/path, duplicate session reuse, receiptless scored session,
  presentation-unproven with and without a receipt, same-day
  in-progress emission, and next-day unclaimed emission; assertions pin exit
  status and stable violation IDs.
- Verification type: CLI snapshot — human output names `eligible durable
  retros`, disposition coverage, missing-start, emission-unproven, duplicate,
  mismatch, and unclaimed counts separately from total score events; JSON pins
  the same fields. A many-score/incomplete cohort does not look healthier than a
  zero-score/fully-disposed cohort.
- Verification type: specdown — the public retro core remains evaluator-generic;
  the Charness adapter-owned scaffold, validator, development guide, and handoff
  name the same grammar and non-claims.
- Verification type: e2e — canonical and exported retro planner payloads both
  expose the continuity command; no live host SessionStart proof is claimed.

## Boundary Ownership

- Producer: repo-local start command produces ledger declaration, stdout, and
  emission receipt; retro author produces the disposition.
- Consumer: continuity reporter and the next retro/handoff operator.
- Owning surface: ledger owns lesson identity/score containment, sidecar receipt
  owns stdout emission, retro owns evaluation disposition, reporter owns the
  aggregate verdict.
- Verdict: owned-correctly

## Critique

- Interrupt Source: issue-615-local-ci-verdict-divergence
- Seam Summary: local focused coverage producer versus CI broad coverage producer.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the #615 spec is completed and refreshed in this slice;
  its exact blocked historical replay and two-round review resolved the forced
  observation, while this lifecycle does not alter that verdict seam.
- What Disproving Observation Is Resolved: the repaired historical wrapper
  blocks on the exact five lines under the broad marker policy, and source/export
  parity is committed.

The pre-implementation critique is recorded at
`charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-spec-critique.md`.
Its act-before-ship findings fixed the 1:1 lifecycle, activation observer,
affirmative `no-effect` semantics, receipt boundary, and acceptance matrix
before code began.

## Canonical Artifact

This file is the living implementation contract. Tests become executable
acceptance evidence; the contract remains current if implementation learns a
different honest boundary.

## First Implementation Slice

Build the strict disposition parser and read-only reconciler against seeded
fixtures first. Then add the start receipt producer, retrofit the scaffold and
planner, synchronize exports, and run the required proof-surface reviews.
