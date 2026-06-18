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
the proof's recorded source baseline. Staleness is a candidate signal, not
automatic proof debt.
Tooling may surface the entry as `stale_candidate` or `needs_adjudication`; the
agent then decides whether the candidate is actual proof debt before requiring
live re-proof.

Use one of these adjudications:

| Adjudication | Meaning |
| --- | --- |
| `reproof_required` | the change can affect the proven behavior, so the entry needs new proof before it anchors live decisions |
| `covered_by_tests` | deterministic tests now cover the behavior within the acceptance class; record the command or artifact |
| `covered_by_newer_proof` | a later proof artifact covers the same acceptance surface |
| `narrow_surface` | the original refs were too broad; narrow them with evidence that the changed path cannot affect the proof |
| `ledger_outdated` | the ledger points at obsolete refs or baseline data; correct the ledger rather than re-proving behavior |
| `accepted_risk` | the operator accepts the stale candidate with owner, reason, decided-at, and revisit trigger |
| `deferred` | the candidate is explicitly postponed with owner, reason, decided-at, and revisit trigger |

Pre-live and completion audits block unresolved adjudication, not every stale
candidate. A stale `verified` entry must not anchor new live decisions until the
adjudication is recorded, and closeout language must not claim a re-proof plan
as a proof result.

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
entry is neither `verified` nor explicitly dispositioned, or while stale-candidate
adjudication is unresolved. When the adapter declares a completion-audit command,
run it and record the result; without one, perform the audit manually against the
ledger and record that it was manual.

Deployment readback and a closed tracker state are not this audit. They prove the
bundle deployed and the tracker closed, not that a connector/provider behavior
was observed; a `verified` entry must cite the behavior channel that observed it,
not the bundle readback or `CLOSED` state it rode in on. An entry confirmed only
by re-reading that same proxy is not `verified` — that is the re-examination
failure that *P4* of the authoring-repo-internal `docs/design-north-star.md`
names. When this audit runs inside an
`achieve` issue-bundle closeout, the distinct fresh-eye disposition reviewer owns
the per-issue confirmation (achieve `lifecycle.md`, *Disposition Gate - Two
Rungs*).

## Ledger tooling ownership

In this version the skill ships the status vocabulary, field semantics, and
audit discipline; the machine-readable schema, ledger file location, and any
check/readiness/re-proof commands are adapter-owned. A consuming repo that
already maintains ledger tooling declares it in the adapter; a repo without
tooling keeps the ledger as a reviewed durable artifact under the adapter's
`output_dir`.
