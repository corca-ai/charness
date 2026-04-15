---
name: gather-notion
description: "Internal support capability for gathering published Notion pages into durable local markdown without requiring consumer repos to supply their own export helper."
---

# Gather Notion

This is a support capability, not a public workflow concept.

Users should still reach this through `gather` when a published Notion page
needs to become a durable local asset.

## Runtime Contract

- this package handles the published-page path only
- keep the conversion helper local to `charness` so consumer repos do not have
  to recreate it
- private Notion API access remains a separate future capability

Use the wrapper:

```bash
python3 scripts/export-page.py \
  "https://www.notion.so/Example-0123456789abcdef0123456789abcdef" \
  charness-artifacts/gather/notion-page.md
```

## Guardrails

- Do not imply private Notion access exists when the page is not published.
- Preserve source identity and limitations in the exported markdown.
- Stop cleanly when the published-page path cannot represent the requested
  content.

## References

- `references/runtime-contract.md`
- `references/provenance.md`
- `scripts/export-page.py`
