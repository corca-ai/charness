# Boy-Scout Duplicate Ratchet

Use this reference when a repo wants duplication to ratchet *down* over time
instead of only being reviewed when someone runs `quality`. It is the teeth on
top of the reviewed-fixable overlay (`dup_review_lib` / `dup-review.json`): the
overlay says which clone families are genuinely fixable versus intentional
boilerplate; the ratchet blocks new fixable duplication and nudges existing
fixable duplication down.

## Ownership

`quality` owns the portable policy:

- the two-arm decision (`dup_ratchet_lib.evaluate`)
- the gate-baseline payload contract
- the escalation-ladder / healthy-floor semantics
- the inert / degraded ladder and the non-claims

The consumer repo owns its artifacts and scope: it points `review_artifact_path`,
`gate_baseline_path`, and `scope_paths` at its own files through the adapter. The
nose engine ships in the plugin, so the consumer already has the detector. An
absent or disabled `dup_ratchet` block leaves the gate fully inert.

## Two Arms

**Hard arm (always blocks).** A NEW fixable-eligible family hard-blocks. "New" =
present in the current scan, absent from the accepted reference, and not
classified `intentional` in the overlay. Recording a new family `unreviewed` does
NOT unblock it — only removing it, reclassifying it `intentional`, or a deliberate
gate-baseline acceptance does.

**Boy-scout arm (escalating nudge).** While the reviewed `fixable_ceiling` stays
above the healthy floor `F` and the overlay has not advanced for `escalation_K`
commits, the normally-advisory "chip the existing fixable duplication down" nudge
escalates to a one-time block, which resets when the overlay edit advances the git
anchor. At or below the floor `F`, the boy-scout arm is fully advisory; the hard
arm still fires.

## Code / Doc Asymmetry

The two surfaces key newness on different identities, and this is deliberate —
driven by what is stable in the detector, not by preference:

- **Code: a gate-owned `family_id` baseline** (`dup-ratchet-baseline.json`,
  `schemaVersion: charness.quality.dup_ratchet_baseline.v1`, a `code_family_ids`
  list). A full `nose query` (one nose 0.14.0 `--root` multi-root call over the
  whole scope, no nose `--baseline`) yields the current code `family_id` set; a
  `family_id` absent from the baseline and not `intentional` is new. The scope is
  analyzed as a single corpus, so a cross-root clone family is grouped (not split
  per root — the pre-0.14.0 per-root-loop missed those; switching that scope model
  is a deliberate one-time re-baseline, since identities are scope-model-scoped and
  the family set shifts when the model does). The identity is nose's
  content-hash `id` (named `family_id` in the removed `scan` output, normalized by
  the resolver). nose's own `key`-based `--baseline` is NOT used for gating, for
  plumbing reasons: it keys on the churn-prone cluster `key` and `--write-baseline`
  clobbers its target each run, so it cannot serve as the accepted-id set.

  **Stability caveat — `family_id` is NOT churn-stable.** The gate keys on
  `family_id` for that plumbing reason, not because it survives sibling churn — it
  does not. The family `id` folds every member's per-span id, and each per-span id
  folds the span's normalized content, its **line offset**, AND its **file path**.
  So editing any scanned member file — even inserting lines *above* an unchanged
  duplicated span — shifts that member's offset, rotates its id, and rotates the
  whole family `id`, even for the byte-identical sibling copies in unrelated files.
  This is the same "an unchanged copy re-keys when a sibling copy changes" failure
  nose's `key` has; `family_id` does not escape it. A rotated id reads as a new
  family (the hard arm blocks) with zero new duplication. The honest recovery is a
  deliberate re-baseline (see "Re-baseline triggers" below). Re-seed per nose
  version too: identities are scanner-version-scoped.
- **Doc: the existing signature drift** (`doc-nose-baseline.json`, sorted member
  `path#heading` signature). The doc `signature` is heading-based and
  position-independent — stable across line-number churn (unlike the code
  `family_id` above), so the doc inventory's drift output already is the
  new-family set; a doc drift family not `intentional` blocks. No separate doc
  gate baseline is needed. (The code/doc asymmetry is real, but only the doc side
  is genuinely churn-stable; the code side trades that away for the multi-root
  plumbing reasons above.)

The counts feeding both the gate and the newness check come from the SAME family
enumeration per surface, never from nose's `--fail-on` (whose count diverges from
the enumerated families).

## Re-Baseline Triggers

A `--write-baseline` re-baseline is legitimate maintenance, not a workaround, in
three cases — all of which rotate `family_id`s without representing new
duplication:

1. **Scanner-version bump.** A new nose version re-hashes every `family_id`; the
   whole set shifts. Trips the `--write-baseline` large-delta guard, so confirm it
   deliberately with `--confirm-baseline-delta`.
2. **Member-file edit that shifts a duplicated span.** Editing any scanned file —
   even inserting lines *above* an unchanged duplicated span, or renaming/moving a
   member file — rotates the `family_id`s of every family that file belongs to
   (see the stability caveat above), even though the duplication is unchanged. The
   gate's hard arm reports these as new families. Before re-baselining, **verify
   the rotated families are byte-identical base-vs-HEAD** (`git show <base>:<file>`)
   so a real new clone is not laundered through as a "rotation"; then re-baseline.
