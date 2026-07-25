# Achieve Goal: Run ranked chunks 1-3 in sequence: (1) close #453 by covering the uncovered changed lines in quality_policy_defaults.py and runtime_budget_lib.py and killing the probe_host_logs.py survived mutants, plus act on the aarch64/unprofiled budget SLACK advisories; (2) close the named residuals - issue_close_comment_floor.py omitted checks, specdown.json hardcoded outFile churn, untested plugin-copy fresh-install render path; (3) sweep for other built-with-intent-but-unused modes and options and delete or justify each on usage evidence.

Status: complete
Created: 2026-07-25
Activation: `/goal @charness-artifacts/goals/2026-07-25-ranked-chunks-1-3.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: real draft awaiting activation — shaped and plan-critiqued
  2026-07-25, consequential discussion resolved with the operator, not stale.
- Current disposition: reopened for operator sign-off, then complete again.
  Slices 1-6 closed the goal as shaped; slice 7 acted on the sweep sign-off the
  operator gave afterwards, and slice 8 starts the `--granularity` extension they
  scheduled in place of deleting it.
- Next action: none. Two operator decisions remain queued (patch release,
  #453 close); the sweep-deletion decision is discharged and its extension
  (paragraph granularity) is implemented end to end.
- Standing hazard (slice 2): never restore a mutation-test target with
  `git checkout -- <path>` while the slice is uncommitted; it reverts to HEAD and
  silently discards the work being proven. Use a pristine `cp` copy and assert a
  green baseline before each mutation.
- Standing hazard (slice 3): run `reviewer_boundary_fingerprint.py verify`
  immediately when a reviewer returns, before applying any of its fixes —
  otherwise the drift set is the parent's own edits and the proof is inconclusive.
- Verification cadence: cheap deterministic checks at each commit boundary
  (`ruff`, targeted `pytest`, plugin-mirror sync, then the owning surface's
  validators); slice-boundary proof is `check_changed_line_mutation_coverage.py`
  for slice 1, a targeted mutant run for slice 2, and `run-quality --read-only`
  for slices 3-5; the sweep slice (6) closes on an evidence artifact, not a gate.
- Slice review packet: intent, changed files with owning/generated surfaces,
  expected invariants, tests and proof commands run, explicit non-claims,
  out-of-scope lines, and open questions — handed to a `bounded-reviewer`
  subagent per the repo fresh-eye contract.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Run ranked chunks 1-3 in sequence: (1) close #453 by covering the uncovered changed lines in quality_policy_defaults.py and runtime_budget_lib.py and killing the probe_host_logs.py survived mutants, plus act on the aarch64/unprofiled budget SLACK advisories; (2) close the named residuals - issue_close_comment_floor.py omitted checks, specdown.json hardcoded outFile churn, untested plugin-copy fresh-install render path; (3) sweep for other built-with-intent-but-unused modes and options and delete or justify each on usage evidence.

**Source handoff entry #5: #453: Mutation test regression on main**

> <!-- corca-ai/charness-mutation-test-regression -->
> Mutation testing failed on `79d23b86b9d44d752302e1540e727b16ce090f78`.
>
> Workflow run: https://github.com/corca-ai/charness/actions/runs/30137393094
>
> # Mutation Testing Summary
>
> - Status: **FAIL**
> - Mutation score: **PASS** (94.2% reachable score vs 80% threshold)
> - Blocking signals: **FAIL** (changed-line coverage)
> - Total mutants: 152
> - Executable mutants: 120 (total minus skipped)
> - Executed: 120 (100.0% of executable total)
> - Killed: 113
> - Survived: 7
> - Scope gaps (uncovered sampled mutants): 0
> - No mutation possible: 0
> - Incompetent: 0
> - Skipped: 32
> - Blocking signal: changed lines were left test-uncovered before mutation (budget/capacity drops of covered changed files are advisory, not blocking).
>
> ## Survived Mutants
>
> Top definitions:
> - `main`: 7
>
> Top operators:
> - `core/NumberReplacer`: 2
> - `core/ReplaceComparisonOperator_Eq_Gt`: 1
> - `core/ReplaceComparisonOperator_Eq_GtE`: 1
> - `core/ReplaceComparisonOperator_Eq_Is`: 1
> - `core/ReplaceTrueWithFalse`: 1
> - `core/ReplaceFalseWithTrue`: 1
>
> Sample locations:
> - `skills/public/retro/scripts/probe_host_logs.py:60` `main` `core/ReplaceComparisonOperator_Eq_Gt` - if args.format == "markdown":
> - `skills/public/retro/scripts/probe_host_logs.py:60` `main` `core/ReplaceComparisonOperator_Eq_GtE` - if args.format == "markdown":
> - `skills/public/retro/scripts/probe_host_logs.py:60` `main` `core/ReplaceComparisonOperator_Eq_Is` - if args.format == "markdown":
> - `skills/public/retro/scripts/probe_host_logs.py:63` `main` `core/ReplaceTrueWithFalse` - print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
> - `skills/public/retro/scripts/probe_host_logs.py:63` `main` `core/ReplaceFalseWithTrue` - print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
> - `skills/public/retro/scripts/probe_host_logs.py:63` `main` `core/NumberReplacer` - print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
> - `skills/public/retro/scripts/probe_host_logs.py:63` `main` `core/NumberReplacer` - print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
>
>
> ## Changed Files Excluded Before Mutation
>
> - `scripts/quality_policy_defaults.py`
> - `skills/public/quality/scripts/runtime_budget_lib.py`
>
> ### Uncovered changed lines
>
> - `scripts/quality_policy_defaults.py`
> - `skills/public/quality/scripts/runtime_budget_lib.py`
>
> ### Selection budget or nodeid (advisory: capacity, not coverage)
>
> - `skills/public/issue/scripts/issue_close_comment_floor.py`
>
> ### Changed-line proof targets
>
> - `scripts/quality_policy_defaults.py:209 return f"mutation_testing.{section}.{key} must be a string"`
> - `scripts/quality_policy_defaults.py:220 return problem`
> - `scripts/quality_policy_defaults.py:253 errors.append(f"mutation_testing.{section} must be a mapping")`
> - `skills/public/quality/scripts/runtime_budget_lib.py:305 return (`
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
> - Status: **PASS** (93.0% reachable score vs 80% threshold)
> - Reachable mutants: 86
> - Killed: 80
> - Survived: 6
> - No coverage: 0
> - Timeout: 0
>
> Survived JS mutants:
> - `scripts/agent-runtime/skill-test-telemetry.mjs:6 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:14 `MethodExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:19 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:27 `BlockStatement``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:39 `ConditionalExpression``
> - `scripts/agent-runtime/skill-test-telemetry.mjs:39 `EqualityOperator``
>
>
> # Mutation Sample
>
> - Base SHA: `835181c38aef7c629f7745aeb4f0ef633d80c9bb`
> - Head SHA: `79d23b86b9d44d752302e1540e727b16ce090f78`
> - Seed: `30137393094:835181c38aef7c629f7745aeb4f0ef633d80c9bb..79d23b86b9d44d752302e1540e727b16ce090f78`
> - Mutation pool files: 584
> - Mutation pools: core-python 1/76 selected (304 pool), public-skill-python 4/126 selected (256 pool), support-skill-python 0/17 selected (24 pool)
> - Eligible files after coverage/mutation-line filters: 219
> - Covered eligible files: 219
> - File coverage floor: 0.85
> - Eligible files after mutation-line filter: 219
> - Executable mutant budget: 120
> - Per-file executable mutant budget: 80
> - Selected executable mutants: 120
> - Test nodeid budget: 40
> - Selected test nodeids: 22
> - Changed pool files: 8
> - Changed eligible files after coverage/mutation-line filters: 2
> - Changed files with uncovered changed lines (blocking): 2
> - Changed-line proof targets: 4
> - Changed files excluded by coverage/mutation-line filters (advisory union): 6
> - Changed files excluded by file coverage floor: 1
> - Changed files excluded by mutation-line coverage: 5
> - Changed files excluded by selection budgets: 1
> - Changed files excluded by per-file mutation budget (advisory): 1
> - Selected: 5/5
> - Test command: `python3 -m pytest -q tests/quality_gates/test_achieve_adapter_policy.py::test_init_adapter_scaffolds_resolvable_policy tests/quality_gates/test_packaging_validation.py::test_eval_registry_omits_redundant_current_repo_smokes tests/quality_gates/test_packaging_validation.py::test_eval_registry_scenarios_are_immutable_contract_records tests/quality_gates/test_profile_and_preset_validation.py::test_validate_profiles_ignores_gitignored_profiles tests/quality_gates/test_profile_and_preset_validation.py::test_validate_profiles_rejects_missing_extends_reference tests/quality_gates/test_profile_and_preset_validation.py::test_validate_profiles_rejects_missing_skill_reference tests/quality_gates/test_profile_and_preset_validation.py::test_validate_profiles_rejects_unknown_smoke_scenario tests/quality_gates/test_profile_and_preset_validation.py::test_validate_profiles_rejects_unknown_top_level_field tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_degrades_honestly_when_logs_are_missing tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_emits_claude_single_session_audit tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_never_substitutes_a_missing_named_claude_session tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_reads_goal_metric_window tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_rejects_goal_window_with_invalid_timestamp tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_rejects_goal_window_with_missing_session_file tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_rejects_goal_window_without_session_file tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_reports_claude_and_codex_metric_availability tests/quality_gates/test_retro_host_log_probe.py::test_host_log_probe_scopes_goal_window_to_claude_session tests/quality_gates/test_seed_t_events_adapter.py::test_dry_run_emits_source_template tests/quality_gates/test_seed_t_events_adapter.py::test_repo_root_dot_invocation_exits_zero tests/test_adapter_shim_inprocess_coverage.py::test_adapter_shim_in_process_coverage tests/test_cautilus_eval_commands.py::test_eval_cautilus_scenarios_writes_summary tests/test_cautilus_eval_commands.py::test_validate_cautilus_scenarios_covers_eval_surface_wiring`
>
> ## Changed files with uncovered changed lines (blocking)
>
> - `scripts/quality_policy_defaults.py`
> - `skills/public/quality/scripts/runtime_budget_lib.py`
>
> ## Changed-line proof targets
>
> - `scripts/quality_policy_defaults.py:209` `return f"mutation_testing.{section}.{key} must be a string"`
> - `scripts/quality_policy_defaults.py:220` `return problem`
> - `scripts/quality_policy_defaults.py:253` `errors.append(f"mutation_testing.{section} must be a mapping")`
> - `skills/public/quality/scripts/runtime_budget_lib.py:305` `return (`
>
> ## Changed files excluded by file coverage (advisory)
>
> - `scripts/quality_policy_defaults.py`
>
> ## Changed files excluded by mutation-line coverage
>
> - `scripts/check_python_lengths.py`
> - `skills/public/issue/scripts/issue_verify_closeout_body.py`
> - `skills/public/quality/scripts/check_runtime_budget.py`
> - `skills/public/quality/scripts/propose_mutation_testing.py`
> - `skills/public/quality/scripts/runtime_budget_lib.py`
>
> ## Changed files excluded by per-file mutation budget (advisory, non-blocking)
>
> - `scripts/check_skill_contracts.py`
>
> ## Changed sample
>
> (none)
>
> ## Fill sample
>
> - `skills/public/debug/scripts/init_adapter.py`
> - `skills/public/setup/scripts/seed_t_events_adapter.py`
> - `skills/public/retro/scripts/probe_host_logs.py`
> - `skills/public/achieve/scripts/init_adapter.py`
> - `scripts/eval_registry.py`

---

**Source handoff entry #3: Budgets were retuned for `local-linux-x86_64-36cpu` only; aarch64 and the unprofiled defaults were left alone**

> Budgets were retuned for `local-linux-x86_64-36cpu` only; aarch64 and the
>    unprofiled defaults were left alone. Act on `SLACK` lines from
>    `check_runtime_budget.py --runtime-profile <profile>`.

---

**Source handoff entry #2: Residuals, not closed: `issue_close_comment_floor**

> Residuals, not closed: `issue_close_comment_floor.py` omits
>    `evaluate_ai_provenance` and the ledger-field / close-keyword checks; every quality
>    run rewrites the tracked specdown report because [specdown.json](../specdown.json)
>    hardcodes `outFile` — restore by hand before staging; the plugin-copy fresh-install
>    render path is untested, the ONLY delivery path for the workflow change.

---

**Source handoff entry #1: Sweep for other built-with-intent-but-unused modes and options**

> (operator
>    request). `retro`'s `weekly` was the first instance: a deliberately designed mode
>    whose entire behavioral delta was two extra `required_reads`, invoked once in
>    3.5 months, with a configured snapshot nothing ever read. Look for the same shape
>    elsewhere — adapter enum fields, planner branches, `--mode`/`--part` style flags,
>    preset variants. The tell is a branch whose two arms produce nearly the same plan.
>    `inventory_skill_ergonomics.py`'s `mode_option_pressure` rule is a starting
>    detector, not the answer; usage evidence (artifact counts, git history) decides.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk. Handoff
  entry #4 (the deferred backlog, ranked chunk 4) is explicitly out.
- **Do not close #453.** The operator closes it; this run lands the fix and
  posts closeout evidence only.
- **No deletions in the unused-mode sweep.** The sweep produces an
  evidence-backed candidate inventory and stops for operator sign-off.
- Not retuning the `local-linux-aarch64-4cpu` or unprofiled `default` budgets:
  `.charness/quality/runtime-signals.json` carries samples for
  `local-linux-x86_64-36cpu` only, so there is no local evidence to retune from.

## Boundaries

- In scope: `scripts/agent-runtime/skill-test-telemetry.mjs`, `scripts/check_python_lengths.py`, `scripts/check_skill_contracts.py`, `scripts/eval_registry.py`, `scripts/quality_policy_defaults.py`, `skills/public/achieve/scripts/init_adapter.py`, `skills/public/debug/scripts/init_adapter.py`, `skills/public/issue/scripts/issue_close_comment_floor.py`, `skills/public/issue/scripts/issue_verify_closeout_body.py`, `skills/public/quality/references/mutation-testing.md`, `skills/public/quality/scripts/check_runtime_budget.py`, `skills/public/quality/scripts/propose_mutation_testing.py`, `skills/public/quality/scripts/runtime_budget_lib.py`, `skills/public/retro/scripts/probe_host_logs.py`, `skills/public/setup/scripts/seed_t_events_adapter.py`, `specdown.json`, `tests/quality_gates/test_achieve_adapter_policy.py`, `tests/quality_gates/test_packaging_validation.py`, `tests/quality_gates/test_profile_and_preset_validation.py`, `tests/quality_gates/test_retro_host_log_probe.py`, `tests/quality_gates/test_seed_t_events_adapter.py`, `tests/test_adapter_shim_inprocess_coverage.py`, `tests/test_cautilus_eval_commands.py`
- Also in scope: the plugin mirror under `plugins/charness/**` for every touched
  skill or script (e.g. `plugins/charness/skills/issue/scripts/issue_close_comment_floor.py`,
  `plugins/charness/skills/quality/scripts/templates/mutation-tests.yml`), synced
  before validators run.
- Portable per implementation-discipline: no host-specific assumption. Budget
  values stay per-profile in `.agents/quality-adapter.yaml`; nothing here hardcodes
  one machine's numbers into skill or script defaults.
- Stop conditions: name on first discovery; do not guess.
  - Stop and ask if the specdown churn root cause turns out to require changing
    what is tracked as spec evidence (the report is deliberately committed).
  - Stop and ask if killing a survived mutant would need a behavior change rather
    than a test.
  - Stop at the sweep inventory; do not delete.

## Discuss before activation

Resolved with the operator during the Before-phase interview (2026-07-25):

- **#453 close authority — resolved:** the operator closes #453. This run lands
  the fix and posts a closeout evidence comment; no `Close #N` keyword on any
  commit, no `gh issue close`. Consistent with the north-star irreversible
  boundary rule and the workflow change that stopped auto-closing.
- **Sweep deletion authority — resolved:** report-first. The sweep emits a
  candidate inventory with usage evidence; every deletion waits for operator
  sign-off in a later run.
- **Bundled scope — resolved:** three ranked chunks in one goal, run in ranked
  order, each slice closing independently. The operator selected the 1-3 span
  from the chunked-routing ranking.
- **Proof-level non-claim — surfaced and accepted:** the aarch64 and unprofiled
  budget retune cannot be proven from this machine (no samples for those
  profiles). Carried in the Operator Decision Queue instead of being faked.
- **Timebox — resolved:** none. Run to completion or to a named blocker.

## User Acceptance

- `#453`'s blocking signal is gone: the changed-line proof targets
  (`scripts/quality_policy_defaults.py:209,220,253` and
  `skills/public/quality/scripts/runtime_budget_lib.py:305`) are covered by real
  tests, confirmed by `check_changed_line_mutation_coverage.py` over
  `base..head`. Separately, the 7 survived
  `skills/public/retro/scripts/probe_host_logs.py` mutants are killed (score
  hygiene, not the blocker).
- The changed-line fix is confirmed by the **next scheduled** mutation run,
  verified with `python3 scripts/check_mutation_run_proof.py --claim changed-line
  --run-id <id>`. A `workflow_dispatch` re-run does **not** count: only
  `schedule` events compute `base_sha`, so a dispatch leaves the changed-line
  classifier inert and proves only the score path.
- `#453` is still open, carrying a comment with the fix commit and the local
  changed-line coverage output, ready for the operator's own close.
- The automated quality gate does not rewrite the tracked
  `.charness/specdown/report.json` (a manual `specdown run` still refreshes it by
  design — timing metadata means it can never no-op), or the goal says exactly
  why the residual is already closed / not repo-fixable.
- `issue_close_comment_floor.py` checks `evaluate_ai_provenance` and the
  ledger-field / close-keyword conditions it previously omitted, with tests that
  fail without the new checks.
- The plugin-copy fresh-install render path has an executed test, not an assertion
  that it was eyeballed.
- The operator receives one durable sweep artifact listing every candidate
  built-with-intent-but-unused mode/option with its usage evidence, and nothing
  was deleted.

## Agent Verification Plan

Low-cost (every commit boundary):

- `ruff check` on touched Python; `python3 -m pytest -q <touched test files>`.
- **Sync the plugin mirror before validators** for every touched skill/script
  (`python3 scripts/sync_root_plugin_manifests.py --repo-root .`), then the owning
  surface's validators for the changed paths. Never validators before sync.
- `git status --short` clean of unintended derived churn before staging (the
  specdown report is the known trap until slice 4 closes it).

Slice-boundary:

- Slice 1: **not** a mutation run. The blocker is computed from a coverage report
  *before* any mutant executes (`classify_changed_line_scope_gap`,
  `scripts/mutation_changed_files_lib.py:34-62`), and the score path already
  passed — running mutants here would prove the wrong thing at high cost. Use
  `python3 scripts/run_slice_closeout.py --produce-mutation-coverage` then
  `python3 scripts/check_changed_line_mutation_coverage.py --base-sha
  835181c38aef7c629f7745aeb4f0ef633d80c9bb --head-sha <fix-commit>`.
  Collect coverage **only** via that producer (`run_test_coverage`), never a bare
  `coverage run -m pytest`: the latter misreports subprocess-invoked CLI scripts
  as 0%, which is exactly the shape of `quality_policy_defaults.py`.
- Slice 2: targeted mutant proof over `probe_host_logs.py` only, with explicit
  `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA`. For the format mutants at line 63
  (`indent=2`, `sort_keys`, `ensure_ascii`), assert on **raw serialized output** —
  a `json.loads` round-trip is indentation-agnostic and cannot kill them.
- Slices 3-5: `./scripts/run-quality.sh --read-only` (or the documented
  substitute), which is the gate that owns these surfaces.
- Slice 6: no gate — the deliverable is an audit artifact; correctness is judged
  by the evidence cited per candidate.

High-confidence / high-cost:

- The authoritative changed-line verdict is the **next scheduled** CI mutation
  run, checked with `scripts/check_mutation_run_proof.py --claim changed-line`.
  Local `check_changed_line_mutation_coverage.py` output is evidence that the
  blocking signal is addressed; it is **not** a claim that the CI mutation job is
  green, and a `workflow_dispatch` re-run cannot supply that claim either.

Closeout obligations (repo contract, not optional follow-up):

- Retire or rewrite handoff entries #1, #2, #3 and the #453 line in
  `docs/handoff.md` at closeout — one write at the end, not at pickup.
- Commit `charness-artifacts/` additions (sweep audit, any debug artifact,
  critique packets, this goal file) with the slice they support.
- Run the mandated bounded fresh-eye critique before each slice's commit.

Test-duplication pressure:

- Slices 1 and 3 add tests to `tests/quality_gates/` and are the ones most likely
  to push a broad duplicate/length/pressure gate toward threshold; each states its
  duplicate-pressure sample in its slice log entry. Slices 4-6 add little or no
  test surface.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | [done] Cover the four uncovered changed lines in `quality_policy_defaults.py` and `runtime_budget_lib.py` | The blocking signal of #453; nothing else can be proven green under a red gate | New tests failing without the covered lines; `check_changed_line_mutation_coverage.py` clean over `base..head`. #453's closeout comment can be posted at the end of this slice | planned |
| 2 | [done] Kill the 7 survived `probe_host_logs.py` `main()` mutants (the `--format markdown` branch at :60 and the `json.dumps` kwargs at :63) | Score hygiene in the same file set — **not** part of #453's blocking signal, and does not gate the closeout comment | Test asserting raw output for both formats; survived count 0 for that file | planned |
| 3 | [done] Wire `evaluate_ai_provenance` into `issue_close_comment_floor.py`; record close-keyword and ledger-field as intentionally not wired, with reasons, and close the residual | Operator decision 2026-07-25: only the provenance check is a genuine gap for the close-with-comment carrier. Close-keyword needs a repo slug `evaluate_close_comment_floor` never receives and is inert inside a comment; ledger fields would need a new public wrapper for unclear benefit | Test that fails with the provenance check removed; the two not-wired rationales recorded in the floor's own docstring/reference so the residual does not return a third time; quality read-only green | planned |
| 4 | [done, reproduced and fixed] Reproduce the tracked-specdown-report churn first, then act | Both the runner (`scripts/run-quality.sh:523`) and the owning surface already write to a temp dir, and `-quiet -no-report` was removed on 2026-07-22 because specdown rejects them — the residual may already be closed | Step 0: full quality gate, then `git status --short .charness/specdown/`. If clean: record "already fixed by the 2026-07-22 change" with the evidence and **stop — do not backfill the slot** (operator decision 2026-07-25; no regression guard, no substitute work). Only debug further if it reproduces | planned |
| 5 | [done, found a shipped bug] Test the fresh-install render path: from a plugin copy, `propose_mutation_testing.py --execute` renders `templates/mutation-tests.yml` into `workflow_path` | Sole delivery path — the workflow is written once at first install, never re-rendered, and `--execute` refuses to overwrite | Test over a fresh temp repo asserting rendered workflow content including `schedule_cron` substitution | planned |
| 6 | [done, 9 confirmed / 3 refuted, zero deletions] Sweep all four surface families for built-with-intent-but-unused modes/options; emit a candidate inventory with usage evidence | Standing operator request; safest once the gate is trustworthy. Scope confirmed 2026-07-25: (a) adapter enum fields, (b) planner branches, (c) `--mode`/`--part` style flags, (d) preset variants — not flags-only, because the `retro` `weekly` instance lived in a planner branch | Audit artifact under `charness-artifacts/audit/` listing each candidate with its usage evidence (artifact counts, git history) and the branch-arms-produce-the-same-plan test result; zero deletions | planned |

Critique plan: a bounded `bounded-reviewer` fresh-eye pass on this plan before
activation, and one per substantial slice (1, 3, 4, 6 at minimum) with the slice
packet named in the Active Operating Frame.

## Operator Decision Queue

- Decision: close #453 once the fix has landed and the mutation gate is green
- Owner: operator (bae.hwidong@corca.ai)
- Why deferred: the operator explicitly retained the close; it is an irreversible
  boundary and the run can finish every other obligation without it
- Unblock action: wait for the next **scheduled** mutation run on the fix commit
  and verify it with `python3 scripts/check_mutation_run_proof.py --claim
  changed-line --run-id <id>` (a `workflow_dispatch` re-run cannot prove this),
  read the closeout comment, then close #453
- Revisit trigger: the closeout comment posted at the end of slice 1

- Decision: whether to retune the `local-linux-aarch64-4cpu` and unprofiled
  `default` runtime budgets, and on what evidence
- Owner: operator
- Why deferred: `.charness/quality/runtime-signals.json` has samples only for
  `local-linux-x86_64-36cpu`; `check_runtime_budget --summary` reports zero slack
  findings here, so there is nothing to act on from this machine
- Unblock action: run `check_runtime_budget.py --runtime-profile
  local-linux-aarch64-4cpu --detail` on the aarch64 box (or import its signals)
  and act on the `SLACK` lines there
- Revisit trigger: next session on aarch64 hardware, or CI publishing per-profile
  runtime signals

- Decision: whether to cut a patch release carrying the plugin-copy render fix
- Owner: operator
- Why deferred: releasing is an irreversible external boundary and outside this
  goal's Non-Goals ("Not a release: no plugin version bump expected"). The fix is
  committed; shipping it is a separate call.
- Unblock action: cut a patch release, or decide the fix rides the next cut. Note
  the affected population is fresh installs on any tag back to at least v2.2.1 —
  `--execute` raises FileNotFoundError after half-scaffolding their adapter, and
  recovery is a hand edit of `.agents/quality-adapter.yaml`.
- Revisit trigger: the correction recorded in
  charness-artifacts/release/2026-07-25-v2.5.0-notes.md

- Decision: [DISCHARGED 2026-07-25] which swept unused modes/options to delete —
  4 deleted, 5 kept, `--granularity` scheduled for extension instead. One newly
  surfaced twin (`recommended_commands`) still needs the same call.
- Owner: operator
- Why deferred: the operator chose report-first; deletions at repo scale are the
  change class most likely to be wrong without a human read
- Unblock action: read [the sweep artifact](../audit/2026-07-25-unused-mode-option-sweep.md)
  and name which of the 9 confirmed candidates to delete. Note that four of them
  (`run_mode: auto`, achieve `default_mode`, hitl `default_scope`, the cautilus
  enum) are published portable contracts, so removal narrows a downstream contract
  this repo cannot observe
- Revisit trigger: delivery of the sweep artifact at the end of this run

## Slice Log

### Slice 1: Slice 1 — #453 changed-line coverage

- Objective: Cover the four changed lines the mutation gate flagged as uncovered before mutation: scripts/quality_policy_defaults.py:209,220,253 and skills/public/quality/scripts/runtime_budget_lib.py:305. This is #453's only blocking signal; the mutation score already passed at 94.2%.
- Why this approach: Wrote behaviour tests through the public entry points (load_quality_adapter, the check_runtime_budget CLI) rather than poking private helpers, so the coverage survives a refactor. The slack-render test pins the operator-facing SLACK line because the handoff instruction is literally 'act on SLACK lines' — the line has to carry which budget, its current value, the worst recent run, and the suggested value.
- Commits:
- What changed: tests/quality_gates/test_quality_mutation_testing.py (3 new adapter-validation tests), tests/quality_gates/test_runtime_budget_gate.py (1 new slack-render test + 11 render tests moved out), tests/quality_gates/test_runtime_summary_render.py (new module), tests/quality_gates/support.py (received seed_runtime_budget_repo)
- Alternatives rejected: Rejected running mutants over the four targets: the blocker is computed from a coverage report before any mutant executes (scripts/mutation_changed_files_lib.py:34-62), so mutation would have proven the wrong thing at high cost. Rejected an _extra_lib companion for the 809/800 length overflow (docs/deferred-decisions.md D33) in favour of a cohesive split along the script boundary: render_runtime_summary.py tests moved out, check_runtime_budget.py tests stayed.
- Targeted verification: All 4 target lines COVERED in a coverage report produced via mutation_sampling_lib.run_test_coverage (the gate's own method, which captures subprocess-invoked CLI scripts; a bare 'coverage run' would have misreported them as 0%). Each of the 4 lines individually mutated and confirmed KILLED by the new tests, then restored. 88 tests pass across the three touched files. run_slice_closeout.py --skip-broad-pytest: Closeout status completed, all verify gates PASS.
- Test duplication pressure: check_dup_ratchet.py --summary: status clean, new_code_family_count 0, no boy-scout or hard block. Length: test_runtime_budget_gate.py went 809 -> under the cap via the split; test_quality_mutation_testing.py sits at 768/800 in the advisory warn band and is the next split candidate if it grows.
- Critique: Bounded fresh-eye bounded-reviewer (agent ad3f32bb6e9f0efe5); boundary fingerprint verified ok/no-drift. Applied: F1 dead render-script loader left in the gate module after the move (5 dead lines in the file that had just failed the cap); F2 a vacuous assertion — the auto_issue fixture never set 'enabled', so the negative assertion could not fail under any mutation; fixture now sets it and asserts the boolean error, covering the enabled branch too. F3 added an in-process _render_slack witness so the line cannot silently lose coverage if that run_script call ever gets an explicit env= dict. F5 corrected an overstated seeder docstring. F6 reused the imported ROOT. Reviewer judged the file split honest against D33 (two scripts, two contracts) and found nothing lost in the move.
- Off-goal findings: none this slice
- Lessons carried forward: The mutation gate's changed-line blocker and its score are two different signals with two different instruments; the handoff's wording ('killing the survived mutants') conflated them and would have sent this slice at the wrong proof. Also: adding a test to a file already at 809/800 forces a split decision mid-slice — worth checking the length headroom before choosing where a new test lands.
- Metrics:

### Slice 2: Slice 2 — probe_host_logs survived mutants

- Objective: Close the 7 mutants that survived in skills/public/retro/scripts/probe_host_logs.py main(). Score hygiene, not #453's blocker — the closeout comment for #453 went out after slice 1 and did not wait on this.
- Why this approach: Four of the seven (sort_keys, ensure_ascii, two indent replacements) are killable by asserting the raw serialized text; a json.loads round-trip is indentation- and order-agnostic and cannot see them. The three on 'if args.format == "markdown"' could not all be killed by a test: with exactly two argparse choices, '==' and '>=' are behaviourally identical, so Eq->GtE is an equivalent mutant. Replaced the comparison with a dict dispatch keyed by the same FORMAT_CHOICES tuple argparse validates against, removing the surface rather than chasing it. Byte-identical output proven for --format json, --format markdown, and the default.
- Commits:
- What changed: skills/public/retro/scripts/probe_host_logs.py (FORMAT_CHOICES + render_output dispatch), its plugin mirror, tests/quality_gates/test_retro_host_log_probe.py (3 new tests)
- Alternatives rejected: Rejected a subprocess-based test to kill the Eq->Is mutant: it is killable that way (real argv strings are not interned, unlike the in-process harness's literals), but the dict dispatch removes the comparison entirely, so the extra process-spawn cost buys nothing. Rejected leaving Eq->GtE as a permanent survivor.
- Targeted verification: 20 tests pass. All 4 json.dumps mutants re-verified KILLED after the refactor, plus a dispatch-pinned-to-json mutant KILLED. Byte-identity vs HEAD confirmed for all three invocations. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review: completed, plugin mirror in sync.
- Test duplication pressure: 3 tests added to test_retro_host_log_probe.py; file is well under the 800-line cap and check_dup_ratchet stayed clean at the previous slice boundary.
- Critique: Bounded fresh-eye bounded-reviewer (agent a33ff8985b32e656e); boundary fingerprint ok/no-drift. F1 BLOCKER, confirmed and fixed: the refactor was present only in the generated plugin mirror — the canonical source had been reverted to HEAD, one test was erroring, and the recorded proof did not match the tree. Cause identified: this slice's own mutant-verification loop ended each iteration with 'git checkout -- <source>', which reverts to HEAD, and the refactor was uncommitted. That also invalidated the post-refactor mutant results (the AttributeError made pytest fail every iteration, so each spuriously reported KILLED). Refactor restored from the mirror, re-synced, and all mutants re-verified with a pristine-copy restore plus a green-baseline assertion. F2 applied: the docstring's claim that 'is' is unkillable was wrong — it survived only because the in-process harness passes interned literals; reworded to the '>=' equivalence, which the reviewer independently verified. F3 (KeyError instead of silent JSON fallback for an unknown format) accepted as the better behaviour.
- Off-goal findings: none this slice
- Lessons carried forward: 'git checkout -- <path>' as a mutation-test restore silently reverts uncommitted work to HEAD. Use a pristine copy (cp) and assert a green baseline before each mutation, otherwise a failing baseline makes every mutant look killed. This is the #258 shape from the inside: the recorded proof was true when taken and false by the time it was written down.
- Metrics:

### Slice 3: Slice 3 — issue_close_comment_floor provenance residual

- Objective: Wire evaluate_ai_provenance into the close-with-comment floor and record close-keyword and ledger-field as intentionally not wired, closing the named residual.
- Why this approach: Same asymmetry the module's own docstring already documents for the HOTL floor: verify-closeout and the commit-msg carrier both check the AI-provenance marker, and the one carrier that writes to GitHub itself did not. The marker is what makes an irreversible external write legible as agent-authored to the rung-2 observer, so the carrier with the strongest need for it was the one without it.
- Commits:
- What changed: skills/public/issue/scripts/issue_close_comment_floor.py (+ mirror), skills/public/issue/references/issue-backend.md (+ mirror), tests/quality_gates/test_issue_close_comment_floor.py (2 new tests)
- Alternatives rejected: Rejected wiring close-keyword: verify-closeout itself exempts this carrier (manual-fallback), and a Closes #N keyword is inert inside an issue comment. Rejected wiring ledger fields: they ARE presence checks that verify-closeout applies to this same body, so the honest reason is scope restraint, not a rung distinction — wiring them would newly refuse short close comments whose ledger lives in the commit carrier, well past the named residual.
- Targeted verification: 8 tests pass in the floor's own file; 36 across test_issue_skill.py + test_issue_close_exemption_advisory.py; 57 including the commit-msg hook file. Mutation spot-check: removing 'and ai_provenance["ok"]' from the ok conjunction is KILLED. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review: completed, mirror in sync.
- Test duplication pressure: 2 tests added; file well under the cap. Dup-ratchet clean at the previous slice boundary and the closeout gate's dup check passed again here.
- Critique: Bounded fresh-eye bounded-reviewer (agent ac3fc30f72186a48a). It corrected two of my OWN justifications, both now rewritten: (1) I framed ledger fields as 'rung-2 content judgment' — wrong; _missing_ledger_fields is presence-only, is the repo's archetype for that shape (evaluate_source_preservation describes itself as mirroring it), and verify-closeout applies it to this same manual-fallback body. (2) My close-keyword reason led with 'the signature cannot supply a repo slug' — inaccurate (the signature takes repo_root, and the sole caller has the slug) and it omitted the decisive evidence: verify-closeout already exempts this carrier explicitly. Both rewritten to the true reasons. F1 applied: skills/public/issue/references/issue-backend.md still listed the floor without the HOTL and AI-provenance checks — the operator-facing surface would have contradicted a new hard refusal. F4 confirmed my judgment that the surviving formatter-guard mutant is genuinely equivalent (evaluate_ai_provenance never returns applies=False with ok=False), so no test was written for it. Reviewer verified the mirror byte-identical and found no consumer broken by the new report key.
- Off-goal findings: none this slice
- Lessons carried forward: A justification checked into a docstring is worse than no docstring when it is wrong — it will be cited by the next reader deciding whether to re-file the gap. Both of my not-wired reasons were plausible and both were contradicted by files one directory away. Also a protocol slip: I ran the reviewer boundary verify AFTER applying the review's fixes, so its drift set is my own edits and the boundary proof for this review is weaker than it should be. Verify immediately on reviewer return, before touching anything.
- Metrics:

### Slice 4: Slice 4 — tracked specdown report churn

- Objective: Reproduce the specdown churn residual before assuming it existed, then fix it. It DID reproduce: a full quality run left 'M .charness/specdown/report.json' whose entire diff was the generatedAt timestamp.
- Why this approach: Root cause: 'specdown run -out <dir>' redirects only the HTML directory; the JSON reporter's destination is reporters[].outFile in specdown.json, which no CLI flag overrides — only -config does. So the automated gate rewrote a tracked file on every run for a field carrying no evidence. New scripts/specdown_ephemeral_config.py emits a redirected config; run-quality.sh and the executable-specs owning surface both use it. The config is written beside specdown.json (gitignored, trap-removed) because specdown resolves 'entry' by joining it onto the CONFIG FILE's directory — even when entry is absolute; both alternatives were tested and failed.
- Commits:
- What changed: scripts/specdown_ephemeral_config.py (new), scripts/run-quality.sh, .agents/surfaces.json, .gitignore, presets/specdown-quality.md, tests/quality_gates/support.py, tests/quality_gates/test_quality_runner.py, plus plugin mirrors
- Alternatives rejected: Rejected pointing the committed specdown.json's outFile at a gitignored path: that untracks the report which is deliberately the committed spec evidence, guarded by check_spec_evidence_durability. Rejected a unique mktemp config name: it fixes a concurrency race that is already harmless and creates unbounded litter in exchange. Rejected leaving the residual closed-as-already-fixed — it reproduced.
- Targeted verification: Full ./scripts/run-quality.sh --read-only: 81 passed, 0 failed, and 'git status --short .charness/specdown/' EMPTY afterwards (was 'M report.json' before the fix). No stray .specdown.ephemeral.json. Adversarially verified the new guards: reintroducing the churn (passing the repo's own specdown.json to -config) FAILS both new tests; adding an unstubbed repo script inside a bash -c gate FAILS the widened drift guard.
- Test duplication pressure: check_dup_ratchet --summary: clean, 0 new code families. Tests added to test_quality_runner.py (2 new + 1 rewritten); file remains under the cap.
- Critique: Bounded fresh-eye bounded-reviewer (agent a989215320a0751fb); boundary verify run IMMEDIATELY on return this time (the slice 3 lesson) — ok, no drift. R1 applied: the rewritten test asserted '-config' as a bare substring, so passing the repo's OWN specdown.json would keep all six assertions green and restore the churn — the same assert-the-proxy hole one level up. Now binds the flag to $specdown_config. R2 applied: added an end-to-end test that observes the property directly (no rewritten report, no leftover config, and the config specdown was actually handed points its reporters outside the repo), using a new argv-recording specdown stub. R3 applied: the seeded-harness drift guard could not see repo scripts invoked from a bash -c gate — exactly why this slice's seeding had to be remembered by hand; widened, then narrowed to repo-root scripts after it over-matched skill-package gates. R4 applied: a reporter with no outFile now fails with a stated policy instead of a KeyError. R5 applied: presets/specdown-quality.md recommended 'specdown run -quiet' — a flag specdown rejects, removed from this repo on 2026-07-22 — and a bare invocation that would dirty a consumer repo's tracked report the same way. R8 applied: || exit 1 parity in the surfaces.json verify command. R6/R7 (repo-root config placement, nested trap quoting) reviewed and confirmed correct; no action.
- Off-goal findings: none this slice
- Lessons carried forward: The residual was real and the prior debug artifact's 'maybe already fixed' framing would have closed it wrongly — reproducing first was worth the full gate run. The deeper lesson is the one the reviewer kept finding: a test named for an outcome that asserts a flag string will pass while the outcome is false. The replaced test had been green for months WHILE dirtying the worktree it was named after, and my first replacement had the same shape one level up.
- Metrics:

### Slice 5: Slice 5 — fresh-install render path (found a shipped bug)

- Objective: Test the plugin-copy fresh-install render path, the ONLY delivery path for the mutation workflow. Testing it found it was not merely untested but BROKEN, in every tag back to at least v2.2.1.
- Why this approach: propose_mutation_testing.py resolved its template as REPO_ROOT / 'skills/public/quality/scripts/templates/mutation-tests.yml'. Plugin export collapses skills/public/<skill>/ to skills/<skill>/, so in the only copy a consumer installs that path does not exist: --execute raised FileNotFoundError AFTER appending the adapter scaffold, and --execute only runs while the block is missing, so recovery is a hand edit. Fixed by resolving the template beside the script (the idiom all nine other live template consumers already use) and checking it before the adapter is written.
- Commits:
- What changed: skills/public/quality/scripts/propose_mutation_testing.py (+ mirror), scripts/check_export_safe_imports.py, four dead REPO_ROOT/skills/public constants deleted across retro and release scripts, tests/quality_gates/test_mutation_workflow_install.py (new, 5 tests), charness-artifacts/release/2026-07-25-v2.5.0-notes.md (correction), charness-artifacts/quality/dup-review.json
- Alternatives rejected: Rejected leaving REPO_ROOT in propose_mutation_testing.py once unused: verified against check_skill_bootstrap_vars.py, check_bootstrap_shim_consistency.py and check_skill_contracts.py that no gate requires it, and leaving a live REPO_ROOT in the one file just burned by it is an invitation to the same mistake. Rejected extracting the now-duplicate bootstrap preamble: it is per-package portability boilerplate the export copies verbatim; classified intentional in dup-review.json.
- Targeted verification: 5 new tests pass; 74 across the three related files; full ./scripts/run-quality.sh --read-only 81 passed 0 failed. Adversarial: reintroducing the REPO_ROOT-relative constant fails 2 of the delivery tests; moving the template check back after the adapter write fails both ordering tests. The bug itself was reproduced by hand against a temp repo before any fix. check_export_safe_imports now validates 585 files clean and, before the four deletions, fired on exactly them.
- Test duplication pressure: check_dup_ratchet went hard-block on a new family created BY the dead-constant deletion (two bootstrap preambles became byte-identical); classified intentional with a note rather than extracted. Now clean, 0 new code families. 5 tests added in a new cohesive module rather than growing test_quality_mutation_testing.py, which sits at 768/800.
- Critique: Bounded fresh-eye bounded-reviewer (agent aaaf6310fb2670780); boundary verify run immediately on return — ok, no drift. F1 (blocker, release surface): confirmed by git — v2.2.1 through v2.5.0 all ship the broken constant, and the v2.5.0 notes' 'Why minor' rationale says the change reaches 'only fresh installs', which is exactly the population that cannot complete. Recorded a Correction section in those notes, fixed the hand-copy path they gave (it named the authoring path, which does not exist in an install), and queued the patch-release decision for the operator since releasing is outside this goal's Non-Goals. F6 (the durable fix) applied: check_export_safe_imports.py already encoded this exact insight for imports and stopped one syntax short of filesystem paths; extended it to reject REPO_ROOT-rooted skills/public paths, with an exemption for deliberate dual-layout probes like resolve_artifact_path.py. F5 applied: four dead constants of the same shape deleted. F2/F3/F4/F9 applied: dead kwarg removed; the render test now anchors to the shipped template instead of only 'a cron is present' (the reviewer noted the identical-renders test would pass if BOTH were wrong); a dry-run test asserts the reported source path exists; and a cheap in-process ordering test carries the partial-write invariant in standing runs, since the layout-faithful one is necessarily release_only.
- Off-goal findings: F1's patch-release decision is queued for the operator rather than acted on — releasing is an irreversible boundary and this goal's Non-Goals exclude it.
- Lessons carried forward: The handoff said 'untested'; it was broken, and had been through eight releases. 'Untested' on a sole delivery path should be read as 'unknown', not 'probably fine'. The durable win was not the three tests — it was noticing that an existing gate already encoded the insight for imports and stopped one syntax short of the filesystem, where the same collapse fails silently instead of raising ModuleNotFoundError.
- Metrics:

### Slice 6: Slice 6 — unused mode/option sweep

- Objective: Sweep all four surface families (adapter enum fields, planner branches, --mode/--part flags, preset variants) for built-with-intent-but-unused options; emit an evidence-backed candidate inventory. Zero deletions per operator decision.
- Why this approach: Four independent surface families each needing a different search method, then per-candidate usage evidence — genuine fan-out work. Ran a 17-agent dynamic workflow: four parallel scouts, then an adversarial refutation pass whose default was that each candidate is WRONG, then synthesis. The refutation pass earned its cost: it killed 3 of 12.
- Commits:
- What changed: charness-artifacts/audit/2026-07-25-unused-mode-option-sweep.md (new)
- Alternatives rejected: Rejected a flags-only sweep: the one confirmed archetype (retro's weekly) lived in a planner branch, so the narrow scope would have missed the case that motivated the request. Rejected acting on any candidate: operator chose report-first.
- Targeted verification: 27 candidates scouted, 13 refutation-verified, 9 confirmed-unused, 3 refuted. Confirmations carry concrete evidence (in-process A/B runs with a monkeypatched adapter; scan_scenario A/B across all 54 real JSON specs; git log -S birth-and-never-touched history; artifact-count proxies). The artifact names its own blind spots explicitly: static-only, cannot see downstream installs of published portable contracts, artifact counts are a proxy, agent-selected options are invisible to flag greps.
- Test duplication pressure: No tests added; the deliverable is an audit artifact. Dup-ratchet clean at the previous slice boundary and the closeout gate's check passed again here.
- Critique: No separate fresh-eye pass: the workflow's own refutation stage IS the adversarial review, run by 12 independent agents whose instructed default was to refute. It overturned 3 candidates — reviewer_tiers.medium (two real consumers the scout missed, one of them prose in a shared reference that a flag-grep cannot see), release-adapter requested_review_policy (the arms genuinely differ and the delta is published in every release artifact), and presets/*.md bodies (deliberate markdown-first contract recorded in deferred-decisions D9/D13, and commit 3b0750a6 from this very session wrote a lesson into one of them).
- Off-goal findings: The sweep flagged two adjacent issues it declined to act on, both recorded in the artifact: a packet tier-propagation inconsistency (critique packets hardcode high-leverage while agents record 'Requested tier: medium'), and presets/specdown-quality.md duplicating DEFAULT_SPECDOWN_SMOKE_PATTERNS with no drift gate.
- Lessons carried forward: My workflow agents were not constrained to read-only and one edited .agents/cautilus-adapter.yaml (run_mode ask -> auto) to A/B a branch, leaving it dirty. Caught by git status and restored, but the parent-side lesson is that a discovery fan-out should spawn read-only reviewers — the repo has a bounded-reviewer type for exactly this and I did not use it for workflow agents. Second lesson, from the refutations: 'no CLI caller' is not evidence of no caller in this repo, because agent-selected options are chosen by prose in SKILL.md and shared references.
- Metrics:

### Slice 7: Slice 7 — operator sign-off on the sweep deletions

- Objective: Act on the operator's sign-off from the slice-6 sweep: delete 4 of the 9 confirmed candidates, keep 5 with reasons recorded.
- Why this approach: Deleted: --scan-comments (zero callers, zero measured effect), required=False plus its three dead consumer arms (an unreachable cautilus-blocking closeout branch), --replace-file (flag only; the guard it relaxed became a hard refusal), and the four profiles/*.json instances (zero runtime effect; schema/README/directory kept because packaging requires profiles_dir). Kept: the four published portable contracts, plus --granularity which the operator scheduled for extension rather than removal.
- Commits:
- What changed: scripts/prompt_mutation_clean_proof_preflight.py, scripts/plan_cautilus_proof.py, scripts/run_slice_closeout.py, scripts/slice_closeout_reporting.py, scripts/refresh_current_pointer.py, profiles/ (4 instances deleted, README rewritten), skills/public/quality/references/attention-state-visibility.json, charness-artifacts/quality/dup-review.json, the sweep artifact's new Operator Disposition section, 3 test files, plus plugin mirrors
- Alternatives rejected: Rejected deleting recommended_commands, the twin dead literal from the same commit: it was not part of the sign-off, so it is recorded in the audit disposition as needing the same decision rather than taken silently. Rejected classifying away the refresh_current_pointer duplication the deletion exposed — the two strategies genuinely shared a tail, so it was extracted; only the two boilerplate families (a three-term bool predicate, the argparse main() preamble across five CLIs) were classified intentional.
- Targeted verification: Broad pytest 5042 passed; full run-quality --read-only 81 passed / 0 failed; run_slice_closeout completed; dup ratchet clean. The rewritten comment-skip test was adversarially verified — making the skip unconditional kills it, which the previous fixture could not do.
- Test duplication pressure: No net test growth: two constant-pinning assertions deleted with the constants they pinned, one fixture key removed, one test rewritten to actually exercise its subject. Dup ratchet went hard-block on three families created BY the deletions; one extracted, two classified with reasons.
- Critique: Bounded fresh-eye bounded-reviewer (agent aeb903ff0b184e317); boundary verified immediately on return, no drift. It cleared the change I most distrusted — removing an attention-state declaration to satisfy a validator — by showing the entry had been asserting a visibility that lived inside unreachable code, and that every genuine surface of the cautilus disabled state is untouched. Applied: F4 (recorded the recommended_commands twin instead of silently leaving it), F6 (dropped an unused repo_root parameter), F8 (the profiles README link dangled once mirrored into the plugin tree, where charness-artifacts is not shipped — now an absolute URL), F9 (the sweep artifact still said 'zero deletions were made', which was now false — appended an Operator Disposition section), F10 (the comment-skip test used a top-level _comment that the visible-key filter drops anyway, so it passed with or without the skip), F11 (stale fixture key). F1/F2/F3/F5 confirmed behaviour-preserving with line evidence.
- Off-goal findings: recommended_commands in plan_cautilus_proof.py is the same dead-literal shape as the deleted required and needs the same operator decision; recorded in the sweep artifact's disposition section.
- Lessons carried forward: Deleting dead code shrinks files until they match other files — the dup ratchet hard-blocked three times on families the deletions created. Two were boilerplate, but one was genuine duplication the dead parameter had been masking, so the ratchet earned its block. Also: an artifact that records a decision ('zero deletions were made') becomes a lie the moment the decision changes, and it is the standing inventory the next reader consults.
- Metrics:

### Slice 8: Slice 8 — implement paragraph granularity

- Objective: Implement the extension --granularity was a seam for, instead of deleting it. Paragraph units now work end to end: split mints them, generate builds real mutants from them, and both the plugin mirror and its public sibling are mutated.
- Why this approach: Section granularity can only say 'this whole section had no observable effect'. Paragraph units distinguish load-bearing prose from decoration inside a section that survives as a whole — which is what the pilot goal recorded granularity as a design axis for. Paragraph units are derived from leaf spans (heading to the NEXT heading of any level) rather than section spans, so a line inside a nested subsection is not claimed by two units; they exclude the heading line, skip YAML frontmatter, and stay top_level=False so the lossless tiling invariant is untouched.
- Commits:
- What changed: scripts/prompt_mutant_split_lib.py (new — the pure splitting half), scripts/prompt_mutant_lib.py, scripts/generate_prompt_mutants.py, docs/prompt-mutation-policy.md, the pilot goal artifact (dated addendum), tests/test_generate_prompt_mutants.py (13 new tests), plus plugin mirrors
- Alternatives rejected: Rejected replacing section units with paragraph units: the coarse arm stays selectable, so a caller that only knew about sections sees exactly what it saw. Rejected an ordinal in unit_id to disambiguate identical paragraphs — a positional element would shift on any neighbouring edit, so duplicates raise loudly instead. Rejected rewriting the pilot goal's scope statement; added a dated addendum so the historical record stays intact.
- Targeted verification: 5055 broad pytest; run-quality --read-only 81 passed / 0 failed; dup ratchet clean. Eleven adversarial mutations all KILLED across two rounds: fence-blindness, heading swallowed, wrong section attribution, top_level marking, end_line off-by-one, leaf-span replacement, generate ignoring granularity, public sibling split at the wrong granularity, silent duplicate-id overwrite, unknown granularity falling through, frontmatter emitted as an arm. On the real retro skill: 59 sections -> 176 units; all re-slice from disk matching content_sha256 with zero paragraph overlaps; one generated paragraph mutant removed exactly its 94 characters from both the plugin mirror and the public sibling.
- Test duplication pressure: 13 tests added to test_generate_prompt_mutants.py. The 480-line cap fired mid-slice, forcing the module split along the seam prompt_mutant_lib's own docstring already named ('pure splitter + git-plumbing helpers'); the dup ratchet then fired on the fence state machine now existing twice, which was extracted into _FenceTracker.
- Critique: Bounded fresh-eye bounded-reviewer (agent ae115722756b31f8d); boundary verified immediately, no drift. P1 was the finding that mattered and it was right: I had implemented split only, so generate rejected every paragraph unit id — the flag would have stayed a seam with no live consumer, just a wider one. Threading granularity through collect_baseline_units, mutate_unit and generate_mutants fixed that and P2 together (the public sibling was split at section granularity, so every paragraph arm would have silently reported public_mutated: False and left the text readable in the captured workspace). Also applied: P3 duplicate unit ids now raise instead of silently overwriting; P4 split_units validates granularity itself rather than trusting build_split_manifest; P5 heading_path is copied rather than shared by reference; P6 YAML frontmatter is excluded (removing it breaks registration, so the arm reads as a strong DETECTED while proving nothing); P7 stale 'section-level' prose in three places; P8 __all__ narrowed to exactly the re-exported splitter names. The reviewer independently cleared the fence, leaf-span, and _FenceTracker edge cases.
- Off-goal findings: none this slice
- Lessons carried forward: Implementing the producing half and calling the feature done is the same shape as a test that asserts a proxy — split minted ids that the next stage rejected, and every local gate was green. The reviewer question that caught it was 'is the paragraph unit safe to actually apply', which forced tracing past the boundary I had changed.
- Metrics:

## Context Sources

- Source: handoff entry #5 (#453: Mutation test regression on main) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #3 (Budgets were retuned for `local-linux-x86_64-36cpu` only; aarch64 and the unprofiled defaults were left alone) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #2 (Residuals, not closed: `issue_close_comment_floor) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #1 (Sweep for other built-with-intent-but-unused modes and options) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `scripts/agent-runtime/skill-test-telemetry.mjs`
- Cited path: `scripts/check_python_lengths.py`
- Cited path: `scripts/check_skill_contracts.py`
- Cited path: `scripts/eval_registry.py`
- Cited path: `scripts/quality_policy_defaults.py`
- Cited path: `skills/public/achieve/scripts/init_adapter.py`
- Cited path: `skills/public/debug/scripts/init_adapter.py`
- Cited path: `skills/public/issue/scripts/issue_close_comment_floor.py`
- Cited path: `skills/public/issue/scripts/issue_verify_closeout_body.py`
- Cited path: `skills/public/quality/references/mutation-testing.md`
- Cited path: `skills/public/quality/scripts/check_runtime_budget.py`
- Cited path: `skills/public/quality/scripts/propose_mutation_testing.py`
- Cited path: `skills/public/quality/scripts/runtime_budget_lib.py`
- Cited path: `skills/public/retro/scripts/probe_host_logs.py`
- Cited path: `skills/public/setup/scripts/seed_t_events_adapter.py`
- Cited path: `specdown.json`
- Cited path: `tests/quality_gates/test_achieve_adapter_policy.py`
- Cited path: `tests/quality_gates/test_packaging_validation.py`
- Cited path: `tests/quality_gates/test_profile_and_preset_validation.py`
- Cited path: `tests/quality_gates/test_retro_host_log_probe.py`
- Cited path: `tests/quality_gates/test_seed_t_events_adapter.py`
- Cited path: `tests/test_adapter_shim_inprocess_coverage.py`
- Cited path: `tests/test_cautilus_eval_commands.py`
- Cited issue: #453

## Interview Decisions

- **Which backlog chunk(s):** family considered — the four ranked chunks from the
  handoff chunked-routing pass. Chosen: the 1-3 span (mutation regression + budget
  follow-through, closeout residuals, unused-mode sweep), in ranked order. Rejected:
  chunk 4 (deferred backlog) — nothing blocks on it and the sweep may reframe parts
  of it. `single-point: the operator selected the span explicitly from the rendered
  ranking; not a system axis.`
- **#453 close authority:** family considered — agent closes via the `issue` skill
  vs operator closes. Chosen: operator closes; agent posts evidence only. Rejected:
  agent close — the north star treats issue close as an irreversible boundary where
  a terminal green is not sufficient proof, and the mutation workflow was already
  changed to stop auto-closing. `single-point: a repo-wide policy boundary, not a
  per-host or per-profile value.`
- **Sweep deletion authority:** family considered — delete-on-evidence in-run,
  report-then-sign-off, or inventory-only-with-follow-up-issues. Chosen:
  report-then-sign-off. Rejected: in-run deletion (unbounded blast radius across
  skills) and inventory-only (drops the operator's decision loop). `single-point:
  a scope decision for this run.`
- **`issue_close_comment_floor` check scope:** family considered — wire all three
  omitted checks, wire provenance + ledger fields, or wire provenance only.
  Chosen: provenance only, with the other two recorded as intentionally not wired.
  Rejected: close-keyword (needs a repo slug the floor's signature never receives,
  is inert inside a comment on GitHub, and contradicts this goal's own no-close-
  keyword stance) and ledger fields (needs a new public wrapper around a private
  helper for unclear benefit). `single-point: a per-carrier applicability call for
  the close-with-comment path, not a system axis.`
- **Slice 4 outcome policy:** family considered — close-and-leave-the-slot-empty,
  add a regression guard instead, or re-ask at reproduce time. Chosen: close and
  leave empty if the churn does not reproduce. Rejected: a regression guard for a
  bug that may no longer exist. `single-point: a scope call for this run.`
- **Sweep surface scope:** family considered — flags/enums only, public skills
  only, or all four surface families. Chosen: all four (adapter enum fields,
  planner branches, `--mode`/`--part` flags, preset variants). Rejected: the
  narrower options — the one confirmed instance (`retro`'s `weekly`) lived in a
  planner branch, so a flags-only sweep would have missed the very case that
  motivated the request. `axis: surface family. The sweep is defined across the
  family, not anchored to the one instance already found.`
- **Timebox:** family considered — no timebox, ~2h, ~4h. Chosen: none. Rejected:
  the timeboxed variants — the operator wants the span finished, not clipped.
  `single-point: this run's work budget.`
- **Chunk 1's budget half:** the handoff bundled "#453" with "act on aarch64/
  unprofiled SLACK lines", but that half has no runnable content from this machine
  (zero slack findings, one sampled profile). Surfaced to the operator during the
  Before-phase discussion and left as a queue item rather than a slice; chunk 1 is
  effectively #453 alone. `single-point: a data-availability fact about this
  machine, revisited when aarch64 signals exist.`
- **Slice 2 retention:** the 7 survived mutants are score hygiene, not #453's
  blocker, so they could have been dropped. Kept: two tests close them and they
  would resurface on the next scheduled run. Raised with the operator and not
  objected to. `single-point: a cost/benefit call for this run.`
- **Runtime budget values:** `axis: runtime profile.` Budgets already vary per
  machine profile in `.agents/quality-adapter.yaml`
  (`local-linux-x86_64-36cpu`, `local-linux-aarch64-4cpu`, `default`). This run
  touches none of them; the x86_64 numbers observed here must not be promoted to a
  global default, which is exactly why the aarch64/default retune stays queued for
  evidence from that hardware rather than being extrapolated.
- **Mutation verdict authority:** `axis: execution environment (local vs CI).` The
  local scoped mutation run is evidence, not the verdict; CI owns the gate result.

## Plan Critique Findings

Reviewer provenance: bounded read-only fresh-eye `bounded-reviewer` subagent
(parent-delegated, agent `a48335f5a241f4372`), 2026-07-25, on the shaped draft
before activation. Parent proved worktree+index integrity around the review with
`reviewer_boundary_fingerprint.py` snapshot/verify (`ok: true`, no drift). The
reviewer reported its envelope as **envelope-unbound**: Bash/Edit/Write/Agent were
absent for the spawn, so read-only was honored as instruction and no writes were
attempted. Every finding below was independently re-verified by the parent against
the cited files before folding.

Blockers folded:

- **F1 — wrong proof instrument (folded into Agent Verification Plan, slice 1).**
  The plan called for a "scoped mutation pass" over the changed-line targets. The
  blocker is computed from a coverage report *before* any mutant runs
  (`scripts/mutation_changed_files_lib.py:34-62`) and the score path already
  passed, so mutants prove the wrong thing at high cost. Replaced with
  `run_slice_closeout.py --produce-mutation-coverage` +
  `check_changed_line_mutation_coverage.py --base-sha ... --head-sha ...`.
- **F2 — false-proof class (folded into User Acceptance and the decision queue).**
  "Operator re-runs the mutation gate and sees PASS" is the named
  `workflow_dispatch` false proof: only `schedule` events compute `base_sha`
  (`skills/public/quality/references/mutation-testing.md:305-315`), so a dispatch
  run leaves the changed-line classifier inert. Now requires the next scheduled
  run plus `check_mutation_run_proof.py --claim changed-line`.
- **F3 — slice 4 rested on a false premise (folded into the Slice Plan).** The
  plan claimed the owning surface uses `-no-report` so another invocation must be
  the culprit; in fact both the runner (`scripts/run-quality.sh:523`) and
  `.agents/surfaces.json:695` already write to a temp dir, and `-quiet -no-report`
  were *removed* on 2026-07-22 because specdown rejects them
  (`charness-artifacts/debug/2026-07-22-debug-review.md:15-22`). Slice 4 now starts
  with a reproduce step and closes the residual as already-fixed if it is clean.

Should-fix folded:

- **F4** — the acceptance criterion was unmeetable as written: the checked-in
  report is manually-refreshed derived state whose timing metadata means it can
  never no-op (`.agents/surfaces.json:697-699`). Scoped to the automated gate.
- **F5** — Boundaries listed no `plugins/charness/**` path though slices 3 and 5
  both touch mirrored files; mirror + sync-before-validators added.
- **F6** — "plugin-copy fresh-install render path" named no file or command; slice
  5 now names `propose_mutation_testing.py --execute` rendering
  `templates/mutation-tests.yml`, written once at first install and never
  re-rendered.
- **F7** — slice 3 treated three unlike omissions as one. `evaluate_ai_provenance`
  is a clean gap; close-keyword needs a repo slug `evaluate_close_comment_floor`
  never receives and is inert inside a comment anyway; ledger fields need a new
  public wrapper. Objective now allows "intentionally not wired, with reason" as a
  passing outcome.
- **F8** — `com/corca-ai/charness/actions/runs/` was a URL fragment auto-extracted
  as a repo path; removed from Boundaries and Context Sources.
- **F9** — `check-coverage` is a whole-repo runner label, not a file-scoped
  command; replaced with the targeted pytest plus the F1 gate.
- **F10** — added the coverage-collection trap: a bare `coverage run -m pytest`
  misreports subprocess-invoked CLI scripts as 0%, exactly the shape of
  `quality_policy_defaults.py`.
- **F11** — slice 2 was coupled to the #453 closeout though the 7 survivors are in
  the score path, which passed. Decoupled: the closeout comment goes out after
  slice 1. Slice 2 also now cites the raw-output assertion rule for format mutants.
- **F12** — closeout obligations (handoff entry retirement, artifact commits,
  mandatory critique) were unstated; added to the Agent Verification Plan.

Over-worry raised but not folded (counterweight pass):

- The reviewer explicitly confirmed the aarch64/unprofiled deferral is honest, not
  an excuse: `runtime-signals.json` carries exactly one profile key and
  `runtime_budget_lib.evaluate` marks unsampled labels `no-sample` rather than
  fabricating slack. Left as written.
- The parent's own worry that "uncovered changed lines" might mean "uncovered by
  the *selected mutation nodeids*" was checked and refuted
  (`scripts/sample_mutation_files.py:214`) — coverage is taken from the broad test
  command before selection, so slice 1's "add real tests" premise survives.
- The #453-close-authority and sweep-report-first decisions were reviewed against
  the north-star irreversible-boundary rule and need no revisiting.

## Off-Goal Findings

- **A shipped bug, found by slice 5 and fixed in it:** `propose_mutation_testing.py`
  could not reach its workflow template from the plugin copy, in every tag back to at
  least `v2.2.1`. Fixed here; the *release* decision is queued for the operator.
- **From the sweep, not acted on** (recorded in
  [the sweep artifact](../audit/2026-07-25-unused-mode-option-sweep.md)): critique
  packets hardcode `high-leverage` while agents record `Requested tier: medium`, making
  those artifacts self-contradictory; and `presets/specdown-quality.md` duplicates
  `DEFAULT_SPECDOWN_SMOKE_PATTERNS` verbatim with no drift gate.
- **Nine confirmed unused options** awaiting operator sign-off; zero deleted.

## Coordination Cues

Routing: impl + prove — selected from installed skill metadata for the six slices;
each slice ran mutate -> sync -> verify with `run_slice_closeout.py` as the pre-commit
aggregate. `critique` owned the five bounded fresh-eye reviews, `debug`-class root-cause
work ran inline inside slices 4 and 5, `quality` gates ran via the closeout aggregate,
`retro` owned the closeout review, and `handoff` chunked routing produced this goal.

Gather: n/a — no external URL or published source became working context for this
goal; every input was repo-local or a GitHub issue already in the backlog.

Release: n/a — this goal's Non-Goals exclude a release and none was cut. Slice 5 found
a bug present in published tags and recorded a correction in the v2.5.0 notes; whether
to ship a patch release is queued as an operator decision rather than taken here.

Issue closeout: n/a — #453 is deliberately left open for the operator's own close per
their Before-phase decision; this run posted evidence only and used no close keyword.

## Final Verification

- Six commits, each gated: `c846dc26`, `5a31ca81`, `7b710a85`, `3b0750a6`, `c92e9561`,
  `90d197d2`. Full `./scripts/run-quality.sh --read-only` green (81 passed, 0 failed)
  after slices 4 and 5, with `.charness/specdown/` clean afterwards — the fix's own
  acceptance criterion.
- #453's four changed-line targets verified COVERED via the gate's own coverage harness,
  each individually mutated and confirmed killed.
- Every new guard this session was adversarially verified by reintroducing the exact
  defect it guards against and confirming failure.
Retro: charness-artifacts/retro/2026-07-25-session-retro.md

Host log probe: charness-artifacts/retro/2026-07-25-session-retro.md

Disposition review: charness-artifacts/retro/2026-07-25-session-retro.md

**Non-claims.** No CI mutation run was executed for the #453 fix; confirmation requires
the next *scheduled* run (a `workflow_dispatch` re-run cannot prove a changed-line fix).
No consumer-repo install was exercised against a real published plugin — slice 5's proof
runs the checked-in plugin copy, which is the same artifact but not a fetched release.
The sweep is static: it cannot see runtime usage of the published portable contracts it
names. The aarch64 and unprofiled runtime budgets were not touched; this machine has no
samples for them.

## User Verification Instructions

1. `git log --oneline -6` — the six slice commits.
2. `./scripts/run-quality.sh --read-only` then `git status --short .charness/specdown/`
   — expect 81 passed / 0 failed and an empty status. Before this run the second command
   printed `M .charness/specdown/report.json` every time.
3. `python3 -m pytest -q tests/quality_gates/test_mutation_workflow_install.py` — the
   fresh-install render path that was broken since v2.2.1.
4. Read [the sweep inventory](../audit/2026-07-25-unused-mode-option-sweep.md) and decide
   which of the nine confirmed candidates to delete.
5. Decide the two queued boundaries: the patch release, and closing #453 after the next
   scheduled mutation run.

## Auto-Retro

Retro: charness-artifacts/retro/2026-07-25-session-retro.md

Retro dispositions: applied: mutation-verification loops restore from a pristine copy and assert a green baseline before each mutation, replacing `git checkout --`, which reverts uncommitted work to HEAD and makes every mutant look killed

Retro dispositions: applied: `scripts/check_export_safe_imports.py` extended from import syntax to filesystem paths, closing the class that shipped the plugin-copy bug; it immediately found four more dead constants of the same shape, now deleted

Retro dispositions: applied: the seeded-harness drift guard now sees repo scripts invoked from `bash -c` gates, the blind spot that let slice 4's harness seeding be forgotten

Retro dispositions: applied: two source-guard tests rewritten to observe the property they are named after rather than a proxy string, both adversarially verified against a reintroduced defect

Retro dispositions: out-of-scope: the two sweep-adjacent findings (critique packet tier propagation, specdown preset duplication) belong to their own surfaces rather than this goal; both are recorded in the sweep artifact and carried to the handoff

Structural follow-up: repo-local guard: charness-artifacts/retro/2026-07-25-session-retro.md
(the `## Sibling Search` section records the per-axis decisions; the one
`valid follow-up outside the slice` axis — a per-test read of the remaining
repo-file-grepping tests — is anchored to the handoff rather than left unowned).
