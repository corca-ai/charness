# Session Retro: Mutation Changed-Scope-Gap Rescope
Date: 2026-05-24
Mode: session

## Context

Issue #208 (scheduled Mutation Tests red on `main` ~2 days) was the only
self-fixable open bug (#184/#185 are deferred ideation). RCA found the
changed-file scope-gap BLOCKER reused whole-file sample-selection predicates
(0.85 statement floor, 100% mutable-line), so a well-tested change to a
partially-covered CLI/validator failed on unrelated pre-existing untested lines.
Rescoped the blocker to changed lines (`mutation_changed_files_lib.py`), kept
whole-file filters as advisory selection diagnostics and budget exclusions as
blockers, and added the two genuinely-uncovered changed-line tests. Ran the
design→impl→pattern-scan→RCA→counterweight→closeout loop with five bounded
fresh-eye subagents; all converged on SHIP.

## Waste

- Implemented the full fix before running the file/function length gates, so
  `sample_mutation_files.py` (already 474/480) and its `main` (already ~99/100)
  blew past their limits and forced a mid-stream extraction into a new module
  plus a `main` compaction. Running `check_python_lengths` against a file that
  is already near its budget before adding to it would have surfaced the need
  for the new module up front.
- The added `bump_version` test duplicated ~75 lines of release-repo setup that
  already existed twice, pushing `test_docs_and_misc.py` past the 800-line test
  limit; the de-duplication helper that fixed it should have been the first
  move, not a reaction to the gate.

## Critical Decisions

- Rescoped the blocker rather than just raising coverage: the false positive was
  reproducible and systemic (every cron window touching a CLI script), so
  whack-a-mole coverage bumps would not stop the recurrence; the handoff named a
  recurring false-positive as the trigger to revisit #207.
- Chose changed-line *statement* coverage over mutation-line coverage for the
  blocker: avoids a Cosmic Ray init on every changed file and is the honest
  invariant a bounded sampler can guarantee; recorded the executed≠asserted
  weakening as a known limitation rather than hiding it.
- Kept budget exclusions (`selection`/`workload`) blocking; only the two
  whole-file coverage buckets became advisory (design-critique guidance).

## Expert Counterfactuals

- Tony Hoare lens: the bug was a contract mismatch — a selection heuristic
  doubling as a correctness gate. Naming the two questions separately ("worth
  mutating?" vs "is this change tested?") up front would have pointed straight
  at changed-line scoping instead of whole-file metrics.
- Kent Beck lens: the length-gate thrash was a "make the change easy, then make
  the easy change" miss — extracting the helper/module first would have made the
  feature edit small and gate-clean in one pass.

## Next Improvements

- workflow: before adding code to a script/test file, check its current line
  count against the 480/360/800 file and 100/150 function budgets; if it is
  within ~15 lines of a limit, extract first.
- workflow: when a quality gate is a *selection* heuristic reused as a *blocker*,
  scope the blocker to the changed surface (changed lines), not the whole
  artifact; keep the whole-artifact metric advisory.

## Sibling Search

- same layer: `scripts/check_coverage.py` per-file 0.85 floor as a hard blocker | decision: intentional boundary | proof: pattern-scan confirmed it is safe only because pinned to a fixed whole-repo `TARGET_FILES`, not a changed subset; added a guard comment so a future narrowing adopts changed-line scoping
- abstraction up: #183 mutation scope-gap hardening | decision: same-class, superseded | proof: #183 made whole-file changed-file exclusion blocking; this session inverts that to changed-line scoping and reopens #207 to record the contract change
- specialization down: StrykerJS `check_js_mutation_score.py` whole-slice blocking | decision: diagnostic-only | proof: Stryker mutates only the configured slice, so whole-slice blocking is honest; no changed-file mis-scope
- mental-model siblings: relevance triggers (`run-quality.sh coverage_relevant_changes_present`) and artifact validators using `git diff` | decision: diagnostic-only | proof: they gate existence/relevance at file granularity where that is the real signal, not a line-level metric

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-24-mutation-changed-scope-gap.md`
