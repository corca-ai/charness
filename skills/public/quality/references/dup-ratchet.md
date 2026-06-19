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
  list). A full `nose query` (one call per scope root — `query` takes one path —
  merged and deduped by family identity, no nose `--baseline`) yields the current
  code `family_id` set; a `family_id` absent from the baseline and not
  `intentional` is new. The identity is nose's content-hash `id` (named
  `family_id` in the removed `scan` output, normalized by the resolver). nose's
  own `key`-based `--baseline` is NOT used for gating: `key` is
  cluster/membership-sensitive, so a copy family re-keys when any sibling copy
  changes and the tool re-flags unchanged copies as drift (a known upstream nose
  key-stability limitation, filed upstream). The content-hash identity stays
  stable across that churn, so the gate keys on it. Re-seed the baseline per
  nose version: identities are scanner-version-scoped.
- **Doc: the existing signature drift** (`doc-nose-baseline.json`, sorted member
  `path#heading` signature). The doc `signature` is heading-based and stable
  across line-number churn, so the doc inventory's drift output already is the
  new-family set; a doc drift family not `intentional` blocks. No separate doc
  gate baseline is needed.

The counts feeding both the gate and the newness check come from the SAME family
enumeration per surface, never from nose's `--fail-on` (whose count diverges from
the enumerated families).

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
   MUST enumerate the full family set (a high `top=`, full `nose query` per root, no
   nose `--baseline`); a truncated or wrong-scope seed would miss families and
   false-block later.
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
  the same discipline as the doc baseline.
