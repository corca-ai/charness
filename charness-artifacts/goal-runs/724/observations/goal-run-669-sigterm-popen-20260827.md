# Goal Run observation — #669 SIGTERM process-tree guard

Date: 2026-08-27 Asia/Seoul

## Scope receipt

- Parent: `corca-ai/charness#724`
- Child: `#669`, `backlog-669`
- Base SHA: `e3ddd1f2ceaeb0a87bb3a52a1dd92a0c4f728374`
- Target SHA: `529062620a28fdae8413dc7b961846266412dee6`
- Path scope: `scripts/subprocess_guard.py`,
  `plugins/charness/scripts/subprocess_guard.py`, and
  `tests/test_subprocess_guard.py`
- Proof worktree: `/tmp/charness-669-proof-20260827`
- Proof branch: `proof/issue-669-sigterm-20260827`

## Decision and implementation

The constructor race was confirmed. Before the repair, a real `Popen` wrapper
sent SIGTERM after fork/exec and before returning the process object; the child
remained live because cleanup was nested inside the not-yet-entered `with`
block. Commit `529062620a28fdae8413dc7b961846266412dee6` adds a temporary
non-raising interruption handler, restores the caller's handlers inside the
cleanup envelope, and replays recorded signals only after group kill and drain.
The checked-in plugin export is byte-identical to the canonical script.

## Verification

- Clean named-worktree preflight and `charness worktree doctor --require-isolation`:
  passed before proof.
- Direct focused `tests/test_subprocess_guard.py`: `25 passed`.
- Exact standing target through `run_standing_pytest.py` with external basetemp
  and `PYTHONDONTWRITEBYTECODE=1`: `25 passed`.
- Related combined standing target with
  `tests/quality_gates/test_standing_pytest_run_execution.py`: `34 passed`.
- Focused ruff, `py_compile`, `git diff --check`, source/export generation
  parity, and final tracked/untracked/cache/pycache cleanliness: passed.

Proof commands used explicit base/target/path scope and did not aggregate the
dirty parent diff. The parent worktree was not reset, restored, stashed, or
broadly cleaned.

## Goal Run provider evidence

The #724 provider updated #669 and returned `status: verified-write` with
`body_verified: true`. The operation receipts are:

- `charness-artifacts/goal-runs/724/observations/update-body-669-runtime-race-20260827-1.started.json`
  (`64427819dba0f181891b5d177508955f565fd64780dadc6636360fa438517854`)
- `charness-artifacts/goal-runs/724/observations/update-body-669-runtime-race-20260827-1.terminal.json`
  (`d9832a9915aaf7d59f77a56edc5bda575590f144f572800aa956d2c25b32ae15`)

A pre-close independent issue read returned `comments_read: true`, `state: OPEN`,
and the body matching the first submitted local body file
(`sha256:da0058c0c60bb3e510d436ba0a5fae23276a5fef77db65619929f3534ed5d509`).

## Closeout readback

The manual fallback carrier was validated before publication, then posted and
closed #669. The close comment is
`https://github.com/corca-ai/charness/issues/669#issuecomment-5430539474`.
The final `verify-closeout --expect-state CLOSED` returned `status: verified`,
`confirmation: confirmed` through backend-state-readback, empty missing fields
and state mismatches, and the explicit advisory that resolution fresh-eye was
skipped because this host exposes no Agent/subagent tool. The Goal Run local
close observation is recorded by:

- `charness-artifacts/goal-runs/724/observations/record-observation-669-close-20260827-1.started.json`
  (`cc557a7c11a85148ef964b1c4633f428e3fb3f2bf73afa403b21c5fd7980125f`)
- `charness-artifacts/goal-runs/724/observations/record-observation-669-close-20260827-1.terminal.json`
  (`4b4612dcbe6c77816d3619393589397020a8e8d26b20920b9c32d8f5e671afed`)

After closeout, the body was corrected through a second Goal Run provider
`update-body` operation so the durable issue surface records the already-CLOSED
#707 separation rather than a new successor candidate. The provider returned
`status: verified-write` and `body_verified: true`:

- `charness-artifacts/goal-runs/724/observations/update-body-669-postclose-truth-20260827-2.started.json`
  (`91e379cb80f0ba473ea2b3408a1f6d8984fc039ef2d907f462d04018a0fb8f78`)
- `charness-artifacts/goal-runs/724/observations/update-body-669-postclose-truth-20260827-2.terminal.json`
  (`841ff9cb07fe4c5c0b3eb103acfe922e1353b047c3f42e33c0c34c575684474d`)

The subsequent independent issue read returned `comments_read: true`,
`state: CLOSED`, `comment_count: 2`, and the body matching the final local body
file (`sha256:25879a257d31ac86c7b095c24ba1bef65f8c4f978b98885ea5dfa0b2ac53501a`).

## Separate surfaced report

The existing #669 comment `#issuecomment-5324465079` also reports a release
planner timeout and empty structured stdout under contention. That is a
separate release-planner/contract-test boundary, not a constructor process-tree
cause, and commit `529062620a28fdae8413dc7b961846266412dee6` does not claim to
resolve it. A read of the existing [#707](https://github.com/corca-ai/charness/issues/707)
confirmed that boundary is already CLOSED under commit `d1d853884`, with its
own closeout. It is not part of this fix, and no new successor is created here.

## Boundary and non-claims

The behavioral verdict is local-only-by-contract: the clean POSIX process-group
fixture and runner proof confirmed the reported behavior. No every-kernel or
Windows guarantee, SIGKILL behavior, installed-host or hosted/remote proof,
consumer-repository rollout, universal changed-line verdict, fresh-eye review,
or handoff update is claimed. The issue was closed through the explicitly
recorded operator-directed manual fallback; no micro-slice record, push,
release, tag, or consumer-repository adoption is claimed.
