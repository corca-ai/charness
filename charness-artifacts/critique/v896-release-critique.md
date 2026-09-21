# Release Critique — charness 8.9.6 (v8.9.6)

- **Release Scope**: `8.9.5` → `8.9.6` (tag `v8.9.6`), patch. One-line
  consumer story: require-change lanes report executor phase markers from
  both output streams, relay them live as PROGRESS lines, stop stalled or
  lingering-blocked lanes early with typed blockers, and classify
  unchanged interrupted lanes as known before-edit instead of
  interrupted-mid-edit.
- **Bump rationale**: patch, not minor: behavior repairs to the task-run
  carrier (dual-stream phase parsing, no-progress guard, BLOCKED-linger
  enforcement, unchanged-interrupt classification) plus regression tests
  and cohesive module splits; no new public skill, command, or install
  surface, and no existing invocation breaks.
- **Reviewed delta**: `f274a39aa..HEAD` at review time across three rounds.
  Round 1 (`a`/`b`) reviewed the base fix; round 2 (`a2`/`b2`) reviewed
  the round-1 answers; the `c2` follow-up reviewed the round-2 answers;
  the narrow `d` worker passed the final tree with no findings. Every
  round-1/round-2/follow-up finding below landed as code plus regression
  tests and is re-proved by the release lane, stated as non-claim.
- **Substrate**: bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lenses below), parent-owned counterweight here. No
  same-agent substitution. Attempt `c` failed at the host (codex backend
  model at capacity, no bounded review delivered) and was retried as
  `c2`; the failed attempt is retained as evidence, not as critique.

Fresh-eye satisfaction: parent-delegated — six file-backed workers
delivered (round 1: A block with 2 findings, B block with 3 findings;
round 2: A2 block with 3 findings, B2 block with 1 finding; follow-up C2
block with 2 findings; final narrow D pass with no findings); the parent
counterweight repaired all eleven with code plus regression tests and the
release lane re-proves every changed line; no same-agent substitution
occurred.

## Reviewer Tier Evidence

- Requested tier: n/a (no tier requested; host-defaulted)
- Requested spawn fields: n/a (run_review.py defaults; no explicit fork/model/effort ask)
- Host exposure state: host-defaulted
- Host detail: this host ran all reviewers through `run_review.py` file-backed workers (backend `codex exec`, read-only); no provider-confirmed model or effort application claim
- Application state: file-backed read-only workers delivered; all blocks received with findings, approval not inferred
- Delivery state: findings-received (a, b, a2, b2, c2, d); collection-failed (c, host capacity)
- Execution mode: file-backed-worker
- Worker A report: charness-artifacts/critique/workers/v896-critique-a/worker-report.yaml (verdict block, 2 findings)
- Worker B report: charness-artifacts/critique/workers/v896-critique-b/worker-report.yaml (verdict block, 3 findings)
- Worker A2 report: charness-artifacts/critique/workers/v896-critique-a2/worker-report.yaml (verdict block, 3 findings)
- Worker B2 report: charness-artifacts/critique/workers/v896-critique-b2/worker-report.yaml (verdict block, 1 finding)
- Worker C2 report: charness-artifacts/critique/workers/v896-critique-c2/worker-report.yaml (verdict block, 2 findings)
- Worker D report: charness-artifacts/critique/workers/v896-critique-d/worker-report.yaml (verdict pass, no findings)
- Failed attempt C: charness-artifacts/critique/workers/v896-critique-c/worker-report.yaml (backend-failed, host model at capacity; retried as C2)

## Reviewed Input Identity

- Final packet path: charness-artifacts/critique/v896-critique-d-packet.json
- Packet SHA256: 6880c98f141f1b320cdff77269c33d7c7d7b3303365903a9673d7cc266817963
- Identity SHA256: f7d118a8837480ee7e8088336d0d42dc26695fcd72a13e8703e6087ec4994317
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v896-critique-d-packet.json --packet-sha256 6880c98f141f1b320cdff77269c33d7c7d7b3303365903a9673d7cc266817963 --identity-sha256 f7d118a8837480ee7e8088336d0d42dc26695fcd72a13e8703e6087ec4994317`
- Round-1 packets (superseded delta, retained as evidence): `v896-critique-a-packet.json` (packet 4318d6c44241dde775fb6b5390e58992c15a4b5d5e1dee757fb7e542f38ba129, identity f6083ade41edf3d3e0acef9fcc57a0b5a6014f8e410e49c3b4c513ca2b5484b4), `v896-critique-b-packet.json` (packet c27262139d2b075ffbb01d55fcb40120dd94498024a9e30b1319838a474dba2c, identity f6083ade41edf3d3e0acef9fcc57a0b5a6014f8e410e49c3b4c513ca2b5484b4)
- Round-2 packets (superseded delta, retained as evidence): `v896-critique-a2-packet.json` (packet 4604513003e6b10479617f2927df2c19064955031ef6f6dbcf1d9fa5369ea8b8, identity aec251e1697cce17131e74e57bd642b7ab9f7082d74e82321d2f05e8f3f88b78), `v896-critique-b2-packet.json` (packet 6862e711cca4d7ffe07efb1ab52f5ead8af14da25c4110b3f3c427cbe4fccd86, identity aec251e1697cce17131e74e57bd642b7ab9f7082d74e82321d2f05e8f3f88b78)
- Follow-up packet (retained as evidence): `v896-critique-c2-packet.json` (packet 90def7ab0b7ee10bfcc26951c33b67f6417b5195bcf7d3a8ccaf68fa0ae26c71, identity bf9bcb5c76db92e32d32409cbb3a3d75cf885c18607d1bf93a80bf5a65e82316)

## Counterweight Disposition

- A/F1 (unknown-vs-absent collapse) — Act Before Ship. Fixed: `scoped_diff_present` is three-valued; unobservable suppresses the stop. Proof: overdue-watch-with-broken-git test.
- A/F2 (receipt weaker than relay) — Act Before Ship. Fixed: guard phases merge into `lane_progress` with `merged_guard_phases` recorded. Proof: merge regression test.
- B/F1 (tail-evicted CONTRACT-READ) — Act Before Ship. Fixed: cumulative phase union with first-observation time kept. Proof: 70 KiB noise regression test.
- B/F2 (doc proof_status mismatch) — Bundle Anyway. Fixed: docs name `proof_status` for the noop contract.
- B/F3 (abnormal-order divergence) — Act Before Ship. Fixed: one shared `_abnormal_child_state` order; combined-flag tests.
- A2/F1 (BLOCKED without enforcement) — Act Before Ship. Fixed: blocked-linger grace kill (default 60 s). Proof: grace unit test.
- A2/F2, B2/F1 (lost marker drops blocker) — Act Before Ship. Fixed: guard stop reason merges into the blocker. Proof: merge tests.
- A2/F3 (no live E2E) — Act Before Ship. Fixed: bounded live kill-and-receipt tests for both the no-progress and the linger paths.
- C2/F1 (evicted BLOCKED evades grace) — Act Before Ship. Fixed: first observed blocker kept cumulatively. Proof: tail-eviction linger test.
- C2/F2 (linger path lacks live proof) — Act Before Ship. Fixed: live blocked-linger kill-and-receipt test.
- D — pass, no findings on the final tree.

Non-claims: no worker ran a test suite or live executor; verdicts rest on the identity-bound inline semantic payloads. The release lane (`run-quality.sh --full --release`, 89 passed, 0 failed) re-proves every changed line independently of these reviews.
