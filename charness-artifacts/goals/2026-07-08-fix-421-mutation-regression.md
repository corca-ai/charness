# Achieve Goal: Resolve #421: clear the blocking changed-line-coverage signal on main by adding proof tests for scripts/boundary_probe_lib.py:80 and the check_boundary_escalation.py CLI main path, and triage the 9 survived mutants.

Status: complete
Created: 2026-07-08
Activation: `/goal @charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: COMPLETE (all six slices done 2026-07-08; see
  `## Final Verification` for proof and non-claims).
- Current slice: none — goal closed.
- Next action: operator lane only — push `main` and watch the next scheduled
  mutation run auto-close #421 (see `## Operator Decision Queue`).
- Verification cadence: cheap deterministic checks (pytest for touched tests,
  `check_changed_line_coverage.py` reproduction, run-quality gate) at every
  commit boundary; slice-boundary proof is each slice's Expected Evidence
  column; remote scheduled-run green is a bundle boundary owned by the
  operator push lane and is NOT claimed by this goal.
- Slice review packet: intent, changed files + owning surfaces, expected
  invariants, red/green proof commands with output, non-claims, out-of-scope
  lines, open questions — handed to a bounded fresh-eye subagent per
  `skills/shared/references/fresh-eye-subagent-review.md` (read-only inspection
  of prior versions, no index-mutating git ops).
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Make the nightly mutation gate on `main` honestly green again so the next
scheduled run auto-closes #421. Session-open investigation (2026-07-08) showed
the issue covers more than the one regression its body names:

