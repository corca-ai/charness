# Mutation Changed-Line Blocker Self-Recurrence Debug
Date: 2026-05-24

## Problem

GitHub issue #209 (auto-filed by the scheduled Mutation Tests workflow). After
the #208 fix landed (`a11eb83`, then handoff `a30320c`), the very next scheduled
run (`26340465805`, on `a30320c`) failed again. The Python (Cosmic Ray) summary
reports `FAIL` with a *passing* reachable score (85.0% vs 80%) and `scope_gap=0`;
the blocking signal is "changed lines were left test-uncovered" naming exactly
one file under "Uncovered changed lines": `scripts/mutation_changed_files_lib.py`
— the new module the #208 fix itself introduced.

## Correct Behavior

When the bounded sampler reports success for a scheduled window, every changed
line in `base..head` that is an executable statement must be test-covered (so the
changed-line scope-gap blocker is empty), and a genuinely untested change must
still block. A new module added by a fix must have its own changed lines covered
before that fix is called verified.

## Observed Facts

- CI window base = previous completed run's `head_sha`
  (`.github/workflows/mutation-tests.yml` Plan step, outputs `base_sha`/`head_sha`).
  For run `26340465805` the window was `b9dbcf5..a30320c`, which spans the #208
  fix commit `a11eb83`.
- `a11eb83` added `scripts/mutation_changed_files_lib.py` as a brand-new 88-line
  file, so in that window every line of the file is a "changed line".
- The blocker (`scripts/mutation_changed_files_lib.py` `classify_changed_line_scope_gap`,
  called from `scripts/sample_mutation_files.py:401`) adds a changed pool file
  when `changed_lines ∩ missing_lines ≠ ∅`, surfaced as the manifest key
  `changed_line_uncovered_changed_files` / `SCOPE_GAP_BLOCKING_SECTIONS`
  (`scripts/mutation_sample_manifest_score_lib.py:11`).
- Local coverage of the module under its own test
  (`tests/quality_gates/test_quality_mutation_sampling.py`) is 97%: exactly one
  missing statement, **line 21** (`return set()` in `changed_line_numbers`).

## Reproduction

```
python3 -m coverage run --source=scripts.mutation_changed_files_lib \
  -m pytest tests/quality_gates/test_quality_mutation_sampling.py -q
python3 -m coverage report --show-missing --include="*/mutation_changed_files_lib.py"
# -> 39 stmts, 1 miss, 97%, Missing: 21
git diff -U0 --no-renames b9dbcf5..a30320c -- scripts/mutation_changed_files_lib.py
# -> @@ -0,0 +1,88 @@ ... +        return set()   (line 21 is a changed line)
```

`changed_lines ⊇ {21}` and `missing ⊇ {21}` ⇒ non-empty intersection ⇒ the file
is classified as an uncovered-changed-line gap ⇒ blocking.

## Candidate Causes

- The empty-base guard `if not base_sha: return set()` (`changed_line_numbers`,
  lines 20-21) is unreachable through its only production caller
  (`classify_changed_line_scope_gap` already returns on `not base_sha` before
  calling it), so no integration path or full-suite coverage run can incidentally
  execute line 21 — it is permanently uncovered. (confirmed primary cause)
- The #208 verification ran the sampler against `git diff base..HEAD` while the
  new module was still uncommitted, so `changed_line_numbers` returned an empty
  set, hit `if not changed: continue`, and the file never entered the gap list →
  false green at verification time. (confirmed contributing cause)
