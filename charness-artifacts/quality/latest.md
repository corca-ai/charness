# Quality Review
Date: 2026-06-24

## Scope

Evaluate and improve the next high-consequence skill through the `quality`
lens. Candidate selected: `issue`, because it owns GitHub issue creation,
resolution, closeout carriers, and external tracker state. Those boundaries are
easy to over-claim if the agent follows prose memory instead of a helper-owned
plan plus final readback.

No Cautilus evaluator run was performed for this slice. The change is a
deterministic skill-surface improvement: planner packet, core compression,
reference discoverability, and focused contract tests.

## Current Gates

- `issue_tool.py plan --intent new|resolve` now emits the run plan before issue reads, mutations, or closeout.
- Focused issue tests pass: `tests/quality_gates/test_issue_skill.py` reports 25/25 passing.
- Skill ergonomics inventory reports `issue` core non-empty lines at 69, down from 148 before the planner/core split.
- Reference discoverability for `issue` is 0 unlisted reference files; the
  reference list now explains each reference's role.
- The remaining inventory heuristic is `portable_package_host_surface_reference`
  from `.codex/issue-adapter.yaml` and `.claude/issue-adapter.yaml` fallback
  paths in `resolve_adapter.py`; prose review disposition: intentional adapter
  fallback, not portable-package debt for this slice.

## Runtime Signals

- runtime source: structured planner JSON from `issue_tool.py plan` and inventory JSON from `inventory_skill_ergonomics.py`.
- runtime hot spots: unavailable; this slice did not collect timing samples beyond normal command completion.
- coverage gate: focused issue tests passed 24/24; broad pytest is deferred to closeout.
- evaluator depth: no Cautilus run; deterministic planner/skill gates only.
- Mutation Tests run `28049447961` passed the old failing `Select mutation sample` step and is still in `Run mutation`.

## Healthy

- The `issue` skill already had real helper coverage: adapter preflight,
  invocation parsing, issue read with comments, body-file create, milestone
  resolution, brief path, close-with-comment, and closeout verification.
- The new planner lets code do what code is good at: assemble adapter state,
  target selection, required reads, trust/cost notes, and next action as
  structured output.
- The compressed `SKILL.md` keeps the trigger contract, GitHub source-of-truth
  rule, intent split, classification routing, and irreversible-boundary warning
  in core.
- References are now role-described progressive disclosure rather than an
  unexplained filename list.

## Weak

- `issue_tool.py` is now within 36 lines of its Python file limit. The next CLI addition should register from a submodule.
- The planner does not classify an issue body by itself; that stays judgment-owned for now.
- Non-`gh` host-mediated issue backend behavior remains structurally tested, not
  provider-roundtrip proven in this slice.

## Missing

- Missing dogfood/evaluator fixture: `suggest_public_skill_dogfood.py --skill-id
  issue` classifies `issue` as evaluator-required. The next behavior proof
  should test whether a fresh session routes to `issue`, runs the planner, and
  follows the planner's next action without being coached by the fixture.
- Scenario review: existing `issue-146` / `issue-148` Cautilus fixtures cover
  causal-review sibling search, not planner-first execution. Keep them unchanged
  for this deterministic slice; add a neutral planner-use fixture later.
- Held-out scenario eval passed 10/10 after updating representative issue core contract markers.
- Missing planner adoption for adjacent high-consequence skills beyond
  `quality`, `release`, and now `issue`.

## Deferred

- Do not add a blocking length gate for `issue_tool.py` in this slice; the
  existing Python length advisory already surfaces the headroom pressure.
- Do not remove `.codex` / `.claude` adapter fallback paths just to satisfy the
  inventory heuristic; those are host adapter seams, not accidental prose
  leakage.
- Do not run Cautilus until a neutral issue-skill fixture is written. A fixture
  must not instruct the model to use the planner; it should observe whether the
  loaded skill naturally does so.

## Advisory

- command: `inventory_skill_ergonomics.py --skill-path skills/public/issue/SKILL.md --json`
  reports `reference_file_count: 6`, `unlisted_reference_count: 0`, and `host_surface_reference_count: 2`.
- prose review result: `prose_review_status=required` was satisfied for the
  issue slice by reviewing trigger boundaries, progressive disclosure, helper
  ownership, and remaining host-surface findings. The planner/core split is a
  real ergonomic improvement; the host-surface findings are intentional adapter
  fallback paths.
- command: `suggest_public_skill_dogfood.py --skill-id issue --json` reports
  `validation_tier: evaluator-required` and `adapter_requirement: required`.

## Delegated Review

- executed: bounded fresh-eye review found and fixed the ignored `plan --intent resolve --target` flag, duplicate closeout on-demand ref, missing fresh-eye policy surfacing, and prose-shaped classification action test. Valid deferrals: neutral Cautilus fixture and non-`gh` provider roundtrip.

## Commands Run

- `python3 skills/public/issue/scripts/issue_tool.py plan --repo-root . --intent resolve -- 399`
- `python3 skills/public/issue/scripts/issue_tool.py plan --repo-root . --intent new`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/issue/SKILL.md --json`
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --path skills/public/issue/SKILL.md --preview-delta 0`
- `python3 scripts/check_python_lengths.py --headroom --paths skills/public/issue/scripts/issue_tool.py skills/public/issue/scripts/issue_plan.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_skill_ergonomics.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/validate_public_skill_validation.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `python3 scripts/check_command_docs.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`
- `python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`
- `python3 scripts/validate_cautilus_diagnostics.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`
- `python3 scripts/eval_cautilus_scenarios.py --repo-root . --mode held_out --baseline-ref origin/main --output-dir /tmp/cautilus-held-out-issue-debug-2`

Focused pytest result: `tests/quality_gates/test_issue_skill.py` passed 25/25.
Focused closeout-discipline pytest result: issue closeout discipline plus issue skill tests passed 34/34.
Python compile over public/support skill scripts passed.

## Recommended Next Gates

- active Finish verification for the `issue` planner/core split, including
  fresh-eye critique and closeout.
- active Watch Mutation Tests run `28049447961`; if it succeeds or auto-closes
  #399, verify #399 state. If it fails in the mutation step, treat that as a new
  manifestation rather than the old sample-selection regression.
- passive until a neutral fixture exists: evaluate issue-skill planner use without naming the planner in the prompt.

## History

- [2026-06-16 quality review](./history/2026-06-16-quality-review.md)
