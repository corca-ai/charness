# Issue skill loader/probe split critique
Date: 2026-06-12

## Decision Under Review

Refactor the issue public skill so repeated sibling module loading is centralized
in `issue_local_import.py`, and move issue preflight backend probing out of the
CLI dispatcher into `issue_backend.py`. The slice should reduce real
`issue_tool.py` length pressure without changing issue CLI behavior or plugin
export behavior.

## Failure Angles

- Michael Jackson / problem framing: the change could have solved an adjacent
  refactor instead of the named duplication and hard-length pressure. Verdict:
  the diff addresses the named problem because `issue_tool.py` leaves the
  Python length warn band and the repeated local loader body is removed from the
  touched issue scripts.
- Gerald Weinberg / diagnostic: moving code could hide the symptom by making
  another module bloated or by missing the CLI branch that changed. Verdict:
  `issue_backend.py` remains cohesive and small enough, and the non-JSON
  preflight config-error path now has focused coverage.

## Counterweight Pass

- Act before ship: include the new source and plugin helper files in the
  commit. This is staging discipline, not a code edit.
- Bundle anyway: the cheap non-JSON preflight test was added in
  `tests/quality_gates/test_issue_skill.py`.
- Over-worry: replacing the `runpy.run_path(... "issue_local_import.py")`
  one-liner with a broader import framework would expand the review surface
  without solving a current failure.
- Valid but defer: future `issue_tool.py` command-handler growth and
  `test_issue_skill.py` length pressure remain real next-slice candidates.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_local_import.py:1 | action: fix | note: include the new source helper and plugin mirror in the commit.
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_issue_skill.py:208 | action: fix | note: focused non-JSON preflight config-error coverage was added.
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/issue/scripts/issue_read.py:8 | action: document | note: broader import framework is unnecessary for this slice.
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_issue_skill.py:1 | action: defer | note: test file length pressure remains a next-slice candidate.
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/scripts/issue_tool.py:27 | action: defer | note: future command-dispatch cleanup belongs in a separate slice.

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
