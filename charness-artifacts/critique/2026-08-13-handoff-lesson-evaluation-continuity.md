# Handoff and Lesson-Evaluation Continuity Critique
Date: 2026-08-13

## Decision Under Review

Refresh the handoff into owner-link form and resume the local lesson ledger
without implying that declared preview snapshots prove exposure or that ledger
scores already control the generated digest.

## Failure Angles

- Problem framing: the first draft diagnosed missing workflow wiring but did
  not put session declaration/presentation into the ordered next-session path,
  so #614 could repeat the same cadence lapse.
- First-reader structure: combining contract and JSON state made declaration
  semantics, current counts, and digest nonclaims look like one owner.
- Publication boundary: both reviewers found #615's local-carrier/OPEN boundary
  clear; adding more disclaimers would be ceremony rather than clarity.

## Counterweight Pass

- Act before ship: add the documented session-declaration/presentation step
  before #614 and retain sparse anchored scoring at retro.
- Bundle anyway: split contract from state, and call the record a declared
  preview snapshot rather than a shown set.
- Over-worry: do not add score-policy tuning, digest wiring, another gate, or
  duplicate #615 nonclaims to this handoff refresh.
- Valid but defer: repo-local planner/adapter wiring is a real structural gap,
  but it remains a separate capability decision under `## Discuss`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md#next-session | action: fix | note: add declared-and-presented lesson session before the next meaningful slice
- F2 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md#current-state | action: fix | note: split lesson contract semantics from ledger state and exposure nonclaim
- F3 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/retro/2026-08-13-session-retro.md | action: fix | note: normalize shown-set wording to declared preview snapshot while preserving actual-presentation instruction
- F4 | bin: over-worry | evidence: strong | ref: docs/handoff.md | action: document | note: no extra digest policy, tuning, gate, or publication disclaimer belongs in this refresh
- F5 | bin: valid-but-defer | evidence: strong | ref: docs/handoff.md#discuss | action: defer | note: planner or adapter wiring remains a separate repo-local capability decision

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted the fields but exposed no applied-model metadata
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Two contrasting angle reviewers and one separate counterweight
reviewer returned findings. All three parent-side boundary fingerprints verified
with `verdict: clean` before repairs were applied.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.md
- Packet path: charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.json
- Packet SHA256: 34636ec0a452ef266b799e71c5ad6216b8fc0735cfaf98586f593cd388d5e235
- Identity SHA256: 96b7ae670c6bc87f339dfb973000f3d20fddfefb3d73257c4b1473acd7582122

## Boundary Ownership

- Producer: lesson-ledger scripts produce declared local snapshots and scores;
  the goal and issue records produce backlog/publication state.
- Consumer: the next-session agent reads the handoff and linked owners.
- Owning surface: handoff for ordered continuation, retro/spec/ledger for detail.
- Verdict: owned-correctly

## Later Follow-Up

The repo-local planner/adapter item classified `valid-but-defer` in the initial
handoff refresh was subsequently taken as a separate `create-skill` improvement slice.
Its capability brief, customer critique, implementation boundary, and retained
non-goals are owned by
`charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md`.
The binding above was regenerated after the final repair and customer readback,
so it names the current handoff/retro inputs rather than the earlier draft.
