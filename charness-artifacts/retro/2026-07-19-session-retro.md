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
- The second lock passed 4,916 broad tests in 141.9s, then its changed-line consumer found 29 unobserved failure/recovery lines; focused tests were added instead of weakening or baselining the consumer.
- Final lock passed broad pytest in 73.0s and changed-line proof with zero blockers. Its focused coverage producer took 333.8s, disproving the assumption that a mapped subset is automatically cheaper than parallel broad instrumentation.
- This follow-on measured dependency-aware selection at 6.03s versus 3.33s
  direct-only, then showed the direct-only result omitted the rollback integration
  test that exercises newly changed release-runtime lines.
- Broad quality passed 81 gates in 67.4s and surfaced one file-length failure;
  73 focused selector/release tests passed after repair. Three fingerprinted
  review phases returned zero worktree/index drift.

## Waste

The broad exploration was requested and productive, so it was not waste. The avoidable rework was conversion delay: evidence compaction was implemented before defining the immutable-delta serialization owner, subprocess removal before defining a hermetic process-state envelope, and resume ancestry before distinguishing optional classification evidence from mandatory identity. Passing focused tests hid these because their fixtures inherited SHA-1, suite order, or deeper commit history; passing broad tests still did not prove changed failure lines were observed. Mutation instrumentation ranged from 141.9-208.3s broad and 333.8s focused: accepted release proof for now, but clearly gate-baseline runtime debt rather than “necessary safety cost.” The follow-on repeated the same class once: optimizing for the nearest test before defining the final coverage consumer's completeness envelope saved about 2.7s in selection but forced a later coverage rerun. The first recovery-state draft also conflated resumability with raw diagnostic retention; fresh-eye review caught the secret, permission, and retention hazard.

## Critical Decisions

- Move issue-close keywords to a post-publication evidence carrier instead of treating the explicit close API call as the first irreversible effect.
- Centralize object identity, NUL path serialization, count, and digest in `release_delta.py` instead of patching planner and checker independently.
- Keep 20 inventory contracts in-process only after snapshot/finally restoration of every newly imported module, while retaining one real subprocess smoke.
- Treat the final reviewers' findings as blockers despite green gates; the north star requires teeth where a wrong answer could escape, not confidence from terminal green.
- Pay a small conservative selection cost before coverage rather than a large
  second producer run after the exact consumer finds omitted lines.
- Persist typed restart facts, not raw exceptions; restore bounded diagnostic
  detail in the terminal only when durable persistence fails.

## Expert Counterfactuals

- Douglas Engelbart's `(H + LAM + T)` lens would have designed the tool and method together: first declare the evidence envelope (Git-owned full identity plus exact path bytes) and the test hermeticity envelope (all touched global state), then implement consumers. That would have prevented both repair loops.
- A direct failure-boundary lens would ask “what is the earliest external observer that can act?” before naming an API operation irreversible. For GitHub auto-close, the answer is the data-bearing branch push, which correctly moves proof construction ahead of the carrier.
- Engelbart's lens also says the selector method and dependency/fingerprint tool
  are one unit. Defining “all final-consumer-relevant tests” before optimizing
  nearest matches, and defining safe recovery state before persistence, would
  have prevented both follow-on repair loops.

## Sibling Search

- same layer: `skills/public/release/scripts/` immutable-range consumers | decision: same waste, fix now | proof: `rg` found no remaining fixed-width full-object-ID contract; planner/checker now share `release_delta.py`
- abstraction up: `tests/script_main.py` loader/runner | decision: intentional boundary | proof: loader restores `sys.path` and runner restores argv/environment; caller-specific imported-module ownership stays explicit
- specialization down: quality inventory bulk contract test | decision: same waste, fix now | proof: `try/finally` removes every post-snapshot module and exact-set assertion plus two-pass probe confirms restoration
- mental-model siblings: release issue-close carrier | decision: same waste, fix now | proof: initial tagged commit has no close keyword; post-publication observer-bound carrier is the earliest auto-close-capable push
- gate-baseline sibling: mutation-instrumented standing pytest | decision: valid follow-up outside the slice | proof: measured 164.1s exceeds the 120s closeout budget | follow-up: deferred docs/handoff.md#discuss
- same layer: mutation selector and release failure runtime | decision: same waste, fix now | proof: `rg` found one changed-file selector owner and no sibling raw-error persistence writer; both fixes stay at their producer owners
- abstraction up: affected-test selection | decision: intentional boundary | proof: static imports/loaders are modeled while pytest implicit fixture/plugin edges fail safe to broad fallback | follow-up: deferred docs/handoff.md#discuss

## Next Improvements

- workflow: before optimizing or compacting a cross-process boundary, write the canonical identity/serialization/state envelope into the implementation contract.
- capability: keep shared boundary owners small and feed all producer/consumer paths through them; add exotic-format fixtures (alternate object format, legal delimiter characters, assertion failure) at introduction time.
- memory: persist “irreversibility starts at the earliest observer-capable write” and “optimization must name its hermetic state envelope” in the generated recent-lessons digest.
- capability: profile mutation coverage startup and worker instrumentation before changing test scope; preserve the 4,912-test confidence boundary while removing orchestration cost.
- workflow: never infer that fewer test files means cheaper proof; measure selector output under the same coverage/parallelism environment before choosing focused versus broad production.
- workflow: specify the restart-input envelope alongside every resumable irreversible state; validate it before downstream recovery logic and make omissions actionable rather than inferring intent from durable side effects.
- workflow: define selection completeness from the final consumer backward;
  measure selector latency only after every covering path is included.
- capability: affected-test selectors should union untracked inputs, imported
  test helpers, and loader entrypoints while preserving an explicit broad fallback.
- memory: durable recovery state stores allowlisted facts, restrictive modes,
  atomic writes, and bounded retention; raw exceptions are not restart state.

## Portable Candidate

- abstract pattern: consumer-backward focused proof combines current untracked
  inputs with static helper/entrypoint dependencies, then lets the exact coverage
  consumer decide truth; recovery records persist allowlisted state rather than logs.
- triggering evidence: the direct-only selector missed an exercising rollback
  test, and the first raw-error YAML draft failed independent security review.
- intended consumer/repo shape: Python repos with focused pytest coverage and
  resumable local release automation.
- destination: create-skill — absorb through quality/prove/create-cli guidance
  when those skills next revise proof selection or recovery-state contracts.
- first-prompt acceptance claim: a consuming repo can add an untracked module
  reached through a test helper and receive a focused command that covers it;
  a forced release failure leaves safe restart YAML or bounded terminal fallback.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-session-retro.md
