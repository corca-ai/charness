# YouTube gather and adapter renderer closeout critique
Date: 2026-06-11

## Decision Under Review

Lock the combined goal diff for #352 YouTube gather support and #353
adapter-lib renderer hygiene: new YouTube web-fetch acquisition, gather
artifact rendering, adapter YAML subset fixes, quality-bootstrap falsy
preservation, plugin exports, debug/gather/goal artifacts, and tests.

## Failure Angles

- Problem fit (Michael Jackson): the diff could solve only the convenient
  generic media route and still leave YouTube artifacts ambiguous.
- Diagnostic fit (Gerald Weinberg): the adapter fix could patch symptoms while
  still allowing lossy unsupported YAML rewrites; YouTube identity could be
  computed from a different attempt than the selected evidence.
- Operational fit (Atul Gawande): generated/plugin mirrors and durable
  artifacts could be stale or make stronger proof claims than the local runtime
  actually produced.

## Counterweight Pass

- Real blockers folded before closeout: block-scalar headers restricted to the
  supported subset; quality adapter glob quoted; YouTube source identity now
  follows `selected_attempt`; debug artifact updated to match limited
  block-scalar support; goal artifact will carry the final validator matrix.
- Cheap bundle folds: YouTube unavailable records now render video id and
  reason without labeling them transcript/metadata-backed; tests pin
  metadata-only persistence as non-extracted.
- Over-worry rejected: authenticated/browser-profile proof and installed
  `yt-dlp` live transcript proof remain out of scope; the local unavailable
  artifact is honest.
- Valid but deferred: malformed `json3` caption recovery and live installed
  `yt-dlp` proof can be follow-up work, but neither blocks this local
  implementation.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/adapter_lib.py | action: fix | note: Block scalar headers accepted every `|`/`>` prefix; folded by rejecting unsupported modifiers and testing `|+`.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/adapter.example.yaml | action: fix | note: Unquoted `*-quality-gate.sh` looked like an alias under the new refusal boundary; folded by quoting the glob and syncing plugin export.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/youtube_source.py | action: fix | note: YouTube source identity could disagree with the selected attempt; folded by deriving identity from `selected_attempt` and adding direct-strong-plus-metadata regression.
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/latest.md | action: fix | note: Debug artifact still claimed block scalars were refused; folded to state limited block-scalar support and alias/tag/modifier refusal.
- F5 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md | action: fix | note: Final validator matrix needed durable binding; goal closeout will record exact commands and results before completion.
- F6 | bin: bundle-anyway | evidence: moderate | ref: skills/public/gather/scripts/gather_public_url.py | action: fix | note: Blocked/unavailable YouTube records lacked rendered video id/reason details; folded without claiming transcript or metadata source type.
- F7 | bin: over-worry | evidence: strong | ref: charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md | action: document | note: No authenticated/browser YouTube proof is required; local proof honestly records captcha plus missing `yt-dlp`.
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/support/web-fetch/scripts/youtube_source.py | action: defer | note: Malformed `json3` caption handling can be improved later; current slice already proves transcript, metadata-only, blocked, unavailable, and selector honesty paths.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage bounded fresh-eye reviewers for code critique.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium,
  service_tier=priority, agent_type=default; packet
  `charness-artifacts/critique/2026-06-11-023045-packet.md` consumed.
- Host exposure state: applied
- Application state: host-confirmed: spawn tool returned three completed
  reviewer results (`019eb485-d154-7fe2-a675-13ff94949231`,
  `019eb485-f853-7121-9a78-90d8fa56f1f2`,
  `019eb486-3b91-7563-b3c4-bee681ba59a8`) with concrete file/line findings.

## Fresh-Eye Satisfaction

Fresh-eye satisfaction: parent-delegated. Three bounded reviewers completed
problem-framing, diagnostic, and operational angles. All Act Before Ship
findings were folded into the diff before final validation. Remaining concerns
are explicitly over-worry or valid-but-defer per Structured Findings.
