# Session retro: #421 mutation-gate recovery goal
Date: 2026-07-08

## Mode

session

## Context

Session pickup ran handoff chunked routing over 8 backlog entries; the
operator selected the live-issue chunk and the session executed the achieve
goal `fix-421-mutation-regression`
(charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md) end to
end: root-caused the recurring nightly mutation-gate red, covered the 16
changed-line proof targets, audited the post-push judgment range, and triaged
all 16 survived mutants.

## Evidence Summary

- Debug artifact with bisect proof:
  charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md
  (worktree at `57af3d2b` red with the exact CI assertion; `38219d95` green).
- CI evidence: run 28909485596 step conclusions (`Select mutation sample` =
  failure; JS runner never ran) vs the posted "StrykerJS report missing"
  symptom; #422 filed for the misattribution.
- Coverage: both proof-target files 100% (37/37, 35/35 statements);
  changed-line consumer `4f272b07..57af3d2b` → blocking=[], and
  `57af3d2b..HEAD` → ok over 11 pool files.
- Mutant triage: Python 7 killed / 2 accepted; JS 1 killed / 6 proven
  equivalent (scoped Stryker rerun 79→80 killed; ~22k-case differential
  fuzzer through the only export).
- Fresh-eye critique:
  charness-artifacts/critique/2026-07-08-421-test-hardening-bundle-slices-3-5.md
  (2 folds applied, 0 act-before-ship).

## Waste

- The first root-cause hypothesis (base==head empty-range sampler bug) was
  wrong and would have burned a slice; the plan-critique reviewer's empirical
  falsification (running the sampler) redirected the debug to CI logs before
  any code was written. Residual waste: one drafted-then-rewritten Goal
  section.
- The gate's misleading failure body ("StrykerJS report missing") cost three
  days of twice-daily red before this session and one wrong hypothesis inside
  it — the structural fix is #422, not memory.
- The pre-push consumer silently ran its own ~10-minute producer (full
  standing pytest) when invoked with `--skip-if-no-coverage`; not knowing
  that cost one blocked foreground slot and a concurrent-edit flake risk.

## Critical Decisions

- Widening the chunk from "add coverage" to the three-defect scope (gate
  red root-cause + debt paydown + recovery-range audit) after evidence showed
  the coverage-only fix could not stop the twice-daily failures — operator
  confirmed before activation.
- Not closing #421 manually: the workflow's scheduled auto-close is the
  designed second observer; the goal ends at local proof + held push lane.
- Accepting 8 mutants with evidence instead of chasing 100% kills; the six JS
  accepts were proven equivalent empirically rather than argued.

## Expert Counterfactuals

- A CI-forensics lens ("read step conclusions before failure prose") applied
  at issue-triage time on 2026-07-06 would have caught the misattribution two
  days earlier; encoded as the debug artifact's Detection Gap + #422.
- A release-engineer lens on RULE_DATE floors ("run the suite as-of
  tomorrow's enforcement date on landing day") would have caught the
  time-armed red before the DBD-2 push; carried as the retro Prevention line
  and the debug artifact's Sibling Search mental model.

## Sibling Search

- time-armed-floor axis: scripts/validate_critique_artifacts.py
  (`FRESH_EYE_PRESENCE_RULE_DATE`, `BOUNDARY_OWNERSHIP_RULE_DATE`) | decision:
  valid follow-up outside the slice | proof: `38219d95` already fills both
  floors' stub sections in the roundtrip test; suite green on local main |
  follow-up: deferred docs/handoff.md#discuss (RULE_DATE landing-day
  as-of-tomorrow suite run practice).

## Next Improvements

- workflow: when repairing an inherited red test, check whether the same red
  explains any open CI regression issue before treating them as separate
  signals (this session found `38219d95` already fixed #421's live failure).
- capability: #422 — the mutation gate should name a baseline-pytest abort
  (failing nodeids) instead of reporting the downstream missing-report
  symptom.
- memory: the pre-push changed-line consumer runs its own full-coverage
  producer when the marker is stale; budget ~10 minutes and never run it
  concurrently with test-file edits.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md