- **Defect A — recurring scheduled failure. RESOLVED by Slice 1+2 (root cause
  found; fix pre-existing).** Only the first failure (run 28741213090, base
  `4f272b07..57af3d2b`) was the changed-line-coverage regression. The 4
  scheduled failures since 2026-07-06 were a time-armed red baseline test:
  DBD-2's Boundary Ownership floor (enforced from `RULE_DATE=2026-07-06`)
  detonated `test_changed_artifacts_passes_scaffold_roundtrip` (which
  truncated the critique stub), the red baseline aborts the sampler, no
  manifest is produced, and the summary misreports "StrykerJS report missing"
  (misreporting filed as #422). The fix already sits on unpushed local `main`
  (`38219d95`, bisect-proven). Full chain:
  [debug artifact](../debug/2026-07-08-issue-421-nightly-mutation-gate-red.md).
  Earlier hypotheses (base==head empty range; JS runner/npm breakage) were
  both falsified — kept here only as history, superseded by the debug
  artifact.
- **Defect B — real changed-line coverage debt (paydown, not the close
  trigger).** Commit `06187605` (cross-surface probe severity-upgrade) left
  `scripts/boundary_probe_lib.py:80` (the working-tree-diff fallback in
  `resolve_changed_paths`) and the whole
  `skills/public/impl/scripts/check_boundary_escalation.py` CLI main path
  (`parse_args`/`main`/`__main__`/ImportError branch, 16 proof-target lines)
  test-uncovered. Plan-critique correction: the next scheduled run after push
  uses base=`57af3d2b` (the failed run's head), so these targets sit in the
  base and are never re-judged — covering them is honest debt paydown but does
  NOT by itself make #421 auto-close. Cover them anyway; the debt is real.
- **Defect C — pre-push audit of the range the recovery run WILL judge.** The
  post-push scheduled run judges `57af3d2b..HEAD` (12+ local commits, 11
  unaudited pool files). Reproduce the changed-line classification over that
  range locally and fix any blocking-uncovered changed lines before closeout,
  or the "recovery" run goes red on a brand-new signal and #421 stays open.
- **Advisory tail.** Triage (not necessarily kill) the 9 survived Python
  mutants and 7 survived JS mutants from the failing run; the score PASSes, so
  this is judgment-bounded hardening, not a blocking signal.

Issue closeout is machine-owned: a scheduled green run auto-closes #421
(workflow "Close recovered mutation issue" step; dispatch-green may NOT close,
per #358). This goal therefore ends at local proof + commit; the push and the
resulting green run belong to the operator lane (handoff Next Session item 1).

**Source handoff entry #7: #421: Mutation test regression on main**

> <!-- corca-ai/charness-mutation-test-regression -->
> Mutation testing failed on `57af3d2ba88d9bcbe91b3e33f9c50de54d54ea71`.
>
> Workflow run: https://github.com/corca-ai/charness/actions/runs/28741213090
>
> # Mutation Testing Summary
>
> - Status: **FAIL**
> - Mutation score: **PASS** (91.3% reachable score vs 80% threshold)
> - Blocking signals: **FAIL** (changed-line coverage)
> - Total mutants: 160
> - Executable mutants: 104 (total minus skipped)
> - Executed: 104 (100.0% of executable total)
> - Killed: 95
> - Survived: 9
> - Scope gaps (uncovered sampled mutants): 0
> - No mutation possible: 0
> - Incompetent: 0
> - Skipped: 56
> - Blocking signal: changed lines were left test-uncovered before mutation (budget/capacity drops of covered changed files are advisory, not blocking).
>
> ## Survived Mutants
>
> Top definitions:
> - `main`: 5
> - `nested_cli_files`: 1
> - `module_release_only_files`: 1
> - `payload_for`: 1
> - `_slug`: 1
>
> Top operators:
> - `core/NumberReplacer`: 4
> - `core/ReplaceContinueWithBreak`: 2
> - `core/ZeroIterationForLoop`: 1
> - `core/ReplaceBinaryOperator_Mul_Div`: 1
> - `core/ReplaceOrWithAnd`: 1
>
> Sample locations:
> - `skills/public/quality/scripts/surface_marker_lib.py:21` `nested_cli_files` `core/ReplaceContinueWithBreak` - continue
> - `skills/public/quality/scripts/surface_marker_lib.py:33` `module_release_only_files` `core/ReplaceContinueWithBreak` - continue
> - `scripts/validate_outcome_assertions.py:65` `main` `core/NumberReplacer` - print(json.dumps({"checked": list(results), "problems": problems}, indent=2))
> - `scripts/validate_outcome_assertions.py:65` `main` `core/NumberReplacer` - print(json.dumps({"checked": list(results), "problems": problems}, indent=2))
> - `scripts/validate_outcome_assertions.py:66` `main` `core/NumberReplacer` - return 1 if problems else 0
> - `scripts/validate_outcome_assertions.py:66` `main` `core/NumberReplacer` - return 1 if problems else 0
> - `scripts/validate_outcome_assertions.py:74` `main` `core/ZeroIterationForLoop` - for err in errs:
> - `skills/public/critique/scripts/scaffold_critique_artifact.py:183` `payload_for` `core/ReplaceBinaryOperator_Mul_Div` - def payload_for(repo_root: Path, *, title: str | None) -> dict[str, object]:
> - `skills/public/critique/scripts/scaffold_critique_artifact.py:86` `_slug` `core/ReplaceOrWithAnd` - return slug or "critique"
>
>
> ## Changed Files Excluded Before Mutation
>
> - `scripts/boundary_probe_lib.py`
> - `skills/public/impl/scripts/check_boundary_escalation.py`
>
> ### Uncovered changed lines
>
> - `scripts/boundary_probe_lib.py`
> - `skills/public/impl/scripts/check_boundary_escalation.py`
>
> ### Selection budget or nodeid (advisory: capacity, not coverage)
>
> - `scripts/boundary_probe_lib.py`
>
> ### Changed-line proof targets
>
> - `scripts/boundary_probe_lib.py:80 return _surfaces_lib.collect_changed_paths(repo_root)`
> - `skills/public/impl/scripts/check_boundary_escalation.py:27 raise ImportError("skill_runtime_bootstrap.py not found")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:38 parser = argparse.ArgumentParser(description="impl cross-surface escalation probe (ownership override)")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:39 parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)`
> - `skills/public/impl/scripts/check_boundary_escalation.py:40 parser.add_argument("--changed-path", nargs="*", help="Explicit changed paths (bypasses git).")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:41 parser.add_argument("--changed-ref", help="Git ref/range for changed-path discovery (else working-tree diff).")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:42 parser.add_argument("--json", action="store_true", help="Emit the full payload as JSON.")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:43 return parser.parse_args()`
> - `skills/public/impl/scripts/check_boundary_escalation.py:61 args = parse_args()`
> - `skills/public/impl/scripts/check_boundary_escalation.py:62 payload = build_payload(args.repo_root.resolve(), args.changed_path, args.changed_ref)`
>
> Score denominator: `killed / (killed + survived)` (reachable mutants only;
> see `skills/public/quality/references/mutation-testing.md` §commands.summary).
> Native Cosmic Ray no-mutation-possible results and Charness filtered
> scope gaps are surfaced as separate blocking signals above and do not
> enter the score. Skipped mutants are explicitly filtered work items and
> also stay out of the score and completion denominators.
>
> ## StrykerJS Mutation Slice
>
> - Status: **PASS** (91.9% reachable score vs 80% threshold)
> - Reachable mutants: 86
> - Killed: 79
> - Survived: 7
> - No coverage: 0
> - Timeout: 0
>
> Survived JS mutants:
> - `scripts/agent-runtime/skill-test-telemetry.mjs:6 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:10 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:14 `MethodExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:19 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:27 `BlockStatement``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:39 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:39 `EqualityOperator``
>
>
> # Mutation Sample
>
> - Base SHA: `4f272b07be9128ddf3271eb38742085df9a2cae6`
> - Head SHA: `57af3d2ba88d9bcbe91b3e33f9c50de54d54ea71`
> - Seed: `28741213090:4f272b07be9128ddf3271eb38742085df9a2cae6..57af3d2ba88d9bcbe91b3e33f9c50de54d54ea71`
> - Mutation pool files: 541
> - Mutation pools: core-python 1/57 selected (272 pool), public-skill-python 3/110 selected (245 pool), support-skill-python 0/17 selected (24 pool)
> - Eligible files after coverage/mutation-line filters: 184
> - Covered eligible files: 184
> - File coverage floor: 0.85
> - Eligible files after mutation-line filter: 184
> - Executable mutant budget: 120
> - Per-file executable mutant budget: 80
> - Selected executable mutants: 104
> - Test nodeid budget: 40
> - Selected test nodeids: 33
> - Changed pool files: 6
> - Changed eligible files after coverage/mutation-line filters: 4
> - Changed files with uncovered changed lines (blocking): 2
> - Changed-line proof targets: 16
> - Changed files excluded by coverage/mutation-line filters (advisory union): 2
> - Changed files excluded by file coverage floor: 1
> - Changed files excluded by mutation-line coverage: 1
> - Changed files excluded by selection budgets: 1
> - Changed files excluded by per-file mutation budget (advisory): 2
> - Selected: 4/5
> - Test command: `python3 -m pytest -q tests/quality_gates/test_check_artifact_surface_preflight.py::test_changed_artifacts_passes_scaffold_roundtrip tests/quality_gates/test_check_artifact_surface_preflight.py::test_emit_stub_critique_carries_required_sections tests/quality_gates/test_check_artifact_surface_preflight.py::test_main_emit_stub_writes_stub tests/quality_gates/test_check_artifact_surface_preflight.py::test_module_main_guard_executes tests/quality_gates/test_critique_boundary_ownership_presence.py::test_boundary_scaffold_default_stub_fails_validation_post_cutoff tests/quality_gates/test_critique_fresh_eye_presence.py::test_critique_scaffold_default_stub_fails_validation_post_cutoff tests/quality_gates/test_seed_worktree_adapter.py::test_existing_file_refuses_without_force tests/quality_gates/test_seed_worktree_adapter.py::test_force_overwrites tests/quality_gates/test_seed_worktree_adapter.py::test_repo_root_dot_invocation_writes_file_and_exits_zero tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_does_not_double_count_nested_seed_dirs tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_emits_interpretation_self_declaration tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_ignores_generated_mutant_tree tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_reports_pytest_temp_footprint tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_splits_module_release_only_nested_cli_files tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_summary_omits_full_nested_cli_list tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_summary_yaml_is_compact_and_parseable tests/quality_gates/test_standing_test_economics.py::test_standing_test_economics_surfaces_runner_startup_shape tests/quality_gates/test_standing_test_economics.py::test_surface_marker_lib_skips_unreadable_files tests/test_critique_scaffold.py::test_critique_scaffold_reports_validator_and_template tests/test_critique_scaffold.py::test_scaffold_surfaced_enums_match_validator_frozensets tests/test_scaffold_inprocess_coverage.py::test_scaffold_main_emits_json_payload_in_process tests/test_scaffold_inprocess_coverage.py::test_scaffold_shim_not_found_raises_import_error tests/test_scaffold_inprocess_coverage.py::test_scaffold_validator_command_repo_local_fallback tests/test_validate_outcome_assertions.py::test_find_and_validate_all_globs_every_set tests/test_validate_outcome_assertions.py::test_main_json_mode_reports_problems tests/test_validate_outcome_assertions.py::test_main_no_sets_is_clean tests/test_validate_outcome_assertions.py::test_main_returns_one_and_reports_on_problem tests/test_validate_outcome_assertions.py::test_main_returns_zero_when_all_valid tests/test_validate_outcome_assertions.py::test_shipped_assertion_sets_all_conform tests/test_validate_outcome_assertions.py::test_validate_file_accepts_valid tests/test_validate_outcome_assertions.py::test_validate_file_rejects_malformed_regex tests/test_validate_outcome_assertions.py::test_validate_file_reports_malformed_json tests/test_validate_outcome_assertions.py::test_validate_file_reports_schema_problems`
>
> ## Changed files with uncovered changed lines (blocking)
>
> - `scripts/boundary_probe_lib.py`
> - `skills/public/impl/scripts/check_boundary_escalation.py`
>
> ## Changed-line proof targets
>
> - `scripts/boundary_probe_lib.py:80` `return _surfaces_lib.collect_changed_paths(repo_root)`
> - `skills/public/impl/scripts/check_boundary_escalation.py:27` `raise ImportError("skill_runtime_bootstrap.py not found")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:38` `parser = argparse.ArgumentParser(description="impl cross-surface escalation probe (ownership override)")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:39` `parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)`
> - `skills/public/impl/scripts/check_boundary_escalation.py:40` `parser.add_argument("--changed-path", nargs="*", help="Explicit changed paths (bypasses git).")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:41` `parser.add_argument("--changed-ref", help="Git ref/range for changed-path discovery (else working-tree diff).")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:42` `parser.add_argument("--json", action="store_true", help="Emit the full payload as JSON.")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:43` `return parser.parse_args()`
> - `skills/public/impl/scripts/check_boundary_escalation.py:61` `args = parse_args()`
> - `skills/public/impl/scripts/check_boundary_escalation.py:62` `payload = build_payload(args.repo_root.resolve(), args.changed_path, args.changed_ref)`
> - `skills/public/impl/scripts/check_boundary_escalation.py:63` `if args.json:`
> - `skills/public/impl/scripts/check_boundary_escalation.py:64` `print(json.dumps(payload, indent=2))`
> - `skills/public/impl/scripts/check_boundary_escalation.py:66` `print(payload["reason"])`
> - `skills/public/impl/scripts/check_boundary_escalation.py:67` `print(f"triggered: {str(payload['triggered']).lower()}")`
> - `skills/public/impl/scripts/check_boundary_escalation.py:68` `return 0`
> - `skills/public/impl/scripts/check_boundary_escalation.py:72` `raise SystemExit(main())`
>
> ## Changed files excluded by file coverage (advisory)
>
> - `skills/public/impl/scripts/check_boundary_escalation.py`
>
> ## Changed files excluded by mutation-line coverage
>
> - `scripts/critique_adapter_lib.py`
>
> ## Changed files excluded by per-file mutation budget (advisory, non-blocking)
>
> - `skills/public/handoff/scripts/plan_handoff_run.py`
> - `scripts/validate_critique_artifacts.py`
>
> ## Changed sample
>
> - `skills/public/critique/scripts/scaffold_critique_artifact.py`
>
> ## Fill sample
>
> - `scripts/validate_outcome_assertions.py`
> - `skills/public/quality/scripts/surface_marker_lib.py`
> - `skills/public/setup/scripts/seed_worktree_adapter.py`

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk — in
  particular, NO `git push` (operator lane, held 2026-07-08) and no test-debt
  rotation sweep.
- No manual close of #421: close is machine-owned by the scheduled workflow's
  auto-close step after a green run; a manual close would be a terminal-green
  substitute at an irreversible boundary.
- Do not chase a 100% mutant kill: survived mutants with a PASSing score are
  triaged (kill-or-accept with reasons), not exhaustively killed.
- Do not redesign the mutation gate or its sampling policy beyond the minimal
  fix for the idle-main false red.

## Boundaries

- In scope (Defect A): the JS mutation runner path (`npm run test:mutation:js`
  — package.json script, StrykerJS config, `scripts/agent-runtime/` runner
  surfaces), `scripts/sample_mutation_files.py`,
  `scripts/run_cosmic_ray_mutation.py`, `scripts/check_mutation_suite_score.py`,
  `.github/workflows/mutation-tests.yml` (only if root cause lands there),
  `skills/public/quality/references/mutation-testing.md` (contract prose if
  behavior is corrected), plus their tests.
- In scope (Defect B): tests covering `scripts/boundary_probe_lib.py` and
  `skills/public/impl/scripts/check_boundary_escalation.py` (source edits only
  if a test reveals a real defect); `tests/test_boundary_probe.py` or a new
  test module.
- In scope (advisory tail): killing tests or recorded accepts for survived
  mutants in `scripts/validate_outcome_assertions.py`,
  `skills/public/quality/scripts/surface_marker_lib.py`,
  `skills/public/critique/scripts/scaffold_critique_artifact.py`,
  `scripts/agent-runtime/skill-test-telemetry.mjs`.
- Every commit this goal lands must itself keep its own changed lines
  test-covered (the gate the goal is fixing will judge these commits next).
- Portable per implementation-discipline: no host-specific assumption; CI
  specifics stay in the workflow file and adapter
  (`.agents/quality-adapter.yaml` `mutation_testing:` block).
- Stop conditions: name on first discovery; do not guess. If Defect A's root
  cause turns out to live in the CI runner environment (not reproducible
  locally), record the concrete signal and stop that slice rather than landing
  a speculative fix.

## User Acceptance

- The recurring twice-daily #421 failure comments stop after the operator
  pushes: the first post-push scheduled run completes green and auto-closes
  #421 (user-visible on the issue page). This goal's own acceptance floor is
  the local proof of that outcome, not the remote event itself.
- Locally: (1) Defect A's root cause is named from the failing CI run logs
  with a falsifiable hypothesis, and the fix is proven red/green at the
  narrowest reproducible surface (local repro if the cause is reproducible;
  otherwise the concrete CI-environment signal is recorded and the fix is
  proven by the strongest available local proxy, stated as such); (2) the 16
  changed-line proof targets from the #421 report are covered by named tests
  that fail when the covered behavior is broken; (3) the post-push judgment
  range `57af3d2b..HEAD` is classified locally and carries no
  blocking-uncovered changed lines; (4) survived-mutant triage table with
  kill-or-accept per mutant.

## Agent Verification Plan

- Cheap (every commit): targeted `python3 -m pytest -q` for touched tests;
  repo run-quality gate before commit.
- Slice boundary (Defect A): evidence starts from the failing CI run logs
  (`gh run view 28909485596 --log` and siblings). Red/green at the narrowest
  reproducible surface: if reproducible locally (`npm run test:mutation:js` /
  the runner path), show fail-then-pass; if the cause is CI-environment-only,
  record the concrete log signal, land the fix the logs justify, and state the
  residual as a non-claim (remote green only after operator push).
- Slice boundary (Defect B + C): reproduce CI's changed-line classification —
  which CI derives from `scripts/sample_mutation_files.py` feeding
  `scripts/check_mutation_suite_score.py` (the
  `skills/public/quality/scripts/check_changed_line_coverage.py` helper is the
  local reproduction surface, per mutation-testing.md) — twice: with explicit
  base/head `4f272b07..57af3d2b` showing the two Defect-B files flip to
  covered, and over `57af3d2b..HEAD` showing zero blocking-uncovered changed
  lines in the range the recovery run will actually judge.
- Final: full local test suite + run-quality gate; goal-level fresh-eye
  critique; `check_goal_artifact.py` green.
- Non-claims (stated now, restated at closeout): no remote CI green is claimed
  by this goal — the scheduled run happens only after the operator push; local
  reproduction of the CI sampler path is a faithful proxy but not the runner
  environment itself.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `debug` root-cause of Defect A from the real CI run logs (`gh run view <failing-run-id> --log`); falsifiable hypothesis; local reproduction only if the logs support one (base==head sampler repro is already falsified — it exits 0) | Bug-class issue: root-cause before fix; it re-fires twice daily | debug artifact naming the log-grounded cause + the narrowest red reproduction the cause allows (or the recorded CI-environment signal) | pending |
| 2 | Fix Defect A minimally at the surface the root cause names (JS runner path / workflow step / environment pin) | Root cause known from Slice 1 | red/green at that surface, or strongest local proxy + explicit non-claim; regression test where the surface is testable; run-quality gate green | pending |
| 3 | Cover Defect B's 16 proof targets: `resolve_changed_paths` working-tree fallback + `check_boundary_escalation.py` CLI main/json/ImportError/`__main__` paths | Real debt from `06187605`, even though it sits in the next run's base and is not what auto-closes #421 | new tests fail on mutated behavior (spot-check) and pass on real code; classifier reproduction over `4f272b07..57af3d2b` flips the two files to covered | pending |
| 4 | Defect C pre-push audit: classify changed lines over `57af3d2b..HEAD` (the range the recovery run judges) and fix any blocking-uncovered lines | The auto-close depends on THIS range going green, not on Defect B | local classification output: zero blocking-uncovered changed lines over `57af3d2b..HEAD` (including this goal's own commits) | pending |
| 5 | Triage 9 Python + 7 JS survived mutants: kill cheap ones, record reasoned accepts for the rest | Advisory tail of the same report; bounded by judgment, not completionism | triage table in Slice Log (mutant → kill-test or accept-reason); any new tests green | pending |
| 6 | Closeout: goal-level fresh-eye critique, `describe_goal_closeout_shape.py` preflight, retro, commit(s) with `#421` reference (no `Close #421` — close is machine-owned), handoff refresh | Task-completing repo work: critique/closeout/commit are part of the work | critique artifact, goal `Status: complete`, clean `check_goal_artifact.py`, committed tree | pending |

Per-slice proof cost: slices 1–2 medium (subprocess reproductions of the
sampler/runner path); slice 3 cheap (unit tests + classifier run); slice 4
cheap-to-medium. Test-duplication pressure: slices 3–4 add test LOC against
existing modules `tests/test_boundary_probe.py` / `tests/test_validate_outcome_assertions.py`
— extend those modules instead of new near-duplicate files; sample duplicate
pressure via `append_slice_log.py --test-pressure` when tests are added
(ratio is advisory-only by standing decision; never shave coverage for it).

Discuss before activation: CONFIRMED by operator 2026-07-08 (AskUserQuestion:
widened A+B+C scope approved for activation; push stays held).
(1) Issue-close path — #421 will NOT be closed by
this goal; the scheduled workflow auto-closes it after the first post-push
green run, and the push itself stays in the held operator lane. Confirmed as
the designed contract (workflow auto-close step + #358 rationale) — resolved.
(2) Scope — the goal reaches into quality-gate infrastructure (the JS mutation
runner path and, only if the root cause lands there, the sampler/workflow),
not just tests; minimal-fix boundary recorded in Non-Goals — resolved. (3) No
live/prod or remote proof is run by this goal; remote green is an explicit
non-claim — resolved. Remaining operator decision (push timing) is queued
below, not a blocker.

## Operator Decision Queue

- Decision: push `main` (will then carry this goal's commits) and observe the
  first post-push scheduled mutation run; expected outcome: green run
  auto-closes #421.
- Owner: operator (bae.hwidong)
- Why deferred: push is an operator-approved lane held 2026-07-08; local proof
  does not require it.
- Unblock action: `git push` + watch the next `17 */12 * * *` scheduled run.
- Revisit trigger: goal reaches `complete` locally, or the operator releases
  the hold earlier.

(One queued decision above; nothing else surfaced during the run that needs
operator action.)

## Slice Log

### Slice 1: Slice 1+2: Defect A root-cause (debug) — fix already landed locally

- Objective: Name the log-grounded root cause of the recurring nightly mutation-gate failure and land the minimal fix.
- Why this approach: Bug-class issue: CI-log evidence first (plan critique falsified the base==head hypothesis). Job-step conclusions showed 'Select mutation sample' failing, not the JS runner; the step log named one red baseline test.
- Commits: none new — fix is pre-existing local commit 38219d95 (bisect-proven: parent red with the exact CI assertion, commit green)
- What changed: charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md (root-cause artifact). Cause chain: DBD-2 (8799343d) added the Boundary Ownership floor with BOUNDARY_OWNERSHIP_RULE_DATE=2026-07-06; the roundtrip test truncated the critique stub, dropping that section; grandfathering masked it on 07-05, enforcement armed it from 07-06; the red baseline aborts the sampler (exit 1, no manifest), commands.full never runs, and the summary misreports 'StrykerJS report missing'. Slice 2 (fix) is therefore satisfied by 38219d95; no new gate code within the minimal-fix boundary.
- Alternatives rejected: Fixing at the JS runner/StrykerJS surface (the reported symptom) — rejected: step conclusions prove the JS slice never ran. Patching the sampler to tolerate red baselines — rejected: a red baseline SHOULD block; the defect was the red test itself plus the misleading summary (filed separately).
- Targeted verification: Red/green bisect in a throwaway worktree at 57af3d2b (FAIL, exact CI assertion), 38219d95^ (FAIL), 38219d95 (PASS); local main PASS (0.44s). CI evidence: run 28909485596 step conclusions + sampler step log.
- Test duplication pressure:
- Critique:
- Off-goal findings: #422 filed: mutation gate misreports a baseline-pytest abort as 'StrykerJS JSON report missing' (cost ~3 days of misdirected red).
- Lessons carried forward: A time-armed (RULE_DATE-gated) red test passes on landing day and detonates the next — pre-push audits should run gates as-of tomorrow's enforcement dates where cheap. Downstream symptom names (missing report) are not causes; check step conclusions before reading failure prose.
- Metrics:

### Slice 2: Slice 3: Defect B proof-target coverage (delegated to lower-power subagent)

- Objective: Cover the 16 changed-line proof targets from the #421 report: resolve_changed_paths branches (boundary_probe_lib.py:80 fallback) and the full check_boundary_escalation.py CLI path.
- Why this approach: Real debt from 06187605; implemented in a sonnet subagent per the standing coding-delegation request, with the parent holding design and verification.
- Commits: uncommitted (batched for the goal closeout commit per mutate->sync->verify->publish)
- What changed: tests/test_boundary_probe.py (+3 tests: explicit-path wins incl. empty list, changed_ref branch, working-tree fallback — all monkeypatched at _surfaces_lib, asserting exact returned lists); tests/quality_gates/test_critique_boundary_ownership_presence.py (+6 tests: ImportError shim branch, parse_args flags/defaults, main --json exact payload, main plain output exact lines, __main__ guard via runpy with deterministic non-matching --changed-path). No production changes; no defect found.
- Alternatives rejected: New dedicated test module — rejected (repo extend-don't-duplicate convention; both files already load the targets). Real-git fixtures for the fallback — rejected in favor of the file's existing monkeypatch style.
- Targeted verification: 33 passed across both files; each of the 9 new nodeids green individually; coverage report shows both target files 100% (37/37, 35/35 statements) incl. lines 80 and 27/38-43/61-68/72; ruff clean; check_python_lengths validated 953 files with neither touched file in the warn band. Formal classifier reproduction (4f272b07..57af3d2b flip + 57af3d2b..HEAD audit) deferred to the locked closeout producer run per implementation-discipline (critique before producer).
- Test duplication pressure: check_dup_ratchet --json: ok=true, status=clean after the additions.
- Critique:
- Off-goal findings:
- Lessons carried forward: The proof-target list from the mutation report mapped 1:1 to uncovered branches; monkeypatching the module seam (_surfaces_lib) kept the tests deterministic without git fixtures.
- Metrics:

### Slice 3: Slice 4: Defect C pre-push audit (recovery-run range clean)

- Objective: Classify changed lines over 57af3d2b..HEAD — the range the first post-push scheduled run will judge.
- Why this approach: Plan-critique blocker: paying down Defect B alone could not make #421 auto-close; the recovery run judges this range.
- Commits: none (read-only audit)
- What changed: reports/mutation/test-coverage.json + freshness marker regenerated by the consumer's own producer path (full standing pytest with coverage, ~10 min).
- Alternatives rejected: Deferring the audit entirely to the remote run — rejected: a red recovery run would keep #421 open on a brand-new signal after the operator spent the push.
- Targeted verification: scripts/check_changed_line_mutation_coverage.py with MUTATION_BASE_SHA=57af3d2b: ok=true, 11 changed pool files evaluated, zero blocking-uncovered changed lines. Same consumer with the original failing range 4f272b07..57af3d2b --reuse-coverage: ok=true, blocking=[], changed_pool_files include scripts/boundary_probe_lib.py and skills/public/impl/scripts/check_boundary_escalation.py — the exact two files blocking in run 28741213090 now judge as covered (Defect B flip evidence).
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward: The pre-push consumer runs its own producer when coverage is stale; budget ~10 minutes and do not run it concurrently with test-file edits.
- Metrics:

### Slice 4: Slice 5: survived-mutant triage (delegated to lower-power subagent)

- Objective: Kill-or-accept each of the 9 Python and 7 JS survived mutants from the #421 report.
- Why this approach: Advisory tail of the same report; bounded by judgment per Non-Goals (no 100%-kill chase).
- Commits: uncommitted (batched for the goal closeout commit)
- What changed: tests/quality_gates/test_standing_test_economics.py (unreadable-then-matching ordering kills both ReplaceContinueWithBreak survivors); tests/test_validate_outcome_assertions.py (exact rc==0 clean-path json assertion + stderr detail-line assertion); tests/test_critique_scaffold.py (punctuation-only title -> -critique.md slug); tests/agent-runtime/native.test.mjs (function-with-token-props does not leak into telemetry). Triage: Python 7 KILLED / 2 ACCEPTED (indent=2 cosmetic x2; line-183 mutant anchors to a keyword-only-marker def line with no arithmetic). JS 1 KILLED / 6 ACCEPTED as empirically-proven equivalent mutants (differential fuzzer ~22k cases through the only export + scoped Stryker reruns: killed 79->80, survived 7->6).
- Alternatives rejected: Killing all JS survivors — rejected: six are mathematically equivalent through the exported API (Number.isFinite type-strictness; null-coercion in reduce; null-vs-undefined collapsed by the only consumer; dead empty-compact branch).
- Targeted verification: pytest 28 passed across the three touched Python test files; npm run test:agent-runtime 59 passed (+1); ruff clean; check_python_lengths 953 files ok; kill assertions spot-checked by flipping expected values (fail) then restoring (pass); scoped Stryker rerun confirms the JS kill.
- Test duplication pressure: check_dup_ratchet --json: ok=true, status=clean (sampled after Slice 3; Slice 5 adds assertions to existing tests, minimal new LOC).
- Critique:
- Off-goal findings:
- Lessons carried forward: Equivalent mutants are provable, not just arguable: a scoped mutation rerun plus a differential fuzzer through the public API turns accept-reasons into evidence.
- Metrics:

### Slice 5: Slice 6: closeout (critique folds, rung-1b corrections, retro, handoff)

- Objective: Prove and close the goal: bundle fresh-eye critique, locked gate aggregate, retro + host-log probe + rung-1b disposition review, handoff refresh, complete flip.
- Why this approach: Task-completing repo work: critique/closeout/commit are part of the work, not follow-up.
- Commits: single closeout commit (this tree) referencing #421 without Close keywords
- What changed: critique artifact (bundle review, 2 folds applied); disposition-review artifact (3 binding corrections folded: disposition-1 overclaim, unbound structural-follow-up clause, missing handoff Discuss entry); retro + recent-lessons refresh; host-log probe JSON; docs/handoff.md closeout rewrite (single end-only write; RULE_DATE practice Discuss entry added); goal closeout sections + Coordination Cues.
- Alternatives rejected: Manual Close #421 on the commit — rejected: close is machine-owned by the scheduled workflow (second observer). Hand-editing generated recent-lessons.md to match disposition prose — rejected: corrected the prose to reality instead.
- Targeted verification: validate_critique_artifacts (both new artifacts) green; validate_retro_artifact green; validate_debug_artifact green; validate_handoff_artifact + doc preflight + pointer freshness green; run_slice_closeout --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage exit 0 (rerun after final artifact edits recorded in Final Verification); check_goal_artifact green at complete flip.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward: Rung-1b caught two real binding overclaims a same-agent pass would have shipped; the disposition floor plus a fresh eye is doing exactly its job.
- Metrics:

## Context Sources

- Source: live open issue #421 (Mutation test regression on main), surfaced by
  handoff chunked routing (`--with-issues`); issue body = first failing run
  28741213090 (base `4f272b07..57af3d2b`); comments 2–6 = the idle-main
  "StrykerJS report missing" failures (runs 28761407963 → 28909485596),
  read 2026-07-08 via `gh issue view 421`.
- Source: `.github/workflows/mutation-tests.yml` — scheduled base-SHA
  selection (previous completed run's head), auto-close contract (#358), and
  the idle-main sampling-rotation NOTE.
- Source: `.agents/quality-adapter.yaml` `mutation_testing:` block —
  `commands.sample/full/summary` used for local reproduction.
- Source: `skills/public/quality/references/mutation-testing.md` — local
  changed-line classifier reproduction (`check_changed_line_coverage.py`,
  explicit `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA`).
- Defect-B origin commit: `06187605` (cross-surface probe severity-upgrade +
  impl escalation hook, #408 #414 #416).
- Cited path: `scripts/agent-runtime/skill-test-telemetry.mjs`
- Cited path: `scripts/boundary_probe_lib.py`
- Cited path: `scripts/critique_adapter_lib.py`
- Cited path: `scripts/validate_critique_artifacts.py`
- Cited path: `scripts/validate_outcome_assertions.py`
- Cited path: `skills/public/critique/scripts/scaffold_critique_artifact.py`
- Cited path: `skills/public/handoff/scripts/plan_handoff_run.py`
- Cited path: `skills/public/impl/scripts/check_boundary_escalation.py`
- Cited path: `skills/public/quality/references/mutation-testing.md`
- Cited path: `skills/public/quality/scripts/surface_marker_lib.py`
- Cited path: `skills/public/setup/scripts/seed_worktree_adapter.py`
- Cited path: `tests/quality_gates/test_check_artifact_surface_preflight.py`
- Cited path: `tests/quality_gates/test_critique_boundary_ownership_presence.py`
- Cited path: `tests/quality_gates/test_critique_fresh_eye_presence.py`
- Cited path: `tests/quality_gates/test_seed_worktree_adapter.py`
- Cited path: `tests/quality_gates/test_standing_test_economics.py`
- Cited path: `tests/test_critique_scaffold.py`
- Cited path: `tests/test_scaffold_inprocess_coverage.py`
- Cited path: `tests/test_validate_outcome_assertions.py`
- Cited issue: #421

## Interview Decisions

- Mode: implementation-continuation assumed (family considered: artifact-only
  draft vs implementation-continuation). The user picked this chunk from the
  chunked-routing ranking after asking to "do the next improvement", which
  names execution intent; artifact-only rejected because the chunk was selected
  to be worked, not merely reviewed. Activation still waits for the explicit
  `/goal` command per lifecycle contract.
- Goal reframing: the drafted chunk objective named only the changed-line
  regression; session-open investigation found the recurring failure is a
  different defect (the scheduled JS mutation slice stopped producing its
  report), and plan critique added a third obligation (pre-push audit of the
  range the recovery run judges). Decision: widen the goal to all three
  because a coverage-only fix would leave #421 re-firing twice daily — the
  narrower alternative was rejected as a wrong answer that escapes.
  `axis: n/a` — this is evidence-driven scoping, not a system-axis value.
- Issue close path: machine auto-close on scheduled green (rejected: manual
  `Close #421` on a commit — the workflow owns recovery proof, and #358
  explicitly forbids dispatch-green closes; a manual close would bypass the
  designed second observer). `single-point: repo-owned workflow contract`.
- CI host value: GitHub Actions + `gh` backend appear throughout.
  `axis: host/tracker` — the issue skill routes through an adapter-resolved
  backend; this goal touches the repo-owned workflow file, which is inherently
  GitHub-specific and stays in `.github/`, per the portability boundary.
- Test placement: extend existing modules (`tests/test_boundary_probe.py`,
  `tests/test_validate_outcome_assertions.py`) rather than new files
  (rejected: parallel new test modules — duplicate-pressure and the standing
  test-debt rotation both push against near-duplicate files).
  `single-point: repo test-suite convention`.

## Plan Critique Findings

Reviewer provenance: bounded fresh-eye subagent (separate context,
read-only in the shared worktree; empirically tested claims, writes to /tmp
only), 2026-07-08, reviewing the shaped draft before activation.

Blockers folded:

- **Wrong root-cause framing (folded into Goal, Slice 1, Verification Plan).**
  The draft asserted Defect A = "base==head idle-main false red". The reviewer
  ran the sampler with `MUTATION_BASE_SHA==MUTATION_HEAD_SHA==57af3d2b`: it
  exits 0 with a full 10/10 manifest, so the presumed local red reproduction is
  actually green. The failure originates in the JS runner/npm path; Slice 1 now
  starts from real CI run logs instead of a presumed repro.
- **Recovery run judges a different range (folded as Defect C / Slice 4).**
  The next scheduled run after push uses base=`57af3d2b` (previous completed —
  including failed — run's head), so the 16 Defect-B proof targets sit in the
  base and are never re-judged; the pushed 12+ commits (11 unaudited pool
  files) are what gets judged. Without a pre-push audit of `57af3d2b..HEAD`,
  the goal could pay down old debt while the recovery run goes red on a new
  signal — a false "fixed" claim. Defect B recast as debt paydown, not the
  close trigger.
- **Verification-plan factual errors (folded into Verification Plan).**
  `check_changed_line_coverage.py` lives at `skills/public/quality/scripts/`,
  not `scripts/`, and it is a local reproduction helper — CI's changed-line
  signal actually comes from `sample_mutation_files.py` via
  `check_mutation_suite_score.py`.

Over-worry raised but not folded:

- The `com/corca-ai/charness/actions/runs/` cited-path artifact in Context
  Sources was flagged as possibly confusing but is a harmless parser tail of
  the run URL; superseded by the rewritten Context Sources entry.
- "Fixing the sampler might break PR dry-run / dispatch modes" — no sampler
  change is currently justified (the sampler handles base==head correctly);
  the concern re-attaches only if Slice 1's root cause lands there.

Verified sound by the reviewer: schedule-only auto-close contract (#358),
all SHAs and file paths cited in the artifact, the sampler CLI contract, and
the survived-mutant counts (9 Python + 7 JS).

## Off-Goal Findings

- #422 filed (mutation gate misreports a baseline-pytest abort as "StrykerJS
  JSON report missing") — discovered during Slice 1 root-cause; kept out of
  this goal per the minimal-fix boundary.

## Coordination Cues

- Routing: find-skills recommended `achieve` as the goal-lifecycle operator
  for this run (`list_capabilities.py --recommend-for-task` over the
  debug/impl/quality/issue phase mix returned achieve first); phase work then
  routed to `debug` (root-cause artifact), `issue` (#422 filing), `critique`
  (bundle review), and `retro` (session retro).
- Gather: n/a — no external URL or published source became working context;
  all evidence was repo-local or `gh`-fetched issue/run state for #421.
- Release: n/a — no plugin version bump or install-manifest change in this
  goal (test files and checked-in artifacts only).
- Issue closeout: n/a — #421's close is machine-owned by design: the
  scheduled workflow's "Close recovered mutation issue" step auto-closes it
  after the first post-push green run (#358 forbids dispatch-green closes);
  this goal stages the close by making that run green (fix `38219d95` +
  clean `57af3d2b..HEAD` audit) while the push stays in the held operator
  lane. A manual `Close #421` would bypass the designed second observer.

## Final Verification

- Defect A (recurring nightly red): root cause bisect-proven (time-armed
  Boundary Ownership floor detonating a truncating roundtrip test; sampler
  baseline aborts; summary misreports). Fix pre-existing at `38219d95` on
  local `main`; worktree red/green evidence in the debug artifact. No new
  gate code was needed (minimal-fix boundary held).
- Defect B (16 proof targets): 9 new tests; both files independently measured
  at 100% statement coverage (37/37, 35/35); changed-line consumer over the
  original failing range `4f272b07..57af3d2b` → `blocking: []` with both
  files present in `changed_pool_files`.
- Defect C (recovery-run range): consumer over `57af3d2b..HEAD` → `ok: true`,
  11 changed pool files, zero blocking-uncovered changed lines.
- Mutant triage: Python 7 killed / 2 accepted (cosmetic indent; def-line
  anchor with no arithmetic); JS 1 killed / 6 accepted as empirically-proven
  equivalents (scoped Stryker rerun 79→80 killed, 7→6 survived; ~22k-case
  differential fuzzer through the only export).
- Bundle fresh-eye critique: 0 act-before-ship; 2 folds applied (foreign-owned
  stderr string decoupled; live-adapter coupling documented) —
  [critique artifact](../critique/2026-07-08-421-test-hardening-bundle-slices-3-5.md).
- Final gate aggregate: `run_slice_closeout.py --verification-lock
  --refresh-broad-pytest-proof --produce-mutation-coverage` exit 0 — all
  sync/verify commands PASS (doc links, markdown, secrets, JS suite, JS
  mutation dry-run, critique validators, seam-risk index, ruff, lengths,
  attention-state, boundary ratchet, standing pytest); broad-pytest proof and
  mutation-coverage fingerprint stamped; rerun after these final artifact
  edits recorded below before commit.
- Non-claims: no remote CI green is claimed — the recovery run happens only
  after the operator push; local reproduction of the CI classifier is a
  faithful proxy, not the runner environment; #421 remains OPEN until the
  post-push scheduled run auto-closes it.

Retro: charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md
Host log probe: charness-artifacts/goals/2026-07-08-fix-421-mutation-regression-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-07-08-fix-421-mutation-regression-disposition-review.md

## User Verification Instructions

1. `git log --oneline -3` — the closeout commit references #421 (no `Close`
   keyword; the close is machine-owned).
2. After you push `main` (held operator lane): watch the next scheduled
   mutation run (`17 */12 * * *`, `.github/workflows/mutation-tests.yml`). It
   judges `57af3d2b..<new head>`; expected outcome: a green run that
   auto-closes #421.
3. Local spot-checks: `python3 -m pytest -q tests/test_boundary_probe.py
   tests/quality_gates/test_critique_boundary_ownership_presence.py` (new
   proof-target tests), and the recovery-range audit:
   `MUTATION_BASE_SHA=57af3d2ba88d9bcbe91b3e33f9c50de54d54ea71 python3
   scripts/check_changed_line_mutation_coverage.py --repo-root .
   --reuse-coverage`.
4. If the post-push run is red for a NEW reason, remember #422: read the
   run's step conclusions first, not the posted summary body.

## Auto-Retro

Retro dispositions: applied: recent-lessons refresh (`refresh_recent_lessons.py`) — the refresher's selection carried the consumer-runs-its-own-producer (~10 min) budgeting lesson and the wrong-first-hypothesis trap into `charness-artifacts/retro/recent-lessons.md`, committed with this closeout (rung-1b correction: the inherited-red-test↔open-CI-regression cross-check lesson was NOT selected by the refresher; its carriers are the debug artifact's Detection Gap entry and the handoff refresh Discuss entry written at this closeout); issue #422 (novel: first recorded instance of the gate misreporting a baseline-pytest abort as a missing StrykerJS report) — the gate must name the failing nodeids instead of the downstream symptom; applied: fresh-eye critique folds committed in this bundle (decoupled foreign-owned stderr assertion in `tests/test_validate_outcome_assertions.py`; dormant live-adapter coupling documented in `tests/quality_gates/test_critique_boundary_ownership_presence.py`).

Structural follow-up: none — the time-armed RULE_DATE floor detonation is a
first recorded occurrence; the practice ("run the suite as-of tomorrow's
enforcement date on a floor's landing day") is carried in the debug artifact's
Prevention section and the handoff refresh Discuss entry (rung-1b corrected:
it is NOT in recent-lessons), and floor-addition restraint says a blocking
gate waits for a recorded recurrence, not first sight.
