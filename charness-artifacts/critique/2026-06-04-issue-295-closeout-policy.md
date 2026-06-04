# Issue 295 Closeout Policy Critique

## Execution

Fresh-eye quality/code critique ran before the direct-commit closeout for issue
#295.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`

## Packet Consumed

charness-artifacts/critique/2026-06-04-112834-packet.md

## Target

Code critique

## Diff Scope

`run_slice_closeout.py` now surfaces broad-pytest phase policy in text output,
and `slice_closeout_broad_gate.py` exposes policy mode, recommendation, cost
warning, and mutually-exclusive phase flag handling. Focused tests cover
lock-required, pre-lock rehearsal, verification-lock, text output, and phase
conflict behavior.

## Change

Success means the runner makes closeout test-selection cost explicit without
pretending to compute the perfect affected-test set. Pre-lock proof remains
focused current-diff evidence; final broad proof remains tied to
`--verification-lock`.

## Angles

- Quality reviewer: no ship blocker. The initial test assertion used a prefix
  that did not match the real broad pytest command; this was folded into the
  tests by asserting through `is_broad_pytest_command`.
- Code/operational reviewer: found one Act Before Ship issue. Passing both
  `--skip-broad-pytest` and `--verification-lock` made pre-lock skip silently
  win over final lock semantics.

## Findings

- Act Before Ship: block mutually-exclusive broad-pytest phase flags. Folded
  into code and tests before closeout.
- Bundle Anyway: add text-output coverage for the lock-required policy path.
  Folded into tests.
- Over-worry: dynamic affected-test selection, timing measurement, caching, and
  CI integration are outside this slice.
- Valid but defer: verification-lock mode has no cost warning; that is
  acceptable because the final locked run intentionally keeps broad pytest in
  the plan.

## Counterweight Triage

- Act Before Ship: none after the phase-conflict blocker was folded in.
- Bundle Anyway: none after text coverage and detector-based filtering tests.
- Over-Worry: no affected-test engine or live timing work.
- Valid but Defer: future docs may restate phase exclusivity, but the runner and
  tests now enforce it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_broad_gate.py | action: fix | note: block simultaneous `--skip-broad-pytest` and `--verification-lock`
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_slice_closeout_broad_gate.py | action: fix | note: use the broad pytest detector in filtering assertions and cover lock-required text output
- F3 | bin: over-worry | evidence: moderate | ref: https://github.com/corca-ai/charness/issues/295 | action: document | note: dynamic affected-test selection and timing are out of scope

## Deliberately Not Doing

This slice does not select the optimal test set. It makes the broad-vs-focused
phase decision explicit so the agent can record honest proof.

## Next Move

Proceed with direct commit for #295.
