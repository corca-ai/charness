# Charness Handoff

## Workflow Trigger

- No goal is running. One handoff commit is local and unpushed; ask for a push grant.
  Start from `## Next Session`.

## Current State

- **19 open issues, and the count is not falling because closing GENERATES issues:**
  Aug 7-10 created 60, closed 42. Filing is one cheap command; every close owes a
  sibling search and the full floor. The residue is decision-shaped, not code-shaped.
- **`#572` CLOSED as `consolidated` into `#590`** — first live use of that path; `#590`'s
  body is the durable home of all three of its events. **Do NOT read the green cron on
  `ed90c1f3` as recovery**: it is an ANCESTOR of the `#590` diagnostic `739a2a3e` and ran
  on the pre-push tree. No scheduled mutation run has hit main since; the next is first.
- **`#582`-`#585` are NOT cheap closes — they are the only home of ten unrepaired
  defects.** All ten members read CLOSED/`NOT_PLANNED`, i.e. `consolidated`, which claims
  nothing about the defect. Four bounded reviewers verified the tree: **CLASS REMAINS,
  4/4**. Closing them completes the laundering path that rule exists to block.
- Three deferred rulings live in the tree rather than only in issue threads: **D53**,
  **D54**, **D55** in [deferred-decisions](./deferred-decisions.md). Each names its
  reopen trigger; D53's is explicitly NOT in-repo observable and says so.
- **The quality gate is fully green: 90 passed, 0 failed.** Both long-standing reds are
  cleared — `dup-ratchet` (one real dedup plus eleven families classified `intentional`
  with per-family reasons) and `check-changed-line-mutation-coverage`.
- The evidence-boundary crosswalk instance was RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md);
  do not rebuild that matrix.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Re-split the umbrellas, do not close them** — per-member evidence and the four
   class instances outside every member are in the
   [class-survival review](../charness-artifacts/audit/2026-08-10-umbrella-class-survival-review.md).
   `#561` also owes its open operator decision a `deferred-decisions` entry.
2. **`#546` phase 2 — the adapter `conditional:` marker.** Phase 1 decides only RENAME;
   the marker makes the other two rot modes decidable, and phase 1's reader makes it
   verifiable. Record: [implementation critique](../charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md).
3. **`#587` — edit, do not close.** It refutes the wrong component: `run-quality.sh`
   wires the label to `prepush_focused_changed_line_coverage.py`, whose mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`, not `expand_targets`.
4. **Wave 2 — small concrete bugs, 2-3 per carrier.** `#539`, `#581`, `#588`, `#528`,
   `#589`, `#542`. Real code plus the fresh-eye review each classification owes.
5. **Wave 3 — the rest.** `#586`, `#590`, `#593`, `#594`, `#595`, `#550`, `#527`.
   (The umbrellas moved to item 1: their instances are all already resolved.)

## Discuss

- **A carrier cannot say "this does not close #N"** — the commit-msg recognizer is
  anchored on keyword-then-number and cannot read negation. Say "`#N` stays open".
- The `Premise-residue:` seam reads markers and nothing writes them.
- `#576` closed by commit keyword, which posts no comment, and the last release note
  points at it as the live record. A manual comment naming D53 is still owed.

## Continuation Capability

- **The round that reads the REPAIRS finds a different class.** Ten for ten. Also true
  of prose: the `#572` close draft claimed both older events were "structurally
  non-recurring"; the score signal is sample-relative and can recur, so the reviewer
  stopped a false disposition from reaching an irreversible public artifact.
- **A handoff list is a plan, not a verdict.** Wave 1 was handed off as six no-code
  closes; review closed four and pulled two out. Four of the six carried a comment
  arguing against their own close, and that comment was right twice.
- **Closing an issue can delete the only copy of a ruling.** Every durable in-repo
  mention of `#576` was a pointer AT it, and `#580`'s "tracked separately" pointed at
  itself. Before closing a record-shaped issue, ask where the record lands.
- **A red gate is often two unrelated debts.** Both long-standing reds cleared in
  under an hour once read: the dup families were three shapes, not twelve decisions.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
