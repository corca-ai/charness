# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts three `check_goal_artifact.py`
complete-evidence subprocess tests to in-process `main()` calls.

## Failure Angles

- Boundary proof: `check_goal_artifact.py` is a closeout gate, so eliminating
  subprocess evidence too aggressively could hide script bootstrap failures.
- CLI modes: `--pursue-ready`, missing path handling, and default checking have
  distinct return-code contracts.
- Complete-state closeout: complete-goal evidence failures are high-value
  behavior and need at least one real subprocess proof in the repo.
- Isolation: monkeypatched `sys.argv` and captured stdout could leak between
  tests if not pytest-scoped.

## Counterweight Pass

- The converted tests still call `main()`, so argparse, JSON stdout, and return
  code behavior remain covered without process startup.
- Real subprocess checks remain for default checking, `--pursue-ready`, and
  missing-path usage/error behavior.
- Repo-level complete-state subprocess coverage remains in
  `tests/quality_gates/test_goal_artifact_lib.py`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_goal_head_freshness.py | action: fix | note: duplicate check_goal_artifact subprocess calls dropped from 7 to 4 while retaining representative CLI modes
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_goal_head_freshness.py | action: defer | note: leave remaining subprocess calls intact because they prove distinct CLI return-code boundaries

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_context=true, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: reviewer completed and returned no blocking findings

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f0176-baa4-7553-b5bb-8900cc793d74`
completed through `multi_agent_v1.spawn_agent`; it found no blocking issue and
identified the retained CLI subprocess paths plus the file-local complete-state
caveat.
