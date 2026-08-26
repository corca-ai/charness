# Child: Provide Exact Goal Run Graph Operations And Guarded Close

Status: proposed executable spec
Proposed disposition: rewrite and reuse `corca-ai/charness#726` after approval
Target docs: [Goal lifecycle](../../../../../docs/goal-lifecycle.md)

## Purpose

Make the existing adapter-resolved `issue` backend the sole provider boundary
for Goal Run parent updates, real sub-issue relationships, exact readback,
resumable reconciliation, and irreversible guarded close.

## Current State

At `HEAD`, `issue` already owns binary/auth readiness, repository-qualified
identity, safe file-backed issue bodies, create/read, generic close, and
post-create verification. It lacks parent-body update and real sub-issue
list/add/remove operations. The unapproved prototype is candidate evidence but
has known readiness, identity-binding, partial-result, and close-ingress gaps.

## Target State

One issue-backend contract exposes exact operations for Goal Runs and returns a
typed Provider Observation for every preflight, mutation, and readback. `achieve`
orchestrates these operations but contains no direct `gh` or GitHub REST logic.

## Owning Surfaces

- `skills/public/issue/scripts/issue_backend.py`, `issue_tool.py`, and a focused
  tracker/Goal Run module if separation improves ownership
- issue adapter example/resolver and `references/issue-backend.md`
- canonical `skills/public/issue/` plus synchronized plugin placement
- fake-backend tests and authorized live dogfood consumer

## Inputs And Dependencies

- exact repository identity for every operation
- parent and child issue numbers, never unqualified global ids
- file-backed desired parent/managed-child bodies
- approved graph entries and binding identity supplied by `achieve`
- backend-declared capability commands for update/list/add/remove/state/close

Provider primitives can be implemented independently. Integration validation
consumes the V1 binding contract but must not parse the Goal Draft itself.

## Required Operations

1. `goal-run-preflight`: adapter validity, binary, auth, exact repository, and
   the complete primitive closure for the requested plan—create, read/body,
   state, update, resolve-id/discover, list, add, remove, comment, and close
2. `read-body` and `update-body`: exact issue identity, file input, byte readback
3. `list-children`: normalized exact child repo/number/URL/parent/state payload
4. `add-child` and `remove-child`: idempotent relationship mutation plus readback
5. `create-or-reuse-child`: exact reuse policy and managed-body verification
6. `read-state`: parent/child provider state without Markdown inference
7. `record-observation`: persist one immutable versioned provider-attempt receipt
8. `close-goal-run`: dedicated guarded close that generic close cannot bypass

`achieve` owns the reconciliation plan, entry order, graph amendments, and
deferral policy. `issue` applies one exact primitive at a time and returns its
typed observation; it does not become a second goal orchestrator.

Alternate backends either provide every requested operation or return typed
`capability-missing` before mutation. No second provider client is selected
implicitly.

## Provider Observation Contract

Each `charness.goal-run-observation/v1` result includes operation/attempt id,
binding/draft/parent identity, Work Item key, exact target, pre-state,
submitted body digest, returned provider/database identity, readback, backend,
outcome, unresolved targets, next action, and receipt SHA-256. Outcome is one of:

- `started`
- `no-write`
- `verified-write`
- `unverified-write`
- `partial-graph`
- `verified-read`
- `refused`

Persist `started` before provider invocation. `no-write` is valid only when no
provider mutation was invoked. A zero exit code without required readback cannot
yield `verified-write`. Successful identities from a partial graph are retained;
a clean retry re-reads every item and mutates only the remaining delta.

Create-or-reuse uses a stable Work Item key in managed body metadata and exact
read-only discovery. An invoked create with no discoverable identity stops for
operator disposition and cannot be retried as another create.

The target command surface implemented by this child is file-input based:

```text
issue_tool.py goal-run-preflight --repo <owner/repo> --plan-file <json>
issue_tool.py goal-run-read --repo <owner/repo> --number <n>
issue_tool.py goal-run-apply --repo <owner/repo> --operation-file <json>
issue_tool.py goal-run-close --repo <owner/repo> --number <n> --proof-file <json>
```

Each command emits one structured result unconditionally. `goal-run-apply`
accepts one planned provider primitive, not an entire policy graph.

## Guarded Parent Close

Every generic update or close/comment-close reads and parses the target before
any mutation. Generic update refuses metadata stripping; generic close returns
`goal-run-close-required` before comment/write. The dedicated operation performs
exact pre-close parent/child readback, requires each child's issue-owned
closeout evidence or verified successor deferral, requires whole-system proof,
persists a terminal started attempt, closes, and performs distinct post-close
state readback.

It distinguishes comment-written/close-failed,
close-invoked/readback-unknown, and closed/readback-failed. Retry reads first,
never re-closes an already-closed parent, and binds terminal evidence only after
exact verification.

No `--force`, unchecked generic backend command, or missing-capability fallback
may bypass this ingress guard.

## Acceptance Criteria

- Preflight names every missing capability before the first provider mutation.
- Every operation is repository-qualified and rejects parent/child identity
  mismatches.
- Parent body update verifies exact bytes, not only command success.
- Child list normalizes exact relationship and parent identity.
- Add/remove are idempotent and re-read before mutation.
- Interruption after each mutation produces a typed partial/unverified result;
  clean retry converges without duplicate issues or relationships.
- An ambiguous create cannot invoke create again until exact read-only discovery
  or operator disposition resolves it.
- Relation count with wrong identities fails reconciliation.
- Generic close refuses a Goal Run.
- Generic body update cannot strip the managed block.
- Guarded close refuses open children and detached/unverified deferrals.
- Guarded close refuses a CLOSED child whose issue-owned behavioral closeout
  evidence cannot be verified.
- Failed post-close readback never reports completion.

## Verification Commands

Create or reshape the focused test module, then run:

```bash
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_issue_tracker.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_issue_skill.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_issue_goal_run_close.py
python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

Run the repo-selected changed-line proof before broad quality. The live #724
roundtrip belongs to the dogfood child and runs only after approval.

## Adversarial Stimuli

- binary present but auth absent
- backend declares update but omits relationship removal
- same issue number in a different repository
- successful mutation command followed by failed/mismatched readback
- interruption after parent update and after each child relation
- wrong children with the correct total count
- open child hidden by a stale list response
- generic close against a body carrying Goal Run metadata
- provider close succeeds but post-close readback fails

## Documentation Impact

Update issue backend reference and generated CLI reference for implemented
commands. `docs/goal-lifecycle.md` remains conditional until integrated
consumer and dogfood proof.

## Closeout Evidence

Focused fake-backend observations, mutation-stimulus receipts, source/export
sync, changed-line proof, and two-round bounded review if the implementation
changes verdict logic. No live provider success is claimed here.

## Non-Goals And Non-Claims

- no concurrency or optimistic-lock protocol
- no transaction coordinator or event store
- no lifecycle policy inside `issue`
- no implicit GitHub-only logic in `achieve`
- no live GitHub claim from fake-backend tests
