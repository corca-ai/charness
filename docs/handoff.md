# Charness Handoff

## Workflow Trigger

- **No open irreversible boundary, nothing unpushed.** #466 is settled: the dispatched
  `Mutation Tests` run
  [30593688078](https://github.com/corca-ai/charness/actions/runs/30593688078) at
  `7ae5bd04` (≥ `fa5683c0`) is **green**, the repo owner closed the issue on 2026-07-30,
  and the run is now cited on it. `main` is at `e011f3ff` with all 82 pre-push gates
  green. So the ordinary rule applies: with no explicit task, run `charness:handoff`
  chunked routing over the live backlog; an explicit user task keeps its own authority.
  Pick the smallest coherent slice and close it end-to-end — mutate canonical source,
  sync mirrors before validators, then prove with critique.

## Continuation Capability

Two records drive the burn-down: the
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
(**5 OPEN + 5 PARTIAL**; E4 and A8's residual are decisions, not work) and the
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
(**24 CLOSED**, S3 PARTIAL). Each header owns its own counts, and the three tables use
three status vocabularies — read the one you cite before citing a row.

Refresh kept: both burn-down records and the un-dispositioned rows.

Refresh non-claims: **S11's floor reads only the artifact** — the same channel the author
wrote — so it raises the cost of a stub and proves nothing about whether a reviewer ran.
**S3 is PARTIAL**; its stub half is pinned as an xfail. No consuming repo exercised the
new floor. The two dup families classified intentional were judged by reading them, not
by a second observer.

## Current State

- **Published `charness` at version `3.0.0`** (tag `v3.0.0`;
  [notes](../charness-artifacts/release/2026-07-31-v3.0.0-notes.md),
  [critique](../charness-artifacts/critique/2026-07-31-release-3-0-0.md)). Major, not
  minor: the changed-line gate's mismatched head used to exit 0 and now exits 3, which
  breaks a documented-natural CI config.
- **Sweep S11 CLOSED** (`4fba59af`, `c8a39e13`;
  [critique](../charness-artifacts/critique/2026-07-31-sweep-s11-delegated-review-substantiation.md)).
  An `executed` delegated review must now substantiate itself. **Round 1's blocker was
  the slice's own guidance text**, and round 2 caught two false refusals against
  checked-in text — **adjacency cannot tell a denied event from a negative result.**
- **Sweep S4 CLOSED, S3 PARTIAL** (`612dbaad`, `244bdf31`;
  [critique](../charness-artifacts/critique/2026-07-31-sweep-s3-s4-closeout-evidence-binding.md)).

## Next Session

1. **The sweep's remaining high rows.** Batch by shared root cause only where one exists:
   **S5 is a density-exemption defect, not an evidence floor**; S7+S8 (cautilus) plausibly
   share a helper; S21/S22 are separate skills, one repair each.
2. **Wire an independent channel into the delegated-review floor**: S11's residual is
   that the artifact is the only thing read, and `reviewer_boundary_fingerprint.py`
   verify output is a real second channel no gate consults.
3. **The hunt's E-cluster** — E1/E3/E6/E7 OPEN, E2 PARTIAL, **E4 is D39 and stays
   deferred**. Mutation-score and freshness-marker proof.
4. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), C6, D4,
   D28 remainder, sibling-scan Tier 2 D. [D39/D41](./deferred-decisions.md) deferred.
5. Held nowhere else: retro anchors `subprocess-only-verdict-branches`,
   `pre-lane-runtime-bases`. S11's residuals live in the sweep record and its critique.

## Discuss

- **Run the armed changed-line gate over your own committed range**:
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .` (the source
  copy, never `plugins/`). Pass `--base-sha <sha before your first commit>`: the default
  merge-base is right only while your commits are unpushed, and a vacuous green after.
- **New tests go in-process unless the CLI boundary is the thing under test:** a new test
  module spawning a validator is a new boundary-bypass candidate, and that ratchet is
  no-increase.
- **The dup ratchet blocked the push on a prior slice's duplication.** One extraction in
  the release CLI plus two intentional classifications cleared it; re-read those two
  notes before adding a third.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [verdict-timing sweep](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md) · [prior goal-run retro](../charness-artifacts/retro/2026-07-30-session-retro.md)
