# Issue #183 Closeout Ledger

Classification: bug

JTBD: Keep Charness mutation testing useful as a repo-testability signal by
running a bounded, representative mutation sample and blocking recovery when
scope gaps, partial execution, or changed-file exclusions make the signal
untrustworthy.

Root cause: The mutation pipeline used weaker upstream selection predicates
than its downstream score gate. Sampling accepted files with some coverage, the
test command stayed too broad or too narrow for the actual sampled mutants, and
score closeout could still pass when changed files were excluded or execution
was partial.

Debug artifact: `charness-artifacts/debug/2026-05-21-mutation-scope-gap-testability.md`
and `charness-artifacts/debug/latest.md`.

Siblings: decision and proof are recorded in the debug and quality artifacts.
The sibling scan covered changed-file exclusions, `PASS-partial`, dependency
setup drift, probe config leakage, CI-portable coverage commands, file-count
runtime budgeting, import/setup-only coverage, sanitizer survivors, and fake
external-tool tests using the real repo root. Proof includes local focused
tests, local hosted-seed replay at `88.9%` with `81/81` executable mutants
executed, and hosted Mutation Tests run `26196843109`.

Prevention: Mutation closeout now aligns producer and consumer contracts:
sampled files must have covered mutable lines, selected files must contribute
focused pytest nodeids, workload budgets are executable-mutant and nodeid
budgets rather than file-count budgets, changed-file exclusions are blocking,
and `PASS-partial` is diagnostic-only.

Manual fallback reason: operator-directed-manual-close. The hosted recovery
workflow already closed #183 after run `26196843109`; this comment provides the
structured issue-resolution ledger required by the repo issue closeout
contract.
