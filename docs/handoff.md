# Charness Handoff

## Workflow Trigger

- **No open work. The sweep-high-rows goal is COMPLETE** — four slices, eight
  review rounds, bundle proof and both closeout reviews recorded in
  [the goal](../charness-artifacts/goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md).
  With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. No open irreversible boundary; ten commits unpushed
  (`7efa0240..HEAD`), which is why the armed changed-line gate below needs an
  explicit `--base-sha`.

## Continuation Capability

Sweep rows close as **NARROWED** far more often than CLOSED, and the row must
say what stays open. This run's arming posture is the operator's: **measure,
then decide** — and where a repair would refuse consumer-authored files or
frozen artifacts, it ships legible and the arming becomes a numbered deferred
decision ([D46](./deferred-decisions.md) adapter-YAML refusal,
[D47](./deferred-decisions.md) inventory value markers).

Non-claims to carry: a length floor **refuses a stub, not a lie**; S35's own
repair is an instance of the class the sweep catalogues (a self-declared adapter
field decides whether the floor fires); S9's corroboration cannot see a repo
git cannot date. No push, no CI dispatch, no cautilus run this session.

## Current State

- **9 of 9 rows dispositioned; only 3 CLOSED** (S28, S13, S23). Six NARROWED
  with residuals on the rows. **S12's and S23's ROWS are corrected** — S12's
  stated triggers mostly never reproduced, and S23's `surface:line` was wrong.
- **Round 2 caught defects created by round 1's own repairs in EVERY slice
  where it ran.** 15 reviewer spawns, 8 rounds. One round is insufficient here.
- **The armed changed-line lane is clean** after naming 33 uncovered lines; the
  serial suite is 6515 passed. Ten dup-ratchet hard-blocks across three slices.

## Next Session

1. **`charness:handoff` chunked routing** over the live backlog. The sweep's
   remaining high rows are S15, S31, S36, S37, S111; the hunt's E-cluster
   (E1/E3/E6/E7 + E2's residual) is untouched and is the most expensive lane;
   issue #467's mutation regression on main is still open.
2. **Three unarmed refusals wait on an operator call**:
   [D46](./deferred-decisions.md) adapter-YAML, [D47](./deferred-decisions.md)
   inventory value markers, [D48](./deferred-decisions.md) release surfaces.
   Each records its measured cost.
3. **`measure_evidence_residual.py` is the third member of the
   measurement-script class** and still exits 0 over an empty corpus while
   reporting `corpus_established: false`. Its two siblings were repaired this
   run; it was not.
4. **Off-goal, found not fixed:** `goal_artifact_floor_grammar.parse_created_date`
   is consumed by FIVE achieve floors with no corroboration — S15's family, and
   a one-helper repair since goal artifacts carry a filename date that
   `critique_enforcement_scope.observed_date` already reads. Two more in the
   goal's `## Off-Goal Findings`.

## Discuss

- **A self-authored constraint in a goal artifact is not a check.** This session
  violated its own stop condition two hours after writing it, and a reviewer
  caught it. Whether goal stop conditions become machine-read is an operator
  call.
- **Run the dup-ratchet at the first edit to a gated file, not at the closeout
  aggregate.** Ten late hard-blocks this session against four last session; the
  recorded lesson has now failed to prevent itself twice.
- **A test that asserts a source substring is not a test.** Round 2 caught this
  goal pinning its own repair with a string search that would survive the
  repair's deletion — in the slice whose thesis is that a verdict must not
  outlive its check.

## References

- [active goal](../charness-artifacts/goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md) · [slice-1 critique](../charness-artifacts/critique/2026-08-01-slice-1-absent-input-batch.md) · [slice-1 retro](../charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md)
- [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md) · [deferred decisions](./deferred-decisions.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
