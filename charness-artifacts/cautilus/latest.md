# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: grouped fixes for issues #146, #147, #148, #149, #150, #151,
  #152, #153, and #154.
- source: operator direction to finish all issue chunks first, then run
  Cautilus once at the end.

## Validation Goal

- goal: preserve
- reason: this slice changes routing, prompt, scenario, and adapter surfaces
  while preserving the whole-repo instruction-surface contract.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`
- changed public skills: `announcement`, `find-skills`, `setup`
- scenario-registry decision: maintained issue coverage now includes
  `issue-sibling-search-concept-fixtures`; no additional scenario IDs were
  needed for announcement/setup because focused deterministic tests and
  scenario review cover those prompt edits.

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml` now passes isolated Codex home mode into the
  local eval runner template.
- `skills/public/announcement/SKILL.md` requires release drafting to inspect
  commit bodies, trailers, closing references, and merge descriptions before
  adjacent docs.
- `skills/public/announcement/references/draft-shape.md` adds the affordance
  rewrite pass and canonical-before-alias examples.
- `skills/public/setup/SKILL.md` seeds announcement-ready commit-body
  expectations during initial repo setup.
- `skills/public/setup/references/agent-docs-policy.md` records commit-body
  guidance for generated agent docs.
- `skills/public/setup/references/default-surfaces.md` adds release-friendly
  commit-message expectations to default operating surfaces.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `cautilus eval evaluate --input .cautilus/runs/20260512T040635596Z-run/eval-observed.json`
- `python3 scripts/eval_cautilus_scenarios.py --repo-root . --mode held_out --baseline-ref origin/main --output-dir /tmp/charness-cautilus-held-out-check`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`
- `pytest -q tests/test_cautilus_scenarios.py`
- broad deterministic gate set: packaging, docs, skills, adapters, surfaces,
  integrations, support sync, tool update, markdown, secrets, py_compile, and
  repo pytest suites.

## Regression Proof

- eval test result: whole-repo routing fixture completed with 0 failed
  observed cases at `.cautilus/runs/20260512T040635596Z-run/`; the summary
  recommendation is `defer` because each live Codex runner case was blocked by
  authentication before producing routing JSON.
- eval evaluate result: 5 blocked / 0 failed / 0 passed. The blocker is
  `runner_execution_failed`; stderr records `401 Unauthorized: Missing bearer
  or basic authentication` from the Codex API.
- deterministic scenario proof passed: 13 Cautilus scenario tests, scenario
  validation, and held-out eval registry execution all passed.
- deterministic repo proof passed: 852 pytest tests passed with 4 skipped, and
  all packaging, docs, skill, adapter, surface, integration, support-sync,
  tool-update, markdown, secret, and py_compile gates passed.

## Scenario Review

- Issue #151 now has behavior-backed concept assertions in real #146/#148
  sibling-search fixtures, a maintained registry scenario, and evaluator
  profile inclusion for the issue skill.
- Issue #146/#148 workflow routing is backed by deterministic CLI and
  find-skills recommendation tests rather than a new live prompt scenario.
- Announcement/setup prompt edits are bounded to release-readiness guidance and
  commit-context collection; deterministic tests assert the collector behavior
  that the prompt asks agents to rely on.
- The Cautilus live runner result is blocked by external authentication, not by
  a routing mismatch produced by the observed agent output.

## Outcome

- recommendation: defer full Cautilus acceptance until the Codex eval runner
  has valid API authentication, but accept the deterministic issue fixes and
  checked-in scenario coverage.
- The operator-requested single end-of-slice Cautilus run was performed; its
  blocker is captured in the run artifact and this proof record.

## Follow-ups

- Re-run `cautilus eval test` and `cautilus eval evaluate` after runner
  authentication is available.
- Use the new `issue-sibling-search-concept-fixtures` scenario as the standing
  proof path for future #146/#148 sibling-search regressions.
