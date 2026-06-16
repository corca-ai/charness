# Critique Review
Date: 2026-06-16

## Decision Under Review

Remove the `pry` external-tool integration from the supported tool surface. pry
was added in the v0.49.0 bundle as an `external_binary_with_skill` manifest
consumed by `quality` as an advisory, exit-0 `inventory-testability-surface`
phase (welded-boundary testability backlog). Operator judgment: it was added too
hastily and should be withdrawn before more surfaces depend on it. A release
follows.

## Failure Angles

- Completeness: a manifest deletion is incomplete if dependency lists, the
  quality run-quality phase, the consumer-fields declaration, doc timing tables,
  or test fakes/fixtures still bind `pry`.
- Over-removal: the agent-runtime `spawn` seam and the general (non-pry)
  testability/structural guidance in `testability-and-selection.md` are
  independent improvements; removing them would be scope creep, not pry removal.
- Generated-surface drift: `plugins/charness/**` mirrors must be regenerated, or
  the export ships stale pry content.
- Consumer contract: removing an advisory phase must not silently change the
  public `quality` consumer contract (routing / artifact shape / dogfood).

## Counterweight Pass

- The pry phase was advisory-only (always exit 0, degraded when the binary was
  absent) and was never part of the `quality` consumer output contract, so its
  removal is a simplification, not a contract break — `validate_public_skill_dogfood.py`
  passes unchanged and pry never touched `docs/public-skill-dogfood.json`.
- The agent-runtime `spawn` seam (`scripts/agent-runtime/run-local-eval-test.mjs`
  + `tests/agent-runtime/native.test.mjs`) was deliberately KEPT; only a
  pry-mentioning comment was cleaned. The seam stands on its own testability
  merit.
- Historical `charness-artifacts/**` records and the v0.49.0 entry in
  `.agents/release-adapter.yaml` remain historical provenance, not current
  contracts; they were intentionally preserved.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: integrations/tools/dependencies.json:7 | action: fix | note: pry removed from dependency list (source + plugin mirror); both parse as valid JSON
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:515 | action: fix | note: the `inventory-testability-surface` phase block removed; bash -n clean; mirror synced
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/inventory-consumer-fields.json:31 | action: fix | note: declaration entry removed in lockstep with the deleted script, so `check_inventory_declaration_coverage.py` stays consistent (both directions green)
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/{test_tool_lifecycle.py,tool_fakes.py,support.py,test_update_output.py,test_managed_install_extended.py} | action: fix | note: pry removed from the validation-role tool-set assertions, the `make_fake_pry` fixture, and the support-sync mapping; focused + release_only install/update tests pass
- F5 | bin: over-worry | evidence: strong | ref: skills/public/quality/references/testability-and-selection.md:184 | action: document | note: only the `## Welded-Boundary Testability Backlog (pry)` section removed; all non-pry structural-testability guidance preserved

## Fresh-Eye Satisfaction

Bounded fresh-eye reviewer spawned in the shared parent worktree (read-only,
no index/worktree mutation). It verified completeness, over-removal,
correctness, mirror sync, and broken cross-references against the staged diff
and `git show HEAD:` baselines. Verdict: **ship** — no blockers, should-fix, or
nits.
