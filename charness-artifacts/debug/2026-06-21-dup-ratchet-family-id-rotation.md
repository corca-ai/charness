# dup-ratchet family_id Rotation Debug
Date: 2026-06-21

## Problem

The boy-scout dup-ratchet gate (`check_dup_ratchet.py` + `dup_ratchet_lib.py`)
keys code-clone newness by diffing the current nose `family_id` set against a
committed baseline. `references/dup-ratchet.md` and the `dup_ratchet_lib` /
`nose_baseline_lib` docstrings claim this content-hash `family_id` is "stable
across sibling churn". Editing a scanned member file rotates the `family_id` of
clusters that include it even when the duplicated code is byte-identical, so the
rotation reads as a brand-new fixable family, the hard arm blocks, and the only
honest recovery is a re-baseline with zero actual new duplication (#395).

## Correct Behavior

Given the gate keys newness on `family_id`, when a scanned member file is edited
without changing any duplicated span's content (and without adding/removing
duplication), then the gate must not report a new fixable family — OR the docs
must accurately state that such edits rotate ids and document the expected
re-baseline workflow, so the forced re-baseline is anticipated, not surprising.

## Observed Facts

- nose 0.14.0 `query` (schema v4) exposes only `id` (family) and per-member `id`;
  no position-independent content identity is emitted.
- The gate uses `nose_report_lib.family_identity` → `family.get("id")`.
- The reported v0.52.6 instance (commit `afc86779`) rotated 2 byte-identical
  family ids and reported `status: hard-block, new_code: 2` against a clean tree.

## Reproduction

Temp copy of `skills/public/quality/scripts`, `nose query <scope> --format json
--min-size 24 --min-members 2`, mutate, re-query, diff ids:

- Test 1 (EOF comment, no line shift): 0 ids rotated — a non-shifting edit is stable.
- Test 2 (insert 6 comment lines ABOVE the spans in one member file; span content
  byte-identical, no duplication added): the per-member `id` rotated
  (`2a4581878705ebdc → 84d513fe458aa348`) AND both family ids containing that file
  rotated (`192889c54d50ef91 → 5afaac…`, `66c7b1c9de4d8f4b → 103a88…`). For the
  25-member family, 24 of 25 member ids were unchanged — one rotated member rotated
  the whole family id.
- Minimal: two files sharing a 12-line function; prepend 5 comments to one →
  family id `f1e6823f50846bb3 → 806e4b5664258151` while the other copy is
  byte-identical (the gate's own characterization test).

## Candidate Causes

- nose's per-member `id` folds the member's line offset (`start`/`end`), not just
  normalized span content — confirmed by Test 2.
- nose's per-member `id` also folds the member's file path — confirmed (Test 1's
  scope-path change shifted the family id).
- The family `id` is a function of all member ids, so any one member's rotation
  rotates the whole family id — confirmed (24/25 unchanged members, id still rotated).
- (Rejected) the edit added/removed real duplication — disproven: function bodies
  byte-identical base-vs-HEAD.

## Hypothesis

If nose's `family_id` folds member offset + path (not content only), and the gate
keys newness on it, then any member-file edit that shifts a span's offset rotates
the id and trips the hard arm with zero new duplication — and solution (a)
(re-key on a content-only id) is impossible because nose emits no such identity.

## Verification

- Full schema-v4 family/location field sweep: only `id`/`member id` exist, both
  fold position+path → solution (a) falsified.
- `check_dup_ratchet.py` hard-blocked on this very fix's docstring edits (4 ids
  rotated); verified all 4 rotated families' function bodies byte-identical
  base-vs-HEAD; lockstep `--write-baseline` of both id-sets → gate clean,
  491→491 count conserved.
- New real-nose characterization test asserts the rotation; green against nose 0.14.0.

## Root Cause

nose's `family_id` = f(span content, line offset, file path); the family id is a
function of all member ids, so any member's offset/path shift rotates the whole
family id with zero content change. The gate keys newness on that id, so the hard
arm reads a pure rotation as a brand-new family. The documented "stable across
sibling churn" claim is narrower than reality.

## Detection Gap

- gate stability claim | no gate/test asserts the documented `family_id`
  stability; acceptance tests inject static `--code-inventory` id sets | add a
  real-nose member-edit characterization test (done).
- consumer ship | the false claim shipped to consumers (v0.52.6) undetected |
  the corrected docs travel with the gate.

## Sibling Search

- same layer: skills/public/quality/scripts/nose_baseline_lib.py (clone advisory) | decision: same class, fixed now | proof: local payload proof (same false claim + same rotation; advisory-only, no hard-block)
- abstraction up: doc-side `signature` baseline (`doc-nose-baseline.json`, `path#heading`) | decision: intentional plain-text or non-rendering boundary | proof: static scan only (position-independent, not vulnerable — the correct half of the asymmetry)
- mental-model sibling: any gate keying newness/drift on nose family_id | decision: valid follow-up outside the slice | proof: static scan only (the gate id-rotation affordance) | follow-up: deferred docs/deferred-decisions.md D30
- cross-file: skills/public/quality/scripts/nose_baseline_lib.py

## Seam Risk

- Interrupt ID: dup-ratchet-family-id-rotation
- Risk Class: operator-visible-recovery
- Seam: nose family_id (offset/path-folding) -> gate id-set baseline diff -> hard-arm block
- Disproving Observation: a pure line-shift rotates the family id while the sibling copy is byte-identical (characterization test green).
- What Local Reasoning Cannot Prove: whether a future nose version will emit a position-independent content id (which would enable solution (a)/(c)).
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Doc correction removes the false "churn-stable" trust across all three carriers;
a new "Re-Baseline Triggers" section documents the verify-then-`--write-baseline`
workflow and the lockstep both-baselines rule; a real-nose characterization test
locks the offset-rotation and flips if a future nose makes the id
position-independent. The gate id-rotation affordance (solution c) is deferred to
`docs/deferred-decisions.md` D30 (needs a baseline schema migration and must guard
a false-negative where a new clone reusing the same member files fingerprint-matches
a vanished family).

## Related Prior Incidents

- nose 0.14.0 compat pass (handoff): re-seeded both id-set baselines for the
  scanner-version bump — the same re-baseline discipline this issue documents for
  member-file edits.
