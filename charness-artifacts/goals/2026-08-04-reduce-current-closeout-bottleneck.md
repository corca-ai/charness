# Achieve Goal: Reduce the current closeout bottleneck without weakening proof

Status: active
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-reduce-current-closeout-bottleneck.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice D — final verification and no-safe-change closeout.
- Current slice intent: preserve the pre-change focused producer after the
  worker-cap candidate failed the fixed materiality test, then lock the local
  proof and durable disposition.
- Next action: run the strongest applicable local closeout, bind the retro and
  independent claims review, and record the exact no-safe-change reopen trigger.
- Verification cadence: cheap deterministic checks at commit boundaries;
  repeated timing and fresh-eye proof at slice boundaries; strongest local
  proof at final closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final proof uses `--verification-lock` and records the exact timing bundle.
- Slice review packet: include the selected command, baseline, preservation
  invariant, falsifier, changed/generated surfaces, timing method, correctness
  channel, and non-claims.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Use the recurring #503 cost signal as a starting point, reproduce the current
critical-path closeout cost in this environment, then implement and measure one
smallest reversible proof-preserving improvement. The goal completes with
repeatable measured relief or an evidence-backed no-safe-change disposition for
the selected current bottleneck; it does not treat historical telemetry or a
green run as proof that a gate is safe to weaken.

The earlier #503 goal is complete as a measurement and decision surface; this is
a new current-environment experiment, not a reactivation of that goal and not a
claim that its historical cohort is still the operator's present pain.

## Non-Goals

- Do not weaken, skip, downgrade, or move a proof gate merely because it is slow.
- Do not treat the historical #503 cohort as proof that the same command is the
  current bottleneck; current measurements choose the target.
- Do not optimize every slow command in one goal. Select one current critical
  path and keep the over-slice signal as a separate unit.
- Do not introduce a universal cross-host runtime promise, a new telemetry
  schema, a release change, a push, or a remote issue close.
- Do not claim runtime relief from a single run or from a faster run that changes
  the proof being measured.
- Do not force an intervention if the current journey no longer reproduces a
  meaningful bottleneck; a durable `historical signal retired` or `no safe
  current target` disposition is an honest outcome.

## Boundaries

- This is a local, reversible optimization goal. No push, release, provider
  proof, remote CI readback, or issue close is in scope.
- The target is the current host/runtime environment only (`axis:
  host/runtime profile`). Results must name the command, environment, corpus,
  and measurement window; they must not become a cross-host promise.
- A gate's correctness, failure visibility, coverage, and recovery path remain
  invariant. A passing run remains distinct from an over-budget advisory.
- Any candidate that changes a gate, validator, runner, or evidence surface is
  treated as a proof-surface change: it requires fresh-eye review and a second
  repaired-surface read when the verdict logic changes.
- The intervention must be reversible until before/after evidence and the
  separate correctness channel are complete.
- If relief is not material, measurements are inconclusive, or correctness
  preservation fails, restore the pre-change behavior. Only evidence-only
  instrumentation may remain, and then only with an explicit reason, owner, and
  reopen observation.
- Historical telemetry is a target-selection signal only. The current baseline
  is the source of truth for this goal.
- Slice A must measure the actual local closeout journey, including the full
  `run-quality.sh --read-only` path and the standing-pytest path, or explicitly
  record why a path is not comparable. A longest single command is not enough:
  selection considers elapsed time, invocation frequency, serial position, and
  proof sensitivity.

## User Acceptance

The user can inspect one durable closeout record and answer:

1. Which current closeout command or phase was selected, and why was it the
   critical path in this environment?
2. What changed, and did at least three comparable post-change observations show
   improvement beyond the pre-change variation? If not, is the result explicitly
   inconclusive rather than called relief?
3. Which correctness and failure-preservation checks show that the work did not
   make the proof weaker or hide a failed run?
4. If no safe improvement was found, what candidate was falsified, who owns the
   decision, and what exact observation reopens it?

