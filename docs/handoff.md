# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: pushed `main` (through `8799343d`), landed Boundary DBD-2, and
  CLOSED #414 + #416.** `main` == `origin/main` == `8799343d`.
  - **Boundary DBD-2 (`8799343d`).** Extended the concept-boundary checkpoint to
    the four remaining #414 stages (issue/spec/achieve/quality). The
    critique-vs-impl carrier analysis (two bounded read-only carrier maps)
    resolved **all four to the impl archetype** — surface the shared brief + an
    emit-only disposition, leaning on the critique/review each stage already runs;
    **no new hard validator floors** (the disposition is a per-change artifact and
    every change flows through a `critique`, so `critique` stays the single
    validated-teeth home). #414 (feature) + #416 (feature; `bug`-labelled but a
    capability gap, not a behavior divergence) closed as one fix-unit.
  - **Fresh-eye critique = REVISE (incorporated).** Caught overstated achieve
    "already floors it" prose (fixed: caveated to the DBD-4 judgment residual, no
    floor added) and an untested issue `Boundary #N:` line (fixed: folded a guard
    at zero net LOC). Portability clean (AC6 grep zero consumer nouns). Full pytest
    (4187) + run-quality (80-81/0) green.
  - **Prior session (`960d8336`): Boundary DBD-4** — charness dogfoods its own
    cross-surface probe (`boundary_cross_surface_globs: [scripts/*_lib.py,
    skills/shared/**]`, ~8%) wired into `run-quality.sh`; #408 closed.

## Next Session

0. **Activate the drafted improvement goal** —
   `/goal @charness-artifacts/goals/2026-07-08-retro-informed-improvement-5pack.md`:
   five decided slices, hard order R → (V/B/G) → D; plan-critiqued (folds
   applied). Corrects item 3 below: #371 is NOT self-contained (ceal raw
   tool-call path is upstream #1334; Tier 1 only, issue stays open). Briefs:
   [design-studies](../charness-artifacts/design-studies/2026-07-08-retro-informed-improvement-briefs.md).
1. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each).**
   pickup / pickup-ambiguous (`workflow-trigger.md`) need a stable closeout token
   designed first; `spill-targets.md` needs its owning-path routing table inlined.
   Method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
2. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture (charness
   detects NORMALIZE in-repo, not GREENFIELD; substance judge already exists).
3. **#371 (agent-browser orphaned-chromium leak)** — open bug-class backlog item,
   not yet queued; self-contained (causal review → fix → resolution critique).
4. **81-site argparse-help debt (run LAST).** Default-off; baseline rotation runs
   alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at 479/480 — extract a
   module before appending.

- **#408 residual (deferred, disclosed in the close):** item 4 (test-authoring
  guidance discouraging permanent forbidden-string assertions) was NOT delivered —
  file a follow-up if wanted.

## Discuss

- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals; reopen
  only if the recorded failure materializes. See [deferred-decisions.md](./deferred-decisions.md).
- **test/production LOC ratio is pinned at ~1.0** (`check-test-production-ratio`,
  `round(test/source, 4) < 1`). It has now blocked two consecutive prose-heavy
  slices (prior session's "2-line source>test ratio"; DBD-2 needed a test trim to
  hold the margin). Any slice that adds tests without Python source trips it.
  Candidate follow-up: widen the guard's headroom or count executable-spec/markdown
  surface, so prose-wiring slices are not forced to shave real coverage. Not filed.

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
