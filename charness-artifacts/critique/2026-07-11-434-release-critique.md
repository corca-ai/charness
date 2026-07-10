# Issue #434 / v0.66.0 Release Critique
Date: 2026-07-11

## Decision Under Review

Ship issue #434 as v0.66.0: add the optional
`scaffold.execution_efficiency_context_path` adapter field, validate its
repo-owned file target, and append one pointer to newly scaffolded goals without
rewriting existing goals or replacing portable frame defaults.

## Execution

- Target: release critique, with code-contract and operator-surface angles.
- Packet Consumed: `charness-artifacts/critique/2026-07-10-233307-packet.md`.
- Angles: operational/path safety; humane adapter interface and boundary
  ownership; separate skeptical counterweight.
- Reviewer boundary proof: both angle reviews and the counterweight returned
  `ok: true` with no worktree, index, HEAD, or untracked-path drift.

## Failure Angles

- Operational/path safety: missing, absolute, escaping, directory, and symlink
  targets must fail before scaffolding; contained regular files and contained
  symlinks must remain usable.
- Humane interface: an operator must be able to uncomment the adapter example
  without corrupting YAML, and the optional field must not imply migration or a
  completion floor.
- Boundary ownership: `achieve` owns both adapter validation and new-goal
  rendering; consumer-specific efficiency policy remains in the referenced
  repo file.
- Release lock: source, exported plugin mirrors, tests, release notes, public
  verification, issue closeout, and maintainer install refresh must agree.

## Counterweight Pass

- Act Before Ship: the initial commented field split
  `draft_active_frame_lines`; fixed by moving it after the complete list and
  protecting the uncomment path with a regression test. Locked verification
  and release publication remain required process actions.
- Bundle Anyway: absolute-path rejection lacked a direct test; added to the
  invalid-path matrix. No further adjacent work earns this release's scope.
- Over-Worry: additional consumer-specific gate schemas, multiple context
  paths, or a new completion validator would expand the contract without
  reported demand. The single pointer keeps policy in the consumer repo.
- Valid but Defer: none. The adapter-contract example names a hypothetical
  consumer file, but the shipped adapter example keeps the field commented and
  the contract explicitly requires operators to create their chosen file.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/adapter.example.yaml | action: fix | note: resolved before verification by moving the optional field after the full frame-line list and testing uncommented YAML
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_goal_artifact_scaffold.py | action: fix | note: resolved by adding explicit absolute-path rejection coverage
- F3 | bin: over-worry | evidence: strong | ref: skills/public/achieve/references/adapter-contract.md | action: document | note: multiple context paths and a new completion floor are deliberately outside the reported capability

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.5`, reasoning effort `medium`, service
  tier `priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but did not expose
  provider-side application metadata.

## Fresh-Eye Satisfaction

parent-delegated — two distinct angle reviewers and one separate counterweight
reviewer completed the bounded read-only review.

## Boundary Ownership

- Producer: `achieve_adapter_policy` validates the consumer-declared pointer.
- Consumer: newly scaffolded `achieve` goal artifacts render the pointer in the
  active operating frame.
- Owning surface: public `achieve` skill adapter and scaffold.
- Verdict: owned-correctly

## Release Scope

- Version: `0.66.0`; tag: `v0.66.0`.
- Consumer change: repositories may add one durable execution-efficiency
  context pointer without copying Charness frame defaults.
- Bump rationale: minor, because this is a new additive maintained adapter
  capability with no migration for existing consumers.

## Surface-Lock Inventory

- Adapter contract and example under `skills/public/achieve/`.
- Adapter validation, goal scaffold rendering, and upsert call site.
- Exported `plugins/charness/skills/achieve/` mirrors.
- Focused adapter/scaffold regression tests.
- Release metadata, public tag/release, issue #434 closeout carrier, and local
  installed-plugin refresh produced by the release helper.

## Quality Review

- Target boundary: `achieve` adapter validation and new-goal scaffold behavior;
  repo-wide heuristic findings are ambient and unchanged.
- Capability needed: a consumer-owned efficiency baseline pointer that composes
  with portable frame defaults.
- Current centers: adapter policy, goal scaffold, focused tests, exported plugin
  mirror, and the existing hitl-recommended dogfood case.
- Structural review result: strengthen the existing adapter/scaffold seam and
  reuse standing gates; no new floor, evaluator scenario, or quality mechanism.
- Prose review result: the new reference remains progressive-disclosure detail;
  it does not change the `achieve` trigger boundary or add a host-specific rule.
- Maintainer-Local Enforcement: healthy — the checked-in pre-push hook owns the
  full read-only quality gate for this skill/export diff.
- Recommended Next Quality Moves: none for this slice after locked proof.

## Public Skill Dogfood Decision

The current `achieve` case in `docs/public-skill-dogfood.json` remains the
correct consumer routing and Before-phase lifecycle contract. Issue #434 does
not change routing, activation, or artifact identity, so the case is retained
without modification. The new adapter/scaffold semantics are proven directly by
the checked-in focused tests; a maintained Cautilus scenario is not required.

## Operator Action Required

- Create the chosen repo-relative context file, configure
  `scaffold.execution_efficiency_context_path`, then run the normal goal
  scaffold flow.
- Before publication, run synced-source validation and locked broad proof; use
  the repo release helper so public readback, issue closeout, and install refresh
  stay in one evidence ledger.

## Upgrade Path

Run `charness update` to install the latest published release. Existing adapters
and existing goals require no migration. Remove the optional field to roll back
the new pointer behavior for future goals.

## Deliberately Not Doing

- No Ceal-specific gate names or embedded efficiency manual.
- No list-valued context API until more than one real consumer need exists.
- No rewrite of existing goal bodies and no new completion floor.

## Next Move

Run the focused and locked repo closeout gates on the reviewed diff, then publish
v0.66.0 with #434 linked and verify behavior through fresh scaffold evidence,
public HTTPS readback, and maintainer install refresh.

## Release Gate Follow-up

The first publish attempt stopped before commit, tag, push, release creation, or
issue close. Its release-only quality pass found four uncovered adapter-error
branches and one existing adapter-validator clone family whose fingerprint
rotated when the explicit `repo_root` call changed. The follow-up kept the clear
parameterized design, added direct tests for empty/multiline values and
`Path.resolve` exceptions, produced fresh changed-line coverage, and performed
the implementation-discipline-prescribed single dup-ratchet rebaseline after
the source batch locked. Focused tests, changed-line coverage, and the dup
consumer now pass. These are proof/ratchet repairs inside the reviewed boundary,
not a new capability or release risk boundary.
