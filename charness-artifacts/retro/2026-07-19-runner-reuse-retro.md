# Runner Reuse Speed Slice Retro
Date: 2026-07-19

## Mode

session

## Context

The focused-coverage speedup suggested a transferable boundary: selection wrappers should declare what to run, while the canonical runner owns how to execute it. This slice tested that idea against sibling call sites and migrated the install/update self-validation wrapper only after an identical-target benchmark proved the gain.

## Evidence Summary

- The unchanged 34-test install/update packet took 91.56s through raw serial pytest and 29.29s through the standing runner; the final wrapper run passed all 34 tests in 20.09s.
- `rg` inspection found no remaining executable multi-target raw-pytest wrapper in the scanned repo surfaces; remaining hits were imports, fixtures, command-shape tests, or documentation strings.
- The wrapper regression test records the exact three replacement targets, read-only mode, and release-only inclusion rather than duplicating xdist policy.
- Packet Consumed: charness-artifacts/retro/2026-07-18-234046-packet.md

## Waste

The avoidable cost was execution-policy bypass: a thin selection wrapper silently chose serial execution and paid roughly a minute per validation. The sibling scan itself was useful rather than waste because xdist startup can make small one-file checks slower; a blanket textual migration would have traded measured improvement for assumption.

## Critical Decisions

- Preserve the exact test-selection boundary and move only execution policy to the standing runner.
- Require same-workload wall-time evidence before migrating another caller.
- Leave small raw or synthetic pytest command shapes alone when they are test fixtures, mutation instrumentation inputs, or likely below the parallel-startup break-even point.

## Expert Counterfactuals

- Douglas Engelbart's `(H + LAM + T)` lens would encode the method in the tool boundary: wrappers express target intent, while the runner supplies parallelism, isolation, failure evidence, and fallback. This prevents each new workflow from relearning execution mechanics.
- A direct performance-engineering lens would define the break-even experiment before the refactor: identical collection, warm/cold wall time, and preserved failure semantics. That keeps “centralize” from becoming an unmeasured architecture slogan.

## Sibling Search

- same layer: executable shell validation wrappers | decision: same waste, fix now | proof: install/update's only measured multi-target raw call migrated after identical 34-case benchmark
- abstraction up: `scripts/run_standing_pytest.py` | decision: intentional boundary | proof: it already owns bounded xdist, external basetemp, serial fallback, and failure evidence
- specialization down: focused mutation-coverage selector | decision: same waste, fix now | proof: prior slice already emits replacement targets through the same canonical runner
- mental-model siblings: single-file checks and synthetic pytest command fixtures | decision: diagnostic-only | proof: scan classified them as startup-sensitive checks or parser/instrumentation test data, not demonstrated runtime bottlenecks

## Next Improvements

- workflow: scan for execution-policy bypasses, then benchmark identical work before moving a caller.
- capability: keep target replacement and execution controls separate so callers cannot accidentally broaden the suite while reusing the runner.
- memory: retain “selection owns what; the canonical executor owns how; migration requires break-even evidence” as the reusable performance rule.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-runner-reuse-retro.md
