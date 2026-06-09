# Critique Review
Date: 2026-06-09

Goal: charness-artifacts/goals/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md

## Decision Under Review

Whether this goal's surfaced improvements are honestly dispositioned — the retro's
`## Next Improvements` (3 dispositions) and the goal's `## Auto-Retro`
(`Retro dispositions:` + `Structural follow-up:`) — with no laundering (a real,
generalizable fix recorded as prose-only "memory" or "none" when it should be an
`applied:` gate or `issue #N`).

## Failure Angles

- An `applied:` disposition that overclaims (the drift tests / persisted memory do
  not actually exist).
- A `Structural follow-up: none` that launders a transferable waste sibling that
  in fact still exists and is unguarded.
- An `out-of-scope:` that should really be `applied` (cheap to do now) or `issue #N`.

## Counterweight Pass

- The three per-improvement dispositions are individually honest and backed by real
  artifacts (drift tests at `tests/quality_gates/test_check_artifact_surface_preflight.py:505-507`;
  the producer ergonomics gap is real at `scripts/run_slice_closeout.py:255`; the
  distinction is recorded in the retro + `recent-lessons.md`).
- The one real blocker was the `Structural follow-up: none` — it laundered a LIVE
  sibling of the B1 waste class at the ORIGIN site, now folded (see F1). Not
  over-worry: the drift was concrete and already present, not hypothetical.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_template.md:121 | action: fix | note: LAUNDERING — `Structural follow-up: none` hid a live sibling of the B1 waste class; the template's hand-quoted destination form had already drifted from `disposition_form.DESTINATION_FORM_SUMMARY` (`applied: <change>` vs `applied: <gate/hook/validator/test/contract change>`). Folded: template re-quoted verbatim + drift-pin guard added; disposition changed to `repo-local guard:`.
- F2 | bin: over-worry | evidence: moderate | ref: skills/shared/references/retro-issue-destination-split.md | action: defer | note: a repo-wide "every quote of an enforced form must be verbatim-pinned" guard would flatten intentional context-specific prose (the reference docs define the arms one-per-bullet; lifecycle.md already matches). Pinned only the proven-drifted author-facing SEED (the template), recorded the prose quoters as not-seeds.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye disposition reviewer (separate subagent context, read-only, bounded packet).
- Requested spawn fields: the retro + goal artifacts, the four named dispositions to falsify, and the laundering key-question (should the lesson become a repo-local guard?).
- Host exposure state: applied
- Application state: host-confirmed: tool signal: a bounded fresh-eye subagent ran via the Agent tool and returned a structured REVISE verdict citing `goal_artifact_template.md:121` drift vs `disposition_form.py:128-131`, with the per-disposition honesty check and the laundering analysis (both sides argued).

## Fresh-Eye Satisfaction

Reviewer verdict: REVISE — the three per-improvement dispositions are sound, but
`Structural follow-up: none` laundered a live transferable sibling at the origin
site. Folded this run: fixed the template drift (`goal_artifact_template.md` now
quotes the live `DESTINATION_FORM_SUMMARY` verbatim) and added a drift-pin guard
(`tests/quality_gates/test_disposition_form_floor.py::test_goal_template_structural_followup_form_matches_live_constant`);
the goal's `## Auto-Retro` `Structural follow-up:` is re-dispositioned to
`repo-local guard:`, and the retro `## Sibling Search` is corrected to record the
found-and-fixed origin sibling. Concrete signal: the subagent's cited file:line
drift evidence, independently reproduced (`disposition_form.DESTINATION_FORM_SUMMARY`
!= the pre-fix template line).
