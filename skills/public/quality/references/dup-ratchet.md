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
  `schemaVersion: charness.quality.dup_ratchet_baseline.v3`, a `code_families` list
  of `{fingerprint, member_hashes}` objects — schema v3, item 5 slice D). A full
  `nose query` (one `--root` multi-root call over the whole scope, no nose
  `--baseline`) yields the current code families; the gate computes, per family, an
  offset/path-INDEPENDENT content fingerprint (`nose_fingerprint_lib`): sha256 over
  the sorted, duplicate-preserving normalized member spans, read by each member's
  `(file, start, end)`. A fingerprint absent from the baseline and not `intentional`
  is new. The scope is a single corpus, so a cross-root clone family is grouped (not
  split per root).

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

  **Normalization: algo v2 (token/comment-aware), v1 (rstrip-only) as fallback.**
  For a Python member (`.py`), the fingerprint tokenizes the span (dedented, via
  `tokenize.generate_tokens`), drops comment and pure-whitespace-structure tokens
  (`COMMENT`/`NL`/`NEWLINE`/`INDENT`/`DEDENT`), and joins the surviving token strings
  with a single space before hashing — so an in-place comment edit or an internal
  whitespace edit inside a duplicated span no longer rotates the fingerprint, while
  a real identifier/literal/operator edit still does (S4-Defer-1, resolved). A span
  that fails to tokenize standalone (a bracket-unbalanced fragment, a dangling
  `else:`) falls back, PER MEMBER, to algo v1 (rstrip each line, join with `\n`) —
  never a crash, never a whole-family degrade for one unparseable member. A
  non-Python member (e.g. a `.mjs` clone) always uses v1 regardless of algo — a
  JS/TS-aware tokenizer is out of scope; this is an accepted, documented gap.
- **Doc: the existing signature drift** (`doc-nose-baseline.json`, sorted member
  `path#heading` signature). Heading-based and position-independent; the doc
  inventory's drift output already is the new-family set, so a doc drift family not
  `intentional` blocks and no separate doc gate baseline is needed.

The counts feeding both the gate and the newness check come from the SAME family
enumeration per surface, never from nose's `--fail-on` (whose count diverges from
the enumerated families).

## Reduction Advisory (Membership Shrink Is Not New Duplication)

**S4-D9 stands: a membership CHANGE still rotates the family fingerprint** — adding
or removing a copy changes the member set, and the fingerprint folds membership and
multiplicity by design (`fp({A,A,B}) != fp({A,B})`, guarding a real 3-member family
from colliding with a real 2-member one). This is not a regression: nose's own
`family_id` already rotates on membership change today. A genuine membership GROW
(a copy added) is real new/changed duplication and hard-blocks like any other new
family — re-baseline is the correct, expected recovery, not a bug to route around.

What schema v3 adds is a narrower, honest carve-out (S4-Defer-3, resolved): before
the hard arm runs, the CLI classifies each would-be-new fingerprint against every
baseline fingerprint that vanished from the live scan. When the candidate's
member-hash multiset is a PROPER sub-multiset of a vanished family's (every member
count `<=`, and a strictly smaller total — a copy was *removed*, not added or
changed), it is a **membership REDUCTION**, not new duplication, and the CLI
excludes it from the hard-block set entirely. A reduction is **never silent**: the
CLI always prints one `ADVISORY (reduction): family OLD shrank to NEW ...` line
naming the one-command scoped accept that folds it into the baseline:

```bash
python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . \
  --accept-rotation OLD_FINGERPRINT=NEW_FINGERPRINT
```

A membership GROW is deliberately NOT a reduction (the candidate would be a
*superset*, not a sub-multiset, of any vanished family) and still hard-blocks, same
as before schema v3. The residual S4-Defer-2 adversary (a vanished/shrunk family's
exact original member set recurring elsewhere) is narrowed by this same pre-pass:
once a reduction is accepted via `--accept-rotation`, the baseline holds only the
shrunk family, so the ORIGINAL full member set recurring under a different identity
is no longer a superset of anything vanished and hard-blocks — it is never silently
re-accepted. The residual applies only while a reduction advisory sits unaccepted
(the CLI prints it every run until then).

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
   and multiplicity). A REMOVAL — one of N copies deleted — is now classified a
   membership REDUCTION by the CLI's pre-pass (see "Reduction Advisory" above) and
   stays advisory-only, with a one-command `--accept-rotation` scoped accept; it no
   longer needs a full re-baseline. A GROW (a copy added) is NOT a reduction and
   still reads as a new family — verify it is genuine new/changed duplication, not a
   laundered clone, then re-baseline.
3. **Fingerprint-algorithm bump.** A change to the normalization (e.g. the v1->v2
   token/comment-aware landing, item 5 slice D) bumps `fingerprint_algo_version`;
   the gate surfaces an algo-skew WARNING so the drifted fingerprints read as
   re-baseline. A repo-wide algo bump uses the one-shot migration tool
   (`migrate_dup_fingerprints.py`, dry-run by default) rather than a fresh
   `--write-baseline`: it remaps every accepted family old-fingerprint ->
   new-fingerprint (preserving `dup-review.json`'s manual classifications
   verbatim), drops anything genuinely vanished, and refuses to silently absorb a
   live family that was not previously accepted (`requires_review`, named in via
   `--accept-new-family`).
4. **Reviewed batch accept.** You genuinely accept new fixable families after review.

**Prefer the scoped mode for routine churn.** `--write-baseline` is a full-scan
overwrite: it silently re-accepts every current family, including any unreviewed
new one, wholesale — the exact erosion a re-baseline should not cause. For triggers
1–3 above, use `--accept-rotation OLD_ID=NEW_ID` (repeatable) and/or
`--accept-family NEW_ID` (repeatable) instead: it starts from the existing baseline,
applies ONLY the named pairs/ids, and refuses (listing them) any other live delta —
so an unrelated new family riding along with a rotation still hard-blocks instead of
being silently absorbed. Two evaluate-tolerated classes are exempt from that
refusal and stay OUT of the baseline: overlay-`intentional` families and unnamed
membership reductions (each re-advised with its `--accept-rotation` hint), so a
rotation the evaluate path itself suggested is acceptable as-is. `--write-baseline` remains for first-time bootstrap (trigger
4, a genuine reviewed batch accept) and prints a WARN naming the scoped mode whenever
it overwrites an existing baseline.

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
  `schemaVersion`, a non-string fingerprint, an empty/non-string `member_hashes`
  list) → advisory integrity warning (`dup_ratchet_baseline_lib.validate_gate_baseline`);
  the hard arm must not run silently on an unvalidated baseline. Never blocks. A
  pre-v3 baseline (the old flat `code_family_fingerprints` list) has no
  `code_families` key at all, so it reads as missing/unreadable (the line above),
  not schema-invalid — same no-dual-read discipline as the v1→v2 re-key.
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
- Does a printed `ADVISORY (reduction)` line genuinely describe a copy removed, or
  did the CLI's pre-pass mis-pair it with an unrelated vanished family? Read the
  named old/new fingerprints against the actual diff before running the suggested
  `--accept-rotation`.
