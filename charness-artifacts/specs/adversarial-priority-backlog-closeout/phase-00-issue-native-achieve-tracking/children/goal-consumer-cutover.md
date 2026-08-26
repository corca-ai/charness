# Child: Bind Goal Evidence Consumers To One Run Identity

Status: proposed executable spec
Proposed disposition: create a new sub-issue after briefing approval
Target docs: [Goal lifecycle](../../../../../docs/goal-lifecycle.md)
Inventory: [Consumer cutover map](../consumer-cutover.md)

## Purpose

Make every durable proof about goal execution name the same frozen Goal Draft,
Goal Binding, parent Goal Run, and selected Work Item. This child owns evidence
lineage, not the entire lifecycle migration.

## Current State

Premise records, slice manifests, critique/retro records, closeouts, host
metrics, and release evidence commonly retain only `goal_path` or infer active
execution from local goal status. Those fields preserve useful planning
provenance, but cannot by themselves prove which provider-backed run or child an
observation belongs to.

## Target State

- Goal Draft path/hash is immutable planning provenance.
- Binding hash plus exact parent repository/number is Goal Run identity.
- Exact child repository/number and manifest key is Work Item identity.
- Every execution-evidence producer either emits that full lineage or records
  an explicit `planning-only`/`not-goal-bound` disposition.
- Cross-run, cross-child, stale-binding, and path-only execution claims refuse.
- Goal close reads child-owned issue closeout evidence; no second local progress
  ledger or duplicate acceptance database is introduced.

## Owning Surfaces

- premise and slice-manifest schemas/producers/validators
- critique, prove, and retro goal-lineage fields
- issue closeout proof references consumed by guarded Goal Run close
- host-metric and release evidence that claim work against a Goal Run
- a machine-readable classifier for all goal-identity consumers
- synchronized `plugins/charness/` mirrors and focused tests for these surfaces

Handoff draft production belongs to `goal-binding-v1`; public `achieve`,
`/goal #N`, and active workflow coordination belong to
`achieve-orchestration`; provider observations and guarded close belong to
`goal-run-provider`. General docs/export cleanup remains with the child that
owns the changed behavior. This child verifies the combined census but does not
become a catch-all writer.

## Dependencies

- Goal Binding V1 and canonical draft producer
- issue-owned Provider Observation and guarded-close contracts
- achieve planning, establishment, pickup, and active-child selection

## Implementation Contract

1. Define one reusable `goal_lineage` shape containing schema version, draft
   path/hash, binding path/hash, parent repository/number, and—when work is
   selected—manifest key plus child repository/number.
2. Embed or reference that shape from premise, slice-manifest, critique/prove,
   retro, closeout, host-metric, and release evidence without changing each
   artifact's domain ownership.
3. Validate complete identity equality before one artifact consumes another;
   matching local paths or issue numbers alone are insufficient.
4. Preserve planning-only records with an explicit non-execution disposition;
   never manufacture nullable/fake parent identity.
5. Keep behavioral closeout evidence on the child issue and bind its exact
   comment/evidence identity into provider observations used by parent close.
6. Do not append execution state to the frozen draft or create a local child
   acceptance ledger.
7. Add `scripts/classify_goal_consumers.py`. It emits deterministic JSON rows
   with path, line, matched token, owning child, classification, and rationale;
   unknown/unclassified rows fail.
8. Scan canonical roots, `.agents`, README surfaces, docs, scripts, tests,
   generated plugin placements, and semantic old-path tokens. Normalize a
   no-match search result as a valid empty set, not a command failure.
9. Treat any defect owned by binding, provider, or orchestration as a blocking
   dependency routed back to that child, not as permission to edit it here.

## Acceptance Criteria

- Each named evidence family has a versioned fixture with complete lineage.
- Cross-draft, cross-binding, cross-parent, and cross-child substitutions fail
  with distinct typed outcomes.
- Planning-only evidence remains valid but cannot satisfy implementation or
  closeout proof.
- Guarded close can map every closed child to issue-owned behavioral evidence
  or a verified successor deferral without consulting a second local ledger.
- The classifier covers every repository match and reports zero unclassified
  or defect rows after all owning children complete.
- The classifier itself does not claim that token absence proves semantics; its
  fixture suite verifies positive, negative, generated, and historical cases.
- Canonical and generated plugin trees are synchronized.

## Verification Commands

Create or reshape the target modules, then run:

```bash
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_evidence_lineage.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_retro_persistence.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_slice_manifest.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_issue_goal_run_close.py
python3 scripts/classify_goal_consumers.py --repo-root . --format json --output .charness/goal-consumer-census.json
python3 scripts/sync_root_plugin_manifests.py --repo-root .
bash scripts/check-docs.sh
```

The classifier command must exit nonzero on unknown/defect rows and emit the
receipt even on failure. Run repo-selected changed-line proof before broad
quality; neither a broad pass nor a zero grep count replaces lineage fixtures.

## Adversarial Stimuli

- same draft path with a different frozen hash
- same issue number in another repository
- premise from one child reused by another child
- planning-only record presented as implementation proof
- closed child with no exact issue-owned behavioral evidence
- generated plugin consumer left stale while canonical tests pass
- unknown consumer token omitted from the classifier's known categories
- clean checkout with no uncommitted prototype files

## Documentation Impact

Update artifact-policy and proof/retro/closeout documentation for the lineage
shape. Promote `docs/goal-lifecycle.md` from conditional to current only after
all four system capabilities and the live dogfood prove the described behavior.

## Closeout Evidence

Versioned lineage fixtures, classified whole-repository census, source/export
sync, docs receipt, changed-line proof, and fresh-eye review of the repaired
evidence validators. Live GitHub establishment remains the dogfood child's
proof obligation.

## Non-Goals And Non-Claims

- no handoff producer rewrite
- no public `achieve` orchestration rewrite
- no provider primitive or lifecycle policy implementation
- no local progress mirror or child-acceptance database
- no historical goal-file rewrite
- no live GitHub claim
