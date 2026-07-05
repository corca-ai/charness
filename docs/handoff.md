# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: pushed `main` (through `960d8336`), landed Boundary DBD-4, and
  CLOSED #408.** `main` == `origin/main` == `960d8336`.
  - **Push repair (`896ff974`).** The pre-push full gate caught 18 pytest failures
    and a cautilus gap the prior session left (it ran only `run-quality.sh`, never
    the full pytest suite, yet the handoff claimed "verification passed"). Fixed: 16
    critique fixtures tripped the new boundary floor (DRY'd via `_seed_critique`),
    an environmental pytest-temp-footprint test (isolated), a 2-line source>test
    ratio, and a non-conforming `finding.md` (added SOURCE/VERDICT/INTERPRETATION
    markers).
  - **Boundary DBD-4 (`960d8336`).** charness now dogfoods its own cross-surface
    probe: `boundary_cross_surface_globs: [scripts/*_lib.py, skills/shared/**]`
    (~8% of recent commits) with `--changed-ref "${base}..HEAD"` wired into
    `run-quality.sh`, so the #408 5b tooth fires in charness CI. Two fresh-eye
    reviews caught a false measurement (`git log -n` cap artifact) and a bare-sha
    wiring bug; both fixed. #408 closed with proof + honest disclosures.

## Next Session

1. **Boundary DBD-2 — extend the checkpoint** to issue/quality/spec/achieve; each
   needs the critique-vs-impl carrier analysis the First Slice did for critique+impl.
   Closes #414/#416 (still OPEN; First Slice landed their authoring lens + brief).
2. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each).**
   pickup / pickup-ambiguous (`workflow-trigger.md`) need a stable closeout token
   designed first; `spill-targets.md` needs its owning-path routing table inlined.
   Method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
3. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture (charness
   detects NORMALIZE in-repo, not GREENFIELD; substance judge already exists).
4. **#371 (agent-browser orphaned-chromium leak)** — open bug-class backlog item,
   not yet queued; self-contained (causal review → fix → resolution critique).
5. **81-site argparse-help debt (run LAST).** Default-off; baseline rotation runs
   alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at 479/480 — extract a
   module before appending.

- **#408 residual (deferred, disclosed in the close):** item 4 (test-authoring
  guidance discouraging permanent forbidden-string assertions) was NOT delivered —
  file a follow-up if wanted.

## Discuss

- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals; reopen
  only if the recorded failure materializes. See [deferred-decisions.md](./deferred-decisions.md).

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
