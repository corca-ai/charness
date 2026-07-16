# Charness Handoff

## Workflow Trigger

- With no explicit task, invoke `charness:handoff` and run chunked routing over
  this baton and live issues. Restart first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- 2026-07-17 landed the CLI affordance slice
  ([spec](../charness-artifacts/spec/cli-output-affordance-contract.md)):
  task rejections and persisted task state carry a recovering `next_step`;
  the CLI reference header documents the affordance convention.
- 2026-07-17 closed #444 (commit `d7747a09`, pushed) and #442 (four slices
  `d312aa6b`/`9faef3b9`/`cc71dbb1`/`c07a575c` plus the closeout commit): the
  commit-msg hook now carves out pausing resolution briefs (provenance-only
  floor, full ledger on close-keyword overlap) and reads bold
  `**Classification**:` lines; spec/critique/announcement dedup to
  185/188/182 of the 200 cap with single-ownership pointers (verdict enum and
  slice ledger → `prove`, spawn enforcement → the shared fresh-eye reference,
  delivery mechanics → `delivery-seams.md`); prove gained the
  claim-fidelity substance floor (`outcome-assertions.json`).
- prove dogfood promotion stays `planned` (blocked): the installed plugin
  surface predates the #439 split — this session's live routing probe returned
  the concrete host signal `Unknown skill: charness:prove`. Promotion needs
  `charness update` plus a session restart, then a real consumer-prompt run;
  only after `reviewed` may `prove` join `review_required_skills`.
- v1.1.0 remains public at tag `55529413`; host sessions may hold stale
  injected skill paths until restart.
- Charness still requests `gpt-5.6-terra` with `medium` effort and
  `fork_turns: "none"` for its subagents. This host exposed no such override
  (typed `bounded-reviewer` spawns, host-defaulted); request contract, not
  applied proof.

## Next Session

1. After `charness update` + restart: run the prove dogfood consumer prompt on
   a real slice, promote `review_status` to `reviewed` with observed evidence,
   and add `prove` to `review_required_skills` (#442 recorded this as the one
   deferred sub-item; the substance floor is already in place).
2. Remaining operator decisions from the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`: the D18 disposition and the live Codex probe
   question.
3. Deferred from #444's critique (fails closed, separable): pause-case
   header/footer polish in `_format_failure`, and a template-vs-regex
   pause-vocabulary drift test.
4. Deferred affordance convergence per the affordance spec's Deferred
   Decisions (`next_action` rename, `next_steps` split, prefix unification).

## Discuss

- Whether a live Codex experiment can add provider-applied reviewer-profile
  evidence without confusing it with the requested configuration contract
  (queued with an owner and revisit trigger in the 2026-07-16 goal's Operator
  Decision Queue).

## References

- [#444 resolution critique](../charness-artifacts/critique/2026-07-17-issue-444-resolution-critique.md)
  · [#442 resolution critique](../charness-artifacts/critique/2026-07-17-issue-442-resolution-critique.md)
  · [release state](../charness-artifacts/release/latest.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: the [prove-promotion blocker](./public-skill-dogfood.json),
  deferred #444 polish, and the requested-vs-applied reviewer boundary.
- Refresh non-claims: the [prove dogfood row](./public-skill-dogfood.json)
  stays `planned`; no provider-applied model/effort claim; #442 caps are
  commit-time counts.
