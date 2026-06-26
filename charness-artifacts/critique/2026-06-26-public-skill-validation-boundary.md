# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the public-skill validation/dogfood test-speed slice that moves ordinary
policy, registry, and matrix assertions below the CLI boundary while retaining
thin subprocess smokes for operator-facing script contracts.

## Failure Angles

- Kent Beck/test feedback: converting tests in-process could remove the only
  proof that CLI argument parsing, `__main__`, exit status, and stderr guidance
  still work.
- Gawande/operations: adding exemptions could hide ordinary behavior that should
  move below the boundary.
- Ousterhout/design: dogfood matrix tests might still pay hidden subprocess cost
  through adapter resolver calls, making the improvement smaller than it looks.

## Counterweight Pass

- The final patch keeps one real subprocess smoke for each of
  `validate_public_skill_validation.py`, `suggest_public_skill_validation.py`,
  `validate_public_skill_dogfood.py`, and `suggest_public_skill_dogfood.py`.
- Policy partition, adapter requirement, suggestion report, registry drift, and
  required-review behavior assertions now call the same library functions the
  CLIs use.
- The quality-gates wrapper parity test still spawns the root suggestion script,
  but its purpose is comparing root/source-wrapper/plugin-wrapper output, not
  retesting ordinary matrix content.
- Exemptions are narrow and include owner plus revisit conditions; plugin mirror
  sync propagated the same list to `plugins/charness`.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/test_public_skill_validation.py | action: fix | note: behavior assertions now call validate_policy, validate_adapter_requirement, build_report, and _format_human directly
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_public_skill_dogfood.py | action: fix | note: registry failure behavior now calls validate_registry directly while a real CLI smoke keeps success and matrix JSON contracts
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_public_skill_dogfood.py | action: fix | note: root matrix content now uses build_matrix in-process and wrapper parity remains a separate real-boundary check
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary-bypass-exemptions.txt | action: document | note: four retained CLI smokes carry why, owner, and revisit rationale
- F5 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/scripts/boundary-bypass-exemptions.txt | action: fix | note: plugin mirror was synced after exemption edits
- F6 | bin: valid-but-defer | evidence: moderate | ref: scripts/public_skill_dogfood_lib.py | action: defer | note: build_matrix can still spawn adapter resolvers internally for adapter-backed skills; this is a smaller later seam, not a blocker for removing outer CLI fanout
- F7 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_public_skill_dogfood.py | action: document | note: duplicate root CLI invocation is acceptable as part of root/source-wrapper/plugin-wrapper parity proof

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent_type=explorer, fork_context=false, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f0140-1e5f-7382-a451-82e7428e8abe`
completed through `multi_agent_v1.spawn_agent`; the reviewer found no blockers,
confirmed all four CLI boundaries still have meaningful proof, and raised the
wrapper-parity subprocess as a low residual risk that is documented above.
