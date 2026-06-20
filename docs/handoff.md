# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **North-Star Overhaul — Phase 4 COMPLETE** (this session; **P0–P4 ALL done**).
  [Phase-4 goal](../charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md)
  `complete`; 6 commits; every slice fresh-eye PASS; bundle pytest 3520/0. Every
  charness-**owned** irreversible boundary is now non-terminal — issue/PR close (P2),
  release publish (WS-1 rung-1+rung-2, F2a), Direction-3 HOTL (WS-2); the un-owned
  prod-apply boundary is **portable** (WS-3: `ceal-dev` / `applied-restarted` / deploy-vocab
  left the core for an adapter seam).
- **Metric discipline (operator, 2026-06-20):** count is NOT the metric in either direction;
  proof = escape-closed + concept-clearer.
  [goodhart retro](../charness-artifacts/retro/2026-06-20-goodhart-not-line-count.md).
- **v0.52.6 released; no new release. ~28 commits ahead of origin/main, unpushed.**

## Next Session

- **TOP PRIORITY — skill-body redesign track (deferred P3/WS-B), then a release.**
  0/20 SKILL.md cores over the 160 cap, but **11 crammed at 150–159** (worst: issue 159,
  impl 158, debug 157; also achieve/create-skill/release/hitl/create-cli/find-skills/
  announcement/critique). Apply the Phase-3 instrument set
  ([per-unit-disposition spec §5](../charness-artifacts/spec/2026-06-20-per-unit-disposition-concept.md):
  no-op test / three length-causes / Leading-Word / named-heuristic / anchor-split)
  **diagnosis-first, per body**.
  - **NOT a trim-to-160 sweep — count is not the metric.** Diagnose each body's length
    *cause*; a justified-density body is **deferred with cause** (as overhaul-sweep WS-B did).
    Success = concept clarity + headroom, not fewer lines. `achieve` goal (Phase-4 = template).
  - **End state:** fix the bodies, **then cut a release** — the live `release` cut exercises
    the new WS-1 floors = the deferred WS-1 live-release proof.
- **Deferred live proofs (operator-approved + phase-scoped at run):** WS-1 live release
  (Phase-4 `## Operator Decision Queue`); overhaul-sweep R2 (a real `issue resolve` / PR-close
  through the floors). **ceal #417:** P4 done → the full doctrine can now propagate to ceal.
- **Secondary:** gate demotions (`check_doc_links` backtick→advisory, then critique/ergonomics;
  `--reuse-coverage` skips a coverage file with none of the changed paths). **Untouched:**
  #391 extractions + tool_version; #392 gather X; #371 agent-browser teardown.

## Discuss

- **Operator decided (2026-06-20):** fix all skill bodies, THEN release — diagnosis-first
  (not a trim sweep); the release's live cut is the WS-1 floor proof. ceal propagation now
  unblocks (charness embodies the full doctrine).

## References

- [Phase-4 goal](../charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md),
  [per-unit-disposition spec](../charness-artifacts/spec/2026-06-20-per-unit-disposition-concept.md) (§5 instruments),
  [design north star](./design-north-star.md),
  [north-star overhaul roadmap](./north-star-overhaul-roadmap.md),
  [goodhart retro](../charness-artifacts/retro/2026-06-20-goodhart-not-line-count.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
