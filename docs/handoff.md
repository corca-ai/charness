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
- Charness still requests `gpt-5.6-terra`/`medium`/`fork_turns: "none"` for
  subagents; this host exposed no such override (typed `bounded-reviewer`
  spawns, host-defaulted) — request contract, not applied proof.

## Next Session

1. Operator: push the local commits (`git push origin main`; changed-line
   mutation-coverage marker is fresh) or fold them into the next release cut.
2. Remaining operator decisions from the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`: the D18 disposition and the live Codex probe
   question.
3. File-or-apply the dogfood scaffold fallback-prompt warning (a row whose
   prompt equals the skill description means `PROMPT_HINTS` lacks an entry;
   details in the 2026-07-17 goal's Operator Decision Queue).
4. Deferred affordance convergence per the affordance spec's Deferred
   Decisions (`next_action` rename, `next_steps` split, prefix unification).

## Discuss

- Whether a live Codex experiment can add provider-applied reviewer-profile
  evidence without confusing it with the requested configuration contract
  (queued with an owner and revisit trigger in the 2026-07-16 goal's Operator
  Decision Queue).

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
