# Consumer Boundary Invariants — Structural Hardening Contract

Date: 2026-08-25
Status: implemented — verification complete

## Problem

The #715–#721 defects were repaired locally, but the second review showed a
repeatable class: producer identity, lifecycle ownership, malformed-input
refusal, and readiness limitations were not represented as one executable
producer-to-final-consumer contract. A future contributor can satisfy a helper
test while omitting the final-consumer obligation.

## Capability Contract

An operator must be able to trust that a boundary cannot claim approval,
readiness, or successful collection unless its producer identity and required
evidence have reached the final consumer. Missing evidence must produce a typed,
observable refusal for every terminal outcome.

## Current Slice

Add a small typed boundary-invariant registry and deterministic quality gate.
Bind the four reviewed boundaries to it: reviewer delivery joins, lesson
all-outcome fencing, candidate-manifest refusal, and duplicate-lineage
approval eligibility. The registry is a contract index, not a second runtime
state model; existing producers and approval owners remain authoritative.

## Fixed Decisions

- The final consumer remains the owner of approval/readiness.
- A failed, timed-out, interrupted, or missing worker outcome still runs the
  parent-state write-fence before collection is classified.
- `output_file`, `receipt_file`, and `producer_run_id` are mandatory for a
  file-backed reviewer approval path.
- Malformed candidate manifests refuse selection; they are never silently
  skipped in favor of a valid sibling.
- Duplicate lineage without stable baseline paths is explicit non-approval, not
  an automatic rebind.
- The registry must be source-controlled, schema-validated, and covered by
  negative fixtures; prose-only rows do not count.
- Source and packaged/plugin copies remain byte-identical where required.

## Probe Questions

- Can one compact registry describe required joins and refusal/readiness policy
  without duplicating each consumer's domain-specific verdict text?
- Which contract rows can be checked structurally, and which need one runtime
  fixture through the final consumer?
- Can the gate report the producer, consumer, missing obligation, and recovery
  without becoming a second approval owner?

## Deferred Decisions

- Host-attested freshness windows and live Ceal/Claude/provider proof.
- Automatic semantic duplicate-family rebind.
- A repo-wide migration of every historical diagnostic that is not on a
  current approval/readiness path.

## Non-Goals

- Reopening or closing GitHub issues.
- Replacing the existing delivery ledger, lesson ledger, or packet format.
- Turning every advisory into a blocking gate without a named consumer owner.

## Deliberately Not Doing

- No generic message formatter: refusal vocabulary stays with each owner.
- No third fresh-eye round for the already-reviewed verdict surfaces; the
  operating contract caps the rounds at two, so this contract adds executable
  prevention and records any post-cap repair as non-approval.

## Constraints

- Keep the registry portable in source and exported plugin layouts.
- The gate must fail closed on missing/duplicate rows, unknown boundary names,
  or a row that lacks a negative fixture reference.
- Verification must include the final consumer, not only the producer helper.

## Success Criteria

1. The registry validates with unique boundary IDs and complete producer,
   consumer, required-obligation, refusal-policy, and negative-fixture fields.
2. Removing a required reviewer producer join or changing a terminal outcome to
   skip the lesson fence makes the contract gate fail.
3. Invalid candidate manifests and unavailable duplicate lineage are represented
   as typed non-approval in the consumer output.
4. One changed/new negative fixture reaches each final consumer.
5. Source/plugin parity, focused tests, duplicate ratchet, and pre-commit pass.

## Acceptance Checks

- `unit`: registry schema and missing-obligation checks.
- `integration`: final-consumer fixtures for reviewer delivery, lesson
  finalization, capability selection, and duplicate ratchet.
- `specdown`: deterministic gate output naming each missing obligation.
- `verification`: source/plugin mirror check and `bash .githooks/pre-commit` (passed).

### Executed Evidence

- Source gate: `check_provenance_contract.py` ran all four exact negative
  fixtures as executable pytest nodes.
- Plugin gate: the exported layout passed schema/anchor validation as
  `proof_level: shape-only`; it explicitly does not claim the authoring-tree
  final-consumer pytest fixtures are packaged there.
- Focused consumer/registry/quality tests: 222 passed in the latest slice run.
- Source/plugin mirror drift, timing-layer completeness, shell syntax, full
  standing pytest (11,409 passed), and `git diff --check` passed. The pre-commit
  closeout completed with no blocking findings.

## Boundary Ownership

The registry and gate are auditors. Reviewer delivery, lesson finalization,
capability selection, and duplicate ratchet remain the producers/consumers that
own their verdicts. The registry must not manufacture approval or readiness.

## Critique

Required before locking implementation: fresh-eye code/spec critique of the
registry shape and its consumer hooks. A second verdict-surface round is owed
only if the implementation changes gate verdict logic; round-2 repairs remain
accepted-unreviewed under the existing cap.

## Canonical Artifact

`charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md`

## First Implementation Slice

Create the registry schema and validator, add the four rows and negative-fixture
references, then wire the existing final consumers to shared required-binding
and readiness helpers. Add focused contract-gate tests before broader quality
verification.
