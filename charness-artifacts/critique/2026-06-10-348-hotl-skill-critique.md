# 348 hotl skill slice critique
Date: 2026-06-10

## Decision Under Review

Slice 3 of the 2026-06-10 next-queue goal: a new portable public skill `hotl`
(human-on-the-loop closure of applied live behavior, issue 348), authored via
the create-skill portable authoring contract from the sibling repo's
close-loop reference, before its direct-commit carrier locks in.

## Failure Angles

- Load-bearing portable concepts (statuses, staleness semantics, proof rules,
  packet fields, completion-audit discipline) could be lost in the port.
- Host facts from the reference repo (commands, chat/sheet surface names,
  ledger schema paths, channels) could leak into portable skill text.
- The hitl/hotl trigger boundary could be blurry enough to misroute
  "review this applied change" prompts.
- The package could overclaim v1 capability (tooling that does not exist).

## Counterweight Pass

- No blockers. The reviewer verified all seven statuses, `verified_against`
  semantics, the staleness triad, all five workflow steps with every packet
  field, all six proof rules, and the never-close-unproven discipline survive
  the port; grep found zero host-fact leaks; every package/registry validator
  ran green; cold-start resolve from a bare repo returns visible defaults.
- Folded nit: placeholder proof commands now produce a visible resolver
  warning (test-pinned) instead of validating silently.
- Deferred nit (out of slice scope): the boundary statement is
  one-directional — the adjacent review skill's core is at its total-line
  ceiling, so the reciprocal line needs a deliberate edit with a compensating
  trim of reviewed prose; routed as an off-goal issue rather than eroding a
  frozen contract under time pressure.
- Deferred nit (adapter-coverable): the reference's default-live-target
  concept has no generalized counterpart; resolve-targets-from-repo-config
  plus adapter command strings cover consuming-repo wiring without skill-text
  edits.
- Over-worry (reviewer-dismissed): the large dogfood-registry diff is
  alphabetical re-sorting; the example adapter naming this repo is the
  authoring repo naming itself; the reviewed dogfood case without a
  consumer-repo live run matches the existing pattern for review-sampled
  skills and the stated non-claims.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: moderate | ref: skills/public/hotl/scripts/resolve_adapter.py | action: fix | note: placeholder proof commands round-tripped warning-free; a placeholder-text warning added and test-pinned in-slice.
- F2 | bin: valid-but-defer | evidence: strong | ref: skills/public/hitl/SKILL.md | action: file-issue | follow-up: deferred — recorded in the goal artifact's Off-Goal Findings pending the post-slice filing | note: the hitl/hotl boundary is stated only on the hotl side; the review skill's core sits at its total-line ceiling so the reciprocal line needs a deliberate trim of reviewed prose — follow-up issue, not a nit fold.
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/hotl/references/adapter-contract.md | action: document | note: the reference's default-live-target concept is adapter-coverable (targets resolve from repo config / command strings); recorded as a v1 residual, no skill-text change needed for consuming-repo wiring.
- F4 | bin: over-worry | evidence: strong | ref: docs/public-skill-dogfood.json | action: defer | note: registry diff size is alphabetical re-sorting; substantive additions are the one case and the hint rows, validated 20/20.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye bounded subagent reviewer (repo-contract pre-approved scope), read-only in the shared parent worktree plus the read-only sibling reference checkout.
- Requested spawn fields: subagent_type=general-purpose, name=slice3-critique, run_in_background=true, prompt carrying the full slice packet (intent, changed files, invariants, proof, non-claims, out-of-scope, four reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: background agent completed with a structured SHIP-WITH-NITS verdict (31 tool uses, 237s) returned via task notification, including a line-by-line port comparison against the reference skill and independent validator runs.

## Fresh-Eye Satisfaction

Reviewer verdict: SHIP-WITH-NITS — zero blockers; concept preservation,
host-fact hygiene, v1 honesty, and package/registry gates independently
confirmed. Nit dispositions: placeholder warning folded in-slice
(test-pinned); the one-directional boundary statement routed as an off-goal
issue after an attempted fold hit the adjacent skill's total-line ceiling and
was deliberately reverted; the default-live-target residual documented as
adapter-coverable.
