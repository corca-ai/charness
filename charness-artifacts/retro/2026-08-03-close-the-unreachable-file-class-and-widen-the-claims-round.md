# Close the unreachable-file class and widen the claims round
Date: 2026-08-03

## Context

Goal `2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round`.
Two structural items. The first: close the class #477 and #478 were sub-forms of
— *shipped prose asserts a file the reader can reach, and the reader cannot* —
by fixing the RULER rather than the current members, because three prior passes
had each reported an honest "0 remaining" with a denominator narrower than the
class. The second (`parents[N]`): make an arithmetic coincidence STATED. Slice E
(widening the claims round to release) had landed before activation.

## Evidence Summary

- **Corpus and ruler, dated 2026-08-04:** 510 markdown files swept.
  `check_doc_links.py`'s `DOC_GLOBS` excludes `plugins/**` entirely — **236 of
  510 files (46%) were scanned by no link gate at all.**
- **A1 (unfollowable links in the shipped mirror): 12 → 0.** #479 listed 11; the
  12th never leaves the plugin root and is broken by the exporter's
  kind-flattening, which an escape-only ruler cannot see.
- **A2 (`authoring-repo-internal` + the consumer's `<repo-root>/`): 6 → 0.**
  #479 listed 5. Its ruler was line-anchored; 4 of the 6 wrap between the phrase
  and the prefix, and one site was missed entirely.
- **A3: 4 sites → 3 repaired, 1 deferred** with a named revisit trigger (D50).
- **A4: 29 sites, deliberately NOT gated.** All 29 name a real repo script,
  which is exactly what makes the axis undecidable statically.
- **Parity proof for the `check_doc_links` rewire:** 27 hand-built edge inputs
  plus **873 live-corpus links, 0 divergences** against `git show HEAD`.
  `iter_doc_lines` change: **2802 repo-owned docs, 0 walk changes** (the only 6
  diffs are node_modules fence-syntax docs, where the new behaviour is correct).
- **`parents[4]` fallback measured DEAD and WRONG:** the ancestor walk succeeds
  for every skill script in both trees (0 failures), and in the mirror
  `parents[4]` is `plugins/`, one level above the `plugins/charness` the walk
  correctly returns.
- Both new rules proven to bite on the LIVE tree by reintroducing a real defect,
  not only on fixtures.
- Filed [#480](https://github.com/corca-ai/charness/issues/480).

## Waste

- **The round-1 blocker cost a full broad-suite run to discover.** Deleting
  `LINK_RE` from `check_doc_links.py` broke `check_doc_authoring_preflight.py`,
  which imported it. `run_slice_closeout.py --skip-broad-pytest` is *why* it
  escaped the slice gate — the cheap-at-commit-boundary cadence is correct, but
  a module-surface deletion is exactly the change class it cannot see.
- **A background test run reported "exit code 0" while its output showed 10
  failures — and it happened TWICE, on two separate runs (10 failures, then 4).**
  I only caught both by reading the output file. Anything read from a completion
  summary rather than the artifact is a proxy.
- **Four of those failures were self-inflicted by concurrency**, not real:
  `test_validate_packaging_committed_*` and the mirror-gate tests copy the repo
  and validate packaging, and I ran `sync_root_plugin_manifests.py` while the
  background suite was mid-flight. All four pass in isolation. Cost: one
  investigation round chasing a phantom. A regenerating mirror is a write to the
  tree the suite is reading.
- **Dup-ratchet fingerprints rotated twice mid-slice** — once on a refactor, once
  on removing a single unused import — costing three classify-and-recheck cycles
  before the ratchet went clean.
- **Two self-inflicted proxy traps.** My AST test for the removed `parents[4]`
  fallback first grepped the function's source text and went red on its own
  docstring explaining the removal. And my fence repair narrowed link matching
  from whole-text to per-line, silently.

## Critical Decisions

- **Fix the ruler, not the members.** The goal's own framing, and it paid: every
  axis grew the moment the ruler widened (11→12, 5→6). Hand-repairing #479's
  list would have produced a fourth honest false zero.
- **Two gates, not one wider glob.** `check_doc_links` judges a link where it is
  AUTHORED; `check_plugin_doc_links` judges it where a consumer READS it, after
  the exporter has moved the file and flattened the layout. A link can be green
  in one and broken in the other — that asymmetry *is* the defect class, so
  collapsing them would have hidden it.
- **Gate A1 and A2; refuse to gate A4.** A bare `scripts/run-quality.sh` in a
  portable doc may legitimately mean the consumer's own tree. Gating it would
  have shipped the exact false positive the previous run had to retract.
- **Sentence-scoped, not line- or paragraph-scoped, for A2.** Line-scoped found
  2 of 6; paragraph-scoped fabricated a contradiction across two independent
  bullets in `spill-targets.md`. Both failure directions were observed, not
  reasoned about.
- **Replace the dead `parents[4]` fallback with a refusal rather than a
  corrected number.** A fallback that cannot be reached cannot be observed to be
  wrong; it would have stayed wrong until the day the walk first failed.

## North Star Alignment

- **P5 (teeth only where a wrong answer escapes) HELD, and was the sharpest
  tool.** A1 and A2 got blocking gates because their verdicts are decidable
  without judgment; A4 got a disposition table because its verdict is not. The
  Floor-Addition Restraint call is recorded at the gate site itself, and it
  rests on a measured recurrence (#477, #478, both closed, 12 live instances
  after) rather than on one finding.
- **P4 (at irreversible boundaries success is provisional) HELD, twice over.**
  The two-round bounded review is the mechanism, and round 2 justified itself
  again: it found three holes that round 1's own repairs had opened. A single
  round would have shipped a blocking gate blind to prose-wrapped links.
- **P3 (principle over rulebook) held in the repairs.** The `parents[N]`
  invariant became an executable test with a stated revisit trigger, not an
  enumerated list of correct indices.
- **Named failure signature walked into: "the fix carries the class it fixes."**
  My repair for a false-positive hole (fenced examples) opened three
  false-negative holes. This is the sixth measured instance of that signature in
  this repo, and the first where I was the one who introduced it *while fixing
  the same class*.
- **A second signature: "assert the thing, not a proxy."** Walked into inside a
  test written to enforce exactly that discipline.

## Expert Counterfactuals

- **A CommonMark implementer** reading `FENCE_RE = (```|~~~)` with a parity
  toggle would have flagged the mismatched-marker inversion instantly — it is a
  known spec rule, not a subtle bug. I reasoned about fences from first
  principles instead of from the spec, and a bounded reviewer had to catch it.
- **Direct counterfactual:** had I run the broad suite once BEFORE the first
  bounded review instead of after, the `LINK_RE` blocker would have been mine to
  find, and round 1 could have spent its whole budget on the gate's logic rather
  than on a mechanical import break. The cheap-gate cadence is right for most
  slices; a slice that DELETES a module-level name should trip a broader run.

## Sibling Search

- axis: other shared-module names this slice's family could delete out from under
  a consumer | location: `scripts/markdown_doc_scan.py`, `scripts/check_doc_links.py`
  | decision: valid follow-up outside the slice | proof: round 2 enumerated every
  `_doc_links.<attr>` read across both trees and found all present; but nothing
  ENFORCES that — the check was a human sweep, not a gate | follow-up: a gate that
  refuses deleting a module-level name another repo module imports
- axis: gates whose commit-time trigger does not scope their verdict | location:
  `docs/conventions/validator-timing-layers.md` | decision: valid follow-up
  outside the slice | proof: both link gates flip on a link TARGET rename that
  stages no `.md`; the table now says so for the new row, and the same hole is
  live for `check-doc-links` | follow-up: deferred — widening the trigger has to
  move both gates together

## Next Improvements

- workflow: a slice that deletes or renames a module-level name should run the
  broad suite at its own boundary, not defer to closeout — `--skip-broad-pytest`
  is correct for additive slices and blind to this one.
- capability: read the OUTPUT of a background command, never its completion
  summary. Two summaries this run said "exit code 0" over runs with 10 and 4
  failures respectively.
- workflow: do not run a generated-surface sync while a background suite is
  reading the tree — four phantom failures came from exactly that, and they look
  identical to real ones until you rerun them in isolation.
- memory: the round that reads the REPAIRS is where the class comes back — now
  six measured instances, and this one recurred inside a repair for the same
  class.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md
