# Debug skill claim-fidelity RE-CAPTURE — 2026-06-30 (post resolved-state fix)

## Verdict

**Floor MISS (cautilus `failed`/`reject`), but OUTCOME-SUBSTANCE PASS-dominant
(`pass_rate 0.8`).** The planner resolved-state fix is PROVEN to change behavior
(the run scaffolded a FRESH artifact and set `Resolution: resolved` at closeout),
but the run STILL skipped its floor reads — so the doc-skip is **independent of**
the `continue-existing-artifact` mis-fire, which was an *aggravating* factor, not
the cause. debug stays a HYPOTHESIS on the floor. The new outcome-assertion set
worked as designed: it graded the structural SUBSTANCE the floor cannot see.

## What ran

`/charness:debug` (the spec's gitignore-scanner bug-class prompt) on `HEAD`
=9981d7a2 (carrying the Slice 2 fix + the migrated `latest.md`), isolated worktree
capture, `--timeout-sec 1200`, exit 0 (finished naturally, NOT the cap — unlike the
prior 900s/exit-124 run). Tools: Bash=35 Read=15 Edit=13 Write=2 Skill=1 Agent=1.
11.26M total tokens, 817s wall. `cautilus evaluate observation`: `failed` (reject);
reference coverage 3/11.

## The planner fix worked (behavior changed)

- The run **scaffolded a fresh dated artifact**
  (`2026-06-30-repo-file-listing-strict-mode-recurrence.md`) instead of continuing
  the closed #365 pointer — the fixed planner routed
  `fresh-investigation-with-prior-memory` for the resolved pointer (proven
  deterministically in `tests/test_debug_plan.py` + on the live repo planner).
- The run **set `- Resolution: resolved`** in its own artifact's Interrupt
  Decision at closeout — the new forward mechanism (SKILL.md closeout prose)
  exercised live.

## The floor miss is real and INDEPENDENT of the mis-fire

- The run did NOT open `five-steps.md` or `debug-memory.md` (the floor), exactly
  like the prior capture — even though the fixed planner now emits them as the
  FIRST required reads in fresh mode. So a competent run reaches the structural
  outcome via the scaffold STRUCTURE without opening the canonical reference docs.
- This corrects the prior finding's framing: the mis-fire AGGRAVATED the doc-skip
  (it buried the reads) but is NOT its root cause. Removing the mis-fire did not
  produce the floor reads. The floor stays `[five-steps.md, debug-memory.md]`;
  do NOT soften it. debug stays a HYPOTHESIS on doc-opening.

## The outcome-assertion set discriminated SUBSTANCE (leg a validated)

Graded via `grade_skill_outcome.py --judge-cmd` (`outcome-grade.md`),
`pass_rate 0.8` (5/6 weighted):

- `detection-gap-substance` PASS — named the specific gate
  (`inventory_gitignore_scan_hygiene.py` DEFAULT_PATH_GLOBS / GIT_AWARE_MARKERS)
  and WHY it failed, with line refs.
- `sibling-search-substance` PASS — mental-model abstraction + per-sibling
  fix/follow-up/no-action decisions with reasons.
- `prevention-substance` PASS — 4 concrete moves tied to named gaps.
- `falsifiable-hypothesis-before-fix` **FAIL** — the run did STATIC-only analysis
  (`proof: static scan only`; no live CI red, no reproduction, no disconfirming
  check) before authoring its conclusion. A genuine discipline gap the FLOOR and
  the prior human prose ("competent structural RCA") both missed — caught only by
  the substance assertion. (Caveat: the bug class "fails only in CI" makes a live
  repro hard; a cheap local disconfirmer was still available and skipped.)

## Harness fix surfaced during grading (committed)

- The first grade FALSE-NEGATIVED `detection-gap` + `sibling-search` because the
  judge-context excerpted each output file at only 500 chars — the substance
  sections sit at the BOTTOM of a ~176-line artifact and were truncated away
  ("Output truncated at '## Correct Behavior'"). Fixed
  `grade_skill_outcome.py _output_excerpts` to `per_file=8000` with a 40KB total
  budget; re-grade moved those two to PASS. Without this, substance assertions are
  ungradeable on any non-trivial artifact — a real defect in leg (a)'s usefulness.

## Disposition

- Planner resolved-state fix: LANDED + proven (Slice 2).
- Outcome-assertion set: LANDED + proven to discriminate (Slice 1 + this grade).
- Judge excerpt-window fix: LANDED (this slice).
- debug stays HYPOTHESIS on the FLOOR. Open follow-up: the floor doc-skip is a
  skill-shape question (does the run need the docs when the scaffold supplies the
  structure?) — NOT a matcher/floor softening, and NOT this goal's scope.
- n=1 caveat. The `falsifiable-hypothesis` FAIL is the most actionable substance
  signal: debug runs reach answers via static analysis without a cheap
  disconfirmer — a candidate future skill/planner emphasis.
