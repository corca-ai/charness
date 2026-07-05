# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: #416/#414/#408 boundary-ownership checkpoint — design agreed +
  First Slice LANDED. `main` is far ahead of origin, UNPUSHED.**
  - Design conversation → spec
    [2026-07-05-boundary-ownership-checkpoint.md](../charness-artifacts/spec/2026-07-05-boundary-ownership-checkpoint.md)
    (`459e262e`); spec fresh-eye REVISE incorporated pre-impl.
  - First Slice (5 sub-slices) implemented, impl fresh-eye REVISE incorporated:
    `30f9f1a1` portable brief + wiring, `429f214a` critique closeout
    presence-floor (typed `Verdict:`, enforce-from 2026-07-06), `06187605`
    repo-owned cross-surface probe (impl stop-gate escalation hook + validator
    `--changed-ref` severity upgrade), `b934bdb8` create-skill/quality
    boundary-taxonomy authoring lens, `b5057d8e` REVISE fixes (FD6 reconcile,
    5b wiring guidance, AC8/AC9 tests).
  - Portability held (zero consumer taxonomy nouns in portable prose; anchor
    guard caught + removed issue anchors in the impl hook). Charness ships its
    OWN probe OFF (opt-in); the #408 override is proven by AC2/AC3/AC7 unit
    fixtures, not charness CI (spec FD6/DBD-4).

## Next Session

1. **Push** the unpushed `main` before new work (external boundary — deferred to
   operator; includes #410 pins `60434368`/`3f47f9f4` + this session's 6 boundary
   commits `459e262e`..`b5057d8e`).
2. **Boundary DBD-4 — charness adopts its own probe.** Choose charness's
   `boundary_cross_surface_globs` (paths where a caller-specific fix would land in
   shared `scripts/`) without false-positives, and wire the escalated critique's
   `--changed-ref` validation into `run-quality.sh` so the 5b tooth fires in
   charness CI (today it is proven only by unit fixtures).
3. **Boundary DBD-2 — extend the checkpoint** to issue/quality/spec/achieve; each
   needs the critique-vs-impl carrier analysis this slice did for critique+impl.
4. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each).**
   pickup / pickup-ambiguous (`workflow-trigger.md`) need a stable closeout token
   designed first; `spill-targets.md` needs its owning-path routing table inlined.
   Method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
5. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture (charness
   detects NORMALIZE in-repo, not GREENFIELD; substance judge already exists).
6. **81-site argparse-help debt (run LAST).** Default-off; baseline rotation runs
   alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at 479/480 — extract a
   module before appending.

- #371 (agent-browser orphaned-chromium leak) is open in the backlog — surfaces
  via `gh issue list`, not yet queued.

## Discuss

- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals; reopen
  only if the recorded failure materializes. See [deferred-decisions.md](./deferred-decisions.md).

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
