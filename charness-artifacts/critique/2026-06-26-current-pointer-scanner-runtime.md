# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship a local-only cleanup that converts seven repeated current-pointer scanner
fixtures to in-process `SCANNER.main()` calls.

## Failure Angles

- CLI output proof: converting every scanner fixture would remove command proof
  for text and JSON output modes.
- HITL coupling: bootstrap/sync subprocesses are cross-tool runtime proof, not
  ordinary scanner fixtures.
- Git-visible fidelity: converted tests must still exercise the scanner's git
  file-listing path under the fixture repos.

## Counterweight Pass

- Text output and JSON output scanner tests remain real subprocesses.
- HITL bootstrap and sync remain real subprocesses.
- Converted fixtures still drive argparse and git-backed fixture repos through
  `SCANNER.main()`.
- Focused pytest, ruff, and boundary-bypass ratchet passed after conversion.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_current_pointer_writes.py | action: fix | note: run_script calls dropped from 11 to 4 while retaining text/JSON scanner and HITL subprocess proof
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_current_pointer_writes.py | action: defer | note: keep remaining subprocesses as scanner output and HITL command-boundary proof

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent deterministic critique only

## Fresh-Eye Satisfaction

not spawned: this scanner conversion retained text/JSON scanner subprocess
proof, retained HITL bootstrap/sync subprocess proof, and passed deterministic
focused proof.
