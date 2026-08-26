# Phase 1: Requalify scope and ownership

Status: planned
Goal: [adversarial-priority-backlog-closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## Objective

Use #723 and #722 as the cross-cutting ownership lens, then adversarially classify every claimed issue as live, stale, duplicate, over-scoped, decision-bound, or already satisfied before any implementation lane starts.

## Scope In

- GitHub bodies and comments for all 26 claimed P0–P2 issues
- current source, tests, shipped version, and consumer ownership evidence
- a per-issue owner, JTBD, premise verdict, proof diet, and parallel-lane assignment

## Scope Out

- P3 issues #711, #709, #705, #702, #688, #612, #599, #584, #583, and #582
- implementation before the issue premise and owner are established
- one global claimed task that serializes issue-owned work

## Dependencies

- GitHub backend is readable and each selected issue returns comments_read=true
- current repository and installed/package evidence are available for premise checks

## Completion Criteria

- Every claimed issue has a current premise verdict, owner, JTBD, and proportional evidence plan
- Stale, duplicate, umbrella, or already-satisfied issues are commented and closed immediately when the evidence is sufficient
- Live issues are partitioned into disjoint issue or issue-group lanes with one writer owner each

## Verification

- GitHub readback confirms the claimed cohort and comments for every issue
- Per-issue premise records cite current source or an explicit unverifiable boundary
- Closed-in-phase issues pass issue closeout readback; open lanes retain a concrete next action

## Non-Claims

- A recount is not proof that an issue premise holds
- No fresh-eye review is claimed for bulk premise classification or stale tracker cleanup
- No push, release, or hosted adoption is implied by local evidence

## Failure Handling

If verification fails, use `debug` and a 5-whys root-cause pass. Record the structural pattern and repair before retrying; a retry alone is not completion.