- The base SHA is stuck so the window keeps re-including stale files. (ruled out:
  base is the previous run's head; the window is `prev-run-head..current`.)
- The coverage command is too narrow to execute the module. (ruled out: line 21
  stays missing even when the module's own full test file runs under coverage.)

## Hypothesis

If the empty-base branch of `changed_line_numbers` (line 21) is exercised by an
assertion `changed_line_numbers(repo, "", head, path) == set()`, then the module
has no uncovered changed statements (100% statement coverage), so it can never be
a `changed_line_uncovered_changed_files` gap in any window, while genuinely
untested changes elsewhere still block.

## Verification

- After adding the empty-base assertion, coverage of
  `scripts/mutation_changed_files_lib.py` is 100% (39 stmts, 0 miss); 100%
  statement coverage means no changed line of this file can be in `missing` for
  any window, which is strictly stronger than reconstructing the CI manifest.
- `tests/quality_gates/test_quality_mutation_sampling.py`: 27 passed.
- `./scripts/run-quality.sh --read-only`: green except 2 pre-existing failures
  resolved by registering this artifact (debug-artifact + seam-index).

## Root Cause

The #208 fix introduced `changed_line_numbers` with a defensive empty-base guard
(`if not base_sha: return set()`, line 21) that mirrors the sibling helper
`list_changed`. But unlike `list_changed`, the guard is dead to every production
caller: `classify_changed_line_scope_gap` already short-circuits on
`not coverage_enabled or not base_sha` *before* it calls `changed_line_numbers`.
A line dead to its only caller is permanently uncovered, yet it is still a
"changed line" for any window that contains the file's introduction, so the
changed-line scope-gap blocker classifies the fix's own module as an
uncovered-changed-line gap and stays red. The #208 verification missed this
because it ran the gate against `git diff base..HEAD` while the new file was
uncommitted (working-tree content is invisible to `git diff base..HEAD`), so the
gate was structurally blind to its own new file until the commit landed.

## Detection Gap

- changed-line gate | a fix's own new file is invisible to a gate verified
  pre-commit against `git diff base..HEAD` | verify changed-line gates against a
  window that includes the committed change (commit-then-verify), not the
  in-progress working tree.
- defensive-guard coverage | a guard branch unreachable from its only caller is
  permanently uncovered yet still counts as a changed line | cover the empty-base
  branch with a direct assertion (added), matching the sibling `list_changed`
  empty-base test.

## Sibling Search

Mental model that produced the bug: *"a fix's own new file is covered by the
suite, so verifying the gate locally (pre-commit, full-suite coverage) proves the
next scheduled run is green."* Four-axis scan:

- same layer: other `if not <param>: return ...` guards in the mutation sampling
  helpers (`scripts/mutation_sampling_lib.py`, `scripts/mutation_changed_files_lib.py`) | decision: same class, diagnostic-only for this slice | proof: static scan only — each is reachable or guards a distinct param; none replicates the unreachable-from-sole-caller shape of line 21.
- abstraction up: any gate verified against `git diff base..HEAD` while exercised on a *new* artifact before commit → false green | decision: valid follow-up outside the slice | proof: static scan only | follow-up: deferred docs/handoff.md#discuss (changed-paths/changed-lines gates verified in-session on new files).
- specialization down: the sibling `list_changed` empty-base path | decision: intentional plain-text or non-rendering boundary | proof: local payload proof — already covered by `test_list_changed_skips_git_when_base_sha_is_empty`, so no action.
- mental-model siblings: covered by the abstraction-up axis (pre-commit verification window blindness) | decision: same class, diagnostic-only for this slice | proof: not inspected to runtime.

## Seam Risk

- Interrupt ID: mutation-changed-line-uncovered-guard-recurrence
- Risk Class: contract-freeze-risk
- Seam: git changed-line discovery -> coverage missing-lines -> changed-line
  scope-gap blocker -> pre-commit verification window
- Disproving Observation: after the fix, coverage of
  `scripts/mutation_changed_files_lib.py` is 100% (0 missing), so no window can
  classify it as a changed-line gap.
- What Local Reasoning Cannot Prove: the hosted scheduled run after push.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

When a fix introduces a new file that a changed-line/changed-paths gate will
score, verify the gate against a window that already contains the committed file
(commit first, then re-run the sampler), not against an in-progress working tree.
Prefer covering or removing guard branches that are unreachable from their only
caller, because they are permanently uncovered changed lines that will block the
next window spanning their introduction.
