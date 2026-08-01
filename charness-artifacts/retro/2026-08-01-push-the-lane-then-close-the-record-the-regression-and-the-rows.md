# push the lane then close the record the regression and the rows
Date: 2026-08-01

## Context

Four-lane goal: push the accumulated backlog to `main` and read the CI it triggers
(A); repair the goal-artifact closeout evidence record (B); settle #467's six
survived mutants and close it (C); disposition five sweep rows and answer D45's
premise (D). All four closed in one session.

The goal's stated purpose was closing the zero-denominator class — a green
rendered over a scope that could not have contained the question. **This run
committed that class three times, in three different lanes, and every instance
was caught by a bounded reviewer rather than by a gate.** That is the retro.

## Evidence Summary

- Lane A: pushed `989a1134..9ea738bb` (**31 commits** — the 30 already on the
  branch at activation plus the blockers commit the push gate forced) then
  `9ea738bb..f40ff27c` (**2**). **33 total**, by
  `git log --oneline 989a1134..f40ff27c | wc -l`. Counted rather than transcribed:
  earlier drafts of these records carried 29, 30, and 31 for this one quantity.
  Backlog empty
  (`git log --oneline origin/main..HEAD` → 0). Remote confirmed at `f40ff27c` via
  `git ls-remote`, a channel distinct from the push output. CI run
  `30702242447` — both jobs success. First run `30701478239` was RED; operator
  answered Q1 "fix forward".
- Lane B: 27 tests in `tests/quality_gates/test_goal_closeout_record_floors.py`;
  248 across the achieve goal-artifact families.
- Distinctness floor, **denominator stated because the headline figure is
  misleading without it**: 23 in scope of 147, **0 refused** — but 20 of those 23
  are artifacts with no parseable `Created:` line, in scope only because the
  predicate fails closed; **3 are dated, and only 2 were actually compared** (the
  third is this goal, whose evidence lines were still `TODO` at measurement time,
  so it short-circuited on "nothing to compare"). Armed anyway — the refusal is
  narrow and the defect is cheap — but "0 refused" is a green over a population
  that could not have contained a violation, and it is the SAME shape round 2
  refuted for the sibling floor in the same slice. See the corrected Sibling
  Search below. **Operator call 2026-08-02: stay ARMED, and replace the
  justification.** The corpus count is not what makes it safe; the rule is narrow
  enough to enumerate — pass, not-compared (a `skipped:` line has no path), and
  refuse — with no legitimate fourth case. The figure floor needed a corpus
  because its question is fuzzy; this one is settled by reading it. The
  enumeration is now pinned by a test rather than asserted in prose.
- Figure floor over the **127 dated** artifacts: strict form **90 refusals**,
  relaxed form **41** — not armed, recorded as D49.
- Lane C: scoped `cosmic-ray` run reproduced exactly the six mutants; re-run
  after the new test went **killed 65 → 66, survived 9 → 8**.
  `scripts/skill_gate_report_render.py` measured **0% (lines 10-34)** before and
  **100%** after.
- Lane D: 5 sweep rows dispositioned — 1 CLOSED, 3 NARROWED, 1 OPEN.
- 4 bounded reviewer spawns, all `parent-delegated`, all delivering findings
  inline.

## Waste

**The single largest waste was the pre-push gate, and it was not waste.** Three
full runs at ~700s each (~35 min wall clock) because the local hook runs
`run-quality.sh --read-only` over a 51-file changed set. Two of those three runs
were *necessary* — the first found two real blockers, the third confirmed the
repair. Only the mid-run polling around them was avoidable.

**Real waste, in order of cost:**

1. **Closing #467 before running its resolution critique.** The critique was
   authored, then the issue was closed, then the artifact validator demanded a
   fresh-eye line — which forced the reviewer spawn that found the closure was
   wrong. Running the review first would have cost the same spawn and saved a
   public correction comment on a closed issue. The ordering was backwards and
   the contract already says so.
