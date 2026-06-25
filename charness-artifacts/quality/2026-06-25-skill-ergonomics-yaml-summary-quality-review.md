# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repo-wide quality slice for script execution speed and
agent-facing token efficiency, focused on prompt-bulk inventory output and
runtime-hotspot ranking fidelity.

Ambient repo findings: the HITL/narrative doc-duplicate advisory, Python
near-limit warnings, and standing nested-CLI test backlog are pre-existing
quality signals, not fixed by this slice.

## Current Gates

- Focused pytest passed 32 tests across runtime-budget rendering and prompt-bulk
  inventory contracts; `ruff` passed on changed Python; plugin export was synced.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: after stale filtering, `run-quality-read-only` 38.1s latest
  / 65.7s median, budget 90.0s; `pytest` 25.1s latest / 26.6s median, budget
  140.0s; `check-coverage` 18.4s latest / 18.9s median, budget 55.0s.
- stale runtime hot spots excluded: `check-duplicates` latest sample
  2026-06-04T12:11:36Z, plus three older retired labels.
- coverage gate: focused tests passed; final broad read-only gate pending at
  artifact draft time.
- evaluator depth: deterministic gates only. No live Cautilus run was in scope
  because this changed helper/report mechanics, not maintained scenario
  behavior.

## Healthy

- `find_inline_prompt_bulk.py --from-adapter --summary` now uses quality adapter
  prompt globs and emits `finding_count` plus a bounded sample, avoiding plugin
  mirror scans and full findings payloads.
- Measured on this checkout: default full JSON was 108,061 bytes and 2.387s;
  adapter-backed summary was 4,736 bytes and 1.585s.
- Runtime hotspot ranking excludes samples older than 14 days from active
  priority, preserves them under `stale_runtime_hotspots`, and names stale-only
  markdown instead of implying absent samples.

## Weak

- Byte size is only a proxy for token efficiency; no tokenizer count was run.
- Runtime freshness prevents stale label ranking, but it is not a cleanup policy.
- The standing boundary-bypass backlog remains: the ratchet prevents growth but
  does not reduce existing subprocess fanout.

## Missing

- Missing before this slice: runtime hotspot ranking had no stale/retired-label
  filter, so obsolete `check-duplicates` samples still looked actionable.
- No new deterministic gate is justified for prompt-bulk output size; the helper
  now exposes the lower-cost path directly.

## Deferred

- Convert one import-safe nested-CLI cluster to in-process tests separately.
- Tokenizer-specific measurement stays deferred until a stable tokenizer seam exists.

## Advisory

- structural review result: command:
  `plan_quality_run.py --repo-root . --json`; planner required runtime summary,
  skill ergonomics, and broad quality evidence, and the structural move was to
  reduce inventory/report noise and stale-ranking false priorities.
- prose review result: artifact:
  `skills/public/quality/references/prompt-asset-policy.md`; it now names the
  preferred `--from-adapter --summary` path so future quality runs do not
  rediscover the low-token invocation manually.
- doc-duplicates advisory: command:
  `./scripts/run-quality.sh --read-only`; HITL/narrative bootstrap similarity is
  retained as review material, not a blocker for this slice.
- Python length advisory: command:
  `./scripts/run-quality.sh --read-only`; 10 warn-band files remain, to trim only
  when touching the owning surface.
- skill-ergonomics inventory result: command:
  `inventory_skill_ergonomics.py --repo-root . --json`;
  `scope_status=scanned`, `prose_review_status=required`, and
  `heuristic_finding_count=17` mean the host-surface portability hits remain
  judgment prompts, not this slice's target.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333` and `nested_cli_standing_or_mixed_file_count=147` support
  the deferred in-process conversion recommendation.
- dup-ratchet interpretation: command:
  `check_dup_ratchet.py --repo-root . --write-baseline` and
  `inventory_nose_clones.py --repo-root . --write-baseline --json`; the seven
  blocked code family ids were reviewed as line-offset rotations in touched
  duplicate-member files, so the gate and advisory id-set baselines were
  deliberately refreshed together.
- quality dogfood decision: command:
  `suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`;
  existing `hitl-recommended` case covers runtime/test-speed review, so no
  scenario-registry change is needed for this helper/report mechanics slice.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f00b7-d116-7c80-a606-847fe69bb0d7` recommended fixing stale/noisy quality
  signals first and called prompt-bulk adapter summary the same low-risk slice.
- Critique fresh-eye reviewers `019f00c6-f822-70c0-9958-82dbbdf48234`,
  `019f00c7-0fff-7540-ab6f-c45d0cb5ceb5`, and
  `019f00c7-2b33-7742-b130-8e32f8b2cc1d` found stale-only markdown and paired
  baseline gaps; both were fixed.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed at inventory level; no test-removal change was
  made in this slice.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `./scripts/run-quality.sh --read-only`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- inventory scripts: skill ergonomics, standing test economics, standing gate verbosity
- `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --json`
- `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --from-adapter --summary`
- command: python3 -m pytest -q tests/quality_gates/test_runtime_budget_gate.py tests/test_find_inline_prompt_bulk.py
- `ruff check skills/public/quality/scripts/runtime_budget_lib.py skills/public/quality/scripts/render_runtime_summary.py skills/public/quality/references/find_inline_prompt_bulk.py tests/quality_gates/test_runtime_budget_gate.py tests/test_find_inline_prompt_bulk.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline`
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Recommended Next Gates

- active none — this slice fixes quality-signal mechanics with focused tests.
- passive convert one nested-CLI cluster to in-process proof because standing
  pytest still pays broad subprocess fanout and the current ratchet only prevents
  growth.
- passive add tokenizer-specific token measurement until a stable repo-owned
  tokenizer seam exists, because byte size is only a portable proxy.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
