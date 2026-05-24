# Retro — RCA Ledger Slice 2 (Auto-Append Wiring)

Mode: session

## Context

Reviewing the session that landed RCA ledger slice 2 (commit `a67675c`): wiring
`record_rca_event.py` into the `debug`/`issue`/`retro` closeout prompts via a
presence-gated shared reference, flipping `AUTO_APPEND_WIRED=True`, syncing
truth surfaces, and a 4-angle + 1-counterweight fresh-eye critique. What matters
next: the wiring is live in the prompts but cannot yet fire (see headline below).

## Evidence Summary

- The diff itself (`git diff` of `a67675c`) and the canonical spec
  `charness-artifacts/spec/rca-conversion-ledger.md` (slice-2 section + critique
  pass).
- A simulation: appending one non-seed event to a copy of the committed ledger,
  then running `aggregate_rca_ledger.py` (verified `baseline_rate_available`
  flips to True and `seed_excluded.rate` to `0.0`).
- `recent-lessons.md` repeat-trap section (the length-budget lesson).

## Waste

- **Headline — slice 2 shipped a latent break (verified)**: the committed
  ledger `charness-artifacts/metrics/rca-ledger.jsonl` doubles as the AC4/AC7
  test fixture. The first live (non-seed) auto-appended event flips
  `baseline_rate_available` to True and `seed_excluded.rate` off `n/a` to a real
  number, so `test_ac4_*` and `test_ac7_*` fail. The auto-append I just turned ON
  is therefore self-defeating: the first real `debug`/`issue`/`retro` closeout
  that appends will red-flag pre-push/CI. The suite is green now only because no
  live event exists yet. This is a `weak_proof`/`bug`-class event — verification
  reached "all gates green" but green was measured against a seed-only state the
  feature's success immediately destroys. Caught by agent reflection in this
  retro, not by a gate.
- **200-line SKILL.md budget trap (recurrence, twice)**: edited
  `skills/public/debug/SKILL.md` while it was already exactly at the
  `MAX_SKILL_MD_LINES=200` gate without pre-checking, so `validate_skills` failed
  and forced mid-stream bullet compression — once on the initial wiring and again
  after the critique's debug-bullet rewrite. `recent-lessons.md` already carries
  this exact lesson, but scoped to `.py` budgets (480/360 file, 100/150 function,
  800 test); it did not transfer to the SKILL.md 200-line gate.
- **doc-link backtick trap (minor)**: the new reference's path-like backticks
  (`scripts/record_rca_event.py`, the ledger path) tripped `check_doc_links`;
  resolved with `<repo-root>/` placeholders. Gate-caught fast, low cost.

## Critical Decisions

- **Presence-gated portable design**: the closeout append applies only where the
  recorder + ledger exist (silent no-op for consumer installs), instead of a new
  adapter or a repo-contract-only home. The critique confirmed this is correctly
  shaped and the structural no-op holds (export omits the ledger).
- **Full critique before commit**: caught the bare `auto_append: ON` overclaim
  (which had deleted the only "do not quote" signal while the seed-only `60.0%`
  kept printing) and three stale OFF-state spec passages. Both would have shipped
  otherwise. High-value, and validates running the critique pre-commit rather
  than as a follow-up.

## Expert Counterfactuals

- **Gerald Weinberg (diagnostic — "what does green actually prove?")**: the
  slice-2 suite proved the mechanism (append works, banner honest) but measured
  green against the seed-only state that the feature's first success destroys.
  Weinberg's question — "what is the first thing that happens when this works?" —
  surfaces the AC4/AC7 break before commit. Changed action: before flipping a
  feature flag ON, run the suite against the *post-activation* state (a ledger
  that already contains a live event), not only the pre-activation fixture.

## Sibling Search

Transferable pattern: "edit a file that is at/near its length gate without
pre-checking the budget." Four-axis scan of files touched this slice —
`skills/public/issue/SKILL.md` (192) and `retro/SKILL.md` (177) both have margin;
the new reference is ~80 lines with no SKILL.md gate. Only `debug/SKILL.md` is
pinned at 200/200. Decision: **same class, diagnostic-only for this slice** —
debug is the lone at-limit surface; the durable fix (extract step-6 detail to a
reference for margin) is a capability follow-up below, not bundled here.
Proof level: static line-count scan of the four edited markdown files.

## Next Improvements

- **capability (immediate next slice)**: decouple AC4/AC7 from the live committed
  ledger — assert the seed-only/empty-baseline guarantees against synthetic
  fixtures so the committed ledger is free to accrue live events. This unblocks
  the wiring; until then the auto-append cannot fire. Once decoupled, this
  retro's own RCA event becomes the first live append (the proper dogfood).
- **workflow**: before flipping a feature flag ON, simulate the post-activation
  state and run the suite against it. Detection point: the AC4/AC7 break would
  have been caught pre-commit.
- **memory**: generalize the "check length budget before editing" habit to ANY
  length-gated file, including the SKILL.md 200-line gate, not only `.py`
  budgets. Detection point: `validate_skills` `MAX_SKILL_MD_LINES`.
- **capability (optional)**: extract some `debug/SKILL.md` step-6 detail into a
  reference so it has margin below 200 instead of sitting pinned at the gate.

## Persisted

Persisted: yes (this artifact); see path in the persist output.
