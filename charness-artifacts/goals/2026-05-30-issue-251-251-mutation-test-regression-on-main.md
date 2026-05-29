# Achieve Goal: #251: Mutation test regression on main

Status: active
Created: 2026-05-30
Activation: `/goal @charness-artifacts/goals/2026-05-30-issue-251-251-mutation-test-regression-on-main.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

#251: Mutation test regression on main

**Objective.** Make the scheduled mutation gate green again on `main`, and raise
the mutated-behavior coverage of the affected scripts so the same regression
class does not recur. Two distinct defects are bundled under #251:

1. **Blocking signal (what FAILs the gate):** three changed files were dropped
   *before* mutation because their changed lines fell below the coverage floor
   (0.85 file / mutation-line): `chunked_routing_issue_backend.py`,
   `chunked_routing_issue_source.py`, `parse_handoff_entries.py` — the chunker
   v2 + issue-source-union scripts shipped just before this run.
2. **Survived mutants (quality signal, not the failing cause):** 8 Python
   mutants survived (score 93.3% ≥ 80% threshold, so the score alone passes):
   - `aggregate_rca_ledger.py:38` `main` — `print(json.dumps(payload, indent=2))`
     (`NumberReplacer` on `indent=2`); the `--json` path of `main` is untested.
   - `chunked_routing_cli.py` `add_input_argument` / `read_pipeline_json` /
     `_fail` (lines 30/41/52/59/93/95) — shared CLI helper edges untested.

Per the Before-phase interview this goal takes the **thorough** scope: fix (1)
AND kill the (2) survived mutants. Verification is **local changed-line +
targeted-mutation proof, then a real `workflow_dispatch` mutation run as live
proof** (the full gate is CI-only/expensive; see #236).

**Source handoff entry #4: #251: Mutation test regression on main**

> <!-- corca-ai/charness-mutation-test-regression -->
> Mutation testing failed on `8a21ab1329496f37c8bd4fbccd6451c98e89916c`.
>
> Workflow run: https://github.com/corca-ai/charness/actions/runs/26640087939
>
> # Mutation Testing Summary
>
> - Status: **FAIL** (93.3% reachable score vs 80% threshold)
> - Total mutants: 188
> - Executable mutants: 119 (total minus skipped)
> - Executed: 119 (100.0% of executable total)
> - Killed: 111
> - Survived: 8
> - Scope gaps (uncovered sampled mutants): 0
> - No mutation possible: 0
> - Incompetent: 0
> - Skipped: 69
> - Blocking signal: changed lines were left test-uncovered, or eligible changed files were dropped by selection/workload budgets, before mutation.
>
> ## Survived Mutants
>
> Top definitions:
> - `main`: 2
> - `add_input_argument`: 2
> - `read_pipeline_json`: 2
> - `_fail`: 2
>
> Top operators:
> - `core/NumberReplacer`: 2
> - `core/ReplaceBinaryOperator_Mul_Div`: 2
> - `core/AddNot`: 2
> - `core/ReplaceComparisonOperator_Eq_LtE`: 1
> - `core/ReplaceFalseWithTrue`: 1
>
> Sample locations:
> - `scripts/aggregate_rca_ledger.py:38` `main` `core/NumberReplacer` - print(json.dumps(payload, indent=2))
> - `scripts/aggregate_rca_ledger.py:38` `main` `core/NumberReplacer` - print(json.dumps(payload, indent=2))
> - `skills/public/handoff/scripts/chunked_routing_cli.py:30` `add_input_argument` `core/ReplaceBinaryOperator_Mul_Div` - *,
> - `skills/public/handoff/scripts/chunked_routing_cli.py:52` `read_pipeline_json` `core/ReplaceBinaryOperator_Mul_Div` - def read_pipeline_json(input_arg: str, *, stage: str, expects: str) -> Any:
> - `skills/public/handoff/scripts/chunked_routing_cli.py:59` `read_pipeline_json` `core/ReplaceComparisonOperator_Eq_LtE` - if input_arg == "-":
> - `skills/public/handoff/scripts/chunked_routing_cli.py:41` `add_input_argument` `core/AddNot` - suffix = f" {help_text}" if help_text else ""
> - `skills/public/handoff/scripts/chunked_routing_cli.py:93` `_fail` `core/AddNot` - if hint:
> - `skills/public/handoff/scripts/chunked_routing_cli.py:95` `_fail` `core/ReplaceFalseWithTrue` - print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
>
>
> ## Changed Files Excluded Before Mutation
>
> - `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
> - `skills/public/handoff/scripts/chunked_routing_issue_source.py`
> - `skills/public/handoff/scripts/parse_handoff_entries.py`
>
> ### Uncovered changed lines
>
> - `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
> - `skills/public/handoff/scripts/chunked_routing_issue_source.py`
> - `skills/public/handoff/scripts/parse_handoff_entries.py`
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
> - Base SHA: `dc91404401251c1f5fb0935a69005a39c1418cdc`
> - Head SHA: `8a21ab1329496f37c8bd4fbccd6451c98e89916c`
> - Seed: `26640087939:dc91404401251c1f5fb0935a69005a39c1418cdc..8a21ab1329496f37c8bd4fbccd6451c98e89916c`
> - Mutation pool files: 370
> - Mutation pools: core-python 1/31 selected (210 pool), public-skill-python 4/16 selected (151 pool), support-skill-python 0/2 selected (9 pool)
> - Eligible files after coverage/mutation-line filters: 49
> - Covered eligible files: 49
> - File coverage floor: 0.85
> - Eligible files after mutation-line filter: 49
> - Executable mutant budget: 120
> - Per-file executable mutant budget: 80
> - Selected executable mutants: 119
> - Test nodeid budget: 40
> - Selected test nodeids: 38
> - Changed pool files: 8
> - Changed eligible files after coverage/mutation-line filters: 1
> - Changed files with uncovered changed lines (blocking): 3
> - Changed files excluded by coverage/mutation-line filters (advisory union): 7
> - Changed files excluded by file coverage floor: 2
> - Changed files excluded by mutation-line coverage: 5
> - Changed files excluded by selection budgets: 0
> - Selected: 5/5
> - Test command: `python3 -m pytest -q tests/quality_gates/test_runtime_budget_gate.py::test_render_runtime_summary_escalates_empty_runtime_visibility tests/quality_gates/test_runtime_budget_gate.py::test_render_runtime_summary_reports_missing_structured_signals tests/quality_gates/test_runtime_budget_gate.py::test_render_runtime_summary_uses_structured_runtime_signals tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_auto_selects_machine_profile tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_fails_on_recent_median_drift tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_fails_unknown_explicit_profile tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_fails_when_over_budget tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_has_no_visibility_findings_when_budget_and_probe_exist tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_no_budgets_passes tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_passes_when_within_budget tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_reports_advisory_ewma_without_enforcing_it tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_reports_empty_selected_profile_budget tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_reports_explicit_empty_runtime_fields tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_reports_latest_spike_without_failing tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_reports_top_runtime_hotspots tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_selects_named_profile_budget_and_samples tests/quality_gates/test_runtime_budget_gate.py::test_runtime_budget_gate_warns_on_missing_sample tests/test_cautilus_scenarios.py::test_eval_cautilus_scenarios_writes_summary tests/test_handoff_chunker_auto_draft.py::test_cli_next_step_routes_through_achieve_before_phase tests/test_handoff_chunker_auto_draft.py::test_cli_refuses_to_overwrite_existing_artifact tests/test_handoff_chunker_auto_draft.py::test_cli_writes_artifact_and_reports_check_goal_ok tests/test_handoff_chunker_cli_contract.py::test_draft_input_alias_matches_chunk 'tests/test_handoff_chunker_cli_contract.py::test_invalid_json_fails_loudly_at_reading_stage[draft_goal_from_chunk-script2]' 'tests/test_handoff_chunker_cli_contract.py::test_invalid_json_fails_loudly_at_reading_stage[prepare_ranker_packet-script1]' 'tests/test_handoff_chunker_cli_contract.py::test_invalid_json_fails_loudly_at_reading_stage[propose_merges-script0]' tests/test_handoff_chunker_cli_contract.py::test_missing_input_file_fails_loudly 'tests/test_handoff_chunker_cli_contract.py::test_prepare_input_flag_alias[--input]' 'tests/test_handoff_chunker_cli_contract.py::test_prepare_input_flag_alias[--merge-proposal]' tests/test_handoff_chunker_cli_contract.py::test_prepare_reads_stdin_by_default 'tests/test_handoff_chunker_cli_contract.py::test_propose_input_flags_are_equivalent[--entries]' 'tests/test_handoff_chunker_cli_contract.py::test_propose_input_flags_are_equivalent[--input]' 'tests/test_handoff_chunker_cli_contract.py::test_propose_input_flags_are_equivalent[-i]' tests/test_handoff_chunker_cli_contract.py::test_propose_reads_stdin_by_default tests/test_handoff_chunker_end_to_end.py::test_end_to_end_pipeline_produces_valid_goal_artifact tests/test_handoff_chunker_merge_proposer.py::test_cli_emits_proposal_from_parser_payload_stdin tests/test_handoff_chunker_ranker_packet.py::test_cli_emits_valid_packet_from_merge_proposal_stdin tests/test_rca_ledger.py::test_ac2_aggregate_rate_and_breakdown tests/test_rca_ledger.py::test_ac7_on_state_keeps_na_and_no_baseline_number`
>
> ## Changed files with uncovered changed lines (blocking)
>
> - `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
> - `skills/public/handoff/scripts/chunked_routing_issue_source.py`
> - `skills/public/handoff/scripts/parse_handoff_entries.py`
>
> ## Changed files excluded by file coverage (advisory)
>
> - `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
> - `skills/public/handoff/scripts/chunked_routing_issue_source.py`
>
> ## Changed files excluded by mutation-line coverage
>
> - `skills/public/handoff/scripts/chunked_routing_lib.py`
> - `skills/public/handoff/scripts/draft_goal_from_chunk.py`
> - `skills/public/handoff/scripts/parse_handoff_entries.py`
> - `skills/public/handoff/scripts/prepare_ranker_packet.py`
> - `skills/public/handoff/scripts/propose_merges.py`
>
> ## Changed sample
>
> - `skills/public/handoff/scripts/chunked_routing_cli.py`
>
> ## Fill sample
>
> - `skills/public/debug/scripts/init_adapter.py`
> - `skills/public/setup/scripts/init_adapter.py`
> - `scripts/aggregate_rca_ledger.py`
> - `skills/public/quality/scripts/runtime_visibility_lib.py`

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk (no #250,
  #243, real-host proof here).
- Not a rework of the mutation gate / sampler / threshold itself — `score_break:
  80` and the cosmic-ray + Stryker runner choice stay as-is. CI-only-failure
  triage policy is #236's job, not this goal's.
- Do not chase the 7 *StrykerJS* survived mutants (`skill-test-telemetry.mjs`):
  that slice already PASSes (91.9% ≥ 80%) and is not part of #251's FAIL.
- Do not retune coverage floors or selection budgets to mask the gap; fix the
  cause (missing tests), not the gate.

## Boundaries

- **Source under test (must gain coverage):**
  `skills/public/handoff/scripts/chunked_routing_issue_backend.py`,
  `skills/public/handoff/scripts/chunked_routing_issue_source.py`,
  `skills/public/handoff/scripts/parse_handoff_entries.py` (blocking trio),
  plus `skills/public/handoff/scripts/chunked_routing_cli.py` and
  `scripts/aggregate_rca_ledger.py` (survived-mutant trio of functions).
- **Test surfaces to add/extend (where edits land):** `tests/test_handoff_chunker_*.py`
  (parse / issue_source / cli_contract), and `tests/test_rca_ledger.py` for the
  `aggregate_rca_ledger.py` `--json` `main` path.
- **Verification tooling (read/run, do not redesign):** `scripts/check_coverage.py`,
  `scripts/mutation_line_coverage_lib.py`, `scripts/mutation_changed_files_lib.py`,
  `scripts/run_cosmic_ray_mutation.py`, `scripts/check_mutation_suite_score.py`,
  `.github/workflows/mutation-tests.yml`, `.agents/quality-adapter.yaml`.
- Portable per implementation-discipline: no host-specific assumption; tests
  must run under the repo's standard `pytest`.
- Stop conditions: if the uncovered changed lines cannot be reproduced locally
  (base/head drift made them no longer "changed"), name it and ask before
  guessing a target set; do not fabricate the failing range.

## User Acceptance

The user can confirm completion by:

- Seeing #251 closed with a comment that links **two** proofs (they cannot be
  one run — critique B1): a green `workflow_dispatch` full run showing the 8
  survived mutants killed and Python score ≥ 80%, **and** the local sampler
  reproduction (explicit base/head) showing **0 blocking** changed files for the
  trio. The next scheduled cron run is the async CI confirmation of the blocking
  fix.
- Running the Slice-Log–named local sampler command
  (`scripts/sample_mutation_files.py` with `MUTATION_BASE_SHA`/`HEAD`) and
  `python3 scripts/check_mutation_suite_score.py --repo-root .` and seeing them
  pass.
- Reading new/extended tests in `tests/test_handoff_chunker_*` and
  `tests/test_rca_ledger.py` that name the exact behaviors that were unmutated.

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` on the new/extended test files passes.
- **Reproduce the actual gate predicate locally** (critique B2): the blocking
  "uncovered changed lines" signal is *not* `check_coverage.py` (that is a
  whole-file floor on a fixed list, by its own docstring). The real predicate is
  `scripts/mutation_changed_files_lib.classify_changed_line_scope_gap`, driven by
  the sampler. Run `scripts/sample_mutation_files.py` with
  `MUTATION_BASE_SHA=<base> MUTATION_HEAD_SHA=<head>` set to the range that
  flags the trio (Slice 1 pins it), confirm the 3 files appear as blocking
  *before* the fix, and confirm **0 blocking changed files** after. This is the
  deterministic local stand-in for the schedule-only CI signal.
