# R596 D47 Snapshot Critique

Date: 2026-08-12

## Execution

Two bounded, read-only fresh-eye rounds reviewed the D47 snapshot slice. The
reviewer boundary fingerprints for both rounds verified clean.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- Requested tier: n/a — host inherited the session model.
- Requested spawn fields: unnamed bounded read-only reviewer scope, exact paths,
  and blocker/major/minor reporting through the host agent interface.
- Host exposure state: metadata-hidden
- Application state: the host returned no reviewer-tier application metadata.
- Delivery state: findings-received

## Boundary Ownership

- Producer: `measure_inventory_marker_rule.py` produced the 2026-08-12 payload;
  the dated snapshot owns that frozen evidence.
- Consumer: D47 renders four dated headlines, while the focused test verifies
  the document-to-snapshot binding.
- Owning surface: D47 measurement evidence.
- Verdict: owned-correctly

## Target

Code critique: D47's measurement evidence, its immutable JSON snapshot, and
the focused proof surface.

## Change

Replace D47's corpus-sensitive equality pins with an immutable, dated,
SHA-256-bound snapshot. Keep four dated headline figures in D47, and test the
snapshot's provenance, document binding, and measurement invariants without
rerunning a later corpus.

## Capability at Stake

An operator can read D47 as evidence for a deferred policy without ordinary
quality-artifact growth forcing a historical decision record to be regenerated.

## Findings and Counterweight Triage

- R1-F1 | act-before-ship | D47 retained a "current corpus" sentence pointing
  to deleted refresh bullets. Removed it and replaced the live claim with the
  immutable 2026-08-12 snapshot boundary.
- R1-F2 | act-before-ship | A filename-plus-hash assertion did not bind D47's
  four rendered headlines to the snapshot payload. The focused test now parses
  and compares all four headline values.
- R1-F3 | bundle-anyway | The test did not check snapshot command descriptors
  or source-commit identity. It now checks both commands, commit shape, and
  local object existence without re-measuring the corpus.
- R2-F1 | act-before-ship | Reopen wording implied that the immutable snapshot
  was an input to the measurement command. It now requires a new dated,
  separately hashed snapshot for a new decision and expressly forbids
  overwriting or recomputing this one.
- R2-F2 | bundle-anyway | The test module docstring still described a live
  script pin. It now describes the hash-bound snapshot contract.
- Over-worry | Do not extend `regenerable-facts` to decision documents. The
  dated/hash-bound structure removes the mutable claim directly, and the
  existing detector is not a reliable authority for D47's figures.
- Valid but defer | The old mutable probe remains historical provenance. Its
  migration or deletion is not needed to establish the new immutable D47
  boundary.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — proof surfaces must bind their
rendered claim to the source authority, not merely show adjacent structure.

## Deliberately Not Doing

- No live corpus equality comparison.
- No `regenerable-facts` scope extension.
- No CI, push, release, consumer, or issue-closeout claim.

## Pre-Merge Action

Round-1 repairs were reviewed in round 2. Round-2 repairs are
accepted-unreviewed under the two-round cap and require focused deterministic
proof before commit.
