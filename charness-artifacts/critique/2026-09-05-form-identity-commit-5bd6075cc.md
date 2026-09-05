# Form-identity commit 5bd6075cc

Date: 2026-09-05

## Decision Under Review

Whether commit `5bd6075cc` (`Hold skill, closeout, consumption, and enum
identity in form`) actually holds those identities in form, or still leaves the
invalid state representable behind a renamed checker. The commit is local on
`main`, not pushed, and is not a release.

## Diff Scope

Shared `core_nonempty_lines`, Closeout Schema refusal, undeclared inventory
citation, install-mode `none` removal plus `x-axis`, and the matching tests and
prose cuts. 31 files.

## Verification Scope Decision

- Claim under test: the four identities this commit named are held by form, not
  by leftover controller prose or a filename-shaped stand-in.
- Changed surfaces: the 31 paths in
  `charness-artifacts/critique/form-versus-controller-packet.md`; final consumers
  are integration-manifest authors, classifier-bearing public skills, quality
  artifacts that cite inventories, and the skill-ergonomics inventory.
- Minimum sufficient proof: two file-backed workers on the identity-bound
  packet, then parent source confirmation of each cited path.
- Deliberately omitted checks: full `--release` lane, live Codex/Claude install
  of a consuming repo, and executing every closeout validator.
- Verifier contract: Charness-owned file-backed worker
  (`run_review.py` / `bounded-review-result.schema.json`); the closeout-schema
  gate is itself a reviewed subject, not this pass's verifier.
- Failure classification: subject-defect
- Negative control: none with rationale: this pass is a semantic review of a
  committed form; the workers' `block` is the discriminating signal, and the
  parent confirmed the cited source paths by reading them.
- Subject identity: sha256:b9928261f59364692ea01f498d9714375ce9f3a3448594dc4e62f5f7741a037c
- Verifier identity: sha256:a699eb17aca0d1f832bfb467ce3cff85b22d420183ea68bc4b52fc3cde6b71a3
- Input identity: sha256:ebcbc32de6d4616a047fe33405b15b8d04709c1726d0af084061f039831c9631
- Failure identity: stable:form-identity-reviewer-block
- Evidence identity: sha256:7c9424485325f3a793b440a50c793e57e8bed3471c7ac8fcb7af9d80b4aff1df
- Retry disposition: first-attempt
- Retry key: sha256:7203506fb54ff2a72c55f6c073371b157bb49f18e885b61e68455e01d7d173b7

## Failure Angles

- Form-versus-controller: a deleted sentinel or a newly refusing gate still
  leaves the invalid state representable (Jackson).
- Repo-already-decided / consumer blast-radius: the slice contradicts its own
  taxonomy or over-applies a quality-namespace rule to other inventories
  (Weinberg / Gawande).

## Counterweight Pass

Two file-backed Codex workers independently blocked. Parent collapsed six
concerns and pushed back on expanding this slice into optional-lifecycle
machinery, executable-validator registries, or structured command receipts.

- Act Before Ship: the taxonomy still tells authors that absence is omit, while
  `lifecycle.install` and `lifecycle.update` remain required with a method
  `mode`; and the Closeout Schema gate treats a `# stub` file as satisfaction of
  a rule that demands refusal behavior. Those are the slice's own claims, not
  new product surface.
- Bundle Anyway: carry `x-axis` field identity through composition/`$ref`;
  namespace inventory citations to `skills/public/quality/scripts/`; delete the
  duplicate ergonomics exemption walker.
- Over-Worry: restore `none`; demand Draft-07 engines honor `x-axis`; chase
  `if`/`then`/`patternProperties` with no live instance.
- Valid but Defer: optional install/update for a tool that does not install
  (no live manifest needs it); negative fixtures that execute every classifier
  validator; binding inventory consumption to structured receipts.