- `pre-commit` cheap gates (incl. `check_python_lengths`) pass on staged files.
  *Note: `chunked_routing_issue_source.py` is 335 lines — near the ~330 warn
  line; adding tests there should not grow the script, but watch the warn.*

### High-Confidence Checks

- **Targeted local mutation re-run** on just the 5 affected source files via
  `run_cosmic_ray_mutation.py` scoped to those files (cheaper than full): the
  8 named survived mutants are now **killed**, no new survivors introduced.
- Full repo `pytest` green (no regression from the new tests).

### External Or Live Proof

> **Critique B1 (folded):** `workflow_dispatch` computes **no `base_sha`**
> (only `schedule` does — workflow yml ~L129-146), so a dispatch run has *zero*
> changed files and the blocking "uncovered changed lines" classifier returns
> `[]`/non-blocking by construction. A green dispatch therefore proves **only
> the score/survivor path**, never the blocking-trio fix. The two defects need
> two different live proofs:

- **Score / survived-mutant fix → `workflow_dispatch` full run** of
  `mutation-tests.yml` on the fix commit: record run URL + green summary showing
  the 8 previously-survived mutants killed and score ≥ 80%. This is the honest
  live proof for defect (2).
- **Blocking-trio fix → next *scheduled* (cron) run** is the only CI path that
  re-runs the changed-line classifier. That run is asynchronous (≤3h cadence)
  and is the user's confirmation step, not a blocker for closeout. The
  deterministic proof we *can* produce now is the Low-Cost local sampler
  reproduction with explicit `MUTATION_BASE_SHA`/`HEAD` (above).
