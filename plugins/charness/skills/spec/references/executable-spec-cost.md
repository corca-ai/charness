# Executable Spec Cost

Executable specs are acceptance artifacts, not a second place to hide the unit
suite.

## Boundary Rule

If the repo already uses executable specs, keep them at the acceptance boundary:

- prove the contract users or operators actually depend on
- keep fine-grained edge coverage in unit or lower-level deterministic tests
- use prose plus a few representative executable cases, not exhaustive
  permutations

## Cost Rule

When choosing an acceptance check, prefer the lightest honest surface:

1. `unit`
2. source-level deterministic check or validator
3. direct adapter or check-table style executable spec
4. shell-driven executable spec
5. broad end-to-end or evaluator flow

Do not reach for a broad shell-driven executable spec when a cheaper lower
layer would prove the same thing honestly.

## Duplicate Coverage Rule

Repeated broad commands are a smell.

- if multiple executable specs re-run the same large test file or suite,
  reduce that overlap
- if the same shell shape appears three or more times with different inputs,
  build a domain adapter or check table instead of copying more shell blocks
- if a spec block mostly parses command output, the shell is doing adapter work
  and should probably be replaced

## Specdown-Informed Signals

These are strong indicators that executable specs are carrying the wrong load:

- one spec file covers many unrelated behaviors instead of one bounded concern
- shell blocks exist mainly to call the project test runner with different
  filters
- spec commands re-run unit-heavy suites instead of boundary examples
- the repo needs a separate overlap checker to keep duplicate spec coverage in
  check

When these signals appear, move detail downward before adding more spec cases.
