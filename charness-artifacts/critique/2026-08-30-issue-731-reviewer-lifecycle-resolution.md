# Issue #731 Reviewer Lifecycle Resolution

Date: 2026-08-30
Classification: resolution verification
Fresh-eye satisfaction: parent-delegated — a distinct Luna reviewer inspected the final integrated lifecycle after the #751 and #756 changes, verified the structural length repair, and ran the bounded lifecycle/backend/semantic discriminator set read-only.
Verdict: PASS for typed partial-progress preservation without approval widening.

## Decision Under Review

Close the frozen #731 Work Item if accepted, running, partial, timed-out,
interrupted, and terminal states are durable; partial bytes remain useful and
identity-bound but never approval-eligible; process cleanup and terminal
identity/schema requirements remain intact.

## Verification Scope

- Lifecycle implementation commit: `e7d5fa707`.
- Integrated structural repair: `8c144f2c7`, which moved worker invocation and
  partial-log projection to named owners after the combined branch exposed a
  373/360 tokei hard failure.
- Parent final focused set: 93 lifecycle, delivery, worker/backend, runner, and
  semantic-command tests passed in 16.23s.
- Independent Luna final review reran the same bounded 93-test surface and
  returned SHIP.
- Ruff, plugin materialization, and the official tokei gate passed with no
  changed-file length warning after the structural repair.

## Failure Angles

- Partial-as-approval: non-empty bytes or a zero process exit could be mistaken
  for a verdict. Approval remains limited to terminal `findings-received`, pass,
  and matching packet/input provenance.
- Lost progress: timeout or interruption could discard useful backend output.
  Failed output is preserved with size and SHA-256, then validated against its
  producer binding before lifecycle projection.
- Orphan process: parent interruption must terminate backend descendants. The
  existing process-group interruption and timeout controls remain green.
- State collapse: accepted, running, partial, timed-out, and interrupted could
  collapse into one generic failure. Typed lifecycle and history fixtures pin
  each transition and reject invalid partial history.
- Delivered block ambiguity: a block is terminal reviewer output, but never
  approval. The pass/block semantic command fixture keeps that distinction.
- Integration regression: #751 semantic bytes and #756 backend ownership could
  be lost in the automatic cherry-pick merge. Their committed-ref/deletion and
  backend-owner discriminators pass on final HEAD.
- Length-gate evasion: deleting comments or spilling helpers into an arbitrary
  `_lib` would hide the ownership problem. Worker argv binding now has the named
  `run_review_invocation.py` owner, and partial-log descriptors live with the
  typed partial-output owner.
- Scope expansion: no new backend, dashboard, credentialed transport, consumer
  Git/submodule/worktree topology policy, or success inference was added.

## Counterweight

Partial output is diagnostic evidence, not a second result protocol. The
implementation therefore preserves bytes and identity without inventing a
partial verdict. The named extraction is warranted by two real consumers and a
hard integration limit, while broader cadence or UI work would exceed the
frozen #731 Work Item.

## Findings

The integrated branch initially failed the official length gate. That blocker
was repaired structurally before publication. No blocking or material advisory
finding remains in the final #731 claim.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye.
- Requested spawn fields: Luna model lane under the operator's all-Luna rule.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden
- Delivery state: findings-received
- Execution mode: typed-subagent

## Boundary Ownership

- Producer: worker process, receipt, and typed partial-output descriptors.
- Consumer: delivery ledger and lifecycle approval projection.
- Owning surfaces: `reviewer_worker_runtime.py`,
  `reviewer_partial_output.py`, `reviewer_worker_report.py`, and
  `reviewer_lifecycle.py`; process argv is owned by
  `run_review_invocation.py`.
- Verdict: owned-correctly

AI-provenance: Agent-authored resolution critique from integrated source,
focused tests, official tokei evidence, and an independent Luna fresh-eye. No
provider state, remote CI, release, real backend transport, or consumer topology
claim is made.
