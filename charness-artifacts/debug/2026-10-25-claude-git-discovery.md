# Debug: Claude repository discovery
Date: 2026-10-25

## Problem

Main a448: the native Claude probe reported its task HEAD as the host HEAD.
Raw consumer: `/home/hwidong/.cache/tmp/charness/runtime/60e0eff95728c8af/task-run/goal870-s33claudegatesproof-20261025/full-report.log:22`.
The host was independently c0afa92d95; the task was 8464a2a0e.

## Correct Behavior

Given a task and foreign checkout with different commits, Git resolves each
checkout by cwd or `-C`. Private-mode task commits remain private until trusted
finalization imports them. Native mode retains explicitly granted shared Git.

## Observed Facts

`configure_claude_environment` exported GIT_DIR and GIT_WORK_TREE for both modes.
`_git` and `_sandbox_git` use these variables only for individual private Git
operations. No GIT_COMMON_DIR exporter exists. Prior memory
`2026-10-25-claude-native-empty-protected-files.md` showed why testing only the
outer sandbox without the actual native tool is insufficient.

## Reproduction

`test_lane_git_discovery_respects_foreign_checkout` builds two distinct repositories
and a linked task worktree, then runs actual Git under the Claude bubblewrap prefix.
Both private and native parameters failed at `foreign -C discovery` before repair.
Evidence: orchestration `state/claude-git-discovery-red.log`.

## Candidate Causes

- Exported repository selection overrides Git cwd discovery. A mistaken source
report alone cannot explain both executable failures in independent repositories.

## Hypothesis

Removing process-wide selectors and binding a private gitdir pointer only over
the task `.git` restores foreign discovery without losing private commits.
Disconfirmer: foreign readback still equals task HEAD, or private finalization fails.

## Verification

The 14-test sandbox module passes, including both new parameters, hooks, shared-Git
read-only policy, private finalization and native continuation with a stale private
marker. Orchestration `state/claude-git-discovery-green.log` records the run.
Live a405 native Claude probe completed. Its actual tool output reports task
c0afa92d95f7d5739cd2447b9293c2a89f8d485a, host/cwd/main
73a4de9a8e8402c7a0abc8ac606b83f75e460413 and GIT_DISCOVERY=PASS.
Consumer: `/home/hwidong/.cache/tmp/charness/runtime/ddef9c1536a6013a/task-run/claudegitdiscoveryproof/full-report.log`.
Raw `claude.events.log` contains each readback; orchestration
`state/claude-git-discovery-live-readback.json` binds independent host recheck and
unchanged cleanliness. Independent scoped review found no blocker: both pointer
aliases and ancestors are protected; native opt-in skips stale private import.

## Root Cause

Pattern: process-scoped repository selection substituted for checkout-scoped
identity. Pattern of patterns: validation covered own-repository success, omitting
cross-repository operations. Why it arose: exporting selectors made private Git
convenient but silently changed every child tool's repository. Fewer next time:
the mount namespace carries task identity; private helper selectors stay local.
Why caught late: existing own-task hook/import tests could not distinguish repos.
Earlier next time: the two-repository seam fails before provider execution.
Why fixed late: discovery was revealed only in a full gate readback; this bounded
repair needs neither another gate run nor a dispatch refusal.

## Invariant Proof

- Invariant: cwd/-C repository selection survives Claude execution and own commits retain their selected custody.
- Producer Proof: configure exports no discovery selector; sandbox mounts a protected private pointer only in private mode.
- Final-Consumer Proof: executable Git foreign HEAD and post-finalization task HEAD assertions; actual Claude tool lines and terminal report above.
- Interface-Shape Sibling Scan: native/private share configure; private importer remains invocation-local.
- Non-Claims: no push, deployment, seat restart, Windows provider run or global inherited-environment hardening.

## Detection Gap

Sandbox tests verified task Git and confinement but never a second checkout.
The parameterized foreign cwd/-C check is the earliest cheap owner.

## Sibling Search

- Mental model: a task-local identity may be exported to unrelated child tools.
- same layer: Claude native/private configure | decision: same bug, fix now | proof: executable fixture.
- abstraction up: Codex/Muse runtime accepts inherited selectors but creates none | decision: valid follow-up outside the slice | proof: static scan only; follow-up:ambient-lane-git-selectors owner=scripts/task_run/task_run_runtime.py.
- specialization down: finalizer previously inferred mode from GIT_DIR; stale private runtime can outlive native opt-in | decision: same bug, fix now | proof: executable fixture.
- mental-model siblings: orchestration readonly_execution strips selectors defensively after consuming the owner; no exports here | decision: same class, diagnostic-only for this slice | proof: existing read-only roundtrip.
- cross-file: Win1/Win2/MacAir/Mac3/OC dispatch uses cwd/-C without selector exports | decision: same class, diagnostic-only for this slice | proof: static scan only.

## Seam Risk

- Interrupt ID: a448
- Risk Class: external-seam
- Seam: Claude process environment to native Git discovery
- Disproving Observation: prior real provider claimed host HEAD equaled task HEAD
- What Local Reasoning Cannot Prove: real Claude native readback
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-10-25-claude-git-discovery.md

## Prevention

Keep discovery in the worktree namespace and private import in the trusted
invocation. Protect both aliases of the mounted pointer against writes. No new
launch or dispatch refusal. Independent critique and live readback are complete; the remaining inherited-selector sibling has a named follow-up owner.
