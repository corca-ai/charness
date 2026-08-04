# Structural closeout runtime candidate premortem
Date: 2026-08-04

## Decision Under Review

Whether to lock a broad in-process replacement for the nested-CLI standing-test
surface, or first require a bounded owned-family spike that can prove material
same-command relief without removing process, packaging, environment, or CLI
failure proof.

## Target

Decision premortem, because no implementation diff exists yet. The reviewed
candidate was selected from Slice A's runtime and standing-test inventories.

## Change

The proposed change would move ordinary test assertions below a process boundary
while retaining thin real-entrypoint smokes. No code change is approved by this
record. The current decision is tightened to a bounded spike contract.

## Capability at Stake

Reduce the real local closeout journey by at least ten seconds on this Linux
runtime profile while preserving the proof facts that a child process currently
exhibits: interpreter and import startup, argv/CWD/PATH/environment isolation,
stdout/stderr and non-zero failure, source/installed packaging behavior, and
the changed-line coverage/consumer verdict where the target is mapped there.

## Angles

- **Jackson — problem framing:** the 194-file subset is material but not a
  causal end-to-end target. The full command is mutation-dominated at 120.2s,
  and the standing pytest phase is queued independently, so subset timing cannot
  establish ten-second full-command relief.
- **Weinberg — diagnostic and ownership:** the inventory counts spawn-shaped
  file text, not launches, nodeids, commands, or boundary purpose. The current
  `inventory_boundary_bypass.py --summary` reports 57 candidates, 1 clean
  in-process sample (`skills/public/release/scripts/check_real_host_proof.py`,
  release-only), 37 internal-boundary candidates, and 31 keep-boundary samples.
  A broad in-process helper would treat the outer launch as the cause without
  proving the inner boundary is ordinary duplicated work.
- **Gawande — operational proof checklist:** an eventual family migration must
  identify one in-process fact, one retained real-boundary success smoke, one
  controlled-failure smoke, and source-tree/installed-package probes where
  packaging is part of the contract. The existing in-process harness changes
  argv/environment and can retain module state, so it is not a drop-in proof
  of child isolation.

## Findings

The 194-file nested-CLI subset ran 3,443 tests in 31.60s, while an ad hoc
counterfactual excluding 209 targets ran 3,554 tests in 18.91s. Those are useful
selection signals only. The inventory's authoritative current counts are 212
nested-CLI files, 194 standing files, 14 mixed release-only files, 1
all-release-only file, and 210 standing-or-mixed files; the “209 targets” label
has no reproducible manifest and is not a migration unit.

The full read-only closeout median is 123.51s, with mutation coverage at 120.2s
and standing pytest at 48.9s. `run-quality.sh` queues those phases concurrently,
and the current mutation mapper selects goal/retro quality tests rather than
the CLI family. A standing-only saving therefore cannot be called end-to-end
relief without three matched full-command before/after observations.

## Repair Reassessment

The midpoint fresh-eye claims review blocked closure because the initial Slice B
record rejected only the broad proposal and did not test a named family. The
repair now binds the exact standing `tests/charness_cli` family to the checked-in
155-node manifest at
`charness-artifacts/quality/2026-08-04-reduce-closeout-runtime-structural-waste-cli-manifest.md`.
The manifest records 58 main-CLI-delivery, 3 internal-process, and 94
in-process-test nodes; its canonical focused runner passed 155 tests in 3.62s.
That is below the fixed 10-second bar, so this named family is falsified as the
first remedy target. The broad heterogeneous nested-CLI surface remains an
unowned selection signal, not a claim that every possible family is impossible;
future work needs a new owner and manifest rather than a repo-wide migration.

The repaired goal also reconciles its active frame, slice plan, final
verification, user instructions, and packet identity. The remaining closeout
claim is provisional until the separate disposition review reads the final
artifact.

## Counterweight Pass

- **Act Before Ship:** require a node-level manifest for one named family:
  nodeid, launched target, launch count, asserted behavior, boundary type,
  retained smoke, and owner. Require the full-command timing protocol before
  claiming materiality. Require the boundary ledger and retained success,
  controlled-failure, and packaging smokes before converting any process proof.
- **Bundle Anyway:** keep the exact inventory command, current boundary-bypass
  payload, command/corpus identity, and the 31.60s subset as an explicitly
  labelled upper-bound selection signal in the goal record.
- **Over-Worry:** do not demand cross-host, CI, cache, remote, or parallel-runner
  evidence for this local reversible decision; those are outside the goal.
