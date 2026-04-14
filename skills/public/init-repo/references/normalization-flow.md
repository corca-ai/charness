# Normalization Flow

This reference covers the normalization moves for repos whose operating docs are
incomplete, duplicated, or inconsistent.

## Goal

Prefer rewriting and consolidating existing truth surfaces over dropping fresh
parallel templates.

## Checks

- is `README.md` current and minimally honest
- if the repo ships an installable surface, do `README.md` and `INSTALL.md`
  name probe semantics without collapsing health, readiness, and
  discoverability into one command
- if the repo wants durable retrospective pickup, is there one stable retro
  memory seam instead of scattered weekly/session notes
- do `AGENTS.md` and `CLAUDE.md` express one clear host-facing contract
- does `docs/roadmap.md` exist when the repo needs short-horizon planning
- can a human operator tell what to do from `docs/operator-acceptance.md`
- are there duplicate docs that should collapse into one source of truth

## Decision Rule

- missing surface: scaffold it
- one missing core surface in an otherwise mature repo: do the smallest
  targeted repair and keep the rest of the operating docs intact
- stale but useful surface: rewrite it
- duplicate surface: collapse it into the more honest source of truth

If the repo already has a strong durable story and the main problem is alignment
across multiple docs, prefer `narrative` as the next deeper skill.
