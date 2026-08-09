# v4.1.0 release claims review

Date: 2026-08-09

Scope: bounded read-only review of
`charness-artifacts/release/2026-08-09-v4.1.0-notes.md` against the current
`v4.0.0..HEAD` delta, version surfaces, compatibility shims, proof receipts,
and rollback guidance.

## Act Before Ship

1. The proof paragraph described release-candidate evidence before the 4.1.0
   version sync and final verification lock existed. It also generalized a
   real-host receipt bound to `v4.0.0..f62e283f` across the later 234-path
   candidate delta. The notes now state the exact pre-RC boundary and retain the
   final-range evaluation as pending.
2. The SLOC summary said the resolved output was the only exclusion, omitting
   the deliberate `.charness` runtime-state exclusion. The notes now distinguish
   the runtime exclusion from the exact generated-output exclusion.
3. The deprecated title-slug checker retained compatibility but did not tell
   direct callers where to migrate. The notes now direct callers to remove the
   advisory automation and use critique's `Title-Slug Coherence Review` for
   rename-heavy work.

## Confirmed

- `v4.1.0` remains an additive minor after preservation of advisory, strict
  0/1, legacy JSON, and four-path compatibility for the deprecated direct-call
  checker.
- The declaration-path claim is supported by exact/wildcard ignore,
  traversal, symlink-escape, and external-support-laundering tests.
- Update and rollback commands match the current CLI, including the explicit
  managed-CLI non-downgrade caveat for `--skip-cli-install`.
- Issue #576, Cautilus, hosted CI, public visibility, installed state, baton
  reconciliation, and issue closure remain honest non-claims.

## Reviewer Tier Evidence

- Requested tier: host default for bounded fresh-eye review.
- Requested spawn fields: existing agent context; no model override requested.
- Host exposure state: host-defaulted
- Application state: findings delivered; provider-side model metadata not exposed.
- Delivery state: findings-received

## Boundary Ownership

- Producer: release notes, current delta, version surfaces, and proof receipts.
- Consumer: installed users, hosted CI observers, and the public release record.
- Owning surface: release owns compatibility and publication claims; quality
  owns candidate-bound execution evidence; issue owns closeout state.
- Verdict: owned-correctly

## Evidence

- Reviewer boundary fingerprint: clean (`release-4.1.0-claims-review`).
- Packaging and source/plugin mirror checks passed in the reviewer context.
- Focused title/declaration tests: 22 passed.

Fresh-Eye Satisfaction: parent-delegated. Round-one repairs are accepted. The
candidate-bound proof paragraph was updated before publication from the final
lock, five fresh-checkout probes, and exact 240-path real-host trigger receipt
bound to code/test candidate `dfdcbf74`; hosted and public facts remain
non-claims.
