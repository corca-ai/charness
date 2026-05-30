# Achieve Goal: #260: Mutation test regression on main

Status: draft
Created: 2026-05-31
Activation: `/goal @charness-artifacts/goals/2026-05-31-260-mutation-test-regression-on-main.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

#260: Mutation test regression on main

**Objective.** Make the scheduled mutation gate green again on `main` and raise
durable mutated-behavior coverage so this regression class stops recurring. #260
is the **third** instance of this class (#219 → #251 → #260), so the chosen scope
is **thorough + preventive**: clear both failing signals, kill **all 22** survived
Python mutants, and add a **local changed-line mutation-coverage teeth** that
would have caught the blocking signal before the scheduled cron run.

Two independent failing causes are bundled under #260:

1. **Blocking signal (one of the two FAIL causes) — uncovered *changed* lines.**
   Three v0.13.0 coordination-cues achieve scripts shipped with changed lines
   left test-uncovered, so the sampler dropped them *before* mutation:
   `skills/public/achieve/scripts/check_goal_artifact.py` (+8),
   `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py` (+28),
   `skills/public/achieve/scripts/goal_artifact_coordination_floors.py` (+283 — the bulk).
   This is the recurring class and the only one the preventive teeth can catch
   cheaply.
2. **Score signal (the *other* FAIL cause, new vs #251) — 78.2% < 80%.**
   `killed 79 / (killed 79 + survived 22) = 78.2%`. The score fail is driven by
   **fill-sampled latent gaps**, not the changed files. The dominant cluster is
   `scripts/render_cli_reference.py:102`
   (`output = args.output if args.output.is_absolute() else repo_root / args.output`):
   the existing test `test_render_cli_reference_matches_checked_in_doc` *does* run
   `main()` as a subprocess, but passes an **absolute** `--output`, so the
   `else repo_root / args.output` branch never executes — leaving the 8
   `ReplaceBinaryOperator_Div_*` mutants (one per operator) plus the
   `mkdir(parents=True, exist_ok=True)` / `return 0` mutants alive. The CI
   "Top definitions: `main`: 18" is aggregated by *function name* across **all**
   fill-sampled files (per critique A3), so it spans `render_cli_reference.main()`,
   `check_glow_backend.main()` (its `ensure_ascii=False` is the two
   `ReplaceFalseWithTrue`), and `setup_artifact_policy_lib.py` — it is **not** one
   function. Remaining survivors: `run_help` ×3 (render_cli_reference) and
   `_load_render_module` ×1 (in `check_glow_backend.py`, **not** render — critique A2).

Covering the blocking trio (cause 1) pulls their now-covered changed lines into
the *next* run's mutation denominator, so those new mutants must be killed too
(the #251 dynamic). Thorough scope kills cause-2 survivors for durable coverage.

**Source handoff entry #3: #260: Mutation test regression on main**

> <!-- corca-ai/charness-mutation-test-regression -->
> Mutation testing failed on `454f7ddcadc8aac9048d1f849d631d1595dbdc42`.
>
> Workflow run: https://github.com/corca-ai/charness/actions/runs/26684100469
>
> # Mutation Testing Summary
>
> - Status: **FAIL** (78.2% reachable score vs 80% threshold)
> - Total mutants: 115 / Executable: 101 / Killed: 79 / Survived: 22 / Skipped: 14
> - Blocking signal: changed lines were left test-uncovered before mutation.
>
> ## Survived Mutants — top definitions: `main`: 18, `run_help`: 3, `_load_render_module`: 1
> Top operators: `ReplaceFalseWithTrue`: 2, `NumberReplacer`: 2, `ReplaceBinaryOperator_Div_*`: 8 (one per operator)
> Sample: `scripts/render_cli_reference.py:102` `main` — `output = args.output if args.output.is_absolute() else repo_root / args.output`
>
> ## Changed files with uncovered changed lines (blocking)
> - `skills/public/achieve/scripts/check_goal_artifact.py`
> - `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
> - `skills/public/achieve/scripts/goal_artifact_coordination_floors.py`
>
> ## StrykerJS slice: **PASS** (91.9%) — 7 survivors in `skill-test-telemetry.mjs` (out of scope)
>
> # Mutation Sample
> - Base SHA: `9565b923d61e525a7f85bd2e5a0fd41430d88011`
> - Head SHA: `454f7ddcadc8aac9048d1f849d631d1595dbdc42`
> - File coverage floor: 0.85 / Executable mutant budget: 120 / Selected: 3/5
> - Fill sample: `scripts/setup_artifact_policy_lib.py`, `scripts/render_cli_reference.py`, `skills/support/markdown-preview/scripts/check_glow_backend.py`

