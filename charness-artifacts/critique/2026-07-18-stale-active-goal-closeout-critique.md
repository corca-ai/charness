# Stale Active Goal Closeout Critique
Date: 2026-07-18

## Decision Under Review

Close the v0.56.7 quality-loop goal as a historical lifecycle repair, using
immutable tag and commit evidence without creating present-day release claims.

## Failure Angles

- Problem/evidence integrity: a mutable `release/latest.md` now describes
  v2.0.0 and cannot prove the older goal.
- Operator clarity: the active frame still instructed a future operator to
  publish an already-published release.
- Boundary honesty: historical release proof cannot establish current install,
  runtime, quality-gate, or GitHub state.

## Counterweight Pass

- Act before ship: cite `v0.56.7`/`4307c2e2`, verification commit `0378b519`,
  archive the control frame, and state the present-state non-claims.
- Bundle anyway: give reproducible `git show`/`git rev-parse` user checks and
  state that rerunning the historical release is neither needed nor authorized.
- Over-worry: no new release or current-state live proof is necessary to repair
  a stale lifecycle field.
- Valid but defer: consider a non-blocking stale-active-goal audit only if the
  pattern recurs; one record does not justify a permanent bespoke gate.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-5.md | action: fix | note: replace mutable release evidence and stale publish instructions
- F2 | bin: bundle-anyway | evidence: strong | ref: 0378b519:charness-artifacts/release/latest.md | action: fix | note: include immutable user verification and explicit present-state non-claims
- F3 | bin: over-worry | evidence: strong | ref: v0.56.7 | action: document | note: do not rerun or republish a historical release
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals | action: defer | note: add a stale-active audit only if this pattern recurs

## Reviewer Tier Evidence

- Requested tier: high-leverage for workflow closeout critique.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium,
  service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two angle reviewers and a separate counterweight reviewer
completed the bounded read-only pass. Parent-side fingerprints were clean for
both angles and for the counterweight rerun; the initial counterweight result
was quarantined after unrelated parent drift.

## Boundary Ownership

- Producer: historical release helper and goal lifecycle writer.
- Consumer: the next goal operator deciding whether an active run exists.
- Owning surface: the goal artifact lifecycle state and immutable release
  evidence cited from git history.
- Verdict: owned-correctly
