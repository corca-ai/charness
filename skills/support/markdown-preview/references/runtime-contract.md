# Runtime Contract

`markdown-preview` owns one narrow seam: turn checked-in Markdown files into
durable terminal-rendered text snapshots that later sessions can inspect.

## Why This Exists

Raw `.md` review can miss spacing, paragraph density, and block readability
problems that only show up after rendering. This support seam keeps that check
available to workflows such as `narrative`, `announcement`, or `specdown`
without turning "preview docs" into a new public skill.

## Specdown

The renderer choice follows the source's authoritative human surface. Ordinary
Markdown prose can use terminal snapshots. Executable `*.spec.md` documents
whose reader surface is a Specdown report should be reviewed through that
rendered report; a raw Markdown terminal preview is only a secondary fallback.

## Scope Selection

Prefer config-owned scope over support-skill hardcoding. The support helper may
ship broad defaults for convenience, but repo-owned config should decide which
documents matter for that repo's landing-doc or spec-review loop.

`on_change_only` should narrow from the configured include set, not invent a
new scope from every changed file in the repo.

YAML config keys, backend posture enums, and `manifest.json` field lists are
owned by `scripts/render_markdown_preview.py` and its config loader, not
restated here.
