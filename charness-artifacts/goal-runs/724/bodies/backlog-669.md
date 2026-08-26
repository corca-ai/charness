<!-- charness-work-item-key: backlog-669 -->
# Existing Work Item #669 — SIGTERM process-tree guard

## Purpose and premise

Fix the constructor race in Charness's long-phase process guard. `Popen` can
fork/exec a child before returning the `Popen` object; a SIGTERM handler that
raises in that window bypasses the existing `with process` cleanup and leaves
the new session alive. Keep unrelated kernel stalls, SIGKILL, and host adoption
outside this child.

## Owned change and acceptance

Charness owns `scripts/subprocess_guard.py` and its checked-in plugin export.
The guard temporarily records SIGINT/SIGTERM/SIGHUP around `Popen`, restores
caller handlers inside the process cleanup envelope, kills the child process
group before replaying a recorded signal, and preserves normal child signal
behavior. The controlled fixture injects SIGTERM after the real `Popen` creates
the child but before wrapper return, records the exact command and injection
point, and proves child, descendant, and group cleanup. Existing wait and
timeout cleanup remains intact.

## Verification and evidence boundary

- Base: `e3ddd1f2ceaeb0a87bb3a52a1dd92a0c4f728374`
- Target: `529062620a28fdae8413dc7b961846266412dee6`
- Proof branch: `proof/issue-669-sigterm-20260827`
- Proof path: `/tmp/charness-669-proof-20260827`
- Direct focused guard suite: `25 passed`
- Standing runner with external basetemp and cache/pycache isolation: `25 passed`
- Related combined standing runner (`tests/test_subprocess_guard.py` plus
  `tests/quality_gates/test_standing_pytest_run_execution.py`): `34 passed`
- Pre-commit prediction, source/export parity, focused ruff, and final clean
  proof-worktree check: passed.

The proof scope was explicit and did not aggregate the dirty parent diff.

## Resolution status

This issue was closed through the explicitly recorded operator-directed manual
fallback after the proof above. The final closeout state and comment are recorded
in the Goal Run observation; the skipped critique is an explicit host limitation,
not a fresh-eye result.

The separate release-planner report from the pre-existing comment is already
owned and closed by [#707](https://github.com/corca-ai/charness/issues/707),
including the script-specific timeout repair. It is not part of this issue and
does not need a new successor here.

## Non-claims

This proves the local POSIX process-group path only; it does not claim every
host kernel, Windows signal behavior, hosted/remote CI, installed-host
adoption, or consumer-repository rollout. No universal changed-line proof,
forced fresh-eye review, handoff update, micro-slice record, push, release, or
tag is claimed by this body.
