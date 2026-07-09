# Quality Review
Date: 2026-07-09

## Scope

Target boundary: repo-wide quality follow-up focused on operator-facing CLI help
and support-skill ergonomics.

Ambient repo findings: runtime packets still show `pytest` as the largest
standing cost, but it remains below budget; the actionable low-risk slice was
the markdown-preview support skill's seven missing argparse help strings.

## Current Gates

- Healthy: markdown-preview focused pytest passed after the help repair.
- Healthy: ruff, skill validation, skill ergonomics validation, packaging
  validation, py_compile, and gitignore scan hygiene passed.
- Healthy: skill ergonomics inventory now reports markdown-preview
  `argparse_missing_help: 0`.
- Weak: broader argparse help debt remains at 81 findings outside
  markdown-preview.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 28.5s latest / 31.5s median, budget 140.0s;
  `dead-code-advisory` 7.8s latest / 7.8s median; `check-coverage` 7.0s latest
  / 7.3s median, budget 55.0s; `check-markdown` 6.1s latest / 5.9s median,
  budget 11.0s; `check-secrets` 5.2s latest / 5.0s median, budget 6.0s.
- coverage gate: focused markdown-preview support tests passed; full slice
  closeout is recorded separately.
- evaluator depth: deterministic gates only; Cautilus stayed ask-before-run and
  no evaluator-backed behavior proof was needed for CLI help text.

## Healthy

- The markdown-preview render CLI now explains all seven arguments.
- The source support skill and plugin mirror carry the same help text.
- The regression test checks option presence and normalized help snippets
  without pinning argparse line wrapping.

## Weak

- The repo still has 81 remaining `argparse_missing_help` findings across other
  skill helper scripts.
- Runtime cost remains dominated by standing pytest, though current samples are
  within budget and not the best next local slice.

## Missing

- Missing: no repo-wide argparse help cleanup was attempted in this slice.
- Missing: no remote CI or pushed-branch proof; this branch remains local.

## Deferred

- Deferred: continue argparse help cleanup package-by-package rather than
  broad-editing all 81 remaining findings.
- Deferred: release-only CLI speed pruning remains separate from this operator
  help repair.

## Advisory

- structural review result: command evidence: skill ergonomics inventory fields
  `checked_skill_count=22`, `finding_status=heuristics_present`,
  `prose_review_status=required`, and `subcheck_counts.argparse_missing_help`;
  markdown-preview moved from seven argparse help findings to zero, while total
  repo debt moved from 88 to 81.
- prose review result: artifact evidence:
  [critique record](../critique/2026-07-09-markdown-preview-help-critique.md);
  fresh-eye review found one inaccurate help string and counterweight found no
  remaining blocker.
- runtime interpretation: command evidence: runtime summary packet; current
  hot spots are real standing costs but stayed below budget, so the help debt
  was the smaller deterministic quality move this turn.

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
- command: focused markdown-preview pytest module runner.
- command: `ruff check skills/support/markdown-preview/scripts/render_markdown_preview.py plugins/charness/support/markdown-preview/scripts/render_markdown_preview.py tests/test_markdown_preview_support.py`
- command: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- command: `python3 scripts/validate_packaging.py --repo-root .`
- command: `python3 scripts/validate_packaging_committed.py --repo-root .`
- command: `python3 scripts/validate_skills.py --repo-root .`
- command: `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- command: `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`

## Recommended Next Quality Moves

- active argparse-help-next-package — capability_needed=operator-facing helper CLIs that explain their inputs; next_center=one remaining package with argparse_missing_help findings; transformation=clear one package at a time with focused help-output proof; proof_boundary=skill ergonomics inventory plus package-focused tests; enforcement_posture=advisory.
- passive standing-pytest-speed because current pytest samples are below budget; capability_needed=faster standing confidence; next_center=mixed release_only/standing CLI tests; transformation=move repeated boundary proof lower only where honest; proof_boundary=runtime summary plus preserved sentinel coverage; enforcement_posture=no-gate until scoped.
- passive split-standing-test-economics-lib because the module is already in the warn band; capability_needed=maintainable inventory helper; next_center=next nontrivial standing-test economics change; transformation=extract another helper before adding behavior; proof_boundary=length checker plus focused tests; enforcement_posture=advisory.

## History

- [2026-07-03 pytest suite audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
