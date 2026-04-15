---
name: specdown-quality
description: "Sample vocabulary preset for repos that use executable Markdown specs and need to control spec cost, overlap, and adapter depth."
preset_kind: sample-vocabulary
install_scope: maintainer
---

# specdown-quality

This preset is a shipped sample for repos that keep acceptance checks in
specdown-style executable specs.

## Intended Use

Apply this when the repo already relies on executable Markdown specs and the
next quality move is to keep them fast, honest, and boundary-focused instead of
letting them absorb unit-test detail.

## Suggested Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `charness-artifacts/`
- quality output directory: `charness-artifacts/quality`
- `coverage_fragile_margin_pp`: `1.0`
- `specdown_smoke_patterns`:
  - `\\bgrep\\s+-q\\b`
  - `\\[pycheck\\]`
  - `\\b(?:uv\\s+run\\s+)?python\\s+-m\\s+pytest\\b`
  - `\\bpytest\\b.*\\s-k\\s+`

## Suggested Gate Vocabulary

- executable-spec smoke: `specdown run -quiet` or repo-native filtered smoke
- overlap control: repo-owned duplicate-command or overlap checker for spec
  commands
- boundary checks: keep only acceptance-criteria examples in executable specs
- lower-level checks: move repeated fine-grained cases into unit tests,
  source guards, or domain adapters
- adapter health: prefer direct adapters or check tables when shell blocks
  repeat the same pattern

## Notes

- executable specs should prove boundary behavior, not replace the unit suite
- if the same broad shell-driven command appears across many specs, treat that
  as a refactor signal
- when a shell block mostly exists to parse output, build an adapter instead of
  adding more shell glue
