# typescript-quality

This preset is a shipped sample for TypeScript and mixed Node/TypeScript repos.

## Intended Use

Apply this when the repo's primary quality surface is TypeScript-centric and the
adapter needs a sane starting vocabulary.

## Suggested Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `skill-outputs/`
- quality output directory: `skill-outputs/quality`

## Suggested Gate Vocabulary

- preflight: dependency install sanity, lockfile presence, repo health
- behavior gates: `vitest`, `jest`, or repo-native test runner
- static gates: `tsc --noEmit`, `eslint`
- confidence extras when justified: coverage, `knip`, dependency review, supply
  chain audit

## Notes

- this preset suggests command families, not exact commands
- the adapter should record the repo's actual commands explicitly
- prefer tightening an existing test or lint surface before layering a new tool
