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
  expected to live. An empty list only means the repo has not declared a
  canonical asset root; it must not suppress inline prompt/content inventory.
- `prompt_asset_policy.source_globs`: which source files to scan for inline
  bulk when the repo wants the inventory
- `prompt_asset_policy.min_multiline_chars`: minimum multi-line string size to
  treat as potential prompt/content bulk
- `prompt_asset_policy.exemption_globs`: files that intentionally keep larger
  inline content

Use [`find_inline_prompt_bulk.py`](./find_inline_prompt_bulk.py) as a cheap
inventory helper when the repo keeps prompt-heavy Python sources and wants a
repeatable advisory scan.

In `charness`, prompt-affecting repo changes should also leave visible
behavioral proof:

- refresh `<repo-root>/charness-artifacts/cautilus/latest.md`
- let the repo adapter choose whether cautilus runs in `auto`, `ask`, or
  `adaptive` mode instead of assuming one global execution policy
- for `preserve` claims, keep a regression-proof record anchored by
  `cautilus eval test --repo-root . --adapter-name <repo-owned-adapter>` or a
  repo-owned dogfood wrapper
- for high-leverage prompt changes, add a short scenario-review note rather
  than pretending routing preservation alone answered the behavioral question
- in `adaptive` mode, do not stop just because scenario review is needed; stop
  only if you are about to add, remove, or update maintained scenario-registry
  coverage
- for `improve` claims, additionally record a baseline compare path with
  `cautilus workspace prepare-compare` and
  `cautilus eval evaluate --input <observed.json>`
