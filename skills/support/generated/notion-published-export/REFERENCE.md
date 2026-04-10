# notion-published-export Support Reference

This generated reference records how `charness` consumes the upstream
support surface without copying it into the local taxonomy.

- upstream repo: `corca-ai/claude-plugins`
- upstream path: `plugins/cwf/skills/gather/SKILL.md`
- sync strategy: `reference`
- support state: `upstream-consumed`
- access modes: `public, human-only, degraded`

## Config Layers

- `operator-step`: The operator may need to publish the Notion page to the web before export is possible.
- `public-fallback`: Use the published-page export helper for public Notion page URLs.

## Reuse Notes

- Relevant upstream handler: `plugins/cwf/skills/gather/scripts/notion-to-md.py`.
- See `plugins/cwf/skills/gather/references/notion-export.md` for publication requirements and limitations.

## Host Notes

- This manifest intentionally models only published-page export. Private Notion API access is a separate future integration.

Regenerate this file through `scripts/sync_support.py` instead of
editing it by hand.
