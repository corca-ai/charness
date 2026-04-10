# Operability Signals

`quality` should treat runtime drift and diagnostic visibility as first-class
operability concerns when the repo has meaningful standing gates or
operator-facing flows.

## Runtime Timing

If the repo runs lint, test, eval, or quality commands regularly:

- prefer a cheap repo-owned elapsed-time signal for the standing commands
- keep the signal machine-readable so later sessions can compare drift instead
  of guessing from memory
- keep the current summary compact and rotate older samples into archives
- prefer per-command timing over only one aggregate wall-clock number

Good timing artifacts help answer:

- which gate is getting slower
- whether a recent change widened the standing bar accidentally
- whether flaky setup or external calls are inflating runtime

## Logs And Diagnostics

If the repo depends on logs, traces, or machine-readable diagnostics for normal
operation or debugging:

- check whether the useful signal appears early enough for an agent or operator
  to act on it
- prefer logs that reveal the failing seam, command, boundary, or recovery path
  without forcing a full repro first
- check whether the format is stable enough that future automation can inspect
  it honestly

## Rotation And Retention

Unbounded logs are an operability quality problem.

Inspect whether:

- logs or timing samples are rotated into bounded archives
- current summaries stay short and useful
- retention is explicit enough that future sessions know what survives
- the repo avoids committing ever-growing machine output by accident

Do not force full observability stacks onto small repos. Apply this lens when
the repo already emits meaningful diagnostics or clearly would benefit from
them.
