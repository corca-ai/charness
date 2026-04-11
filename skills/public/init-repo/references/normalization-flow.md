# Normalization Flow

Use this when a repo already has some operating docs, but they are incomplete,
duplicated, or inconsistent.

## Goal

Prefer rewriting and consolidating existing truth surfaces over dropping fresh
parallel templates.

## Checks

- is `README.md` current and minimally honest
- do `AGENTS.md` and `CLAUDE.md` express one clear host-facing contract
- does `docs/roadmap.md` exist when the repo needs short-horizon planning
- can a human operator tell what to do from `docs/operator-acceptance.md`
- are there duplicate docs that should collapse into one source of truth

## Decision Rule

- missing surface: scaffold it
- stale but useful surface: rewrite it
- duplicate surface: collapse it into the more honest source of truth

If the repo already has a strong durable story and the main problem is alignment
across multiple docs, prefer `narrative` as the next deeper skill.
