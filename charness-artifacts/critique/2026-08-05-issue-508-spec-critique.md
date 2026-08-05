# Issue #508 Pre-Implementation Spec Critique
Date: 2026-08-05

## Decision Under Review

Repair the gather classifier's false `login-wall` verdict for readable content
containing the incidental substring `design intent`, while preserving genuine
login-marker blocking and the gather writer's no-persistence behavior for real
blockers.

## Execution

Executed as a delegated pre-implementation critique with three independent
angle reviewers and a separate counterweight reviewer. All four reviewers were
unnamed, one-shot, read-only shared-worktree reviews. The parent verified clean
boundary fingerprints after each review:

- Minto: `issue-508-spec-minto`, clean.
- Jackson: `issue-508-spec-jackson`, clean.
- Weinberg: `issue-508-spec-weinberg`, clean.
- Counterweight: `issue-508-spec-counterweight`, clean.

The first packet exposed the unresolved contract; the parent applied the
required repairs, refreshed the final binding packet, and re-ran the risk
interrupt planner. The planner now records `chosen_next_step: impl` and
`impl_status: allowed`. The reviewers' findings are not represented as a claim
that they re-read the repaired packet; the refreshed packet is the current
binding for the repaired contract.

## Fresh-Eye Satisfaction

parent-delegated — all four fresh-eye reviews returned findings; the parent
verified each shared-worktree boundary independently before applying repairs.

## Packet Consumed

- Packet path: `charness-artifacts/critique/2026-08-05-issue-508-spec-closeout-binding-v2-packet.json`
- Packet SHA256: `415ecc4d35b708249c8d92463066a68f3c30ddd88bde95653d80a874a144738f`
- Identity SHA256: `9ed8534300ae6bc554b0bef96df368e59ecc2812ac7b124aad6807e9a1f108b9`
- Initial reviewer packet: `charness-artifacts/critique/2026-08-05-issue-508-spec-packet.json`
  (`ec17a661a762e828e9009fdce51a7efb3ae546ac959541fc219b72b571ec1b51`,
  identity `f7656539299e8b4cc83ee4816d44310fba813aac0f861a4efde0907fb2811bfe`).

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-05-issue-508-spec-closeout-binding-v2-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-05-issue-508-spec-closeout-binding-v2-packet.json`
- Packet SHA256: `415ecc4d35b708249c8d92463066a68f3c30ddd88bde95653d80a874a144738f`
- Identity SHA256: `9ed8534300ae6bc554b0bef96df368e59ecc2812ac7b124aad6807e9a1f108b9`

## Failure Angles

- The proposed boundary fix could still overclaim that a lexical marker proves
  a real authentication wall.
- Matching against raw HTML could miss markup-split visible markers or preserve
  false positives from attributes and incidental source text.
- The source classifier and shipped plugin mirror could diverge.
- A classifier-only green test could leave the gather persistence/no-write seam
  unproven.
- A narrow English repair could silently drop supported markers, precedence, or
  Korean exact-marker behavior.

## Findings

The initial review found four act-before-ship gaps: the auth-boundary claim was
too broad; the plugin classifier mirror was incorrectly described as absent;
the matcher input and markup-split behavior were unspecified; and persistence
checks lacked an explicit `--persist-extracted-content` success assertion plus
a genuine-blocker no-write assertion. The counterweight also required the
complete marker matrix and concrete reopen triggers for deferred decisions.

## Counterweight Pass

- Act Before Ship: fixed — the contract now calls this a bounded login-marker
  precision heuristic, specifies case-folded normalized visible-text matching,
  names the actual plugin mirror, and requires source/plugin parity.
- Act Before Ship: fixed — the matrix covers `design intent`, title prose,
  `Sign in`, `Please log in`, `sign-in`, `login`, exact `로그인`, larger-token
  negatives, and a markup-split visible marker.
- Act Before Ship: fixed — the seeded gather check must request extracted
  persistence, assert the former false-positive phrase in the written record,
  and assert the genuine login fixture writes no record or latest pointer.
- Bundle Anyway: retained — blocker precedence and the existing gather route
  boundary stay in the same focused slice.
- Valid but Defer: page-level auth signals, provider-specific vocabularies,
  browser fallback, and live/installed-host roundtrips remain deferred with
  explicit recorded-response or operator-need reopen triggers.
- Over-Worry: no live acquisition claim is needed; the two named URLs remain
  route-blocked evidence supplied by the issue, while the local control capture
  remains the durable public-source record.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md:15-25 | action: fix | note: narrow the claim from actual authentication-boundary proof to supported bounded-marker precision; repaired in the contract and debug invariant
- F2 | bin: act-before-ship | evidence: strong | ref: plugins/charness/support/web-fetch/scripts/classify_fetch_response.py | action: fix | note: the shipped plugin mirror exists and must be changed and parity-checked with the source classifier
- F3 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/classify_fetch_response.py | action: fix | note: match case-folded normalized visible text and include markup-split `Sign <span>in</span>` coverage
- F4 | bin: act-before-ship | evidence: strong | ref: tests/test_web_fetch_support.py | action: fix | note: require explicit extracted persistence for content and no record write for the genuine blocker
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md:51-62 | action: document | note: keep the complete marker matrix and blocker precedence in this first slice
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md:64-73 | action: defer | note: reopen page-level/provider/browser expansion only on a recorded recurrence or operator need
- F7 | bin: over-worry | evidence: moderate | ref: charness-artifacts/gather/2026-08-05-g15e-aop-and-css.md | action: defer | note: do not expand this local classifier repair into live provider acquisition or a broad page-quality corpus

## Coherence and Acceptance Coverage

- Initial coherence result: FAIL. The first contract overclaimed semantic auth
  truth, misdescribed the plugin mirror, and left matcher-input and persistence
  probes underspecified.
- Repaired coherence result: PASS. The producer/consumer seam, bounded claim,
  implementation owner, and non-claims now agree.
- Initial acceptance coverage result: FAIL. It lacked an explicit complete
  marker matrix, markup-split visible text, and durable persistence/no-write
  assertions.
- Repaired acceptance coverage result: PASS. The contract names runnable
  pytest selections, source/plugin `cmp`, debug/risk validators, and the exact
  seeded gather observations required for the slice.

## Deliberately Not Doing

No page-level authentication model, provider-specific corpus, browser or
credentialed route, live-host proof, Cautilus evaluation, public enum, or gather
route/persistence rewrite is included.

## Boundary Ownership

- Producer: `skills/support/web-fetch/scripts/classify_fetch_response.py` and
  its shipped plugin mirror produce the classifier status and matched signals.
- Consumer: `skills/public/gather/scripts/gather_public_url.py` consumes that
  status to choose persistence or no-write behavior.
- Owning surface: the classifier owns login-marker precision and precedence;
  gather owns disposition-to-persistence mapping; parity is an export contract.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewer.
- Requested spawn fields: `model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none`; one unnamed one-shot reviewer per angle.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden — the host returned four distinct completed finding payloads, but provider-side field application metadata was not independently exposed.
- Delivery state: findings-received

## Next Move

Run the implementation slice against the allowed contract, then execute focused
classifier/gather proof, source/plugin parity, changed-line mutation coverage,
and the required closeout critique before committing. Keep the commit local;
the only push remains the final publish boundary for the overall goal.
