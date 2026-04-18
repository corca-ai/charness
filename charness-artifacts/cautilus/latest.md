# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `gather` private SaaS browser-fallback contract
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: widen `gather` and `agent-browser` wording for browser-mediated
  private-source acquisition without regressing the maintained root
  instruction-surface routing contract

## Prompt Surfaces

- `skills/public/gather/SKILL.md`
- `skills/public/gather/references/capability-contract.md`
- `skills/public/gather/references/browser-mediated-private-sources.md`
- `skills/support/agent-browser/SKILL.md`
- `skills/support/agent-browser/references/runtime.md`
- `skills/support/agent-browser/references/auth-bootstrap.md`

## Commands Run

- `pytest -q tests/test_gather_google_workspace.py tests/charness_cli/test_capability_resolution.py`
- `python3 scripts/validate-skills.py --repo-root .`
- `python3 scripts/validate-integrations.py --repo-root .`
- `python3 scripts/check-skill-contracts.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in bootstrap case still routes as
  `bootstrapHelper=find-skills` plus `workSkill=impl`; compact no-bootstrap
  implementation still routes to `impl`; contract-shaping still routes to
  `spec`
- gather notes: the new contract now names official API/export first,
  `agent-browser` browser fallback, first-class auth/bootstrap modes, and
  remote/headless degradation without perturbing the maintained first-skill
  routing surface

## Follow-ups

- close `charness#40` if the repo-facing contract and example scope are
  judged sufficient
- if `gather` needs long-context chatbot coverage next, add it to the packet
  only after this contract lands and is stable
