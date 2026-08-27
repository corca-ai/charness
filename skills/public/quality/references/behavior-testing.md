# Behavior-Test Recommendations

`quality` treats agent or user behavior robustness as a proof-routing problem,
not as a new local runner inside Charness.

## Boundary

- Charness owns detection, recommendation, and honest evidence wording.
- Consumer repos own the workflow or product surface under test, the preserved
  task/log/source packet, and any repo-specific oracle or evaluator.
- Reviewers own judgment about behavior that cannot be reduced to a deterministic
  local assertion.

Do not build a second behavior-test runner in Charness. When a behavior seam
needs stronger evidence, recommend the consumer's existing evaluator or a
bounded human review and record whether it was executed, unavailable, blocked,
or recommend-only.

## When To Recommend

Recommend a behavior test or review when deterministic gates cannot honestly
prove the risk because it lives in agent behavior, prompt routing, multi-turn
recovery, source use, or baseline-vs-variant judgment.

Common seams:

- instruction or skill routing robustness
- prompt or skill regression after a contract change
- source-coverage behavior that cannot be reduced to a static source guard
- interruption, resumption, or handoff behavior
- semi-invalid user actions where graceful recovery matters
- baseline-vs-variant skill behavior after a proposed skill edit
- production agent runtime behavior where deterministic tests can prove the
  branch but not the quality of fallback, partial-output recovery, cheap-first
  routing, or escalation decisions; see `agent-production-runtime.md`

Do not recommend a behavior test for lint, unit tests, type checks, doc links,
or other deterministic repo gates. Those stay in CI, hooks, or repo-owned
validators.

## Recommendation Shape

A quality recommendation should include:

- behavior seam under risk
- why deterministic proof is insufficient
- source packet or an explicit statement that it is missing
- expected behavior relation such as `preserve`, `surface_failure`, `recover`,
  `clarify`, or `refuse`
- evidence fields the consumer or reviewer must preserve, including status,
  reason codes, limitations, recommendation, and next actions
- current state: `executed`, `recommend_only`, `blocked`, or `unavailable`

Routine quality review can recommend stronger evidence without running it. A
new local gate is justified only when it proves a distinct deterministic seam;
otherwise keep the recommendation at the consumer or reviewer boundary.
