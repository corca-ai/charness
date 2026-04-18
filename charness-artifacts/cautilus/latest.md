# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `spec` contract layering, specdown on-demand viewer policy, and canonical premortem stop wording
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: clarify that public executable contracts stay reader-facing while
  on-demand behavioral proof remains artifact-backed, without intentionally
  changing the standing routing claims for `spec`

## Prompt Surfaces

- `skills/public/spec/SKILL.md`
- `skills/public/spec/references/public-executable-contracts.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`
- `skills/public/quality/references/fresh-eye-premortem.md`

## Commands Run

- `python3 scripts/validate-skills.py --repo-root .`
- `pytest tests/quality_gates/test_spec_premortem.py tests/quality_gates/test_docs_and_misc.py tests/test_public_skill_validation.py`
- `python3 scripts/check-doc-links.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `specdown run -quiet -no-report`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `reject`
- instruction-surface summary: `3 passed / 1 failed / 0 blocked`
- routing notes: `compact-no-bootstrap-impl` still routes directly to `impl`,
  both contract-shaping cases still route to `spec`, and the checked-in
  bootstrap case still collapses to observed `impl` after loading
  `find-skills`
- contract notes: this slice clarified that public executable pages may act as
  viewers over checked on-demand artifacts, but the checked artifact remains
  the source of truth for the run
- premortem notes: `premortem` stays `hitl-recommended` and `adapter-free`,
  with behavioral proof remaining on-demand rather than standing
  evaluator-required

## Follow-ups

- close `charness#39` only after the checked-in bootstrap expectation is
  updated or reclassified under the released `bootstrapHelper/workSkill` split
- keep `premortem` out of standing evaluator-required routing coverage unless
  a narrow low-noise route-only expectation proves worthwhile
- if more on-demand artifacts need reader-facing visibility, add specdown
  viewer pages over checked artifacts rather than promoting source guards into
  public executable specs
