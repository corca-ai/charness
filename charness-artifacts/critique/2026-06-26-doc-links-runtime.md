# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts most `check_doc_links.py` subprocess
tests to in-process `main()` calls while retaining representative CLI smokes.

## Failure Angles

- Boundary proof: converting all calls would erase proof that the script boots
  through the real entrypoint.
- Argument proof: `--require-git-file-listing` uses a distinct repo-file
  listing path and should retain real subprocess evidence.
- Error wrapper fidelity: in-process failure tests must mimic the script's
  `ValidationError` catch and stderr rendering.
- Value: because this validator runs in pre-commit, weakening its delivery
  boundary would be costly despite the runtime savings.

## Counterweight Pass

- Real subprocess checks remain for one failure, one success, and the git-file
  listing mode.
- The in-process helper catches `ValidationError`, prints to stderr, and returns
  code `1`, matching the script's `__main__` wrapper.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.
- The converted cases are individual rule fixtures, not unique CLI modes.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_check_doc_links.py | action: fix | note: duplicate check_doc_links subprocess calls dropped from 18 to 3 while retaining representative CLI smokes
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_check_doc_links.py | action: defer | note: leave remaining subprocess calls intact because they cover script bootstrap, normal success, and require-git-file-listing mode

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_context=true, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: reviewer completed and returned no blocking findings;
  `--require-git-file-listing` caveat fixed before commit

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f017a-9b2e-74b0-8f58-7603a89697c2`
completed through `multi_agent_v1.spawn_agent`; it found no blocking issue and
its caveat led to an explicit retained `--require-git-file-listing` subprocess
smoke.