`none` stays gone. Manual stays a real install method. Count identity in
`skill_core_density.core_nonempty_lines` is a real improvement and is not a
blocker.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/spec/references/taxonomy-axis-checkpoint.md; integrations/tools/manifest.schema.json | action: fix | note: taxonomy says absence is omit and a non-installing tool is not a fake method, but lifecycle.install/update and action.mode are required; make those two sentences agree with the schema (qualify the worked example) rather than restoring none or adding unused optional-lifecycle machinery
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_skill_output_schemas.py:47; scripts/gates/validate_skill_output_schemas.py:64-74 | action: fix | note: the gate claims the Closeout Schema Rule is satisfied when a matching filename exists, including a # stub; stop encoding that lie in the test and in gap_summary
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/gates/check_schema_enum_axis.py:81-107 | action: fix | note: field_name is dropped through oneOf/anyOf/allOf and local $ref, so a generic enum can evade x-axis; live schemas put enum on the property node, so this is a hatch in the new gate, not a live corpus failure
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/gates/validate_inventory_consumption.py:57,414; skills/public/quality/references/inventory-consumer-fields.json | action: fix | note: undeclared-citation refusal matches basenames only, so a non-quality inventory_*.py in Commands Run is judged against the quality declaration
- F5 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/skill_ergonomics_lib.py:45-68 | action: fix | note: the count walker is shared, but prose heuristics still use an unbounded exemption set that omits Closeout Vocabulary and is not fence-aware
- F6 | bin: over-worry | evidence: weak | ref: integrations/tools/manifest.schema.json; scripts/gates/check_schema_enum_axis.py | action: document | note: restoring none, requiring ordinary JSON Schema engines to honor x-axis, and walking if/then with no live instance
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/install_tools.py:108; scripts/gates/validate_skill_output_schemas.py; scripts/gates/validate_inventory_consumption.py | action: defer | note: optional lifecycle omit, executable classifier-validator fixtures, and structured inventory receipts are real next forms once a consumer needs them

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority` (from the prepare packet; application unverified)
- Host exposure state: host-defaulted
- Application state: adapter selected file-backed `codex_exec`; no independent provider-application signal
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: `.charness/reviewer-round-form-versus-controller/worker-report.yaml` <!-- reproduction-source -->
- Worker report identity: 805fbc492b2c5263234c4a36a745dd69eafa0381fc2fd3eef1c1274779fa04b0
- Worker report approval: approval_eligible: false
- Worker report delivery: findings-received
- Worker report packet identity: ebcbc32de6d4616a047fe33405b15b8d04709c1726d0af084061f039831c9631
- Worker report input identity: b9928261f59364692ea01f498d9714375ce9f3a3448594dc4e62f5f7741a037c
- Worker report parent receipt identity: parent-95c3a3464af605e3948127c16b72e22bcb27657405808159
- Worker report findings identity: 7c9424485325f3a793b440a50c793e57e8bed3471c7ac8fcb7af9d80b4aff1df
- Second worker report: `.charness/reviewer-round-repo-decided-blast-radius/worker-report.yaml` identity `37926b559b6d6bbcd7dd8f82c9aefde0a5497359f9cda4a8c66db405efaf4717`, findings `9cff104c5c4ade16ce241ae3617b28011a8fde406a9c16e4cf992c4d4b4e6109`, parent receipt `parent-3a7460e8e1dc6773ed3fec9b3a9179163b928a1f1e361bdc`, also `approval_eligible: false` / `findings-received` / verdict `block` <!-- reproduction-source -->

## Fresh-Eye Satisfaction

parent-delegated; two file-backed Codex workers delivered `findings-received`
with `review_verdict=block` and `approval_eligible: false`. This artifact is the
parent counterweight of those findings, not approval of commit `5bd6075cc`. No
same-context substitute was used.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/form-versus-controller-packet.json
- Packet path: charness-artifacts/critique/form-versus-controller-packet.json
- Packet SHA256: ebcbc32de6d4616a047fe33405b15b8d04709c1726d0af084061f039831c9631
- Identity SHA256: b9928261f59364692ea01f498d9714375ce9f3a3448594dc4e62f5f7741a037c
- Twin packet (identical bytes): charness-artifacts/critique/repo-decided-blast-radius-packet.json

## Boundary Ownership

- Producer: `taxonomy-axis-checkpoint.md` produces the omit rule; the integration
  manifest schema produces representable lifecycle states; `validate_skill_output_schemas.py`
  produces the Closeout Schema verdict; `skill_core_density.py` produces the
  core-count identity.
- Consumer: authors of integration manifests, classifier-bearing skills, quality
  artifacts, and the skill-ergonomics inventory.
- Owning surface: the schema or gate that holds the identity, not a second
  checker or a taxonomy sentence that the schema cannot represent.
- Verdict: owned-correctly

## Defect Class Cross-Link

`copy-held-by-test`: the stub-clearing test is the Closeout Schema contract.
The omit/required split is the same class as a rule held only in prose.

## Capability Gap

None. The gates exist; the form they enforce is incomplete relative to the
sentences this slice published.

## Deliberately Not Doing

- Restoring install mode `none`.
- Adding optional lifecycle.install/update before a non-installing tool exists.
- Executing every classifier validator or requiring negative fixtures for all
  of them in this repair.
- Replacing lexical inventory citation with structured receipts.
- Walking every JSON Schema keyword the live corpus does not use.

## Pre-Merge Action

Commit `5bd6075cc` is already local. Before push or release:

1. Make taxonomy-axis-checkpoint and the manifest schema agree about omit
   (F1). Smallest honest form: every integration manifest has install and
   update methods; do not encode inapplicability as `none`.
2. Stop treating a stub file as Closeout Schema satisfaction (F2).
3. Bundle F3–F5 while that surface is open.
4. One follow-up fresh-eye round on the repaired proof surface. Do not spawn
   round 2 over this unchanged tree.

## Next Move

Repair F1 and F2, bundle F3–F5, then one round-2 worker pass on the repaired
tree. Do not push `5bd6075cc` as the form-identity closeout.
