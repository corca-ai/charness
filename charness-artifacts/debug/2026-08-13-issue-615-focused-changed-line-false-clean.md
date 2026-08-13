# Issue 615 Focused Changed-Line False Clean Debug
Date: 2026-08-13

## Problem

For the same base and effectively the same head, the pre-push focused changed-line
lane exited 0 with `clean` while the CI mirror and an independent coverage JSON
read found five uncovered changed lines in a file the local lane said it analyzed.

## Correct Behavior

Given a mapped changed file with any changed line absent from the focused coverage
measurement, when the pre-push lane renders its verdict, then it must block or
render an explicit unproven state; it must never grant `clean` from missing,
stale, or otherwise non-comparable evidence.

## Observed Facts

- GitHub issue #615 is OPEN with `comments_read: true` and no comments.
- The local lane on base `d0c33e6b4a653bd758f5e5910c115819dd0333b4`
  reported `clean` and listed `publish_release_resume_state.py` among
  `changed_pool_files`.
- CI on `d315d989` blocked on lines 116, 117, 132, 133, and 134 of that file.
- A separate `coverage json` read found the same five lines absent; adding tests
  for the two classifier arms made them present and the next CI run green.
- In a detached worktree at `d315d989`, a planner test first required a named
  branch; after creating only that branch, fresh/no-reuse reproduced `clean`.
- The same isolated tree/base through the CI-shaped broad producer ran 8,867
  standing tests in 20m38s and blocked on exactly lines 116, 117, 132, 133, 134.
- Disabling xdist while retaining the focused wrapper still reported `clean`.
- The focused wrapper passes `--include-release-only`; the broad producer reads
  `cosmic-ray.toml`, whose command excludes `release_only`. Removing those 42
  cases from the same 26 focused test files leaves all five target lines missing.

## Reproduction

- Isolated worktree `d315d989`, local named branch, base
  `d0c33e6b4a653bd758f5e5910c115819dd0333b4`:
  focused fresh/no-reuse -> 535 passed, exit 0 `clean`, five lines executed;
  broad CI-shaped -> 8867 passed / 100 deselected, exit 1, the same five lines
  missing; focused with `PYTEST_ADDOPTS='-p no:xdist'` -> still `clean`; the
  focused 26 files with `-m 'not release_only'` -> 493 passed / 42 deselected and
  all five lines missing.

## Candidate Causes

- Stale reused coverage — disconfirmed by a fresh no-reuse reproduction.
- Export `include_paths=mapped` hides target lines — disconfirmed because the
  target row exists and explicitly marks all five lines executed.
- xdist worker collection changes the result — disconfirmed by the serial
  focused wrapper retaining `clean`.
- Producer command mismatch admits tests CI excludes — confirmed: local includes
  `release_only`; broad CI excludes it; removing only that marker class changes
  the five lines from executed to missing.

## Hypothesis

- Confirmed claim: the local wrapper's `--include-release-only` makes its test
  population not a subset of the CI broad producer's `-m 'not release_only'`
  population, so extra local-only execution can turn a broad-missing line into a
  focused-executed line. Disconfirmer: keep the focused files but apply the broad
  marker filter; all five lines become missing, which occurred.
- Claim type: attribution
- Candidate claim: the standing-runner optimization introduced the marker-policy
  mismatch by preserving the former bare-pytest population.
- Cheapest falsifier: inspect the introducing commit and its parent at
  `_focused_pytest_command`; a parent that already excluded `release_only` or an
  introducing change without the override would disprove the attribution.
- Result: confirmed — `git show 3c241399^:scripts/prepush_focused_changed_line_coverage.py`
  shows a bare pytest command with no marker filter, while commit `3c241399`
  replaced it with the standing runner plus `--include-release-only` and the
  explicit scope-preservation rationale.

## Verification

- Confirmed. Source-state reuse and xdist are not necessary; marker parity alone
  flips the exact target lines.
- Post-repair, the isolated `d315d989` wrapper over base `d0c33e6b...`, with the
  repair applied and no coverage reuse, returned 1/`blocked` on the same five
  `changed_and_missing` lines. Exact command and coverage fingerprint:
  ```text
  python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha d0c33e6b4a653bd758f5e5910c115819dd0333b4 --coverage-json /tmp/charness-615.DboDaN/repaired-focused-coverage.json --json
  ```
  `61d0508a8b49357386ff5f1c8f42e856fc6d39502b89584991df84bedea312e3`.
  The patched historical worktree also reported its expected dirty repair file;
  that additional non-clean signal is not clean-state or hosted-CI proof.

