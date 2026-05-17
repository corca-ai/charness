# Behavior-Test Recommendations

`quality` treats agent or user behavior robustness as a proof-routing problem,
not as a new local runner inside Charness.

## Boundary

- Charness owns detection, recommendation, adapter-facing configuration, and
  honest artifact wording.
- Cautilus owns agent behavior evaluation semantics, execution, comparison, and
  machine-readable result shape.
- Consumer repos own the workflow or product surface under test, the preserved
  task/log/source packet, and any repo-specific oracle.

Do not build a second behavior-test runner in Charness. When a behavior seam
needs evaluator-backed proof, name the Cautilus robustness contract and record
whether the proof was executed, unavailable, blocked by policy, or
recommend-only.

## When To Recommend

Recommend a Cautilus-backed behavior test when deterministic gates cannot
honestly prove the risk because the risk lives in agent behavior, prompt
routing, multi-turn recovery, source use, or baseline-vs-variant judgment.

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

Do not recommend Cautilus for lint, unit tests, type checks, doc links, or other
deterministic repo gates. Those stay in CI, hooks, or repo-owned validators.

## Recommendation Shape

A quality recommendation should include:

- behavior seam under risk
- why deterministic proof is insufficient
- likely Cautilus mode: `fixture`, `observation`, or `skill-experiment`
- source packet or missing source packet
- Cautilus packet target: `cautilus.robustness_request.v1`,
  `cautilus.robustness_plan.v1`, or `cautilus.robustness_report.v1`
- expected relation such as `preserve_behavior`, `surface_failure`, `recover`,
  `clarify`, or `refuse`
- expected result artifact fields the repo needs to preserve, including
  relation status (`satisfied`, `violated`, `blocked`, `invalid`, or
  `inconclusive`), reason codes, limitations, recommendation, and next actions
- current state: `executed`, `recommend_only`, `blocked`, or `unavailable`

Use the helper when a quality run needs a structured recommend-only finding:

```bash
python3 "$SKILL_DIR/scripts/recommend_behavior_test.py" \
  --behavior-seam handoff-resumption \
  --subject-ref skills/public/handoff/SKILL.md \
  --risk-focus "resumption after compacted or interrupted work" \
  --deterministic-gap "static docs cannot prove multi-turn recovery behavior" \
  --source-evidence-ref <gathered-or-local-source-ref> \
  --mutation-kind stimulus \
  --markdown
```

For this repo, live execution still follows
[cautilus-on-demand.md](./cautilus-on-demand.md): consult the planner first and
use `scripts/run_cautilus_eval.py` only with an explicit log-backed behavior
source. Routine quality review can recommend a proof without running it.

## Cautilus Contract

The stable consumer result shape is owned by Cautilus and was settled in
[corca-ai/cautilus#44](https://github.com/corca-ai/cautilus/issues/44). The
contract is documented in Cautilus `docs/contracts/robustness-evaluation.md`
and uses request, plan, and report packets instead of a Charness-owned runner.
