# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the five-pass boundary cleanup slice that converts repeated subprocess
assertions to in-process calls where existing callable seams can preserve the
same behavior proof.

## Failure Angles

- Kent Beck/test feedback: converting too aggressively could remove the only
  proof that an operator-facing script still parses arguments and emits JSON or
  success text.
- Gawande/operations: in-process script loaders could leak `sys.argv`, miss
  stdout capture, or hide import-time side effects.
- Ousterhout/design: repeated path-loader helpers could become test scaffolding
  complexity rather than speed cleanup.

## Counterweight Pass

- Fresh-eye found two high over-conversions: setup operator-acceptance synthesis
  and quality closeout contract validation had no other real CLI proof.
- The final patch restores those subprocess tests and keeps only conversions
  where another CLI proof exists or where the test targets validator internals.
- Focused pytest, ruff, and boundary-bypass ratchet passed after the restore.
- Cautilus was not run because `plan_cautilus_proof.py` returned
  `next_action: none`; this is a deterministic test-structure slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_docs_and_misc.py | action: fix | note: restored the only real CLI proof for synthesize_operator_acceptance.py after fresh-eye flagged its removal
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_docs_and_misc.py | action: fix | note: restored the only real CLI proof for validate_quality_closeout_contract.py after fresh-eye flagged its removal
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_find_skills_shadowing.py | action: fix | note: list_capabilities shadowing behavior now runs in-process while other tests still cover the real CLI
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/test_find_skills_synced_support.py | action: fix | note: synced-support cross-link behavior now runs in-process while preserving JSON payload assertions
- F5 | bin: bundle-anyway | evidence: strong | ref: tests/control_plane/test_integrations_validation.py | action: fix | note: four validate_integrations failure cases now call direct validator functions and keep the relevant error fragments
- F6 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_docs_and_misc.py | action: fix | note: find-skills trusted-root and impl survey behavior use in-process main calls with monkeypatched argv and captured stdout
- F7 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_docs_and_misc.py | action: defer | note: duplicated dataclass-safe script loaders are acceptable in this slice but should become a helper if the pattern repeats

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent_type=explorer, fork_context=false, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f014f-0f66-7582-a917-7bfb3b576989`
completed through `multi_agent_v1.spawn_agent`; the reviewer found two high
findings, and the parent patch restored both unique CLI proofs before closeout.
