# Issue preflight test split critique
Date: 2026-06-12

## Decision Under Review

Split issue preflight/backend-resolution tests out of
`tests/quality_gates/test_issue_skill.py` into
`tests/quality_gates/test_issue_preflight.py`, and centralize the duplicated
issue adapter YAML fixture writer in `tests/quality_gates/support.py`.

## Failure Angles

- Problem framing: this could be metric gaming if the slice merely moved lines
  out of the warned file. Verdict: the split is behavior-aligned because the
  preflight assertions remain visible in a dedicated test module, while only
  mechanical adapter YAML scaffolding moved into support.
- Diagnostic: this could introduce hidden coupling through an over-broad test
  helper. Verdict: the helper only writes the shared base adapter fixture; tests
  still mutate shape-specific adapter details and keep behavior assertions local.

## Counterweight Pass

- Act before ship: include the new `test_issue_preflight.py` file in the commit;
  otherwise the moved assertions would be dropped.
- Over-worry: a broader adapter fixture builder or fake-binary DSL would expand
  the slice beyond the current pressure point.
- Valid but defer: repeated fake `ceal` binary setup and broader issue-test
  architecture cleanup remain possible future slices.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_preflight.py:1 | action: fix | note: include the new preflight test file in the commit.
- F2 | bin: over-worry | evidence: strong | ref: tests/quality_gates/support.py:65 | action: document | note: hidden-behavior concern is over-worry because the helper only writes fixture YAML.
- F3 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_issue_skill.py:158 | action: document | note: generalizing all remaining adapter writes would broaden the slice.
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_issue_preflight.py:81 | action: defer | note: repeated fake ceal binary setup is a future test-fixture cleanup candidate.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted reviewer requests; host did not confirm provider-side application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned two bounded angle
reviewers and one separate counterweight reviewer through `multi_agent_v1`;
all completed read-only review. No same-agent substitute was used.
