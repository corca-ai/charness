# Charness Handoff

## Workflow Trigger

- No goal is running. One handoff commit is local and unpushed; ask for a push grant.
  Start from `## Next Session`.

## Current State

- **23 open issues; the count is not falling because closing GENERATES issues.** Aug 7-10:
  created 60, closed 42. Filing is one command; closing owes the full floor.
- **`#572` CLOSED as `consolidated` into `#590`** (first live use of that path). **Do NOT
  read the green cron on `ed90c1f3` as recovery** — it is an ANCESTOR of `#590`'s
  diagnostic `739a2a3e`. No scheduled mutation run has hit main since.
- **`#582`-`#585` CARRY their own status** — per-member outcome and disposition in each
  body. **CLASS REMAINS, 4/4.** Do not close them.
- **Gate green: 89 passed, 0 failed, 1 UNPROVEN** — baseline taken BEFORE any deletion.
  Filed: `#596` (probe-pin tax; its tracker `#536` is closed COMPLETED), `#597`
  (`check_quality_tool_fixtures` passes on an empty set, unwired), `#598` (a gate blocking
  on a word preference + a five-week-unactioned reclassification audit).
- **D53/D54/D55** in [deferred-decisions](./deferred-decisions.md) each name a reopen
  trigger; D53's is explicitly NOT in-repo observable and says so.
- The evidence-boundary crosswalk instance was RETIRED by operator ruling; do not rebuild
  that matrix ([record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md)).

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
2. **Then the recorded sweep** — 3 deletions + 2 reworks; **no counterweight ran, triage
   first.** RE-key the boundary-bypass arm (never delete it); fix `#531` via the adapter
   `artifact_path`. Both owe a second round.
   [Critique](../charness-artifacts/critique/2026-08-11-deletable-surfaces-sweep.md).
3. **`#546` phase 2 — the adapter `conditional:` marker.** Phase 1 decides only RENAME.
   [Critique](../charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md).
4. **`#587` — edit, do not close.** Wrong component: the mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`, not `expand_targets`.
5. **Wave 2 — small concrete bugs, 2-3 per carrier.** `#539`, `#581`, `#588`, `#528`,
   `#589`, `#542`. Real code plus the fresh-eye review each classification owes.
6. **Wave 3 — the rest.** `#586`, `#590`, `#593`-`#598`, `#550`, `#527`. Umbrellas are in
   no wave; they stay open until their work ships.

## Discuss

- A carrier cannot say "this does not close #N": the recognizer cannot read negation.
- **Does a pattern-match decide what someone MEANT?** Then a declared route replaces it,
  as `--intent` replaced `should_fire_chunker`. Suspects: `setup_skill_routing_lib`'s
  semantic-completeness regex (ships to consumers), `chunked_routing_parser`,
  `classify_push_diff_lib`. Form validators are NOT in this class.
- `#576` closed by commit keyword (no comment) and a release note points at it as the
  live record. A manual comment naming D53 is still owed.

## Continuation Capability

- **The round that reads the REPAIRS finds a different class.** Ten for ten, and true of
  prose too: a reviewer stopped a false disposition from reaching a public artifact.
- **Six of six deletions were refuted — then one refutation was itself refuted.** Proving
  the proposer's REASON wrong is not proving the surface load-bearing; only the second
  blocks a deletion. Name the consumer grep in both directions.
- **Closing an issue can delete the only copy of a ruling.** Every durable in-repo
  mention of `#576` was a pointer AT it, and `#580`'s "tracked separately" pointed at
  itself. Before closing a record-shaped issue, ask where the record lands.
- **A green ratchet can be the record of paying its own tax.**
  [dup-review.json](../charness-artifacts/quality/dup-review.json) carries 57 rotation
  notes; green means ids were re-recorded, not that the class is gone.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
