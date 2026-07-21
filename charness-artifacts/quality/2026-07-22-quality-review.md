# Quality Review
Date: 2026-07-22
Title: Five-Pass Quality Review

## Scope

Target boundary: repository-wide quality, correctness, and runtime review across five evidence-led passes.

Ambient repo findings: existing Python length warnings, intentional portable bootstrap clones, and the prior #450 mutation-coverage freshness warning were reviewed but not widened into this repair slice.

## Current Gates

The final read-only quality run, `./scripts/run-quality.sh --read-only`, completed with 81 passes and 0 failures after the repairs.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: read-only quality 69.6s latest / 64.8s median against a 90s budget; pytest 42.8s latest / 48.5s median against 140s. command: `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --summary`
- coverage gate: passed; the final quality run reports a separate stale changed-line mutation-coverage advisory for the prior #450 range.
- evaluator depth: deterministic gates only; the Cautilus planner marked evaluation optional and its contract requires an explicit operator confirmation before execution.

## Healthy

- Specdown executes all repository specs with a temporary report directory, leaving the tracked derived report untouched during quality runs.
- Online external-link validation passes after Defuddle's npm UI URLs were replaced by the official upstream repository URL.
- Shell, lint, focused regressions, dead-code advisory, duplicate ratchet, and final read-only quality run all pass.

## Weak

- Fifteen Python files remain in the advisory size band; none crossed a hard limit or was changed in this slice.

## Missing

- No release-only or Cautilus behavioral proof was requested; this review makes no claim about those optional surfaces.

## Deferred

- Test-file/nested-CLI economics are measured but not changed: 415 test files and 163 standing nested-CLI files need value-preserving profiling before consolidation.

## Advisory

- structural review result: `inventory_structural_waste.py --summary` found only one repeated-read candidate; it was outside the repaired quality-runner boundary. command: `python3 skills/public/quality/scripts/inventory_structural_waste.py --repo-root . --summary`
- prose review result: no target-skill prose change; the fix preserves the existing concise phase-summary and verbose-on-failure model. artifact: `charness-artifacts/debug/2026-07-22-debug-review.md`
- dead-code review: `release_tag_identity.single_remote_object_id` remains because `publish_release_helpers.py` obtains it through `runpy`; the remaining Vulture candidate is a dynamic-entrypoint false positive. command: `CHARNESS_QUALITY_DEAD_CODE=1 CHARNESS_QUALITY_LABELS=dead-code-advisory ./scripts/run-quality.sh --read-only`

## Delegated Review

- Delegated Review: executed — a bounded fresh-eye reviewer found no blocker in the temporary Specdown output fix and confirmed the incidental tracked report must not be committed.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated; runtime budgets were healthy and no slow-gate change was made.

## Commands Run

- `./scripts/run-quality.sh --review` (baseline: exposed two failures).
- `CHARNESS_LINK_CHECK_ONLINE=1 ./scripts/check-links-external.sh`.
- `CHARNESS_QUALITY_DEAD_CODE=1 CHARNESS_QUALITY_LABELS=dead-code-advisory ./scripts/run-quality.sh --read-only`.
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`.
- `./scripts/run-quality.sh --read-only` (final: 81 passed, 0 failed).

## Recommended Next Quality Moves

- active refresh the changed-line mutation coverage proof before a push — capability_needed=fresh focused coverage; next_center=the prior #450 changed range; transformation=run the closeout producer; proof_boundary=its freshness marker; enforcement_posture=existing gate.
- passive profile nested CLI consolidation only after a representative wall-clock breakdown because current runtime budgets are healthy and file counts do not prove waste — capability_needed=per-test startup evidence; next_center=standing pytest; transformation=measure before refactor; proof_boundary=preserved behavior coverage; enforcement_posture=no-gate.

## History

- [2026-07-14 open-issue quality proof](history/2026-07-14-open-issue-resolution-proof.md)
