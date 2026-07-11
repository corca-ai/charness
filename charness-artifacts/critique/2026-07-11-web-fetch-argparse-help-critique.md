# Critique Review — Web Fetch Argparse Help

Date: 2026-07-11

## Decision Under Review

Clear all 18 missing-help findings in the cohesive web-fetch route, acquire,
and classify CLI package without changing parser or runtime behavior.

## Failure Angles

- Semantic accuracy: help must describe browser, collect, and selected-content
  behavior without promising broader behavior.
- Test fidelity: option names in the usage line must not create false-green
  proof that their descriptions exist or are paired correctly.
- Counterweight: avoid parser factories, full snapshots, new floors, or a
  repo-wide sweep for a help-only package.

## Counterweight Pass

- Browser/collect/selected-content wording was tightened to actual fallback
  behavior.
- The first test revision was too weak; final assertions slice each option's
  argparse help block and bind it to a distinctive fragment.
- Parser-metadata tests and a generic argparse parser are over-worry because the
  production diff changes only `help=` values.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/acquire_public_url.py | action: fix | note: clarify that browser `always` still runs only when fallback remains needed, collect enables network-recon fallback, and selected content requires a successful selected attempt.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_web_fetch_help.py | action: fix | note: bind every one of the 18 option rows to its own help fragment so usage-only or swapped descriptions fail.
- F3 | bin: over-worry | evidence: strong | ref: tests/test_web_fetch_help.py | action: defer | note: whole-output snapshots and parser factories add brittleness without protecting this help-only diff.
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-07-11-web-fetch-argparse-help.md | action: defer | note: the remaining 62 findings require separate owner-level package triage.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded quality/code review.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`,
  `service_tier=priority`; implementation used a lower-power worker.
- Host exposure state: requested_fields_sent
- Application state: host returned independent selection, semantic,
  test-fidelity, and counterweight payloads; provider-side application metadata
  was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated — independent reviewers changed both wording and test design;
the final counterweight approved the corrected option-scoped proof.

## Boundary Ownership

- Producer: each argparse parser produces its option contract and help text.
- Consumer: operators and agents invoking the three web-fetch CLIs consume it.
- Owning surface: each support-owned script owns its flag description; focused
  tests own readback without introducing a shared parser abstraction.
- Verdict: single-surface
