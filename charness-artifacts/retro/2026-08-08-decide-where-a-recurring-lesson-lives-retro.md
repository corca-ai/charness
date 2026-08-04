# Goal Retro: Decide Where a Recurring Lesson Lives

Date: 2026-08-08

Goal: `2026-08-08-decide-where-a-recurring-lesson-lives`

## Context

This retro covers the shaped goal's five slices: selecting the evidence-carrying
control for #499/#491, building the semantic reviewer question, assigning the
#502 receipt owner, repairing the #500/#501/#497 producer/export boundaries, and
staging the final closeout carrier. The durable goal, slice logs, issue carrier,
resolution critique, disposition review, probe, and verification commands are
the evidence sources. Local implementation and artifact claims are strong;
remote tracker state is only strong where the independent GitHub readback is
recorded.

## Window

The window runs from goal shaping on 2026-08-08 through the checked-in closeout
state at `827a77fc`; the issue carrier was published on the default branch and
#497, #500, and #501 were independently read back CLOSED through `gh issue view`.
The retained readback is `charness-artifacts/issue/2026-08-08-decide-where-a-recurring-lesson-lives-remote-readback.md`.

## Evidence Summary

- The goal's selector and six-row ledger are recorded in its `## Goal`, `## Slice
  Log`, and `## Plan Critique Findings` sections.
- The semantic reviewer question and its worked #499/#491 application are in
  the critique packet and the Slice B source/plugin mirrors.
- The #502 final-line receipt, shared goal-value owner, helper-aware import
  predicate, and exported-layout validator are covered by the Slice C/D logs,
  focused tests, broad standing runs, and the direct changed-line producer.
- The issue carrier and resolution critique bind #497/#500/#501 to distinct
  behavior channels; the goal disposition review audits those claims.
- The remote issue readback artifact records the authenticated GitHub observer,
  carrier SHA, command, and CLOSED result for #497/#500/#501.
- The closeout shape gate found that the previously cited retro belonged to a
  different goal. This artifact is the corrected goal-bound retro evidence.
- Host token/tool totals are unavailable because no goal-scoped host metric
  window was recorded; no such totals are claimed.

## Waste

- **Wrong retro binding at the completion boundary** (recurrence-class: goal-closeout-evidence-binding) — the goal cited
  `2026-08-04-session-retro.md`, whose `Goal:` names a different objective. The
  goal status was already `complete`, but the authoritative closeout validator
  rejected the evidence binding. The avoidable waste was not the validator run;
  it was allowing a claimed completion to carry a merely existing artifact
  instead of a goal-bound one. Decision: fix now by creating this bound retro,
  updating the goal's citation, and rerunning the evidence gate.
- The broad verification, fresh-eye rounds, and carrier checks were necessary
  safety work at proof and issue boundaries, not waste. No host metric evidence
  supports a per-goal runtime or token comparison.

## Critical Decisions

- Chose one selector policy with three candidate answers: fix the owning surface
  when it can carry the semantic fact, require a reviewer question when the fact
  remains judgment-bound, and add a gate only for an observable predicate with a
  recorded escape and measured false-fire cost.
- Applied that policy per issue rather than forcing one mechanism across the six
  records: #499/#491 use the semantic reviewer question; #500/#501/#497 use
  producer/export surface fixes; #502 uses the per-run terminal receipt owner.
- Kept issue publication and remote closeout distinct from local carrier proof,
  then verified the published issue states through a separate GitHub observer.
- Repaired the retro evidence binding after the closeout validator exposed the
  mismatch, rather than weakening the binding rule or treating `Status: complete`
  as terminal proof.

## Trends vs Last Retro

The 2026-08-07 retro recorded the same family of failures in a different form:
guards and verdicts were written against observed shape or unsupported figures
instead of the invariant and reader need. This goal improved the producer and
reviewer surfaces, but the current correction shows that the closeout's own
evidence surface can still lose the reader's required identity. The trend is
therefore mixed: implementation boundaries improved, while evidence ownership
needed one more explicit binding check.

## North Star Alignment

Consulted `docs/design-north-star.md`.

**Held.** P1/P3 kept semantic judgment in a reviewer packet instead of adding a
meta-gate for "correct reasoning". P4/P5 held at the issue boundary: local proof,
carrier validation, publication, and GitHub state readback were treated as
separate claims and channels. The claims review read the goal's acceptance bar
and closeout record instead of treating green tests as completion.

**Mis-applied.** The closeout initially treated the presence of a retro path as
if it proved the retro belonged to this goal. That is the exact form-passed
versus content-correct failure the north star warns about. The binding gate
caught it; the repair is to carry the goal identity in the evidence artifact and
verify it before the status claim is accepted.

## Expert Counterfactuals

- **Engelbart's system-improving lens:** design the human method, language, and
  tool together. The goal format already had a binding rule, but the closeout
  authoring flow let a stale path survive until the final gate. A stronger method
  would make the goal slug part of the retro creation command and show the
  binding result before the status flip.
- **Direct evidence-discipline lens:** at every irreversible claim, ask what
  exact identity the next reader must act on, then vary that identity in a
  negative control. The stale retro was a same-shape artifact with the wrong
  owner; existence-only checking could not distinguish it.

## Next Improvements

- workflow: freeze quality artifacts and host probes before broad verification so
  the proof record and the implementation surface share one identity.
- capability: keep the corpus-denominator packet capability separate until it
  has a named consumer and owner; it is out of scope for this goal.
- memory: carry the semantic reviewer question and the worked #499/#491
  application in the critique packet and its source/plugin mirrors.
- capability: make the terminal quality receipt carry verdict, failed identity,
  and recovery path at the actual truncation boundary.
- capability: keep rolling telemetry separate from a per-run receipt until a
  named consumer, retention, and stale-state contract exists.
- quality: run the changed-line producer after focused branch additions and
  before the final broad gate.
- workflow: reconcile debug ownership, invariant, sibling, and final-consumer
  proof text before binding a closeout record.
- workflow: run the closeout-shape preflight and binding check before writing the
  final status, with the goal slug present in every required evidence artifact.
- workflow: keep the claims review and retro as distinct observers and distinct
  files, then update the goal citation only after both paths resolve.
- capability: make retro persistence accept or derive the owning goal identity so
  a cross-goal session retro cannot be mistaken for goal evidence.
- memory: keep the semantic reviewer question, the worked #499/#491 application,
  and the surface-owner examples in the goal-bound packet and handoff pointers.
- quality: continue broad verification per slice when it is the only observer
  that can catch a cross-surface defect; record the resulting number in the slice
  log immediately.

## Sibling Search

- same layer: goal `## Final Verification` evidence paths | decision: same waste,
  fix now | proof: the closeout binding gate reproduced the mismatch and this
  goal-bound path resolves it.
- abstraction up: achieve closeout preflight and `check_goal_artifact.py` | decision:
  intentional boundary | proof: the validator already owns identity binding;
  no second semantic classifier was added.
- specialization down: retro persistence and per-goal artifact naming | decision:
  valid follow-up outside the slice | proof: this run repaired the concrete goal
  record; a general creator-level binding contract needs its own design and is
  tracked in issue #504. follow-up: https://github.com/corca-ai/charness/issues/504
- mental-model siblings: issue carriers, disposition reviews, probes, and release
  readbacks | decision: diagnostic-only | proof: each already carries an explicit
  owner or channel, and the claims review checked their distinctions.

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-04-050143-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md
