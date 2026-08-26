# Implementation contract — #669 SIGTERM process-tree guard

Date: 2026-08-27 Asia/Seoul

## Decision

Close the ownership gap at the `Popen` constructor boundary. A monitored phase
records SIGINT/SIGTERM/SIGHUP without raising until the returned process object
is bound, restores the caller's handlers inside the existing cleanup envelope,
and kills/drains the process group before replaying a recorded signal. Do not
mask the child, redesign scheduling, or broaden proof to every host kernel.

## Owned surface

Charness owns `scripts/subprocess_guard.py`, its checked-in
`plugins/charness/scripts/subprocess_guard.py` export, and
`tests/test_subprocess_guard.py`. The direct child/descendant fixture proves
the local process-group boundary. Host signal semantics, SIGKILL, Windows,
hosted enforcement, and consumer adoption remain outside this slice.

## Acceptance checks

- Inject SIGTERM after a real `Popen` has created the child and before wrapper
  return; record command, injection point, child/descendant PIDs, and group.
- Prove the guard performs one group cleanup and bounded drain before replaying
  the signal, with no live group or descendant afterward.
- Preserve the existing wait-exception, timeout, output, and normal signal
  behavior paths.
- Verify source/export parity and run focused plus related standing tests from
  an explicit clean named proof worktree.

## Change carrier

Commit `529062620a28fdae8413dc7b961846266412dee6` adds the constructor-boundary
handler guard and the deterministic child-plus-grandchild regression fixture.

## Verification receipt

- Base: `e3ddd1f2ceaeb0a87bb3a52a1dd92a0c4f728374`
- Target: `529062620a28fdae8413dc7b961846266412dee6`
- Proof branch: `proof/issue-669-sigterm-20260827`
- Proof path: `/tmp/charness-669-proof-20260827`
- Direct focused guard suite: `25 passed`
- Standing focused runner with external basetemp and cache/pycache isolation:
  `25 passed`
- Related combined standing runner: `34 passed`
- Pre-commit prediction, focused ruff, source/export parity, explicit
  isolation, and final clean proof worktree: passed.

No dirty-parent changed-line verdict was attempted.

## Non-claims

No universal changed-line proof, forced fresh-eye review, handoff update,
micro-slice record, installed-host behavior, every-kernel guarantee, remote CI,
push, release, tag, or consumer-repository adoption is claimed.
