# Resolution Critique #371 - agent-browser lifecycle split

Date: 2026-06-15
Issue: #371
Classification: bug, not locally fixed
Reviewer: bounded fresh-eye causal-review subagent plus bounded fresh-eye
resolution-critique subagent, read-only shared parent worktree.

## Slice under review

Record #371 as a non-closure upstream split because Charness owns only
post-hoc runtime drift detection and owned orphan daemon-tree cleanup for
`agent-browser`, while the reported bug requires invocation-bound teardown of
the upstream daemon's Chrome process tree and `agent-browser-chrome-*` profile
directory on completion, cancellation, provider failure, and timeout.

Changed surfaces:

- `integrations/tools/agent-browser.json`
- `plugins/charness/integrations/tools/agent-browser.json`
- `charness-artifacts/debug/2026-06-15-issue-371-agent-browser-upstream-lifecycle.md`
- `charness-artifacts/debug/seam-risk-index.json`
- `charness-artifacts/issue/2026-06-15-issue-371-upstream-split.md`

## Causal Review

JTBD: do not claim #371 is fixed unless process tree and profile-dir teardown
are proven at invocation end across normal completion, cancellation, provider
failure, and timeout.

Classification confirmation: bug, but not locally fixed. The local issue asks
for lifecycle teardown; Charness currently has only post-hoc detection/cleanup
after residue exists.

Root cause: durable lifecycle ownership is upstream `agent-browser` and/or a
host integration that can bind a daemon/Chrome/profile lease to a tool-call
handle. Local Charness code has no launch/session/end callback or profile lease.

Invariant proof: the split artifact and manifest note make the non-closure
explicit. Upstream `vercel-labs/agent-browser#1334` covers the broader
interrupted/killed/timed-out helper/profile leak, with adjacent coverage in
`#1401` and `#1371`. #371 remains open locally.

Detection gap: Charness already tests owned orphan daemon-tree cleanup, but had
no durable guard against future agents mistaking that mitigation for lifecycle
closure.

Sibling search: #302/#365 are mitigation siblings, not lifecycle owners. The
structural siblings are upstream daemon/session teardown, host cancellation
semantics, and profile lease cleanup.

Fresh-Eye Satisfaction: parent-delegated.

## Resolution Critique Findings

### Act Before Ship

- The initial draft allowed closure by "an explicit upstream-owned closure
  decision" without teardown proof, which weakened the #371 invariant.

Disposition: fixed before commit. The debug and issue artifacts now require
controlled proof that both process tree and profile directory are torn down at
invocation end before local closure.

### Bundle Anyway

- Include generated/export surfaces with the source manifest note.

Disposition: bundled. `sync_root_plugin_manifests.py` updated
`plugins/charness/integrations/tools/agent-browser.json`, and the debug
seam-risk index was refreshed.

- Tighten manifest wording so downstream "cleanup" cannot be read as full
  lifecycle teardown.

Disposition: bundled. The manifest now says Charness owns downstream drift
detection and owned orphan daemon-tree cleanup after residue already exists.

### Valid but Defer

- No runtime guard behavior, validator, or test change is required for this
  split. A local source change would risk treating post-hoc cleanup as #371
  teardown proof.

### Over-Worry

- The issue artifact's accidental-closeout language is otherwise safe: it says
  this slice does not close #371 and is not a local fix claim.

## Structured Findings

- bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-06-15-issue-371-upstream-split.md | action: fix | note: remove closure wording that did not require process/profile teardown proof
- bin: bundle-anyway | evidence: strong | ref: plugins/charness/integrations/tools/agent-browser.json | action: fix | note: bundle generated plugin manifest with source manifest
- bin: bundle-anyway | evidence: moderate | ref: integrations/tools/agent-browser.json | action: fix | note: clarify that local cleanup is owned orphan daemon-tree cleanup, not invocation-bound lifecycle teardown
- bin: valid-but-defer | evidence: strong | ref: scripts/agent_browser_runtime_guard.py | action: defer | note: runtime guard behavior remains post-hoc mitigation and should not be changed without teardown proof
- bin: over-worry | evidence: moderate | ref: charness-artifacts/issue/2026-06-15-issue-371-upstream-split.md | action: defer | note: draft says do not close from this slice and not a local fix claim

## Reviewer Tier Evidence

- requested tier: default
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: spawn tool accepted reviewer agent ids `019ecb28-8265-7df3-aaa2-e91f855b2ba9` and `019ecb28-986c-7bf2-986d-c6736a4b9dc2`; reviewer-tier application details are host-hidden.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. The causal-review and
resolution-critique subagents both completed; the closure-loophole wording was
fixed before commit.

## Verification

- `python3 scripts/validate_debug_artifact.py --repo-root . --report-all` passed.
- `python3 scripts/build_debug_seam_risk_index.py --repo-root . --write` refreshed the index.
- `python3 scripts/validate_integrations.py --repo-root .` passed.
