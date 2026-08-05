# Issue #508 Resolution Critique
Date: 2026-08-05

## Decision Under Review

Repair the web-fetch login-wall classifier so incidental prose such as
`design intent` is not treated as a blocker, while preserving supported login
markers, blocker precedence, source/plugin parity, and gather persistence
boundaries.

## Execution

This proof-surface slice used the required two bounded fresh-eye code rounds.
Round 1 found missing marker-axis and matched-signal coverage plus an
implementation-packet evidence gap. Round 2 read the repaired surface and found
an over-broad repeated-separator regex and a packet metadata/binding mismatch.
The parent repaired the separator grammar, added negative fixtures, and created
the final current binding packet. The round-2 code repair is recorded as
accepted-unreviewed under the repository's two-round cap.

- Round 1: `issue-508-proof-round1`; reviewer delivery received; focused suite
  was 39 passed.
- Round 2: `issue-508-proof-round2`; reviewer delivery received; fingerprint
  verification was `parent-attributed` with only parent-declared paths after
  the parent applied the round-2 repair.
- Final packet: implementation paths are rebound after the separator repair;
  its reviewed-input identity is current.

## Fresh-Eye Satisfaction

parent-delegated — two bounded fresh-eye code rounds returned findings. Round 1
and round 2 were distinct reviewer contexts, and the parent verified the shared
worktree boundary for each; the round-2 repair itself is explicitly
accepted-unreviewed under the cap.

## Packet Consumed

- Packet path: `charness-artifacts/critique/2026-08-05-issue-508-implementation-final-binding-v2-packet.json`
- Packet SHA256: `d64c9b0f3d899a21e249f6ef2a38dd1e4c98210c0a6d9327ae3f1da7d52f97ca`
- Identity SHA256: `32fbf37be6174c2d86e58fc35a3ecc74ebf07ac959885c8ea96a1ecb61a3137b`

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-05-issue-508-implementation-final-binding-v2-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-05-issue-508-implementation-final-binding-v2-packet.json`
- Packet SHA256: `d64c9b0f3d899a21e249f6ef2a38dd1e4c98210c0a6d9327ae3f1da7d52f97ca`
- Identity SHA256: `32fbf37be6174c2d86e58fc35a3ecc74ebf07ac959885c8ea96a1ecb61a3137b`

## Capability Delivered

- The classifier now matches supported login markers against case-folded,
  normalized visible text with independently bounded tokens.
- A single hyphen or ordinary whitespace separates `sign in`/`log in`; repeated
  or spaced hyphens are not supported markers.
- Exact standalone `login` and `로그인` remain blockers; larger embedded tokens
  remain content-positive; markup-split visible markers remain blockers.
- Gather persists the corrected content fixture when explicitly requested and
  keeps genuine login blockers non-persistent.

## Findings and Counterweight

- F1 | bin: act-before-ship | evidence: strong | ref: skills/support/web-fetch/scripts/classify_fetch_response.py | action: fix | note: round 1 required visible-text matching and the full supported marker/matched-signal matrix; fixed with normalized matching and explicit fixtures
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_web_fetch_route_and_classify.py | action: fix | note: round 2 required log-in, embedded Korean, canonical matched signals, and repeated/spaced-hyphen negatives; fixed before final binding
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-08-05-issue-508-implementation-final-binding-packet.json | action: fix | note: the round-2 packet metadata had to be rebound after the final repair; final packet identity is current and JSON/Markdown section counts agree
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/test_web_fetch_support.py | action: document | note: keep explicit extracted persistence and genuine-blocker no-write coverage at the gather seam
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md | action: defer | note: page-level auth signals, provider vocabularies, browser fallback, and live/installed-host proof require a recorded recurrence or operator need
- F6 | bin: over-worry | evidence: moderate | ref: charness-artifacts/gather/2026-08-05-g15e-aop-and-css.md | action: defer | note: local control and fixture proof are sufficient for this bounded classifier repair; no live-source claim is made

Round-2 disposition: the single-delimiter regex repair and its negative fixtures
were applied after the second reviewer and are accepted-unreviewed as the
repository's explicit two-round cap permits. The final focused tests and parity
checks passed after that repair.

## Verification

- `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_support.py` — 39 passed.
- `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py -k token_aware_login_markers` — 1 passed, 18 deselected.
- Source/plugin classifier and public gather `cmp -s` checks — parity.
- `python3 scripts/validate_debug_artifact.py --repo-root .` — passed.
- `python3 scripts/plan_risk_interrupt.py --repo-root . --paths charness-artifacts/debug/latest.md charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md --detail` — `impl_status: allowed`.
- `git diff --check` — passed.

These are local source-tree and fixture proofs. They do not establish live URL
acquisition, installed-host behavior, provider roundtrip, remote CI, or
Cautilus behavior.

## Deliberately Not Doing

No page-level auth model, provider-specific corpus, browser or credentialed
route, gather route rewrite, public enum, or live-source claim is included.

## Boundary Ownership

- Producer: the source and plugin web-fetch classifier mirrors produce
  `login-wall` and `matched_signals`.
- Consumer: the public gather helper maps the classifier disposition to durable
  persistence or no-write behavior.
- Owning surface: classifier marker precision and precedence stay with the
  classifier; disposition-to-persistence stays with gather; parity is the
  packaging/export boundary.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewer.
- Requested spawn fields: `model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none`; unnamed one-shot reviewers.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden — the host returned two distinct completed finding payloads, but provider-side field application metadata was not independently exposed.
- Delivery state: findings-received

## Next Move

Run the repo quality/closeout gates and a separate closeout-claims review before
committing this slice. Keep the carrier local; no push is authorized until the
final publish boundary for the overall goal.
