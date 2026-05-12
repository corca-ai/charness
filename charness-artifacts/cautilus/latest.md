# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: issue #146/#148 follow-up plus support-skill installation policy.
- source: operator correction that sibling search must generalize from the
  mistaken mental model, followed by a policy decision that upstream support
  skills belong in the installed Charness plugin, not in this repo source or
  checked-in plugin export.

## Validation Goal

- goal: preserve
- reason: this slice should preserve issue-skill routing while changing where
  upstream support skills are discovered and materialized.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `truth_surface_change`
- `scenario_review_change`
- changed public skills: `find-skills`, `issue`, `spec`
- scenario-registry decision: no maintained registry mutation in this slice;
  issue-specific fixtures remain under `evals/cautilus/`, while broader
  fixture-quality work is tracked in corca-ai/charness#151.

## Prompt Surfaces

- `skills/public/issue/SKILL.md` requires mental-model sibling search.
- `skills/public/issue/references/causal-review.md` expands Lens 3 with
  mental-model siblings.
- `skills/public/spec/SKILL.md` remains part of the worktree-readiness prompt
  surface from #146.
- `skills/public/find-skills/references/support-consumption.md` now describes
  installed-plugin support materialization instead of repo-local generated
  support as the active synced-support model.
- `skills/shared/references/source-bound-records.md` was adjusted to keep the
  source-bound report-owner concept while satisfying durable link rules.
- Removed upstream support bodies from source prompt surfaces:
  `skills/support/agent-browser/SKILL.md`,
  `skills/support/agent-browser/references/auth-bootstrap.md`,
  `skills/support/agent-browser/references/runtime.md`,
  `skills/support/specdown/SKILL.md`, and
  `skills/support/specdown/references/source-notes.md`.
- Truth docs changed through `README.md`: upstream support skills are
  materialized into the installed Charness plugin support surface.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/issue-146-sibling-search.fixture.json --runtime codex`
- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/issue-148-sibling-search.fixture.json --runtime codex`
- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --runtime codex`
- `python3 scripts/eval_support_sync_contracts.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_integrations.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`

## Regression Proof

- eval test result: issue #146 fixture passed, recommendation `accept-now`.
  Run artifact: `.cautilus/runs/20260511T224215741Z-run/`.
- eval test result: issue #148 fixture passed, recommendation `accept-now`.
  Run artifact: `.cautilus/runs/20260511T224230330Z-run/`.
- eval test result: standing whole-repo routing fixture rejected with 4 passed
  / 1 failed / 0 blocked. Run artifact:
  `.cautilus/runs/20260511T224400482Z-run/`.
- deterministic support proof passed: support-sync contracts, skill
  validation, integration validation, packaging validation, py_compile, and
  focused pytest suites for sync, doctor, install, packaging, runtime guard,
  and find-skills all passed.

## Scenario Review

- The issue-specific fixtures remain useful for the mental-model sibling-search
  behavior, but they still rely on manual inspection for concept-level claims.
- The support-skill policy change is mostly a truth/control-plane relocation:
  source-owned support remains under `skills/support`, while upstream support
  skills are copied into the installed plugin during install/update/sync.
- The standing route failure predates the support relocation and is still
  tracked in corca-ai/charness#151.

## Outcome

- recommendation: accept deterministic support-policy implementation, but do
  not claim full Cautilus closeout because the standing whole-repo fixture still
  rejects.
- The installed-plugin direction is implemented: checked-in source and plugin
  exports no longer carry upstream agent-browser/specdown bodies; install and
  tool update/sync materialize upstream support skills under
  `support/<tool-id>/` in the installed Charness plugin.

## Follow-ups

- Resolve corca-ai/charness#151 for brittle prompt-surface tests and standing
  fixture quality.
- Keep any future upstream support body updates source-bound through tool
  manifests and installed-plugin materialization, not checked-in vendored
  copies.
