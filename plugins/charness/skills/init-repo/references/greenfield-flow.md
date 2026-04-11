# Greenfield Flow

Use this when the repo has little or no durable operating surface.

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

## Expected Surfaces

- `README.md`
- `AGENTS.md`
- `CLAUDE.md` symlink to `AGENTS.md`
- `docs/roadmap.md`
- `docs/operator-acceptance.md`

Add `INSTALL.md` and `UNINSTALL.md` only when the repo actually exposes an
installable plugin, package, or operator-facing install contract.
