---
name: markdown-preview
description: "Internal support capability for rendering checked-in Markdown into durable preview artifacts so doc-facing workflows can review real terminal output instead of raw source alone."
---

# Markdown Preview

This is a support capability, not a public workflow concept.

Use it when a doc-facing workflow needs rendered terminal snapshots for
README, docs, or spec prose review.

## Runtime Contract

- prefer `glow` for terminal-faithful Markdown rendering when it is available
- render checked-in Markdown at explicit widths and persist the result as text
  artifacts
- search for repo-local config at [`.agents/markdown-preview.yaml`](../../../.agents/markdown-preview.yaml),
  `.codex/markdown-preview.yaml`, `.claude/markdown-preview.yaml`,
  `docs/markdown-preview.yaml`, and [`markdown-preview.yaml`](../../../.agents/markdown-preview.yaml)
- when `glow` is missing, write degraded artifacts that say so explicitly
  instead of pretending source-only review is equivalent

Use the helper:

```bash
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --file README.md --width 80 --width 100
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --changed-only
python3 "$SKILL_DIR/scripts/render_markdown_preview.py" --repo-root . --config .agents/markdown-preview.yaml
```

## Guardrails

- Do not claim rendered review happened when the run fell back to degraded
  source snapshots.
- Do not hardcode one repo's doc scope into the support skill when config can
  carry that choice.
- Do not turn readability into a binary fail gate before the repo has
  established what should be reviewed and at which widths.

## References

- `references/runtime-contract.md`
- `scripts/render_markdown_preview.py`
