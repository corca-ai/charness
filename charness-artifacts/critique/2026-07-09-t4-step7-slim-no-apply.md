# T4 step-7 slim no-apply critique
Date: 2026-07-09
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Whether to apply the frozen step-7 slim rewrite after the refreshed T3 run.
Deterministic sentinels passed and blinded output judges split, but the
post-hoc unblinding sweep found history/ref probes in every refreshed capture.

## Failure Angles

- Blinding boundary: the goal pre-registered transcript sweep taint as part of
  the evidence, so a passing sentinel table cannot by itself make T3 green.
- Shipping boundary: T4 allows the prose edit only if T3 is green; a tainted
  capture is not a clean ship-configuration proof.
- Artifact honesty: keeping the already-applied local handoff edit after the
  taint finding would silently convert advisory evidence into a shipped change.

## Counterweight Pass

- The rewrite/sentinel implementation itself still worked: the scorer returned
  `experiment_valid: true`, every sentinel fired in both arms, and the blinded
  judges did not find a material output-quality regression.
- Those positives support keeping the experiment as a negative report and
  keeping the policy/tooling documentation current, but they do not satisfy
  the T4 ship gate.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-unblinding-sweep.json` | action: document | note: Every refreshed capture executed identity-relevant git history/ref probes; this blocks T4 application under the goal contract.
- F2 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-judge-results.json` | action: document | note: Judge split means no material regression, but advisory quality evidence does not override tainted blinding evidence.
- F3 | bin: bundle-anyway | evidence: strong | ref: `plugins/charness/skills/handoff/SKILL.md` | action: fix | note: The handoff prose edit was backed out; T4 outcome is no edit.

## Reviewer Tier Evidence

- Requested tier: bounded closeout.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium; service_tier inherited.
- Host exposure state: requested_fields_sent
- Application state: host returned reviewer agent id and completion payload.

## Fresh-Eye Satisfaction

parent-delegated — one bounded read-only reviewer completed through
`multi_agent_v1.spawn_agent` and returned `BLOCK`.

## Boundary Ownership

- Producer: T3 capture/scoring/judge/sweep artifacts produce the experiment verdict.
- Consumer: T4 application gate consumes that verdict before any skill prose edit.
- Owning surface: prompt-mutation experiment report and goal scratchpad.
- Verdict: owned-correctly
