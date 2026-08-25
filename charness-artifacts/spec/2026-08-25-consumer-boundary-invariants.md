# Consumer Boundary Invariants — Structural Hardening Contract

Date: 2026-08-25
Status: implemented — adversarial hardening; second review completed; post-round2 repairs accepted-unreviewed

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
approval eligibility. The repaired slice also validates the duplicate overlay,
requires established scanner/fingerprint identity for lineage approval, retains
producer identity in the final report, and schedules the full declared runtime
dependency closure. The registry is a contract index, not a second runtime
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
- Duplicate lineage with missing or skewed scanner/fingerprint stamps is explicit
  non-approval, even when the family set is otherwise clean.
- A malformed duplicate review overlay is typed degraded input, never an empty
  reviewed set.
- The final reviewer report retains `producer_run_id` together with its output
  and receipt binding.
- Registry trigger paths cover the consumer's runtime helpers, schemas, and
  producer-owned output dependencies; changing one schedules the provenance
  checker and its independent self-test.
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
- Plugin gate: the exported layout passed mapped consumer-anchor validation as
  `proof_level: shape+consumer-anchors`; it explicitly does not claim the
  authoring-tree final-consumer pytest fixtures are packaged there.
- Focused consumer/registry/quality tests (`tests/test_provenance_contract.py`,
  `tests/quality_gates/test_dup_ratchet.py`, and
  `tests/quality_gates/test_reviewer_worker_report.py`,
  `tests/quality_gates/test_staged_commit_gate_plan.py`): 156 passed after the
  second-round repairs.
- The source provenance checker executed all four exact negative fixtures and
  returned `proof_level: executable-fixtures`; the packaged checker returned
  `proof_level: shape+consumer-anchors` with its fixture non-claim.
- The second bounded review is recorded in
  `charness-artifacts/critique/rounds/2026-08-25-2026-08-25-consumer-boundary-r2.md`;
  its delivery ledger bound packet identity
  `53760e09896c47393c4bf802963ca9b02217a5bc87ddc23ea587ee789b2af1f3`, reviewed
  input identity `a2351af508172d3147ca4193d002de3fb10428f4fecabcc636ce733550f7a406`,
  and findings identity
  `aadc2f11d58c556252bd2aeaa1a2138c2c153c61b026be25066349b66cb10eb3`.
- The canonical standing runner was re-executed at the current HEAD and its
  fresh count is recorded by the runner receipt, not copied into this prose.
  Source/plugin mirror drift, timing-layer completeness, shell syntax, and
  `git diff --check` remain required closeout checks. The pre-commit closeout
  is not claimed until the repaired verdict surface receives its second
  fresh-eye review.

## Boundary Ownership

The registry and gate are auditors. Reviewer delivery, lesson finalization,
capability selection, and duplicate ratchet remain the producers/consumers that
own their verdicts. The registry must not manufacture approval or readiness;
`required_fields` and `refusal_code` remain metadata obligations whose runtime
semantics are proven by consumer-owned fixtures, not by the registry alone.

## Critique

Required before locking implementation: fresh-eye code/spec critique of the
registry shape and its consumer hooks. A second verdict-surface round is owed
only if the implementation changes gate verdict logic. The second round found
four blockers, all repaired locally; repairs after that round remain
accepted-unreviewed under the existing cap. No same-agent review substitutes
for the delivered worker result.

## Canonical Artifact

`charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md`

## First Implementation Slice

Create the registry schema and validator, add the four rows and negative-fixture
references, then wire the existing final consumers to shared required-binding
and readiness helpers. Add focused contract-gate tests before broader quality
verification.
