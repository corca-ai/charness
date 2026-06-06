# Debug: #320 Mutation Changed-Line Coverage Regression
Date: 2026-06-06
Issue: #320

## Problem

The scheduled mutation run on `main` (head `d92a0106`, run 27048499611) reports
`Status: FAIL`, `Mutation score: PASS` (92.5%), `Blocking signals: FAIL`. The
blocking changed-line signal flags `scripts/staged_commit_gate_plan.py:72-73`
(`except _surfaces_lib.SurfaceError: return []`) as a test-uncovered changed
line; two more files are dropped by the selection/workload budget.

## Correct Behavior

Given a scheduled run computing changed lines over `base..head`, when an eligible
mutation-pool Python file has changed lines, then every changed line must be
covered (executed and mutation-killable) so the classifier does not drop the file
before mutation. The `except SurfaceError` degrade branch in
`fast_surface_verify_gates` must be exercised by a test.

## Observed Facts

- #320 body: score PASS (92.5% vs 80%), Blocking signals FAIL. Changed-line proof
  targets: `staged_commit_gate_plan.py:72 except _surfaces_lib.SurfaceError:` and
  `:73 return []`. <!-- reproduction-source -->
- Selection-budget drops (separate signal, no proof targets):
  `scripts/setup_agent_docs_fresh_eye_lib.py`, `scripts/setup_commit_discipline_lib.py`.
- Local coverage before fix: `staged_commit_gate_plan.py` 84%, `Missing` includes
  `72-73`. <!-- reproduction-source -->
