# Normalization Flow

This reference covers the normalization moves for repos whose operating docs are
incomplete, duplicated, or inconsistent.

## Goal

Prefer rewriting and consolidating existing truth surfaces over dropping fresh
parallel templates.

## Checks

- is [`README.md`](../../../../README.md) current and minimally honest
- if the repo ships an installable surface, do [`README.md`](../../../../README.md) and the repo-local bootstrap guidance
  name probe semantics without collapsing health, readiness, and
  discoverability into one command
- if the repo wants durable retrospective pickup, is there one stable retro
  memory seam instead of scattered weekly/session notes
- do [`AGENTS.md`](../../../../AGENTS.md) and `CLAUDE.md` express one clear host-facing contract
- when the repo requires bounded fresh-eye or premortem-style subagent review,
  does [`AGENTS.md`](../../../../AGENTS.md) say that this stop gate is already delegated and that
  host spawn restrictions must stay visible
- when adapter-declared policy sources imply delegated review, does
  `inspect_repo.py` emit a `recommendations[]` queue item with priority,
  confidence, evidence, suggested action, and acknowledgement state
- does `docs/roadmap.md` exist when the repo needs short-horizon planning
- can a human operator tell what to do from [`docs/operator-acceptance.md`](../../../../docs/operator-acceptance.md)
- are there duplicate docs that should collapse into one source of truth

## Decision Rule

- missing surface: scaffold it
- one missing core surface in an otherwise mature repo: do the smallest
  targeted repair and keep the rest of the operating docs intact
- stale but useful surface: rewrite it
- duplicate surface: collapse it into the more honest source of truth

Task-completing normalization should run bounded delegated review after
deterministic inspection. Use host-instruction policy, operating-surface
adapter fit, and operator takeover flow as the default lenses. Help, routing,
and raw-inspection calls do not need that review gate.

If the repo already has a strong durable story and the main problem is alignment
across multiple docs, prefer `narrative` as the next deeper skill.
