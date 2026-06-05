fix(web-fetch): guarantee gather browser close and fail-visible clean-runtime proof

Close #302.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #302 ensure agent-browser gather sessions close and prove clean runtime on
exported hosts.
JTBD: a gather/web-fetch run that opens an agent-browser session — on any host,
including exported/installed layouts and arbitrary repo roots — must always close
the session and prove the runtime is clean, failing visibly instead of leaking a
Chromium tree or reporting a skipped proof as a clean success.
Root cause: close ran inline with no `finally` (a raise between open and close
leaked the session); the post-close guard returned None (= clean) when
`repo_root/scripts/agent_browser_runtime_guard.py` was absent, silently skipping
proof on exported/non-repo-root hosts; and the runtime guard only flagged orphan
*daemons*, so reparented (PPID=1) or `<defunct>` Chromium whose daemon had died
was reported clean.
Debug artifact: charness-artifacts/debug/2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md
Siblings: sibling search covered all four in-process browser exit paths
(render success/failure, network recon success/failure, classification failure,
timeout) and both guard consumers (acquire's post-close assert and the doctor
healthcheck), plus the gather→acquire→guard reach across repo-root and exported
layouts. Decision: fix the whole class — wrap the session lifecycle in
try/finally so close + proof run on every path; resolve the guard from
repo_root/scripts then any ancestor (bundled) and return guard_unavailable when
absent; extend inspect_runtime with reparented/zombie residue folded into the
health check. Proof: 63 tests green across the web-fetch and runtime-guard suites
(close-attempted on success+failure, guard_unavailable fail-visible, exported
reach with a failing bundled guard proving it ran, reparented/zombie residue not
clean, desktop-Chrome/dockerd not false-flagged); deterministic closeout
aggregate completed; dev host residue count 0.
Prevention: close is guaranteed by `finally`; a missing guard degrades via
guard_unavailable; the runtime gate counts reparented/zombie residue; and
regression tests lock each gap (incl. the desktop-Chrome PID-1 false-positive
guard), so a future edit that reintroduces a silent skip or misclassification
fails a test. Reaping PID-1 zombies stays Ceal-owned (Charness only avoids
misclassifying them as clean); live exported-host runtime proof is a non-claim.
Tests: `pytest -q tests/test_web_fetch_cleanup.py
tests/test_agent_browser_runtime_guard.py tests/test_web_fetch_support.py
tests/test_web_fetch_content_persistence.py tests/test_gather_google_workspace.py`
(63 passed); `run_slice_closeout.py` deterministic aggregate completed.
Critique: charness-artifacts/critique/2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md
