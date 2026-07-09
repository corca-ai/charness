# Quality Review
Date: 2026-07-09

## Scope

Target boundary: repo-wide quality follow-up focused on public-skill helper CLI
ergonomics, specifically the debug planner's `--repo-root` help.

Ambient repo findings: broader argparse help debt remains, but the debug planner
had a single deterministic omission that could be closed with a focused test and
packaging proof.

## Current Gates

- Healthy: focused debug planner tests passed after the help repair.
- Healthy: ruff, py_compile, skill validation, skill ergonomics validation,
  packaging validation, and gitignore scan hygiene passed.
- Healthy: skill ergonomics inventory now reports debug
  `argparse_missing_help: 0`.
- Healthy: public-skill dogfood review inspected the current `debug` consumer
  contract and `evals/cautilus/scenarios.json`; routing, artifact home, and the
  maintained `debug-adapter-bootstrap` scenario are unchanged because this slice
  only adds planner `--help` text.
- Weak: broader argparse help debt remains at 80 findings outside debug planner.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 28.5s latest / 31.5s median, budget 140.0s;
  `dead-code-advisory` 7.8s latest / 7.8s median; `check-coverage` 7.0s latest
  / 7.3s median, budget 55.0s; `check-markdown` 6.1s latest / 5.9s median,
  budget 11.0s; `check-secrets` 5.2s latest / 5.0s median, budget 6.0s.
- coverage gate: focused debug planner tests passed; full slice closeout is
  recorded separately.
- evaluator depth: deterministic gates only; Cautilus stayed ask-before-run and
  no evaluator-backed behavior proof was needed for CLI help text. `plan_cautilus_proof.py`
  reported `next_action: none` with `debug` scenario review required; review
  decision: no maintained scenario mutation or live Cautilus run.

## Healthy

- `plan_debug_run.py --help` now explains `--repo-root`.
- The source debug planner and plugin mirror carry the same help text.
- The regression test checks the option and human-facing purpose without
  pinning argparse wrapping.

## Weak

- The repo still has 80 remaining `argparse_missing_help` findings across other
  helper scripts.
- Runtime cost remains dominated by standing pytest, though current samples are
  below budget.

## Missing

- Missing: no repo-wide argparse help cleanup was attempted in this slice.
- Missing: no remote CI or pushed-branch proof; this branch remains local.

## Deferred

- Deferred: shared `adapter_init_lib.py` argparse help debt is real but affects
  multiple init adapters and should be handled in a separate slice.
- Deferred: release-only CLI speed pruning remains separate from this operator
  help repair.

## Advisory

- structural review result: command evidence: skill ergonomics inventory fields
  `checked_skill_count=22`, `finding_status=heuristics_present`,
  `prose_review_status=required`, and `subcheck_counts.argparse_missing_help`;
  debug moved from one argparse help finding to zero, while total repo debt moved
  from 81 to 80.
- public-skill review result: command evidence:
  `suggest_public_skill_dogfood.py --skill-id debug --json` returned the existing
  durable-debug consumer prompt, and `evals/cautilus/scenarios.json` still maps
  `debug` to `debug-adapter-bootstrap`; this helper help repair does not change
  that contract.
- prose review result: artifact evidence:
  [critique record](../critique/2026-07-09-debug-planner-help-critique.md);
  fresh-eye review found no code blocker and counterweight confirmed no closeout
  blocker remained.
- runtime interpretation: command evidence: runtime summary packet; current
  hot spots are real standing costs but stayed below budget, so targeted
  CLI-help cleanup remained the smallest deterministic quality move.

## Delegated Review

- Delegated Review: executed — worker implemented the repair; two fresh-eye
  reviewers checked operator wording and source/plugin proof; counterweight
  confirmed no blocker remained.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  executed — the runtime packet was reviewed, but no slow-gate scope change was
  made.

## Commands Run

- command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- command: `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- command: `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- command: focused debug planner pytest module runner.
- command: `ruff check skills/public/debug/scripts/plan_debug_run.py plugins/charness/skills/debug/scripts/plan_debug_run.py tests/test_debug_plan.py`
- command: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- command: `python3 scripts/validate_packaging.py --repo-root .`
- command: `python3 scripts/validate_packaging_committed.py --repo-root .`
- command: `python3 scripts/validate_skills.py --repo-root .`
- command: `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- command: `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`

## Recommended Next Quality Moves

- active argparse-help-next-package — capability_needed=operator-facing helper CLIs that explain their inputs; next_center=another one-package argparse_missing_help slice; transformation=clear one package at a time with focused help-output proof; proof_boundary=skill ergonomics inventory plus package-focused tests; enforcement_posture=advisory.
- passive shared-init-adapter-help because it crosses multiple adapter init call sites; capability_needed=clear init-adapter CLI help; next_center=scripts/adapter_init_lib.py; transformation=add shared help text with focused adapter-init tests; proof_boundary=shared helper tests plus skill ergonomics inventory; enforcement_posture=advisory.
- passive standing-pytest-speed because current pytest samples are below budget; capability_needed=faster standing confidence; next_center=mixed release_only/standing CLI tests; transformation=move repeated boundary proof lower only where honest; proof_boundary=runtime summary plus preserved sentinel coverage; enforcement_posture=no-gate until scoped.

## History

- [2026-07-03 pytest suite audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
