# Gather Acquisition Repair Plan Critique

- Date: 2026-05-16
- Target: pre-impl spec critique for the next gather acquisition repair slice
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-16-015120-packet.md`
- Source Artifact: `charness-artifacts/critique/2026-05-16-gather-acquisition-subagent-critique.md`

## Change

The proposed next slice would repair the blockers found in the gather
acquisition code critique. The initial repair outline named seven Act Before
Ship issues plus two cheap bundle items, but it had not yet been converted into
an implementation contract.

## Angles

- Barbara Minto / structure and acceptance coverage: checked whether the repair plan has a coherent Fixed / Probe / Defer split and runnable acceptance matrix.
- Michael Jackson / problem framing: checked whether the plan solves public gather acquisition, not only trace honesty.
- Atul Gawande / operational acceptance: checked whether the plan names operator-visible proof, negative regressions, plugin sync, and deterministic gates.
- Counterweight: separated required pre-impl contract work from over-specification.

## Counterweight Triage

### Act Before Ship

1. Convert the repair triage into an implementation contract before `impl`.
   - Required sections: Current Slice, Fixed Decisions, Probe Questions, Deferred Decisions, Non-Goals, Success Criteria, and deterministic Acceptance Checks.
   - Rationale: the current artifact is a bug triage, not yet a contract implementation can consume without inventing policy inline.

2. Fix unresolved decisions explicitly.
   - Invalid `--expect-regex`: config/input error or invalid proof, never success proof.
   - Domain routes: either execute bounded routes or emit truthful skipped / not-implemented attempts.
   - Selector proof: implement `--expect-selector` with tests or remove the shipped documented promise.
   - Blocker plus proof: choose blocked or contested; positive proof must not override blocker signals.

3. Add acceptance coverage for each blocker with asserted JSON/artifact fields.
   - Minimum negative tests: non-HTTP URL, invalid regex, blocker-before-proof, missing tools, skipped domain routes, and recon-only non-success.
   - Acceptance must also cover selected attempt / final status semantics.

4. Decide whether public `gather` invokes `web-fetch` for arbitrary public URLs in this slice.
   - If yes: add a proof path showing the public workflow records route, attempts, selected proof, access mode, and open gaps in the durable asset.
   - If no: do not claim the slice closes gather acquisition; name it as support-tool trace/proof correctness.

5. Choose the slice claim: acquisition maximization or trace/proof correctness.
   - If acquisition maximization remains the claim, define minimal acquired-content persistence or a selected acquired-content output contract.
   - If only trace/proof correctness is in scope, explicitly defer raw acquired-content persistence and avoid claiming acquisition maximization.

6. Specify network reconnaissance semantics.
   - Recon-only output may be a lead, not selected success.
   - A candidate URL can count toward acquisition only after it is fetched and classified in the same run.

7. Include plugin sync/export and packaging validators in acceptance.
   - Required commands include `python3 scripts/sync_root_plugin_manifests.py --repo-root .`, `python3 scripts/validate_packaging.py --repo-root .`, and `python3 scripts/validate_packaging_committed.py --repo-root .`.

### Bundle Anyway

1. Add one explicit weak-direct-success / `defuddle` rule while touching the contract.
   - Cheap version: weak direct success may stop unless the slice explicitly claims reader extraction or acquisition maximization.
   - External `defuddle` runtime proof can remain stubbed; deterministic command-shape and error-handling tests are enough for this slice.

### Valid But Defer

1. Raw acquired-content persistence can defer if the current contract honestly scopes to durable trace/proof only.

2. No-site-name / generic-helper lint can defer; it is useful anti-fossilization work, not required for this repair slice.

### Over-Worry

1. Requiring live external `defuddle` proof before this repair ships is over-scoped.
   - Stubbed invocation plus deterministic command-shape/error-handling tests are enough for the current slice.

## Next Move

Before editing code again, write a compact implementation contract for the
repair slice. The contract should choose between `gather acquisition
maximization` and `web-fetch trace/proof correctness`; then map each fixed
decision to one deterministic acceptance check.
