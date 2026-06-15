# Issue #371 repair mitigation record
Date: 2026-06-15

Issue: https://github.com/corca-ai/charness/issues/371
Local disposition: mitigation shipped; do not close #371 from this change.

## Summary

Charness now exposes an operator-facing repair path for the runtime residue it
does own:

```bash
charness tool repair agent-browser
charness tool repair --execute agent-browser
```

The dry-run previews checkout-owned orphan daemon-tree cleanup. The execute
form runs `scripts/agent_browser_runtime_guard.py --cleanup-orphans --execute`,
then refreshes `agent-browser` doctor state and reports the post-doctor result.

## Causal Review

Fresh-eye causal review classified this as a mitigation, not a #371-closing
fix. The mistaken model is: "if Charness can clean and doctor passes afterward,
then the lifecycle bug is fixed." The correct model is: cleanup-after-leak
proves recovery, not prevention.

Issue #371 asks for invocation-bound teardown of both the browser process tree
and the matching `agent-browser-chrome-*` profile directory on normal
completion, cancellation, provider failure, and timeout. Charness still does
not own that upstream `agent-browser` daemon/profile lifecycle.

## Implemented Mitigation

- `charness tool repair agent-browser` reports a dry-run preview.
- `charness tool repair --execute agent-browser` executes owned orphan cleanup
  and post-doctor verification.
- `charness tool doctor agent-browser` now points cleanup-command runtime drift
  at `charness tool repair --execute agent-browser` instead of leaving the
  operator to copy a lower-level guard command.
- Repair JSON/text output includes the caveat that this is post-hoc mitigation
  only and that invocation-bound Chrome/profile teardown remains
  upstream/unproven.
- Unsupported tool repairs fail visibly with `repair.status: unsupported`.
- The generated CLI reference includes the new command.

## Non-Closure Reason

This does not prove invocation-end teardown. It intentionally keeps the same
boundary recorded in the upstream split artifact:

- cleanup runs after residue already exists;
- reparented/zombie-only residue can still require init/container action;
- profile-directory lifecycle remains upstream/host-owned unless Charness gains
  an invocation handle that can prove matching process and `/tmp` profile
  teardown for completion, cancellation, provider failure, and timeout.

## Proof

- `pytest -q tests/charness_cli/test_tool_lifecycle.py -k 'tool_repair or agent_browser_repair'`
  passed.
- `pytest -q tests/test_agent_browser_runtime_guard.py tests/test_web_fetch_cleanup.py tests/test_youtube_source.py -k 'agent_browser or browser or cleanup or orphan'`
  passed.
- `python3 ./charness tool repair --repo-root . --execute agent-browser` passed
  on this machine and post-doctor reported `agent-browser` ready.
- `python3 scripts/validate_packaging.py --repo-root .` and
  `python3 scripts/validate_packaging_committed.py --repo-root .` passed after
  plugin mirror sync.

## Issue Comment

Post a #371 comment after push/release stating that the repair UX shipped as a
downstream mitigation, but #371 remains open until controlled invocation-bound
process/profile teardown proof exists.
