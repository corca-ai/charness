# Critique Review
Date: 2026-07-09

## Decision Under Review

Autonomous quality repair after repo-wide bug/test-speed scan: A/B harness
validation and stream preservation, markdown-preview out-of-repo target
rejection, quality artifact update, plugin mirror sync, and raw stream retention
guard.

Packet Consumed: `charness-artifacts/critique/2026-07-09-131243-packet.md`

## Failure Angles

- Problem framing / diagnostic: initial A/B validation still allowed empty arms,
  unsafe config names, malformed arm entries, and raw CLI exceptions. These were
  fixed before closeout.
- Operational boundary: preserving `stream.jsonl` fixed scorer fallback but
  risked committing raw streams under `charness-artifacts/efficiency`; `.gitignore`
  now blocks preserved raw stream files while local fallback remains available.
- Target selection boundary: markdown preview rejected absolute outside paths
  but needed the same resolved-path guard for repo-relative symlinks and mixed
  globs. Both cases are now covered.

## Counterweight Pass

- Act Before Ship: retention guard for raw preserved streams; fixed with
  `.gitignore` plus a regression assertion.
- Bundle Anyway: malformed arm entries should emit validation errors instead of
  raw exceptions; fixed in `_validate_run_spec`.
- Over-Worry: plugin mirror drift and quality artifact concealment did not
  remain after sync and artifact validation.
- Valid but Defer: broader A/B schema and privacy/retention policy is real, but
  this slice closes the concrete path-material, empty-evidence, and raw-stream
  commit-risk cases.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_skill_efficiency_ab.py:313 | action: fix | note: raw stream preservation needed a commit-retention guard; fixed by ignoring preserved efficiency stream.jsonl files
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run_skill_efficiency_ab.py:73 | action: fix | note: empty arms, unsafe config names, and malformed arm entries now fail before capture spend
- F3 | bin: act-before-ship | evidence: strong | ref: skills/support/markdown-preview/scripts/markdown_preview_lib.py:148 | action: fix | note: absolute and symlink-resolved out-of-repo markdown targets are rejected before rendering
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/run_skill_efficiency_ab.py:279 | action: defer | note: broader A/B schema validation remains outside this slice

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: subagent tool accepted spawn fields; provider application not independently confirmed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: A/B harness and markdown-preview target selection.
- Consumer: scorer fallback, committed efficiency artifacts, markdown-preview renderer, and operator CLI.
- Owning surface: producer-side validation and artifact-retention policy own the fix.
- Verdict: owned-correctly
