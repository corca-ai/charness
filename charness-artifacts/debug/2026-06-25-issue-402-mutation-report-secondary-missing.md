# Issue 402 Mutation Report Secondary Missing Debug
Date: 2026-06-25

## Problem

Issue #402 reported scheduled mutation testing failed on
`789762a8725b972ae136d00e7d9660bb9b9ca4a7` because
`reports/mutation/stryker-js.json` was missing. <!-- reproduction-source -->

## Correct Behavior

Given a scheduled full mutation run on `main`, when the Python mutation sample
coverage probe aborts before the full mutation command reaches StrykerJS, then
the closeout should classify the missing StrykerJS JSON as a downstream missing
artifact, not as proof that the JS mutation runner itself failed.

## Observed Facts

- GitHub run `28140431084` failed before the mutation summary: the log says
  `test-command coverage probe failed with exit 1: python3 -m pytest -q -m 'not release_only' tests`.
- The failing test in that coverage probe was
  `tests/test_handoff_plan.py::test_handoff_plan_derives_refresh_and_pickup_from_invocation_text`.
- At the failing SHA, `docs/handoff.md` had 63 lines. That crossed
  `NEAR_LIMIT_LINES = 60` in `skills/public/handoff/scripts/plan_handoff_run.py`,
  so the handoff planner returned `repair_or_prune_handoff` before pickup.
- Current `docs/handoff.md` has 53 lines, and
  `python3 -m pytest -q tests/test_handoff_plan.py::test_handoff_plan_derives_refresh_and_pickup_from_invocation_text`
  passes locally.
- Current StrykerJS full mode runs locally:
  `npm run test:mutation:js` exited 0 and wrote
  `reports/mutation/stryker-js.json`. <!-- reproduction-source -->
- `python3 scripts/check_js_mutation_score.py --repo-root .` reports
  `StrykerJS score: 91.9% threshold: 80% reachable: 86`.

## Reproduction

Historical reproduction is the GitHub Actions run:

```bash
gh run view 28140431084 --repo corca-ai/charness --log-failed
```

Current recovery checks:

```bash
python3 -m pytest -q tests/test_handoff_plan.py::test_handoff_plan_derives_refresh_and_pickup_from_invocation_text
npm run test:mutation:js
python3 scripts/check_js_mutation_score.py --repo-root .
```

## Candidate Causes

- StrykerJS ran but failed to write `reports/mutation/stryker-js.json`. <!-- reproduction-source -->
- The Python mutation coverage probe failed before StrykerJS ran, leaving the
  JS report missing as a downstream symptom.
- The workflow summary classified a missing downstream report without carrying
  the upstream Python probe failure prominently enough.

## Hypothesis

The root incident is the second candidate: a live-state handoff planner test
failed at the historical SHA because the handoff artifact was near its line
limit, causing the Python coverage probe to abort before JS mutation ran. If so,
the current pruned handoff plus local targeted test and JS mutation proof should
recover the reported state without a StrykerJS code change.

## Verification

- PASS: `python3 -m pytest -q tests/test_handoff_plan.py::test_handoff_plan_derives_refresh_and_pickup_from_invocation_text`.
- PASS: `npm run test:mutation:js`.
- PASS: `python3 scripts/check_js_mutation_score.py --repo-root .` reported
  91.9% reachable score against the 80% threshold.
- PASS: bounded causal-review subagent confirmed the primary abort was the
  Python mutation sample coverage probe and that missing StrykerJS JSON was
  downstream.
- NOT RUN: a fresh GitHub scheduled or manual mutation workflow after this
  closeout; remote proof remains pending until the next scheduled run or final
  publication.

## Root Cause

The mutation workflow failed during its Python test-command coverage probe
before StrykerJS executed. At the failing SHA, `docs/handoff.md` was near-limit,
so `plan_handoff_run.py` returned `repair_or_prune_handoff`; the live-state
handoff planner test expected `follow_workflow_trigger`, failed, and caused the
coverage probe to fail closed. The later missing StrykerJS JSON summary was a
secondary missing-artifact report, not the primary defect.

## Invariant Proof

- Invariant: mutation summary closeout must distinguish an upstream Python
  coverage-probe abort from a StrykerJS runner failure.
- Producer Proof: `scripts/sample_mutation_files.py` fails closed with the
  exact coverage-probe exit and command when the sampled pytest command fails.
- Final-Consumer Proof: current closeout records the upstream Python probe
  failure and current JS runner proof separately; existing summary scripts still
  report missing downstream artifacts after an upstream abort.
- Interface-Shape Sibling Scan: prior issue #274 recorded the same secondary
  missing-report pattern after an earlier skipped/aborted mutation phase.
- Non-Claims: this does not prove the next scheduled GitHub mutation run will
  pass; it proves the reported missing StrykerJS JSON was not an active local
  StrykerJS report-generation defect.

## Detection Gap

- live handoff fixture coupling | `tests/test_handoff_plan.py` asserted pickup
  behavior against mutable `docs/handoff.md`, so a near-limit handoff artifact
  could fail a mutation coverage probe unrelated to mutation behavior | smallest
  change: seed an isolated handoff fixture for that test or explicitly accept
  the current live-state coupling as a signal.
- mutation summary phase classification | summary scripts can report missing
  Python/JS artifacts after an upstream phase abort | smallest change: carry the
  upstream abort class into the mutation issue body before listing missing
  downstream reports.

## Sibling Search

- Mental model: a missing mutation report means the report-producing runner
  failed, even when an upstream phase aborted before that runner executed.
- same layer: `scripts/check_js_mutation_score.py` missing-report summary |
  decision: same class, diagnostic-only for this slice | proof: static scan
  only; no code change because current closeout records the upstream abort.
- abstraction up: mutation workflow summaries after skipped or aborted phases |
  decision: same class, diagnostic-only for this slice; no-action reason:
  issue #274 already recorded the pattern and this closeout keeps the phase
  distinction visible | proof: static scan only.
- specialization down: handoff planner test live-state coupling |
  decision: valid follow-up outside the slice | proof: local payload proof |
  follow-up: deferred docs/handoff.md Discuss.
- cross-file: `charness-artifacts/debug/2026-06-02-274-mutation-workflow-tokei-dependency.md`
  records the same downstream missing-report pattern from a different upstream
  abort.

## Seam Risk

- Interrupt ID: issue-402-mutation-report-secondary-missing
- Risk Class: operator-visible-recovery
- Seam: GitHub Actions scheduled mutation workflow versus local recovery proof.
- Disproving Observation: the workflow log shows the Python coverage probe
  failed before StrykerJS ran, while local StrykerJS now writes the expected JSON.
- What Local Reasoning Cannot Prove: whether the next scheduled or manual
  GitHub mutation workflow will fully pass after publication.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Leave #402 open until a fresh GitHub scheduled or manual mutation workflow proves
the remote recovery boundary. Preserve the upstream Python probe abort and
current local StrykerJS proof as diagnostic context rather than claiming a new
StrykerJS implementation fix.

## Related Prior Incidents

- `charness-artifacts/debug/2026-06-02-274-mutation-workflow-tokei-dependency.md`
  recorded a prior mutation issue where missing StrykerJS JSON was downstream of
  an earlier aborted phase.
- `charness-artifacts/debug/2026-06-25-issue-400-js-mutation-weight-gap.md`
  fixed a separate real JS mutation sampler weight/seed problem and should not
  be conflated with this secondary missing-report issue.
