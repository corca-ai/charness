---
name: go-quality
description: "Sample vocabulary preset for Go-oriented quality work in maintainer environments."
preset_kind: sample-vocabulary
install_scope: maintainer
---

# go-quality

This preset is a shipped sample for Go repos.

## Intended Use

Apply this when the repo's primary quality surface is Go-centric and the
adapter needs a sane starting vocabulary.

## Suggested Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `charness-artifacts/`
- quality output directory: `charness-artifacts/quality`

## Suggested Gate Vocabulary

- preflight: module download sanity, repo health, generated-code freshness
- behavior gates: `go test ./...`
- static gates: `go vet ./...` and the repo's chosen formatter check
- confidence extras when justified: coverage, `govulncheck`, secret scanning,
  dependency review, supply-chain audit

## Notes

- this preset suggests command families, not exact commands
- the adapter should record the repo's actual commands explicitly
- prefer tightening existing `go test` or `go vet` coverage before layering a
  new tool
