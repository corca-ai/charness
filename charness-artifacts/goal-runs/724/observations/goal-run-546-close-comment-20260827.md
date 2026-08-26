## Resolution — Charness-owned runtime-budget contract

JTBD: make runtime-budget intent explicit and validate the label membership
universe without pretending to own consumer scheduler execution.

Boundary: Charness owns adapter declaration and membership reconciliation;
scheduler, hosted/installed enforcement, and consumer repository runners remain
outside this issue.

Resolution brief: complete the local contract and hand the remaining behavior
to a successor rather than keeping this issue open for unrelated owners.

Issue #546 is complete at the boundary this repository owns. The adapter now
declares runtime-budget intent for the complete budget universe, the validator
reconciles the declaration with the consumer-visible membership seam, and
conditional intent remains explicit rather than being inferred as execution.

Implementation: `459e3c084bcfd7d49ee6c3acf80c9b10e33e1ee7` added the
adapter-owned consumer-universe seam and its source/plugin export parity.

Prevention: keep conditional execution as `execution_proven: false`, require
explicit adapter-owned membership declarations, and send scheduler/host/consumer
enforcement requests to a separate successor owner.

## Behavior verdict

- Focused consumer/adapter/runtime regressions: `87 passed`.
- Exact runtime-budget target: `35 passed`.
- Adapter validation: `16/16` resolvers and YAML files with no unreconciled
  keys.
- Isolated changed-line proof for the consumer-universe implementation:
  `status: clean`, `consumer_returncode: 0`, `blocking: []`, and no unmapped
  changed files; all seven mapped source files were analyzed and covered.
- Source/plugin parity and the implementation pre-commit checks passed.

Behavior #546: local-only-by-contract — the distinct adapter/universe test and
isolated proof channels confirm the Charness-owned membership contract; they do
not confirm conditional execution.

## Resolution critique

The remaining scheduler, hosted-enforcement, installed-host, and consumer
repository work is a different ownership boundary. Keeping this issue open to
represent those unimplemented surfaces would conflate a verified Charness
contract with behavior this repository cannot observe or enforce. Those items
are intentionally successor work, not hidden acceptance criteria for this
issue.

## Explicit non-claims

This resolution does not claim scheduler changes, conditional trigger execution
or budget firing, hosted or installed-host enforcement, consumer-repository
runner adoption/schema, remote CI, push, release, tag, or fresh-eye review.
Forced handoff and micro-slice rituals were omitted by operator direction.

Implementation carrier: `459e3c084bcfd7d49ee6c3acf80c9b10e33e1ee7`.
The issue body was updated through the #724 Goal Run provider and read back as
`body_verified: true` before this close operation.

AI-provenance: authored by an agent session.

Manual fallback reason: operator-directed-manual-close.

Critique: blocked operator-directed implementation path omits forced fresh-eye
review; the bounded local contract evidence and explicit successor boundary are
the intended closeout scope.
