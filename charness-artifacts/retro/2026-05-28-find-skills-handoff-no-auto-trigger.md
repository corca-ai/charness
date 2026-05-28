# Retro: find-skills → handoff routing did not auto-trigger on `@docs/handoff.md` pickup

Date: 2026-05-28

## What happened

Session opened with the user `@docs/handoff.md` mentioning the handoff
artifact. The agent read the file content (via the host's @-mention expansion)
and answered in prose without first calling `charness:find-skills` or
`charness:handoff`, even though `CLAUDE.md` "Start Here" mandates
`find-skills` as the first call of every task-oriented session and the
handoff itself names `charness:find-skills` then `charness:handoff` as the
`Workflow Trigger`.

The user pointed out the miss explicitly: "왜 find-skills → 핸드오프 스킬이
발동하지 않았지? 이거 자체가 setup 스킬의 개선감이네요."

## Why it matters

The `@<path>` host pattern is a common pickup shape — the user is using the
handoff artifact as the entry point — but the host-injected `CLAUDE.md`
"Start Here" prose did not deterministically nudge the agent into the named
workflow before it answered. Prose instruction alone lost to the @-mention's
"here is content, react to it" affordance.

## Setup skill improvement candidate

`setup` owns the `CLAUDE.md` / `AGENTS.md` "Start Here" surface. The current
prose carries the right intent but does not survive the @-mention pickup
shape. Candidate improvements (not yet decided which is right):

- Make the Start Here pattern explicit about pickup shapes that look like
  pure content (`@docs/handoff.md`, raw artifact paste) and name them as
  workflow triggers, not just reading.
- Have `setup` provision (or `handoff` co-own) a tiny `Workflow Trigger`
  line at the top of `docs/handoff.md` so the artifact itself re-asserts
  `find-skills → handoff` as the first action when the agent reads it. The
  current handoff already has this line; the miss was the agent skipping
  past it after the host expanded the @-mention.
- A hook-based nudge is out of scope here (host-side affordance).

## Next-time checklist

- **workflow**: when the first user signal in a session is `@<artifact>`
  or a pasted artifact body, treat it as pickup and run `find-skills` first,
  then the workflow the artifact names — do not let the visible content
  short-circuit routing.
- **capability**: revisit `setup`'s `CLAUDE.md` Start Here block to make
  it more resistant to @-mention short-circuiting. Open a candidate
  issue if the next session confirms this is recurring.
