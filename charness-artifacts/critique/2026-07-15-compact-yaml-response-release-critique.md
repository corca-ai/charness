# Critique Review
Date: 2026-07-15

## Decision Under Review

Release a corrective patch that makes high-fanout root `charness` commands
emit compact YAML summaries by default and reserve full evidence for `--detail`.

## Failure Angles

- A compatibility migration can leave legacy tests and sibling commands
  expecting fields that the new default intentionally excludes.
- A flag advertised as detail can be silently ignored by an earlier command
  branch, leaving a valid but misleading YAML response.
- A concise response that loses status, version transition, health, or the
  next operator step would be smaller but not operationally useful.

## Counterweight Pass

- The reviewers confirmed that summary projection is the right shape: preserve
  concise decision data, retain raw evidence in `--detail`, and do not impose
  blind byte clipping.
- The two concrete migration defects and one coverage gap were fixed before
  release; no speculative redesign remains.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/charness_cli/test_tool_lifecycle.py | action: fix | note: legacy full-payload lifecycle tests now invoke `--detail`, while summary tests retain the compact contract.
- F2 | bin: act-before-ship | evidence: strong | ref: charness | action: fix | note: `doctor --detail --next-action` is rejected as mutually exclusive so neither flag is silently ignored.
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/charness_cli/test_yaml_output_branch_coverage.py | action: fix | note: high-fanout handler coverage now proves summary routing and detail preservation.
- F4 | bin: over-worry | evidence: moderate | ref: charness | action: defer | note: arbitrary response byte limits would conceal data rather than address the raw execution-graph leak.

## Reviewer Tier Evidence

- Requested tier: high-leverage fresh-eye review.
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority.
- Host exposure state: metadata-hidden
- Application state: three reviewers completed; the host returned no applied-model metadata.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: root `charness` command handlers and their internal diagnostic payloads.
- Consumer: operators and agents reading root command stdout.
- Owning surface: root CLI output projection in `charness`.
- Verdict: owned-correctly