3. **Reviewed batch accept.** You genuinely accept new fixable families after
   review (the only case that should change the duplication picture).

Re-baseline **both id-set baselines together** when ids rotate: the gate baseline
(`dup-ratchet-baseline.json`) and the clone-advisory baseline (`nose-baseline.json`)
key on the same `family_id` set and rotate in lockstep, so updating only the gate
baseline that blocked you leaves the advisory baseline stale (silent advisory drift).

A re-baseline driven by case 2 is expected churn, not a defect — it is the cost of
keying on an offset-sensitive `family_id` (the known limitation the gate documents
rather than hides). A future gate affordance could recognize a pure id-rotation
(a "new" family whose position-independent member set matches a vanished baseline
family) and downgrade it from hard-block to advisory — though that design must guard
a false-negative: a genuinely new clone that reuses the same member files would
fingerprint-match a vanished family and be wrongly downgraded, so the affordance is
deferred to its own slice rather than bolted on here. Until then, case-2 re-baselines
are the honest recovery.

## Stagnation Without A Counter

Stagnation is measured from git — no checked-in counter, no self-SHA. The anchor
is the commit that last touched the overlay (`git log -1 --format=%H -- <overlay>`);
stagnation is `git rev-list --count <anchor>..HEAD`. Lowering the ceiling means
editing the overlay, which is a commit touching it, which resets the clock. This
avoids both circularities (a hook cannot commit a counter into the push it gates;
a commit cannot store its own SHA). Edge rules the gate enforces:

- **anchor not an ancestor of HEAD** (rebase / squash / force-push orphaned it):
  the boy-scout arm degrades to advisory ("re-baseline needed"); it never blocks
  on a phantom. The hard arm is independent of the anchor and still fires.
- **interval at pre-push** counts `<anchor>..HEAD`; on a long feature branch this
  counts branch commits — accepted as the push proxy.

`evaluate` takes the stagnation distance *injected*; the git seams
(`resolve_anchor` / `anchor_is_ancestor` / `stagnation_commits`) are separate and
injectable so the policy stays pure and testable.

## Inert / Degraded Ladder

- `dup_ratchet` absent or `enabled: false` → inert (exit 0).
- enabled but the overlay OR the gate baseline is missing / unreadable → advisory,
  never blocks (a missing reviewed subset must not be a silent all-clear *or* a
  false block).
- enabled but `scope_paths` is empty → advisory degrade. A real scan would fall
  back to nose `DEFAULT_PATHS` (the wrong tree on a consumer repo), so the whole
  gate degrades rather than block on — or silently pass — a misconfigured scan.
  Set `scope_paths` to your code roots.
- the gate baseline is present and loadable but schema-invalid (wrong
  `schemaVersion`, non-string ids) → advisory integrity warning
  (`dup_ratchet_lib.validate_gate_baseline`); the hard arm must not run silently on
  an unvalidated baseline. Never blocks.
- nose missing or the scan errors → degraded advisory; the doc-duplicates
  `--require-nose` phase owns failing closed on nose presence, not this gate.

## Adoption

Order matters: the gate-baseline seed reads `scope_paths`, so configure scope
*before* you seed (otherwise the seed enumerates the wrong tree and false-blocks
later — the trap step 3 below warns about).

1. Add the `dup_ratchet` block with `enabled: false` and point `scope_paths` /
   `review_artifact_path` / `gate_baseline_path` at your repo.
2. Seed the reviewed overlay: `seed_dup_review.py --repo-root . --write`.
3. Seed the gate baseline (accept today's full code `family_id` set):
   `check_dup_ratchet.py --repo-root . --write-baseline`. It reads `scope_paths` and
   MUST enumerate the full family set (a high `top=`, one `--root` multi-root
   `nose query`, no nose `--baseline`); a truncated or wrong-scope seed would miss families and
   false-block later. Re-running `--write-baseline` later guards a large shift: a
   delta (added+removed `family_id`s) beyond `--baseline-delta-threshold` (default
   50) refuses without an explicit `--confirm-baseline-delta`, so an accidental
   broken-scan seed cannot silently overwrite the accepted baseline; a deliberate
   re-baseline passes the flag. This guard is on the maintenance command only — it
   never touches the gate evaluate path, so it cannot false-block a push.
4. Flip the block to `enabled: true`.
5. Wire `check_dup_ratchet.py` into your broad gate / pre-push (reuse a persisted
   doc-duplicates `--json-out` via `--doc-inventory` to avoid a second doc scan).
   Keep it OUT of a fast docs-only subset (the broad path carries the teeth).

## Review Questions

- Is a flagged new family genuine extractable duplication, or intentional portable
  boilerplate that belongs in the overlay as `intentional`?
- Is the gate baseline being re-seeded to *accept reviewed* new families, or to
  silence a block without review? Only the former is legitimate.
- Has the `fixable_ceiling` actually decreased since the last review, or is the
  overlay edit cosmetic? The anchor advances on any overlay commit; keep edits
  honest.
- Did a scanner-version bump shift `family_id`s? Re-baseline per scanner version,
  the same discipline as the doc baseline — a version swing trips the
  `--write-baseline` large-delta guard, so confirm it deliberately with
  `--confirm-baseline-delta`.
