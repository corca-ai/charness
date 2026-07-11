# Issue-Create Safety, Quality, and Speed Sweep Retro
Date: 2026-07-11

## Mode

session

## Context

This retro covers the activated goal that repaired issue #433's release-close
carrier, audited sibling producer/final-consumer seams, and profiled standing
pytest before one structural test-speed change. The next move is final locked
verification, not another implementation branch.

## Evidence Summary

- Goal: `charness-artifacts/goals/2026-07-11-issue-create-safety-quality-speed-sweep.md`.
- Debug records for #433 and artifact lifecycle/kind collapse; three resolution
  critiques; quality artifact with 72/95/26-test focused proofs.
- Standing baseline 30.68s/30.66s/30.32s for 4,469 tests; target-node wall
  median 4.88s -> 0.655s; isolated full-suite A/B remained inconclusive.
- Packet Consumed: `charness-artifacts/retro/2026-07-11-issue-create-safety-quality-speed-sweep-retro-packet.md`.
- Host token/tool-call totals are unavailable; repeated worker status polling
  and repeated post-review pre-lock runs are workflow proxies, not measured cost.

## Waste

- Producer and final-consumer contracts were inspected separately, allowing a
  release carrier, resolved debug pointer, and pre-review packets to look valid
  locally while failing or overwriting at the next boundary.
- The first artifact-contract fresh-eye review preceded the cheapest complete
  structural pre-lock, so length and subprocess-boundary findings caused an
  avoidable review/fix/re-review cycle.
- Several implementation workers stopped at progress narration before editing;
  narrowing ownership and giving an exact falsifiable contract recovered the
  work, but repeated polling was reducible coordination waste.
- The explicit broad quality gate ran only after the first coverage lock. It
  surfaced production duplicate families late, and the cleanup then required
  repeated full coverage passes as each newly visible branch was covered.
- Broad exploration itself was necessary: the goal explicitly asked for sibling
  discovery. The triage lock—confirmed mismatch/precondition/contract/overreach/
  defer—prevented that breadth from becoming speculative patches.

## Critical Decisions

- Reuse the issue-owned closeout validator and actual commit-msg consumer instead
  of creating release-owned schema or weakening the irreversible-boundary gate.
- Treat debug/quality lifecycle intent and prepare-packet kind as carrier facts;
  keep the shared current-pointer helper lifecycle-neutral.
- Reject headline suite speed claims when paired deltas were mixed; ship the
  stronger orchestration test and claim only the measured node reduction.
- Keep external push/release/issue close outside this local goal run.
- Remove same-owner release duplication, classify only genuinely portable
  residual idioms, and let the full suite falsify the extracted resume boundary
  before accepting the common helper.

## Expert Counterfactuals

- Engelbart's system-improving-itself lens would design H + LAM + T together at
  the start: name producer/carrier/final-consumer in the method, make lifecycle
  and kind explicit in tool payloads, and add the composed roundtrip test as the
  technical enforcement. That would have prevented manual packet repair.
- A direct verification-economics lens would run the cheap complete structural
  pre-lock before the first final reviewer, then reserve fresh-eye judgment for
  semantics that deterministic gates cannot answer. Reviewer-driven code changes
  would still trigger a bounded delta review, not a full repeated fan-out.

## Sibling Search

- same layer: debug and quality artifact path callers | decision: same waste, fix now | proof: record-intent, collision, and executable-refresh tests
- abstraction up: shared current-pointer path helper | decision: intentional boundary | proof: lifecycle intent belongs to callers, so the helper remains filesystem-only
- specialization down: critique and retro prepare-packet validators | decision: same waste, fix now | proof: producer-title plus kind tests and wrong-title/wrong-kind escapes
- mental-model siblings: nested real-gate pytest nodes | decision: diagnostic-only | proof: duration profile ranked one duplicate; other slow nodes remain owner proof until a future critical-path profile says otherwise

## Next Improvements

- workflow: applied — composed producer-to-final-consumer proof and five-bucket sibling triage now gate each repaired seam before implementation closeout.
- capability: applied — release carrier validation, fresh-record routing, packet-kind recognition, and orchestration-focused pytest tests landed with owner gates intact.
- memory: applied — debug, quality, critique, goal, and this retro preserve exact evidence, non-claims, and the speed comparison.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-11-issue-create-safety-quality-speed-sweep-retro.md
