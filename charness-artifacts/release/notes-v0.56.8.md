# Charness v0.56.8

## Scope

A single focused change: the boy-scout **dup-ratchet quality gate** (and its clone
advisory) stop keying code-clone newness on nose's `family_id` and now key on a
gate-computed, offset/path-independent **content fingerprint**. This resolves
deferred decision D30 — the gate's long-standing false hard-block whenever an edit
to any scanned file shifted a duplicated span's line offset (nose's `family_id`
folds line offset and file path, so an unchanged duplicated span re-keyed on every
incidental member-file edit and forced a manual re-baseline with zero new
duplication).

## What Changed

- A new `nose_fingerprint_lib` computes each clone family's identity from member span
  CONTENT only (a sha256 over the sorted, duplicate-preserving, rstrip-normalized
  member spans), excluding line offset and file path. A pure line-shift no longer
  produces a "new" family; a genuine span-content change still rotates the
  fingerprint, so real new/changed duplication is caught with no false-negative. The
  v1 fingerprint is rstrip-only normalization, so an in-place comment/whitespace edit
  inside a duplicated span and a membership change (adding/removing a copy) remain
  deliberate re-baseline triggers — see `references/dup-ratchet.md`.
- The gate baseline (`dup-ratchet-baseline.json`), the clone-advisory baseline
  (`nose-baseline.json`), and the `dup-review.json` reviewed-overlay are migrated in
  lockstep to the new fingerprint identity (`code_family_fingerprints`, schema
  `dup_ratchet_baseline.v2` / `nose_baseline.v3`); the overlay's reviewed
  classifications are re-keyed in place. Six already-stale orphan overlay entries
  (whose families had vanished from the live scan before this change, so they
  suppressed nothing) were dropped — their notes remain in git history — and every
  still-live classification's operator note is preserved.
- Both baselines additionally stamp a `fingerprint_algo_version`; the gate now warns
  (never degrades) on either a nose-version skew or a fingerprint-algorithm skew, so
  a future normalization change reads as "re-baseline", not a corpus-wide false block.
- The `nose` tool manifest floor is reconciled to `>=0.15.0`. This is a metadata
  correction, not a new requirement: the committed baselines were already seeded on
  nose 0.15.0 in v0.56.7 while the manifest still read `>=0.14.0` (stale drift). The
  family SET nose groups is scanner-version-scoped, so the floor now matches the
  baselines' real provenance.

## Consumer Impact

- Charness's own committed baselines are migrated in this release, so the
  maintainer gate is green out of the box.
- **A consumer repo that has opted into the `dup_ratchet` gate with its own
  committed baseline** (keyed on the old `code_family_ids`) will, after
  `charness update`, read that legacy baseline as unrecognized and **degrade the
  gate to advisory (this path never false-blocks)** until the consumer re-baselines
  once: `check_dup_ratchet.py --write-baseline` and `inventory_nose_clones.py
  --write-baseline` in lockstep. This is a one-time re-baseline, not a breaking
  change; the gate stays safe (advisory) in the interim.
- **A consumer scanning with a nose version other than 0.15.0** is a distinct path:
  families can REGROUP, drifting the fingerprint set. That surfaces a scanner-version
  skew WARNING and — unlike the legacy-baseline path — does NOT auto-degrade, so it
  CAN hard-block on the drift until a per-version re-baseline. Relatedly, the floor
  bump to `>=0.15.0` means a consumer pinned to nose 0.14.x and using the gate must
  update nose (`charness tool update nose`) to satisfy the manifest.
- A consumer not using the `dup_ratchet` gate is unaffected.

## Verification

The release bundle is verified through the repo-owned release helper, which runs the
version bump, generated surface sync, quality gate, fresh-checkout probes, tag and
branch push, public release creation, distinct-channel verification, and maintainer
install refresh. Before this release: the full pytest suite (3797) and
`run-quality.sh --read-only` (79/0, live dup-ratchet phase PASS) were green; the
change carried bounded fresh-eye spec and implementation critiques.

## Upgrade

Run `charness update`, then restart existing Codex or Claude sessions that should
load the refreshed plugin surface. Consumers using the `dup_ratchet` gate with a
committed baseline: re-baseline once (above) after updating. No other migration step
is required.
