# Quality Review
Date: 2026-06-27

## Scope

Target boundary: repo-wide quality slice covering test-maintenance pressure,
`run-quality.sh` help-path startup cost, prompt-bulk inventory precision, and
dup-ratchet cleanup.

Ambient repo findings: broader nested-CLI fanout and standing `pytest` cost
remain; this slice removes one concrete near-limit test pressure point and one
prompt-inventory false-positive class instead of claiming the runtime backlog is
solved.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed: 79 phases, 0 failed, total
  39.0s.
- Focused pytest passed 23 tests across quality bootstrap split files and
  prompt-bulk inventory behavior.
- `dup-ratchet` passed after reviewing the rotated `matches_any` family as
  intentional portable helper boilerplate in `dup-review.json`.
- Packaging validation passed after `sync_root_plugin_manifests.py` refreshed
  `plugins/charness`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 22.7s latest / 23.5s median, budget 140.0s;
  `check-coverage` 5.6s latest / 5.6s median, budget 55.0s; `check-markdown`
  4.8s latest / 4.8s median, budget 11.0s; `specdown` 3.0s latest / 3.0s
  median, budget 10.5s.
- coverage gate: read-only quality gate passed; changed-line mutation coverage
  and test-completeness phases passed inside the gate.
- evaluator depth: deterministic-gates-only; Cautilus planner reported
  `next_action: none` and ask-before-run posture, so no live evaluator run was
  claimed.

## Healthy

- `tests/quality_gates/test_quality_bootstrap.py` moved out of the warn band:
  749/800 code lines before, 474/800 after; new support/test files have 585 and
  727 lines of headroom.
- `scripts/run-quality.sh --help` no longer invokes `run_standing_pytest`
  target expansion, while selected phases that need expanded targets still pass.
- Prompt-bulk inventory now excludes module/class/function docstrings and keeps
  control-flow string expressions; adapter-scoped summary dropped from 297
  findings to 53 more relevant template/content findings.
- Fresh-eye review caught the docstring-owner bug before closeout; the fix is
  covered by `test_find_inline_prompt_bulk_keeps_control_flow_string_expressions`.

## Weak

- Prompt-bulk inventory still reports checked-in templates and generated test
  fixture bodies; useful for review, not a direct token-saving verdict.
- The `matches_any` duplicate family is intentionally accepted because shared
  extraction would add import coupling for a two-line predicate across portable
  skill scripts.
- Broader `pytest` and nested-CLI fanout remain the main runtime surface; this
  slice did not alter standing proof depth.

## Missing

- No active missing gate for this slice after the read-only quality pass.
- No tokenizer-specific prompt measurement was added; prompt work here narrowed
  inventory signal rather than measuring model-token deltas.

## Deferred

- Further nested-CLI consolidation remains a later runtime slice.
- CI-backed `check-markdown` offload remains passive because it saves only about
  4.8s and does not address the dominant local proof costs.

## Advisory

- structural review result: command:
  `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`;
  target-vs-ambient split is explicit above; the
  helper-owned packet exists for quality planning and was used before mutation.
- prose review result: artifact:
  `charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md`;
  `quality` still routes correctly for this request, the
  prompt helper behavior is deterministic inventory support rather than live
  evaluator behavior, and dogfood suggestion for `quality` remains satisfied by
  the existing public-skill dogfood case.
- duplicate review result: artifact:
  `charness-artifacts/quality/dup-review.json`; family `ba16871eb91a1f15` is intentional rotated
  two-line `matches_any` helper boilerplate; extracting it would be worse than
  local copies for portable scripts.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --summary` reported
  `test_file_count=345`, `nested_cli_file_count=146`, and
  `nested_cli_standing_or_mixed_file_count=145`, so runtime debt remains in
  scope but was not solved by this slice.
- prompt inventory result: command:
  `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --from-adapter --summary --summary-limit 5` reports 53 findings after docstring exclusion.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f05c3-0863-79f0-ba5f-dbabf8a557a5` found a docstring over-exclusion bug
  and an EOF whitespace issue; both were fixed before broad verification.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not re-delegated; this slice did not recommend moving or
  weakening a slow standing gate after CI-recoverability review kept dominant
  costs local.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_ci_recoverable_gates.py --repo-root . --json`
- `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --from-adapter --summary`
- `pytest -q tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_adapter_gate_design.py tests/test_find_inline_prompt_bulk.py`
- `CHARNESS_QUALITY_LABELS=check-test-completeness ./scripts/run-quality.sh --read-only`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- active none — current deterministic gates cover this slice after the
  read-only quality pass and fresh-eye fixes.
- passive split the next broad nested-CLI or mixed test file because standing
  pytest remains the dominant local proof cost.
- passive revisit `check-markdown` local placement because CI already mirrors it
  but the savings are small until a larger runtime slice is in scope.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
