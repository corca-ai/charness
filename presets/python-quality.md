---
name: python-quality
description: "Sample vocabulary preset for Python-oriented quality work in maintainer environments."
preset_kind: sample-vocabulary
install_scope: maintainer
---

# python-quality

This preset is a shipped sample for Python repos.

## Intended Use

Apply this when the repo's primary quality surface is Python-centric and the
adapter needs a sane starting vocabulary.

## Suggested Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `charness-artifacts/`
- quality output directory: `charness-artifacts/quality`

## Suggested Gate Vocabulary

- preflight: environment sync sanity, lockfile presence, repo health
- behavior gates: `pytest` or repo-native test runner
- static gates: `ruff check`, `mypy` or `pyright`
- confidence extras when justified: coverage, `deptry`, `gitleaks` or another
  repo-native secret scanner, dependency review, supply-chain audit

## Notes

- this preset suggests command families, not exact commands
- the adapter should record the repo's actual commands explicitly
- prefer one honest type-checking path over multiple overlapping weak ones
