# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Mutation changed-line premerge-gate: spec + slice 1 (consumer) + slice 2
  (producer mechanism) landed, unreleased.** 13 commits on `main` ahead of
  `origin` (`f862b0dd`..`6a3facf6`). The #320/#321 **5th-recurrence** seam is now
  addressed in code: the
  [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  is impl-ready; the **consumer** is wired into pre-push (`run-quality.sh`
  read-only, reuse-fresh-coverage-or-skip, never the slow probe, non-blocking when
  stale/absent); the **producer** marker mechanism (`--write-head-marker`) is built
  and unit-tested. Each slice had full verification; slice 1 had a bounded
  fresh-eye review (REVISE folded).
- **Producer auto-run is BLOCKED on a cost decision** (the crux for next session):
  the faithful probe is the full suite with `dynamic_context` coverage — run live
  it was **>10 min** and produced a **~1.34 GB** coverage JSON. Do NOT auto-wire
  the full probe. See spec "Slice 2 — Cost finding".
- Forced risk-interrupt is **consumed in the spec** (`plan_risk_interrupt` ->
  `handoff-recorded` when the spec is in-slice); it stays "live" on a clean tree
  until the gate is active — the producer slice touches the spec, satisfying it.
- **#321 CLOSED** (same seam as #320, band-aided per-file again 2026-06-06). Open
  issues: **#322, #184**. v0.24.1 shipped (unchanged).

## Next Session

1. **Producer (A+B) + push + release — bundled (decided 2026-06-07).** Land the
   producer with the chosen lever: **drop `dynamic_context` + piggyback coverage
   onto the broad pytest closeout already runs** (one instrumented run, small
   artifact, no double-run). **Verify via the push**, not a fresh local faithful
   probe: the pre-push consumer gate + the scheduled cron backstop are the proof;
   false-positive blocks the push (fix+retry), false-negative caught post-merge;
   iterate if the push errors. Then bundle the push + release. Owner:
   premerge-gate spec "Slice 2" + "Decided next-session approach".
2. **#322 (scope C, spec-first) — the original pick this session pivoted off.**
   Breadth: 4-field self-declaration rollout to ~6 inference surfaces, **plus** the
   nose family classifier (Q1). `spec`-first per the #322 body. Saved analysis:
   [nose-clone interpretation](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md).
3. **Skill portability of the gate's lessons (so other repos benefit).** At
   minimum add the pattern + freshness-guard + producer-cost lesson to
   [mutation-testing.md](../skills/public/quality/references/mutation-testing.md);
   optionally promote the gate to a `quality`-skill capability + adapter contract
   (libs-packaging decision). Route via `create-skill`/`quality`; see spec.
4. Backlog: **#184** — 제품 성공 기준과 핵심 메트릭 정의.

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof; worth
  deciding whether to add light push/tag CI. (Producer lever + verification are
  decided — see Next Session #1 / spec.)

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice Status + Cost finding),
  [#320 debug](../charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md)
- [nose-clone interpretation (#322 Q1/Q2)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
