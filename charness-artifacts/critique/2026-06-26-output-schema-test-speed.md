# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the output-schema test-speed slice that moves tmp-repo survey behavior
assertions below the subprocess boundary while preserving a real CLI JSON smoke
for `scripts/validate_skill_output_schemas.py`.

## Failure Angles

- Jackson/problem framing: optimizing nested process cost could accidentally
  remove the shipped script contract.
- Gawande/operations: behavior might become hidden behind helpers if assertions
  move away from the test site.
- Kent Beck/test feedback: the slice should reduce repeated subprocess fanout
  without requiring a new gate or broad redesign.

## Counterweight Pass

- The first draft failed the real-boundary check; fresh-eye found that an
  in-process `main()` smoke did not prove `python scripts/... --json`.
- The final patch keeps one subprocess `run_script()` smoke and parses full JSON
  from stdout.
- The tmp-repo survey assertions remain visible at the test site and exercise
  the same classifier-schema, validator-file, and prose-only decisions through
  `survey()`.
- Adding another candidate now is over-worry; this slice already repaired the
  false-confidence gap found during review.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_skill_output_schemas.py | action: fix | note: first draft removed the real subprocess CLI smoke; final patch restores it
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_skill_output_schemas.py | action: fix | note: tmp-repo behavior cases now call survey directly while keeping assertions readable
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_skill_output_schemas.py | action: fix | note: in-process main smoke parses full JSON instead of accepting a substring
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-06-26-output-schema-test-speed-quality-review.md | action: defer | note: remaining clean candidates should be converted one at a time after boundary-smoke review
- F5 | bin: over-worry | evidence: moderate | ref: scripts/validate_skill_output_schemas.py | action: document | note: requiring every survey behavior case to stay subprocess-backed would preserve cost without adding boundary confidence

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent_type=explorer, fork_context=false, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f010d-f1e6-7660-8e63-cc1ab4f2d0ce`
completed through `multi_agent_v1.spawn_agent`, found one act-before-ship issue,
and the parent patch restored a real subprocess CLI smoke before closeout.
