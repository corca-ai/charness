# Mutation Changed-Scope-Gap Whole-File Blocking Debug
Date: 2026-05-24

## Problem

GitHub issue #208 (auto-filed by the scheduled Mutation Tests workflow). The
scheduled `Mutation Tests` workflow has been red on `main` continuously since
2026-05-21 18:56 (last green run `26246717249`); every 3h cron run since then
failed. The Python (Cosmic Ray) summary reports `FAIL` with a passing reachable
score (e.g. 87.4% vs 80%) and `scope_gap=0`, but the blocking signal is
"changed files were excluded before mutation by coverage, mutation-line, or
selection-budget filters."

## Correct Behavior

When the bounded mutation sampler reports success for a scheduled run, the
changed code in the `base..head` window must have received trustworthy mutation
signal: the *changed lines* must be test-covered (so they could be mutated),
and a genuinely untested change must still block. A well-tested change to a file
that happens to contain unrelated, pre-existing untested plumbing must NOT
block.

## Observed Facts

- Base SHA selection is the previous completed run's `head_sha`
  (`mutation-tests.yml` Plan step), so the window is `prev-run-head..current`,
  not a stuck base.
- Gate logic (`scripts/check_mutation_score.py:200-207`): `score_passes`
  requires `changed_scope_gap_count == 0`, derived from the manifest
  scope-gap union (`scripts/mutation_sample_manifest_score_lib.py`).
- The union was `file_coverage_excluded + mutation_line_excluded +
  selection_excluded` — the first two are pure whole-file predicates
  (`scripts/mutation_sampling_lib.py`: 0.85 statement floor; 100% mutable-line).
- This is the deliberate #207 / #183 hardening ("changed-file exclusions are
  blocking", `charness-artifacts/issue/2026-05-21-issue-183-closeout.md`).

## Reproduction

Ran the sampler locally with full-suite coverage for the next-run window
(base=`000b584`, head=`HEAD`/`b9dbcf5`). All 4 changed pool files were excluded
→ `changed_scope_gap_count=4` → the next run would fail again (no self-heal):

| File | changed lines | uncovered changed | classification |
|---|---|---|---|
| `scripts/artifact_validator.py` | 124 | none | mutation-line bucket (uncovered mutables 18,36,41,54,88,181 are UNRELATED to the change) — false positive |
| `skills/public/issue/scripts/issue_runtime.py` | 85-94 | none | file-floor bucket (file 68% from unrelated CLI plumbing) — false positive |
| `skills/public/issue/scripts/issue_tool.py` | 224-229 | 229 | `command_brief_path` success emit untested — genuine gap |
| `skills/public/release/scripts/bump_version.py` | 109-113 | 111 | valid `--set-version` assignment untested — genuine gap |

## Candidate Causes

- The changed-file scope-gap blocker reuses whole-file SAMPLE-SELECTION
  predicates (0.85 statement floor, 100% mutable-line) as a change-set gate.
- The base SHA is stuck so the window keeps growing (ruled out: base is the
  previous run's head; window is `prev-run-head..current`).
- The two genuine gaps (`issue_tool:229`, `bump_version:111`) are real untested
  changed lines, so the gate is partly correct, not purely a false positive.
- Coverage is computed from too narrow a test command (ruled out: the coverage
  command is the full suite, `pytest -m 'not release_only' tests`).

## Hypothesis

If the changed-file scope-gap blocker judges only the *changed lines* (changed
lines ∩ uncovered statements) instead of whole-file selection metrics, and the
two genuinely-uncovered changed lines get tests, then the next run's
`changed_line_uncovered_changed_files` is empty while a genuinely untested
change still blocks.

## Verification

- Re-ran the sampler for `000b584..HEAD` after the fix plus the two coverage
  tests: `changed_line_uncovered_changed_files = []`; the whole-file exclusions
  remain recorded as advisory only. The next scheduled run passes on this axis.
- `tests/quality_gates/test_quality_mutation_sampling.py` and
  `test_quality_mutation_score_validity.py`: changed-line blocker, advisory-only
  pass, budget-still-blocks, and hunk parsing all green.
- New coverage tests cover `issue_tool` brief-path success and `bump_version`
  valid `--set-version`; `./scripts/run-quality.sh --read-only` otherwise green.

## Root Cause

The changed-file scope-gap BLOCKER reused the whole-file SAMPLE-SELECTION
predicates (≥0.85 statement coverage; 100% of the file's mutable lines covered).
Selection predicates answer "is this file worth spending mutation budget on";
the change-set guarantee should answer "is this CHANGE test-covered". Conflating
them means a small, regression-tested fix to a large CLI script is blocked
purely because unrelated, pre-existing lines in the same file are uncovered.
Because `main` commits frequently touch CLI/validator/release scripts that
always carry some uncovered plumbing, nearly every cron window contained ≥1 such
file → permanent red. It is a producer/consumer predicate mismatch — the same
defect *class* as #183 but inverted: the downstream blocker is now stricter than
what a bounded sampler can or should prove.

## Detection Gap

- mutation gate | no test asserted that a well-tested change to a
  partially-covered file passes the changed-file blocker | added a changed-line
  scope-gap predicate and a passing advisory-only test.
- changed-line scope | the blocker had no concept of changed-line coverage,
  only whole-file selection | added `classify_changed_line_scope_gap`.

## Sibling Search

- Sibling scan (fresh-eye) found no true sibling. Closest adjacent surface is
  `scripts/check_coverage.py` (same 0.85 per-file floor as a hard blocker) but
  it is safe because pinned to a fixed whole-repo `TARGET_FILES` list, not a
  changed subset; a guard comment now records that constraint.
- Relevance triggers (`run-quality.sh coverage_relevant_changes_present`) and
  artifact validators use changed-paths for existence/relevance, not as a
  line-level metric, so they cannot mis-scope the same way.

## Seam Risk

- Interrupt ID: mutation-changed-scope-gap-whole-file
- Risk Class: contract-freeze-risk
- Seam: git changed-line discovery -> coverage missing-lines -> changed-file
  scope-gap blocker
- Disproving Observation: local sampler re-run for `000b584..HEAD` reports
  `changed_line_uncovered_changed_files = []` after the fix; whole-file
  exclusions stay advisory.
- What Local Reasoning Cannot Prove: the hosted scheduled run after push.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

Keep selection predicates (whole-file coverage floor, whole-file mutation-line)
separate from the change-set blocker; the blocker must judge the change, not the
whole file. Decision: ship statement-coverage of changed lines — it avoids a
Cosmic Ray init on every changed file and is the honest invariant a bounded
sampler can guarantee. Known limitation (recorded in the #207 reopen): the
blocker treats an incidentally-executed-but-unasserted changed line as covered,
so it is weaker than the old whole-file mutation-line filter; sampled files
still get full mutation+score rigor, and this is a recovery gate, not the only
line of defense. Reopen #207 with this reproducible evidence rather than closing
#208 alone, so the by-design contract record matches the code.
