# Issue #349 resolution critique (hitl/hotl reciprocal boundary)
Date: 2026-06-10

## Decision Under Review

Resolving corca-ai/charness#349 with a deliberate frozen-contract edit to the
review-required, previously at-cap (200/200) `skills/public/hitl/SKILL.md`:
one reciprocal boundary line added to the intro ("Post-apply verification of
applied or live behavior routes to `hotl` instead."), compensated by
compressing the Bootstrap defaults block 7→2 lines (both paths verbatim).
Claim: `preserve` — trigger, workflow, guardrails, and all behavior rules
byte-stable outside the two edits. Carrier `Closes #349` staged on the slice
commit; the close lands on the next operator push.

## Failure Angles

- The trim could erase load-bearing reviewed prose pinned by the dogfood
  contract or tests.
- The reciprocal line's vocabulary could drift from hotl's own boundary
  statement and confuse routing instead of fixing it.
- The class behind the issue (at-cap adjacent skill silently blocking
  cross-skill boundary propagation) could recur unguarded on the next new
  skill.

## Counterweight Pass

- Slice reviewer (change correctness): SHIP-WITH-NITS, no blockers. Verified
  vocabulary symmetry with hotl ("applied or live" / pre-apply vs post-apply
  opposition), defaults compression semantics-preserving (paths verbatim, no
  consumer parses the block shape; dogfood cases[9] pins paths and behavior,
  not layout), placement symmetric with hotl's own intro-paragraph statement,
  and byte-stability of everything else vs HEAD.
- Resolution reviewer (recurrence): ACCEPT-WITH-PROPOSALS. The class is
  systemic — five public skills sit at exactly 200/200 (debug, find-skills,
  impl, issue, quality) and 12 of 20 are ≥190; the create-skill propagation
  step names adjacent-skill inspection but is silent on the at-cap outcome.
  Recurrence is loud, not silent (the ceiling validator fails the edit), so
  no reciprocity validator is warranted; the cheap guards are a create-skill
  checklist line for the at-cap outcome and an optional near-cap (≥195/200)
  preflight warning — both proposed as a follow-up issue, not this slice.
- Recorded asymmetries (not folded; scope is ONE reciprocal line): hotl also
  carries a guardrail bullet for the boundary while hitl does not (4 lines of
  headroom remain if a future slice wants parity); hitl's frontmatter
  description is unchanged, so description-only routers still need the body.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/hitl/SKILL.md | action: fix | note: fix existed only in the working tree; committed with the `Closes #349` carrier plus mirror and goal-artifact slice log in one deliberately scoped commit.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/create-skill/SKILL.md | action: file-issue | follow-up: deferred to goal Auto-Retro disposition (single off-goal issue bundling F2+F5) | note: propagation step is silent on the at-cap outcome; five skills at 200/200 make the trap systemic — propose the checklist line, do not edit create-skill in this slice.
- F3 | bin: over-worry | evidence: strong | ref: scripts/validate_skills.py | action: defer | note: a semantic reciprocity validator needs pair knowledge — high cost, low precision; loud ceiling + prose propagation step is acceptable handling.
- F4 | bin: over-worry | evidence: strong | ref: skills/public/hitl/SKILL.md | action: defer | note: the 4-line headroom does not silently re-arm the trap; exhaustion fails loudly and forces a deliberate trim-or-file decision.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_skill_surface_preflight.py | action: file-issue | follow-up: deferred to goal Auto-Retro disposition (single off-goal issue bundling F2+F5) | note: near-cap (≥195/200) pre-edit warning would surface the trap before prose is written; out of slice scope (no new validators).

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: two bounded fresh-eye subagent reviewers (repo-contract
  pre-approved scope), read-only in the shared parent worktree.
- Requested spawn fields: subagent_type=general-purpose; first prompt carried
  the slice packet (intent, diff, invariants, proof, non-claims, out-of-scope,
  four reviewer questions), second carried the resolution-critique handoff
  (decision artifact, prior structural context from the issue, recurrence
  framing question, success, out-of-scope).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned structured verdicts
  from both reviewers (SHIP-WITH-NITS, 10 tool uses, 84s; and
  ACCEPT-WITH-PROPOSALS, 9 tool uses, 90s) with independently verified repo
  facts (preflight counts, mirror cmp, validator passes, at-cap skill census).

## Fresh-Eye Satisfaction

Issue #349 resolution: both bounded reviews returned no blockers. The
preserve claim held under independent inspection; recurrence handling is
recorded with two named structural proposals routed to one follow-up issue at
goal closeout. Critique #349 binding artifact: this file.