Acceptance check matrix:

| Criterion | Decisive check | Required evidence |
| --- | --- | --- |
| Current target | Compare the local closeout journey and candidate contributors | Same command/corpus identity, phase timing, frequency, serial position, proof sensitivity, and target-selection decision |
| Material relief | Repeat at least three comparable before/after observations with a fixed statistic and threshold chosen before the intervention | Baseline and candidate samples, cache/load/profile facts, exclusions, variation, threshold, and result or inconclusive disposition |
| Proof preservation | Run focused controlled failure/fixture checks and the final local correctness channel separately from timing | Same non-zero outcome, visible failure name, recovery receipt, and final locked proof where applicable |
| No-safe-change | Falsify the candidate or fail the relief threshold, restore pre-change behavior, and retain only explicitly justified evidence instrumentation | Tested seam, preservation result, owner, rollback/retention reason, and exact reopen trigger |

## Agent Verification Plan

### Low-Cost Checks

- Read the existing #503 cohort, decision, and local-closeout records together
  with `docs/deferred-decisions.md#d51` before selecting a target.
- Run the current read-only quality and standing-pytest paths with timing
  capture, including the actual local closeout journey, then split the selected
  command into its phases or gate labels before changing code.
- Confirm the selected command and corpus are the same before and after the
  experiment. Record `HEAD`, changed-path/corpus identity, command arguments,
  `PYTEST_ADDOPTS`, xdist/runtime profile, cache warmth, and machine-load facts
  when available; mark unavailable fields explicitly instead of inferring them.
- Inspect changed surfaces and generated/plugin parity before validators read
  them; run cheap focused checks at each commit boundary.

### High-Confidence Checks

- Establish at least three comparable baseline observations and at least three
  candidate observations. Interleave or alternate baseline and candidate runs
  when feasible; if the result remains ambiguous, record `inconclusive` rather
  than ritualistically increasing the sample.
- Choose the materiality threshold and fixed comparison statistic before the
  intervention. The threshold must reflect an operator-relevant saving and be
  larger than the observed measurement resolution; it remains fixed afterward.
- Name the timing producer, timing consumer, selected-seam owner, preservation
  invariant, and falsifier before implementation.
- Run the candidate through the fixed timing protocol, then use focused
  controlled failure/fixture checks and the final correctness channel separately
  from the timing measurement.
- Exercise success, failure, and any unproven/blocked path the candidate could
  affect. Preserve failure names, recovery logs, and non-zero outcomes.
- Use a bounded fresh-eye critique before implementation. If verdict logic or a
  proof surface changes, run the required second review of the repaired surface.
- Run the strongest applicable local closeout at the final bundle, including
  mutation coverage when eligible Python proof surfaces change.

### External Or Live Proof

- N/A — this goal intentionally stops at local current-environment evidence.
  Remote CI, provider/live behavior, release publication, and issue state are
  explicit non-claims.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reproduce the current local closeout journey and identify one critical-path bottleneck | Historical #503 telemetry is a lead, not a current diagnosis; recent evidence suggests the full quality gate may dominate standing pytest | At least three comparable baselines where feasible, phase timing, frequency/serial-position/proof-sensitivity matrix, environment/corpus identity, producer-consumer-owner map, and either a target or `historical signal retired` disposition | completed |
| B | Choose one reversible intervention and its falsifier | Speed pressure must not choose a proof-weakening remedy by intuition | Option comparison, preservation invariant, specific controlled failure channel, fixed statistic/threshold, named selected-seam owner, fresh-eye decision, and stop/reopen rule | completed |
| C | Implement and exercise the smallest proof-preserving improvement | The goal must change an actual current cost source, not only improve its report | Focused tests, interleaved/repeated before-after runs, controlled failure-path checks, synchronized generated surfaces, and measured result or explicit inconclusive/no-safe-change outcome | completed — no safe change |
| D | Verify, record, and disposition the result | Runtime relief is provisional until the same proof remains intact | Separate correctness channel, final local gate, durable #503 follow-up, retro, claims review, and explicit relief/no-safe-change outcome | in_progress |

