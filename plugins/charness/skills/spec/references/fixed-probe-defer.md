# Fixed, Probe, Defer

This is the core discipline for `spec`.

## `Fixed Decisions`

These must be decided before the current implementation slice starts.

Use `Fixed Decisions` when the answer changes:

- scope
- user-visible behavior
- acceptance criteria
- dependency choice
- rollout or migration risk

## `Probe Questions`

These should be answered by a small build, spike, failing acceptance test, or
targeted experiment.

Use `Probe Questions` when:

- discussion alone will not settle the question honestly
- the safest way to learn is to implement a thin slice
- the answer is needed soon but not before all coding starts

Every probe should name:

- what will be built or tested
- what signal will answer the question
- how the spec should change depending on the result

## `Deferred Decisions`

These can wait without making the current slice dishonest.

Use `Deferred Decisions` when:

- implementation can proceed safely without the answer
- the choice belongs to a later rollout stage
- the user has not expressed enough preference and forcing a decision now would
  create fake precision

Deferred items must remain visible in the artifact. Hidden deferral becomes
drift.
