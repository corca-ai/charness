# Closeout Bundle Slice 1 Critique

Date: 2026-08-06

## Decision Under Review

Lock the first executable slice of the opt-in closeout-bundle orchestrator:
safe local phase ordering, packet/input identity binding, source/plugin parity,
and explicit separation from pointer writes, behavior execution, and release.

## Failure Angles

- Problem framing and diagnosis: the orchestrator must own ordering and receipt
  evidence, while preflight, packet identity, authoring, pointer freshness, and
  verification remain with their existing owners.
- Operations and first use: planned commands must be rejected before any sync
  can run; dry-run, execute, receipt, and non-claim semantics must be legible.
- Structure and source of truth: the active goal, execution contract, CLI help,
  and generated plugin copy must describe the same capability.

## Counterweight Pass

- Act Before Ship items were repaired: durable packet identity is compared with
  the runner binding; all initially planned executable sync/lock commands are
  validated before the first runner call; help states `ready` and `completed`
  semantics; the inert `--json` flag was removed; and the goal now says pointer
  freshness validation rather than pointer refresh.
- Bundle Anyway: generated packet Markdown is left to artifact-shape ownership,
  with general doc authoring preflight applied to hand-authored Markdown.
- Over-Worry: adding generated headers to plugin copies or encoding provider and
  release policy into the generic orchestrator would add coupling without proof.
- Valid but Defer: consuming the generated packet through a separate fresh-eye
  claims review, full-log retention, and broader CLI-reference placement remain
  later closeout/documentation boundaries.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: [closeout_bundle_lib.py](../../scripts/closeout_bundle_lib.py#L156) | action: fix | note: runner-reported identity is now compared with the durable packet identity before verification lock
- F2 | bin: bundle-anyway | evidence: strong | ref: [closeout_bundle_lib.py](../../scripts/closeout_bundle_lib.py#L258) | action: fix | note: planned sync and lock commands are validated before any runner call
- F3 | bin: bundle-anyway | evidence: moderate | ref: [closeout_bundle.py](../../scripts/closeout_bundle.py#L16) | action: fix | note: help now explains ready/completed and local-only non-claims
- F4 | bin: bundle-anyway | evidence: strong | ref: [closeout_bundle.py](../../scripts/closeout_bundle.py#L39) | action: fix | note: misleading inert --json option was removed because output is always JSON
- F5 | bin: bundle-anyway | evidence: strong | ref: [closeout bundle goal](../goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md#L65) | action: fix | note: goal wording now names pointer-freshness validation and preserves pointer-owner authority
- F6 | bin: valid-but-defer | evidence: strong | ref: [execution contract](../spec/2026-08-06-closeout-bundle-execution-contract.md#L120) | action: defer | follow-up: deferred Slice 4 delegated claims-review boundary | note: packet generation is not silently promoted to fresh-eye approval
- F7 | bin: valid-but-defer | evidence: moderate | ref: [closeout_bundle_lib.py](../../scripts/closeout_bundle_lib.py#L67) | action: defer | follow-up: deferred operator-diagnostics slice | note: phase output truncation has no observed proof loss yet
- F8 | bin: valid-but-defer | evidence: moderate | ref: [execution contract](../spec/2026-08-06-closeout-bundle-execution-contract.md#L99) | action: defer | follow-up: deferred CLI-reference owner | note: broader generated CLI-reference placement is not needed for this opt-in slice

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden; the host returned reviewer findings but did not expose applied model metadata
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; three bounded angle reviewers and one separate counterweight
reviewer returned findings, and each shared-worktree boundary verified clean.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.json
- Packet path: charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.json
- Packet SHA256: e180301ea9ebf39ddd2db5b222ea339484d44aa229cc67fc71f9d321cc2c3cdb
- Identity SHA256: 7e5d7cff20a1987437c3e7485d9231cae7fc138f87fd3e297556cee45d7ef345

## Boundary Ownership

- Producer: `prepare_packet.py` produces the packet and its reviewed-input binding.
- Consumer: the closeout-bundle receipt and later verification/claims readers consume the bound evidence.
- Owning surface: [closeout_bundle_lib.py](../../scripts/closeout_bundle_lib.py) owns orchestration-level ordering and receipt binding, while packet generation and identity reconstruction remain delegated owners.
- Verdict: owned-correctly
