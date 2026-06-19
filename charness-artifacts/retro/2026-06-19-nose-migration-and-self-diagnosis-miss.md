# Retro — nose 0.13.3 scan→query migration + a self-diagnosis miss

## Mode

session

## Context

Migrated the code-clone path from the removed `nose scan` to `nose query`
(commit `15d5df4f`), re-baselined, verified (run-quality 77/0, 104 focused
tests, 2-reviewer fresh-eye critique), committed. Then, at the user's prompt,
investigated the mutation-coverage producer's "blocking" verdict and found it was
a false positive. The user named the sharpest lesson: I should have recognized
that false positive myself, up front, instead of reporting it as a real concern.

## Waste

- **Reported a tool artifact as a genuine open concern (the headline miss).** The
  changed-line mutation-coverage producer "blocked" on 3 files showing 0% — with
  *every line, including docstrings and imports*, marked uncovered, against a
  2.1GB coverage file and a stale fingerprint. Those three signals are a textbook
  tell of a coverage attribution/format artifact (docstrings/imports always
  execute on import — a real 0% there is impossible). I instead presented it as an
  "honest open item / pre-push concern," overstating risk, and only root-caused it
  as a stale, context-keyed leftover after the user said "investigate first." Cost:
  a misleading hedge + an extra round-trip.
- **Inverted the trust hierarchy.** The canonical gate (`run-quality`) had already
  *skipped* this check non-blocking (stale fingerprint → `--require-fresh-coverage`
  skip). I then ran a non-canonical bare `--reuse-coverage` (which trusts any
  coverage file regardless of freshness/format) and treated *its* block as more
  authoritative than the canonical gate's pass. A forced, off-contract probe should
  not outrank the standing gate.
- **Re-introduced a known footgun by dropping a special-case in a rewrite.** The
  old `build_command` dropped `--top` on `--write-baseline` so a baseline records
  EVERY family; my `query` rewrite used the display `--top`, truncating the advisory
  baseline to 53 instead of 487. Caught at re-seed verification, not at edit time.
- **Mirror sync missed a late edit.** The ownership-overlap docstring fix landed
  after my last `sync_root_plugin_manifests.py`, leaving the plugin mirror stale —
  a real BLOCKER. The fresh-eye critique caught it (working as designed), but a
  sync immediately before the critique/commit would have pre-empted it.

## Critical Decisions

- **Install nose 0.13.3 (vs develop on 0.13.0).** Right call: enabled honest
  verification on the real target and a single post-freeze re-baseline. `latest`
  == 0.13.3 removed version-drift risk.
- **Version-agnostic resolver** (read `families`/sv2 AND `top_candidates`/sv3) and
  **move the advisory baseline to a pure id-set** (after empirically proving nose's
  native `--baseline` clobbers across single-path query writes and keys on the
  churn-prone cluster key). Both were grounded in probes, not assumption.
- **Re-baseline after freeze + critique**, per the prior retro lesson. Followed,
  though the truncation bug + critique fixes still forced a couple of re-seeds.

## Expert Counterfactuals

- **Brendan Gregg / "trust but verify the instrument" lens.** A performance/SRE
  debugger treats a measurement that violates a known invariant as a measurement
  bug first. "Whole file 0% including docstrings/imports" violates the invariant
  that imported modules execute their top level — so the *coverage artifact* is
  suspect, not the code. The heuristic I lacked: **a surprising all-fail from a
  tool is a hypothesis about the tool until its own output shape is sanity-checked**
  (here: is the coverage file even keyed by repo-relative paths? It was keyed by
  function/context names — the target files were absent entirely).
- **Weinberg / "things got that way for a reason" lens.** A 2.1GB,
  `show_contexts:true` file that my plain producer (which exports `show_contexts:
  false`, path-keyed) could not have written should have prompted "what wrote this,
  and is it the format this consumer expects?" before trusting `--reuse-coverage`.

## Next Improvements

- **workflow:** Before reporting a coverage/quality tool's surprising 0%/all-fail
  as a finding, sanity-check the tool's own output: does the artifact contain the
  target file paths at all? Treat "whole-file-uncovered including non-executable
  lines" as a tool/format artifact, not a real gap.
- **workflow:** Don't let an off-contract probe's verdict outrank the canonical
  gate. If `run-quality` skipped a check, a hand-run `--reuse-coverage` block is a
  reason to investigate the probe, not to report a regression.
- **capability:** `check_changed_line_mutation_coverage --reuse-coverage` should
  reject a coverage JSON that contains none of the changed files' repo-relative
  paths (wrong-format/stale) — degrade to "no usable coverage → skip" rather than
  scoring every changed file 0% and blocking. This removes the entire false-block
  class. (follow-up; destination: charness gate hardening.)
- **memory:** When migrating a command builder that had read-vs-write special
  casing, preserve the invariant explicitly — a baseline write MUST enumerate the
  full set, never the display `--top`. (Captured here + in the spec Slice 3 note.)
- **follow-up (genuine, separate from this migration):** `check_dup_ratchet.py` has
  0% *attributed* coverage because slice-2 tests it via subprocess (the #393
  class). Add an in-process coverage test before pushing the unpushed stack.

## Sibling Search

Transferable pattern: **a validator/gate trusting a malformed or wrong-shaped
input and emitting a confident wrong verdict, which an agent then relays as real.**

- `check_dup_ratchet.py` already guards a sibling of this: a real code scan that
  returns 0 families against a non-empty gate baseline degrades (not a silent clean
  pass). So the dup-ratchet gate has the input-sanity instinct that
  `check_changed_line_mutation_coverage --reuse-coverage` lacks — the
  capability fix above ports that instinct to the coverage consumer.
- The advisory/gate id-baselines already degrade on a legacy/wrong-shape file
  (`load_baseline_ids`/`load_gate_baseline_ids` → `None` → advisory), so those
  surfaces are covered.
- Decision: one real sibling worth a `keep`/fix (the coverage consumer, captured as
  the capability follow-up above); the baseline readers are already defended. No
  broad sweep warranted.

## Persisted
