# Critique Review
Date: 2026-07-22

## Decision Under Review

Resolve #450 by treating only `.specdown` and `specdown.json` as Specdown
runtime markers. A prose-only `*.spec.md` document must not add
`specdown-quality` during quality-adapter bootstrap.

## Failure Angles

- Problem framing: the narrow detector change could leave the reported
  prose-document bootstrap mutation intact or accidentally remove valid runtime
  detection.
- Diagnostic and ownership: the change could fix the source copy while leaving
  the checked-in plugin export stale, or incorrectly move a classifier concern
  into adapter-lineage merging.
- Counterweight: a generic negative-lineage policy or new positive-marker test
  could enlarge the slice without evidence that either is needed.

## Counterweight Pass

- Act Before Ship: none. The first review found the generated plugin stale and
  a weak retained-lineage assertion; both are now repaired in the final diff.
- Bundle Anyway: none after the final reviewers confirmed source/export parity
  and the bootstrap idempotence fixture.
- Over-Worry: a generic explicit-negative lineage mechanism is not justified;
  the actual false positive was a prose glob in the detector. A separate
  `specdown.json` test is not required because that direct, unchanged positive
  branch is outside this diff.
- Valid but Defer: none.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/quality_bootstrap_detect.py | action: fix | note: synchronized the checked-in plugin export before final review
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap.py | action: fix | note: assert retained `python-quality` lineage in the prose-only bootstrap fixture
- F3 | bin: over-worry | evidence: strong | ref: scripts/quality_bootstrap_lib.py | action: defer | note: do not introduce a generic negative-lineage mechanism for an unproven broader class
- F4 | bin: over-worry | evidence: moderate | ref: scripts/quality_bootstrap_detect.py | action: defer | note: unchanged `specdown.json` positive detection does not need a new slice-local test

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`,
  `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: the host accepted the requested spawn fields; no provider
  application metadata was exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.json
- Packet SHA256: 9ed808f7d58294d98291b8e82e499d4e1433fea9081852168dc6b857b1626314
- Identity SHA256: 0540e7f1d08f6e724bbafb389dd72edcd88690d7638f4e6f1effc27dd96cbe36

## Boundary Ownership

- Producer: `detect_preset_lineage` supplies inferred preset lineage.
- Consumer: `build_bootstrap_state` writes the quality adapter, while the
  checked-in plugin export serves installed consumers.
- Owning surface: the root detector plus its generated plugin mirror.
- Verdict: owned-correctly

## Deliberately Not Doing

- No generic explicit-negative lineage syntax.
- No change to accepted `.specdown` or `specdown.json` runtime markers.
