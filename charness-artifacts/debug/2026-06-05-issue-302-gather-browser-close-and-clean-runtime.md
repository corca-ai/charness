# Debug #302 — gather agent-browser close + clean-runtime proof on exported hosts
Date: 2026-06-05
Issue: #302 (bug-class; mechanism documented in the issue, confirm-and-fix)
Surface: `skills/support/web-fetch/scripts/acquire_public_url.py`,
`skills/support/web-fetch/scripts/agent_browser_session.py` (new),
`scripts/agent_browser_runtime_guard.py`,
`skills/public/gather/scripts/gather_public_url.py`.

## Problem

A `gather` agent-browser acquisition could leak a `charness-gather-*` browser
session and still report a clean close, especially on exported/installed hosts.
Four falsifiable gaps, all confirmed against pre-fix code, combine so that a
session leak or post-close runtime residue is silently read as success.

## Correct Behavior

Every in-process acquisition path closes its agent-browser session, and a
post-close runtime proof must actually run (or fail visibly) on the repo-root,
exported plugin, and arbitrary-user-repo layouts. Reparented or zombie residue
must count as unclean, while unrelated host processes must not.

## Observed Facts

- Pre-fix `acquire` ran `agent-browser close` inline after render + network
  recon with no `finally` (`git show HEAD:...acquire_public_url.py:288-321`).
- Pre-fix `_assert_browser_runtime_clean` returned `None` (= clean) when
  `repo_root/scripts/agent_browser_runtime_guard.py` did not exist.
- `gather_public_url.py` resolves the support impl via `SCRIPT_DIR.parents[2]`;
  the guard proof was reachable only at `repo_root/scripts`.
- Pre-fix `inspect_runtime` only flagged orphan daemons (`agent-browser` +
  `daemon.js`, `ppid==1`); reparented-to-PID-1 or `<defunct>` residue was unseen.

## Reproduction

Reading the pre-fix code paths confirms each gap: a raise between opening the
session and the inline close (e.g. `classify`/`_attempt_from_text` or the
network branch raising) leaves the session open; an exported/arbitrary repo_root
has no `repo_root/scripts` guard so the proof is skipped; a daemon death that
reparents Chromium to PID 1 seeds no descendant scan so residue reads clean —
the ceal-prod runtime-pressure pattern.

## Candidate Causes

- No `finally` around the render + network stage, so any intermediate raise
  skips the close (Gap 1).
- Absent-guard default returned "clean" instead of fail-visible, so exported
  surfaces silently skipped the post-close proof (Gap 2).
- Guard reachable only at `repo_root/scripts`, so the exported plugin layout and
  arbitrary user repo_root could not resolve it (Gap 3).
- Residue classifier scoped to orphan daemons only, missing reparented/zombie
  browser trees (Gap 4).

## Hypothesis

Close must run in a `finally`; the runtime proof must be resolvable from the
exported layout and fail visibly when no guard is found; and the residue
classifier must also count reparented-PID-1 and `<defunct>` agent-browser /
headless-Chromium processes — without misclassifying desktop Chrome or dockerd.

## Verification

Test-level only (fakes for agent-browser / ps / guard); no live exported-host
run is claimed. `tests/test_web_fetch_cleanup.py` (close attempted on render
success + failure; `guard_unavailable` fail-visible in an isolated layout;
gather→acquire→bundled-guard reach in a synthetic exported layout where a failing
bundled guard proves it ran) and `tests/test_agent_browser_runtime_guard.py`
(reparented/zombie residue not clean; desktop Chrome and dockerd not flagged) —
63 tests green; deterministic closeout aggregate completed; dev host residue 0.

## Root Cause

The acquisition lacked a `finally`-guaranteed close, the post-close runtime
proof defaulted to "clean" when its guard could not be resolved from non-repo
layouts, and the residue classifier only recognized orphan daemons — so a leak
or post-close residue was reported as a clean success.

## Prevention

- Gap 1: `_browser_stage` wraps render + network in `try` and closes + asserts
  runtime clean in `finally`, so close runs on every in-process path including an
  exception (which then propagates loudly — never a silent clean).
- Gap 2: new `agent_browser_session.assert_runtime_clean` returns a fail-visible
  `guard_unavailable` string when no guard resolves, degrading the disposition
  (`cleanup=failed`), never a clean close.
- Gaps 2+3: new `resolve_runtime_guard` searches `repo_root/scripts` first, then
  every ancestor of the acquire script, so the bundled guard is reachable from
  the exported layout and an arbitrary user repo_root. Exported reach + cleanup
  proof pinned by test.
- Gap 4: `inspect_runtime` adds `reparented_residue` (PPID=1 browser-marked,
  non-daemon, non-defunct) and `zombie_residue` (`<defunct>` agent-browser /
  headless-Chromium); `runtime_residue_total` folds both into `--assert-no-orphans`
  / `--doctor-check` health (waivable by `CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1`).
  Detection is scoped to agent-browser names plus *headless* Chrome/Chromium so a
  desktop Chrome at PID 1 is not misclassified, and `daemon.js` is excluded so
  dockerd's `daemon.json` is not flagged. Residue is detected, not reaped —
  reaping PID-1 zombies stays the container init's job (Ceal-owned).
