# Critique Review
Date: 2026-07-09

## Decision Under Review

Markdown-preview support CLI help repair: add useful argparse help text for all
`render_markdown_preview.py` options in the source support skill and exported
plugin mirror, plus a focused help-output regression test.

Packet Consumed: `charness-artifacts/critique/2026-07-09-142102-packet.md`

## Failure Angles

- Operator-facing CLI help: help text could exist but misdescribe behavior.
- Generated/export sync: source support skill and plugin mirror must stay in
  sync, with packaging proof rather than a duplicate plugin behavior test.
- Scope control: the repo still has broader argparse help debt, but this slice
  should close the markdown-preview support capability only.

## Counterweight Pass

- Act Before Ship: the initial `--changed-only` wording was wrong because it
  filtered selected targets, not only globbed targets; fixed before closeout.
- Bundle Anyway: `--artifact-dir` now says repo-relative, and `--backend` names
  the currently supported `glow` backend.
- Over-Worry: exact argparse wrapping snapshots and plugin-mirror help behavior
  tests would add maintenance cost without proving a distinct branch.
- Valid but Defer: the remaining 81 argparse help findings belong to later
  standalone slices.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/support/markdown-preview/scripts/render_markdown_preview.py:40 | action: fix | note: `--changed-only` help had to describe selected Markdown targets, not only globbed targets
- F2 | bin: bundle-anyway | evidence: moderate | ref: skills/support/markdown-preview/scripts/render_markdown_preview.py:38 | action: fix | note: `--artifact-dir` and `--backend` help were clarified while touching the same CLI surface
- F3 | bin: over-worry | evidence: moderate | ref: tests/test_markdown_preview_support.py:67 | action: document | note: normalized snippet assertions prove useful help without pinning argparse wrapping
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/inventory_skill_ergonomics.py | action: defer | note: broader argparse help debt remains real but outside this markdown-preview slice

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host accepted angle reviewers and counterweight reviewer.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: markdown-preview support skill CLI source and generated plugin export.
- Consumer: operators and agents invoking `render_markdown_preview.py --help`.
- Owning surface: support skill package plus checked-in plugin export.
- Verdict: owned-correctly
