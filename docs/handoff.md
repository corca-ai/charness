# Charness Handoff

## Workflow Trigger

- With no explicit task, skip chunked routing and continue with `spec` → `impl`
  on the operator-directed affordance convergence (Next Session item 1, breaking
  changes allowed); the chunker resumes after that item closes. Restart first
  only when testing installed-plugin behavior; an explicit user task keeps its
  own authority.

## Current State

- 2026-07-17 closed the prove-dogfood goal
  ([artifact](../charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md),
  Status: complete): the #444 deferred F5/F6 polish landed (`963e147c` —
  pause-only hook failures now name the `AI-provenance:` remedy, plus the
  template↔regex pause-vocabulary drift test), and the `prove` dogfood row was
  promoted to `reviewed` on live consumer-run evidence with `prove` added to
  `review_required_skills` (`b1b74e0c`); the md required list now mirrors the
  json under a new drift pin.
- v1.3.0 is public (operator said "푸시 릴리즈"): release commit `39a860ee`,
  tag `v1.3.0`, distinct-channel https confirmation 200, fresh-checkout
  probes passed, install refreshed via `charness update`; verification record
  in [release state](../charness-artifacts/release/latest.md). The first
  publish attempt was refused by the release quality battery; the three gate
  failures were repaired at root in `b0f4ae74` before the rerun.
- 2026-07-17 operator decisions (chat): the subagent model/effort request is
  now a PER-HOST contract (AGENTS.md `Subagent Delegation`: Codex hosts request
  `gpt-5.6-terra`/`medium`/`fork_turns: "none"`; Claude Code hosts use typed
  agents + session-model inheritance and no longer record a not-exposed
  limitation); D18 was passed over (stays pending, same reopen trigger); the
  dogfood scaffold fallback-prompt warning was applied immediately
  (`prompt_fallback` flag + advisory stderr warning + tests).

## Next Session

1. OPERATOR-DIRECTED (2026-07-17 chat): run the affordance convergence per the
   [affordance spec](../charness-artifacts/spec/cli-output-affordance-contract.md)
   Deferred Decisions — `next_action` rename, `next_steps` split, prefix
   unification — with **breaking changes allowed** (no compatibility alias;
   see the APPROVED note in the spec). Start here even on a bare pickup.
2. Restart hosts to load the installed v1.3.0 surface before testing
   installed-plugin behavior.
3. D18 disposition (passed over 2026-07-17, still pending with the same
   reopen trigger) — see the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`.

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

- Refresh kept: the per-host reviewer contract in `AGENTS.md`, the
  published-v1.3.0 restart-to-load state (first action), and the carried D18
  decision.
- Refresh non-claims: the [dogfood registry](./public-skill-dogfood.json)'s
  prove `reviewed` status is one live consumer run on one host; no
  push/release/provider write occurred at refresh time; the #444/#442 history
  detail spilled to the goal artifact and resolution critiques.
