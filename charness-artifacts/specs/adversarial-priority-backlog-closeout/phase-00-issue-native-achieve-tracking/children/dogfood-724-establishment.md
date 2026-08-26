# Child: Bootstrap, Then Prove #724 As The First Goal Run

Status: proposed executable spec
Proposed disposition: rewrite and reuse `corca-ai/charness#725` after approval
Target docs: [Goal lifecycle](../../../../../docs/goal-lifecycle.md)
Graph: [Proposed child graph](./index.md)
Readiness: [Existing Work Item readiness](../existing-work-item-readiness.md)

## Purpose

Use this goal itself as the first end-to-end case without a circular dependency:
preserve the premature #724 history, perform one explicitly bounded bootstrap
reconciliation after approval so GitHub can own progress, then use the completed
target capabilities to re-prove the exact graph and clean `/goal #724` pickup.

## Current State

Provider readback on 2026-08-26 found open parent `corca-ai/charness#724` with
29 real children: 26 original backlog issues plus provisional #725–#727; three
children were closed. Their bodies were created before the now-required two
critiques, to-be docs, alignment, briefing, and approval. No further mutation is
authorized during planning.

## Target State

- #724 remains the stable parent identity and records the premature bootstrap
  plus planning reset honestly.
- #725–#727 are rewritten to the approved specs or superseded if exact reuse is
  unsafe; two new system-capability issues are created for binding and consumer
  evidence lineage.
- All five system-capability children and all 26 original issue identities are
  real direct children exactly matching the approved manifest.
- Managed system-child bodies and 23 open backlog bodies/addenda match approved
  digests; three closed backlog issues bind observed identity and issue-owned
  behavioral closeout evidence without a managed-body claim.
- Immutable binding records the approved initial graph; separate provider
  observations prove establishment and current membership.
- A clean session invoking `/goal #724` validates the chain and selects an
  executable open child without relying on local prototype state.

## Authorization Boundary

Do nothing in this child until the operator explicitly approves the final
purpose/structure/execution/proof briefing. That approval authorizes only the
described graph reconciliation and subsequent child implementation; push,
release, tag, hosted CI mutation, and installed-host mutation remain separately
gated.

## Dependencies

- bootstrap phase: explicit briefing approval, frozen final Goal Draft, reviewed
  V1 data contract, and the minimum create/read/update/list/add/remove provider
  primitive slice implemented and locally proven under already-linked #726
- final proof/close: all four system capabilities are implemented and proven,
  V1 validator passes exact frozen bytes/parent/manifest, and the target issue
  backend preflight passes its complete live capability closure

## One-Time Bootstrap Boundary

The generic target lifecycle has no bootstrap mode. This existing #724 run is
the first instance and therefore cannot depend on its own not-yet-built pickup
and provider commands. After approval, the current planning session may first
implement only the minimum provider primitive slice under already-linked #726;
that pre-authority slice gets local/fake-backend proof and cannot claim live
Goal Run success. It then creates the binding data, reconciles approved bodies/
relationships through that adapter-resolved boundary, and captures exact
readbacks. The parent then owns routine progress, but its managed metadata says
`bootstrap_verification: pending-target-roundtrip`; clean `/goal #724` pickup,
target-provider success, and dogfood-child close remain blocked.

No other implementation child and no second session may infer target-runtime
readiness from that bootstrap marker. After the four capabilities are built,
the target commands re-read and reconcile the same identities, replace the
marker with the verified establishment observation, and exercise clean pickup.
This exception is not adapter policy, not reusable fallback, and not copied into
the evergreen lifecycle.

## Bootstrap Reconciliation Plan

1. Run read-only preflight and read #724 body, state, and all real children.
2. Freeze the complete approved Goal Draft. Re-read all 26 existing issues
   against the approved readiness contract and materialize exact desired body
   bytes for the 23 open issues plus evidence dispositions for closed #721,
   #694, and #628. Stop for reapproval on a materially changed premise.
3. Build exact desired graph entries for five system children plus 26 existing
   issues with managed-body digests, closed-evidence fingerprints, dependency
   order, and execution rank, then create the immutable V1 binding.
4. Re-read before every write.
5. Update #724 managed metadata and human briefing, recording premature
   bootstrap and planning reset.
6. Rewrite/reuse #725, #726, and #727 only when exact issue identity and intended
   capability match; otherwise mark the old child superseded and create the
   approved one without losing history.
7. Create the binding and evidence-lineage children, then link exact
   relationships.
8. Rewrite/read back the 23 approved managed cohort bodies/addenda. Preserve the
   three closed issue bodies and verify their exact closeout evidence. Add only
   missing relationships and remove only manifest-excluded provisional system
   children.
