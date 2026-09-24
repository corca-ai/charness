# Goal 844: Lane lifecycle and orchestration ownership

## Problem and outcome

`charness task run` lanes are fire-and-forget while orchestration stays tribal in private session scripts. Sixteen lane issues landed in two weeks (#814-#816, #822, #823, #826-#836), each adding one flag or field; open #837-#842 plus umbrella #843 would continue the accretion without a unifying loop. This goal owns the whole loop (before/during/after-landing plus learning) and closes #837-#843 as instances of it.

## Approved contract and execution order

The operator approved the briefing: typed result-kind envelope with exit codes 0-5 first (WI-1), then the hard-frontier fan-out (WI-2, WI-3, WI-4, WI-7), soft-edge parallel slices (WI-5, WI-6, WI-8a, WI-8b, WI-9, WI-10a, WI-10b, WI-11), and guarded closeout (WI-12). Self-review default narrowed to irreversible-boundary lanes per the operating-contract reserve clause. Frozen planning: `charness-artifacts/goals/2026-09-24-lane-lifecycle.md`.

1. wi-1-result-kinds: envelope, exit codes 0-5, event-schema v1.
2. wi-2-executor-probe: availability probe, executor_unavailable, fallback.
3. wi-3-steer: steer file-queue plus same-candidate scope amend.
4. wi-4-premise-gates: brief critique, premise check, acceptance-first.
5. wi-5-launch-hygiene: base freshness, skeleton-first, primitive rule, size.
6. wi-6-lesson-inject: ledger injection into lane prompts.
7. wi-7-review: self-review phase plus landing review trigger.
8. wi-8a-train: generic merge-train core plus verify profile.
9. wi-8b-dag: DAG static plan, ready-derivation, single-shot pull.
10. wi-9-report-ledger: report economy plus decision ledger.
11. wi-10a-metrics: review and rework metrics.
12. wi-10b-test-cache: content-addressed test cache, non-authority.
13. wi-11-learning-loop: friction log, retro, re-injection, guidance.
14. wi-12-closeout: guarded close of #837-#843 with readback.

## Readiness and completion

Local readiness requires integrated changes, focused topical proof, changed-line proof for verdict logic, and `check-docs.sh` for doc-touching slices. Children remain open until their acceptance is observed on the provider. Parent owns the sole execution cursor. No release publication, version bump, push, executor CLI changes, or hosted daemon. No milestone exists.

## Current frontier

WI-1 (#845), WI-10a (#855), WI-3 (#847), and WI-8a (#852) are landed and verified closed. WI-4 premise lane running; WI-2 launching next. Open: #846 WI-2, #848 WI-4, #849 WI-5, #850 WI-6, #851 WI-7, #853 WI-8b, #854 WI-9, #856 WI-10b (gates satisfied: WI-1 and WI-8a landed), #857 WI-11, #858 WI-12.

<!-- charness-goal-run:v1
{
  "binding_schema": "charness.goal-binding/v1",
  "binding_path": "charness-artifacts/goals/2026-09-24-lane-lifecycle.binding.json",
  "binding_sha256": "be3796de56c5903faf606b74de2eb1ce687f04bb7cd8694b13fc554576672b40",
  "draft_path": "charness-artifacts/goals/2026-09-24-lane-lifecycle.md",
  "draft_sha256": "76a32d4a94e195caa1b27433d748c47fdbeab5b95f5bd8e543ca1748ebb71146",
  "initial_graph_sha256": "ac748cc0deb9fc785c38bbd56d31cc3cd57484cbbcb047564f3b2699927616b7",
  "bootstrap_verification": "verified-target-roundtrip",
  "parent_identity": {
    "repo": "corca-ai/charness",
    "number": 844,
    "url": "https://github.com/corca-ai/charness/issues/844"
  },
  "progress": {
    "schema": "charness.goal-progress/v1",
    "revision": 2,
    "total": 14,
    "completed": 4,
    "open": 10,
    "next": {
      "key": "wi-2-executor-probe",
      "repo": "corca-ai/charness",
      "number": 846,
      "url": "https://github.com/corca-ai/charness/issues/846",
      "state": "OPEN"
    }
  }
}
-->
