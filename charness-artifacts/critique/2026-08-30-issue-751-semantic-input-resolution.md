# Issue #751 Semantic Input Resolution Critique

Date: 2026-08-30
Classification: resolution verification
Fresh-eye satisfaction: parent-delegated — an independent Luna reviewer first blocked the path-only implementation on the tools-disabled Claude backend; after remediation, a distinct Luna pass verified the integrated commit and ran the bounded discriminator tests.
Verdict: PASS for backend-independent, identity-checked semantic input.

## Decision Under Review

Close #751 only if every declared reviewed path contributes actual bound bytes
to the worker prompt, rather than merely a path name or unrelated packet
section, and invalid semantic input refuses before reviewer launch.

## Verification Scope

- Initial implementation commits: `943278d75` and `5126a6e32`.
- Fresh-eye blocker: `claude_p` runs with filesystem tools disabled, so a prompt
  that only instructed the worker to open paths did not carry their bytes.
  Committed-ref reviews could also read a later workspace path instead of the
  bound target.
- Remediation commit: `1a0a00e79` re-reads and identity-checks working-tree,
  committed-ref, and deleted-preimage bytes, materializes read-only carriers,
  and embeds the bounded payload in the prompt for every backend.
- Integrated focused suite: 99 passed in 19.34s. Final fresh-eye discriminator
  slice: 10 passed, 7 deselected.

## Failure Angles

- Backend reachability: Claude's tools-disabled process receives only stdin.
  The prompt now contains `prompt_content`; the worker no longer depends on
  opening a repository path.
- Ref drift: a committed packet must not read later working-tree bytes. The
  committed-ref fixture changes the workspace after the target commit and
  proves that `base_head:path` supplies the carrier.
- Deletion identity: a missing current path must not erase what was removed.
  Commit, range, working-tree, mismatch, unavailable, and oversize pre-image
  controls remain explicit.
- Empty ceremony: a packet section or path count must not substitute for
  reviewed bytes. Zero reviewed paths and exact-set mismatch refuse before
  launch.
- Silent truncation: the combined semantic payload is bounded; excess bytes
  produce a typed refusal rather than a partial review.
- Approval widening: the change occurs before backend launch and does not alter
  lifecycle/report eligibility. The existing delivered pass/block control still
  keeps block ineligible.
- Scope expansion: the implementation retrieves bytes from Charness's existing
  identity substrate only. It adds no consumer Git, submodule, worktree, or
  topology policy.

## Counterweight

The first fresh-eye block was material, not speculative: one supported backend
could not execute the instruction that was supposed to make content reachable.
After direct byte carriage, adding backend-specific filesystem tools would be a
weaker and more complex remedy. The shared bounded payload is the smallest
backend-independent contract and keeps unavailable or oversized input
fail-closed.

## Findings

The initial path-only implementation was blocked and remediated before
publication. No blocking or material advisory finding remains in the final
integrated #751 claim.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye.
- Requested spawn fields: Luna model lane under the operator's all-Luna
  delegation rule.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden
  No separate runtime record proves the
  effective model parameter.
- Delivery state: findings-received
- Execution mode: typed-subagent

## Boundary Ownership

- Producer: reviewed-input identity and semantic-input materializer.
- Consumer: file-backed critique worker prompt shared by `codex_exec` and
  `claude_p`.
- Owning surfaces: `skills/public/critique/scripts/semantic_review_input.py`
  and `skills/public/critique/scripts/run_review_packet.py`.
- Verdict: owned-correctly.

AI-provenance: Agent-authored resolution critique from integrated source,
focused tests, one blocking fresh-eye review, and one independent post-remedy
Luna SHIP review. No provider state, remote CI, release, or consumer topology
claim is made.