- **Valid but Defer:** investigate the mutation lane separately once a selected
  family proves a changed-mapper relationship. Do not build a repo-wide in-process
  harness or broad migration before one family demonstrates both clean ownership
  and plausible materiality.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `skills/public/quality/scripts/surface_marker_lib.py:8` and goal Boundaries | action: fix | note: replace the heterogeneous file-count candidate with a node-level owned-family manifest and boundary ledger
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/run-quality.sh:556` and goal Slice A timing bundle | action: fix | note: require three matched full-command before/after observations before any ten-second relief claim
- F3 | bin: act-before-ship | evidence: strong | ref: `scripts/inventory_boundary_bypass.py --summary` and `skills/public/quality/references/boundary-bypass-ratchet.md:77` | action: document | note: retain child-process proof for packaging, environment, argv, stderr, exit-code, and recovery contracts
- F4 | bin: bundle-anyway | evidence: strong | ref: goal Slice A scorecard and `/tmp/charness-structural-goal-nested-cli-1.log` | action: document | note: preserve the subset timing as an upper-bound selection signal, never as causal end-to-end relief
- F5 | bin: over-worry | evidence: weak | ref: goal Non-Goals | action: defer | note: cross-host and remote proof are not needed for this local decision
- F6 | bin: valid-but-defer | evidence: moderate | ref: goal Slice A mutation mapper finding and `docs/deferred-decisions.md#d51` | action: defer | note: revisit mutation-lane structure only after a family proves mapping and materiality

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, fork_context=false; the host schema exposed no `fork_turns` field to the caller.
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no applied claim made.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct angle reviewers and one separate counterweight
reviewer returned findings in the parent context. Angle boundary window
`structural-runtime-premortem-20260804` verified with `verdict: clean`,
`drift: []`, no parent-declared paths, no staged paths, and no HEAD movement
using the explicit snapshot `/tmp/charness-reviewer-boundary-structural-runtime.json`.
Counterweight window `structural-runtime-counterweight-20260804` verified with
the same clean result using
`/tmp/charness-reviewer-boundary-structural-counterweight.json`. The initial
verify without `--before` read an older repository snapshot and was discarded;
the explicit before-path verifies are authoritative for these windows.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/structural-runtime-final-packet.json`
- Packet path: `charness-artifacts/critique/structural-runtime-final-packet.json`
- Packet SHA256: `d8c9eb623182284b4c13e0648960a734585defa3c17525dccb09572070809451`
- Identity SHA256: `a2429b2a1c7ed9faaa8ea48be4e5dc8f9574d62fb2415d79aa7573443b41aa2b`

## Boundary Ownership

- Producer: the standing-test economics and boundary-bypass inventories produce
  candidate signals; the test files and entrypoint scripts produce the actual
  process-boundary behavior; `run-quality.sh` produces the phase verdicts.
- Consumer: the active goal's operator, the standing quality runner, and the
  closeout claims reviewer consume the candidate and its timing/proof claims.
- Owning surface: the goal artifact owns the candidate decision contract;
  each selected test family and entrypoint owns its own boundary proof. A
  repo-wide in-process migration is not owned by one current surface.
- Verdict: escalated-to-issue-spec — broad migration remains unowned; the
  named standing CLI family is owned enough to reject on measured materiality.

## Verification

- `python3 scripts/inventory_boundary_bypass.py --repo-root . --summary` returned
  the current 57/1/37/31 candidate summary; the one clean sample is release-only.
- Three clean `./scripts/run-quality.sh --read-only` receipts passed 85/0 at
  HEAD `23f60313ca9c58a4bac235166966b87a5f3bbb37`; medians were 123.51s total,
  48.9s standing pytest, and 120.2s changed-line mutation.
- `python3 scripts/inventory_standing_test_economics.py --repo-root . --summary`
  reports 194 standing nested-CLI files; the measured subset and corrected
  test-module-only exclusion probe are recorded in the goal Slice Log. The
  named-family manifest independently binds 155 collected nodes to its 3.62s
  runner receipt.
- No implementation, gate, validator, test, or export surface changed from
  this premortem. No provider, remote, release, push, issue-close, or Cautilus
  proof is claimed.

## Deliberately Not Doing

No broad in-process harness, test pruning, global runner change, gate relocation,
cache reuse, or parallelism is being locked. No “209 targets” manifest is being
treated as real until a producer can emit one. The release-only clean boundary
sample is not generalized to the standing closeout path.

## Next Move

Do not implement the broad replacement. The named `tests/charness_cli` family
now has its manifest and boundary ledger and is rejected at 3.62s. Record the
no-safe-change disposition for this candidate and carry D51 forward without
weakening proof; any future family must start from a fresh owner, manifest, and
full-command materiality test.
