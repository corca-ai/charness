# Canonical Markdown Surface Retro
Date: 2026-04-24

## Trigger

The user challenged my fix for `check_doc_links`: I converted `AGENTS.md`
mentions inside public skill bodies into source-repo-relative markdown links.

## What Went Wrong

- I treated the validator message as a mechanical rewrite instruction.
- I missed the stronger design boundary: `AGENTS.md`, `CLAUDE.md`, and
  adapter-owned handoff paths can be canonical operator concepts, not ordinary
  source file references.
- The right place for that distinction is quality adapter policy, not ad hoc
  skill prose or one-off validator exceptions.

## Correction

- Add adapter-owned `canonical_markdown_surfaces`.
- Default `AGENTS.md` and `CLAUDE.md` in the quality adapter resolver.
- Let this repo add `docs/handoff.md` explicitly.
- Make `check_doc_links.py` allow plain or backticked mentions of those
  canonical surfaces while continuing to reject ordinary file references.

## Next Habit

When a prose validator rejects a path-like token in a public skill, classify
whether the token is a repo-local file reference or a portable canonical surface
before choosing between links, adapter policy, or prose rewrite.

## Persisted

yes `charness-artifacts/retro/2026-04-24-canonical-markdown-surfaces.md`
