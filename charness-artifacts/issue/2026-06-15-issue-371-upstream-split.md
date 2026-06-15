# Issue #371 upstream split draft
Date: 2026-06-15

Issue: https://github.com/corca-ai/charness/issues/371
Local disposition: do not close from this slice.

## Summary

The #371 symptom is real, but the durable fix is not in this repo's current
owned surface. Charness owns downstream runtime detection and cleanup for
checkout-owned orphan `agent-browser` residue; it does not own the
invocation-bound `agent-browser` daemon, Chrome process group, or temporary
profile directory lifecycle.

## Upstream tracker

- Primary: https://github.com/vercel-labs/agent-browser/issues/1334
- Adjacent Linux launch zombie path: https://github.com/vercel-labs/agent-browser/issues/1401
- Adjacent high-CPU/temp-profile residue path: https://github.com/vercel-labs/agent-browser/issues/1371

`vercel-labs/agent-browser#1334` covers interrupted/killed/timed-out sessions
leaving Chrome helpers and temp `agent-browser-chrome-*` profile dirs. This is
the closest owning-layer tracker for the #371 lifecycle ask.

## Local change in this slice

`integrations/tools/agent-browser.json` now states that invocation-bound Chrome
process/profile teardown is upstream `agent-browser` lifecycle ownership and
that Charness' runtime guard is downstream drift detection and cleanup after
residue already exists.

## Non-closure reason

No controlled teardown proof exists in this slice for normal completion,
cancellation, provider failure, or timeout. A local reaper or doctor warning
would not satisfy #371 because it runs after residue already exists and cannot
prove profile ownership at the ended invocation boundary.

## Draft issue comment if updating #371 later

This remains open locally as an upstream/tool-call lifecycle split, not a local
fix claim. The closest upstream owner is
vercel-labs/agent-browser#1334, with adjacent coverage in #1401 and #1371.

In Charness, the runtime guard can detect and clean checkout-owned orphan daemon
residue after it exists, but it cannot tie the upstream daemon/Chrome/profile
lifetime to normal completion, cancellation, provider failure, or timeout.
Closing this issue still needs controlled proof that both the process tree and
`agent-browser-chrome-*` profile dir are torn down at invocation end.
