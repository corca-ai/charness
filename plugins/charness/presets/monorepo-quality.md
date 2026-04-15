---
name: monorepo-quality
description: "Sample vocabulary preset for monorepos that need scoped gates, ownership-aware checks, and honest top-level smoke coverage."
preset_kind: sample-vocabulary
install_scope: maintainer
---

# monorepo-quality

This preset is a shipped sample for monorepos with multiple packages, apps, or
services under one repo-owned quality bar.

## Intended Use

Apply this when the repo needs one maintainer-facing vocabulary that can talk
about package-level gates, shared top-level smoke, and ownership-aware
verification without collapsing into one giant always-run command.

## Suggested Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `charness-artifacts/`
- quality output directory: `charness-artifacts/quality`

## Suggested Gate Vocabulary

- workspace sanity: lockfile integrity, graph health, package discovery
- scoped behavior gates: per-package tests and type checks
- shared smoke: one top-level integration or CLI smoke that proves packages
  compose correctly
- ownership checks: changed-package targeting, dependency boundary review,
  dead-package detection
- confidence extras when justified: coverage deltas, graph drift, generated
  artifact validation

## Notes

- do not replace package-local deterministic gates with one broad shell wrapper
- keep the top-level smoke thin; let package-local suites carry most detail
- prefer explicit package or boundary ownership over hidden global defaults
