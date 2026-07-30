# Charness Handoff

## Workflow Trigger

- No open irreversible boundary. With no explicit task, run `charness:handoff` chunked
  routing over the live backlog; an explicit user task keeps its own authority. Pick the
  smallest coherent slice and close it end-to-end: mutate canonical source, sync
  generated/plugin mirrors before validators, then prove with the mandated critique.

## Continuation Capability

Two records drive the burn-down. The
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
reproduced 30 defects over 22 surfaces; **5 OPEN + 5 PARTIAL remain**, of which E4 and
A8's residual are decisions, not work (its header names both). The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
first-looked 146 more never-examined surfaces: **86 leads open, 24 of them high**. The
three tables use three status vocabularies — read the one you cite before citing a row.

Refresh non-claims: the pre-push lane's five-hole state, the D42/D43 answers, and the
raised-bar detail are gone — closed, and owned by the goal artifact. No claim that any
consumer repo gained push-time teeth, and none that the sweep's remaining rows were
re-triaged; their provenance is still what their own cells say.

## Current State

- **#465 is CLOSED** ([critique](../charness-artifacts/critique/2026-07-30-issue-465-resolution.md)).
- **21 rows closed on 2026-07-30** across five slices (hunt A5/A6/A9/A10/B1/B4/B5,
  sweep S14/S16/S17/S18/S25/S39/S40/S42/S43/S44/S46/S49/S53/S56). A8 and S15 are
  PARTIAL with their reasons in-row; R8 is REFUTED at HEAD.
- **Round 2 caught blockers in four of five batches, always by reading the REPAIRED
  surface** — #465's caught a repair that shipped the class it fixed, plus a confounded
  premise measurement. **Size the next slice so both rounds fit.**
- **The subprocess-coverage mechanism is MEASURED and the old claim was wrong:** an
  inherited-env child running an in-repo script IS attributed, so **a subprocess test
  is never by itself a reason to doubt a BLOCK**; only an `env=` that REPLACES the
  environment or an out-of-tree COPY loses it. Three surfaces are corrected.

## Next Session

1. **The sweep's 24 remaining high rows.** Batch by shared root cause where one
   exists, and check that it does: **S3+S4 are one file**; S11 is adjacent but a
   different predicate; **S5 is a density-exemption defect, not an evidence floor.**
   S7+S8 (cautilus) plausibly share a helper; S21/S22 are separate skills, one repair
   each.
2. **The hunt's E-cluster** — E1, E3, E6, E7 OPEN and E2 PARTIAL; **E4 is D39 and
   stays deferred**. Mutation-score and freshness-marker proof; the hunt's own
   suggested order carries the supersession note.
3. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9),
   C6 PARTIAL (residual is a contract change), D4 PARTIAL, D28 remainder,
   sibling-scan Tier 2 finding D.
4. **[D39](./deferred-decisions.md) / [D41](./deferred-decisions.md)** (the armed
   lane's gaps) stay deferred; no reopen trigger fired this session.
5. **Two local runtime budgets were raised** (`6ea39160`, operator-directed, local
   profile only); derivations are in the
   [quality adapter](../.agents/quality-adapter.yaml) comments.

## Discuss

- **Run the armed changed-line gate over the committed range after each commit**:
  `prepush_focused_changed_line_coverage.py --repo-root . --base-sha <the sha before
  your first commit>` — `HEAD` there is an empty range and a vacuous verdict. On a
  dirty worktree it reports UNPROVEN, and `--allow-dirty` only downgrades that to a
  recorded `dirty_pool_unverified`; it does not buy a green.
- **A gate that establishes nothing prints `UNPROVEN`, not `PASS`** — exit 3, opt-in
  per label via `UNESTABLISHED_CAPABLE_LABELS`, not a repo-wide default.
- **A gate blocking on your own lines is a finding, not a chore.** Both #465
  follow-ups came from asking WHY a blocked line was unreachable — a dead shim with
  zero callers, and an env-shape false negative. Probing beat covering, twice.
- **Measure the cause before raising a budget**, and record the number where the bar
  lives; a raise to green your own push is the bar-moving shape.
- Run release/skill helpers from `skills/public/.../scripts/`, never an installed or
  `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [verdict-timing sweep](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md) · [session retro](../charness-artifacts/retro/2026-07-30-session-retro.md)
