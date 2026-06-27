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

## Code / Doc Identity

Both surfaces key newness on a position-independent identity — deliberately,
driven by what is stable in the detector. They differ in mechanism only because
the inputs differ:

- **Code: a gate-owned content-fingerprint baseline** (`dup-ratchet-baseline.json`,
  `schemaVersion: charness.quality.dup_ratchet_baseline.v2`, a
  `code_family_fingerprints` list). A full `nose query` (one `--root` multi-root
  call over the whole scope, no nose `--baseline`) yields the current code families;
  the gate computes, per family, an offset/path-INDEPENDENT content fingerprint
  (`nose_fingerprint_lib`): sha256 over the sorted, duplicate-preserving
  rstrip-normalized member spans, read by each member's `(file, start, end)`. A
  fingerprint absent from the baseline and not `intentional` is new. The scope is a
  single corpus, so a cross-root clone family is grouped (not split per root).

  **Why not nose's `family_id` (slice 4 re-key, resolving D30).** nose's `family_id`
  folds each member span's normalized content, its **line offset**, AND its **file
  path**, so editing any scanned member file — even inserting lines *above* an
  unchanged span — rotated the whole id and false-blocked the hard arm with zero new
  duplication. The content fingerprint is STABLE across such pure line-shifts (a
  member's own span bytes do not change when lines move around it) and still rotates
  on a genuine span-content change, so real new/changed duplication is caught with no
  false-negative. The family SET (which spans nose groups at a given mode/min-size)
  is still nose-version-scoped, so a nose bump can regroup families and drift the
  fingerprint set — re-baseline per nose version (self-detecting; see below).

  **v1 limitation.** The rstrip-only normalization is stricter than nose's tokenizer:
  an in-place comment or internal-whitespace edit *inside* a duplicated span (no
  line-count change) rotates the fingerprint where nose's id would not. This is a
  different, low-frequency edit class than the offset shift the fix removes, and it
  falls back to the same re-baseline recovery; token/comment-aware normalization is
  deferred (its arrival would bump `fingerprint_algo_version`).
- **Doc: the existing signature drift** (`doc-nose-baseline.json`, sorted member
  `path#heading` signature). Heading-based and position-independent; the doc
  inventory's drift output already is the new-family set, so a doc drift family not
  `intentional` blocks and no separate doc gate baseline is needed.

The counts feeding both the gate and the newness check come from the SAME family
enumeration per surface, never from nose's `--fail-on` (whose count diverges from
the enumerated families).

## Re-Baseline Triggers

A `--write-baseline` re-baseline is legitimate maintenance, not a workaround, in
these cases — none of which represent new duplication. (A pure member-file
line-shift is NO LONGER one of them: the content fingerprint is stable across it —
the false-block slice 4 removed.)

1. **Scanner-version bump.** A new nose version can regroup families (the family SET
   is nose-version-scoped), drifting the fingerprint set. Self-detecting: each
   baseline stamps the producing `tool_version`, and the read path surfaces a skew
   WARNING when the live version differs.
2. **Membership change.** Adding or removing a copy of a clone family changes its
   member set, so its content fingerprint rotates (the fingerprint folds membership
   and multiplicity). Removing one of N copies — a legitimate reduction — therefore
   reads as a new family and re-baselines, the SAME behavior as nose's id today (the
   fingerprint does not make it worse; a subset-aware "reduction" diff is a deferred
   enhancement). Verify the change is a real reduction, not a laundered new clone,
   then re-baseline.
3. **Fingerprint-algorithm bump.** A change to the normalization (e.g. landing
   token/comment-aware normalization) bumps `fingerprint_algo_version`; the gate
   surfaces an algo-skew WARNING so the drifted fingerprints read as re-baseline.
4. **Reviewed batch accept.** You genuinely accept new fixable families after review.

Re-baseline **both fingerprint baselines together**: the gate baseline
(`dup-ratchet-baseline.json`) and the clone-advisory baseline (`nose-baseline.json`)
key on the same fingerprint set in lockstep, so updating only the one that blocked
you leaves the advisory baseline stale. The `dup-review.json` overlay also keys code
entries by fingerprint, so a re-baseline that changes family identities must keep the
overlay's `intentional` classifications mapped to live fingerprints (a member-preserving
remap), or accepted boilerplate re-enters the hard arm.

**Version skew detection.** Both code baselines stamp the nose `tool_version` and the
`fingerprint_algo_version` that produced them (from the same scan, never a fresh
probe). On read, the gate and advisory compare each against the live values and
surface a one-line WARNING per axis when they differ. The warning *explains* a block,
never *suppresses* one (degrading would silently drop the gate and let real new
duplication through) — the operator reads the hard-block as version/algo drift to
re-baseline, not dup to remove. A *missing* stamp is "unknown", not a mismatch, so
legacy baselines do not warn until their next deliberate re-baseline.

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
