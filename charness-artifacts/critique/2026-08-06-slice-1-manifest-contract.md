# Critique Review
Date: 2026-08-06

## Decision Under Review

Define Slice 1 as a narrow, checked-in JSON identity manifest plus a deterministic
validator/loader for the post-push baseline. The manifest must bind the exact
target and carrier SHAs, captured remote observations, critique evidence, and
owner-referenced source/plugin/consumer reader roots without becoming a workflow
or issue-state store.

## Failure Angles

- Identity and stale-state failure: a branch name, abbreviated SHA, mismatched
  carrier, or CI readback for another commit could be accepted as the baseline.
- Ownership and portability failure: a fixed `skills/` → `plugins/charness/`
  assumption could omit exported `scripts/`, or the manifest could silently
  become a second packaging/surface contract.
- Proof-surface failure: a local validator could report a green result for
  absent, stale, or live/provider evidence it did not actually observe.

## Counterweight Pass

The first slice should not add command arrays, gate selection, execution order,
automatic sync/publish behavior, universal root discovery, or provider/consumer
runtime checks. Those concerns are valid later only when their owning slices have
a concrete consumer. The narrow identity/root contract is still required now:
later premise and bundle preflights need one stable record, and a stale identity
must fail before those consumers act.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: manifest target/carrier and remote-readback fields | action: fix | note: require full 40-hex SHAs, explicit carrier relation, and exact readback SHA equality; reject branch names, abbreviations, and mismatches.
- F2 | bin: act-before-ship | evidence: strong | ref: packaging/charness.json and .agents/surfaces.json | action: fix | note: make reader roots owner-referenced and portable; do not duplicate packaging or generated-surface ownership in the manifest.
- F3 | bin: act-before-ship | evidence: strong | ref: validator proof fields | action: fix | note: keep captured remote evidence distinct from live revalidation and refuse missing/stale/ambiguous proof rather than emitting a terminal claim.
- F4 | bin: bundle-anyway | evidence: moderate | ref: fixture matrix | action: fix | note: cover valid baseline, malformed schema, unsafe paths, missing roots, SHA mismatch, source/plugin mismatch, and incomplete captured evidence.
- F5 | bin: over-worry | evidence: weak | ref: later workflow fields | action: defer | note: universal scheduling, cryptographic external attestation, full-repository hashing, and installed-provider discovery are not Slice 1 requirements.
- F6 | bin: valid-but-defer | evidence: moderate | ref: future preflight and ledger slices | action: defer | note: live origin refresh, generalized carrier relations, generated proof-command bundles, and immutable publish reconciliation belong to their named later slices.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: unverified — the spawn surface accepted the requested fields but exposed no provider-application confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct angle reviewers (identity, portability/ownership,
proof-surface behavior) and one separate counterweight returned findings. The
parent-side boundary fingerprint for window `slice1-design-round1` verified clean
after the reviewers returned; no worktree, index, or HEAD drift was observed.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.md` for commit-boundary currency; the design fresh-eye findings were originally produced from the earlier design packet.
- Packet path: `charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.json`
- Packet SHA256: `59de83bfdc017d8fb82ee6294ec2da799054a81736855d2cef9d64687a508e7a`
- Identity SHA256: `18ebbe13e8824992a1a0d41a704f8e6015169c163e75e635805c2b0407ab19ef`

## Boundary Ownership

- Producer: `packaging/charness.json`, `.agents/surfaces.json`, and the
  manifest validator produce/verify the declared reader-root identity; GitHub
  and GitHub Actions remain producers of issue/CI state.
- Consumer: later premise preflight, final-bundle preflight, and publish-ledger
  reconciliation consume the manifest identity without replacing those owners.
- Owning surface: the slice manifest and validator own execution/proof identity;
  packaging, surfaces, GitHub, and Actions retain their existing state ownership.
- Verdict: owned-correctly