- Per Honest Proof Discipline: the After report states plainly which proofs ran.
  If the dispatch run cannot be triggered from this host, mark live proof
  not-run; **do not** claim the blocking signal is CI-proven off a dispatch run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Reproduce + locate | Must pin the exact uncovered changed lines & survived-mutant call sites before writing tests; guards against base/head drift | Concrete line list per file + mapping to functions; local coverage report showing the gap (or an explicit "no longer changed" finding) | planned |
| 2 | Cover the blocking trio | This is what FAILs the gate; greening it is the foundation | Targeted tests added; changed-line coverage for the 3 scripts ≥ floor; pytest green | planned |
| 3 | Kill the survived 8 mutants | Thorough scope chosen; raises durable mutated-behavior coverage | `aggregate_rca_ledger.py:38` killed by a **raw-stdout** assertion (`"\n  " in stdout`, not `json.loads` — critique B3, the parsed-payload test is indent-agnostic); cli helper edges pinned; targeted local mutation re-run kills all 8 | planned |
| 4 | Prove + dispatch | The CI gate is the real acceptance; close #251 on the two-proof story | `workflow_dispatch` full run URL + green summary (score/survivor path); local sampler 0-blocking reproduction (blocking path); full pytest + suite-score; #251 closed citing both + next-cron note | planned |

