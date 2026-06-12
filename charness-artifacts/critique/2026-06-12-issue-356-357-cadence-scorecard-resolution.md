# Critique Review
Date: 2026-06-12

## Decision Under Review

Resolution of corca-ai/charness#356 (quality-signal scorecard before
structural cleanup) and corca-ai/charness#357 (meaningful-slice cadence) as a
coupled feature bundle: new `skills/shared/references/meaningful-slice-cadence.md`
and `skills/public/quality/references/quality-signal-scorecard.md`, with
delegating wiring from critique `cadence.md`, impl `review-gate.md`, quality
`gate-classification.md` / `inventory-dispatch.md` /
`testability-and-selection.md` / SKILL anchor, and achieve `lifecycle.md`.

## Failure Angles

- Desired-outcome coverage: does each issue bullet land in an owned surface,
  or does a bullet silently drop?
- Recurrence path: will a consumer-repo agent actually encounter the
  scorecard/cadence references at the moment the original Ceal drift happened
  (duplicate/pressure-gate-triggered structural cleanup)?
- Coherence: contradictions with the critique escalation ladder, achieve
  per-slice verification, or operating-contract commit discipline.
- Portability/gates: issue anchors, dated incidents, host refs, self-version
  pins, and relative link depth in the new package surfaces.
- Deferral honesty: is reference-only delivery under-delivery against the
  issues' "require or strongly recommend" language?

## Counterweight Pass

- Real blocker (folded): the actual incident path — duplicate/pressure-gate
  failure → structural test cleanup — bypassed the scorecard because the only
  requirement lived on the clone-family path. Folded: SKILL testability
  anchor amended in place, and `testability-and-selection.md` now routes
  structural cleanup through the scorecard before editing.
- Folded cosmetic: scorecard cost row spoke charness-flavored "mirror sync";
  now "any generated-surface or mirror sync".
- Folded durability: deferred helper script + metric-only closeout guard now
  recorded as deferred decision D29 in `docs/deferred-decisions.md` with
  reopen triggers, instead of living only in a close comment.
- Over-worry (not folded): coherence concerns — the cadence reference
  explicitly disclaims escalation-ladder ownership, achieve lifecycle keeps
  its duplicate-pressure-sample carve-out, and operating-contract commit
  discipline is a lower bound the cadence text does not contradict.
- Over-worry (not folded): the shared cadence reference names the scorecard
  without a markdown link; that is the correct portable choice because
  shared→public relative depth differs between source and installed layouts.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/SKILL.md testability anchor; skills/public/quality/references/testability-and-selection.md | action: fix | note: wire the scorecard into the duplicate/pressure-gate structural-cleanup path the incident actually took — folded this session.
- F2 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/references/quality-signal-scorecard.md cost row | action: fix | note: replace charness-flavored "mirror sync" wording with generated-surface-or-mirror phrasing — folded.
- F3 | bin: valid-but-defer | evidence: moderate | ref: docs/deferred-decisions.md | action: document | note: helper script and metric-only closeout guard stay deferred as D29; the issues' Desired Outcome requires the scorecard judgment itself, and a rationale-classifying guard would be a content classifier the deterministic-floor philosophy avoids until an observed gaming instance shapes it.
- F4 | bin: over-worry | evidence: strong | ref: skills/public/critique/references/cadence.md; skills/public/achieve/references/lifecycle.md; docs/conventions/operating-contract.md | action: defer | note: no contradiction with escalation ladder, per-slice verification, or commit discipline; raised and verified, not folded.

## Reviewer Tier Evidence

- Requested tier: medium (routine bounded fresh-eye resolution review per the
  shared fresh-eye policy).
- Requested spawn fields: bounded read-only packet (issue bodies via issue
  tool, working-tree diff, wiring list, deferral statement, recurrence
  questions); shared parent worktree; mutation forbidden.
- Host exposure state: host-defaulted
- Application state: host-confirmed: resolution reviewer subagent
  `a907194065e148b72` returned verdict REVISE with the F1 wire; counterweight
  reviewer subagent `a199d46adf3400486` independently scanned the same tree,
  found no blocker in the resolution work, and confirmed the folds.

## Fresh-Eye Satisfaction

Resolution reviewer verdict: REVISE → folded (F1 wiring landed, F2 wording
landed, F3 recorded as D29). Per-issue JTBD judgment from the reviewer: #357
satisfied; #356 satisfied after the F1 wire, which is now in the tree.
Counterweight reviewer verdict on the post-fold tree: SHIP with no new
blocker in the resolution work. Both issues remain OPEN remotely by design:
the direct-commit carrier is local-only this session (no push approval), so
remote auto-close and `verify-closeout --expect-state CLOSED` are explicitly
deferred to the operator's wake-up push decision.