9. Read the entire parent/body/child/relationship graph back and compare exact
   identities/digests to the manifest.
10. Persist a typed bootstrap observation and parent marker; do not claim target
    provider establishment and do not rewrite the immutable Goal Binding.

At this point the exact GitHub graph is execution authority for the current
session and child state may carry routine progress. Target `/goal` activation
remains blocked.

## Final Target Roundtrip

After all four system capabilities are proven:

1. run target preflight and read #724 in a new process;
2. validate the frozen draft and immutable binding with the built validator;
3. reconcile/read every body, identity, relationship, and current graph
   amendment with the target issue commands;
4. persist the verified establishment observation and update/read back parent
   metadata without changing the binding; and
5. start a clean session and exercise `/goal #724` pickup.

Every interrupted or failed-readback outcome stops. Retry starts with full
readback, reuses verified identities, and mutates only the remaining delta.

## Acceptance Criteria

- Pre-mutation readback and exact approved manifest are retained as evidence.
- No provider mutation precedes explicit approval or complete capability
  preflight.
- #724 identity is reused; its timeline is not erased or replaced.
- Parent metadata exactly matches binding path, draft hash, graph hash, and
  planning reset.
- Graph equality is by exact repository/number/parent tuple and managed-body
  digest or closed-evidence disposition, not count.
- All 23 open existing issues satisfy the executable-body predicate and fresh
  premise check; all three closed issues expose exact behavioral evidence.
- No duplicate issue is created for a reuse entry.
- Interruption after every mutation boundary converges on clean retry.
- A partial/unverified result never produces a bound claim; bootstrap state is
  visibly weaker and cannot satisfy target pickup.
- `/goal #724` from a clean session reads provider state and selects a valid
  open child; local sidecar/file paths are not user input.
- `/goal #725` refuses because a child is not a Goal Run.
- Parent remains open after target establishment; this child does not close the
  26 backlog issues or the parent.

## Verification Commands And Live Evidence

For bootstrap, first implement and prove the minimum provider primitives named
above inside #726, then retain their exact preflight/read/create-or-update/
relationship commands and distinct post-mutation readbacks. Only approved
file-backed bodies may cross the boundary. If that slice cannot perform or
verify one required primitive, bootstrap stops; direct ad hoc REST calls and the
unapproved prototype's success claims are not substitutes.

For the final target roundtrip, first run the focused fake-backend/recovery and
binding suites from the prerequisite children. Then use these implemented
adapter-resolved commands with file-backed inputs:

```bash
python3 skills/public/issue/scripts/issue_tool.py goal-run-preflight --repo corca-ai/charness --plan-file <approved-plan.json>
python3 skills/public/issue/scripts/issue_tool.py goal-run-read --repo corca-ai/charness --number 724
python3 skills/public/issue/scripts/issue_tool.py goal-run-apply --repo corca-ai/charness --operation-file <one-operation.json>
python3 skills/public/issue/scripts/issue_tool.py goal-run-read --repo corca-ai/charness --number 724
```

The commands are target contracts and do not exist at the planning baseline;
absence blocks the final target roundtrip rather than licensing an ad hoc REST
call. Retain every structured started/result observation and run the final read
from a new process.

After the live roundtrip, run:

```bash
bash scripts/check-docs.sh
python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

and the targeted public-skill/issue-provider suites from the prerequisite
children. Any broad quality run follows changed-line proof and records skipped
checks explicitly.

## Adversarial Stimuli

- current graph has the expected count but one wrong child identity
- #725–#727 body changed since planning
- one of the 23 open cohort issues has a stale premise or incomplete body
- one closed cohort issue has CLOSED state but missing/mismatched closeout proof
- interruption after parent update, issue creation, or relation add/remove
- create succeeds and readback fails
- clean retry sees an already-created issue but missing relationship
- parent metadata draft hash differs by one byte
- stale local prototype reports success while provider graph differs
- clean `/goal #724` run has no knowledge of planning chat

## Documentation Impact

Record exact provider evidence in separate Goal Run observations, keep #724
managed metadata current without mutating the binding, and promote conditional
goal-lifecycle docs only if all prerequisite consumer behavior is proven. Do
not use parent-body progress narration for routine child closures.

## Closeout Evidence

This child closes only with exact live provider readback, clean-process retry
evidence, clean `/goal #724` pickup, and fresh-eye review of the reconciliation
receipt. Closing the child is not proof that any remaining backlog issue or the
parent is complete.

## Non-Goals And Non-Claims

- no implementation or closure of the 26 backlog Work Items
- no parent close
- no push, release, tag, remote CI, or installed-host mutation
- no concurrent-human edit protocol
- no inference of provider success from local fixtures
