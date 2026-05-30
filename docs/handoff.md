# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` now fires chunked routing too (#249), and the chunker unions the
  **live open-issue backlog** with the entries below — so this list is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` PUSHED + synced; v0.13.0 RELEASED** (tag `v0.13.0`, GitHub release
  public-verified). Ships the coordination-cues achieve feature + accumulated
  since-0.12.0 work (#253 disposition gate, #255 portability, #256/#257 closeout
  gates, #251 mutation, #232, #244/#245 SessionStart hook auto-install) — all
  CLOSED. Per-item detail lives in the release notes + each goal/retro artifact.
- **achieve goal-doc coordination cues SHIPPED** (goal
  [`2026-05-30-coordination-cues`](../charness-artifacts/goals/2026-05-30-coordination-cues-find-skills-routing.md)):
  a `## Coordination Cues` find-skills routing carrier + gather/release
  presence-only closeout floors in `goal_artifact_coordination_floors.py`,
  grandfathered `Created >= 2026-05-31`.
- **v0.13.0 real-host (clean-machine) proof — maintainer-attested DONE**
  ([proof artifact](../charness-artifacts/release/2026-05-30-v0.13.0-real-host-proof.md)).
  Clears the long-carried "real-host proof pending" item; raw `--json` not
  captured in-session (attestation, not agent-captured record).

## Next Session

> A bare `/handoff` unions the tracker — so chunk the live backlog rather than
> trusting this list. This memo carries only cross-issue judgment.

1. **Backlog** (push/#253/#255/#244/#245/real-host all DONE): #243
   (usage-episodes consumer/report gap), #242/#219 (mutation), #233, #241,
   #237/#236, #184/#185, and this session's off-goal finds #258/#259.
2. Optional: upgrade the v0.13.0 real-host attestation to captured `--json`
   evidence if a stronger durable record is wanted.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there. Full session waste / decisions:
  [closeout retro](../charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [chunker contract](./handoff-chunked-routing.md),
  [release latest](../charness-artifacts/release/latest.md)