## Operator Decision Queue

none — the user confirmed that #503 is the next goal, and all work is local and
reversible. The measurement-derived target and threshold are agent decisions
that will be recorded before the intervention, not operator-only approvals.

## Coordination Cues

- Routing: quality — select and measure the current closeout critical path;
  quality owns proof-cost posture and preservation checks.
- Routing: impl — implement the selected local optimization after its invariant
  and falsifier are fixed.
- Routing: critique — review the candidate boundary and any repaired verdict
  surface before the final lock.
- Routing: retro — record measured waste, relief, and the next disposition.
- Gather: n/a — the goal uses checked-in issue and repository evidence; no new
  external source is introduced.
- Release: n/a — no version or install-manifest surface is in scope.
- Issue closeout: n/a — #503 is context and this goal does not close the remote
  issue; remote closure remains outside the local optimization boundary.

## Discuss Before Activation

Discuss before activation: resolved — the user selected #503 as the next
problem because reducing a shared closeout bottleneck should make later work
faster; the goal remains local, does not weaken gates, and chooses the concrete
target only after a fresh current baseline.

## Slice Log

No slices executed; this is a draft awaiting explicit `/goal` activation.

### Slice 1: A — Reproduce the current closeout journey and select the bottleneck

- Objective: Reproduce the full local closeout journey and identify one current critical-path contributor before changing proof behavior.
- Why this approach: The current host baseline, not historical #503 telemetry, determines the target; the full read-only quality path and standalone standing-pytest path were both measured.
- Commits: e1f0f88b — activate the goal; no implementation change was made in this slice.
- What changed: No production or gate files changed. Baseline logs remain under /tmp and runtime artifacts under reports/. The durable goal and critique packet are the checked-in evidence surfaces.
- Alternatives rejected: Standing pytest was not selected: standalone runs were 42.42s, 44.25s, and 44.45s for 7,087 passing tests, while the full quality path was 122.35s, 122.71s, and 123.33s. Broad plain coverage was measured at 110.99s but is a different corpus/command shape and does not by itself justify replacing the focused proof.
- Targeted verification: Full read-only quality: 85 passed, 0 failed on all three runs; phase timings named check-changed-line-mutation-coverage at 119.1s, 119.3s, and 120.1s. Standalone pytest: 7,087 passed on all three runs. Runtime summary and standing-test/CI-recoverable inventories corroborate the mutation phase as the current serial critical path. Focused mapper: 4 changed pool files, all mapped and analyzed; 26 test files / 667 tests passed in the focused no-coverage control.
- Test duplication pressure: No tests were added or expanded in Slice A; duplicate-pressure sample is not applicable.
- Critique: The selected target is the focused changed-line coverage producer/consumer journey. The delegated pre-implementation packet was read by three distinct lenses; all boundary verifications were clean. Their shared finding is that any worker adjustment must be focused-only, preserve xdist/no-xdist fallback and coverage export/consumer semantics, and be measured with matched interleaved samples before implementation.
- Off-goal findings: No off-goal issue was filed. Moving the gate to CI, weakening the partial/unmapped policy, broad cache reuse, and changing the standing runner globally remain out of scope.
- Lessons carried forward: The full quality path is dominated by the focused mutation coverage phase, not by the standing suite. Separate test execution cost from coverage/export cost: the mapped tests took 20.86s without coverage, while the focused producer took about 115–120s.
- Metrics: Host: Linux x86_64, 36 CPUs, empty PYTEST_ADDOPTS, clean e1f0f88b. Full quality median 122.71s; mutation phase median 119.3s. Standalone pytest median 44.25s. Measurement window 2026-08-04 local time; cache/load facts were not instrumented beyond repeated warm local runs and are recorded as unavailable rather than inferred.

### Slice 2: B — Falsify focused worker-cap candidate

