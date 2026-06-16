# Ledger And Dispositions

The ledger is the durable answer to "what applied behavior is proven, and what
is everything else waiting on". The statuses and field semantics below are
portable; the machine-readable ledger schema, its path, and any audit commands
are adapter-owned (see `adapter-contract.md`).

## Statuses

Every loop entry ends in exactly one status:

| Status | Meaning |
| --- | --- |
| `verified` | the success criteria were observed via the proof packet's method; evidence is linked |
| `blocked-needs-operator` | proof needs a human action (approval, UI judgment, manual ingress) that has not happened |
| `blocked-needs-capability` | proof needs a repo-owned command or surface that does not exist or is not adapter-declared |
| `deferred-by-operator` | an operator explicitly chose to postpone proof; the entry stays open with a revisit trigger |
| `issue` | the loop surfaced a defect or gap now tracked as its own issue; the entry links the tracker ref |
| `accepted-risk` | the operator accepts the unproven behavior with a recorded reason |
| `out-of-scope` | the entry does not belong to this loop's acceptance surface; the reason says why |

A status is a recorded decision, not a mood: "probably fine" is not a status.

## Verified entries

`verified` requires:

- `verified_at`: when the proof was observed
- `verified_against.source_commit`: the repo state the proof covered
- `verified_against.proof_artifact`: the durable evidence (readback output,
  screenshot ref, recorded action packet result)
- `verified_against.proving_surface_refs`: the repo-owned behavior or verifier
  files whose change would make this proof stale
- provider refs when the surface exposes them (message ids, run ids, row refs)

## Staleness

A `verified` entry is stale when any `proving_surface_refs` entry changed after
`verified_at`. Staleness is proof debt, not noise:

- re-prove against the new state, or
- narrow the proving-surface refs when the change provably cannot affect the
  proof, or
- replace `verified` with an explicit disposition

Pre-live and completion audits must treat unresolved staleness warnings as
blocking: a stale `verified` must not anchor new live decisions.

## Non-verified dispositions

Every final non-verified status carries:

- `disposition.owner`: who decided
- `disposition.reason`: why this is acceptable or blocked
- `disposition.decided_at`: when
- `disposition.revisit_trigger`: the event or date that reopens the entry

When a non-verified status depends on an operator-only decision, confirmation,
credential action, manual proof step, or external-boundary approval, carry the
same information into the active goal's `## Operator Decision Queue` when one
exists:

- `Decision`: the exact operator-only decision or confirmation needed
- `Owner`: the operator or named human owner
- `Why deferred`: why the HOTL run did not stop immediately
- `Unblock action`: the exact action or answer needed
- `Revisit trigger`: the event, date, or proof boundary that reopens the item

Use `blocked-needs-operator` when proof cannot proceed without that action. Use
`deferred-by-operator` when the operator explicitly postpones proof. Safe local
work may continue while the item is deferred; stop only when it blocks every
safe next proof or implementation step.

## Completion audits

Before closing a goal, feature, or issue whose acceptance includes applied live
behavior, audit the linked ledger entries: completion is blocked while any
entry is neither `verified` nor explicitly dispositioned. When the adapter
declares a completion-audit command, run it and record the result; without one,
perform the audit manually against the ledger and record that it was manual.

## Ledger tooling ownership

In this version the skill ships the status vocabulary, field semantics, and
audit discipline; the machine-readable schema, ledger file location, and any
check/readiness/re-proof commands are adapter-owned. A consuming repo that
already maintains ledger tooling declares it in the adapter; a repo without
tooling keeps the ledger as a reviewed durable artifact under the adapter's
`output_dir`.
