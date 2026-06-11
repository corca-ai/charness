# Critique Review
Date: 2026-06-11

## Decision Under Review

Land the YouTube route-owned `youtube-browser-transcript-ui` fallback and the
`issue_tool.py read` comments-read requirement, including synced plugin mirrors
and focused regression tests.

## Failure Angles

- Michael Jackson / problem framing: weak direct YouTube HTML could satisfy the
  generic classifier and bypass the transcript UI fallback, solving adjacent
  "fetch any text" instead of the named transcript problem.
- Gerald Weinberg / diagnostic: UI metadata-only or failed UI attempts could
  mask the earlier `yt-dlp` captcha/error signal unless only transcript success
  is selectable.
- Atul Gawande / operational: runtime cleanup order and missing-comments failure
  needed direct tests so the new helper path did not silently leak processes or
  allow skipped issue comments.

## Counterweight Pass

- Act-before-ship findings were real and fixed in the slice: weak direct success
  no longer preempts YouTube UI transcript extraction, non-transcript UI outcomes
  are diagnostic, cleanup order/failure is tested, missing comments fail closed,
  and repeated transcript segments are preserved.
- The untracked-file concern is handled by normal staging plus the plugin mirror
  drift gate.
- A future gate that audits resolution artifacts for a recorded
  `comments_read: true` payload is valid but deferred; it is a broader issue
  workflow proof contract than this helper/script change.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_youtube_source.py | action: fix | note: added regressions for weak direct success, captcha masking, cleanup order/failure, and repeated transcript segments.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_read.py | action: fix | note: added negative coverage proving `issue_tool.py read` fails when backend JSON omits comments.
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/SKILL.md | action: defer | note: future issue-resolution artifacts could record a consumed read payload, but the current slice only adds the required helper and instruction path.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted parent-spawn requests and returned completed reviewer notifications for all angle/counterweight reviewers.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Angle reviewers returned concrete
pre-ship findings; parent applied the required fixes and the separate
counterweight reviewer reported no remaining act-before-ship item.
