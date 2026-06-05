# Quality Review
Date: 2026-06-03

## Scope

User-requested rigorous quality pass ("빡세게 검토해서 개선사항 전부 적용") on a clean
`main` after the 0.15.0 release and the #281/#184 closeouts. Re-derived the
gate/source surface, ran the existing gates, inspected the four lenses, and
implemented the concrete fix found instead of only reporting it. The live
wrong-boundary suspect was the open mutation regression #283 on newly added
Codex session/token reporter code — a test-confidence gap inside an existing
gate, not concept/architecture drift — treated here as the primary gap.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed before and after the change:
  68 → 69 gates, 0 failed, 51.4s; the +1 is the new tokens unit-test module
  joining the standing pytest target.
- Touched-surface tests pass: `test_codex_session_audit_tokens.py` (16, new) and
  `test_retro_codex_session_audit.py` (9, +3). `ruff` clean. No production source
  changed, so the packaging mirror stays in sync (no tests mirror under `plugins/`).

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`;
  profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `check-coverage` 42.2s latest / 41.7s median, budget 45.0s;
  `pytest` 26.7s latest / 23.5s median, budget 140.0s; `check-duplicates`
  11.0s latest / 10.8s median, budget 11.0s.
- coverage gate: `run-quality --read-only` passed (69 passed, 0 failed).
- evaluator depth: no live Cautilus run; proof was deterministic gates, targeted
  local cosmic-ray on the two #283 files, and a bounded fresh-eye reviewer.

## Standing Test Economics

- `inventory_standing_test_economics.py`: `test_file_count`=231 (188 on 2026-05-24)
  and `nested_cli_file_count`=104 (was 81); the trend continues. This pass adds one
  small pure-function unit module by design and does not widen the slow release-only
  CLI lifecycle surface, the real economics watch item.

## Coverage and Eval Depth

- Root cause of #283: the pure functions in `scripts/codex_session_audit_tokens.py` had only a loose end-to-end consumer test, so the sampler saw nearly every numeric/comparison/boolean mutant survive. Fix is structural — direct unit tests pin each branch and constant, so coverage-based selection now picks tight killers.
- Local cosmic-ray on `codex_session_audit_tokens.py`: survivors 23 → 12 (killed 49 → 60). All 12 residual are equivalent: 11 are `|` on the `str | None` annotation (skipped by `filter_cosmic_ray_mutants.py`), 1 is `Eq_GtE` on the bool parse (equivalent for the `{true,false}` regex domain).
- Local cosmic-ray on `audit_codex_session.py` `main`: survivors 6 → 4 after routing + non-ASCII tests. The 4 residual are equivalent/cosmetic (`Eq_GtE` on the `{json,markdown}` argparse domain, `indent` ×2, `sort_keys`). The `run_session_jsonl`/`parse_args` survivors in the unfiltered local run are coverage-filter artifacts (uncovered lines the gate skips), not a new gap.

## Enforcement Triage

- `AUTO_EXISTING`: read-only quality, packaging, current-pointer freshness,
  inventory-consumption, secrets/supply-chain, runtime budgets, and the scheduled
  mutation gate (`mutation-tests.yml`, owner of #283).
- `AUTO_CANDIDATE`: none — the fix is coverage the existing mutation gate owns.
- `NON_AUTOMATABLE`: residual equivalent/cosmetic mutants; chasing them needs
  brittle byte-exact output guards the quality contract discourages.

## Healthy

- #283 surface: all behaviorally-meaningful mutants in `token_summary`,
  `aggregate_tokens`, `cost_signal_status`, and audit `main` routing are now
  killed; only equivalent mutants remain (cosmic-ray verified).
- `inventory_lint_ignores.py`: 85 suppressions, `blanket`=0, `codes` dominated by
  E402 (post-bootstrap import order), all `scope`=inline; zero new this pass.
- `inventory_skill_ergonomics.py`: `checked_skill_count`=23,
  `heuristic_finding_count`=0, `prose_review_status`=still_required.
- prose review result: no trigger overlap, undertrigger, mode/option pressure, or
  repeated-prose-ritual smell found; the skill surface is healthy.
- `inventory_public_spec_quality.py`: 4 specs, `source_guard_row_count`=0,
  `executable_block_count` 1–3 per spec — no brittle source guards, no duplicated
  proof. CLI ergonomics and standing-gate verbosity inventories also scanned clean.

## Weak

- Standing test economics keeps rising (231 test files / 104 nested-CLI); the
  slow release-only CLI lifecycle tail is untouched this pass.
- Three files sit in the advisory file-length warn band (see Advisory).

## Missing

- No missing standing gate; #283 was a coverage gap inside an existing gate.

## Deferred

- #184 (product success metrics) deferred by design pending maintainer judgment.
- #282 (provider-safe goal closeout metrics) is a closeout/retro design item, not
  a quality-gate gap; left for its own slice.

## Advisory

- `check-python-lengths` WARN (exit 0): `check_mutation_score.py` (438),
  `setup_agent_docs_lib.py` (435), `test_release_publish_real_host_delta.py` (721)
  sit in advisory bands. Not refactored — no file has an obvious structural
  extraction win and trimming only to clear an advisory band adds risk; revisit at
  the hard limits (480/480/800).
- `pytest_temp_footprint`: local pytest temp was ~5 GiB across 5 stale sessions —
  local cache, not repo state, governed by failed-only retention.

## Delegated Review

- Delegated Review: executed. Tier requested `high-leverage` (adapter
  `reviewer_tiers` null → host default reviewer).
- One bounded fresh-eye reviewer audited the #283 fix by simulating the actual
  mutants. Verdict: solid. It confirmed the non-interned-string kills are reliable
  in CPython and `sort_keys`/`Eq_GtE` residuals are equivalent, and surfaced one
  cleanly-killable mutant I had deferred (`ensure_ascii=False` on the audit JSON
  print). Applied: a non-ASCII snippet test kills it (`main` 5 → 4, re-verified).
- Slow-gate economics lenses (fixture-economics, parallel-critical-path,
  duplicated-proof) were not separately re-delegated this pass: standing test
  economics is an unchanged advisory carry-forward, not the slice under review.

## Commands Run

- `find-skills` bootstrap routed to `quality`; quality adapter + artifact bootstrap.
- `./scripts/run-quality.sh --read-only` (×2), `ruff`, targeted `pytest`.
- `inventory_standing_test_economics.py`, `inventory_lint_ignores.py`,
  `inventory_skill_ergonomics.py`, `inventory_public_spec_quality.py`,
  `inventory_cli_ergonomics.py`, `inventory_standing_gate_verbosity.py`,
  `inventory_dual_implementation.py`, `render_runtime_summary.py`.
- Targeted `cosmic-ray init/exec/dump` on the two #283 files (before/after);
  source restored via `git checkout` after each in-place run.
- `gh issue view 283/282`, `gh issue list`.

## Recommended Next Gates

- active `AUTO_EXISTING`: let the next scheduled mutation run confirm #283 recovers
  above the 80% threshold; the auto-issue mechanism owns close/reopen.
- passive `NON_AUTOMATABLE`: continue #184/#282 because target/LLM-judge and
  provider-safe-evidence choices need maintainer product judgment, not a gate.
- passive `NON_AUTOMATABLE`: keep watching standing test economics because the next
  real win is shrinking the release-only CLI lifecycle surface, not pruning tests.

## History

- [2026-05-24 quality review](history/2026-05-24-quality-review.md)
- [2026-05-21 mutation-testability closeout](history/2026-05-21-mutation-testability-closeout.md)
