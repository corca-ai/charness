# Child: Freeze A Full Goal Draft And Validate Goal Binding V1

Status: proposed executable spec
Proposed disposition: create a new sub-issue after briefing approval
Target docs: [Goal lifecycle](../../../../../docs/goal-lifecycle.md)

## Purpose

Give Charness one coherent planning model: a rich Goal Draft that may change
until approval, then freezes completely, plus a narrow machine-readable binding
that proves which draft, parent, and approved child graph belong together.

## Current State

At `HEAD`, `goal_artifact_lib.py` models one mutable Markdown artifact as draft,
active/blocked state, slice log, closeout record, and `/goal @file` identity.
`handoff` has a second copied producer. The unapproved prototype adds a minimal
receipt, but that receipt is explicitly superseded.

## Target State

- One canonical Goal Draft producer/schema is shared by `achieve` and `handoff`.
- The complete draft is mutable only before approval; the approval record is
  added, then the entire file byte sequence is SHA-256 bound and immutable.
- The deterministic sibling `.binding.json` implements
  `charness.goal-binding/v1` exactly as documented.
- The complete binding is immutable and contains approval, parent, frozen draft,
  and exact initial work-item manifest identity, never observations or mutable
  execution state.
- Validation returns typed, actionable refusal codes and does not consult
  GitHub when local integrity already fails.

## Owning Surfaces

- canonical: `skills/public/achieve/scripts/`, achieve references, adapter schema
- producer consumer: `skills/public/handoff/scripts/draft_goal_from_chunk.py`
- generated: matching `plugins/charness/` placements through the repo sync
- tests: new binding/draft tests plus existing goal-producer and handoff fixtures

Candidate implementation modules may replace the prototype receipt modules,
but there must be one obvious owner for draft creation and one for binding
parse/validate/freeze. Do not retain both receipt and binding concepts.

## Inputs And Dependencies

- approved Goal Draft path and exact bytes
- explicit approval record tied to the final briefing
- exact Goal Run repository/number/URL
- key-sorted approved work-item records, including create/reuse and body policy
- final briefing/approval identity

No provider capability is required to unit-test or close the schema/validator
portion of this child. Provider integration is owned by the provider child.

## Implementation Contract

1. Define one versioned JSON schema and canonical JSON serialization for the
   approved work-item digest.
2. Validate repository-relative paths against escape, symlink escape, absence,
   wrong suffix, and wrong draft/binding pairing.
3. Hash the complete frozen draft bytes, not selected semantic sections.
4. Require exact parent identity coherence and exact approved-graph digest.
5. Hash the complete canonical binding bytes and require parent metadata to bind
   that hash; reject edited-and-rehashed core substitution against the approved
   parent/draft identities.
6. Reject unknown versions and extra state-like/observation fields such as
   `status`, `progress`, `current_child`, `establishment`, `terminal`, or copied
   parent bodies.
7. Make post-freeze draft mutation fail until a new explicit approval produces
   a newly bound hash; never auto-rebind.
8. Make `handoff` call the canonical draft producer/schema and remove its copied
   lifecycle template.
9. Keep current receipt helpers until the orchestration/evidence consumers cut
   over atomically; this child must not delete a still-consumed runtime path.
10. A provider-less planning fallback emits no binding; add a typed refusal/test
    for any attempt to bind without exact parent readback.

## Typed Results

Positive result includes schema version, binding hash, approval identity, draft
path/hash, parent identity, and approved-graph hash. Negative results must
distinguish at least: `schema-unknown`, `path-invalid`, `draft-missing`,
`draft-hash-mismatch`, `parent-mismatch`, `graph-digest-mismatch`,
`binding-hash-mismatch`, `state-field-forbidden`, `approval-missing`,
`parent-unverified`, and `draft-frozen`.

## Acceptance Criteria

- Two identical semantic inputs serialize to identical manifest bytes and hash.
- Any single-byte draft change fails validation and cannot be auto-approved.
- Parent repo, number, or URL mismatch fails independently.
- Reordering input work items does not change canonical output; changing any
  key, identity, dependency, body policy, or managed-body digest does.
- Binding fixtures containing execution-state fields are rejected.
- Observation fields and provider-less parent placeholders are rejected.
- Rewriting the binding core and matching only its internal hashes fails against
  the approval/parent binding hash.
- Handoff and achieve create the same valid Goal Draft shape through one owner.
- A clean process can validate a frozen draft/binding pair without importing
  prototype-only state.

## Verification Commands

The implementation child creates focused tests with stable names, then runs:

```bash
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_binding_v1.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_artifact_producers.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/test_handoff_chunker_auto_draft.py
bash scripts/check-docs.sh
```

After canonical edits, synchronize generated placements with:

```bash
python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

Then verify source/export parity through the repo-owned quality checks selected
for the changed surface.

## Adversarial Stimuli

- mutate one draft byte after approval
- replace the binding with one from another draft
- substitute a different repository or parent number
- reorder and then alter one manifest entry
- inject active/progress/provider-state fields
- use `../`, absolute, missing, and symlink-escape paths
- invoke handoff production after deleting its historical copied template

## Documentation Impact

Keep `docs/goal-lifecycle.md` conditional until the whole system is built.
Update Goal Draft/binding and handoff-producer documentation owned by this
capability. Keep `docs/goal-lifecycle.md` conditional and avoid claiming the
provider-backed runtime until integrated dogfood proves it.

## Closeout Evidence

The child closes on focused deterministic receipts, source/export sync, and a
fresh-eye review of the schema/refusal surface. It does not require or claim a
live GitHub mutation.

## Non-Goals And Non-Claims

- no execution progress storage
- no legacy artifact migration or reader
- no host `/goal` runtime modification
- no provider graph success claim from local schema tests
