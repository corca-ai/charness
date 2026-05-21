# Usage Episodes Disabled Handoff Critique
Date: 2026-05-21

## Execution

- status: blocked
- Fresh-Eye Satisfaction: blocked host signal: active delegation policy did not allow `spawn_agent` for this turn without a user subagent request.
- host signal: active developer delegation rule restricts `spawn_agent` use to turns where the user asks for subagents, delegation, or parallel agent work; this turn requested an adapter and handoff update only.
- Target: short code/config and handoff critique

## Change

Add `.agents/usage-episodes-adapter.yaml` with `enabled: false` and update
`docs/handoff.md` so the next session defines the Charness usage-episode
vocabulary before enabling runtime capture.

## Findings

- Act Before Ship: keep the adapter disabled, because enabling it now would make
  `validate_usage_episodes.py` require `.charness/usage-episodes/usage_episode.jsonl`
  before a runtime emitter and vocabulary exist.
- Act Before Ship: make the handoff say `disabled`, not `no_adapter`, so the
  next operator sees intentional opt-out state.
- Bundle Anyway: compress stale #183 handoff detail while adding the new next
  step; the handoff was already near the size budget and overly historical.
- Valid But Defer: runtime emitter design belongs after vocabulary selection.

## Deliberately Not Doing

- Do not add a PR CI workflow in this slice; the maintainer explicitly paused
  that policy change.
- Do not add sample runtime JSONL. `.charness/usage-episodes/` is local
  generated state, and checked-in fixtures should be intentional.

## Next Move

Validate adapter/docs, run the slice closeout, commit the disabled adapter,
handoff update, and critique artifact together.
