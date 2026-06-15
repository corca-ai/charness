# Issue 371 agent-browser Upstream Lifecycle Split Debug
Date: 2026-06-15

## Problem

Issue #371 reports that `agent-browser` leaves Chromium process trees and
`agent-browser-chrome-*` profile directories alive after the invoking turn ends
by normal completion, cancellation, provider failure, or timeout.

## Correct Behavior

The browser process tree and its temporary profile directory should be tied to
the tool-call/session lifecycle. Ending or aborting the invocation should tear
down the daemon-owned Chrome tree and remove or bound the profile directory; a
downstream age-based reaper is only a mitigation.

## Observed Facts

- The local issue is open and names a ceal incident with 99 Chromium processes,
  roughly 1080 PIDs, and 46-50h-old `agent-browser-chrome-*` profile dirs.
- `scripts/agent_browser_runtime_guard.py` detects this checkout's orphaned
  daemon/residue by `/proc/<pid>/cwd` and can clean owned orphan daemon trees.
- The guard does not launch `agent-browser`, hold a per-tool-call session
  handle, observe provider aborts, or own temp-profile cleanup.
- `integrations/tools/agent-browser.json` declares upstream
  `vercel-labs/agent-browser` and a manual external-binary lifecycle.
- Upstream issue `vercel-labs/agent-browser#1334` is open and covers
  interrupted/killed/timed-out sessions leaving Chrome helpers and temp
  `agent-browser-chrome-*` dirs.
- Adjacent upstream issues `#1401` and `#1371` cover Linux launch zombies and
  high-CPU orphaned helpers under temp profiles.
- `gh repo view vercel-labs/agent-browser` shows issues enabled but this token's
  `viewerPermission` is `READ`.

## Reproduction

Source inspection reproduces the ownership gap in this repo: the only local
runtime code is `scripts/agent_browser_runtime_guard.py`, which scans existing
processes after residue exists. It has no call path that starts or joins an
`agent-browser` tool invocation, no session-end callback, and no profile-dir
lease to delete on completion or abort.

## Candidate Causes

- Host abort semantics may kill only the client side of an exec, not the
  in-container daemon or its Chrome process group.
- `agent-browser` self-daemonizes, so a parent-process kill does not necessarily
  reach the detached daemon or browser tree.
- Charness consumes `agent-browser` as an external binary and owns only a
  healthcheck/cleanup guard, not the upstream daemon's launch and teardown
  lifecycle.
- Profile-dir cleanup is coupled to upstream Chrome/session ownership; local
  process-table cleanup cannot prove which `agent-browser-chrome-*` dirs belong
  to a just-ended invocation.

## Hypothesis

#371 should not be closed by local reaper or doctor changes. The honest local
disposition is an upstream split to `vercel-labs/agent-browser#1334`, with
`#1401` and `#1371` as adjacent upstream evidence, plus a local manifest note
that the runtime guard is downstream drift detection rather than lifecycle
teardown.

## Verification

- `gh issue view 371 --repo corca-ai/charness` confirmed #371 is open and asks
  for tool-call lifecycle teardown, not another reaper.
- `gh issue view 1334/1401/1371 --repo vercel-labs/agent-browser` confirmed
  open upstream coverage for the same or adjacent process/profile leak class.
- `gh repo view vercel-labs/agent-browser --json viewerPermission,hasIssuesEnabled`
  confirmed upstream issues are enabled and this token has read-only permission.
- Local inspection confirmed no Charness code owns the invocation-bound daemon
  or profile lifecycle needed to produce teardown proof.

## Root Cause

The durable lifecycle owner is upstream `agent-browser` and/or the host
integration that can bind a daemon/browser session to a tool-call handle.
Charness only observes residue after the fact through a repo-local runtime
guard, so it cannot prove normal/abort/failure/timeout teardown or safely claim
profile-dir ownership at invocation end.

## Invariant Proof

- Invariant: #371 is closable only with proof that a completed, aborted, failed,
  or timed-out invocation tears down both the browser process tree and
  `agent-browser-chrome-*` profile directory, or with an explicit split to the
  owning layer.
- Producer Proof: upstream `agent-browser` owns daemon launch, Chrome process
  group, and temp profile creation; Charness declares that ownership in
  `integrations/tools/agent-browser.json`.
- Final-Consumer Proof: this slice records no local issue closeout and adds a
  manifest note that the Charness guard is downstream drift detection, while the
  upstream lifecycle bug is tracked in `vercel-labs/agent-browser#1334`.
- Interface-Shape Sibling Scan: local guard issue #365 covered ownership-safe
  cleanup after residue exists; it is a mitigation sibling, not a lifecycle
  teardown fix.
- Non-Claims: no live teardown proof was produced; #371 remains unresolved in
  the local issue tracker until upstream/tool-call lifecycle behavior is fixed
  or a host-owned lifecycle handle is added.

## Detection Gap

The repo had a guard for owned orphan daemons but no artifact or manifest note
that prevented future agents from treating that guard as full lifecycle
closure. The smallest local detection is this split record plus an integration
note that points at upstream lifecycle ownership.

## Sibling Search

- same layer: `scripts/agent_browser_runtime_guard.py` cleans residue after it
  exists; decision: leave behavior unchanged because broadening reaping would
  not prove invocation teardown.
- abstraction up: host/tool-call orchestration owns cancellation and timeout
  boundaries; follow-up: deferred host-lifecycle-handle until a concrete host
  integration surface is available.
- specialization down: temp profile dirs need upstream session/profile leases;
  follow-up: deferred upstream-agent-browser-1334.
- cross-file: `integrations/tools/agent-browser.json` was missing the ownership
  note that distinguishes runtime drift detection from upstream lifecycle.

## Seam Risk

- Interrupt ID: agent-browser-upstream-lifecycle-371
- Risk Class: operator-visible-recovery
- Seam: external binary daemon lifecycle, host tool-call cancellation, and temp profile ownership
- Disproving Observation: upstream #1334/#1401/#1371 show the leak exists in the external lifecycle layer; local Charness code has only post-hoc runtime guard access
- What Local Reasoning Cannot Prove: that upstream or a host runtime now tears down Chrome process/profile state on completion, abort, failure, and timeout
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Record #371 as an explicit upstream split rather than a local closeout. Keep
#371 open from Charness until a controlled teardown proof covers both process
tree and profile directory at invocation end.

## Related Prior Incidents

- `2026-06-14-issue-365-agent-browser-orphan-ownership.md` - local guard
  ownership bug; fixed post-hoc cleanup scoping, not invocation lifecycle.
- `2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md` - earlier
  gather/browser closeout recurrence on runtime residue.
