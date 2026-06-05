# Debug #302 — gather agent-browser close + clean-runtime proof on exported hosts

Date: 2026-06-05
Issue: #302 (bug-class; mechanism documented in the issue, confirm-and-fix)
Surface: `skills/support/web-fetch/scripts/acquire_public_url.py`,
`skills/support/web-fetch/scripts/agent_browser_session.py` (new),
`scripts/agent_browser_runtime_guard.py`,
`skills/public/gather/scripts/gather_public_url.py`.

## Four falsifiable gaps (all confirmed against pre-fix code)

### Gap 1 — close not guaranteed on every in-process path
Pre-fix `acquire` ran `agent-browser close` inline *after* the render and
network recon, with **no `finally`**. A raise between opening the session and
that close (e.g. `classify`/`_attempt_from_text` raising, or the network branch
raising) left the `charness-gather-*` session open — a leaked browser tree.
Confirmed by reading `git show HEAD:...acquire_public_url.py:288-321`.

### Gap 2 — missing post-close guard silently read as clean
Pre-fix `_assert_browser_runtime_clean` returned `None` (= clean) when
`repo_root/scripts/agent_browser_runtime_guard.py` did not exist. On
installed/exported surfaces or an arbitrary gather repo_root, the guard file is
absent, so the post-close runtime proof was silently skipped and the close read
as a clean success.

### Gap 3 — exported-surface reach untested / fragile
`gather_public_url.py` resolves the support impl via `SCRIPT_DIR.parents[2]`,
which happens to land in both the repo-root and exported plugin layouts only
because the export drops `public/` and lifts `support/` (the offsets cancel).
The cleanup proof (the guard) was reachable only at `repo_root/scripts` — so an
exported gather against a user repo skipped proof (Gap 2). No test pinned the
exported reach + cleanup-proof path.

### Gap 4 — runtime guard misclassifies reparented/zombie residue as clean
Pre-fix `inspect_runtime` only flagged orphan *daemons* (`agent-browser` +
`daemon.js`, `ppid==1`). If the daemon died and its Chromium got reparented to
PID 1 (or became `<defunct>`), nothing seeded the descendant scan, so the
residue was reported clean — exactly the ceal-prod runtime-pressure pattern.

## Fixes

- **Gap 1:** `_browser_stage` wraps render+network in `try` and closes + asserts
  runtime clean in `finally`, so close runs on every in-process path including an
  exception (which then propagates loudly — never a silent clean).
- **Gap 2:** new `agent_browser_session.assert_runtime_clean` returns a
  fail-visible `guard_unavailable` string when no guard resolves, which degrades
  the disposition (`cleanup=failed`), never a clean close.
- **Gaps 2+3:** new `resolve_runtime_guard` searches `repo_root/scripts` first,
  then every ancestor of the acquire script, so the bundled guard
  (`plugins/charness/scripts/...`) is reachable from the exported layout and an
  arbitrary user repo_root. Exported reach + cleanup proof pinned by test.
- **Gap 4:** `inspect_runtime` adds `reparented_residue` (PPID=1 browser-marked,
  non-daemon, non-defunct) and `zombie_residue` (`<defunct>` agent-browser /
  headless-Chromium); `runtime_residue_total` folds both into `--assert-no-orphans`
  / `--doctor-check` health (waivable by `CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1`).
  Detection is scoped to agent-browser-specific names plus *headless* Chrome/Chromium
  so a developer's desktop Chrome at PID 1 is not misclassified, and `daemon.js`
  is excluded so dockerd's `daemon.json` is not flagged. Residue is detected, not
  reaped — reaping PID-1 zombies stays the container init's job (Ceal-owned).

## Proof

Test-level only (fakes for agent-browser / ps / guard); no live exported-host
run is claimed. `tests/test_web_fetch_cleanup.py` (close attempted on render
success + failure; `guard_unavailable` fail-visible in an isolated layout;
gather→acquire→bundled-guard reach in a synthetic exported layout where a failing
bundled guard proves it ran) and `tests/test_agent_browser_runtime_guard.py`
(reparented/zombie residue not clean; desktop Chrome and dockerd not flagged) —
63 tests green; deterministic closeout aggregate completed; dev host residue 0.
