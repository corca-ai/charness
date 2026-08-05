# Issue #506 Resolution Critique
Date: 2026-08-05

## Decision Under Review

Make reviewer-boundary verification reject an unqualified canonical default
snapshot unless the caller supplies `--window-id`; preserve explicit `--before`
verification, parent attribution, legacy snapshots, and the checked-in plugin
mirror.

## Execution

Executed as a delegated code critique with three bounded angle reviewers and a
separate counterweight reviewer. All four review windows returned before any
parent write and verified `clean` with no parent declarations:

- Jackson: `issue-506-critique-jackson`
- Weinberg: `issue-506-critique-weinberg`
- Gawande: `issue-506-critique-gawande`
- Counterweight: `issue-506-critique-counterweight`

## Fresh-Eye Satisfaction

parent-delegated — four unnamed fresh-eye reviewers returned findings inline;
each boundary verify was exit 0 with `verdict: clean` and `drift: []`.

## Packet Consumed

- Packet path: `charness-artifacts/critique/2026-08-05-054651-packet.json`
- Packet SHA256: `0e7f19d0d5d34e8a528e9e2e5945e0936f43a0a43bd3b56cc29227104b970a52`
- Identity SHA256: `f2ac69d10ab1d4d9a9797d554263bd719ed670e61985e80612d7f81d37afb418`

## Target

Code critique, shaped by the Jackson problem-framing, Weinberg diagnostic, and
Gawande operational angles, followed by a distinct counterweight pass.

## Diff Scope

The helper, its checked-in plugin mirror, focused boundary/parity tests, the
debug record, and the operating-contract invocation example.

## Change

The default snapshot path is now fail-closed unless the verify command carries
`--window-id`. A caller may instead identify the evidence with an explicit
`--before <snapshot-path>`, which preserves the existing legacy and attribution
semantics for deliberately selected paths.

## Capability at Stake

The parent must be able to distinguish a clean reviewer-boundary proof from a
verdict rendered against an unspecified or stale review interval.

## Angles

- Jackson: the change closes the reported JTBD without turning explicit path
  selection into a new failure mode; `Bundle Anyway`.
- Weinberg: the guard is at default-path identity resolution, before drift
  attribution and verdict rendering; source/plugin parity and parent-attributed
  exits remain downstream and intact; `Bundle Anyway`.
- Gawande: canonical-path detection could prevent spelling the default path as
  `--before`, but that would redefine explicit path selection; sent to the
  counterweight rather than folded automatically.

## Findings

The implementation is at the diagnosed cause, tests the new refusal and the
preserved explicit-path behavior, and keeps the plugin mirror byte-identical.
The round-2 repaired-surface review found no verdict-logic blocker and one
documentation correction, which was applied before this critique: the operating
contract now shows a complete executable `--before <snapshot-path>
--window-id <id>` invocation.

## Counterweight Triage

- Act Before Ship: none.
- Bundle Anyway: preserve the default-path refusal, matching/mismatched window
  checks, explicit-path compatibility, parent attribution, and mirror parity;
  all are in the current change and focused tests.
- Over-Worry: requiring `--window-id` whenever an explicitly supplied path
  happens to resolve to `.charness/reviewer-boundary/snapshot.json`. This would
  require a new canonical-path normalization/symlink contract and would narrow
  the deliberately supported explicit `--before` boundary.
- Valid but Defer: none.

## Deliberately Not Doing

No parity-harness redesign, no canonical-path alias detection, no mandatory
window id for noncanonical explicit snapshots, and no host-installed/provider
behavior claim. The existing debug artifact records these scope boundaries.

## Defect Class Cross-Link

The stale implicit-proof-input pattern is cross-linked to
`charness-artifacts/retro/recent-lessons.md`; #506 is the owning helper-level
repair rather than a new adjacent issue.

## Capability Gap

None identified. The repository exposes the helper, deterministic focused tests,
the plugin mirror, and an executable operator contract.

## Pre-Merge Action

None. The second verdict-logic review found no blocker; its documentation minor
was repaired and accepted unreviewed under the repository's two-round cap.

## Boundary Ownership

- Producer: `reviewer_boundary_fingerprint.py` captures/reads the snapshot and
  renders the drift verdict.
- Consumer: the review parent reads that verdict as evidence before accepting a
  bounded reviewer boundary.
- Owning surface: reviewer-boundary helper plus its invocation contract.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: four unnamed bounded spawns were accepted and returned
  findings inline to the parent.
- Delivery state: findings-received

## Next Move

Run the closeout gates, publish the direct-commit carrier, push only if the
pre-push gate passes, and verify GitHub reports #506 CLOSED through the adapter.