## Root Cause

1. The wrapper printed `clean` from focused evidence marking all five lines executed.
2. `--include-release-only` admitted those executions while `cosmic-ray.toml:5`
   excludes them, so the broad report marked the same lines missing.
3. The standing-runner optimization preserved old bare-pytest scope and treated
   file-target narrowing as the only subset dimension.
4. No executable comparability contract bound the focused marker regime to broad;
   its command test instead asserted the mismatching flag.

## Invariant Proof

- Invariant: when the focused coverage producer writes
  `reports/mutation/prepush-focused-coverage.json` <!-- reproduction-source --> from a test population whose
  marker policy is not a subset of the broad producer's policy, the changed-line
  consumer and final `prepush_focused_changed_line_coverage.py` wrapper must
  refuse `clean` until producer comparability is established.
- Producer Proof: fresh isolated focused JSON names all 12 mapped changed files
  and marks the five target lines executed only when release-only cases are
  admitted; the same focused targets under `-m 'not release_only'` leave those
  exact lines missing.
- Final-Consumer Proof: the wrapper passes that JSON to
  `check_changed_line_mutation_coverage.py`, translates its exit/payload at
  `scripts/prepush_focused_changed_line_coverage.py:419-435`, and prints `clean`;
  the same tree/base under the CI-shaped broad producer and consumer blocks on
  the exact five targets.
- Interface-Shape Sibling Scan: searched focused/broad coverage command owners,
  exported copies, and final quality renderers. The source and
  `plugins/charness/` wrapper copies share the mismatching flag; the closeout
  producer and full release-quality command intentionally own broad populations
  and make no focused-subset claim.
- Non-Claims: no claim about the frequency of false clean verdicts or broad CI
  correctness outside this one independently confirmed case; no repaired hosted
  CI or installed-plugin roundtrip exists before an authorized push.

## Detection Gap

- Focused command-shape test | asserted `--include-release-only` as scope
  preservation, never compared the CI marker regime | assert the flag is absent
  and pin the broad/focused marker parity.
- Final workflow | permanent tests split marker execution, coverage transport, and
  consumer verdict, while the repaired historical receipt binds their composition |
  retain all three proof layers and the exact incident receipt.
- Hosted mirror | caught the defect only after push | retain as external proof;
  local prevention is the producer-policy parity regression above.

## Sibling Search

- Mental model: selecting fewer test files is sufficient to make execution
  coverage a subset, even when marker policy admits tests the broad run excludes.
- same layer: `plugins/charness/scripts/prepush_focused_changed_line_coverage.py:194`
  | decision: same bug, fix now | proof: static scan only; repair through export
  sync.
- abstraction up: `mutation_coverage_producer.py` carries the exact broad command
  when closeout produces coverage and does not claim focused-subset equivalence |
  decision: intentional plain-text or non-rendering boundary | proof: local
  payload proof.
- specialization down:
  `tests/quality_gates/test_prepush_focused_changed_line_coverage.py:125-141`
  asserts producer command shape without executing a real release-only population
  | decision: same bug, fix now | proof: static scan only.
- mental-model sibling: `run-quality.sh:714` deliberately includes release-only
  for the full release-quality gate, but makes no subset-of-CI claim | decision:
  intentional plain-text or non-rendering boundary | proof: static scan only.
- cross-file: `cosmic-ray.toml:5` is the broad producer policy owner; the local
  wrapper must preserve its exclusion when narrowing targets.

## Seam Risk

- Interrupt ID: issue-615-local-ci-verdict-divergence
- Risk Class: host-disproves-local
- Seam: local focused coverage producer versus CI broad coverage producer.
- Disproving Observation: CI and an independent report read found the same five
  uncovered lines after the local lane printed `clean`.
- What Local Reasoning Cannot Prove: hosted CI equivalence for every environment,
  adapter, xdist schedule, or historical reused report.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-13-issue-615-focused-changed-line-verdict-contract.md

## Prevention

Remove the focused wrapper's release-only override, pin producer-policy parity in
the command-shape test, execute a real release-only sentinel through the focused
child command, retain the exact historical wrapper proof alongside existing
transport/final-consumer regressions, synchronize the plugin mirror, and preserve
hosted CI as an explicit post-push non-claim.