- `git log d92a0106..HEAD` shows only `b92dd9f9` (#319) touched the file since the
  failing run; the two setup files did not change in that range.
- `match_surfaces` -> `normalize_repo_path` raises `SurfaceError` on a
  repo-escaping changed path (`../` or `/` prefix); that is the production path
  reaching 72-73 (the manifest is structurally validated by `load_surfaces`
  first, so a bad path is the real trigger).

## Reproduction

```bash
python3 -m coverage run --source=scripts.staged_commit_gate_plan \
  -m pytest tests/quality_gates/test_staged_commit_gate_plan.py
python3 -m coverage report --show-missing --include="*staged_commit_gate_plan.py"
# -> 84%  Missing: 49, 72-73, ...
```

Caveat (`skills/public/quality/references/mutation-testing.md`): a plain
`coverage run` under-reports subprocess-only scripts. Lines 72-73 are an
in-process branch, so the gap is real — the existing degrade test only hits the
sibling return sites 66/70.

## Candidate Causes

- Real coverage gap: the `except SurfaceError: return []` branch had no test
  exercising it (confirmed root).
- Measurement artifact: `coverage run` under-reporting subprocess coverage (ruled
  out — 72-73 is an in-process branch, not a subprocess-only file).
- Transient budget: the two setup files dropped by workload budget, not coverage
  (separate signal; unchanged in d92a0106..HEAD).

## Hypothesis

If a test calls `fast_surface_verify_gates(ROOT, ["../escape.py"])` — a
repo-escaping path that makes `match_surfaces` raise `SurfaceError` — then 72-73
execute and become covered, and a line-73 mutant (`return []` -> non-empty) is
killed. Falsifier: coverage still reports 72-73 missing, or the mutant survives.

## Verification

- PASS: new test `test_fast_surface_verify_gates_degrade_on_surface_error`
  (1 passed).
- PASS: coverage after fix — 85%, `Missing` no longer lists 72-73. <!-- reproduction-source -->
- PASS (targeted-mutant proof, bound to the gate target): mutated line 73
  `return []` -> `return [GateCommand('MUTANT', ('noop',))]`; the new test FAILED;
  the sibling degrade test (66/70) still PASSED (specificity); reverted; green.
- PASS: full `tests/quality_gates/test_staged_commit_gate_plan.py` (20 passed).
- NOT RUN: a fresh scheduled mutation run; the remote `base..head` verdict is
  CI-only and pending. A `workflow_dispatch` run cannot prove a changed-line fix
  (only `schedule` computes `base_sha`).

## Root Cause

The `except _surfaces_lib.SurfaceError: return []` branch (added with the #314
fast-surface-verify reconciliation) was never exercised. The existing degrade
test covers `manifest is None` and empty-paths (66/70) but not the `SurfaceError`
branch (72-73). The gate computed changed lines over a base predating that
branch, found uncovered changed lines, and dropped the file before mutation — the
recurring #219 -> #251 -> #260 class. The selection-budget drops are a separate,
non-coverage signal, not part of this fix.

## Invariant Proof

- Invariant: every changed line in an eligible mutation-pool file must be covered
  (executed AND mutation-killable) before merge, or the file is dropped.
- Producer Proof: the new test exercises 72-73 via a real `SurfaceError`;
  coverage confirms 72-73 left `Missing`.
- Final-Consumer Proof: targeted-mutant proof on proof-target line 73 shows the
  test kills the mutant; the `blocking_targets` path:line contract is satisfied.
  Scheduled-run consumer proof is CI-only and pending.
- Interface-Shape Sibling Scan: the three `return []` sites (66, 70, 73) checked;
  the degrade test pins 66/70, the new test pins 73.
- Non-Claims: does not prove the next scheduled run is green on the score path;
  does not address the two setup files' selection-budget drop.

## Detection Gap

- scheduled mutation gate | fired correctly and filed #320, but post-merge via
  the <=3h cron, not pre-merge | durable fix is covering the flagged lines
  in-slice; `scripts/check_changed_line_mutation_coverage.py` reproduces it
  pre-merge but needs a real `base_sha` + slow coverage probe and is not in the
  per-slice gate, so it stays CI/opt-in by design.
- new error-branch authoring | no per-slice gate counts a newly-added branch as a
  changed line needing coverage | the standing prevention is authoring coverage
  for error branches when added.

## Sibling Search

- Mental model: "degrade one-liners are too obvious to need a test" — wrong; the
  changed-line gate counts them as changed lines requiring coverage.
- return-site axis: 66/70/73 in `fast_surface_verify_gates` | 66/70 already
  covered by the degrade test, 73 now covered | proof: coverage + targeted mutant.
- other-error-branch axis: `collect_staged_paths` RuntimeError (48) | already
  covered by `test_collect_staged_paths_reports_git_error` | proof: that test.
- selection-budget axis: the two setup_*_lib files | out of slice — non-coverage
  workload signal, unchanged in d92a0106..HEAD, no proof targets | proof: issue
  lists them only under "Selection budget or nodeid" |
  follow-up: follow-up:mutation-selection-budget-setup-libs
- main()-CLI axis: 277-293 uncovered | pre-existing, not a changed line here |
  proof: not in #320 proof targets.
- cross-file: the selection-budget axis above names the two `setup_*_lib` files
  outside the subject `staged_commit_gate_plan.py`; the return-site and
  other-error-branch axes stay within the subject file (marker added by the #2b
  cross-file-scope enforcement, slice 2 of the quality-scan goal).

## Seam Risk

- Interrupt ID: issue-320-mutation-changed-line-coverage
- Risk Class: repeated-symptom
- Seam: the scheduled mutation gate keeps failing post-merge because a newly
  changed line in a mutation-pool file lacks coverage; 4th occurrence on this
  seam (#219 -> #251 -> #260 -> #320), and #251/#260 already proposed an
  unbuilt pre-merge detection follow-up. The per-file coverage fix is durable per
  file but does not address the missing pre-merge gate, so the class recurs.
- Disproving Observation: the local fix and targeted-mutant proof are in-process;
  the blocking verdict is computed by the scheduled run over a real `base_sha`,
  which a `workflow_dispatch` cannot reproduce.
- What Local Reasoning Cannot Prove: that the next scheduled run shows
  `Blocking signals: PASS`, and whether the setup-file budget drop recurs.
- Generalization Pressure: factor-now

## Interrupt Decision

- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/mutation-changed-line-premerge-gate.md

## Prevention

When adding a degrade/error branch to an eligible mutation-pool file, cover it
with a test in the same slice — the changed-line gate counts it as a changed line
needing coverage. The durable fix for the #219 -> #251 -> #260 class is test
coverage of the flagged lines, not a floor/budget tweak.
follow-up:mutation-selection-budget-setup-libs — confirm whether the
`setup_agent_docs_fresh_eye_lib.py` / `setup_commit_discipline_lib.py`
selection-budget drops recur on the next scheduled run; if so that is a
workload-budget tuning question, distinct from coverage.

## Related Prior Incidents

- `2026-05-27-issue-224-219-mutation-annotation-filter.md` — #219, same
  changed-line class.
- `2026-06-01-273-mutation-gate-helper-coverage.md` — #273, same "cover the
  changed lines" resolution.
- `2026-06-02-274-mutation-workflow-tokei-dependency.md` — prior `latest.md`,
  now a dated record.
