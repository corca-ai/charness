# Quality Review
Date: 2026-06-25

## Scope

Target boundary: repo-wide quality slice for agent-facing inventory output
efficiency, focused on `inventory_skill_ergonomics.py` summary output.

Ambient repo findings: existing Python near-limit warnings, stale changed-line
coverage before commit, and the HITL/narrative doc-duplicate advisory are not
caused by this slice. Per operator direction, manual `nose` latest checks are
not part of this loop.

## Current Gates

- Focused pytest passed 16 tests across skill-ergonomics and standing-test
  economics summary contracts.
- Changed-surface validators passed for packaging, skills, dogfood,
  inference-interpretation, gitignore scan hygiene, boundary-bypass, ruff, and
  plugin mirror sync.
- Broad `./scripts/run-quality.sh --read-only` passed 79/79 after this slice.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`;
  profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 32.8s latest / 26.6s median, budget 140.0s;
  `check-coverage` 18.7s latest / 19.0s median, budget 55.0s.
- coverage gate: broad read-only gate passed; changed-line coverage remains
  pre-commit stale until the locked closeout producer refreshes it.
- evaluator depth: deterministic gates only. No Cautilus run was in scope
  because this changed inventory serialization, not prompt behavior.

## Healthy

- `inventory_skill_ergonomics.py --summary-yaml` now emits the same compact
  payload as `--summary`, preserving full `--json` attribution behavior.
- On this checkout, skill-ergonomics compact summary measured 12,201 bytes as
  JSON and 9,392 bytes as YAML, a 23% serialized-byte reduction.
- Shared `summary_output_lib.py` owns YAML dumping and summary emission for the
  two YAML-enabled quality inventories, reducing helper drift.
- Plugin export is synced; public and plugin quality scripts are byte-identical
  for the changed helper surfaces.

## Weak

- The efficiency proof measures serialized bytes, not tokenizer-specific token
  counts. It is a useful proxy for agent context size, not a tokenizer claim.
- Missing PyYAML behavior is covered through the helper seam, not a subprocess
  CLI invocation. That is adequate for this small branch, but weaker than an
  end-to-end import-failure CLI proof.

## Missing

- No active missing deterministic gate is justified by this slice. Existing
  validators cover inventory declaration, interpretation pairing, packaging, and
  exported plugin sync.

## Deferred

- Other agent-facing inventory summaries remain candidates for YAML only when
  a measured payload shows meaningful serialized-byte savings.
- Tokenizer-specific measurement is deferred until a repo-owned tokenizer seam
  exists; byte comparison remains the portable local proxy for now.

## Advisory

- structural review result: command:
  `plan_quality_run.py --repo-root . --json`; planner required runtime and
  skill-ergonomics evidence, and the next structural move was a compact
  consumer-facing output mode rather than weakening any standing gate.
- prose review result: command:
  `inventory_skill_ergonomics.py --repo-root . --summary-yaml`; summary engages
  `checked_skill_count`, `heuristic_finding_count`, `subcheck_counts`, and
  `prose_review_status=required` through `skills_with_heuristics` without full
  per-finding payload expansion.
- test-economics review result: command:
  `inventory_standing_test_economics.py --repo-root . --summary-yaml`; this
  slice did not change standing test scope, but the inventory still reports
  `test_file_count=332`, `nested_cli_file_count=150`, and
  `nested_cli_standing_or_mixed_file_count=146`.
- runtime interpretation: command:
  `render_runtime_summary.py --repo-root . --json`; current hot spots remain
  within budget, so this loop improved review-output cost rather than reducing
  test proof.
- dup-ratchet interpretation: command:
  `inventory_nose_clones.py --repo-root . --write-baseline` and
  `check_dup_ratchet.py --repo-root . --write-baseline`; helper extraction
  removed the new YAML helper clone, then both code duplicate baselines accepted
  remaining line-offset family-id rotations in existing inventory boilerplate.
- public-skill dogfood result: command:
  `suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`;
  the existing quality case is `hitl-recommended` and still covers slow-gate,
  structural-review, runtime-budget, and durable-artifact consumer behavior.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019efea7-7720-7c61-a060-198f52d45a05` found no blockers, confirmed JSON/full
  inventory behavior and plugin mirror sync, and warned that the compactness
  proof is byte-sized rather than tokenizer-measured.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed via runtime hot spots, broad read-only gate
  output, and dup-ratchet family attribution; no test-removal change was made.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary[,-yaml]`
- `pytest -q tests/quality_gates/test_quality_skill_ergonomics_summary.py tests/quality_gates/test_standing_test_economics.py`
- `ruff check skills/public/quality/scripts/inventory_skill_ergonomics.py skills/public/quality/scripts/inventory_standing_test_economics.py skills/public/quality/scripts/summary_output_lib.py tests/quality_gates/test_quality_skill_ergonomics_summary.py tests/quality_gates/test_standing_test_economics.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing`
- `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- active none — this slice extends an existing compact summary contract and
  shares helper code without adding a low-noise blocking invariant.
- passive convert more agent-facing summaries to YAML because byte measurement
  must show material savings while JSON remains the stable machine contract.
- passive add tokenizer-specific measurement until a repo-owned tokenizer seam
  exists, because byte size is only a portable proxy for token efficiency.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
