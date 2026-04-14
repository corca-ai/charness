# Retro Self-Improvement Spec

## Problem

`charness` now has the beginnings of durable retrospective memory, but it still
depends too much on explicit human intent and manual upkeep:

- a user can ask for `retro`, but ordinary `impl` or support-tool work does not
  reliably leave behind a compact lesson digest
- new repos created through `init-repo` do not yet inherit the same
  `recent-lessons` memory seam that `charness` now uses for itself
- `retro` can narrate waste and improvement ideas, but it does not yet own a
  stable mechanism for refreshing a compact next-session digest
- efficiency signals such as duration, turn count, token count, or tool-call
  count are not modeled honestly yet; some may be derivable from host logs, but
  that availability differs by host and version
- `quality` already reviews skill package drift, but it does not yet make skill
  ergonomics explicit enough as a first-class lens

The result is that users only benefit from retrospective accumulation when they
explicitly ask for it or when a maintainer manually persists the lesson.

## Current Slice

Design the next portability-safe step so `charness` can help repos learn from
past sessions with less manual ceremony, without pretending that all hosts
expose the same metrics or that every task should pay the cost of a full retro.

## Fixed Decisions

- Keep retrospective memory local-first and explicit. No mandatory remote
  telemetry, no hidden background services, and no host-specific global writes
  outside declared adapter paths.
- Keep `skill-outputs/retro/recent-lessons.md` as the stable compact digest path
  when a repo opts into this pattern.
- Extend `init-repo` so newly scaffolded repos can inherit the same memory seam:
  a retro adapter with `summary_path`, an AGENTS memory entry, and a lightweight
  digest file.
- Let `retro` own digest refresh. Weekly and session retros may both update the
  compact digest when `summary_path` is configured.
- Treat efficiency metrics in tiers:
  - tier 1: portable repo-native proxies such as retries, failed closeouts,
    repeated validations, or command-to-green churn
  - tier 2: host-log-derived metrics such as duration or skill frequency when a
    stable local log exists
  - tier 3: turns, tokens, or tool-call counts only when a host exposes them
    through a stable, parsable, declared local source
- Never fabricate turn, token, or tool-call counts. If the host log does not
  expose them, `retro` must say so plainly and fall back to portable proxies.
- Expand `quality` so skill ergonomics are an explicit review lens when a repo
  authors skills:
  - concise `SKILL.md` core
  - progressive disclosure honesty
  - unnecessary mode/option pressure
  - trigger overlap or undertrigger risk
  - repeated manual ritual that should become a script
- Do not force every recommended external tool to become a support skill.
  Discoverability and support-backing remain separate design axes.
- Consider Jef Raskin a candidate anchor only where it sharpens concrete
  behavior around discoverability, modelessness, and next-step clarity rather
  than serving as decorative philosophy.

## Premortem

If this work is implemented badly, the likely failure modes are:

- `retro` becomes a heavy always-on tax, so users stop invoking it and agents
  start skipping it
- host-specific telemetry leaks into the portable public core and breaks on one
  host while appearing authoritative on another
- the digest becomes another hand-maintained stale file that no workflow owns
- `init-repo` scaffolds too much policy, making small repos pay for a
  sophistication they do not want
- `quality` starts judging style preferences instead of real ergonomics and
  progressive-disclosure honesty
- the system claims "self-improvement" while only writing more prose and not
  actually changing future behavior or next-step selection

## Probe Questions

- Which local Claude or Codex logs, if any, stably expose duration, turn,
  token, or tool-call counts in a way that can be parsed by a repo-owned helper
  script without relying on internal unsupported formats?
- Should `impl` trigger a short session retro only on explicit misses and
  corrections, or also after bounded slice closeout when the repo opted into
  automatic retrospective accumulation?
- Should `recent-lessons.md` be rewritten entirely from the latest retro, or
  updated as a bounded rolling digest that preserves a small set of recurring
  traps?
- How much of skill ergonomics should live in `quality` versus
  `public-skill-validation`?
- Which skill families would actually benefit from a Jef Raskin anchor:
  `create-cli`, `find-skills`, `init-repo`, or a smaller discoverability-only
  reference?

## Deferred Decisions

- Whether `retro` should add a machine-readable `recent-lessons.json` sibling
  for downstream automation
- Whether host-log-derived metrics should live behind one shared helper or
  separate per-host helpers
- Whether `find-skills` should surface retrospective memory hints directly when
  a repo advertises them
- Whether `quality` should eventually fail on some skill ergonomics issues or
  keep them advisory-only

## Non-Goals

- Building a full `gstack`-style telemetry stack inside `charness`
- Requiring background daemons or remote analytics services
- Guaranteeing that every repo becomes "smarter" without maintaining any
  durable artifacts
- Treating turn or token counts as mandatory quality or retrospective metrics
- Solving all skill-trigger optimization in this slice

## Constraints

- Keep the public core portable across hosts.
- Keep repo docs in English.
- Do not claim metric availability unless a declared local source proves it.
- Keep weekly retro narrative-friendly when no metrics exist.
- Avoid making ordinary `impl` work materially slower by default.
- Keep handoff concise; use dedicated retro artifacts for accumulated lessons.

## Success Criteria

- `init-repo` can scaffold a repo with a retro adapter that includes
  `summary_path: skill-outputs/retro/recent-lessons.md`.
- `init-repo` also scaffolds AGENTS memory that points at the recent-lessons
  digest when retro memory is enabled.
- `retro` owns a helper that refreshes `summary_path` from the latest durable
  retro in a bounded, predictable shape.
- `retro` can optionally include an `Efficiency Signals` section when a
  declared local script returns real data, and can explicitly report
  `unavailable` when the host does not expose that data.
- A repo-owned helper can probe Claude/Codex local logs and return structured
  availability status for:
  - duration
  - turn count
  - token count
  - tool-call count
- `quality` explicitly reviews skill ergonomics when skills are in scope.

## Acceptance Checks

- `python3 skills/public/retro/scripts/resolve_adapter.py --repo-root .`
  returns `summary_path` when configured.
- `init-repo` tests prove that the retro memory seam can be scaffolded into a
  fresh repo.
- `retro` tests prove that the digest refresh helper updates
  `recent-lessons.md` deterministically from a bounded source artifact.
- Host-log probe tests prove honest degradation:
  unavailable metrics return structured `unavailable`, not fake zeros.
- `quality` tests prove that skill ergonomics guidance is reachable through the
  current review contract when skill packages are touched.

## Canonical Artifact

- This document: `docs/retro-self-improvement-spec.md`

## First Implementation Slice

1. Extend `init-repo` so retro memory scaffolding is opt-in but first-class:
   retro adapter `summary_path`, digest file, and AGENTS memory entry.
2. Add a repo-owned retro helper that refreshes `recent-lessons.md` from the
   most recent durable retro artifact.
3. Add a narrow host-log probe helper that reports which efficiency metrics are
   actually available for the current host and binary.
4. Teach `quality` to call out skill ergonomics explicitly when skills are in
   scope, using existing `skill-quality` and `public-skill-validation`
   posture as the base.

## Notes On Existing Signals

`gstack` is a useful design reference, but it is not a drop-in contract.
Its local telemetry clearly tracks skill name, duration, outcome, browse use,
and timeline events. In the current inspected surface it does not provide
portable proof that turn, token, or tool-call counts are always available.

That means `charness` should copy the honesty pattern, not the full stack:

- local-only by default
- stable explicit file paths
- structured `available` vs `unavailable`
- no claims beyond the actual host logs