## Slice Log

### Slice 1: Reproduce + locate

- Objective: Pin the exact uncovered changed statement lines + survived-mutant sites before writing tests
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Faithful gate repro via run_test_coverage (parallel + COVERAGE_PROCESS_START subprocess capture) over the handoff-chunker tests; classify_changed_line_scope_gap over dc91404..8a21ab1
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Cover the blocking trio

- Objective: Add tests covering every changed statement line in issue_backend/issue_source/parse_handoff_entries so none block the gate
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Faithful gate repro: BLOCKING=(none); issue_backend 100%, issue_source 100%, parse_handoff_entries 93.2% with 0 changed&missing. 38 targeted tests pass.
- Test duplication pressure: check_duplicates: clean (no matches at 0.98 threshold); +14 test fns across 2 files; 2 small fake_load_issue_module stubs added (gate not tripped)
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Kill the 8 survived mutants

- Objective: Pin every survived-mutant behavior: aggregate indent (raw-format), cli keyword-only markers, help-suffix, ==/<= sentinel, hint branch, ensure_ascii
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Manual mutation harness applies each of the 8 mutations + runs its killing test + git-restores: 8/8 KILLED, all files restored clean. No equivalent mutants.
- Test duplication pressure: check_duplicates clean at 0.98; +11 in-process unit tests (new tests/test_handoff_chunker_cli_unit.py) + 1 rca raw-indent test
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: Local proof

