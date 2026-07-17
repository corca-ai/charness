# Charness Handoff

## Workflow Trigger

- With no explicit task, invoke `charness:handoff` and run chunked routing over
  this baton and live issues. Restart first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- 2026-07-17 closed the prove-dogfood goal
  ([artifact](../charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md),
  Status: complete): the #444 deferred F5/F6 polish landed (`963e147c` —
  pause-only hook failures now name the `AI-provenance:` remedy, plus the
  template↔regex pause-vocabulary drift test), and the `prove` dogfood row was
  promoted to `reviewed` on live consumer-run evidence with `prove` added to
  `review_required_skills` (`b1b74e0c`); the md required list now mirrors the
  json under a new drift pin.
- These commits are LOCAL ONLY (autonomous session, no push approval): the
  first operator action is deciding the push (queued with unblock action in
  the goal's `## Operator Decision Queue`).
- v1.2.0 remains the published/install surface; no release change this session.
- 2026-07-17 operator decisions (chat): the subagent model/effort request is
  now a PER-HOST contract (AGENTS.md `Subagent Delegation`: Codex hosts request
  `gpt-5.6-terra`/`medium`/`fork_turns: "none"`; Claude Code hosts use typed
  agents + session-model inheritance and no longer record a not-exposed
  limitation); D18 was passed over (stays pending, same reopen trigger); the
  dogfood scaffold fallback-prompt warning was applied immediately
  (`prompt_fallback` flag + advisory stderr warning + tests).

## Next Session

1. Operator: push the local commits (`git push origin main`; changed-line
   mutation-coverage marker is fresh) or fold them into the next release cut.
2. D18 disposition (passed over 2026-07-17, still pending with the same
   reopen trigger) — see the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`.
3. Deferred affordance convergence per the affordance spec's Deferred
   Decisions (`next_action` rename, `next_steps` split, prefix unification).

## Discuss

- Optional under the 2026-07-17 per-host split: a live Codex-host session can
  still add provider-applied evidence that the Codex-scoped
  `gpt-5.6-terra`/`medium` request is honored; the split already removed the
  Claude-side not-exposed noise, so this is evidence polish, not a blocker.

## References

- [prove-dogfood goal closeout](../charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md)
  · [disposition review](../charness-artifacts/critique/2026-07-17-prove-dogfood-via-444-polish-disposition-review.md)
  · [session retro](../charness-artifacts/retro/2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md)
  · [release state](../charness-artifacts/release/latest.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: the unpushed-local-commits state (it changes the first
  operator action), the two carried operator decision queues, and the
  requested-vs-applied reviewer boundary.
- Refresh non-claims: prove's `reviewed` status is one live consumer run on
  one host (non-claims in the registry row); no push/release/provider write
  occurred this session; the #444/#442 history detail spilled to the goal
  artifact and resolution critiques.
