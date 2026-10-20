# Release Critique: Charness v8.15.0
Date: 2026-10-20

## Decision Under Review

Release the candidate at `526fbaa17` as minor version 8.15.0. Since v8.14.9 it adds receive-time stamps (`charness_received_at`) on every JSON line of a lane's events log and `charness task status <task-id> --commands`, which reads them back into command durations, family starts, and phase times. The first critique attempt blocked the candidate at `9e4df9c8d`; `526fbaa17` repairs both findings, and this record covers the first attempt and its follow-up.

## Release Scope

- Version: `8.15.0`
- Tag: `v8.15.0`
- Bump rationale: minor, because `task status --commands` is a new additive operator option and the events log gains a field; nothing existing changes shape or invocation.
- Consumer change: none required. Event lines gain one leading field, and readers that ignore it see the executor's bytes unchanged.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the publish helper.
- Consumer-visible behavior: the stamped `<executor>.events.log`, `task status --commands`, and `execution.event_capture_incomplete` on a task result whose capture lost bytes.
- Documentation: `docs/agent-task-runs.md`, `docs/cli-reference.md`, and the v8.15.0 release notes.
- Adapter and integration surfaces: none changed.

## Verification Scope Decision

- Claim under test: event stamping never loses executor bytes silently on close, timeout, or interrupt; the timing reader does not fail on naive or malformed stamps; and the notes describe both accurately.
- Changed surfaces: `scripts/task_run/task_run_event_timing.py` and `scripts/task_run/task_run_execution.py`, their tests, `docs/agent-task-runs.md`, and the release notes in `9e4df9c8d..526fbaa17`. The full release range `1f09b8012..526fbaa17` was covered by the first attempt.
- Minimum sufficient proof: two verified committed-ref packets (the full range, then the repair range) each read by an independent read-only file-backed reviewer, plus the parent's run of `tests/charness_cli` (1419 passed). The new tests drive a real executor process through timeout, a signalled child, and a detached descendant, along with a parent interrupt and a failing sink, and assert the retained events log byte for byte.
- Deliberately omitted checks: the follow-up reviewer did not execute tests; the parent's run stands in. The full quality lane runs in the publish helper and the pre-push hook, not here.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback; unchanged in this release.
- Failure classification: subject-defect
- Negative control: none with rationale: the repair is pinned by tests that fail on the pre-repair pipe (an unread sink after close and a naive-stamp TypeError), and the follow-up judged the frozen repaired commit.
- Subject identity: sha256:e4ad0d71be8994c7fab4a28800bb898f8b7eb736984cb56ddea100c5edaaa06c
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:e3023c9dd207351733eaba567ee1a90ae7b7d9bed3e65d632ddb75075ed9bc39
- Failure identity: stable:no-failure
- Evidence identity: sha256:40302c987354fbfec2fcd088506af56a561e4561c793921e00dced22e6e92ba8
- Retry disposition: retry-new-identity
- Retry key: sha256:bf3bc2edd456d34e45c8263738a29ad772b5f826c88c5fb8e795fb847c6b680f

## Failure Angles

- Gawande / operational: whether the stamping pipe keeps every event byte and fails loudly. The first attempt found that close() could abandon its reader and the caller then closed the sink (R1, blocker), and that naive stamps could crash the reader (R2). The follow-up found both repaired and tested at the real pipe.
- Minto / communication: whether the notes match the code. The first attempt asked that durations be called receive-time estimates. The follow-up found that the notes now call them upper bounds and describe the capture receipt accurately.
- Raskin / interface: whether the `--commands` option and its refusal wording are sound. The first attempt dismissed the wording concern.

## Counterweight Pass

- Act Before Ship: R1 and R2, both fixed in `526fbaa17` before release.
- Bundle Anyway: the notes wording on receive-time upper bounds (watch item), fixed in the same commit.
- Over-Worry: that minor is too large a bump; the option is additive operator surface.
- Valid but Defer: none.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_event_timing.py | action: fix | note: R1. The reader now drains the buffered bytes on close, the sink is written only under a lock close() takes, a failing sink keeps the pipe drained, and any loss is recorded in `execution.event_capture_incomplete`; the follow-up resolved it.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_event_timing.py | action: fix | note: R2. A naive or malformed stamp counts as unstamped, and a mixed-log test pins it; the follow-up resolved it.
- F3 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: fix | note: the notes call durations receive-time upper bounds; the follow-up verified it.

## Operator Action Required

No migration is required. Operators update with `charness update`.

## Upgrade Path

Run `charness update`, then use `charness version` to read back the installed version.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: run_review.py file-backed worker, adapter backend codex_exec, read-only capability envelope, follow-up from the first attempt's result
- Host exposure state: host-defaulted
- Application state: the worker report records model_application_state unverified-by-provider, so the requested model and effort are not host-confirmed; read-only boundary on the lifecycle
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/review-20261020T184009Z-651960/worker-report.yaml
- Worker report identity: 9641beb73c33bd25c35bbcec99ca1b0d27ad032eb265de3fb8e2784586586ac3
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 470f764c37f39d7bfddc1c9c86cb936cd28a506e288e1ac32bfb2a8607daa6c4
- Worker report input identity: e3023c9dd207351733eaba567ee1a90ae7b7d9bed3e65d632ddb75075ed9bc39
- Worker report parent receipt identity: parent-ccc008003b31574b8578fa98459cbd7b2939e32521aa228a
- Worker report findings identity: 40302c987354fbfec2fcd088506af56a561e4561c793921e00dced22e6e92ba8

## Fresh-Eye Satisfaction

worker-delivered: the first file-backed read-only worker (`release-8150-candidate`) returned `block` with R1 and R2; a follow-up worker over the repair range returned `pass` with both resolved and an approval-eligible carrier bound to the packet below.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/review-20261020T184009Z-651960-packet.md
- Packet path: charness-artifacts/critique/review-20261020T184009Z-651960-packet.json
- Packet SHA256: 470f764c37f39d7bfddc1c9c86cb936cd28a506e288e1ac32bfb2a8607daa6c4
- Identity SHA256: e3023c9dd207351733eaba567ee1a90ae7b7d9bed3e65d632ddb75075ed9bc39
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/review-20261020T184009Z-651960-packet.json --packet-sha256 470f764c37f39d7bfddc1c9c86cb936cd28a506e288e1ac32bfb2a8607daa6c4 --identity-sha256 e3023c9dd207351733eaba567ee1a90ae7b7d9bed3e65d632ddb75075ed9bc39`

## Boundary Ownership

- Producer: `StampingPipe` and the executor invocation in `scripts/task_run/`.
- Consumer: `task status --commands`, lane events-log readers, and the task result.
- Owning surface: the repair lives in the existing timing owner; the execution record gains one key only when capture is incomplete.
- Verdict: owned-correctly
