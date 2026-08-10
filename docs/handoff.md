# Charness Handoff

## Workflow Trigger

- No goal is running. Wave 1 is DONE and carried in unpushed commits; start from
  `## Next Session`.
- **Push is held by operator decision until the backlog is closed.** `git log --oneline
  origin/main..HEAD` lists the unpushed set. Four issues close on that push (`#591`,
  `#576`, `#580`, `#592`) — carriers are written and validated, do not re-author them.
  `#595` was filed this session and is not in any wave yet.
  One decision is owed first — see the `#572` circularity below.

## Current State

- **`#572` cannot close without a push, and push is held until issues close.** Its
  diagnostic is in unpushed `739a2a3e`, the cron runs on main, and the test passes
  locally so it cannot be reproduced here. Break the loop by choosing: push early for
  this one, close everything else and push with `#572` open, or redefine it as the
  rolling ticket its own newest comment proposes.
- Three deferred rulings now live in the tree instead of only in issue threads:
  **D53**, **D54**, **D55** in [deferred-decisions](./deferred-decisions.md). Each names
  its reopen trigger; D53's is explicitly NOT in-repo observable and says so.
- The evidence-boundary crosswalk instance was RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md);
  do not rebuild that matrix.
- `dup-ratchet` and `check-changed-line-mutation-coverage` are red and BOTH predate
  this session, whose own files are clear. Recount with `bash scripts/run-quality.sh`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **`#546` phase 2 — the adapter `conditional:` marker.** Phase 1 shipped
   (`ac768bc2`) and closes only the RENAME mode; `dead-code-advisory` is a live
   instance the new gate reports green. The marker is what makes the other two modes
   decidable, and phase 1 built the reader that makes it verifiable rather than an
   unchecked annotation. Record:
   [implementation critique](../charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md).
2. **`#587` — edit, do not close.** Its retargeting refutes the wrong component:
   `run_standing_pytest.expand_targets` is not "the mapper" here — `run-quality.sh:867`
   wires the label to `prepush_focused_changed_line_coverage.py`, whose mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths` (`:85-87`: a missed match
   "costs a false block"). Re-point the question at the partially-mapped case.
3. **Wave 2 — small concrete bugs, 2-3 per carrier.** `#539`, `#581`, `#588`, `#528`,
   `#589`, `#542`. Real code plus the fresh-eye review each classification owes.
4. **Wave 3 — the rest.** Umbrellas `#582`-`#585` and their instances, plus `#586`,
   `#590`, `#593`, `#594`, `#550`, `#527`. An umbrella closes when its instances resolve
   or when a ruling retires it; making that call is the wave's first task.

## Discuss

- **A carrier cannot say "this does not close #N"** — the commit-msg recognizer is
  anchored on keyword-then-number and cannot read negation. Say "`#N` stays open".
- The `Premise-residue:` seam reads markers and nothing writes them.
- The matrix's `not_measured` names ten gaps; two are worth a slice.
- `#576` closes by commit keyword, which posts no comment; the last release note points
  at it as the live record. Consider a manual comment naming D53.

## Continuation Capability

- **The round that reads the REPAIRS finds a different class.** Ten for ten. Sharpest
  today: round 1 found a docstring claiming a safety mechanism that did not exist;
  round 2 found that its repair shipped a SECOND claim with no mechanism — a
  documented fail-open branch that was dead code, so the real behavior was
  fail-closed with a wrong remedy.
- **A handoff list is a plan, not a verdict.** Wave 1 was handed off as six no-code
  closes; review closed four and pulled two out. Four of the six carried a comment
  arguing against their own close, and that comment was right twice.
- **Closing an issue can delete the only copy of a ruling.** Every durable in-repo
  mention of `#576` was a pointer AT it, and `#580`'s "tracked separately" pointed at
  itself. Before closing a record-shaped issue, ask where the record lands.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
