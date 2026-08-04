# Retro: Reduce closeout runtime by removing structural waste

## Context

This retro covers the active goal's measurement, candidate triage, delegated
premortem, midpoint claims review, and bounded named-family falsification. The
goal sought at least ten seconds of real local closeout relief while preserving
process and delivery-boundary proof. Strong claims come from the three matched
full gate receipts, the canonical focused runner receipt, and the checked-in
node-level manifest; broader inventory counts remain advisory.

## Window

The window runs from goal activation at commit `23f60313` through the Slice B
repair and closeout preparation on 2026-08-04. It includes no production code,
test, validator, generated export, release, remote, provider, or live behavior
change.

## Evidence Summary

- Three matched `./scripts/run-quality.sh --read-only` runs passed 85/0 with
  medians of 123.51s total, 48.9s standing pytest, and 120.2s changed-line
  mutation. The mutation mapper did not select the CLI family.
- The inventory-derived nested-CLI subset ran 3,443 tests in 31.60s, but its
  file-pattern corpus was not a migration unit. The ad hoc exclusion probe is
  retained only as a non-causal selection signal.
- The exact standing `tests/charness_cli` family collected 155 nodes, deselected
  46 release-only nodes, and passed in 3.62s through the canonical focused
  runner. The checked-in manifest binds nodeids, classifications, boundaries,
  and owner to that result.
- The delegated premortem and midpoint fresh-eye claims review both preserved
  the boundary concern. The midpoint review initially blocked closure because
  the named-family evidence and closeout-state reconciliation were missing;
  its explicit boundary verify was clean after the parent completed the review.
- No goal-scoped host metric window was exposed. Temporary timing receipts are
  reproduction sources, not host token, turn, or cost totals.

## Waste

- `candidate-corpus-identity` (strong) — the initial broad subset was useful
  exploration, but the ad hoc “209 targets” exclusion briefly looked like a
  migration unit without a producer. Decision: same waste, fix now. Proof: the
  checked-in 155-node manifest records the collection command, nodeid digest,
  boundary classification, and owner before the family was rejected.
- `stale-closeout-state` (strong) — Slice B was marked complete while final and
  user-verification prose still described Slice A as active, and the first
  critique packet became stale after the ledger repair. Decision: same waste,
  fix now. Proof: the goal frame, final sections, refreshed packet, and critique
  identity were reconciled before closeout preparation.
- `gate-baseline-runtime` (strong) — mutation coverage consumed a 120.2s
  median and dominates the full local path. Decision: valid follow-up outside
  the slice. Proof: D51 names the quality-gate owner and reopen context; the
  CLI candidate was not mapped to that lane.
- `review-snapshot-selection` (moderate) — the first boundary verify used the
  helper's stale default snapshot and was discarded. Decision: valid follow-up
  outside the slice. Proof: every authoritative reviewer window in this goal
  records its explicit `/tmp` before snapshot and clean `drift: []` result;
  follow-up: issue #506
- `supporting-probe-drift` (strong) — adding the durable manifest changed a
  checked-in quality corpus and exposed a stale inventory-marker probe during
  the full gate. Decision: same waste, fix now. Proof: the repository-owned
  measurement script regenerated the top-level and recursive values, and the
  pinned probe now matches both live reruns.

## Critical Decisions

- Kept the ten-second full-command bar fixed before implementation and rejected
  the 3.62s named CLI family without shaping a migration.
- Treated the 31.60s heterogeneous nested-CLI subset as an upper-bound signal,
  not causal end-to-end relief.
- Preserved all process, packaging, environment, failure, and mutation-proof
  boundaries because no selected family demonstrated an owned ordinary fact
  worth moving in-process.
- Kept mutation-lane optimization deferred to D51 because the current mapper
  does not select the CLI family.

## Trends vs Last Retro

The prior durable retro is for a different goal and has no comparable
goal-scoped host metric window. Qualitatively, this goal repeats the useful
pattern of rejecting a tempting local speed signal when a distinct observer
finds that its ownership and end-to-end attribution are unproven.

## North Star Alignment

- Held the north-star rule for reversible work by measuring and falsifying the
  named family locally without publication or irreversible side effects.
- Held the proof-boundary rule by keeping child-process and packaging claims
  separate from in-process classification, and by using delegated fresh-eye
  reviews with explicit boundary snapshots.
- Mis-applied the standard briefly in the artifact state: stale Slice A prose
  and a superseded packet made the current decision harder to observe. The
  repair was to refresh the packet and reconcile every closeout surface before
  claiming completion.
- The failure signature was “a measurable subset is not a measured fix.”

## Expert Counterfactuals

- Ousterhout's design lens would have required the node-level family interface
  before accepting any file-count inventory as a refactor boundary. The next
  session should begin with the manifest and owner, not with a helper design.
- Klein/Kahneman's decision-quality lens would have precommitted the ten-second
  falsifier and the full-command attribution test before looking at the 31.60s
  subset. That would have prevented the ad hoc exclusion probe from acquiring
  migration-like status.

## Next Improvements

- Workflow: require a reproducible node-level manifest and boundary ledger
  before any broad runtime candidate enters implementation. This was applied
  in-session in the goal artifact and checked-in manifest.
- Workflow: rerun corpus-pinned measurement probes after adding durable quality
  artifacts. This was applied in-session by synchronizing the inventory-marker
  probe through its repository-owned measurement script.
- Capability: add a future repo-local guard that rejects stale default reviewer
  snapshots when an explicit before-path is required; issue #506 carries the
  separate helper-level design.
- Quality: investigate the mutation/quality-gate baseline under D51 rather than
  optimizing the unmapped CLI family; issue #505 carries the observed runtime
  and proof-preserving target.

## Sibling Search

- same layer: goal candidate scorecards and Slice Logs | decision: same waste, fix now | proof: reconciled the named-family manifest, packet identity, and final disposition in this goal
- abstraction up: `scripts/run-quality.sh` phase ownership and D51 | decision: valid follow-up outside the slice | proof: mutation is the 120.2s critical phase and D51 names its owner; follow-up: issue #505
- specialization down: `tests/charness_cli/support.py` and the 155 collected nodes | decision: intentional boundary | proof: 58 nodes retain real CLI delivery proof and the family is below the materiality bar
- mental-model siblings: critique packet binding and reviewer boundary fingerprints | decision: valid follow-up outside the slice | proof: stale packet/default snapshot events were explicitly corrected for this goal, while the helper-level guard is issue #506; follow-up: issue #506

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-04-132934-packet.md`

## Host Metrics

Host metric window: absent. The host did not expose a goal-scoped session file or
window; the three full-run receipts and focused runner receipt are explicit
timing evidence only.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-04-reduce-closeout-runtime-structural-waste-retro.md
helper.