- Objective: Confirm no regression and gather the deterministic local proof before outward-facing CI
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Full suite python3 -m pytest -m 'not release_only' tests: 1784 passed, 4 skipped, 57 deselected (exit 0). Trio BLOCKING=none; 8/8 mutants killed; check_duplicates clean.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- **Failing run:** GH Actions run `26640087939`; base `dc91404401251c1f5fb0935a69005a39c1418cdc`, head `8a21ab1329496f37c8bd4fbccd6451c98e89916c`. Current `main` is past that (`6a70159`), so Slice 1 must re-derive the changed-line set rather than trust the historical range.
- **Gate config:** `.agents/quality-adapter.yaml` `mutation_testing` (`score_break: 80`; full = cosmic-ray + `npm run test:mutation:js`; summary = `check_mutation_suite_score.py`); workflow `.github/workflows/mutation-tests.yml` (schedule cron `17 */3 * * *`, `workflow_dispatch`, PR=dry-run).
- **Gate contract:** [skills/public/quality/references/mutation-testing.md](../../skills/public/quality/references/mutation-testing.md) (reachable-mutant denominator; changed-files-with-uncovered-lines is a separate blocking signal from score).
- **Related backlog:** #219 (same regression class, subsumed), #236 (CI-only failure triage — the verification-cost tension this goal navigates).
- **Pre-pickup state:** [recent lessons](../retro/recent-lessons.md), [quality latest](../quality/latest.md).
- Source: handoff entry #4 (#251: Mutation test regression on main) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `com/corca-ai/charness/actions/runs/`
- Cited path: `scripts/agent-runtime/skill-test-telemetry.mjs`
- Cited path: `scripts/aggregate_rca_ledger.py`
- Cited path: `skills/public/debug/scripts/init_adapter.py`
- Cited path: `skills/public/handoff/scripts/chunked_routing_cli.py`
- Cited path: `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
- Cited path: `skills/public/handoff/scripts/chunked_routing_issue_source.py`
- Cited path: `skills/public/handoff/scripts/chunked_routing_lib.py`
- Cited path: `skills/public/handoff/scripts/draft_goal_from_chunk.py`
- Cited path: `skills/public/handoff/scripts/parse_handoff_entries.py`
- Cited path: `skills/public/handoff/scripts/prepare_ranker_packet.py`
- Cited path: `skills/public/handoff/scripts/propose_merges.py`
- Cited path: `skills/public/quality/references/mutation-testing.md`
- Cited path: `skills/public/quality/scripts/runtime_visibility_lib.py`
- Cited path: `skills/public/setup/scripts/init_adapter.py`
- Cited path: `tests/quality_gates/test_runtime_budget_gate.py`
- Cited path: `tests/test_cautilus_scenarios.py`
- Cited path: `tests/test_handoff_chunker_auto_draft.py`
- Cited path: `tests/test_handoff_chunker_cli_contract.py`
- Cited path: `tests/test_handoff_chunker_end_to_end.py`
- Cited path: `tests/test_handoff_chunker_merge_proposer.py`
- Cited path: `tests/test_handoff_chunker_ranker_packet.py`
- Cited path: `tests/test_rca_ledger.py`
- Cited issue: #251

## Interview Decisions

- **Fix scope — chose Thorough (cover blocking trio + kill 8 survived mutants)**
  over Minimal (cover the 3 blocking files only). Minimal would green the gate
  fastest since the score already passes; Thorough was chosen for durable
  mutated-behavior coverage. Rejected-alt note: `aggregate_rca_ledger.py` is
  off-chunker, so its survived mutant is broader scope than #251's trigger — kept
  in because the user chose thorough, but flagged so Slice 3 can split it if it
  balloons.
  - `axis: none` — this is a coverage-completeness choice, not a system axis.
- **Verification depth — chose Local coverage proof + CI `workflow_dispatch`**
  over local-only (no live proof the real gate is green) and full-local-run (too
  expensive for a 3-hourly gate). Live CI dispatch is the only honest proof the
  actual gate passes.
  - `axis: ci-run / push-range` — the "changed files" set is per-CI-run (base..head
    of the triggering push), not a global constant. The fix targets durable
    changed-line coverage of the scripts so *any* future range over them stays
    green, rather than reproducing one historical range.
- **Mutation threshold `score_break: 80`** — `single-point`: repo-wide value
  declared once in `.agents/quality-adapter.yaml`; not varied per host/profile.
- **Mutation runner (cosmic-ray + StrykerJS)** — `axis: runner` at the public
  quality-skill layer (stack-neutral by contract), but `single-point` for *this*
  repo, which pins both in the adapter. Not changed by this goal.

## Plan Critique Findings

Bounded fresh-eye subagent critique (general-purpose, critique discipline) run
before saving the draft. Three real blockers, all folded:

- **B1 — `workflow_dispatch` can't prove the blocking signal (folded into
  External-Or-Live + User Acceptance + Slice 4).** The "uncovered changed lines"
  classifier is driven by `base_sha`, which `mutation-tests.yml` computes only
  for `schedule` events (~L129-146); dispatch runs have zero changed files, so
  the classifier returns non-blocking by construction. A dispatch green proves
  only the score/survivor path. Split into a two-proof acceptance story; the
  blocking-trio CI proof is the next scheduled cron run (async) + the local
  sampler reproduction.
- **B2 — wrong local tool for changed-line coverage (folded into Low-Cost
  Checks).** `check_coverage.py` is a whole-file floor on a fixed list (per its
  own docstring L39-44), not the changed-line predicate. The real predicate is
  `mutation_changed_files_lib.classify_changed_line_scope_gap`, reproduced by
  running `sample_mutation_files.py` with `MUTATION_BASE_SHA`/`HEAD`.
- **B3 — the `indent=2` mutant isn't killable by a parsed-JSON test (folded into
  Slice 3).** `tests/test_rca_ledger.py` uses `json.loads`, which is
  indentation-agnostic, so the `NumberReplacer` on `indent=2` survives. Slice 3
  must assert on raw stdout formatting.

Over-worry raised but **not** folded (consciously set aside):

- Base/head "wrong invariant": `8a21ab1` is an ancestor of current `main`
  (`6a70159`) and the trio is unchanged between them, so the durable
  changed-line-coverage target (Interview Decisions, `axis: ci-run/push-range`)
  + Slice 1 re-derivation already handle it. No change.
- `aggregate_rca_ledger.py` scope creep: already flagged with a split/defer
  escape hatch; user chose thorough. Conscious.
- `chunked_routing_cli.py:30` `*,` keyword-only mutant *may* be equivalent: a
  Slice-3 note, not a plan defect; if equivalent, record it rather than chase it.
- `run_cosmic_ray_mutation.py` has no file-scoping flag (scoping is via the
  sampler rewriting `cosmic-ray.toml`): Slice 3 wording is "scoped via sampler",
  mechanically loose but achievable.

Reviewer provenance: read goal artifact; `mutation-tests.yml` (L129-151);
`sample_mutation_files.py`; `mutation_changed_files_lib.py` (L14-61);
`mutation_sample_manifest_score_lib.py`; `check_mutation_score.py`;
`run_cosmic_ray_mutation.py`; `aggregate_rca_ledger.py:30-46`;
`tests/test_rca_ledger.py:104-135`; `check_coverage.py:39-44`. Ran
`git diff 8a21ab1..6a70159` (empty over the trio) and `git merge-base
--is-ancestor` (ancestor confirmed). Did not run the mutation suite/sampler.

## Off-Goal Findings

- **Transferable mutation-survivor pattern (not filed):** other `--json` CLIs
  whose only tests do `json.loads` round-trips can hide `indent`/format mutants
  (the critique B3 / `aggregate_rca_ledger.py` smell). Recorded in the retro's
  `## Sibling Search` as a follow-up audit candidate, not filed as an issue this
  run (out of #251 scope).
- **`chunked_routing_issue_source.py` is 335 lines** — within ~5 lines of the
  ~330 soft warn. Not grown by this goal (tests only), but the next edit there
  should watch the length gate.

## Final Verification

Self-verification against the goal (Deming "study" step — measured vs predicted):

- **Defect 1 (blocking trio) — RESOLVED (local-deterministic).** Faithful gate
  repro (`run_test_coverage` subprocess-capture + `classify_changed_line_scope_gap`)
  over the failing range `dc91404..8a21ab1`: `BLOCKING: (none)`.
  issue_backend 100%, issue_source 100%, parse_handoff_entries 93.2% with 0
  changed-line gaps (was 58.3% / 72.8% / 86.4% with 15 / 44 / 4 uncovered
  changed lines).
- **Defect 2 (8 survived mutants) — KILLED (local-deterministic).** Manual
  mutation harness applied each of the 8 mutations, ran its killing test, and
  git-restored: **8/8 KILLED**, no equivalent mutants, all files restored clean.
- **No regression.** Full suite `python3 -m pytest -m 'not release_only' tests`:
  **1784 passed, 4 skipped, 57 deselected**. `check_duplicates` clean (0.98).
  Pre-push quality gate: 68 passed / 0 failed.
- **Live CI proof (score path):** `workflow_dispatch` run on fix commit
  `86ea3ea` — https://github.com/corca-ai/charness/actions/runs/26664721232
  (full mode). Result recorded at closeout.
- **Live CI proof (blocking path):** per critique B1, `workflow_dispatch` has no
  `base_sha` and cannot exercise the changed-line classifier — only the next
  **scheduled** cron run re-checks it on fixed `main`. That confirmation is
  asynchronous (≤3h) and is the user's verification step; the deterministic
  stand-in (local sampler repro above) is the proof produced now.

Retro: charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md
Host log probe: charness-artifacts/probe/2026-05-30-issue-251-mutation-coverage.json

### Residual risks & non-claims

- **NOT claimed:** that the CI gate is green for the *blocking-trio* path — that
  is proven locally and awaits the next scheduled run. A dispatch green proves
  only the score/survivor path.
- The local repro pins the historical range; the next scheduled run computes its
  own base/head. The fix targets durable changed-line coverage of the scripts,
  so any range over them stays covered — but a *different* newly-changed file
  could block a future run (a new regression, not this one).
- StrykerJS survivors (`skill-test-telemetry.mjs`) are out of scope (that slice
  passed) and untouched.

## User Verification Instructions

1. Local: `python3 -m pytest -q tests/test_handoff_chunker_issue_source.py tests/test_handoff_chunker_parse.py tests/test_handoff_chunker_cli_unit.py tests/test_rca_ledger.py` → all pass.
2. CI score path: open the `workflow_dispatch` run linked above → green summary,
   8 survivors killed, score ≥ 80%.
3. CI blocking path: the next scheduled (cron) Mutation Tests run on `main`
   should report **0** "changed files with uncovered changed lines".

## Auto-Retro

See [retro](../retro/2026-05-30-issue-251-mutation-coverage.md). Highlights:

- **Waste:** a naive `coverage run` showed parse_handoff_entries at 0% (misses
  subprocess scripts) — corrected by reproducing through the gate's own
  subprocess-capturing `run_test_coverage`; and a 1GB full-suite coverage run
  started then abandoned for the cheaper test-scoped repro.
- **Critical decisions:** faithful gate-predicate repro; plan critique before
  activation (caught B1/B2/B3); manual mutation harness for deterministic 8/8.
- **Next improvements:** repro via gate `run_test_coverage` (never naive/full
  first); a base/head changed-line-coverage helper; fold the two durable traps
  (subprocess-capture; dispatch has no base_sha) into the mutation-testing ref.
- **Sibling search:** parsed-form assertions hiding format mutants — follow-up
  audit candidate, not filed.
- RCA: one `weak_proof` event (`--source retro`, converted) for the B1 catch.
