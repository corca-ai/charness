# Charness Handoff

## Workflow Trigger

- **One open irreversible boundary: #466 is repaired and NOT closed.** Its two commits
  are UNPUSHED and its confirming observer is the nightly `Mutation Tests` cron, which
  cannot see them until they land. Push, then read the next cron. Only then the ordinary
  rule: with no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end — mutate canonical source, sync generated/plugin mirrors
  before validators, then prove with the mandated critique.

## Continuation Capability

Two records drive the burn-down: the
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
(**5 OPEN + 5 PARTIAL**, of which E4 and A8's residual are decisions, not work) and the
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
(**86 leads open, 24 high**). Each header owns its own counts. The three tables use
three status vocabularies — read the one you cite before citing a row.

Refresh kept: both burn-down records and their vocabularies, the E-cluster and
un-dispositioned rows, the armed-gate rule.

Refresh non-claims: #466's repair is proven only by the workflow's baseline command
passing locally. Its bounded reviews are **quarantined** — the boundary fingerprint
`verify` reported drift (parent bookkeeping, not reviewer mutation, but not a clean
verify), and the nested-session finding is read-derived. No claim that 2026-07-30's
closed rows were re-verified.

## Current State

- **#466 repaired, unpushed, awaiting the cron** (`74445d9c`, `fa5683c0`;
  [critique](../charness-artifacts/critique/2026-07-30-issue-466-mutation-lane-baseline-repair.md)).
  Two tests read ambient CI-runner state; it is scrubbed in
  [the suite conftest](../tests/conftest.py).
- **Commit before reading a changed-line verdict, always** — the gate is a false green
  over uncommitted pool files and says so.
- **The gate was RIGHT to refuse, and asking why paid better than the CI fix.** An
  exported `MUTATION_HEAD_SHA` silently turned `FAIL` into `OK` exit 0 on the portable
  changed-line gate. **Consumer-visible: a mismatched head now exits 3** (`ok: true`,
  could-not-judge), never the exit 1 reserved for real uncovered lines.
- **Round 2 caught four blockers round 1 could not see**, all on surfaces round 1's own
  fixes created. **Size the next slice so both rounds fit.**

## Next Session

1. **Push, then read the next cron** — not a local run. A red cron is not automatically
   a new finding: check the exit-3 refusal this repair introduced first, since it is the
   one consumer-visible behavior change.
2. **The sweep's 24 remaining high rows.** Batch by shared root cause where one exists,
   and check that it does: **S3+S4 are one file**; S11 is adjacent but a different
   predicate; **S5 is a density-exemption defect, not an evidence floor**; S7+S8
   (cautilus) plausibly share a helper; S21/S22 are separate skills, one repair each.
3. **The hunt's E-cluster** — E1, E3, E6, E7 OPEN and E2 PARTIAL; **E4 is D39 and
   stays deferred**. Mutation-score and freshness-marker proof.
4. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), C6
   PARTIAL (residual is a contract change), D4 PARTIAL, D28 remainder, sibling-scan Tier
   2 finding D. [D39/D41](./deferred-decisions.md) stay deferred.
5. Held nowhere else: retro anchors `subprocess-only-verdict-branches`,
   `pre-lane-runtime-bases`.

## Discuss

- **Run the armed changed-line gate over the committed range after each commit**:
  `prepush_focused_changed_line_coverage.py --repo-root .`. Its `--base-sha` already
  defaults to the merge-base of `origin/main` and `HEAD`; pass it only when that default
  is wrong (after a push or rebase). **Its exit 3 is its own** — dirty pool, established
  nothing — NOT the portable gate's new mismatched-head 3.
- **A gate blocking on your own lines is a finding, not a chore.**
- **A test that asserts its own postcondition is not a regression test.** Negative-control
  each new guard by disabling what it guards — when a fixture can produce the condition.
  When it would need a live product path mutated, record the guard as read-derived.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [verdict-timing sweep](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md) · [prior goal-run retro](../charness-artifacts/retro/2026-07-30-session-retro.md) (the pre-push lane run, not this session)
