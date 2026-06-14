# Critique Review: #361 mutation survivor coverage

Date: 2026-06-14

Resolution critique (bounded fresh-eye, high-leverage tier, separate agent
context — subagent `ad2b814c3037cad8b`) of the fix for corca-ai/charness#361.
Recurrence framing: "what would let this class of issue come back — and is the
closure disposition honest given the gate is sampled?"

## Decision Under Review

Fix for #361 (`mutation-test`, automated tracker): tests-only coverage that kills
the consistently-surviving real mutants in `runtime_profile_lib.py`
(18/30/36/64/66), `record_rca_event.py` (27/92/93/108), and `render_report.py`
(30/31/49). Each kill was proven by mutating the exact line → target test fails →
revert. Disposition: push the tests (`Refs #361`, no `Close`), comment on #361
with the proven evidence, and leave the issue OPEN for the auto-close marker —
a local pass cannot confirm the scheduled (sampled) score ≥80%.

Prior causal-review context (not redone): missing-gate coverage — tests asserted
happy-path return values but not operator polarity / raw JSON format / error
branches. Durable fix is coverage, not a floor/budget tweak
(`mutation-testing.md:291`). Recommendation (A).

## Failure Angles

- Closure honesty: manually closing #361 would assert an unproven sampled gate
  result.
- Whack-a-mole: the next seed could surface other survivors, making the coverage
  non-durable.
- Over-reach / gaming: indent/required tests could be score-gaming; leaving
  identity mutants could be dishonest.

## Counterweight Pass

- Whack-a-mole largely unfounded: survivors are on stable files; the next seed
  re-samples the same now-covered lines, so the killed set is durable.
- Structural mutant-pool exclusion of argparse boilerplate IS the floor-tweak
  the reference forbids — correctly NOT done.
- Indent/required tests assert raw output / argparse exit codes — legitimate
  behavioral coverage with #219/#251 precedent, not gaming. Leaving the
  near-equivalent identity (`Eq_Is` / `NotEq_IsNot`) mutants is honest and
  consistent with documented repo precedent for that class.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: git working tree | action: fix | note: keep #366's production change out of the #361 carrier and evidence; ship as separate commits and scope the #361 comment to the survivor-kill tests (resolved)
- F2 | bin: valid-but-defer | evidence: strong | ref: https://github.com/corca-ai/charness/issues/361 | action: defer | note: a local pass cannot confirm the sampled scheduled score >=80%; leave #361 OPEN for the auto-close marker rather than asserting an unproven result with a manual close
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/runtime_profile_lib.py:30 | action: defer | note: accepted near-equivalent identity survivors (Eq_Is/NotEq_IsNot on :30 and :59) noted by path:line so the next scheduled-fail triager does not re-chase them
- F4 | bin: over-worry | evidence: strong | ref: skills/public/quality/references/mutation-testing.md:291 | action: document | note: whack-a-mole fear unfounded for stable files; pool-exclusion would be the forbidden floor-tweak

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.5, reasoning_effort medium, service_tier priority (from .agents/critique-adapter.yaml reviewer_tiers.high-leverage)
- Host exposure state: host-defaulted
- Application state: not host-confirmed; the adapter mapping is a Codex-host field, so this Claude Code host spawned its strongest reviewer (Opus 4.8) instead of sending the gpt-5.5 fields

## Fresh-Eye Satisfaction

parent-delegated — the parent spawned this bounded reviewer in a separate agent
context and it completed the angles + counterweight directly.
