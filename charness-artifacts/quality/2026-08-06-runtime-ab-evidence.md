# Quality Review
Date: 2026-08-06
Title: Controlled runtime A/B evidence

## Scope

Target boundary: `validate-inventory-consumption-declaration` runtime
measurement and the `run-quality.sh` scheduling seam. This packet measures
contention sensitivity; it does not change validator semantics, scheduling, or
the runtime budget.

Ambient repo findings: full quality, remote CI, installed-consumer behavior,
provider state, and mutation proof are outside this measurement packet.

## Current Gates

The existing post-repair quality record reports 85/85 read-only gates and keeps
the 15.500s budget unchanged. This packet does not rerun the full standing
gate; its evidence is the controlled command cohort below.

## Runtime Signals

- runtime source: structured runtime metrics from controlled direct-command
  measurements captured in
  `/tmp/runtime-ab-2026-08-06.jsonl`; host profile was Linux x86_64 with 36
  available CPUs, and both arms used `taskset -c 0-3`.
- runtime hot spots: the measured target command was
  `python3 scripts/validate_inventory_consumption_declaration.py --repo-root .`.
- coverage gate: not rerun; this packet is a measurement, not a full gate.
- evaluator depth: deterministic-gates-only; no Cautilus run was requested.

## Controlled A/B Result

| condition | samples | elapsed ms | return codes |
| --- | ---: | --- | --- |
| isolated, no background workers | 6 | 6451, 6503, 6511, 6551, 6567, 6615; median 6531 | 6/6 zero |
| contended, four inline Python CPU burners pinned to the same 0-3 affinity | 6 | 10275, 10428, 10433, 10493, 10576, 10664; median 10463 | 6/6 zero |

The controlled synthetic-contention median was 3932 ms higher (1.60×) than
the isolated median. The command output was the same successful declaration
validation in every sample: 9 inventory scripts validated.

## Healthy

- The A/B arms used the same host, command, CPU affinity, sample count, and
  return-code assertion.
- The result is directionally consistent across all six samples per arm, not a
  single noisy timing.
- The measured effect is evidence for contention sensitivity, while the
  existing runner repair still owns phase isolation and receipt propagation.

## Weak

- The contended arm uses synthetic CPU burners, not the exact first-phase
  subprocess population of `run-quality.sh`.
- This is one host and one four-CPU affinity slice; it is not a cross-host or
  distributional runtime claim.
- The measurements were kept out of the ignored standing runtime-signal store
  so an exploratory A/B could not overwrite standing-gate history.

## Missing

- A repeated cohort across supported host profiles.
- A same-host comparison using the exact pre-repair first-phase queue and the
  repaired isolated queue under one controlled runner harness.
- A policy decision that would change the 15.500s runtime budget.

## Deferred

- Keep the 15.500s budget and do not generalize the scheduler from this packet.
- Collect another controlled cohort only if a budget or runner change is
  proposed; require fresh packet identity and bounded review for that change.

## Advisory

- structural review result: command: `plan_quality_run.py`; target is the existing runtime owner and consumer;
  the measured transformation is evidence capture, not a new gate. `plan_quality_run.py`
  supplied the required quality lenses and existing runtime-budget owners;
  command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`.
- prose review result: command: inline A/B harness; the evidence separates isolated, synthetic-contended,
  and exact-runner claims; the latter two remain non-claims until measured;
  command: inline A/B harness captured `/tmp/runtime-ab-2026-08-06.jsonl`.
- runtime interpretation: artifact: this controlled A/B packet; synthetic same-affinity contention is a plausible
  contributor to the historical budget excursions, but this packet does not
  establish that it was the sole cause; artifact: this controlled A/B packet.

## Delegated Review

- Delegated Review: not_applicable — this is a measurement-only artifact with
  no code, verdict logic, threshold, or scheduler change. A bounded fresh-eye
  review is required before any implementation or budget decision.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and
  duplicated-proof were executed through the quality planner; no threshold
  change is recommended from this cohort.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`
- `command -v taskset && nproc && taskset -pc $$` — confirmed taskset and
  36-CPU host affinity before measurement.
- Inline Python A/B harness: six direct validator runs with `taskset -c 0-3`,
  then six identical runs while four inline Python CPU burners held the same
  affinity; raw JSONL captured at `/tmp/runtime-ab-2026-08-06.jsonl`.
- Python summary over the raw JSONL — medians, delta, ratio, and return-code
  checks recorded above.

## Recommended Next Quality Moves

- active — capability_needed=runtime-causal evidence; next_center=the existing
  runtime profile and budget consumer; transformation=repeat the same-affinity
  A/B only before a threshold or scheduler change; proof_boundary=versioned
  runtime packet plus independent review; enforcement_posture=advisory.
- active — capability_needed=complete final proof selection; next_center=the
  existing mutation producer helper and final-bundle planner; transformation=run
  the locked broad and changed-line mutation lanes after all semantic inputs are
  frozen; proof_boundary=verification-locked closeout; enforcement_posture=existing-gate-reuse.

## History

- [prior runtime phase-isolation review](history/2026-07-19-portable-proof-path-learning-review.md)
