# Debug Seam Index Round-2 Resolution Critique

Date: 2026-08-25

## Reviewed Input

- Proof surface: `scripts/build_debug_seam_risk_index.py` and its checked-in
  plugin mirror.
- Regression surface: `tests/quality_gates/test_debug_seam_risk_index.py`.
- Repaired corpus: the three 2026-08-24 debug interrupts, their matching spec
  handoffs, and `charness-artifacts/debug/seam-risk-index.json`.
- Fresh-eye satisfaction: parent-delegated, read-only reviewers with shared-tree
  boundary fingerprints.

## Quarantined First Attempt

The first review returned no blocker, but the parent refreshed the retro lesson
index while its boundary window was open. Fingerprint verification returned
`boundary-drift` on the lesson index and current retro, so that review is
quarantined and supplies no approval. The retry used a different reviewer and a
fresh snapshot; verification returned `clean` with no drift.

## Round-1 Findings and Repairs

The clean retry found two blockers. `latest.md` was deduplicated only when it
resolved to the same path as a dated record, so byte-copy and hard-link pointer
layouts counted one interrupt twice. Malformed UTF-8 escaped the new diagnostic
batch as a traceback.

The repair deduplicates symlink and hard-link pointers by filesystem identity,
then substitutes a regular `latest.md` for the newest equal-content dated record.
Only the pointer gets content deduplication; two dated records with equal bytes
remain distinct. Decode/read failures join the same path-bound invalid-artifact
batch. Regressions cover symlink, hard-link, byte-copy, and malformed UTF-8
layouts.

## Round-2 Findings

Round 2 verified the pointer repair, multiple-identical-dated-record behavior,
malformed UTF-8 batching, no-write-on-invalid behavior, and source/plugin parity.
It then found one blocker: a broken `*.md` symlink failed during the initial
`stat()` walk before the batch handler. Raw `OSError` reasons could also carry an
absolute checkout path, making diagnostics environment-dependent.

## Accepted-Unreviewed Cap Repair

- Discovery-time `stat()` failures now join the invalid-artifact batch.
- Filesystem and Unicode failures render a stable error kind and explanation;
  the outer record carries the repo-relative artifact path, so raw absolute
  paths are not repeated inside reasons.
- The expanded discovery logic is split into pointer-normalization helpers after
  the full lint gate exposed a complexity-budget breach; no lint threshold or
  exception was weakened.
- The batch regression includes a broken symlink and asserts that the temporary
  repo root is absent from stderr.
- The focused suite passes 7 tests, source/plugin copies are byte-identical, and
  both source and plugin entrypoints validate the 160-source/146-indexed corpus.
- The two-round proof-surface cap is consumed. These round-2 repairs are
  accepted-unreviewed; no third semantic review or approval is claimed.

## Reviewer Tier Evidence

- Requested tier: inherited host default
- Requested spawn fields: none; existing bounded reviewer contexts were reused
- Host exposure state: host-defaulted
- Application state: both clean-window findings were delivered; effective model
  metadata was not independently exposed.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap — round 1 found pointer-identity and decode
batching gaps; round 2 read those repairs and found the discovery-time broken
symlink and absolute-path diagnostic gap. The round-2 repair has focused proof
but deliberately receives no third-round approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.json
- Packet path: charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.json
- Packet SHA256: 623307fd032470b5f295ab31210fcdeb3f569185c186c279d271a94059c2ede2
- Identity SHA256: 5aaa255b1050f043aa3bc538e6a41b4dc836d95072765e2ed85fc1df934bbdd0

The packet binds the final accepted-unreviewed working tree in working-tree
mode with `changed_ref: null`; its embedded verifier must report `ok: true` and
`status: current` before commit.

## Boundary Ownership

- Producer: a debug artifact and the adapter-selected `latest.md` pointer.
- Consumer: `build_debug_seam_risk_index.py` and its generated JSON index.
- Owning surface: one deterministic corpus walk binds each invalid reason to a
  repo-relative path and counts one current-pointer role once.
- Verdict: moved-to-owner

## Structural Follow-up

- #721 owns producer-bound scaffold/targeted-validation enforcement. Complete
  batch diagnostics reduce repeated reruns but do not prevent hand-authored
  malformed records from reaching broad quality.
- #720 owns stable lineage for reviewed duplicate families. This slice removed
  the real same-file Node duplication and reclassified three rotated identities;
  it did not solve volatile duplicate-review keys.
- #695 owns the critique-specific machine-field/shape-source drift that recurred
  when this hand-authored resolution omitted exact scaffold fields. Closed #334
  is the historical reviewer-tier precedent; no duplicate issue was filed.
- The parent-write-during-review-window recurrence was detected by the boundary
  rail, quarantined, and retried only after the stimulus changed to a clean,
  write-frozen window.

## Non-Claims

- The cap repair has no third fresh-eye approval.
- No issue was closed or commented on. No push, PR, release, tag, version bump,
  installed-cache mutation, or Cautilus run occurred.
