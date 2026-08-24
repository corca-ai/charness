# Issue #714 Round-2 Resolution Critique

Date: 2026-08-24

## Reviewed Input

- Round-1 packet: `charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.json`
- Round-1 packet SHA-256: `7787421dc8e67bb587caaaa152116ca8cdb218bc389899f43faa82f195e5ae85`
- Round-1 reviewed identity: `955e6a8aa5930d75db86d65e5bd75410685aba2ffa7cccbe1e89d628517bd1e6`
- Round-2 packet: `charness-artifacts/critique/2026-08-24-issue-714-round2-packet.json`
- Round-2 packet SHA-256: `ef31225ba7dd356db5d384bc201dbc65f35895ae98c7cdbf55ea678c2b137878`
- Round-2 reviewed identity: `10f99ee46f8972bef797056d17aa2e943809f8fdeba880ef65d331471bdfa4eb`
- Fresh-eye satisfaction: `parent-delegated`, read-only; boundary fingerprints verified clean.

## Review Findings and Repairs

Round 1 found that process diagnostics could cross run ownership through
inter-run wrapper chatter and that a trailing duration-shaped fragment could
supersede the real TAP run. The first repair introduced one selected-run window
and paired regressions for those structures.

Round 2 proved that the repaired verdict surface still had three false-kill
paths: compact TAP could drop an earlier owned result, a later TAP-like header
could erase an earlier file diagnostic, and incomplete or internally
inconsistent summaries were accepted through zero-filled counts. These are
blockers because each can turn an unreadable or process-broken mutant run into a
`killed` verdict.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: the parent reused the existing bounded reviewer
  context under the host's inherited model controls; no model override was sent.
- Host exposure state: host-defaulted
- Application state: the reviewer context was delivered and findings were
  received; effective runtime model metadata was not independently exposed.
- Delivery state: findings-received.

## Accepted-Unreviewed Cap Repair

- One `_NodeRun` owner now binds candidate text, validated summary, and typed
  counts.
- A candidate requires unique verdict-critical keys, a plan matching `tests`,
  count arithmetic matching `tests`, and top-level result numbers exactly
  covering `1..N`.
- Explicit candidates try structurally valid headers without letting a later
  header erase earlier selected-run diagnostics; compact candidates derive
  their start from all plan-owned result records.
- Direct reporter and `classify_mutant_run` regressions cover all three round-2
  falsifier families and retain the round-1 axes.
- The two-round proof-surface cap is consumed. These repairs are
  accepted-unreviewed; no third semantic review or approval is claimed.

## Corrected Identity Binding

The round-1 `changed_ref: HEAD` packet is retained as failure evidence; it bound
the old committed substrate and is not closeout proof. The round-2 packet bound
the pre-cap working tree. The final cap repair is therefore captured by a new
working-tree packet with `changed_ref: null`:

- Packet: `charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.json`
- Packet SHA-256: `3e6038f4b24df4f080d00c87fbba1c69831a77b954cd89e3c361df67806f9c33`
- Reviewed identity: `4c2497fa9293ab5b0f8fe85653917ffb405e2667ac20d335653cc984fa877a5e`
- Verifier command is embedded in the packet and must report `ok: true`,
  `status: current` before commit.

## Capability and Delivery Non-Claim

An attempted file-backed worker review reported that it could not read the
declared files. That is a worker capability non-claim, not a GitHub or `gh`
authentication failure and not review evidence. The actual parent-delegated
round-2 reviewer supplied the findings above. A clean boundary fingerprint for
the failed worker proves only that it did not alter the checkout.

## Boundary Ownership

- Producer: `NodeTestReporter._selected_run` and its structural validator.
- Consumer: mutation accounting through `classify_mutant_run`.
- Owning surface: one selected `_NodeRun` carries summary counts and process
  diagnostics from the same complete observation window.
- Verdict: moved-to-owner

## Structural Follow-up

- #718 tracks the general packet-substrate mismatch that allowed historical
  `HEAD` content to verify as current while the intended worktree differed.
- The operator's guessed packet-generator path failed before execution. The
  recovery was repository discovery followed by the canonical
  `skills/public/critique/scripts/prepare_packet.py` interface, not an unchanged
  retry. This is the same command-shape/locator family already being recorded in
  the session RCA rather than a product-auth failure.

## Non-Claims

- Changed-line mutation proof is not claimed until the repair is committed and
  a non-degenerate base-to-head range can be tested.
- No issue was closed or commented on, and no push, release, PR, tag, version
  bump, installed-cache adoption, or Cautilus run occurred.
