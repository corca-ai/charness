# arm-the-verdict-and-close-the-false-green-cluster disposition review
Date: 2026-08-08

## Decision Under Review

Closing `charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`
EARLY at 2 of 7 slices by operator instruction, and re-homing its remaining claims
into a larger successor goal shaped around the structural defect class the run
surfaced. Under review: the closeout CLAIMS and the successor SCOPE, not the slice
code (which already had two bounded review rounds per slice).

## Failure Angles

- A closeout can cite evidence that does not exist; a floor rejecting a literal
  `TODO` will happily accept a dangling path.
- A retro can assert a persistence step in the past tense before it has run.
- An early close can claim work is "re-homed" while the surface a next session
  actually reads still routes elsewhere.
- A successor can re-shape a slice around a remedy some durable record already
  refuted, because the issue title survives longer than the refutation.
- An issue can be "released for a decision" into a queue that has no entry for it,
  which is abandonment wearing the vocabulary of deliberation.

## Counterweight Pass

Real blockers: the five below, all of which are the closing goal's own subject
appearing in its closeout rather than in its code. Over-worry, deliberately not
acted on: the absence of checked-in review packets is recorded as a non-claim
rather than fixed, because manufacturing packets after the fact would be weaker
evidence than saying plainly that the rounds are supported by prose. The
`out-of-scope:` deferral of a portable gate is defensible on wolf-crier grounds;
only its SCHEDULING at slice 9 of 9 is recorded as a risk.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal `## Final Verification` `Disposition review:` | action: fix | note: cited a critique artifact path that did not exist, rendering complete-shaped evidence for an unreadable file
- F2 | bin: act-before-ship | evidence: strong | ref: retro `## Persisted` | action: fix | note: claimed lessons were recorded in recent-lessons.md when that file had no entry and the lesson index had zero matches
- F3 | bin: act-before-ship | evidence: strong | ref: successor `## Backlog Recount` not-claimed | action: fix | note: `#535` released for a decision with no queue entry anywhere, and `#535`/`#554` mis-cited to the predecessor's queue which holds neither
- F4 | bin: act-before-ship | evidence: strong | ref: successor slice 8 and `#534` acceptance line | action: fix | note: re-shaped `#534` around a premise a prior goal built green, refuted, reverted in full and posted to the issue as possibly not worth building
- F5 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md lines 5, 42-44 | action: fix | note: pickup surface still routed to the predecessor's slice 3, told the next session to measure before arming, and named the refuted `#554` remedy
- F6 | bin: bundle-anyway | evidence: moderate | ref: goal `## Final Verification` self-verification | action: fix | note: dropped the "at an earlier commit" qualifier from the 7816 full-suite figure exactly where it served as closeout proof
- F7 | bin: bundle-anyway | evidence: moderate | ref: goal `## Auto-Retro` | action: fix | note: four retro Waste items undispositioned and the blocked-closeout commit ordering dropped from every artifact
- F8 | bin: bundle-anyway | evidence: moderate | ref: successor `## Backlog Recount` Counted line | action: fix | note: called the reconciliation "programmatic" without naming the command, against the same goal's own no-denominator-without-a-command boundary
- F9 | bin: valid-but-defer | evidence: moderate | ref: successor `## Plan Critique Findings` | action: document | note: the portable-gate generalization is parked at slice 9 of 9 while the two preceding goals reached slice 2; recorded as a named scheduling risk
- F10 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals/2026-08-08-finish-the-declaration-to-verdict-sequence.md | action: document | note: a live sibling draft also claims `#518`; two drafts owning one issue is the successor's own subject at the artifact layer
- F11 | bin: over-worry | evidence: contested | ref: goal mutation ledger | action: document | note: two mutants were resolved by deleting their host branch rather than killed by a test; ledger now says resolved rather than killed
- F12 | bin: over-worry | evidence: weak | ref: skills/public/achieve/scripts/goal_artifact_backlog.py | action: defer | note: `check()` returns ok for template placeholders in isolation, but the composed path is safe because UNSHAPED_MARKER catches them

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only Read/Grep/Glob envelope), spawned unnamed as a one-shot
- Requested spawn fields: subagent_type bounded-reviewer, packet naming the three artifacts to read, eight scoped questions, explicit non-claims and out-of-scope lines
- Host exposure state: applied
- Application state: host-confirmed: the agent returned a completed report and self-reported the envelope bound, seeing only Read/Grep/Glob with no Bash/Edit/Write/Agent exposed
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: `achieve` produces the goal artifact's closeout evidence — `## Final Verification`, `## Auto-Retro`, `## Coordination Cues` — and the successor goal artifact.
- Consumer: a next session reads `docs/handoff.md` for pickup routing, and `check_goal_artifact.py` reads the closeout evidence as the complete-flip gate.
- Owning surface: `achieve` for the goal artifacts, `handoff` for the pickup surface, `retro` for the lessons record; the `#534` refutation stays on the GitHub issue where a prior goal posted it.
- Verdict: owned-correctly

Every repair landed with the surface's owner. The pickup-surface fix routed
`docs/handoff.md` at the successor rather than copying goal state into it, and
this review only stopped a new goal from re-shaping `#534` around a framing its
own issue already carries a refutation for. Nothing moved between producers and
no new shared surface was created, so there is no boundary to escalate.

## Verified As Correct

All five `applied:` dispositions name changes that exist and behave as described:
`iter_warn_scope_adapters` and its summary scope, `is_shaping_status` shared by
both sibling gates, the two wiring-level tests with a one-variable control,
`tests/fixtures/*` in the surfaces manifest, and the quoted-path test loading.
Also verified: the 10-test count, the mutation arithmetic's internal consistency,
the successor's recount set identity, slice order not being issue-number order,
and the early-close reason being honest — operator instruction, explicitly not
blocked work.

## Non-Claims

Read-only envelope: the reviewer could not run commands, so `git log`, the
quality-gate figures, and the bodies of `#536`/`#542`/`#549`/`#550`/`#528` were
unverifiable from the tree. The parent supplied the commit count (13) and the
`#534` refutation record; both were confirmed. Class membership for `#536`,
`#542`, `#549` remains unproven either way. There is no checked-in packet or
fingerprint artifact for any of the four slice-level review rounds, so their
occurrence rests on the goal artifact's own prose.
