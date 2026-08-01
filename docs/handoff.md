# Charness Handoff

## Workflow Trigger

- **No open work.** The three-unarmed-refusals goal is COMPLETE — D46, D48, and
  D47 each answered, recorded, and closed in
  [the goal](../charness-artifacts/goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md).
  With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. No open irreversible boundary; the branch is well ahead of `origin/main`
  (`git log --oneline origin/main..HEAD`), which is why the armed changed-line gate
  needs an explicit `--base-sha` — at the pushed base it inherits blocks from
  earlier sessions.

## Continuation Capability

**A deferred decision's "better repair" is prose nobody re-verified.** Two of the
three entries picked up this run named a remedy that could not be built as
described, and both were killed by plan critique before any code moved. Treat a
named remedy as a hypothesis with a premise to check in one command, not as a
plan. That is [#468](https://github.com/corca-ai/charness/issues/468), and D45 is
the next candidate carrying the same shape.

Non-claims to carry: nothing was armed this run — all three refusals stay
deferred; no push, no CI dispatch, no cautilus run, no release. D48's teeth sit at
the publish boundary only, and `publish_release_resume.py` still reaches
`create_release` with no surface check at all.

## Current State

- **Round 2 again caught defects created by round 1's own repairs**, in both
  slices where it ran. Three of five rounds found defects in a CLAIM rather than
  code: a string-replace "repair" that silently never applied, a units swap that
  manufactured agreement, a comment asserting a branch was live beside a probe
  recording zero.
- **The dup-ratchet-at-first-edit lesson is now holding.** Fired four times, four
  real extractions, zero late hard-blocks — against ten late blocks last session.
- **The bundle quality gate is 82 passed / 1 failed**; the failure is
  `check-changed-line-mutation-coverage`, whose four goal-owned files are now
  covered. `inventory_ci_local_gate_parity.py` remains blocked and is inherited
  from `7efa0240`, not this run.

## Next Session

1. **`charness:handoff` chunked routing** over the live backlog. The sweep's
   remaining high rows are S15, S31, S36, S37, S111; the hunt's E-cluster
   (E1/E3/E6/E7 + E2's residual) is untouched and is the most expensive lane;
   issue #467's mutation regression on main is still open, and #468 is new.
2. **Verify the changed-line gate on this session's own base** and clear the
   inherited `inventory_ci_local_gate_parity.py` block, or scope it deliberately.
   The run at the pushed base judges every unpushed commit, not just this run's.
3. **`goal_artifact_floor_grammar.parse_created_date` is still consumed by FIVE
   achieve floors with no corroboration** — carried from the last handoff,
   untouched this run, and a one-helper repair since
   `critique_enforcement_scope.observed_date` already reads the filename date.

## Discuss

- **A read-only check and an irreversible boundary deserve different teeth.** D48
  resolved by leaving `drift` untouched and refusing at publish. That split is now
  precedent; whether other gates should adopt it is an operator call.
- **Round 2 is capped at two, and round 2 keeps finding real blockers.** Slice 2's
  round-2 findings were sharper than round 1's. Whether a third round is ever
  warranted on a proof surface is unresolved.
- **Three things were built and reverted this run**, each now a named known gap
  with its reason. That is better than a half-guard, but it was real waste that a
  one-command premise check would have prevented.

## References

- [active goal](../charness-artifacts/goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md) · [retro](../charness-artifacts/retro/2026-08-01-three-unarmed-refusals-retro.md) · [marker-rule probe](../charness-artifacts/probe/2026-08-01-inventory-marker-rule.json)
- [deferred decisions](./deferred-decisions.md) (D45–D48) · [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
