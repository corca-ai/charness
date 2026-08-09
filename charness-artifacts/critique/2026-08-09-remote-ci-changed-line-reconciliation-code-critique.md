# Remote CI Changed-Line Reconciliation Code Critique
Date: 2026-08-09

## Decision Under Review

Repair the local changed-line accelerator at the supported dynamic-loader
boundary, then make the existing regenerable-facts test observe the entry and
fallback branches in-process, without changing the non-blocking policy for
genuinely unmapped files.

## Failure Angles

- Jackson and Weinberg: distinguish the root reachability/observation defect
  from the adjacent temptation to reverse mapper policy or weaken the remote
  gate.
- Gawande: require the final local consumer, not unit tests or selector output,
  to own the eventual clean verdict; preserve dirty-tree refusal as a non-pass.
- Minto and a future maintainer: pin all three promised loader token modes and
  the safe same-basename over-selection direction rather than only the original
  filename spelling.

## Findings

- Round 1 found no production-design blocker. The bounded AST loader family is
  the right reachability owner, and direct in-process tests are the right
  executable-observation owner.
- Act before ship: the contract initially compressed post-test target coverage
  and a dirty-tree wrapper exit 3 into a future “pass.” It now records mapper-
  only exit 1, eight-line post-test coverage, dirty-tree `unestablished`/exit 3,
  and the pending post-commit wrapper proof separately.
- Act before ship: the first test fixed only the filename form. The repaired
  parameterized test now pins full path, filename, and stem, while a second test
  proves same-basename loader selection can over-select and an arbitrary quoted
  filename cannot map.
- Bundle anyway: the first packet's six identity-bound paths versus seven
  changed surfaces were clarified. The final round-2 packet binds all seven
  current repaired inputs, including the current pointer.
- Round 2 read the repaired full surface and found no blocker or accepted-
  unreviewed verdict-logic risk.

## Counterweight Pass

- Act before ship: post-commit old-range wrapper proof is still required; it is
  an explicit pending non-claim, not an approval.
- Bundle anyway: keep the token-mode, same-basename, and plain-string controls
  with this change.
- Over-worry: general AST data-flow resolution and eliminating all safe extra
  test selection are not warranted by this recorded escape.
- Wrong/not relevant: the old packet-count concern no longer applies to the
  final packet identity and does not alter verdict logic.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md | action: fix | note: separate selector mapping, target coverage, dirty-wrapper refusal, and post-commit proof states
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_suggest_mutation_coverage_command.py | action: fix | note: pin full-path, filename, stem, same-basename over-selection, and plain-string non-mapping
- F3 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/critique/2026-08-09-080414-packet.json | action: document | note: final packet binds all seven repaired inputs and supersedes the ambiguous round-1 count
- F4 | bin: over-worry | evidence: strong | ref: scripts/suggest_mutation_coverage_command.py | action: defer | note: arbitrary alias data-flow and removal of safe false-stop over-selection exceed the recorded failure

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`, read-only prompts.
- Host exposure state: requested_fields_sent
- Application state: the spawn surface accepted the requested fields and
  returned completed findings; provider application metadata was not exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Round 1 used three independent read-only angles and a separate
read-only counterweight. Their two act-before-ship findings changed the test and
evidence surfaces. A distinct round-2 reviewer then read the repaired full
verdict surface and found no blocker. Parent-side boundary verification returned
`verdict: clean` for the angle, counterweight, and repaired-surface windows.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-09-080414-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-09-080414-packet.json`
- Packet SHA256: `8442d8931c0cd22027f2f2bdc413f20a87dd608c75d167edd9b0902e494c13bd`
- Reviewer-facing packet: `charness-artifacts/critique/2026-08-09-080414-packet.md` (SHA256 `7a0fb1c7d7abbfb94d2a0fea1087d5190f930cb5abf5e271584bc8b1ab1eda34`)
- Identity SHA256: `8760b6a762532f726fe13321eaa9fcf7f1f6ff8064c892dab9ad809f75344497`

## Boundary Ownership

- Producer: the shared selector produces test reachability; the selected tests
  produce executable observations.
- Consumer: `prepush_focused_changed_line_coverage.py` produces the final local
  changed-line verdict; GitHub's broad mirror is the hosted independent reader.
- Owning surface: selector recognition, owning tests, and existing consumers
  retain separate responsibilities.
- Verdict: owned-correctly

## Deliberately Not Doing

- No mapper-policy reversal, coverage exclusion, scope reduction, new gate,
  arbitrary data-flow resolver, push, or hosted-CI success claim.

## Pre-Merge Action

Sync generated projections, pass changed-surface and quality gates, commit the
repair, then run the old-range final local consumer on the clean analyzed tree.

## Next Move

Complete deterministic closeout and the post-commit old-range wrapper proof.
Ask for push approval only after local proof and commits are complete; read back
the hosted result through GitHub after any approved push.
