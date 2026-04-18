# Prompt Asset Policy

When evaluator-backed review, A/B comparison, or prompt-regression tracking
matters, prompt bytes should be easy to diff independently from code bytes.

Portable `quality` posture:

- treat declared prompt/content asset roots as a positive pattern
- inventory large inline prompt/content strings in source files as an advisory
  signal, not an automatic failure
- prefer adapter-owned source globs and thresholds over hard-coding one repo's
  layout into the public skill body
- if a fresh reader only discovers prompt bulk by reading a consumer CLAUDE or
  AGENTS file manually, surface that as a quality gap

Suggested adapter split:

- `prompt_asset_roots`: checked-in paths where prompt/content assets are
  expected to live
- `prompt_asset_policy.source_globs`: which source files to scan for inline
  bulk when the repo wants the inventory
- `prompt_asset_policy.min_multiline_chars`: minimum multi-line string size to
  treat as potential prompt/content bulk
- `prompt_asset_policy.exemption_globs`: files that intentionally keep larger
  inline content

Use [`find_inline_prompt_bulk.py`](find_inline_prompt_bulk.py) as a cheap
inventory helper when the repo keeps prompt-heavy Python sources and wants a
repeatable advisory scan.

In `charness`, prompt-affecting repo changes should also leave visible
behavioral proof:

- refresh [`charness-artifacts/cautilus/latest.md`](../../../../charness-artifacts/cautilus/latest.md)
- for `preserve` claims, run `cautilus instruction-surface test --repo-root .`
- for `improve` claims, additionally record a baseline compare path with
  `cautilus workspace prepare-compare` and
  `cautilus mode evaluate --baseline-ref <ref>`
