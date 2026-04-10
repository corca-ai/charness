# google-public-export Support Reference

This generated reference records how `charness` consumes the upstream
support surface without copying it into the local taxonomy.

- upstream repo: `corca-ai/claude-plugins`
- upstream path: `plugins/cwf/skills/gather/SKILL.md`
- sync strategy: `reference`
- support state: `upstream-consumed`
- access modes: `public, human-only, degraded`

## Config Layers

- `operator-step`: The operator may need to share or publish the Google document so the export endpoint is reachable.
- `public-fallback`: Use the public Google export endpoint for supported Docs, Slides, or Sheets URLs.

## Reuse Notes

- Relevant upstream handler: `plugins/cwf/skills/gather/scripts/g-export.sh`.
- See `plugins/cwf/skills/gather/references/google-export.md` for format limits and export caveats.

## Host Notes

- This manifest intentionally models only the public export path. Private Google Workspace access is a separate future integration.

Regenerate this file through `scripts/sync_support.py` instead of
editing it by hand.
