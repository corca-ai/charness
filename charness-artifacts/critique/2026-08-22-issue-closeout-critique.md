# Critique Review
Date: 2026-08-22

## Decision Under Review

Closing fourteen open issues — #635, #638, #639, #670, #672, #676, #677, #678,
#679, #681, #682, #683, #685, #686 — on the strength of behavioral
requalification, and shipping the `#681` repair to
`goal_artifact_cadence_owner.py` that the same sweep found still live.

Counted, not estimated: fourteen closed out of sixteen probed. The two held open
are #671 (the issue named two invariants and only the executable one is met) and
#688 (not reproduced from any constructed fixture; a comment asking for the
source bullet was posted instead).

## Failure Angles

- **A probe that never reaches the surface.** This is not hypothetical here: the
  predecessor packet recorded #681 as `already-satisfied` from a checker run
  against an artifact with no `Gate cadence:` bullet, on a goal since gone
  `complete` so the floor skips outright. Every probe in this sweep had to show
  the defect path was entered.
- **A repair that carries the class it repairs.** The `#681` fix rewrites the
  sentences a verdict surface tells its reader. Round 1 found the repair had
  hedged one branch and not its twin; round 2 found the blocking branch left
  undisclosed and a causal clause still standing.
- **A test that pins prose instead of behavior.** Round 1 found two of three new
  tests discriminating only on wording; round 2 predicted a mutant that survives
  all three, and the mutant was run and survived.
- **Closing on a partial satisfaction.** An issue naming two invariants, with one
  met, reads as resolved once closed.
- **A shared worktree corrupted mid-sweep.** Ten probes ran concurrently in the
  parent's tree.
- **Subagent findings taken at face value.** Ten of sixteen probes were delegated.

## Counterweight Pass

- **Real blocker, acted on:** the refusal branch — the one that blocks `/goal`
  activation — carried no disclosure of the known over-fire while the harmless
  decline branch did. The operator who hits the documented over-fire was the one
  operator getting no clue, and the payload's remedy would have had them delete a
  correct acceptance line. Fixed by disclosure, not by guessing at meaning.
- **Real blocker, acted on:** `test_the_two_declines_...` had zero content pins on
  the absent branch. A digit-free copy of the found branch's prose passed all
  three new tests — verified by running the mutant, not by reading. That is #681's
  mirror image shipped by the test named for the repair. A positive pin now kills
  the mutant, re-verified.
- **Over-worry, deferred:** `applies: true` asserting `## User Acceptance` "does
  not restate the gate cadence" when that heading is absent or differently cased.
  Round 2 checked the consequence: `pursue_readiness` computes `missing_sections`
  from the same case-sensitive scan, so such an artifact is refused as incomplete
  on the same report. The sentence is locally false; the verdict is not wrong.
- **Not over-worry after all:** round 1 flagged the attention-state registry entry
  as stale and it was declined; round 2 argued that a proof-surface registry making
  a false claim about the module under review is the same pattern one level up.
  That was right, and it was fixed.
- **Held, not softened:** #671 stays open. The issue named a critique-packet
  portability angle; no angle file mentions it and `Path portability disposition:`
  appears in no shipped markdown. Closing on the executable half would make the
  tracker say something untrue.
- **Rung-2 judgment the carrier's own advisory asks for:** every `Probe record #N:`
  line is the typed disposition `accepted-risk`, not a measurement, and the
  validator names that as "the cheap escape from producing a record". Judged
  honest here, with the cost stated: a probe genuinely ran for all fourteen and
  its commands, controls and outputs are quoted in the requalification artifact,
  so the claim is "an executed probe", which is what the disposition says. What is
  missing is the `probe_record_lib` schema — `claim`, `claim_kind`, `observable`,
  `source_ref`, `base_ref`/`head_ref`, `base_arm`, `call_sites_unproven`. The real
  loss is machine-checkability: nothing can verify these fourteen claims without a
  human reading prose, which is the condition #677 exists to reduce. Authoring
  fourteen conformant records was not done and is not claimed to have been done.
