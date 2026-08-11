# Charness Handoff

## Workflow Trigger

- **Read [recent lessons](../charness-artifacts/retro/recent-lessons.md) BEFORE acting**, then
  `## Next Session`. The digest is measurably lossy and the correction is filed — see
  [thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md), not this file.
- No goal is running. Unpushed commits: `git log --oneline origin/main..HEAD` (23). A push
  grant has been declined every session for several sessions — state the count, do not ask.

## Continuation Capability

- **Run the REPO's script, never `~/.agents/src/charness`.** Last session reported a shipped
  ruling as pending because it checked the installed copy, which lags the source.
  `recent-lessons.md:11` names this trap; it still cost a wrong claim to the operator.
- **A "not executed" banner on an artifact is a claim, and it rots.** Same incident, same
  cause. Per-section status or nothing.
- **The round that reads the REPAIRS is the one that catches you.** Round 1 found a pin I had
  replaced with a tautology; round 2 found that round 1's own repair had silently moved four
  enforced counts in the masking direction. Both were verified-then-wrong, not sloppy.
- **A removal proposal without its consumer grep is malformed.** Nine verifiers under this rule
  refuted 8 of 13 candidates on real consumers.
- **Before writing a list, a pin, or a key: does a surface here already know the answer?**
  Shipped five times, fixed four without noticing it was one class —
  [Declared Where Derivable](./conventions/implementation-discipline.md#declared-where-derivable).
- **An exhaustiveness gate cannot tell you a row is TRUE** — stated where it bites, under the
  [classification table](./conventions/validator-timing-layers.md#classification-table).

## Current State

- **24 open issues.** Gate **90/0 re-measured at `8d4337c5`**, then 89/0 + 1 UNPROVEN on each
  subsequent dirty-worktree run; `check-changed-line-mutation-coverage` returns `clean` once
  committed. Re-take the baseline; do not inherit this line.
- **The pickup-deletion ruling SHIPPED at `a24b0155`.** Not pending. The plan artifact now
  carries `## Execution status` per section.
- Landed: `c9b9e243` `322664d5` `50975458` `85fc6770` `5c680650` `eae29aad` — dead-code
  deletions, pin repairs, an enforcement-tuple narrow, the commit-gate scoping, and the six
  rulings. **Nothing deleted a gate, validator, baseline, or reference doc.**
- **`check_title_slug_drift` is DELETED** (4 paths + its compatibility test) under ruling 4.
  It owes a release-note line naming the removal at the next bump, which is a MAJOR: it was a
  shipped entrypoint. The `title-slug coherence` critique lens stays and is its replacement.
- **`#582`-`#585` CARRY their own status. CLASS REMAINS, 4/4.** Do not close them.
- **D53's reopen trigger is NOT in-repo observable** ([deferred](./deferred-decisions.md)).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **All six operator decisions are RULED and unexecuted** —
   [six-operator-rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md).
   Do not re-litigate; four overturned the framing handed up. Start with ruling 1, whose
   design is measured, not just decided: scan shell fences plus inline code, skip comment
   lines, and the derived subcommand check finds **two live defects** (`charness verify`,
   `charness propose` — neither exists nor ever did) at zero false positives.
2. **Ruling 6 is the largest slice** and the only one needing a schema change:
   `inventory_boundary_bypass_lib` records no call-site line info, so the payload, its
   public validator, and both baselines move together.
3. **Redesign the recent-lessons SELECTION policy — operator has the design.** Do not add a
   filter; that stacks a heuristic on a heuristic. Measured this session: of 884
   `next_improvement` candidates the top two by weight are content-free bookkeeping
   ("This retro plus the recent-lessons digest"), because every retro emits that line and
   recurrence boost rewards it. It is still occupying a slot in the current digest, and it
   outranked the improvement naming the digest's own defect.
4. **`#587` — edit, do not close.** Mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`.
5. **`#546` phase 2 — the adapter `conditional:` marker.**
6. **Waves 2-3.** `#539` `#581` `#588` `#528` `#589` `#542`, then `#586` `#590` `#593`-`#599`
   `#550` `#527`. Umbrellas wait on their own work.

## Discuss

- **Does a pattern-match decide what someone MEANT?** `--intent` replaced
  `should_fire_chunker`; the same shape survives in `setup_skill_routing_lib`'s
  semantic-completeness regex (ships to consumers), `chunked_routing_parser`,
  `classify_push_diff_lib`. Form validators are NOT in this class.
- **`>= 35` is a ratchet floor that goes slack at 36.** Same shape as every count pin this
  repo keeps rediscovering. Is a floor that must be hand-bumped better than the pin it replaced?

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md)
- [Umbrella class disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md) — per-section execution status, the sweep with its consumer greps, and the pickup-deletion ruling.
- [Harness-improvement thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md) — the digest slot-policy finding and the autonomy precondition.
- [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — all six with the evidence that produced them, and the two feasibility measurements.
- [Validator timing layers](./conventions/validator-timing-layers.md) — the live registry and what its gate cannot check.
- [This session's retro](../charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md) — six corrections, zero self-initiated, and the Engelbart lens on the class that shipped without a tool.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