- Objective: Choose and falsify one reversible intervention at the focused changed-line coverage producer seam: a focused-only xdist worker cap, measured against the existing uncapped command.
- Why this approach: The mutation coverage phase is the current serial critical path. The critique packet fixed the preservation invariant, the separate correctness channel, and a 5-second materiality threshold before any implementation decision.
- Commits: c01bc0b1 — baseline and Slice A evidence; no production implementation commit because the candidate did not meet the fixed relief threshold. The candidate critique artifact is recorded with this slice.
- What changed: No production, gate, runner, test, generated, or plugin files changed. Added the durable candidate critique record; exploratory timing output remains outside the repository under /tmp.
- Alternatives rejected: Rejected a global CHARNESS_PYTEST_WORKERS default, a forced -n 4 outside xdist detection, moving proof to CI, broad plain-coverage replacement, cache reuse, and standing-suite pruning. Each changes scope or proof shape beyond this reversible focused experiment.
- Targeted verification: Six matched direct producer runs used the same base SHA 827a77f, four changed pool files, mapped corpus, host, and clean consumer verdict. Uncapped samples were 114.95s, 113.92s, 115.24s (mean 114.70s); cap-4 samples were 114.31s, 114.75s, 115.37s (mean 114.81s). The cap was 0.11s slower on mean and did not meet the predeclared 5s threshold, so the candidate is falsified for this host and pre-change behavior is retained. A separate focused correctness channel passed 43 tests in 4.68s; all six consumer verdicts remained clean with the same mapped proof scope.
- Test duplication pressure: No tests were added or expanded because no implementation shipped; the existing producer and consumer test modules supplied the separate 43-test correctness channel.
- Critique: Three delegated read-only reviewers returned findings before implementation. They required focused-only scope, preservation of xdist/no-xdist fallback, unchanged corpus/export/marker/consumer semantics, and matched samples before calling relief. Boundary fingerprints verified clean after each return. The findings are persisted in charness-artifacts/critique/2026-08-04-reduce-closeout-bottleneck-worker-cap-candidate-critique.md. No second repaired-surface round is owed because no verdict logic or proof surface was changed.
- Off-goal findings: No off-goal issue was filed. Broad optimization, CI relocation, global runner policy, and cache reuse remain separate follow-ups; no safe current change was found at this seam.
- Lessons carried forward: Worker-cap scheduling was not material on this host; the 0.11s mean difference is noise relative to the fixed 5s threshold and must not be reported as relief. If reopened, expose a focused producer-only option subordinate to xdist detection and rerun the same matched protocol with a material candidate. Keep coverage/export and test execution cost as separate measurements.
- Metrics: Host: Linux x86_64, 36 CPUs, empty PYTEST_ADDOPTS, same mapped corpus and base SHA 827a77f across all runs; local warm-run cache/load conditions were not instrumented and remain unavailable. Uncapped median 114.95s, cap-4 median 114.75s; ranges 1.32s and 1.06s. Timing logs: /tmp/charness-mutation-focused-default-matched-{1,2,3}.log and /tmp/charness-mutation-focused-cap4-matched-{2,3}.log plus the first cap-4 log. Correctness log: /tmp/charness-closeout-mutation-correctness.log. Decision owner: this goal's parent agent under the active operating frame; reopen only after a new same-host candidate exceeds 5s median relief without proof-scope change.

## Context Sources

Durable references this goal was shaped from:

1. [Design North Star](../../docs/design-north-star.md) — P1/P4/P5 require
   judgment on reversible runtime work and distinct proof when changing a proof
   surface; speed is not permission to remove evidence.
