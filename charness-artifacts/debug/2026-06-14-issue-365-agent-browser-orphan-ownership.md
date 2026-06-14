# Issue #365 agent-browser Orphan Ownership Debug
Date: 2026-06-14

## Problem

`scripts/agent_browser_runtime_guard.py --cleanup-orphans --execute` killed a
concurrent, unrelated task's live agent-browser daemon running in a different
checkout on the same host (#365).

## Correct Behavior

- Given a host where this checkout has a leftover agent-browser daemon AND a
  neighbor task (another checkout) has a live agent-browser daemon,
- When the guard runs `--cleanup-orphans --execute` (or `--assert-no-orphans` /
  `--doctor-check`),
- Then it targets/flags only daemons it can prove are owned by THIS checkout and
  leaves the neighbor's daemon untouched; a daemon whose ownership cannot be
  proven is never killed (fail closed).

## Observed Facts

- Symptom (verbatim intent): a `parental-interaction-eval` job in another
  checkout had its `agent-browser wait` hang after this session ran
  `--cleanup-orphans --execute`; its daemon had been killed.
- `inspect_runtime` selects kill targets via
  `orphan_daemons = [p for p in daemons if p.ppid == 1]`
  (`scripts/agent_browser_runtime_guard.py:126`) over `daemons` matched by
  `is_agent_browser_daemon` (`:90`, command contains `agent-browser` +
  `daemon.js`), scanned machine-wide by `list_processes` (`:82`, `ps -eo ...`).
- No ownership/checkout filter exists anywhere in the daemon/residue selection.

## Reproduction

Launched one charness gather-style session from this checkout
(`agent-browser --session charness-causalprobe-<pid> open about:blank`) and
inspected the resulting daemon read-only (no kills of anything else):

- `ps`: the daemon shows `<pid> 1 node .../dist/daemon.js` — `ppid == 1` while
  the session is live and actively in use.
- `readlink /proc/<pid>/cwd` -> `/home/hwidong/codes/charness` (this checkout);
  `PWD=/home/hwidong/codes/charness`; `AGENT_BROWSER_SESSION=charness-causalprobe-<pid>`.
- After `agent-browser close`, the daemon persists and `--json` inspect reports
  it as `orphan_daemon_count: 1`.

## Candidate Causes

- Control-flow: `ppid == 1` is treated as "abandoned/orphan" but agent-browser
  daemonizes (setsid -> reparent to init), so EVERY live daemon has `ppid == 1`.
- State/environment: the scan is machine-wide (`ps -eo`) and single-tenant in
  its assumption — it presumes every agent-browser daemon on the host is this
  task's, ignoring concurrent checkouts/tasks.
- Logic: `is_agent_browser_daemon` matches by command substring only, with no
  per-checkout ownership signal (cwd / env / socket dir) consulted.

## Hypothesis

If the guard scoped daemon/residue selection to processes whose `/proc/<pid>/cwd`
resolves under the guard's `repo_root` (fail-closed on unknown cwd), then a
neighbor checkout's daemon (cwd outside `repo_root`) would not be selected and
would survive `--cleanup-orphans --execute`, while a genuine this-checkout
daemon would still be flagged and cleaned.

## Verification

- Confirmed empirically that a live, in-use daemon already has `ppid == 1`
  (falsifies "ppid==1 == abandoned").
- Confirmed the daemon's cwd is the launching checkout and it does not `chdir`
  away (falsifies "cwd is unreliable / daemon chdirs to /"), so cwd is a
  reliable checkout-ownership signal on this Linux runtime.
- Confirmed `AGENT_BROWSER_SESSION` is present in the daemon environ as a
  secondary marker, but cwd is the checkout-specific signal (session names are
  charness-wide, not checkout-specific) and needs no launch-path change.

## Root Cause

The guard classifies a daemon as a reapable "orphan" purely by `ppid == 1` over
a machine-wide process scan with no ownership filter. Because agent-browser
daemons are detached-by-design (always `ppid == 1`), this matches every live
daemon on the host, so `--cleanup-orphans --execute` reaps neighbor tasks' live
daemons. Structural cause: a single-tenant-host mental model encoded as a coarse
machine-global signal (`ppid==1` + command substring) with no per-task ownership
scoping.

## Invariant Proof

- Invariant: n/a - not a workflow-boundary propagation bug (single-component
  process-ownership classification bug, no producer/consumer transport)
- Producer Proof: n/a
- Final-Consumer Proof: n/a
- Interface-Shape Sibling Scan: n/a
- Non-Claims: cwd-ownership is verified on Linux `/proc` only; non-Linux hosts
  cannot read `/proc/<pid>/cwd` and fall to fail-closed (no cleanup), which is
  not separately proven here.

## Detection Gap

- runtime-guard unit tests (`tests/test_agent_browser_runtime_guard.py`) | every
  orphan/residue test simulates a single-tenant host (all simulated daemons are
  implicitly "mine"); none model a foreign-checkout daemon, so none could fire
  on the cross-task kill | smallest change: add a test asserting a foreign-cwd
  daemon is NOT in `orphan_tree_pids`/`cleanup` targets and a this-checkout
  daemon still is.
- release fresh-checkout / doctor probe | calls `--assert-no-orphans` but has no
  concurrency model, so it false-passes single-tenant and false-fails when any
  unrelated daemon is alive | smallest change: ownership scoping makes the probe
  robust under concurrent browser activity (covered by the same fix).
- This class is human-detected (a neighbor task hung); no monitor watches
  cross-task daemon kills.

## Sibling Search

- Mental model: "this host is single-tenant — every agent-browser process I can
  see is mine, and `ppid==1` means abandoned." Both halves are false on a shared
  host running concurrent checkouts with detached daemons.
- same-layer (in-file): `reparented_residue` (`:137`) and `zombie_residue`
  (`:145`) select machine-wide with the SAME no-ownership flaw | decision: same
  bug, fix now (scope all three uniformly) | proof: static scan + local payload
  proof (inspect_runtime over simulated processes).
- abstraction-up: any other gate that reaps/flags a machine-global resource as
  task-owned | decision: proof-backed no-action | proof: `rg` over `scripts/`
  for `os.kill|SIGKILL|SIGTERM|pkill|ppid == 1|ps -e` finds only this guard;
  `run_slice_closeout.py:121 process.kill()` kills the guard's own child by
  handle (not machine-wide) and `run_cosmic_ray_mutation.py` signals itself —
  neither is a sibling.
- specialization-down: the cleanup kill path (`cleanup_orphans` -> `kill_pids`
  over `orphan_tree_pids`) inherits ownership scoping for free once
  `orphan_daemons` is scoped | decision: same bug, fixed by the root fix | proof:
  `orphan_tree_pids` derives from scoped `orphan_daemons`.
- cross-file: no cross-file sibling: the only machine-wide `ppid==1`
  process-kill-by-coarse-signal site in the repo is this guard (rg-confirmed).

## Seam Risk

- Interrupt ID: agent-browser-orphan-ownership-365
- Risk Class: operator-visible-recovery
- Seam: OS process table + /proc host runtime; --cleanup-orphans is destructive to live processes
- Disproving Observation: a live in-use agent-browser daemon already has ppid==1 (host disproved the "ppid==1 means abandoned" local model), confirmed by direct observation and resolved this session
- What Local Reasoning Cannot Prove: that /proc/<pid>/cwd is readable and checkout-specific on every host (non-Linux / restricted hosts); handled by fail-closed and recorded as a non-claim
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Scope daemon/residue selection in `inspect_runtime` to this-checkout-owned
  processes via `/proc/<pid>/cwd` resolved under `repo_root`; fail closed on
  unknown cwd so a daemon that cannot be proven owned is never killed/flagged.
- Add the missing detection: a unit test asserting a foreign-cwd daemon is never
  targeted and a this-checkout daemon still is (closes the detection gap), plus a
  real-process CLI test that spawns owned + foreign marker processes and proves
  the foreign one survives `--cleanup-orphans --execute`.

## Related Prior Incidents

- `2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md` — reparented/
  zombie residue detection added (the in-file siblings now being scoped).
- `2026-05-21-agent-browser-orphan-closeout-recurrence.md` — prior orphan
  closeout recurrence on the same guard.
- `2026-05-20-agent-browser-runtime-hygiene.md` — original runtime-hygiene
  guard introduction.
