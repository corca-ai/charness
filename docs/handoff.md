# Charness Handoff

## Workflow Trigger

- No goal is running. One handoff commit is local and unpushed; ask for a push grant.
  Start from `## Next Session`.

## Current State

- **21 open issues, and the count is not falling because closing GENERATES issues:**
  Aug 7-10 created 60, closed 42; this session closed 1 and filed 2. Filing is one cheap
  command; every close owes the full floor. The residue is decision-shaped, not code-shaped.
- **`#572` CLOSED as `consolidated` into `#590`** (first live use of that path; `#590`
  holds all three of its events). **Do NOT read the green cron on `ed90c1f3` as
  recovery** — it is an ANCESTOR of `#590`'s diagnostic `739a2a3e`. No scheduled mutation
  run has hit main since; the next is the first real check.
- **`#582`-`#585` now CARRY their own status** — each body states a per-member outcome
  (not fixed / declined / partial) and its disposition, so the ten defects no longer live
  only in closed issues. **CLASS REMAINS, 4/4.** Do not close them.
- **Gate green: 90 passed, 0 failed** — 2026-08-11 baseline, taken BEFORE any deletion so
  a later red is attributable. `#596` (probe-pin tax, whose tracker `#536` is closed
  COMPLETED) and `#597` (`check_quality_tool_fixtures` passes on an empty set and is not
  in the gate) filed this session.
- **D53/D54/D55** live in [deferred-decisions](./deferred-decisions.md), each with a
  reopen trigger; D53's is explicitly NOT in-repo observable and says so.
- The evidence-boundary crosswalk instance was RETIRED by operator ruling
  ([record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md));
  do not rebuild that matrix.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Clean deletion slice.** `render_skill_routing.py`'s unused PARAMETER only (keep the
   `listed_skill_ids` key — `eval_setup.py:220-224` raises without it),
   `plan_quality_run.py:327`, and [pickup.spec.json](../evals/cautilus/handoff-claim-fidelity/pickup.spec.json) ONLY, with coverage substitution in
   the same commit. Then rework: re-key `boundary_bypass_ratchet_lib.py` (do NOT delete
   the arm), `#531` via the adapter `artifact_path`. Both owe a second review round.
   Plan: [disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md).
2. **`#546` phase 2 — the adapter `conditional:` marker.** Phase 1 decides only RENAME;
   the marker makes the other two rot modes decidable, and phase 1's reader makes it
   verifiable. Record: [implementation critique](../charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md).
3. **`#587` — edit, do not close.** It refutes the wrong component: the mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`, not `expand_targets`.
4. **Wave 2 — small concrete bugs, 2-3 per carrier.** `#539`, `#581`, `#588`, `#528`,
   `#589`, `#542`. Real code plus the fresh-eye review each classification owes.
5. **Wave 3 — the rest.** `#586`, `#590`, `#593`, `#594`, `#595`, `#550`, `#527`, `#596`,
   `#597`. The umbrellas are not in a wave: they stay open until their work ships.

## Discuss

- **A carrier cannot say "this does not close #N"** — the commit-msg recognizer is
  anchored on keyword-then-number and cannot read negation. Say "`#N` stays open".
- The `Premise-residue:` seam has no marker writer BY DESIGN (`recount_residue_lib.py:63-67`)
  — a prior handoff read that as a defect and nearly got the seam deleted.
- `#576` closed by commit keyword, which posts no comment, and the last release note
  points at it as the live record. A manual comment naming D53 is still owed.

## Continuation Capability

- **The round that reads the REPAIRS finds a different class.** Ten for ten. Also true
  of prose: the `#572` close draft claimed both older events were "structurally
  non-recurring"; the score signal is sample-relative and can recur, so the reviewer
  stopped a false disposition from reaching an irreversible public artifact.
- **A handoff list is a plan, not a verdict.** Wave 1 shipped as six no-code closes;
  review closed four and pulled two out. Then a 6-deletion plan lost 5 to critique.
- **Closing an issue can delete the only copy of a ruling.** Every durable in-repo
  mention of `#576` was a pointer AT it, and `#580`'s "tracked separately" pointed at
  itself. Before closing a record-shaped issue, ask where the record lands.
- **A green ratchet can be the record of paying its own tax.** [dup-review.json](../charness-artifacts/quality/dup-review.json) carries
  57 rotation notes; green means rotated ids were re-recorded, not that the class is gone.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
