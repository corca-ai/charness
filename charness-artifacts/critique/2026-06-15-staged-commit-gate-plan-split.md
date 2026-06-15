# Staged Commit Gate Plan Split
Date: 2026-06-15

## Decision Under Review

Split private helper families out of `scripts/staged_commit_gate_plan.py` into
`scripts/staged_commit_gate_plan_helpers.py`, keep the planner module as the
public API/CLI owner, sync the plugin mirror, and record the quality closeout.

## Failure Angles

- Michael Jackson/problem framing: the split could solve "line count" while
  losing the commit-boundary shift-left rationale or changing the public import
  surface.
- Gerald Weinberg/diagnostic: the split could move the symptom into a helper
  while leaving direct script execution or plugin-export execution broken.
- Counterweight: avoid expanding a narrow headroom repair into a broader planner
  architecture refactor or test-economics cleanup.

## Counterweight Pass

- Acted before ship on commit composition: new helper files, plugin mirror, the
  critique packet, and this critique record must be included with the slice.
- Bundled cheap reviewer findings: added short helper docstrings for moved
  rationale and a plugin-export CLI regression in
  `tests/quality_gates/test_staged_commit_gate_plan.py`.
- Treated broad planner redesign and helper-name tidiness as valid but deferred;
  neither changes behavior for this headroom split.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:17 | action: fix | note: include the new source and plugin helper files so planner imports cannot break after commit
- F2 | bin: bundle-anyway | evidence: moderate | ref: scripts/staged_commit_gate_plan_helpers.py:38 | action: fix | note: restore short why-oriented helper context after extraction
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_staged_commit_gate_plan.py:345 | action: fix | note: add plugin-export direct CLI regression for the import-path risk
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/staged_commit_gate_plan.py:37 | action: defer | note: broader planner architecture remains dense but is out of scope for this headroom repair
- F5 | bin: over-worry | evidence: weak | ref: scripts/staged_commit_gate_plan.py:17 | action: document | note: public API break concern is unsupported because old imports are re-exported and tested

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.5`, reasoning_effort `medium`, service_tier `priority`.
- Host exposure state: requested_fields_sent
- Application state: tool accepted agent ids `019ecb7f-3aea-7221-b092-2d417e53cef6`, `019ecb7f-3b1c-75c3-a8be-a687643776ab`, `019ecb7f-3b91-7961-9208-afb733cdf689`; provider application not independently confirmed.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Packet consumed:
`charness-artifacts/critique/2026-06-15-133555-packet.md`. Two angle reviewers
and one counterweight reviewer completed read-only review in the shared worktree
with no prohibited git operations. No code blocker remained after the bundled
docstring and plugin-CLI test changes.
