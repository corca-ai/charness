# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: completed the retro-informed improvement 5pack goal**
  ([goal artifact](../charness-artifacts/goals/2026-07-08-retro-informed-improvement-5pack.md),
  Status: complete) — all five decided slices landed locally, **NOT pushed**
  (`main` is ahead of `origin/main`; push is an operator-approved lane):
  - **R `6415175b`** — live hard test/production-ratio pin removed; posture is
    advisory-only (run-quality gate keeps `--advisory`); per-branch fixtures.
  - **V `6440b24d`** — new blocking `validate-scenario-conditional-reads` gate
    (planner forced-reads no scenario forces are flagged; classTag + allowlist
    waivers; the 7/2 incident is machine-caught) + stub-debt fix `30e3dd11`.
  - **B `cf7e6f47`** — #371 Tier 1 SIGTERM/SIGINT/atexit gather-browser
    teardown, red/green subprocess proof; #371 stays open.
  - **G `de54a977`** — forbidden-string test-authoring principle
    (unit-test-quality.md §7, cross-linked) — the #408 residual delivered.
  - **D `5d85de98`** — dup-ratchet fingerprint algo v2 (tokenize-normalized) +
    schema v3 member hashes + reduction advisory; ONE migration of the three
    lockstep baselines (9 reviewed accepts, 1 dead path deleted). Gate CLEAN.
  - Plus `38219d95` — repaired the inherited pre-goal red critique-stub
    roundtrip test (truncation dropped the DBD-2 Boundary Ownership floor).
  - Every slice ran a bounded fresh-eye critique; goal-level retro, host-log
    probe, and disposition review are checked in with the goal artifact.

## Next Session

1. **Operator lane**: push `main` + one remote CI pass over the bundled state
   (held 2026-07-08 by operator; local proof complete). The #371
   partial-resolution comment is POSTED (issuecomment-4911427366).
2. **Test-debt rotation (standing, value-motivated)**: sweep the
   post-2026-07-03-audit test-LOC delta (~+3.2k) for consolidation; every
   deletion needs mutation-coverage proof + fresh-eye review; never
   headroom-pressured (ratio is advisory-only by decision).
3. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each).**
   pickup / pickup-ambiguous (`workflow-trigger.md`) need a stable closeout
   token designed first; `spill-targets.md` needs its owning-path routing
   table inlined. Method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
4. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture (charness
   detects NORMALIZE in-repo, not GREENFIELD; substance judge already exists).
5. **#371 residuals (open by decision)** — upstream
   `vercel-labs/agent-browser#1334` owns the ceal raw tool-call path; Tier 1b
   (profile-dir lease) is gated on a pinned-CLI capability probe.
6. **81-site argparse-help debt (run LAST).** Default-off; baseline rotation
   runs alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at 479/480 —
   extract a module before appending.

## Discuss

- **Ratio pin RESOLVED (Slice R, 2026-07-08)**: the live hard bound is gone;
  posture is advisory-only by decision (no ratchet — re-Goodharts). Test-debt
  reduction is a value-motivated standing rotation item scoped to the
  post-2026-07-03-audit delta — queued as Next Session item 2 (2026-07-08).
- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals;
  reopen only if the recorded failure materializes. See
  [deferred-decisions.md](./deferred-decisions.md).
- dup-ratchet phase runtime reference is now ~3s (spec's ~1.4s note corrected
  in place); not a regression signal.

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
