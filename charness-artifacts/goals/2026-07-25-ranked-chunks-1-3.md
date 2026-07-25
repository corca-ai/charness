# Achieve Goal: Run ranked chunks 1-3 in sequence: (1) close #453 by covering the uncovered changed lines in quality_policy_defaults.py and runtime_budget_lib.py and killing the probe_host_logs.py survived mutants, plus act on the aarch64/unprofiled budget SLACK advisories; (2) close the named residuals - issue_close_comment_floor.py omitted checks, specdown.json hardcoded outFile churn, untested plugin-copy fresh-install render path; (3) sweep for other built-with-intent-but-unused modes and options and delete or justify each on usage evidence.

Status: active
Created: 2026-07-25
Activation: `/goal @charness-artifacts/goals/2026-07-25-ranked-chunks-1-3.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: real draft awaiting activation — shaped and plan-critiqued
  2026-07-25, consequential discussion resolved with the operator, not stale.
- Current slice: slices 1-2 done. Slice 3 is next.
- Next action: slice 3 — wire `evaluate_ai_provenance` into
  `issue_close_comment_floor.py`, record close-keyword and ledger-field as
  intentionally not wired with reasons.
- Standing hazard (learned in slice 2): never restore a mutation-test target with
  `git checkout -- <path>` while the slice is uncommitted; it reverts to HEAD and
  silently discards the work being proven. Use a pristine `cp` copy and assert a
  green baseline before each mutation.
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
| 3 | Wire `evaluate_ai_provenance` into `issue_close_comment_floor.py`; record close-keyword and ledger-field as intentionally not wired, with reasons, and close the residual | Operator decision 2026-07-25: only the provenance check is a genuine gap for the close-with-comment carrier. Close-keyword needs a repo slug `evaluate_close_comment_floor` never receives and is inert inside a comment; ledger fields would need a new public wrapper for unclear benefit | Test that fails with the provenance check removed; the two not-wired rationales recorded in the floor's own docstring/reference so the residual does not return a third time; quality read-only green | planned |
| 4 | Reproduce the tracked-specdown-report churn first, then act | Both the runner (`scripts/run-quality.sh:523`) and the owning surface already write to a temp dir, and `-quiet -no-report` was removed on 2026-07-22 because specdown rejects them — the residual may already be closed | Step 0: full quality gate, then `git status --short .charness/specdown/`. If clean: record "already fixed by the 2026-07-22 change" with the evidence and **stop — do not backfill the slot** (operator decision 2026-07-25; no regression guard, no substitute work). Only debug further if it reproduces | planned |
| 5 | Test the fresh-install render path: from a plugin copy, `propose_mutation_testing.py --execute` renders `templates/mutation-tests.yml` into `workflow_path` | Sole delivery path — the workflow is written once at first install, never re-rendered, and `--execute` refuses to overwrite | Test over a fresh temp repo asserting rendered workflow content including `schedule_cron` substitution | planned |
| 6 | Sweep all four surface families for built-with-intent-but-unused modes/options; emit a candidate inventory with usage evidence | Standing operator request; safest once the gate is trustworthy. Scope confirmed 2026-07-25: (a) adapter enum fields, (b) planner branches, (c) `--mode`/`--part` style flags, (d) preset variants — not flags-only, because the `retro` `weekly` instance lived in a planner branch | Audit artifact under `charness-artifacts/audit/` listing each candidate with its usage evidence (artifact counts, git history) and the branch-arms-produce-the-same-plan test result; zero deletions | planned |

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

- Decision: which swept unused modes/options to delete
- Owner: operator
- Why deferred: the operator chose report-first; deletions at repo scale are the
  change class most likely to be wrong without a human read
- Unblock action: read the slice 6 audit artifact and name the candidates to delete
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

## Final Verification

## User Verification Instructions

## Auto-Retro
