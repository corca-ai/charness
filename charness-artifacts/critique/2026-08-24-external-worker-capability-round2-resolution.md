# External Worker Capability Round-2 Resolution Critique

Date: 2026-08-24

## Reviewed Input

- Round-1 packet: `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.json`
- Round-1 packet SHA-256: `7253c6f654a16808434c569c4faa4efc8d5d0b62acf134b454a950de89c37f0e`
- Round-1 reviewed identity: `1ca49554044af210b4b379dc2ac051cb88a9f8a4f80dc2271153f3115dd6d107`
- Round-2 packet: `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.json`
- Round-2 packet SHA-256: `9b1f923b5592af7634f8c66210815bcf3a99eefea254c775c0284ac81ce02b56`
- Round-2 reviewed identity: `69ab801fe2313de14a40b6eae0bca4754bda4ca6f58bfd248e60c4f66d35a001`
- Both fresh-eye runs were parent-delegated and read-only; boundary fingerprints
  verified clean.
- Fresh-eye satisfaction: accepted-unreviewed-under-round-cap two-round proof-surface cap consumed after delivered round-2 findings.

## Round-1 Findings and Repairs

Round 1 blocked approval because capability target identity was not joined to
the delivery ledger, deny-all/optional policy could be ignored, timestamp
freshness was under-specified, and path confinement admitted bypasses. Repairs
bound the exact target set and launch/collection envelope hashes across the
attempt chain, enforced required/optional policy, narrowed freshness to
same-attempt evidence, and confined resolved worker paths to the declared repo
root.

## Round-2 Verdict

`FAIL / repair required`. The two-round proof-surface cap is consumed.

Round 2 found two approval blockers. Optional-target non-claims were accepted by
substring, so contradictory prose could fail open, and the result/report chain
did not bind those non-claims to the launch envelope. The nominal `live`
freshness enum also accepted stale and future timestamps. Two recovery hazards
were valid but deferred: retry lineage accepts active/foreign attempts, and the
runner can terminalize a ledger before the complete receipt/report chain is
validated. #719 owns those recovery-path defects.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: the parent reused an existing bounded reviewer under
  host-inherited controls; no model override was sent for the review.
- Host exposure state: host-defaulted
- Application state: reviewer findings were delivered; effective runtime model
  metadata was not independently exposed.
- Delivery state: findings-received.

## Accepted-Unreviewed Cap Repair

- Optional non-claims are now structured, target-bound records with canonical
  statement/scope, per-record identity, and a collective digest.
- The exact record set and digest are joined through capability envelope,
  worker result, receipt, combined report, and installed carrier. Contradictory,
  missing, reordered, or foreign-target non-claims fail closed.
- The misleading `live` vocabulary was removed. Only same-attempt evidence is
  accepted, with deterministic stale/future timestamp regressions.
- Capability-specific launch, collection, non-claim, failure-adaptation, and
  receipt lifecycle moved into `reviewer_worker_capability.py`; the generic
  runtime remains responsible for process lifecycle, schema/result validation,
  and atomic publication.
- Focused capability/worker/report/runner/carrier/delivery proof passes 98 tests.
- These repairs are accepted-unreviewed under the two-round cap. No third review
  or semantic approval is claimed.

## Hard-Gate Failure Disposition

The cap-repair worker initially described `reviewer_worker_runtime.py` at 364
tokei Python code lines as advisory even though the configured limit is a hard
360. That claim was rejected. The ownership extraction above reduced the runtime
below the hard limit. An independent Ruff pass then found C901 complexity in
preflight validation and runtime process execution, which the worker's unstaged
no-op pre-commit had not tested. Per-target policy checks were separated and
generic subprocess lifecycle moved to the existing `reviewer_process.py` owner;
Ruff now passes without suppression. The runtime is 345 lines and remains in
the `[330, 360]` advisory band; the reviewer had already judged the remaining
generic runtime cohesive, so this is recorded as headroom debt rather than
hidden or line-shaved.

## Corrected Identity Binding

The round-2 packet used `changed_ref: HEAD`; it is retained as review lineage and
failure evidence, not final worktree closeout proof. #718 owns the general
wrong-substrate verifier escape. The complete cap repair is bound by:

- Packet: `charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.json`
- Packet SHA-256: `f99cbe0b6fcb14d88a9c273e51c97e5ea56716f1967f3f957ce8426f8e76ba7c`
- Reviewed identity: `058a2fa83e3fe85a2aeaf4ff240964a7b92442e620a45b38bf9b347c3d1758f1`
- Mode: working tree, `changed_ref: null`; all implementation,
  source/plugin/schema/test and RCA paths then present in `git status` are
  explicitly reviewed. This resolution artifact is excluded to avoid a
  self-referential packet hash and is validated independently.

## Failure Pattern and Pattern-of-Pattern

- Direct pattern: lexical or nominal capability proxies (`unavailable` in prose,
  `live` as an enum, a worker's own selector claim) were trusted without binding
  the producing observation to its target, attempt, consumer, and evidence time.
- Higher-order pattern: boundary outputs lose producer/version/scope/lifecycle
  identity, then later stages infer provenance from content shape. The structural
  answer is one typed identity chain with exact hashes and explicit non-claims,
  not a retry or a narrower stimulus.
- Operational instance: inline shell prompts allowed backtick command
  substitution. Subsequent Codex workers receive file-backed prompts through
  stdin so prompt content is not interpreted by the shell.

## Boundary Ownership

- Producer: host adapter/preflight creates a typed capability envelope for one
  attempt and target set.
- Consumer: worker launch/collection, result validator, receipt/report builder,
  installed carrier, and delivery ledger.
- Owning surface: `reviewer_capability.py` owns canonical envelope semantics;
  `reviewer_worker_capability.py` owns the worker-facing lifecycle; report and
  carrier boundaries revalidate but do not invent capability facts.
- Verdict: moved-to-owner

## Non-Claims

- #719 retry lineage/terminalization is not resolved by this slice.
- The 345-line runtime advisory is not claimed clean or resolved.
- A backend's prose cannot prove its launch model, host selector availability,
  authentication, or external-read capability.
- Installed Charness/Ceal adoption remains unproven and is tracked separately by
  #715 and the Ceal follow-ups.
- No issue was closed or commented on, and no push, release, PR, tag, version
  bump, installed-cache mutation, or Cautilus run occurred.
