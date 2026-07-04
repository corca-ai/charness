# Context-Tax Measurement Design Premortem

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Packet Consumed: `charness-artifacts/critique/2026-07-04-011351-packet.md`.
Target: `premortem-decision.md`.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- host exposure state: unsupported
- application state: host exposes `model` only; angle + counterweight
  reviewers spawned as bounded fresh-eye subagents on `sonnet` (operator
  standing instruction: lower-power models for delegated work where judgment
  allows)

## Decision

Lock the systemic context-tax measurement design
([context-tax-measurement-design.md](../reference-compaction/context-tax-measurement-design.md))
as the resolution of the reference-compaction held-open item
([intent.md](../reference-compaction/intent.md) §"Held open").

Klein Lineage Cite: first premortem for this decision; substrate lineage is the
reference-compaction critique chain (churn sweep, apparatus-floor audit).

## Capability at Stake

Whether the harness can ever detect the operator's founding symptom (systemic
dumbing) without building the measurement apparatus the intent names as the
disease. Success = a design that changes real prune/keep decisions at
near-zero standing cost; failure = a paper instrument that no-ops or bloats.

## Angles

- Michael Jackson (problem framing) — bounded fresh-eye subagent.
- Gerald Weinberg (diagnostic, current-evidence pull) — bounded fresh-eye subagent.
- Atul Gawande (checklist/operational, silent-failure hunt) — bounded fresh-eye subagent.
- Separate counterweight pass — bounded fresh-eye subagent.

## Findings

### Act Before Ship (all applied to the design before lock-in)

- Pilot success test was rigged: it conflated instrument validity with
  decision utility and named already-closed sessions, so a truthful null would
  wrongly shelve the instrument. Split into two gates + real-ledger-entry
  precondition.
- "Primary instrument" (piece 2) vs "only honest instrument" (piece 3) label
  clash and the whole-harness n=1 overreach. Rescoped: piece 2 = triage,
  piece 3 = one surface/one task, never a harness-wide verdict.
- Evidence balance omitted: one pre-effort anecdote for, two post-effort
  audits cold. Added "Current evidence, stated honestly" up top; pieces 2–3
  marked designed-in-case.
- Piece 2 assumed a full-session judge-readable transcript that no renderer
  produces (real sessions 0.5–13MB jsonl vs a 20K-char text-only renderer).
  Flagged as an open sub-problem owned by the pilot, subject to the
  anti-apparatus test.
- Piece 3 conflated two ask-before-run gates. Named the actual harness
  (`run_skill_efficiency_ab.py` + `grade_skill_outcome.py`) and its own
  judge-spend gate as separate from the cautilus contract.

### Bundle Anyway (all applied)

- Carried-artifact contamination loop (handoff/lessons written by a taxed
  session) added as a first-class citable surface; T2 "already auditable"
  claim softened to the static inventory side.
- Piece 3 trigger loosened to any contested prune/keep, however surfaced
  (matches the repo's actual escalation history).
- Symptom ledger wired: file created and seeded with the founding entry, one
  pointer sentence added to operating-contract Session Discipline, honest
  manual-only trigger rule stated.
- Audit output path named (`tax-audit-<date>.md`, no `latest.md` pointer).

### Over-Worry

- Operator-perception drift as a third confound-tracking mechanism: the
  ledger records a perception and the selection-bias clause already says it is
  never cited as a measurement; formal confound apparatus for a non-gating
  ledger is the over-elaboration the intent warns against.

### Valid but Defer

- Transcript preprocessing choice for the pilot — deferred to the pilot
  itself by design; building it now fails the anti-apparatus test.
- The whole-harness "is charness net-positive" question — stays open; would
  need its own deliberate operator-approved experiment design.
- Token-accounting trend line — deferred until a real decision needs trend
  data; advisory-only even then.

## Acceptance Tightening

- Pilot precondition: ≥1 NEW post-2026-07-02 ledger entry AND a live open or
  contested decision in the audited session.
- Pilot verdict split: instrument validity (span-cited falsifiable cases)
  judged separately from decision utility (changed a live call).

## Deferred Decisions

Recorded in the design artifact's `## Deliberately NOT doing` and
`Valid but Defer` above; none silently dropped.

## Next Move

Design is locked and committed with the ledger seed and the operating-contract
pointer. Build (rubric + pilot) stays gated on a new ledger entry plus
operator approval, per the design's smallest-next-slice preconditions.
