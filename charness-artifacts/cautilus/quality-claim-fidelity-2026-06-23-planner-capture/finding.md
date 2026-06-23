# Quality planner-backed claim-fidelity capture - 2026-06-23

## Fixture

The neutral runtime fixture was:

```bash
scripts/agent-runtime/capture-skill-run.sh \
  --ref HEAD \
  --invocation "/charness:quality" \
  --out-dir /tmp/charness-quality-planner-capture-20260623-133818 \
  --repo-root . \
  --timeout-sec 1200
```

The fixture did not name the planner, primer references, `quality-lenses.md`,
the expected reference coverage, or the expected ordering. It only invoked the
quality skill.

## Verdict

`build-skill-execution-observation.mjs` classified the execution as `passed`
for `execution-quality-claim-fidelity`.

- `outcome`: `passed`
- `reference coverage`: `9/39` declared references opened
- required reference observed: `skills/public/quality/references/quality-lenses.md`
- `duration_ms`: `154968`
- `total_tokens`: `2111885`
- tool profile: `Read=13 Bash=8 Skill=1`

This is a material shift from the prior diagnostic rejection that observed
`0/39` declared quality references during a gate-first run.

## Runtime Shape

The captured session followed the intended early order:

- Session-start loaded `charness:find-skills`.
- The agent loaded the installed `charness:quality` skill.
- `plan_quality_run.py` ran before broad gates or fixes.
- The run read the required primer references, including `quality-lenses.md`,
  before executing deterministic quality gates as a report-first pass.
- The first `./scripts/run-quality.sh --read-only` pass ran after primer
  loading and reported `Quality summary: 76 passed, 1 failed, total 42.9s`.

## Non-Claims

This packet proves the #397 runtime-reference predicate for the improved quality
skill. It is not a full repository quality closeout.

The capture was stopped after the early-flow predicate was proven because the
agent began a second read-only quality run to inspect the one reported failure.
The interrupted `/tmp/ql.txt` from that second run shows `FAIL pytest` caused by
manual termination while pytest was running; that is interruption noise, not a
fresh gate-health finding.

The remaining diagnostic-proof-contract problem is separate: valid negative
Cautilus findings still need a canonical artifact home when the evaluator
correctly rejects a run. That follow-up is tracked as
https://github.com/corca-ai/charness/issues/398 and should not block closing
#397's primary runtime-reference defect.