2. **Round 1 of Lane B armed a floor on a number that meant nothing**, and round
   2 had to undo it: a rule-date change, a docstring rewrite, a D49 rewrite, six
   test rewrites. All of it caused by not asking "what is in this denominator"
   about my own measurement, in the goal about denominators.
3. **Duplicate-ratchet churn: five hard blocks across Lane B**, each requiring a
   classification pass, three of them pure fingerprint rotation caused by my own
   subsequent edits (including one caused by `ruff --fix` reordering an import).
   The verification plan says to run the ratchet at the FIRST edit to a gated
   file, not at the closeout aggregate. I ran it at the aggregate, five times.
4. Two `ruff` rejections after a green pytest, each costing a full closeout
   re-run. The commit-gate aggregate exists precisely to surface these together.

## Critical Decisions

- **Fix forward on the red CI rather than revert** (operator, Q1). Correct: the
  red was a missing test on four lines, and reverting 31 commits of validated
  work over it would have re-created the problem the push existed to solve.
- **Refute five of six mutants rather than kill them.** Killing the L65
  `ensure_ascii` mutant would have required making `check_chunk_contract` echo
  chunk text into its messages — writing a defect to satisfy a mutant. Refusing
  that is the whole point of allowing written refutations.
- **Disarm the figure floor after round 2, rather than defend the arming.** The
  measurement said 41 of 127 dated artifacts would refuse. A floor that refuses a
  third of a repo's existing closeouts describes a house style it disagrees with,
  not a defect.
- **Leave #467 closed and post a correction** rather than reopen. The blocking
  signal is now settled by direct line coverage — strictly stronger than the
  evidence the close originally offered — and reopening would churn the cron
  dedupe marker without changing that.
- **Record S37 as CLOSED, not REFUTED.** One `git show` at the sweep date
  separated "we were wrong" from "a later commit fixed it".

## Expert Counterfactuals

- **Goodhart, directly.** Every one of this run's three zero-denominator
  instances took the same shape: an honest metric, then a scope quietly chosen so
  the metric reads clean. Round 1's "0 refused" is the purest example — it did not
  fake a number, it selected a population. A Goodhart lens applied to *my own*
  measurements, not just to the gates under review, would have caught all three
  before a reviewer did. The operational form is one question: **"what is in the
  denominator, and could it have contained the thing I am claiming?"**
- **Feynman's "you are the easiest person to fool."** The run applied rigorous
  denominator scepticism to `check_doc_links`, to the parity gate, and to the
  local changed-line gate — and none to its own three measurements. The
  asymmetry is the finding: scepticism was aimed outward by default.

## Sibling Search

- axis: measurement-scope | location: every `*_RULE_DATE`-grandfathered floor in
  `skills/public/achieve/scripts/` | decision: valid follow-up outside the slice |
  proof: **this is not tomorrow's risk — it happened today, in this slice.** The
  distinctness floor shipped ARMED on "23 in scope, 0 refused", where 20 of 23 are
  undatable and only 2 were really compared. A closeout-claims review caught the
  retro describing it as a future hazard while it sat one screen above.
  `test_the_corpus_measurement_the_non_arming_rests_on` asserts a non-empty DATED
  denominator for the FIGURE floor only; no sibling floor, including the one armed
  here, makes that assertion | follow-up: issue #470
- axis: review-ordering | location: `issue` resolution closeout | decision: the
  resolution critique must precede the irreversible close, not follow it |
  proof: this run closed #467 and then discovered the closure was wrong |
  follow-up: issue #470

## Next Improvements

- workflow: run the resolution critique and its fresh-eye round BEFORE the issue
  close, not before the artifact validator. Filed as #470.
- capability: a shared assertion for Created-gated floors that a corpus
  measurement's denominator contains dated artifacts, so "0 refused" cannot be
  produced by grandfathering. Filed as #470.
- memory: the transferable rule is **"a clean measurement of my own work needs
  its denominator stated before it is believed"**. Disposition is `applied:` — it
  is written into this run's Auto-Retro and into the goal's lessons, not filed to
  #470, which carries the two STRUCTURAL items only.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md
