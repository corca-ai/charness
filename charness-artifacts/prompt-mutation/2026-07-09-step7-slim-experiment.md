# Step-7 Slim Rewrite Experiment
Date: 2026-07-09

## Setup

- Scenario: `evals/cautilus/handoff-claim-fidelity/refresh.spec.json`
- Runs: baseline N=2, `step7_slim` N=2
- Baseline provenance: `f84eb223`
- Baseline parentless snapshot: `36636b8fc079680e498f5afe928d8a59a8784770`
- Slim parentless snapshot: `4ded67f41ba8f95a93b7b0e86608edc63366ebb4`
- Rewrite unit: `plugins/charness/skills/handoff/SKILL.md#handoff/workflow@51a25aa66f`
- Frozen replacement hash: `860483a0a100132980da0c077a9e9b80abfd5d2598d358c63cee5796e4170e01`
- Capture budget: 8/8 used. The first 4 captures used the wrong chunked-routing scenario and were discarded; the final proof attempt used 4 refreshed captures.
- Judge command: none. Output-quality judging used bounded blinded subagents, not Cautilus judge spend.

Artifacts:

- Capture results: `charness-artifacts/efficiency/prompt-mutation-handoff-step7-slim/results.json`
- Survival score: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-survival.json`
- Judge packets: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-judge-packet-run0.md`, `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-judge-packet-run1.md`
- Judge results: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-judge-results.json`
- Unblinding sweep: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-unblinding-sweep.json`

## Deterministic Score

The scorer returned `experiment_valid: true`.

Baseline required summary fragments fired in both baseline runs:

- `Refresh kept:`
- `Refresh non-claims:`

All-arm sentinels fired in every baseline and slim run:

- `Refresh kept:`
- `Refresh non-claims:`
- `spill-targets.md`
- planner trace marker `plan_handoff_run.py`

The slim unit verdict was `NO-OBSERVED-EFFECT` with survival rate `1.0` across N=2 runs.

## Efficiency Snapshot

From the refreshed capture aggregate:

| Metric | Baseline Mean | Slim Mean | Delta |
| --- | ---: | ---: | ---: |
| total tokens | 1,914,066.5 | 2,369,254.5 | +23.8% |
| output tokens | 61,585.5 | 55,312.0 | -10.2% |
| duration ms | 371,989.0 | 465,806.5 | +25.2% |
| tool count | 23.5 | 38.0 | +61.7% |
| waste smell count | 2.5 | 2.5 | 0.0% |
| output lines | 31.0 | 24.0 | -22.6% |

Both arms had matcher pass rate `1.0`; outcome grading recorded 0 errors and 6 skipped judge assertions per arm.

## Blinded Output Judge

Pre-registered rule: material regression requires baseline to be preferred in both pairings with contract-grounded reasons.

Mapping after judging:

- Run 0: A = `step7_slim`, B = baseline
- Run 1: A = baseline, B = `step7_slim`

Results:

- Run 0 judge preferred A, therefore `step7_slim`.
- Run 1 judge preferred A, therefore baseline.

Verdict: no material regression under the pre-registered judge rule. This is advisory only; it does not override deterministic or blinding failures.

## Unblinding Sweep

Post-hoc transcript sweep found executed git history/ref probes in every refreshed capture. The slim captures also include direct HEAD/mutant-SHA probes. All runs are tainted for the blinding claim, so the step-7 slim captures are not a clean ship-proof.

Required closeout wording from the taint adjudicator:

> Post-hoc transcript sweep found executed git history/ref probes in every refreshed capture. All runs are tainted for the blinding claim, so the step-7 slim captures are not a clean ship-proof. Sentinels passed and the blinded judge did not find material regression, but T4 does not apply; no edit.

## Outcome

T4 does not apply. The slim prose is **not** shipped.

The handoff skill files remain on the original step-7 wording. The experiment is useful as a negative report: rewrite/sentinel tooling worked, the output-quality channel did not find material regression, and the remaining blocker is that the capture environment still permits observable history/ref probes during the task.
