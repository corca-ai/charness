# Critique — corca-ai/charness#503 resolution

- **Execution**: executed (bounded fresh-eye reviewer)
- **Fresh-eye Satisfaction**: parent-delegated
- **Reviewer tier**: high-leverage; requested `gpt-5.6-terra` with medium reasoning effort
- **Boundary fingerprints**: first review `issue-503-quality-20260805` — drifted and quarantined; second review `issue-503-quality-final-20260805` — clean
- **Target**: runtime-budget owner/decision contract and quality artifact

## Reviewer Tier Evidence

- requested tier: high-leverage
- requested spawn fields: model `gpt-5.6-terra`, reasoning_effort `medium`; no service-tier override was requested
- host exposure state: requested_fields_sent
- application state: first reviewer `019fd055-0d85-7582-b13d-4a879d7c79d9` and second reviewer `019fd057-e1d4-7000-954a-7fbb0ae56b81` were accepted; provider-side model application was not independently exposed
- Delivery state: findings-received; the first review's approval was quarantined after its boundary verify detected parent drift

## Boundary Ownership

- Producer: `.agents/quality-adapter.yaml` records runtime budgets and owner decisions; `.charness/quality/runtime-signals.json` supplies the measured cohort.
- Consumers: `check_runtime_budget.py`, the pre-push gate, the current quality artifact, and the later #505 matched-cost experiment consume these records.
- Owning surface: `quality` owns runtime telemetry/budget records; `achieve` owns the goal-level over-slice response. The issue carrier binds the split without adding a new gate.
- Verdict: owned-correctly

## Change

Resolve #503 by retuning the stale local pytest budget from 58500ms to the
helper-derived 97500ms, recording the current 20-sample cohort, and assigning
every recurring class an owner and destination. Quality-suite and release-bundle
signals retain their current policy and flow to #505 for matched remeasurement;
over-slice response remains goal-level achieve work.

## Reporter JTBD

Maintainers need recurring gate and over-slice cost to land with an owner and an
explicit measured decision, rather than decaying in recent-lessons prose.

## Findings (deduped)

- **Act Before Ship**: the first fresh-eye read correctly found that pytest-only
  retuning left the quality-suite and release-bundle recurrence ownerless. The
  proposal was repaired to make `quality` the telemetry/budget owner and bind
  both retained dispositions to #505.
- **Act Before Ship**: the quality artifact initially failed its advisory-evidence
  validator. The required command/artifact markers were added and
  `validate_quality_artifact.py` then passed. This round-2 shape repair is
  accepted-unreviewed; it changed no verdict logic.
- **Act Before Ship**: the first push gate exposed a stale checked-in D47 probe
  after the new quality artifact changed the corpus. The sibling floor probe,
  marker probe, D47 prose, and producer comment were refreshed together; the
  two measurement test files then passed all 60 tests. The refusing gate exposed
  a real synchronization obligation rather than a reason to bypass it.
- **Over-Worry**: no new aggregate relationship test is needed; the existing
  relationship test protects the dominant changed-line lane and both aggregates
  clear the new pytest bar by a wide margin.
- **Valid but Defer**: parallelism, batching, CI relocation, and aggregate/release
  retuning remain deferred to #505's matched full-command experiment.
- **Boundary disposition**: the first reviewer was not used as approval because
  the immediate verify reported drift from parent edits. The second review read
  the repaired semantic surface and returned clean boundary evidence.

## Deliberately Not Doing

- No pytest, runner, mutation, coverage, or proof-floor test change.
- No retune of aggregate or release budgets from unmatched samples.
- No claim of remote CI, installed-host behavior, GitHub CLOSED state, or issue closure.

## Next Move

Run the issue closeout shape/validator against the exact direct-commit carrier,
then publish and read back #503 through the GitHub adapter. The distinct
behavior verdict must come from the measured runtime-budget readback and the
quality artifact, not from the carrier body or GitHub state.
