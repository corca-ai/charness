# SIGTERM-at-construction Debug Review
Date: 2026-08-27

## Problem

`run_monitored_phase` cleaned a child only after `subprocess.Popen` had returned
and entered its `with` block. A SIGTERM handler that raised during the narrow
fork/exec-to-return window therefore left the newly created child session alive.

## Correct Behavior

The guard must own the child process group before an interruption can escape.
Signals arriving while `Popen` is still constructing are recorded without
raising, the caller's handler is restored once the process object is bound, and
the group is killed and drained before the recorded signal is replayed. Normal
child signal dispositions and post-construction timeout/exception cleanup stay
unchanged.

## Observed Facts

- Before the repair, an inline wrapper called the real `Popen`, sent SIGTERM
  before returning its object, and observed `poll=None`; manual cleanup was
  required.
- The old cleanup lived inside `with subprocess.Popen(...) as process`, so that
  injection never reached `_kill_tree`.
- The repaired fixture records the parent and grandchild PIDs plus the process
  group, and the guard performs one group cleanup before replaying SIGTERM.
- Direct guard tests passed `25`; the standing wrapper passed `25`; the related
  standing combined run passed `34`.

## Reproduction

Run `python3 -m pytest -q tests/test_subprocess_guard.py -k popen` (or the
standing command naming `tests/test_subprocess_guard.py`) with the controlled
fixture `test_monitored_phase_kills_the_tree_when_sigterm_interrupts_popen`.
Its injection point is `after-real-Popen-before-return`; the child launches a
grandchild in the new session before the injection.

## Candidate Causes

- Cleanup was structurally nested below an object-binding boundary that could
  be interrupted.
- The signal handler raised before the parent had a PID/group owner.
- A broad process-mask fix could have leaked a blocked signal mask into the
  child, changing graceful termination semantics.

## Hypothesis

The missing ownership step is the constructor boundary: if the interruption is
recorded until the `Popen` object is bound, then the existing group kill and
bounded drain can close the tree without delaying signals during the wait.
disconfirmer: inject SIGTERM at the real-Popen-before-return seam and assert the
recorded group and descendant state after the guard exits.

Claim type: liveness
Candidate claim: the constructor-boundary repair owns and cleans the spawned tree.
Cheapest falsifier: the executable child-plus-grandchild fixture above.
Result: confirmed locally; the pre-fix probe orphaned the child and the repaired
fixture removed the group.

## Verification

Confirmed. The focused fixture fails the old shape by observing a live process
after the injected handler exception, and passes the repaired shape with one
`_kill_tree` call, a completed direct child, an absent process group, and absent
child/descendant PIDs. The standing and related combined runner paths also pass.

## Root Cause

The process guard had a cleanup contract only for exceptions after `Popen` had
returned. It had no owner for the interval in which the kernel had already
created the child but Python had not yet assigned the `Popen` object. The fix
closes that exact interval with a temporary non-raising handler and replays the
signal only after group cleanup.

## Invariant Proof

- Invariant: no Python-observable interruption at the `Popen` return boundary
  may leave a monitored child process group running.
- Producer Proof: the deterministic fixture injects SIGTERM at the named seam
  and records the exact process/group inputs.
- Final-Consumer Proof: `run_monitored_phase` invokes `_kill_tree` and bounded
  `_drain` before replay; the clean runner observed exit 0 and no live group.
- Interface-Shape Sibling Scan: `scripts/standing_pytest_run_record.py` is the
  caller-owned SIGTERM-to-KeyboardInterrupt boundary; it uses the repaired guard
  rather than duplicating tree cleanup.
- Non-Claims: no Windows, every-kernel, SIGKILL, hosted/remote, installed-host,
  consumer-repository, changed-line, fresh-eye, handoff, or release proof.

## Detection Gap

The existing test covered an exception from `_await_child` after `Popen` binding,
but no test injected a signal before the `with` body existed. The new real-Popen
wrapper closes that gap without making changed-line proof a universal gate.

## Sibling Search

- Mental model: lifecycle cleanup is placed after a resource-binding boundary.
- same layer: `scripts/subprocess_guard.py::_await_child` | decision: same class,
  diagnostic-only for this slice | proof: existing timeout/exception tests cover
  the already-bound path.
- abstraction up: `scripts/standing_pytest_run_record.py::_terminate_reaps_the_child`
  | decision: same class, fix now | proof: standing combined runner uses the
  shared guard and its signal handler remains restored.
- cross-file: `scripts/standing_pytest_run_record.py` | decision: same class,
  diagnostic-only for this slice | proof: static caller inspection plus `34`
  passed combined execution.

## Seam Risk

- Interrupt ID: constructor-process-ownership-gap-2026-08-27
- Risk Class: external-seam, repeated-symptom
- Seam: parent signal handler -> Popen construction -> child process-group owner
- Disproving Observation: the controlled fixture leaves a live group or
  descendant after the guard returns.
- What Local Reasoning Cannot Prove: signal delivery and process reaping on every
  host kernel, Windows behavior, or an installed consumer runtime.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Review Note: the risk taxonomy normally routes this external seam through a
  spec/fresh-eye boundary. The user explicitly directed direct `impl` work and
  omitted forced fresh-eye and handoff updates; no fresh-eye result is claimed.
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md

## Prevention

Keep constructor-boundary interruption coverage in the shared guard fixture,
preserve group ownership as an explicit acceptance check, and run focused plus
related combined gates from a clean named worktree. Treat other kernels, SIGKILL,
and hosted adoption as separate proof questions rather than adding a universal
changed-line blocker.

## Evidence Disposition

- Report Identity: issue:669#sha256:25879a257d31ac86c7b095c24ba1bef65f8c4f978b98885ea5dfa0b2ac53501a
- Reported Findings: 1
- Dispositioned Findings: F1
- Missing Findings: none
- Evidence Digest: sha256:867f15f1a2901844b73aa497de5ccc0b7a78f9c0263e0872d9b80c90d64deacb
- Report Source: charness-artifacts/goal-runs/724/bodies/backlog-669.md
- Report Source SHA256: 25879a257d31ac86c7b095c24ba1bef65f8c4f978b98885ea5dfa0b2ac53501a

## Adversarial Verification

- Finding: F1 | source: issue-669 | expected: SIGTERM during Popen construction reaps the entire child process group | stimulus: injected SIGTERM after real Popen and before wrapper return | disposition: reproduced | observed: pre-fix child remained alive until manual cleanup and repaired fixture killed group and descendant | proof: executable fixture | handoff: issue-669 debug record | next move: clean named-worktree proof | receipt: charness-artifacts/debug/receipts/2026-08-27-issue-669-constructor-race.json | receipt sha256: 9863d8611a049d9d246d2960106c6ac0c905ca93a4ac6c9ae10af547e2eb6e23
