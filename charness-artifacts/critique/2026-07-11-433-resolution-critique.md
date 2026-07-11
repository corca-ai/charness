# Issue #433 Release Closeout Carrier Resolution Critique
Date: 2026-07-11

## Decision Under Review

Make the release helper transport a complete issue-owned closeout carrier,
validate the exact final commit before expensive quality or mutation, and reuse
the validated message for normal and resumed publication.

## Failure Angles

- Problem framing (Jackson): the normal path met the reporter's JTBD, but the
  first review found the parallel `--resume --close-issue` path had not received
  the new carrier/classification inputs.
- Diagnostic ownership (Weinberg): direct draft validation covered requested
  issue numbers while the commit-msg consumer scans every close keyword, so an
  extra carrier reference could still fail late.
- Operational recovery (Gawande/Raskin): resume initially validated a newly
  reconstructed draft rather than the already-tagged `HEAD` body it would push.
- Test economics (quality review): behavior-floor, draft-validator,
  commit-msg, and seeded-publish tests overlap in data but prove distinct
  boundaries; broad fixture or worker-count cleanup would be scope inflation.

## Counterweight Pass

- Act before ship: forward carrier/classification on resume, validate the exact
  existing `HEAD` body before quality/push, and reject close-keyword numbers not
  in the requested issue set. All three were implemented and focused tests pass.
- Bundle anyway: retain the synthetic carrier fixture for legacy release tests,
  but add explicit missing/invalid carrier and resume regressions so injection
  cannot hide the new contract.
- Over-worry: do not redesign source/installed dynamic loading; the two layouts
  have direct portability coverage and typed absence handling.
- Valid but defer: release still recognizes the issue-owned classification
  vocabulary at its CLI/transport boundary. Move that parser to an issue-owned
  shared helper only if the classification set changes or another drift appears.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py | action: fix | note: resume now forwards carrier inputs and validates the actual HEAD carrier before quality or push
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout_message.py | action: fix | note: exact carrier validation now rejects unintended close-keyword issue numbers through the issue-owned scanner
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_release_publish_resilience.py | action: fix | note: focused complete, thin, and extra-close resume fixtures preserve recovery behavior
- F4 | bin: over-worry | evidence: contested | ref: tests/quality_gates/test_release_issue_closeout_behavioral_floor.py | action: document | note: keep the bounded source and installed module-loader design with direct portability proof
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/release_issue_closeout_message.py | action: defer | note: share classification parsing only after a real vocabulary-change or recurrence trigger

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: application not claimed; the host exposed submission but no provider-application signal

## Fresh-Eye Satisfaction

parent-delegated — three distinct angle reviewers plus one separate
counterweight completed in fresh contexts; parent fingerprint verification
reported no worktree or index drift after every review.

## Boundary Ownership

- Producer: release helper commit-message assembler and resume transport.
- Consumer: commit-msg closeout gate backed by the issue verifier.
- Owning surface: issue-owned closeout validity; release-owned transport and early proof.
- Verdict: moved-to-owner

## Packet Consumed

`charness-artifacts/critique/2026-07-11-041729-packet.md`

## Verification

- Focused release, resume, issue-validator, and commit-msg regression set:
  `72 passed in 22.55s`.
- Non-claims: no live release, push, issue close, provider roundtrip, installed
  plugin execution, broad pytest closeout, or Cautilus evaluation ran.
