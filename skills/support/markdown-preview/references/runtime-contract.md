# Runtime Contract

`markdown-preview` owns one narrow seam: turn checked-in Markdown files into
durable terminal-rendered text snapshots that later sessions can inspect.

## Why This Exists

Raw `.md` review can miss spacing, paragraph density, and block readability
problems that only show up after rendering. This support seam keeps that check
available to workflows such as `narrative`, `announcement`, or `specdown`
without turning "preview docs" into a new public skill.

## Backend Posture

- preferred backend: `glow`
- preferred output: width-specific `.txt` snapshots plus a machine-readable
  `manifest.json`
- fallback posture: degraded artifact with explicit backend-missing notice and
  the raw source copied only as a reference aid

Degraded output is honest but weaker. It helps later sessions understand what
happened, but it does not count as equivalent proof that the rendered document
was reviewed.

## Config Shape

The helper accepts a small YAML mapping. Keep it simple enough for the repo's
lightweight YAML loader:

```yaml
enabled: true
backend: glow
widths:
  - 80
  - 100
include:
  - README.md
  - docs/**/*.md
on_change_only: true
artifact_dir: .artifacts/markdown-preview
```

Field meanings:

- `enabled`: disable the preview run without deleting the config file
- `backend`: current supported value is `glow`
- `widths`: explicit render widths
- `include`: repo-relative file paths or glob patterns
- `on_change_only`: keep only changed Markdown targets from the configured
  scope
- `artifact_dir`: directory for preview artifacts and `manifest.json`

## Artifact Shape

Recommended artifact naming:

- `README.w80.txt`
- `README.w100.txt`
- `docs__specs__index.spec.w100.txt`
- `manifest.json`

`manifest.json` should preserve:

- selected backend
- whether rendering was real or degraded
- config path used, if any
- widths requested
- target files and generated artifact paths
- warnings such as missing backend or skipped files

## Scope Selection

Prefer config-owned scope over support-skill hardcoding. The support helper may
ship broad defaults for convenience, but repo-owned config should decide which
documents matter for that repo's landing-doc or spec-review loop.

`on_change_only` should narrow from the configured include set, not invent a
new scope from every changed file in the repo.
