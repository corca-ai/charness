# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **Branch `north-star-p123` (PR open): north-star P1-P3 sweep.** 24
  counterweight-verified findings implemented by 14 bounded subagents + 3
  fresh-eye critique reviewers; all critique blockers fixed in-branch. Key
  moves: mechanism-keyed issue-close floors (colon/comma keyword forms
  covered), release behavioral floor + `state-verified` rename + same-proxy
  probe flag, critique fresh-eye typed-presence floor (fail-closed undatable,
  2-name legacy allowlist), announcement verification ledger with adapter
  cross-check, cut-safety deletion REVIEW wiring (incl. `skills/shared/`),
  achieve lifecycle split (861 -> index + 3 phase files, phase_brief routes
  per-phase), impl/find-skills/setup/AGENTS.md dedup, scaffold shim
  unification, dup-ratchet scoped re-baseline mode.
- Operator inputs honored: `check_test_production_ratio` KEPT (restored after
  an in-flight miss), `check_python_lengths` KEPT blocking (message now
  teaches split-or-delete); governing reference gathered at
  [enforcing-quality-of-ai-generated-code](../charness-artifacts/gather/2026-07-04-enforcing-quality-of-ai-generated-code.md).
- Gate audit artifact:
  [gate-reclassification](../charness-artifacts/audit/2026-07-04-gate-reclassification.md);
  critique record:
  [sweep critique](../charness-artifacts/critique/2026-07-04-north-star-p1-p3-sweep-branch-north-star-p123.md).

## Next Session

1. Review/merge the `north-star-p123` PR; post-merge, `charness update`
   refreshes the managed checkout (also activates the earlier session-start
   front-load, handoff item from v0.61.0 era).
2. Audit Follow-ups worth their own slices: wire `vulture` (configured, never
   run — dead-code gap vs the operator toolset); 81-site argparse-help debt
   (opt-in ergonomics rule landed, default-off); dup_ratchet module split
   (both files in WARN band).
3. Deferred: nested-delegated evidence-linking (accepted gap, own
   floor-addition call); shared closeout-contract extraction across
   impl/spec/setup (pinned-string coupling made it unsafe this round).

## Discuss

- test_handoff_plan.py live-root brittleness is FIXED (fixtures + validator
  constants single-sourced) — the old "keep this file under 60 lines"
  workaround no longer applies.
- Lesson: mid-run operator overrides crossed agent inboxes twice; verify
  override receipt with the owning agent before integration, not after.

## References

- pickup: [gate-reclassification](../charness-artifacts/audit/2026-07-04-gate-reclassification.md) · [sweep critique](../charness-artifacts/critique/2026-07-04-north-star-p1-p3-sweep-branch-north-star-p123.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
