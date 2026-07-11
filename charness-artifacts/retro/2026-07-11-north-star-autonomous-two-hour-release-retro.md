# North-Star Autonomous Two-Hour Release Retro
Date: 2026-07-11

## Mode

session

## Context

This retro covers the timeboxed north-star improvement campaign from activation
at 20:05:59 KST through the public v0.66.2 release and its independent readback.
Five bounded improvement slices landed, the full `v0.66.1..v0.66.2` carrier was
reviewed, and the release was published without closing #433.

## Evidence Summary

- Goal and slice ledger: `charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md`.
- Full release readiness: `charness-artifacts/quality/2026-07-11-0662-full-carrier-release-readiness.md`.
- Release record: `charness-artifacts/release/latest.md`; release commit
  `746510ec`, public-evidence commit `68f24313`, and public URL
  `https://github.com/corca-ai/charness/releases/tag/v0.66.2`.
- The final immutable campaign proof passed broad pytest, structural gates, and
  changed-line mutation consumption with `blocking: []`; the release helper's
  own quality command took 74.685 seconds and fresh-checkout probes passed twice.
- Goal-window host probe: `charness-artifacts/probe/2026-07-11-north-star-autonomous-two-hour-release.json`.
  Measured in the scoped window: 2,376 events, 4 context compactions, 263 custom
  tool calls, 257 function calls, 24 subagent spawns, 113 waits, and 18 patch
  applications. Patch applications overlap custom tool calls and are not added
  to them. Token totals and per-call cost were unavailable; cached-input volume
  is not used as a waste claim.
- Packet Consumed: `charness-artifacts/retro/2026-07-11-131833-packet.md`.

## Waste

- Verification-phase waste: generated SLOC drift was discovered after an
  expensive verification lock had already run. Committing the generated file
  correctly changed HEAD and invalidated the proof, so broad instrumented pytest
  had to run again. A later handoff-only correction repeated the sequence.
  Individual broad runs observed in closeout were roughly 95–103 seconds. The
  broad proof itself was necessary safety cost; discovering deterministic sync
  drift only after paying that cost was reducible waste.
- Publication-phase waste: the first release attempt spent 77.859 seconds in
  the release quality command before `docs/handoff.md` failed the references
  inventory. The gate did its job before external mutation, but the cheaper
  targeted references check should have been part of release-prep triage.
- Coordination overhead was high: the scoped host probe records 24 subagent
  spawns and 113 waits. Much of that breadth was explicitly requested and
  produced independent perspectives; the reducible portion was repeated review
  after a concurrent worker changed the boundary fingerprint, forcing the first
  approval to be quarantined.

## Critical Decisions

- A broad green test run was not treated as sufficient after the strict mutation
  consumer found five uncovered changed lines. Release stopped, tests were added,
  and a fresh reviewer strengthened two false-green cases before publication.
- The release scope was rebound from the local unpushed carrier to the full
  `v0.66.1..HEAD` tag delta. This prevented release notes and critique from
  silently omitting commits already present on origin after the prior tag.
- #433 stayed outside release closeout. Pre/post reads remained OPEN, the helper
  carried no close option, and no closing keyword entered the release carrier.
- After the first release attempt failed, local helper mutations were reverted
  without deleting or repointing tags; publication was retried only from a clean,
  re-locked HEAD.

## Expert Counterfactuals

- Douglas Engelbart's `(H + LAM + T)` lens would move generated-surface discovery
  from operator memory into the tool: the method already says
  `mutate -> sync -> verify -> publish`, but the tooling still lets an expensive
  verification lock continue after sync dirties the tree. Issue #436 turns that
  gap into a tool-level follow-up instead of another prose reminder.
- A release-operations counterfactual would order cheap carrier-specific gates
  before the broad release suite. Running the references inventory immediately
  after the final handoff edit would have preserved the strong final gate while
  avoiding one 77.859-second failed publish attempt.

## Sibling Search

- same layer: `scripts/run_slice_closeout.py` plus `charness-artifacts/quality/sloc-inventory/latest.json` | decision: valid follow-up outside the slice | proof: two post-sync dirty-tree cycles reproduced during this closeout | follow-up: https://github.com/corca-ai/charness/issues/436
- abstraction up: `docs/conventions/implementation-discipline.md` phase barrier | decision: intentional boundary | proof: the existing contract already requires sync before verify; weakening it would make proof less trustworthy
- specialization down: `skills/public/release/scripts/publish_release_execute.py` pre-push quality path | decision: diagnostic-only | proof: the first publish attempt failed before tag/push, preserved external safety, and the retry succeeded after the targeted doc fix
- mental-model siblings: verification-lock and release-tag evidence | decision: intentional boundary | proof: both must bind to immutable state; reusing proof across a changed HEAD was correctly rejected

## Next Improvements

- workflow: filed #436 so generated sync drift becomes visible before an
  expensive verification lock is bound, without weakening the final broad gate.
- capability: #436 carries the tool-level desired outcome and observed 95–103
  second rerun evidence; the design remains open between sync-only preflight and
  fail-fast-after-sync.
- memory: this retro and the closeout handoff bind the recurrence to #436, so the
  next session can route from a live backlog item rather than rediscovering it.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md
