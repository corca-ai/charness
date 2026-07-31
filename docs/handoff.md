# Charness Handoff

## Workflow Trigger

- **No open irreversible boundary.** #466 is settled: the dispatched `Mutation Tests`
  run [30593688078](https://github.com/corca-ai/charness/actions/runs/30593688078) at
  `7ae5bd04` (≥ `fa5683c0`) is **green**, and the issue was closed by the repo owner on
  2026-07-30. **One inherited red gate, not caused by this session:**
  `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary`
  hard-blocks on three duplicate families whose members are untouched by recent slices;
  reproduced in a clean worktree at `cddb0c42`, so it predates them. Settle it before
  the next push — classify the families as intentional in the dup-review record, accept the baseline,
  or refactor `publish_release_cli.py:289-337`. Then the ordinary rule: with no explicit
  task, run `charness:handoff` chunked routing over the live backlog; an explicit user
  task keeps its own authority. Pick the smallest coherent slice and close it end-to-end
  — mutate canonical source, sync mirrors before validators, then prove with critique.

## Continuation Capability

Two records drive the burn-down: the
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
(**5 OPEN + 5 PARTIAL**; E4 and A8's residual are decisions, not work) and the
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
(**24 CLOSED**, S3 PARTIAL). Each header owns its own counts, and the three tables use
three status vocabularies — read the one you cite before citing a row.

Refresh kept: both burn-down records, the un-dispositioned rows, the inherited dup block.

Refresh non-claims: **S11's floor reads only the artifact** — the same channel the author
wrote — so it raises the cost of a stub and proves nothing about whether a reviewer ran.
**S3 is PARTIAL**; its stub half is pinned as an xfail. No consuming repo exercised the
new floor, and the five unpushed commits' pre-push lane has never run.

## Current State

- **Sweep S11 CLOSED** (`4fba59af`, `c8a39e13`, unpushed;
  [critique](../charness-artifacts/critique/2026-07-31-sweep-s11-delegated-review-substantiation.md)).
  An `executed` delegated review must now name the channel that ran, the disposition it
  returned, or the record's path; negated markers do not count. 71 of 71 checked-in
  executed sections still pass.
- **Round 1's blocker was the slice's own guidance text**: the fill guard explaining the
  rule contained the words the rule refuses. Comments are now stripped before a section
  is read as author claims. Round 2 then caught two false refusals against checked-in
  text ("no reviewer identified a blocker") and a denial arm defeated by one adjective —
  **adjacency cannot tell a denied event from a negative result of one.**
- **Sweep S4 CLOSED, S3 PARTIAL** (`612dbaad`, `244bdf31`, unpushed;
  [critique](../charness-artifacts/critique/2026-07-31-sweep-s3-s4-closeout-evidence-binding.md)).

## Next Session

1. **The inherited dup-ratchet block** (see Workflow Trigger). It is a gate red on lines
   nobody in these sessions touched — decide it deliberately, do not accept it silently.
2. **The sweep's remaining high rows.** Batch by shared root cause only where one exists:
   **S5 is a density-exemption defect, not an evidence floor**; S7+S8 (cautilus) plausibly
   share a helper; S21/S22 are separate skills, one repair each.
3. **Wire an independent channel into the delegated-review floor**: S11's residual is
   that the artifact is the only thing read, and `reviewer_boundary_fingerprint.py`
   verify output is a real second channel no gate consults.
4. **The hunt's E-cluster** — E1/E3/E6/E7 OPEN, E2 PARTIAL, **E4 is D39 and stays
   deferred**. Mutation-score and freshness-marker proof.
5. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), C6, D4,
   D28 remainder, sibling-scan Tier 2 D. [D39/D41](./deferred-decisions.md) deferred.
6. Held nowhere else: retro anchors `subprocess-only-verdict-branches`,
   `pre-lane-runtime-bases`. S11's residuals live in the sweep record and its critique.

## Discuss

- **Run the armed changed-line gate over your own committed range**:
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .` (the source
  copy, never `plugins/`). Pass `--base-sha <sha before your first commit>`: the default
  merge-base is right only while your commits are unpushed, and a vacuous green after.
- **New tests go in-process unless the CLI boundary is the thing under test:** a new test
  module spawning a validator is a new boundary-bypass candidate, and that ratchet is
  no-increase.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [verdict-timing sweep](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md) · [prior goal-run retro](../charness-artifacts/retro/2026-07-30-session-retro.md)
