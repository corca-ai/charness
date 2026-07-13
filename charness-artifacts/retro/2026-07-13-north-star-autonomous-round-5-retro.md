# North-Star Autonomous Round 5 Retro
Date: 2026-07-13

## Mode

session

## Context

Reviewed the evidence-admitted two-hour improvement run that fixed two operator
boundary defects and published v1.0.4. The next concern is keeping release-time
host proof and post-release quality memory aligned without adding ceremony.

## Evidence Summary

- Goal and slice decisions: `charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md`.
- RCA and critique: the catalog invalid-root and custom-home Claude debug/code
  critique artifacts; release critique; two zero-drift reviewer windows per slice.
- Locked proof: standing broad pytest passed in 94.92s for `v1.0.3..HEAD`;
  release quality passed in 72.297s; fresh checkout, public HTTPS, and install
  refresh passed in `charness-artifacts/release/latest.md`.
- Independent observer: unauthenticated GitHub REST body contained both fixes;
  installed CLI, checkout, Codex cache, and Claude plugin read 1.0.4 with no drift.
- Packet Consumed: `charness-artifacts/retro/2026-07-13-085819-packet.md`.

## Waste

- The quality-scaffold current pointer briefly looked like an overwrite bug
  because the required record resolver was skipped; reading the skill contract
  corrected the invocation without a product change.
- Broad standing-test timing probes added little after the existing structured
  runtime and bounded scouts had already shown no safe speed candidate. The
  useful result was the explicit no-change decision, not more duration sampling.
- Post-release quality reconciliation happened only after the closeout reviewer
  caught stale `Missing` text. Release proof and the quality memory were both
  correct in isolation but temporarily disagreed at their consumer boundary.

## Critical Decisions

- Required a current reproduction or same-command cost before admitting work;
  this prevented a forced test-speed refactor and a hollow release delta.
- Put invalid-root authority in the catalog refresh producer and error rendering
  in both final CLI consumers; list/resolve semantics stayed unchanged.
- Centralized custom-home behavior at the Claude subprocess seam and added
  observation plus add/remove process-boundary proof before shipping.
- Treated helper success as provisional and required a separate observer using
  remote refs, unauthenticated GitHub REST content, and installed doctor/cache.

## Expert Counterfactuals

- Douglas Engelbart's system-improving lens would design the proof tool and the
  workflow language together: when a release touches a root CLI host-mutation
  seam, the real-host trigger taxonomy should either match it or render the
  explicit nonclaim before critique, not surface that judgment late.
- A direct operational counterfactual would make post-release quality-memory
  reconciliation a named closeout step immediately after the release artifact
  lands, before asking a fresh reviewer whether the goal is closable.

## Sibling Search

- host-proof axis: root CLI host subprocess boundaries beyond current adapter globs | decision: valid follow-up outside the slice | proof: release planner reported `real_host_required=false` while `charness` changed Claude host mutations; fake-CLI proof plus an explicit real-host nonclaim made v1.0.4 honest | follow-up: deferred docs/handoff.md#next-session

## Next Improvements

- workflow: after publish, reconcile quality/goal/handoff claims from the release
  artifact before the final quality reviewer, then use that reviewer as a real
  contradiction check rather than a stale-text detector.
- capability: evaluate whether the release adapter needs a narrow declared
  surface for root `charness` host-plugin mutations; add a trigger only if it can
  request a safe, scoped host proof instead of forcing destructive real-host work.
- memory: keep the independent observer's substantive REST and installed
  doctor/cache evidence in a durable probe/disposition artifact, not only chat.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md