The full unabridged CI report is preserved in the GH Actions run linked above and
in this goal's git history; trimmed here to keep the artifact within the size gate.

## Non-Goals

- **Not a release:** no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk (no #250,
  #252, real-host proof here).
- **Not a rework of the gate / sampler / threshold.** `score_break: 80`, the
  0.85 coverage floor, cosmic-ray + StrykerJS runner choice, and selection
  budgets stay as-is. Do not retune any of them to mask the gap — fix the cause
  (missing tests), not the gate. CI-only-failure-triage policy is #236's job.
- Do not chase the 7 **StrykerJS** survivors (`skill-test-telemetry.mjs`): that
  slice PASSes (91.9% ≥ 80%) and is not part of #260's FAIL.
- **Preventive teeth is changed-line-coverage only.** It is NOT a full local
  mutation runner and does NOT attempt to prevent *score*-path regressions
  locally (those need full mutation runs and stay CI-only). **No existing issue
  owns local score-path prevention** (critique A5): #236 is the CI-only-failure
  *triage*/cost tension reference, not its home — if local score-path prevention
  is ever pursued, file a new issue. The teeth reproduces only
  `classify_changed_line_scope_gap` over a base..head range.
- Do not auto-close #219 as subsumed without independently verifying its specific
  survivors are killed by this work (the #251 resolution-critique correction).

## Boundaries

- **Source under test (must gain mutated-behavior coverage):**
  - Blocking trio: `skills/public/achieve/scripts/check_goal_artifact.py`,
    `goal_artifact_closeout_evidence.py`, `goal_artifact_coordination_floors.py`
    (+ `goal_artifact_lib.py`, advisory-excluded).
  - Score survivors: `scripts/render_cli_reference.py` (`main` — the line-102
    relative-output branch — and `run_help`),
    `skills/support/markdown-preview/scripts/check_glow_backend.py` (`main`,
    `_load_render_module`), `scripts/setup_artifact_policy_lib.py`.
- **Test surfaces (where edits land):** `tests/quality_gates/test_command_docs_gate.py`
  (render_cli_reference `main()`), achieve test suite for the trio, and
  test files for setup_artifact_policy / markdown-preview survivors. Add new test
  files only where no home exists.
- **Preventive-teeth surface (Slice 4):** a new local script under `scripts/`
  reusing `scripts/mutation_changed_files_lib.py` (`classify_changed_line_scope_gap`,
  `changed_line_numbers`) and `scripts/mutation_sampling_lib.py` (`read_test_command`,
  `run_test_coverage`, `load_file_statement_lines`, `select_test_nodeids`) — the
  lib that actually holds the wrapper's deps (critique A4); its own targeted test;
  optional pre-push wiring via `.githooks/`/quality adapter only if it stays bounded.
- **Verification tooling (read/run, do not redesign):** `scripts/sample_mutation_files.py`,
  `scripts/mutation_changed_files_lib.py`, `scripts/mutation_line_coverage_lib.py`,
  `scripts/run_cosmic_ray_mutation.py`, `scripts/check_mutation_suite_score.py`,
  `.github/workflows/mutation-tests.yml`, `.agents/quality-adapter.yaml`.
- Portable per implementation-discipline: no host-specific assumption; tests run
  under the repo's standard `pytest`.
- **Stop conditions:** (a) if the uncovered changed lines / survivors cannot be
  reproduced locally on current `main` (base/head drift made them no longer
  changed, or a survivor is equivalent), name it and ask before guessing — do not
  fabricate a target set; (b) if Slice 4's teeth exceeds a bounded thin-wrapper
  size or needs gate-design decisions, file it as an issue and defer rather than
  balloon this goal.

## User Acceptance

The user can confirm completion by:

- Seeing **#260 closed** with a comment linking **two** proofs (they cannot be one
  run — the #251 B1 lesson): a green `workflow_dispatch` full run showing the
  previously-survived mutants killed and Python score ≥ 80% (**score path**),
  **and** the local sampler reproduction (explicit base/head) showing **0
  blocking** changed files for the trio (**blocking path**). The next scheduled
  cron run is the async CI confirmation of the blocking fix.
- Running the new **preventive teeth** locally against a base..head range and
  seeing it flag uncovered changed lines (and pass clean on the fixed tree).
- Running the Slice-Log–named local commands (sampler with
  `MUTATION_BASE_SHA`/`HEAD`; `python3 scripts/check_mutation_suite_score.py`) and
  seeing them pass.
- Reading new/extended tests that name the exact behaviors that were unmutated
  (notably `render_cli_reference.main()` relative-output-path resolution).

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` on the new/extended test files passes.
- **Reproduce the actual gate predicate locally** (#251 B2 lesson): the blocking
  "uncovered changed lines" signal is *not* `check_coverage.py` (whole-file floor
  on a fixed list). The real predicate is
  `scripts/mutation_changed_files_lib.classify_changed_line_scope_gap`, driven by
  the sampler. Run `scripts/sample_mutation_files.py` with
  `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` set to the range that flags the trio;
  confirm the 3 files appear blocking *before* the fix and **0 blocking** after.
  Reproduce coverage through the gate's own subprocess-capturing `run_test_coverage`,
  never a naive `coverage run` (#251 waste lesson — subprocess scripts read 0%).
- The new preventive-teeth check, run against the failing base..head range,
  reports the trio as blocking; run against the fixed tree, reports clean.
- `pre-commit` cheap gates (incl. `check_python_lengths`) pass on staged files.

### High-Confidence Checks

- **Targeted local mutation re-run** scoped (via the sampler rewriting
  `cosmic-ray.toml`) to the affected source files: all 22 named survivors now
  **killed**, no new survivors introduced; newly-covered achieve-trio lines killed.
- Full repo `pytest` green (no regression from the new tests).
- `check_mutation_suite_score.py` reports Python score ≥ 80%.

### External Or Live Proof

> The #251 B1 split still holds: `workflow_dispatch` computes **no `base_sha`**
> (only `schedule` does — `mutation-tests.yml` ~L129-146), so a dispatch run has
> zero changed files and the blocking changed-line classifier returns
> non-blocking by construction. A dispatch green proves **only the score/survivor
> path**, never the blocking-trio fix.

- **Score / survived-mutant fix → `workflow_dispatch` full run** on the fix commit:
  record run URL + green summary showing the named survivors killed and score ≥
  80%. Honest live proof for the score path.
- **Blocking-trio fix → next *scheduled* (cron) run** is the only CI path that
  re-runs the changed-line classifier (async, ≤3h cadence). It is the user's
  confirmation step, not a closeout blocker; the deterministic stand-in produced
  now is the local sampler reproduction above.
- Per Honest Proof Discipline: the After report states which proofs ran. If the
  dispatch run cannot be triggered from this host, mark live proof not-run; do
  **not** claim the blocking signal is CI-proven off a dispatch run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Reproduce + locate on current `main` | Pin the exact uncovered changed lines + survivor call sites before writing tests; guard against base/head drift (current `main` is past `454f7dd`) | Concrete line list per file + survivor→function map; faithful gate repro showing the trio blocking + the 22 survivors (or an explicit "no longer reproduces" finding) | planned |
| 2 | Cover the blocking trio | This is one of the two FAIL causes and the recurring class; greening it is the foundation | Targeted tests added; changed-line coverage for the 3 achieve scripts ≥ floor with 0 changed&missing; pytest green | planned |
| 3 | Kill all 22 survivors (thorough) | The other FAIL cause; crosses the 80% score and raises durable coverage | `render_cli_reference.main()` test passing a **relative** `--output` to pin the line-102 branch (kills the `Div_*` cluster + mkdir/return-0); `run_help`, `check_glow_backend.main()`/`_load_render_module`, `setup_artifact_policy` pinned; targeted local mutation re-run kills all 22 | planned |
| 4 | Preventive teeth (changed-line mutation-coverage check) | 3rd recurrence; realizes #251's deferred "base/head changed-line-coverage helper" so the blocking class is caught pre-merge, not by cron | New thin local script reusing the sampler/classifier + its targeted test; demonstrated catching the trio on the failing range; bounded (defer-and-file if it balloons) | planned |
| 5 | Prove + dispatch + close | The CI gate is the real acceptance; close #260 on the two-proof story | `workflow_dispatch` run URL + green summary (score path); local sampler 0-blocking repro (blocking path); full pytest + suite-score; #219 re-checked (close-or-leave with reason); #260 closed citing both + next-cron note | planned |

## Slice Log

### Slice 1: Reproduce + locate on current `main`

- Objective: Pin the uncovered changed statement lines + the 22 survivor sites on current `main` before writing tests
- Why this approach: Faithful gate repro through the gate's own `run_test_coverage` + `classify_changed_line_scope_gap` (#251 B2), not a naive coverage run. Survivor set proven via the cheaper targeted scoped re-run path (Context Sources A1), not by reproducing the CI fill sample.
- Commits: (recorded with Slice 2)
- What changed: No source change — investigation only. Goal Slice-Log updated.
- Alternatives rejected: Reproducing the exact CI fill sample with `MUTATION_SAMPLE_SEED` — rejected as costlier and unnecessary (A1 allows proving survivors killed via the scoped re-run instead).
- Targeted verification:
  - **Drift guard passed:** trio source AND its test files are unchanged `454f7dd..HEAD(105edd2)` (0 diff lines each); changed-line counts over base..head match exactly (check_goal_artifact +8 = L100-107, closeout_evidence +28 = L190-207/212-214/301-307, coordination_floors +283 = L1-283). `f55be70` (added both the trio source AND comprehensive tests) is inside base..head, so the tests were present when CI failed.
  - **Blocking trio reproduced (all 3 block):** ran the full-suite coverage probe (1849 passed, 388s) then `classify_changed_line_scope_gap` over base `9565b92`..head `454f7dd`. Exact uncovered changed lines: `check_goal_artifact.py` = **whole file NOT TRACKED** (only run via subprocess → coverage reads 0%, the #251 lesson; never executed in-process by pytest); `goal_artifact_closeout_evidence.py` = **L202** (`raise ImportError` in `_load_sibling_coordination_floors`); `goal_artifact_coordination_floors.py` = **L110** (`_mask_fences` unbalanced-fence fail-open `return text`) + **L129** (`_section_span` heading-at-EOF `return (len,len)`). Comprehensive tests exist but miss these specific error/fail-open branches; the classifier blocks on ANY uncovered changed line.
  - **Survivor set reproduced (scoped cosmic-ray, faithful filter):** scoped config over the 3 fill-sampled files + focused nodeids derived from the same coverage JSON (CI's own mutation-test-command construction). Filter: **115 pending → 14 filtered → 101 executable** (matches CI "Executable: 101"). Result: **80 KILLED, 15 SURVIVED, 6 NO_TEST** (NO_TEST = also not-killed) = 21 not-killed, all in render+glow; `setup_artifact_policy_lib.py` = **0 survivors** (focused setup_inspect tests already kill all its mutants — explains why "main:18" is an aggregate, A3). Map: `render_cli_reference.py` — L102 Div cluster **11** mutants (5 SURVIVED + 6 NO_TEST; else-branch `repo_root / args.output` never runs because the existing test passes an ABSOLUTE `--output`), L103 `parents=True`→False ×1, L57 `check=False`→True ×1, L61 `!=`→`<`/`>` ×2 (run_help, A-confirms `run_help:3`); `check_glow_backend.py` — L13 `or`→`and` ×1 (`_load_render_module`, A2 confirms it lives here not render), L23 `ensure_ascii=False`→True ×1 + `indent=2` NumberReplacer ×2, L24 `==`→`is`/`>=` ×2 (`main`).
- Test duplication pressure: n/a (no tests added this slice)
- Critique: The 22-vs-21 count delta is expected — survivor set is sample/seed/test-command-dependent (A1); the local scoped set is the authoritative target for THIS tree. The line-102 cluster is the dominant gap and a single relative-output test kills all 11 (any non-`/` operator on two Paths raises TypeError). Trio newly-covered lines will enter the next run's mutation denominator (#251 dynamic) → Slice 3's re-run must include the trio to confirm those new mutants die too.
- Off-goal findings: none
- Lessons carried forward: `check_goal_artifact.py` is NOT TRACKED (whole-file block) because no in-process test exercises it — the Slice-2 test must `import` it and call `main()` in-process, not just shell out (subprocess-only → 0% coverage, #251). The 6 NO_TEST line-102 mutants are not-killed exactly like SURVIVED — both fall to the relative-output test.
- Metrics: coverage probe 388.46s / 1849 passed, 4 skipped; scoped mutation baseline 115→101 executable, 21 not-killed (when available).

### Slice 2: Cover the blocking trio

- Objective: Add tests covering every changed statement line in check_goal_artifact / goal_artifact_closeout_evidence / goal_artifact_coordination_floors so none block the gate
- Why this approach: Target exactly the Slice-1 gap lines (not blanket coverage) and pin each as real behavior, not coverage-chasing. All four tests live in `test_goal_coordination_floors.py` (the feature's natural home) so no new test file is needed and the achieve lib gains zero re-export lines (Boundary: single-file gate).
- Commits: (this slice)
- What changed: `tests/quality_gates/test_goal_coordination_floors.py` +4 tests: (1) `_mask_fences` unbalanced-fence fail-open → floors L110; (2) `_section_span` heading-at-EOF empty span → floors L129; (3) `_load_sibling_coordination_floors` raises ImportError when spec is None (monkeypatched) → closeout L202; (4) `check_goal_artifact.main()` in-process CLI test refusing a complete goal with an unsatisfied gather floor → makes the whole file TRACKED and covers L100-107. No source changed.
- Alternatives rejected: A new dedicated test file per script — rejected (would fragment the floors tests and risks a new re-export through the line-gated lib). Running check_goal_artifact via subprocess `run_script` — rejected: subprocess-only execution reads 0% under the gate probe (the #251 / Slice-1 NOT-TRACKED lesson), so it must run `main()` in-process.
- Targeted verification: `pytest test_goal_coordination_floors.py` 29 passed (was 25). Faithful re-run of the gate predicate over the achieve suite (gate's own `run_test_coverage` → `classify_changed_line_scope_gap`, base 9565b92..head 454f7dd): **0 blocking**; all three trio files report `changed&missing=[]` (check_goal_artifact now TRACKED). The full-suite confirmation is deferred to Slice 5.
- Test duplication pressure: low — the 4 tests target branches no existing test reaches (error/fail-open/CLI paths); the CLI test reuses the existing `_seed` helper and the established full-goal shape. No near-duplicate of an existing assertion.
- Critique: The CLI test asserts on the printed issue substring "coordination floors: gather step missing" — a behavior pin, but it couples to that exact phrasing; acceptable since the phrasing is itself the changed-line surface under test. The scoped (achieve-suite) verification could in principle differ from the full-suite gate if a trio line were covered only by a non-achieve test — but here every gap line is covered by the new tests directly, and Slice 5 re-confirms on the full suite.
- Off-goal findings: none
- Lessons carried forward: covering these changed lines pulls their mutants into the next run's denominator → Slice 3's targeted mutation re-run must include the trio to confirm the newly-covered lines' mutants die (the #251 dynamic).
- Metrics: scoped achieve-suite coverage probe 87 passed / ~3s; 0 blocking (when available).

### Slice 3: Kill all 22 survivors (thorough)

- Objective: Pin every survived-mutant behavior — render_cli_reference main() path resolution, run_help, _load_render_module, setup_artifact_policy, check_glow_backend
- Why this approach: In-process tests that exercise the exact mutated branches (the existing subprocess tests are whitespace/encoding-insensitive and only hit the absolute-output / healthy-status paths). One relative-output test kills the whole line-102 Div cluster (any non-`/` op on two Paths raises TypeError). Mocked payloads pin the glow ensure_ascii/indent/`==` decisions. Verified by a faithful scoped cosmic-ray re-run.
- Commits: (this slice)
- What changed: `tests/quality_gates/test_command_docs_gate.py` +3 (relative-output resolution kills L102 Div×11 + L103 parents; run_help nonzero-exit + signal-death kill L57 `check=` and L61 `!=` comparisons); `tests/test_markdown_preview_support.py` +3 (`_load_render_module` ImportError kills L13 `or`→`and`+L14; healthy mocked payload with non-interned status + non-ASCII note + 2-space indent kills L23 `ensure_ascii=False`/`indent=2`×2 + L24 `==`→`is`; unhealthy `status="unhealthy"` kills L24 `==`→`>=`). Plus `tests/quality_gates/test_goal_coordination_floors.py` +1 parametrized `_mask_fences` test (kills the trio's 28→4 `_mask_fences` survivor cluster across both modules). No source changed.
- Alternatives rejected: Reproducing the exact CI seeded fill sample — unnecessary (A1; proved kills via the scoped re-run). Running the render relative-output test via subprocess into the real repo — rejected (would write generated output into the repo); stubbed `render_cli_reference` + tmp repo-root instead. Killing ALL trio latent survivors — out of scope (filed #261; some equivalent).
- Targeted verification:
  - **Survivor files (the 22): scoped cosmic-ray re-run, 115→101 executable → 101 KILLED / 0 SURVIVED / 0 NO_TEST** (was 15 SURVIVED + 6 NO_TEST = 21 not-killed). `setup_artifact_policy_lib.py` was already 0. The score-path FAIL cause is fixed.
  - **Trio newly-covered-from-uncovered (gap) lines: 0 not-killed.** Trio scoped re-run (654→490 executable) — every mutant on the literal gap lines (check_goal_artifact 100-107 incl. the L103 Add cluster ×11 + L100 AddNot; floors 110/129 + closeout 202 had no executable mutants post-filter) is KILLED. The #251 dynamic (now-covered changed lines must die) is satisfied.
  - **Surgical trio hardening (user decision):** the trio's broader pre-existing latent survivors (94) clustered in `_mask_fences` (28). A single parametrized `_mask_fences` test (input includes a tab in BOTH the fence marker and the fenced body, distinguishing `==` from `<=`/`<`) killed 24/28 in a focused re-run (48 `_mask_fences` mutants → 44 killed, 4 left). This lifts the two fill-eligible files to **closeout 88.8%, floors 85.0%** (both comfortably above the `score_break: 80` gate, where they sat at 82.0%/80.4% before).
  - No leftover mutations: `git status` clean on all source after every exec (a `timeout`-killed exec had left one `repo_root >> args.output` mutation on render_cli_reference.py:102 mid-Slice-2 — caught and restored; all later execs ran to completion + defensive `git checkout`).
- Test duplication pressure: low — the in-process tests target branches no existing test reaches (relative-output, signal-death exit, mocked unhealthy payload, fence-with-tab). They sit beside the existing subprocess tests, which still cover the happy/absolute paths; no assertion is duplicated.
- Critique: The 4 remaining `_mask_fences` survivors are EQUIVALENT (`char == "\n"`→`char is "\n"`; CPython interns single-char strings) — named, not chased (goal stop condition). The surgical per-file rates (88.8%/85.0%) are derived deterministically: the new test only ADDS `_mask_fences` kills and cannot un-kill other mutants, so a full closeout+floors re-run was not re-paid; the focused `_mask_fences` re-run is the proof. The remaining ~70 trio survivors are pre-existing latent (filed #261).
- Off-goal findings: **#261** — coordination-cues trio has ~70 residual latent mutation survivors (closeout 23 / floors 32 / check_goal 15-excluded), incl. equivalent regex-flag `BitOr→Add` ×7; surfaced because the trio was never mutation-tested (chronic blocking). Out of #260 scope (anti-balloon + equivalent-mutant). check_goal_artifact (73.3% cov) is fill-EXCLUDED so its 15 don't threaten the gate.
- Lessons carried forward: line coverage ≠ mutation coverage (line 102 was "executed" yet its else-branch Div mutants survived); a tab (ord 9 < `\n` ord 10) is the key to killing `==`→`<=`/`<` char-comparison mutants; `flag | flag2` ≡ `flag + flag2` for disjoint bits (equivalent). cosmic-ray exec killed by `timeout` leaves the in-flight mutant applied → always `git checkout` source after.
- Metrics: survivor re-run 101/101 killed; trio re-run 490 exec / 94→70 not-killed after `_mask_fences` fix; closeout 88.8% / floors 85.0% (when available).

### Slice 4: Preventive teeth (changed-line mutation-coverage check)

- Objective: Add a bounded local script that reproduces classify_changed_line_scope_gap over a base..head range so uncovered changed lines are caught pre-merge
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification:
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 5: Prove + dispatch + close

- Objective: Confirm no regression, gather the two-proof story, re-check #219, close #260
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification:
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- **Failing run:** GH Actions run `26684100469`; base `9565b923d61e525a7f85bd2e5a0fd41430d88011`, head `454f7ddcadc8aac9048d1f849d631d1595dbdc42`.
  - **Sample seed (critique A1 — survivor sample is seed-deterministic):**
    `MUTATION_SAMPLE_SEED=26684100469:9565b923d61e525a7f85bd2e5a0fd41430d88011..454f7ddcadc8aac9048d1f849d631d1595dbdc42`.
    The **blocking-trio** repro is seed-independent (keys on changed files) → reproduces from base/head alone. The **survivor set** is sample-dependent → reproduce it with this CI seed, OR (cheaper, preferred) prove survivors killed directly via Slice 3's targeted scoped re-run rather than reproducing the CI fill sample. Slice 1 must state which path it took.
  - Current `main` is past the failing head (HEAD `599c941`, ahead of origin by 2: #258 commit-gate fix + retro), but `git diff 454f7dd..599c941` over the trio is empty, so the historical range still reproduces the blocking signal. Slice 1 re-derives on current `main` rather than blindly trusting the historical range.
- **Prior same-class goal (template + lessons):** [2026-05-30-issue-251](./2026-05-30-issue-251-251-mutation-test-regression-on-main.md) — faithful subprocess-capture repro, dispatch-has-no-base_sha (B1), check_coverage-is-not-the-predicate (B2), raw-format-mutant rule (B3); its retro deferred "a base/head changed-line-coverage helper" → realized here as Slice 4.
- **Gate config:** `.agents/quality-adapter.yaml` `mutation_testing` (`score_break: 80`; full = cosmic-ray + `npm run test:mutation:js`; summary = `check_mutation_suite_score.py`); workflow `.github/workflows/mutation-tests.yml` (schedule cron `17 */3 * * *`, `workflow_dispatch`, PR=dry-run).
- **Gate contract + recurrence note:** [mutation-testing.md](../../skills/public/quality/references/mutation-testing.md) (reachable-mutant denominator; changed-files-with-uncovered-lines is a separate blocking signal from score; §"Fixing a changed-line-coverage regression" from #251).
- **Related backlog:** #219 (same-class, distinct *score* failure over a different range — re-check at Slice 5, do not assume subsumed); #236 (`quality` CI-only-failure *triage* lesson — the verification-cost tension this goal navigates; it does **not** own local score-path mutation prevention — critique A5).
- **Pre-pickup state:** [recent lessons](../retro/recent-lessons.md), [quality latest](../quality/latest.md).
- Source: handoff entry #3 (#260: Mutation test regression on main) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `scripts/render_cli_reference.py`
- Cited path: `scripts/setup_artifact_policy_lib.py`
- Cited path: `scripts/agent-runtime/skill-test-telemetry.mjs`
- Cited path: `skills/public/achieve/scripts/check_goal_artifact.py`
- Cited path: `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
- Cited path: `skills/public/achieve/scripts/goal_artifact_coordination_floors.py`
- Cited path: `skills/public/achieve/scripts/goal_artifact_lib.py`
- Cited path: `skills/public/quality/references/mutation-testing.md`
- Cited path: `skills/support/markdown-preview/scripts/check_glow_backend.py`
- Cited path: `tests/quality_gates/test_command_docs_gate.py`
- Cited issue: #260

## Interview Decisions

- **Fix scope — chose Thorough (cover blocking trio + kill all 22 survivors)**
  over Minimal-to-green (cover the trio + just enough survivors to hold ≥80%).
  This is the 3rd recurrence; durable mutated-behavior coverage was chosen over
  the fastest green. The gap is small once `render_cli_reference.main()` is covered
  (that one function is 18 of 22 survivors).
  - `axis: none` — coverage-completeness choice, not a system axis.
- **Recurrence prevention — chose Add preventive teeth now** over Fix-only + file
  a separate issue. Realizes the #251 retro's deferred "base/head
  changed-line-coverage helper." Scoped tightly to the *blocking* (changed-line)
  class, which is the recurring one and cheap to detect locally; local score-path
  prevention is out of scope and **unowned** (file a new issue if ever pursued —
  not #236, which is CI-only-failure triage; critique A5).
  - `axis: prevention-layer` — local pre-merge vs CI-only. Chose to add a local
    layer; kept it a thin reuse of existing sampler/classifier, not a new runner.
- **Verification depth — chose Local-deterministic + CI `workflow_dispatch`** over
  local-only. Live CI dispatch is the only honest proof the actual score gate is
  green; the blocking path's CI confirmation remains the next scheduled cron (B1).
  - `axis: ci-run / push-range` — "changed files" is per-CI-run; the fix targets
    durable changed-line coverage so any future range over the scripts stays green.
- **Mutation threshold `score_break: 80` / runner (cosmic-ray + StrykerJS)** —
  `single-point` for this repo (declared in `.agents/quality-adapter.yaml`); not
  changed by this goal.

## Plan Critique Findings

Bounded fresh-eye subagent critique (general-purpose, `critique` discipline,
read-only in the shared parent worktree) run before saving. Five real blockers,
all folded:

- **A1 — survivor sample is seed-deterministic; repro plan lacked the seed.**
  `mutation_sampling_lib.deterministic_sample` orders fill candidates by
  `stable_hash(f"{seed}:{path}")` and `sample_mutation_files.py` reads
  `MUTATION_SAMPLE_SEED`; without the CI seed a local run selects a *different*
  fill sample and may not pick `render_cli_reference.py` at all. Folded: the CI
  seed is in Context Sources, and the repro is split — blocking-trio repro is
  seed-independent, the survivor set is proven via Slice 3's targeted scoped
  re-run (preferred) or the seeded sampler.
- **A2 — `_load_render_module` is in `check_glow_backend.py`, not render.**
  Verified: defined at `skills/support/markdown-preview/scripts/check_glow_backend.py:10`;
  no `scripts/` definition. Folded in Goal + Boundaries + Slice 3.
- **A3 — "18 survivors in render_cli_reference.main()" over-attributed.** The CI
  `main: 18` is aggregated by function name across all fill files;
  `render_cli_reference.main()` hosts only the line-102 `Div_*` cluster + mkdir/
  return-0. The two `ReplaceFalseWithTrue` are `check_glow_backend.main()`'s
  `ensure_ascii=False`. Folded: Slice 3 no longer sizes the render test as the
  whole fix.
- **A4 — Slice-4 reuse cited the wrong lib.** The wrapper's deps
  (`read_test_command`, `run_test_coverage`, `load_file_statement_lines`,
  `select_test_nodeids`) live in `mutation_sampling_lib.py`, not
  `mutation_line_coverage_lib.py`. Folded in Boundaries.
- **A5 — "#236 owns score-path prevention" mis-routed the deferral.** `gh issue
  view 236` confirms #236 is a `quality` CI-only-failure *triage* lesson, not a
  prevention home. Folded: local score-path prevention is named unowned (file a
  new issue if pursued); #236 kept only as the cost-tension reference.

Over-worry raised but **not** folded (consciously set aside):

- **Score stays <80% after new trio mutants enter the denominator.** Real but
  already named (Goal cause-1 dynamic); thorough cover-and-kill is the mitigation.
- **B1 contradicted?** No — verified intact: `mutation-tests.yml` computes
  `base_sha` only for `schedule`; `classify_changed_line_scope_gap` returns `[]`
  when `not base_sha`. The two-proof story carries B1/B2/B3 forward correctly.
- **Base/head drift on current `main`.** `git diff 454f7dd..599c941` over the trio
  is empty; changed-line counts verified exact (check_goal_artifact +8,
  closeout_evidence +28, coordination_floors +283 = the bulk). Slice-1 re-derivation
  guard handles it.
- **"never exercises main()" phrasing.** Loosely stated; tightened to "runs main()
  only on the absolute-path branch, so line-102's else never executes." The
  concrete relative-output-path fix is correct and load-bearing.
- **#219 disposition / StrykerJS fence / Slice-4 balloon.** "Re-check, close-or-leave
  with reason"; StrykerJS correctly fenced (passes 91.9%); Slice-4 defer-and-file
  brake adequate. All sound.

Reviewer provenance: read this artifact + the #251 goal (B1/B2/B3 + Final
Verification); `scripts/render_cli_reference.py` (all 109 lines);
`tests/quality_gates/test_command_docs_gate.py` + `support.py:23-33`;
`scripts/mutation_changed_files_lib.py`; `.github/workflows/mutation-tests.yml`;
`scripts/run_cosmic_ray_mutation.py`; `check_glow_backend.py`. Greps:
`mutation_sampling_lib.py` (deterministic_sample:26, read_test_command:32,
run_test_coverage:72, load_file_statement_lines:190, select_test_nodeids:367),
`sample_mutation_files.py` env vars (360-362), repo-wide `_load_render_module` /
`run_help`. Read-only git: `git rev-parse HEAD`, `git diff --stat 9565b923..454f7dd`
and `454f7dd..599c941` over the trio (empty), `gh issue view 219/236/260`. Did
**not** run the mutation suite, sampler, or any mutating git op.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
