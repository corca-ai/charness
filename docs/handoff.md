# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session landed 2 commits — `main` is UNPUSHED (2 ahead of origin/main):**
  - **#410 handoff/refresh MOVE proven + pinned.** Retired the census-INLINE
    doc-open floor `state-selection.md` to an emitted-token RSF
    (`Refresh kept:` / `Refresh non-claims:`); `plan_handoff_run.py` no longer
    forces the refresh re-read. A fresh ask-before-run capture PROVED honest
    compaction (`Read(state-selection.md)=0`) + honest-substance tokens, with
    `spill-targets.md` kept as a genuinely-opened DEPTH floor. Skill `60434368`,
    pin `3f47f9f4`. Fresh-eye: SHIP. Evidence:
    [handoff-refresh-move-2026-07-05/finding.md](../charness-artifacts/cautilus/handoff-refresh-move-2026-07-05/finding.md).
  - A would-be "no-flip" finding was caught as the documented planner-forced-read
    method error by a fresh-eye refute before it reached the record — the flip is
    the correct move, not a keep.

## Next Session

1. **Push `60434368` + `3f47f9f4`** before new work (external boundary — was
   deferred to operator this session).
2. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each).**
   pickup / pickup-ambiguous (`workflow-trigger.md`) need a stable closeout token
   designed first — a faithful pickup hands off to the invoked workflow, so its
   RSF token is fragile. `spill-targets.md` needs its owning-path routing table
   inlined (or a spill-conditional scenario) before it can MOVE. Method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
3. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture (charness
   detects NORMALIZE in-repo, not GREENFIELD; substance judge already exists).
4. **#416 / #414 / #408 concept-boundary discipline (design interview).**
   Adapter-owned boundary checkpoint for the lifecycle skills, Charness stays
   portable (no repo-local taxonomy). Design conversation first; no code until agreed.
5. **81-site argparse-help debt (run LAST).** Default-off; baseline rotation runs
   alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at 479/480 — extract a
   module before appending.

- #371 (agent-browser orphaned-chromium leak) is open in the backlog — surfaces
  via `gh issue list`, not yet queued.

## Discuss

- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals; reopen
  only if the recorded failure materializes. See [deferred-decisions.md](./deferred-decisions.md).

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