- **Recorded, not smoothed:** a subagent reverted
  `scripts/session_start_lesson_context.py` in the shared tree. Restored from
  `HEAD`, byte-verified, re-covered by tests, and the #639 verdict it could have
  contaminated was re-probed by the parent instead of being accepted.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:215 | action: fix | note: the blocking refusal branch disclosed nothing about the known literal-match over-fire while the non-blocking branch did; disclosure added
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_goal_artifact_cadence_owner.py:285 | action: fix | note: mutant giving the absent branch the found branch's prose survived all three new tests; run and confirmed, positive pin added and mutant re-killed
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:197 | action: fix | note: "defers in prose" was false for a flag on a sub-bullet or a second cadence line; claim scoped to the text read on that line
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/references/attention-state-visibility.json:855 | action: fix | note: registry claimed "the only skip is `complete` artifacts" while the module has four non-evaluating outcomes
- F5 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:58 | action: file-issue | note: negated or two-clause flag mention reads as deferral and refuses a truthful artifact; reproduced, filed as https://github.com/corca-ai/charness/issues/694 rather than patched, because reading polarity is the paraphrase matching this module refuses by design | follow-up: https://github.com/corca-ai/charness/issues/694
- F6 | bin: bundle-anyway | evidence: strong | ref: skills/public/impl/scripts/init_adapter.py | action: file-issue | note: idempotence wired into 1 of 16 skills shipping the script; filed as https://github.com/corca-ai/charness/issues/692 | follow-up: https://github.com/corca-ai/charness/issues/692
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/critique/SKILL.md:114 | action: file-issue | note: claims same-context substitutes refuse, with no such check in record_round_findings.py; filed as https://github.com/corca-ai/charness/issues/693 | follow-up: https://github.com/corca-ai/charness/issues/693
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:200 | action: defer | note: `applies: true` reason asserts the acceptance section does not restate the cadence even when that heading was never read; mitigated because the same report refuses the artifact as incomplete
- F9 | bin: over-worry | evidence: weak | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:130 | action: document | note: first-match-only cadence selection was undisclosed; added to the module's narrowness list rather than changed

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (host typed subagent, Read/Grep/Glob only).
- Requested spawn fields: subagent_type, prompt, description.
- Host exposure state: applied
- Application state: host-confirmed: two bounded-reviewer spawns returned typed findings inline; the round-2 reviewer reported `envelope-unbound` did not apply because Bash, Edit, Write and Agent were absent from its spawn, so the read-only envelope bound by construction.
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: n/a — this is the typed host-subagent branch, not the file-backed worker path.
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

Boundary proof, both rounds, via `reviewer_boundary_fingerprint.py`:

- window `issue-681-repair-review`: `ok: true`, `verdict: parent-attributed`,
  `drift: []`; the sole parent-attributed path is the restore of
  `scripts/session_start_lesson_context.py`.
- window `issue-681-round-2`: `ok: true`, `verdict: parent-attributed`,
  `drift: []`; five parent-attributed paths, all declared.

The tool's own caveat is preserved: git proves the shared tree changed, never who
changed it, so parent-declared paths are recorded testimony rather than proof.

## Fresh-Eye Satisfaction

parent-delegated

Two rounds ran; the two-round cap is consumed. The round-2 repairs (F1–F4) are
recorded as **accepted-unreviewed under the round cap** — no third round read
them. F2's repair is the exception with independent evidence: the mutant round 2
predicted was executed before and after, surviving three tests before and failing
on the new pin after.

## Reviewed Input Identity

<!-- No prepared packet was consumed; both rounds read the working tree directly at the paths named in their prompts. -->

## Boundary Ownership

- Producer: `goal_artifact_cadence_owner.check` renders the cadence-owner verdict and its human reason.
- Consumer: `goal_artifact_lib.pursue_readiness` and `check_goal`, which gate on `cadence["ok"]` and prefix the reason; no consumer parses the reason text.
- Owning surface: the achieve goal-artifact proof surface.
- Verdict: owned-correctly
