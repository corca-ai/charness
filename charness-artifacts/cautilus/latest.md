# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: `issue resolve` closeout guidance now prefers GitHub auto-close
  through commit, PR, or merge bodies before manual close commands.
- source: operator observation that issue resolution tends not to use
  auto-closing commit/PR linkage.

## Validation Goal

- goal: preserve
- reason: this slice tightens issue-skill closeout sequencing without changing
  the existing evaluator scenario registry.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`
- changed public skills: `issue`
- scenario-registry decision: no new scenario ID is needed; the existing issue
  evaluator scenarios cover routing and sibling-search behavior, while this
  closeout-carrier rule is guarded by deterministic text-contract tests.

## Prompt Surfaces

- `skills/public/issue/SKILL.md` now makes auto-close linkage the preferred
  issue-resolution closeout path.
- `skills/public/issue/references/closeout-discipline.md` adds the
  resolve auto-close linkage contract.
- `skills/public/issue/references/resolve-flow.md` records PR-body and
  direct-to-default commit-body close keyword expectations.
- `skills/public/issue/references/resolution-brief.md` carries the same
  boundary into PR or commit closeout carriers.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `cautilus eval evaluate --input .cautilus/runs/20260512T054024489Z-run/eval-observed.json`
- `pytest -q tests/quality_gates/test_issue_closeout_discipline.py tests/quality_gates/test_issue_skill.py`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`

## Regression Proof

- eval test result: whole-repo routing fixture command passed at runner-command
  level; run artifact `.cautilus/runs/20260512T054024489Z-run/`; summary
  recommendation is `defer`.
- eval evaluate result: 5 blocked / 0 failed / 0 passed. Stderr still records
  `401 Unauthorized: Missing bearer or basic authentication`; Cautilus binary
  version was `0.15.3`.
- deterministic issue proof passed: issue closeout-discipline and issue-tool
  tests passed, including the auto-close carrier contract.
- skill, packaging, and markdown link validators passed for this slice.

## Scenario Review

- Existing issue evaluator scenarios remain focused on routing and
  mental-model sibling search; they are not the right carrier for this
  commit/PR-body closeout rule.
- The new deterministic assertion pins the behavior where it lives: the issue
  skill and closeout references must prefer PR-body or direct-to-default
  commit-body close keywords before manual close.
- The live Cautilus runner remains blocked by the Codex isolated-home auth
  issue tracked upstream as corca-ai/cautilus#35.

## Outcome

- recommendation: accept the deterministic issue-skill closeout tightening,
  but defer live evaluator acceptance until Cautilus runner auth is fixed.
- The latest local Cautilus binary was checked and is `0.15.3`; the isolated
  Codex auth blocker still reproduces.

## Follow-ups

- Re-run the whole-repo Cautilus eval after corca-ai/cautilus#35 is fixed.
- Consider a later Charness integration-manifest improvement if `charness
  update all` should make manual external-binary update boundaries more
  visible to operators.
