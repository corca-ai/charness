# Session Retro — at-cap achieve closeout module split

Mode: session

## Context

Split the two at-cap achieve closeout modules — `goal_artifact_disposition.py`
(352/360) and `goal_artifact_closeout_evidence.py` (348/360) — into cohesive
leaf sub-modules, behavior-preserving, mirror byte-synced, restoring real
headroom so the next floor/rung addition starts from a clean split rather than
another shared-grammar/CLI workaround (the #339 deferred structural debt). Three
slices: (1) extract the disposition markdown-grammar/scope leaf; (2) extract the
closeout sibling-loader leaf; (3) bundle closeout (broad gate + changed-line
coverage + retro + dispositions).

## Evidence Summary

- Source diff: commits `a4830fec` (slice 1) + `35ad8ef8` (slice 2) + the slice-3
  coverage/closeout commit; 4 new/changed achieve scripts + 2 new leaf modules.
- Load-bearing proof: a 68-goal closeout-gate verdict-parity harness, byte-identical
  pre/post each split (slice 1 sha `28e3f24a`; slice 2 pristine temp-revert sha
  `93e4d04d`, all confounds removed).
- Headroom: disposition 352->250, grammar leaf 152; closeout_evidence 348->261,
  loaders leaf 140. Fresh-rung demo: disposition+30 = 275 (<330 warn) where
  pre-split 352+30 = 382 would have breached the 360 hard cap.
- Gates: +6 tests; broad verification-lock gate PASS (broad pytest 396s);
  export-safe-imports (448) + plugin-import-smoke green; mirror byte-synced.
- Host signals (thread-wide, claude project jsonl): 4 compactions, 2 fresh-eye
  subagents, no repeated broad gates, one coverage-producer round-trip.

## Waste

- **Coverage-producer round-trip on pre-existing uncovered branches (the main
  waste, partly avoidable).** I carried the #339 lesson "cover any NEW module's
  lines IN the introducing slice so the bundle producer confirms, not discovers"
  into the operating frame — but still ran the bundle producer and had it
  *discover* 7 uncovered changed lines (the `_mask_fences` unbalanced-fence
  branch, `_section_body` heading-at-EOF branch, and 5 loader `raise ImportError`
  branches). Root cause: I reasoned "verbatim move ⇒ already covered" and missed
  that moving code into a NEW file makes every line a *changed* line, so
  pre-existing uncovered branches in the moved source become newly-gated. The
  branches were never covered even pre-split; the move surfaced them. Cost: a
  second ~6.5-min producer run after adding the coverage. The producer ran FIRST
  (per the guardrail), so the gap surfaced at the boundary, not post-merge — but
  it discovered rather than confirmed.
- **Verdict-parity harness confound iteration (minor, well-handled).** The first
  parity diff flagged `remaining_minutes` (wall-clock) then `head_sha` (HEAD
  advanced on commit) — two benign confounds owned by untouched modules. Resolved
  cleanly by normalizing wall-clock in the harness and finally doing a pristine
  temp-revert (same HEAD, same goal text) so only the slice logic varied. The
  temp-revert is the gold-standard form; reaching for it first would have skipped
  the two normalization iterations.

## Critical Decisions

- **Split by concern, not by line count.** Disposition -> grammar/scope leaf vs
  rung-verdict orchestrator; closeout_evidence -> sibling-loader boilerplate leaf.
  Both fresh-eye reviewers judged the leaves genuinely cohesive (SHIP), satisfying
  the "no incoherent fragments" non-goal.
- **Re-bind pattern preserved the public + monkeypatch + ImportError surface.**
  Loading the leaf and re-binding its symbols as module attributes kept
  `ce._load_shared_helper` monkeypatchable (check_complete_evidence resolves the
  bare global at call time) and every importer/test green without editing them.
- **Pristine temp-revert parity proof.** Eliminating the wall-clock and head_sha
  confounds by comparing HEAD-inline vs split at the same HEAD/text gave a
  byte-identical behavior proof, the load-bearing boundary.

## Expert Counterfactuals

- **Michael Feathers (characterization-test / seam lens).** Before moving code
  into a new file, enumerate the *branches* of the functions being moved and
  confirm each is exercised — because the move re-gates every line as "changed,"
  a pre-existing uncovered branch becomes a new blocking signal. Feathers would
  have run the changed-line coverage probe against the *target functions'
  branches* in the introducing slice, making the bundle producer a single-pass
  confirmation instead of a discover-cover-rerun cycle.
- **Counterfactual (no persona).** Running the producer once at the FIRST slice
  boundary (not only at the bundle) would have surfaced the moved-branch gap one
  slice earlier, when the surface area was smaller and the re-run cheaper.

## Next Improvements

- **workflow:** For a verbatim-MOVE-into-new-file refactor, treat every
  pre-existing uncovered branch in the moved code as a newly-gated changed line —
  cover those branches IN the introducing slice (not just the new glue like
  `_load_local_module`). This refines the #339 "cover new lines in-slice" lesson
  to explicitly include moved-but-previously-uncovered branches.
- **memory:** Persist the refinement above to recent-lessons so the next
  module-split goal starts from it (this retro's persistence refreshes the digest).

## Sibling Search

Transferable waste pattern: **"a verbatim code-MOVE into a new file re-gates every
moved line as a changed line, so pre-existing uncovered branches in the moved code
become newly-blocking at the bundle boundary — discovered, not covered-in-slice."**

- axis: workflow/process (refactor coverage discipline). Recurs for ANY
  module-split / extract-leaf goal, not just this one.
- Closest sibling: the #339 carried lesson and the `2026-06-08-run-slice-closeout-module-split`
  precedent already say "cover new branches in-slice"; this is a *refinement*
  (the moved-but-previously-uncovered branch case), not a novel class.
- Decision: **recent-lessons refinement (memory)** — extend the existing
  in-slice-coverage guardrail wording rather than file a new issue; the structural
  home is the same recurring lesson, and no new gate is needed (the producer
  already catches it at the boundary; the fix is authoring discipline).

## Persisted

(stamped by persist_retro_artifact.py)
