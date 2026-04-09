# Quality Lenses

`quality` uses four lenses.

## Concept

Borrow from `concept-review`:

- stable concepts
- ownership honesty
- source-of-truth clarity
- doc-to-runtime synchronization
- duplicate documentation that creates competing sources of truth
- skill trigger-contract honesty when the repo authors skills

Boundary note:

- `quality` should catch duplicated or drifting concept surfaces when they are
  already visible in docs, gates, or runtime seams
- a deeper question like "should these be two concepts at all?" still belongs
  to concept-review-style analysis, not only duplicate detection

## Behavior

Borrow from `test-improvement`:

- behavior-facing assertions
- failure-path confidence
- low-signal or gameable checks
- duplicate-pressure and missing seam coverage
- helper scripts that actually prove the skill can cold-start and resolve its
  adapter seams

## Security

Borrow from `security-audit` and broader review practice:

- dependency and supply-chain posture
- secret handling
- risky trust boundaries
- CI and setup safety assumptions

## Operability

Check whether the quality bar can actually be maintained:

- local setup honesty
- CI gate realism
- maintenance burden
- drift between claimed and runnable commands
- refactor pressure from copied helper seams or skill-package drift
- duplicated documentation that should collapse into one maintained surface