2. [Completed #503 goal](2026-08-04-make-recurring-closeout-cost-actionable.md)
   — prior work measured recurrence and created the detail receipt, but recorded
   zero measured relief and deferred a safe optimization.
3. [#503 cohort record](../issue/2026-08-04-issue-503-slice-a-cohort.md), [#503
   decision](../issue/2026-08-04-issue-503-slice-b-decision.md), and [#503 local
   carrier](../issue/2026-08-04-issue-503-local-closeout.md) — selected units,
   owner, preservation boundary, historical cohort, and reopen conditions.
4. [D51](../../docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime)
   — runtime treatment remains deferred until a concrete current optimization
   candidate exists.
5. [Recent lessons](../retro/recent-lessons.md) — freeze evidence before the
   final proof and keep telemetry separate from per-run claims.

## Interview Decisions

- Target selection: compare current `run-quality.sh` and standing-pytest timing,
  then select one present critical path. `axis: host/runtime profile` — the
  historical largest cohort does not automatically represent this host. Reject
  optimizing the historical command without reproduction.
- Intervention scope: one reversible local change with a fixed preservation
  invariant. Reject gate weakening, broad suite pruning, and simultaneous
  optimization of `over_slice` because they change the proof question before it
  is understood.
- Success test: record a materiality threshold after the repeated baseline but
  before the intervention; require at least three comparable post-change
  observations and improvement beyond measured noise. `single-point:` the
  threshold is one decision for this goal, but its numeric value must be derived
  from the current measurement rather than inherited from historical 120-second
  advisory text.
- Proof channel: keep timing measurement and correctness verification separate.
  `single-point:` local correctness and local elapsed time are the only claims in
  scope; no provider or remote channel is needed.
- External boundary: no push, release, or issue close. `single-point:` the user
  chose a local speed-improvement goal, not publication.

## Plan Critique Findings

Delegated fresh-eye critique of the draft packet ran with three distinct lenses;
all three reviewers were read-only and their boundary fingerprints verified
clean. The packet and findings are persisted in
`charness-artifacts/critique/2026-08-04-reduce-current-closeout-bottleneck-goal-critique.md`.

The following repairs were folded into this artifact:

- Folded blocker: historical recurrence must not select the current target;
  Slice A requires a fresh same-environment baseline.
- Folded blocker: a faster command is not a successful optimization if it drops
  coverage, failure visibility, or the recovery receipt; Slice B fixes the
  preservation invariant and falsifier first.
- Folded blocker: timing and correctness must not be the same proof channel;
  Slice D requires separate correctness verification.
- Folded blocker: optimizing all slow findings would recreate the previous
  scope expansion; only one gate-runtime bottleneck is in scope and `over_slice`
  remains separate.
- Folded blocker: the baseline must cover the actual local closeout journey, not
  only two convenient commands; target selection now includes elapsed time,
  frequency, serial position, and proof sensitivity.
- Folded blocker: repeated timing is now a defined protocol with comparable
  samples, fixed command/corpus/environment facts, a fixed statistic, and an
  explicit `inconclusive` outcome.
- Folded blocker: no-relief handling now names the tested seam, preservation
  result, owner, rollback/retention reason, and reopen trigger; failed or
  inconclusive performance changes must be restored before closeout.
- Over-worry not folded: cross-host normalization, a universal runtime budget,
  and a new telemetry schema are deferred until a real consumer needs them.
- Over-worry not folded: remote CI or release proof is unnecessary for this
  local reversible goal.
- Valid but defer: optimizing `over_slice`, release-helper ordering, and wider
  scheduling/CI restructuring remain separate follow-ups.
- Reviewer provenance: requested tier `high-leverage`; requested model
  `gpt-5.6-terra`, reasoning `medium`, service tier `priority`, fork turns
  `none`; host exposure state `requested_fields_sent`; findings received from
  Zeno, Godel, and Banach; all three boundary windows were clean. A repaired
  surface read by Schrodinger confirmed the journey, comparability, acceptance,
  and separate correctness design, then required and drove the rollback rule;
  its boundary window was also clean. A final repair read by Carver found one
  remaining `two` versus `three` sample-count inconsistency; the parent fixed
  it before activation and verified Carver's boundary clean. The activated goal
  still needs a slice-level critique of the concrete implementation.

## Off-Goal Findings

- #491, #502, and #504 remain separate. They may benefit from a faster common
  gate later, but none is an acceptance criterion here.
- The prior #503 carrier's historical cohort remains evidence context, not a
  current relief claim.

## Final Verification

- Final self-verification: the current closeout bottleneck was the focused
  changed-line coverage phase. The worker-cap candidate was falsified: uncapped
  mean 114.70s versus cap-4 mean 114.81s, so the 5s materiality threshold was
  not met and the pre-change producer behavior was retained. No production,
  gate, runner, test, generated, or plugin behavior changed in this goal.
- Proof preservation: the controlled fixture channel ran
  `python3 -m pytest -vv tests/quality_gates/test_mutation_coverage_producer.py::test_produce_broad_coverage_skips_emit_on_failure tests/quality_gates/test_mutation_coverage_producer.py::test_run_focused_closeout_coverage_marks_failed_payload tests/quality_gates/test_changed_line_coverage_gate.py::test_flags_uncovered_changed_line`
  and passed 3 tests in 0.70s. These fixtures assert a failed producer returns
  non-zero, does not export/stamp fresh coverage, records `status=failed`, and
  keeps an uncovered changed line blocking. Receipt:
  `/tmp/charness-closeout-controlled-failure.log`.
- Separate correctness channel: the focused producer/consumer tests passed 43
  tests in 4.68s. Receipt: `/tmp/charness-closeout-mutation-correctness.log`.
- Final local quality: `./scripts/run-quality.sh --read-only` passed 85 checks
  with 0 failures in 122.0s; the changed-line phase was 118.9s and the
  standing pytest phase was 44.8s. Receipt:
  `/tmp/charness-closeout-final-quality.log`. The run executed at HEAD
  `ab0e4ad8d9999e3383401e348bf3d651746e4033` and the pre/post identity receipt
  shows that HEAD did not move. The worktree contained only the closeout goal,
  retro, packet, index, and claims-review artifacts listed in that receipt; no
  production or proof-surface path changed. Those artifact changes were also
  covered by the gate's artifact validators and the final goal check below.
- Final disposition: no measured relief, no cross-host or remote claim, no
  host token/tool/turn totals, no Cautilus evaluation, no proof-surface change,
  and no issue close or release/push action. The exact reopen trigger is a new
  same-host focused candidate that preserves the mapped proof scope and exceeds
  the fixed 5s median-relief threshold.

Retro: `charness-artifacts/retro/2026-08-04-reduce-current-closeout-bottleneck-retro.md`
Host log probe: skipped: host-log-not-exposed: no goal-scoped host metric window is exposed; explicit local command timing is recorded instead.
Disposition review: `charness-artifacts/critique/2026-08-04-reduce-current-closeout-bottleneck-claims-review.md`

## User Verification Instructions

Activate with:

    /goal @charness-artifacts/goals/2026-08-04-reduce-current-closeout-bottleneck.md

The goal has completed a local no-safe-change experiment. To verify it, inspect
the Slice Log, the bound retro, the candidate critique, the disposition review,
and the separate success/failure receipts named under Final Verification. A
future retry is justified only by the recorded 5s same-host focused-candidate
reopen trigger; no gate weakening or global worker change is implied.

## Auto-Retro

Retro dispositions: applied: used the fixed-threshold, matched-sample, and
separate-correctness protocol for this experiment; future adherence is a
non-claim, while the protocol is durably recorded in the goal and critique.
Retro dispositions: none — no producer-owned worker option is safe to add until
a new focused candidate exceeds the fixed 5s median-relief threshold while
preserving the existing proof scope; D51 remains the follow-up anchor.
Retro dispositions: applied: recorded the falsified global-cap result, exact
reopen trigger, and packet identity in the committed goal, critique, and bound
retro so the candidate is not retried from memory alone.
Structural follow-up: none — the transferable workflow lesson is already
applied in the fixed timing/correctness protocol, and the remaining historical
gate-runtime owner is D51; this no-change evidence does not justify another
permanent guard.
