# Greenfield Flow

This reference covers the minimum honest flow for a repo with little or no
durable operating surface.

## Goal

Create the smallest honest repo surface that lets a maintainer and an agent
understand what this repo is, where it is going next, and how to take it over.

## Minimum Questions

Ask only what materially changes the first scaffold:

1. What is this repo for right now?
2. Who is the primary user or operator?
3. What are the next 1-3 concrete work items?
4. If a human had to take over tomorrow, what would they need to do first?

If the user already answered these in the session or the repo files, do not
re-ask them.

## Expected Core Surfaces

- `<repo-root>/README.md`
- `<repo-root>/AGENTS.md`
- `CLAUDE.md` symlink to `<repo-root>/AGENTS.md`
- consumer-owned documentation index at `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->

Add `<repo-root>/docs/roadmap.md` only when active ordered work is evidenced or
requested. Add `<repo-root>/docs/operator-acceptance.md` only when a real
install, deployment, or operator takeover path exists; neither is a default
greenfield surface.

Add separate bootstrap and uninstall docs only when the repo actually exposes
an installable plugin, package, or operator-facing install contract.

Add retro memory only when the repo wants that seam from day one. If it wants
the optional compact digest, seed `<repo-root>/.agents/retro-adapter.yaml` and
`<repo-root>/charness-artifacts/retro/recent-lessons.md` with
`$SKILL_DIR/scripts/seed_retro_memory.py` rather than hand-writing them; a
ledger-only repo may declare `summary_path: null`.

If those docs are needed, seed a small explicit probe surface early so future
wrappers or operators do not have to reverse-engineer:

- install or update path
- binary healthcheck
- machine-readable discovery if it exists
- repo or install readiness
- local discoverability or materialization step
