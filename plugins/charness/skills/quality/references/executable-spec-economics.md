# Executable Spec Economics

Slow executable specs are not automatically strong quality.

They are healthy when they prove boundary behavior that cheaper gates cannot
cover. They are weak when they mostly duplicate unit tests, hide broad shell
wrappers, or spend large runtime on repeated coverage.

## What To Inspect

When a repo uses executable specs, inspect:

- whether the spec suite stays at acceptance level or drifts into unit detail
- whether the same test file or broad command is invoked from many specs
- whether shell blocks are doing parsing or orchestration that should live in a
  direct adapter
- whether the repo already has overlap or duplication guards and whether they
  are strict enough
- whether spec filters, scoped runs, or source guards could keep the standing
  bar fast

## Common Failure Modes

- shell-only adapters become a universal escape hatch for every check
- each spec re-runs a large shared test target instead of one representative
  boundary example
- new specs add coverage by stacking more integration commands rather than
  pushing detail into unit tests
- the suite relies on “broad equals safer” instead of measuring overlap and
  signal

## Preferred Fix Order

1. delete duplicate or low-signal executable cases
2. move fine-grained assertions into unit tests or source-level checks
3. replace repeated shell patterns with a direct adapter or check table
4. optimize repeated command bodies with adapter-level caching or equivalent
   runtime reuse when the repo can do so honestly
5. use bounded parallelism or scoped execution where the runner supports it
6. keep one thin repo-level executable-spec smoke for the contract boundary
7. only then widen standing spec coverage if the cheaper layers still miss a
   meaningful regression class

## Principle

Do not solve slow executable specs by casually deleting the standing gate.

First ask:

- is the slowness coming from duplicate coverage rather than needed boundary proof
- is a broad shell command hiding repeated execution that a guard or adapter
  could collapse
- is the repo missing continuous timings that would make runtime drift visible

Speed work is healthy when it preserves the contract while reducing duplicated
execution. It is weak when it only removes proof.
