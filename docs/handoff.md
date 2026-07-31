# Charness Handoff

## Workflow Trigger

- **No open irreversible boundary, nothing unpushed.** The latest release
  (`git describe --tags --abbrev=0`) is published and verified — release page
  confirmed on a distinct channel, installed readback matched, per
  [release state](../charness-artifacts/release/latest.md); `main` and
  `origin/main` agree. So the ordinary rule
  applies: with no explicit task, run `charness:handoff` chunked routing over the
  live backlog; an explicit user task keeps its own authority.

## Continuation Capability

Two records still drive the burn-down: the
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
(E-cluster: E1/E3/E6/E7 OPEN, E2 PARTIAL, E4 is D39 and stays deferred) and the
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md),
whose **selected high rows are done** (S5/S7/S21/S22 CLOSED, S8 REFUTED) — but the
table is not: of 37 high rows, 13 are still SUBAGENT-CONFIRMED, 2 LEAD, 1
PARENT-CONFIRMED, 3 PARTIAL.
Each header owns its own counts and the tables use different status vocabularies.
The sweep's new `## 2026-07-31 closeout non-claims` section bounds every row it
closed; read it before treating one as fully covered.

Refresh kept: the unpushed-commits fact, the E-cluster and un-dispositioned rows,
and S5's residual (the repair is author-time-preflight only).

Refresh non-claims: **S5 is closed at the preflight only**; the divergence it
leaves is written up in [authoring-preflight](./conventions/authoring-preflight.md).
**S21's detection is a floor, not a detector.** **S22 repairs a checker with no
caller.** No live cautilus run, no mutation lane, no CI dispatch this session.

## Current State

- **Published a patch release** ([notes](../charness-artifacts/release/2026-07-31-v3.0.1-notes.md),
  [critique](../charness-artifacts/critique/2026-07-31-release-3-0-1.md)). Four gates
  got stricter and three ship in the plugin, so a consumer's previously-green run can
  go red — the notes' Migration section is the load-bearing part.
- **Goal complete** — four repairs, one refutation, all proof executed:
  [goal record](../charness-artifacts/goals/2026-07-31-repair-the-sweep-s-remaining-high-rows-s5-density-exemption.md).
- **Round 2 caught what round 1 could not, twice**, and the release critique
  caught a third: a gate whose remediation named the wrong cause. Every one was
  created by the previous round's own repair.
  [retro](../charness-artifacts/retro/2026-07-31-session-retro.md)

## Next Session

1. **The two queued operator decisions** in the goal artifact: porting the bounded
   exemption into the portable copy, and whether S8's freshness residual is a row.
2. **The hunt's E-cluster** — E1/E3/E6/E7 OPEN, E2 PARTIAL, E4 deferred.
   Mutation-score and freshness-marker proof; the most expensive lane to prove.
3. **Wire an independent channel into the delegated-review floor**: S11's residual
   is that the artifact is the only thing read; `reviewer_boundary_fingerprint.py`
   verify output is a real second channel no gate consults.
4. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9),
   C6, D4, D28 remainder, sibling-scan Tier 2 D; [D39/D41](./deferred-decisions.md)
   deferred, S3's stub half pinned as an xfail.
5. Held nowhere else: retro anchors `subprocess-only-verdict-branches`,
   `pre-lane-runtime-bases`.

## Discuss

- **Run the armed changed-line gate over your own committed range**:
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .`
  (the source copy, never `plugins/`). Pass `--base-sha <sha before your first
  commit>`: the default merge-base is right only while your commits are unpushed,
  and a vacuous green after. It found a real uncovered branch this session.
- **When a structural walk (fences, headings, frontmatter) appears a second time
  in one work unit, unify it then.** Three ad hoc fence walks cost two review
  findings and a dup-ratchet cycle before `skill_markdown_lib.split_fenced_lines`
  existed.
- **List the assertions that pin today's behavior before planning verdict-logic
  work.** Three of five rows had one; one plan slice contradicted itself over it.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
