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

The first implementation batch has landed:

- `probe_host_logs.py` reports honest Claude/Codex metric availability
- `refresh_recent_lessons.py` refreshes `recent-lessons.md` from the latest
  durable retro artifact
- `persist_retro_artifact.py` now auto-refreshes the digest when a durable
  retro artifact is written
- `init-repo` can seed `.agents/retro-adapter.yaml` and
  `charness-artifacts/retro/recent-lessons.md` for repos that opt into durable retro
  memory
- `quality` now treats skill ergonomics as an explicit lens with an advisory
  inventory helper
- `retro` can now auto-trigger a bounded `session` retro for configured
  repeat-trap seams via adapter-declared surface ids and path globs

The next slice should only deepen this seam where it changes behavior rather
than prose volume: for example making ergonomics stronger than advisory in some
repos, or deciding how release-time real-host proof should feed back into retro
memory.

## Fixed Decisions

- Keep retrospective memory local-first and explicit. No mandatory remote
  telemetry, no hidden background services, and no host-specific global writes
  outside declared adapter paths.
- Keep `charness-artifacts/retro/recent-lessons.md` as the stable compact digest path
  when a repo opts into this pattern.
- Implement the host-log probe as a standalone helper first. `retro` may
  consume it later, but this slice should not make host-log collection an
  always-on retro dependency.
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

- Should the host-log probe read Codex's SQLite-backed runtime logs directly,
  or shell out to the repo-owned `codex-state-logs` helper when the sibling
  source tree is available?
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
  `summary_path: charness-artifacts/retro/recent-lessons.md`.
- `init-repo` also scaffolds AGENTS memory that points at the recent-lessons
  digest when retro memory is enabled.
- `retro` owns a helper that refreshes `summary_path` from the latest durable
  retro in a bounded, predictable shape.
- `retro` can optionally include an `Efficiency Signals` section when a
  declared local script returns real data, and can explicitly report
  `unavailable` when the host does not expose that data.
- The first implementation slice ships a standalone helper at
  `skills/public/retro/scripts/probe_host_logs.py`.
- The second implementation slice ships a standalone helper at
  `skills/public/retro/scripts/refresh_recent_lessons.py`.
- The third implementation slice ships `skills/public/init-repo/scripts/seed_retro_memory.py`
  so new repos can opt into the same seam without hand-writing it.
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
- `python3 skills/public/retro/scripts/probe_host_logs.py --home <fixture-home>`
  returns structured per-host metric availability without requiring sibling
  source trees or network access.
- `quality` tests prove that skill ergonomics guidance is reachable through the
  current review contract when skill packages are touched.

## Canonical Artifact

- This document: `docs/retro-self-improvement-spec.md`

## First Implementation Slice

1. Teach `quality` to call out skill ergonomics explicitly when skills are in
   scope, using existing `skill-quality` and `public-skill-validation`
   posture as the base. Landed.
2. Decide whether a thin retro orchestration helper should call
   `refresh_recent_lessons.py` automatically when durable retro artifacts are
   updated, or whether the current explicit script boundary is the intended
   product posture. Landed in favor of auto-refresh through
   `persist_retro_artifact.py`.
3. Decide whether `init-repo` should also wire the recent-lessons seam into
   scaffolded `AGENTS.md` memory by default when retro memory is enabled.
   Landed.

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

## Confirmed Local Host-Log Surfaces

Inspection on this machine found a sharper split than the earlier generic note
implied.

### Claude

- Thin history file:
  `~/.claude/history.jsonl`
  This appears to be navigation / prompt history only and is not a trustworthy
  source for efficiency metrics.
- Rich project logs:
  `~/.claude/projects/<project>/<session>.jsonl`
  These logs do expose structured assistant usage. On this machine they include:
  - `message.usage.input_tokens`
  - `message.usage.cache_creation_input_tokens`
  - `message.usage.cache_read_input_tokens`
  - `message.usage.output_tokens`
  - `message.usage.server_tool_use.web_search_requests`
  - `message.usage.server_tool_use.web_fetch_requests`
  - message content items of type `tool_use`

Implication:

- token counts: available
- server web-tool counts: available
- generic tool-call counts: probably derivable by counting `tool_use` items
- turn counts: derivable, but not via one stable top-level field

### Codex

- Thin prompt history:
  `~/.codex/history.jsonl`
  This looks like prompt history, not reliable efficiency telemetry.
- Runtime TUI log:
  `~/.codex/log/codex-tui.log`
  On this machine it clearly contains timestamps, `turn.id=...`, and
  `ToolCall: ...` lines.
- Runtime SQLite log store:
  `~/.codex/logs_2.sqlite`
  This stores rendered runtime log lines, including thread ids and the same
  textual bodies visible in the TUI log.
- Sibling source tree:
  `../codex`
  Source inspection confirms that Codex has a real token-usage event in the
  app-server protocol (`ThreadTokenUsageUpdatedNotification`) and a repo-owned
  log client (`codex-state-logs`) for the SQLite log store.

Implication:

- timestamps / coarse duration: available from TUI log or SQLite log store
- turn counts: available from `turn.id=` lines
- tool-call counts: available from `ToolCall:` lines
- token counts: supported in Codex internals, but not yet proven to be emitted
  into the default local logs inspected here; treat as `unavailable` until the
  probe proves a stable local path

## Probe Design Consequences

The host-log probe should therefore report per-host, per-metric availability
instead of one blanket "metrics supported" answer.

- Claude probe:
  prefer project JSONL over history JSONL
- Codex probe:
  prefer the SQLite/TUI runtime logs and classify token counts separately from
  turn/tool-call counts
- Cross-host contract:
  return structured `available`, `derivable`, or `unavailable` with the source
  path or helper name that justified the status
