# Session Retro
Date: 2026-07-19

## Mode

session

## Context

An aggressive autonomous improvement pass repaired the release issue-close state machine, compressed release-plan evidence, and accelerated a repeated inventory contract test. Final fresh-eye review then exposed two boundary mistakes in otherwise passing work: SHA-1-width coupling and incomplete process-global cleanup.

## Evidence Summary

- Commits `3881fd8b`, `e84ff411`, `940e6416`, and `c6394f21` separate correctness, token-density, test-speed, and reviewer-driven portability/isolation repair.
- Planner output fell from 23,533 to 7,061 bytes and its real-host command from 8,108 to 175 characters; the controlled inventory test fell from 4.44s pytest to 0.84s.
- Fresh-eye reviewers independently reproduced SHA-256 rejection and `sys.modules` residue, then confirmed the repairs with 60 focused tests and repeated-interpreter probes.
- `./scripts/run-quality.sh --read-only` passed in 56.4s; all cost claims above are measured command/runtime evidence, not host-token estimates.
- The first mutation-instrumented lock ran 164.1s and caught four failures after 4,912 passes; the gate failed correctly, but its >120s baseline is routed as runtime debt.

## Waste

The broad exploration was requested and productive, so it was not waste. The avoidable rework was conversion delay: evidence compaction was implemented before defining the immutable-delta serialization owner, subprocess removal before defining a hermetic process-state envelope, and resume ancestry before distinguishing optional classification evidence from mandatory identity. Passing focused tests hid these because their fixtures inherited SHA-1, suite order, or deeper commit history. The 164.1s mutation-instrumented gate is accepted release proof for now but remains gate-baseline runtime debt, not “necessary safety cost.”

## Critical Decisions

- Move issue-close keywords to a post-publication evidence carrier instead of treating the explicit close API call as the first irreversible effect.
- Centralize object identity, NUL path serialization, count, and digest in `release_delta.py` instead of patching planner and checker independently.
- Keep 20 inventory contracts in-process only after snapshot/finally restoration of every newly imported module, while retaining one real subprocess smoke.
- Treat the final reviewers' findings as blockers despite green gates; the north star requires teeth where a wrong answer could escape, not confidence from terminal green.

## Expert Counterfactuals

- Douglas Engelbart's `(H + LAM + T)` lens would have designed the tool and method together: first declare the evidence envelope (Git-owned full identity plus exact path bytes) and the test hermeticity envelope (all touched global state), then implement consumers. That would have prevented both repair loops.
- A direct failure-boundary lens would ask “what is the earliest external observer that can act?” before naming an API operation irreversible. For GitHub auto-close, the answer is the data-bearing branch push, which correctly moves proof construction ahead of the carrier.

## Sibling Search

- same layer: `skills/public/release/scripts/` immutable-range consumers | decision: same waste, fix now | proof: `rg` found no remaining fixed-width full-object-ID contract; planner/checker now share `release_delta.py`
- abstraction up: `tests/script_main.py` loader/runner | decision: intentional boundary | proof: loader restores `sys.path` and runner restores argv/environment; caller-specific imported-module ownership stays explicit
- specialization down: quality inventory bulk contract test | decision: same waste, fix now | proof: `try/finally` removes every post-snapshot module and exact-set assertion plus two-pass probe confirms restoration
- mental-model siblings: release issue-close carrier | decision: same waste, fix now | proof: initial tagged commit has no close keyword; post-publication observer-bound carrier is the earliest auto-close-capable push
- gate-baseline sibling: mutation-instrumented standing pytest | decision: valid follow-up outside the slice | proof: measured 164.1s exceeds the 120s closeout budget | follow-up: deferred docs/handoff.md#discuss

## Next Improvements

- workflow: before optimizing or compacting a cross-process boundary, write the canonical identity/serialization/state envelope into the implementation contract.
- capability: keep shared boundary owners small and feed all producer/consumer paths through them; add exotic-format fixtures (alternate object format, legal delimiter characters, assertion failure) at introduction time.
- memory: persist “irreversibility starts at the earliest observer-capable write” and “optimization must name its hermetic state envelope” in the generated recent-lessons digest.
- capability: profile mutation coverage startup and worker instrumentation before changing test scope; preserve the 4,912-test confidence boundary while removing orchestration cost.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-session-retro.md
