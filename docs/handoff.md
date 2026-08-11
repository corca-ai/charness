# Charness Handoff

## Workflow Trigger

- **Read [recent lessons](../charness-artifacts/retro/recent-lessons.md) BEFORE acting.**
  Last session read it and applied none of it, and paid seven refuted proposals for that.
- No goal is running. Commits are local and unpushed; ask for a push grant. Then
  `## Next Session`.

## Current State

- **23 open issues; closing GENERATES issues** (Aug 7-10: created 60, closed 42).
- **`#572` CLOSED as `consolidated` into `#590`.** **Do NOT read the green cron on
  `ed90c1f3` as recovery** — it predates `#590`'s diagnostic `739a2a3e`.
- **`#582`-`#585` CARRY their own status** (per-member outcome + disposition in each body).
  **CLASS REMAINS, 4/4.** Do not close them.
- **Gate green: 89/0, 1 UNPROVEN** — baseline taken BEFORE any deletion. Filed `#596`
  (probe-pin tax; tracker `#536` is closed COMPLETED), `#597` (`check_quality_tool_fixtures`
  passes on an empty set, unwired), `#598` (a gate blocking on a word preference + a
  five-week-unactioned reclassification audit).
- **D53/D54/D55** in [deferred-decisions](./deferred-decisions.md) each name a reopen
  trigger; D53's is NOT in-repo observable and says so.
- The evidence-boundary crosswalk was RETIRED by operator ruling; do not rebuild it
  ([record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md)).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **OPERATOR RULING — delete the pickup ambiguity heuristic and both eval specs.** It
   guesses intent by COUNTING `## Next Session` entries. The edge that makes both specs
   fall out for free: `claim_fidelity_lib.py:283-301` AST-scans the planner for any
   `references/*.md` literal REGARDLESS of branch, so `continuation-sequence.md` must also
   leave `plan_handoff_run.py:28`. Keep the substance judge. Scope + verified consumer
   sets: [plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md).
2. **Then the recorded sweep, AS A DYNAMIC WORKFLOW ON SONNET** (operator-directed): 3
   deletions + 2 reworks, fanned out one agent per candidate, each REQUIRED to emit its
   consumer grep before proposing. **No counterweight ran on the sweep — triage first.**
   RE-key the boundary-bypass arm (never delete it); fix `#531` via the adapter
   `artifact_path`. Both owe a second round.
   [Critique](../charness-artifacts/critique/2026-08-11-deletable-surfaces-sweep.md).
3. **`#546` phase 2 — the adapter `conditional:` marker.**
   [Critique](../charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md).
4. **`#587` — edit, do not close.** The mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`, not `expand_targets`.
5. **Wave 2 — small concrete bugs.** `#539` `#581` `#588` `#528` `#589` `#542`.
6. **Wave 3 — the rest.** `#586`, `#590`, `#593`-`#598`, `#550`, `#527`. Umbrellas are in
   no wave; they stay open until their work ships.

## Discuss

- **Does a pattern-match decide what someone MEANT?** Then a declared route replaces it,
  as `--intent` replaced `should_fire_chunker`. Suspects: `setup_skill_routing_lib`'s
  semantic-completeness regex (ships to consumers), `chunked_routing_parser`,
  `classify_push_diff_lib`. Form validators are NOT in this class.
- `#576` closed by commit keyword (no comment); a manual comment naming D53 is owed.

## Continuation Capability

- **A removal proposal without its consumer grep is malformed.** Seven wrong proposals in
  one session, each refuted by one grep. Put the grep and its result IN the proposal.
- **Every correction last session was operator-initiated.** The reviewers were right every
  time and were only spawned when asked. Run the adversarial pass before being told to.
- **The round that reads the REPAIRS finds a different class.** Ten for ten, prose included.
- **Six of six deletions were refuted — then one refutation was itself refuted.** Proving
  the proposer's REASON wrong is not proving the surface load-bearing; only the second
  blocks a deletion. Name the consumer grep in both directions.
- **Closing an issue can delete the only copy of a ruling** — or rot its pointer: `#536`
  closed COMPLETED while the cost it tracked survived. Ask where the record lands.
- **A green ratchet can record paying its own tax.**
  [dup-review.json](../charness-artifacts/quality/dup-review.json) has 57 rotation notes.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
