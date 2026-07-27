# Publish gate D1 D2 D3 D5
Date: 2026-07-27

## Decision Under Review

Fixing D1, D2, D3 and D5 from the evidence-surface bug hunt — the publish-gate
family. D1: a suffixed `## Release State` heading disabled the whole five-entry
ledger check while the audit reported `passed`. D2: the mutable-pointer rule was
exactly inverted, blocking the pinned link and passing `main`. D3: the same-proxy
guard was a positional prefix match defeated by flag order, wrappers, and
absolute paths. D5: the release-version cross-check silently no-opped on a
reformatted claim, and a decoy first match shadowed the real one. All four gate
release publish — an irreversible boundary.

## Failure Angles

- **The fix reproduces the defect it fixes.** Every one of these is "a check
  reports a verdict over a scope it did not establish". A fix that adds a new
  reader without asking what that reader cannot see re-enacts the class. Bit
  hardest: the D1 fix was fence-blind, so a fenced *example* ledger satisfied all
  five checks over an empty real one — a false PASS at publish.
- **Tightening a portable rule over-reaches into a repo it does not own.** D2's
  path literal was repo-specific; removing it for portability made the rule fire
  on third-party links whose remediation is impossible.
- **A guard biased to flag becomes a guard that is disabled.** D3's subset
  matching is deliberately over-inclusive; pushed too far it refuses legitimate
  probes and the operator routes around it.
- **A stricter validator turns correct state into a false alarm.** D5's claim
  patterns nest; capturing markup residue reports a current pointer as stale.
- **A number that reports a status it cannot support.** The handoff said "20
  remain" by folding PARTIAL rows in as landed — the same class, in the tracking
  record itself.

## Counterweight Pass

- Real blockers, all found by the two bounded reviewers and all fixed here: the
  fenced-ledger false PASS, the third-party-link over-block, four surviving D3
  bypasses (unparseable-command fail-open, wrapper+absolute-path composition, tag
  omission, budget exhaustion), the degenerate-template over-flag, D5's markup
  residue and placeholder mis-diagnosis, and the contradictory blocker pair.
- Deliberately accepted, stated not hidden: a branch NAMED like a version passes
  `_IMMUTABLE_REF_RE`, and a tag can be moved with `git tag -f`. Neither is
  decidable from a ref string, so the rule is "version-shaped or sha-shaped", not
  "provably immutable".
- Deliberately deferred with the row left PARTIAL: D2's notes audit still never
  runs on the `--generate-notes` default path. Closing it needs a post-create
  readback of the published body, which belongs with D4/D6/D8 rather than being
  bolted on here.
- Over-worry: that D3's flag bias would eat real probes. Measured — `curl`,
  `git ls-remote`, `gh api`, `gh release download` and a custom script all pass,
  while eleven same-proxy disguises are refused.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/audit_public_release_narrative.py:41 | action: fix | note: the D1 fix reproduced D1 — `_release_state_block` takes the first matching heading and was fence-blind, so a fenced example ledger satisfied all five entry checks over an empty real section; both audits now read fence-stripped text
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:214 | action: fix | note: an unparseable probe command failed OPEN, so one apostrophe inside a `#` comment ran the identical same-proxy query under bash while the guard reported distinct; unparseable and budget-exhausted both fail closed now
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:150 | action: fix | note: only the first token was basename-normalized, so `sudo /usr/bin/gh release view` escaped although each half alone was caught; and omitting the tag escaped, where `gh release view` with no tag resolves to the latest release — moments after publish, the one being confirmed
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/audit_public_release_narrative.py:103 | action: fix | note: dropping the repo-specific path literal made the mutable-ref rule fire on third-party links whose remediation ("pin to the release tag") is impossible; fence-stripping resolves the real case and the ref pattern no longer over-blocks short shas, `v1.0`, or the `refs/tags/` raw form
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/validate_current_pointer_freshness.py:68 | action: fix | note: the three claim renderings nest, so `**\`2.11.3\`**` compared backticks-and-all and reported a current pointer as stale; a placeholder value was compared as if it were a version, diagnosing the wrong problem
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:190 | action: fix | note: a degenerate `release_view` template made the guard refuse `gh api` or pass everything; it now declines to render a verdict it cannot establish and records `same_proxy_guard: inconclusive-...` so absence is not read as a passed check
- F7 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md:18 | action: fix | note: the backlog said "20 remain" by counting PARTIAL rows as landed; corrected to 23 OPEN + 5 PARTIAL with the counting rule stated, since a tracking number that overstates status is the defect class this hunt exists to find
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/audit_public_release_narrative.py:170 | action: defer | note: the notes audit never runs on `--generate-notes`, the default publish path, whose bodies are commit messages and PR text; D2 stays PARTIAL and this lands with the D4/D6/D8 readback slice
- F9 | bin: over-worry | evidence: contested | ref: skills/public/release/scripts/audit_public_release_narrative.py:115 | action: document | note: a branch named `1.0.0` passes as immutable and a tag can be moved; neither is decidable from a ref string, so the constant's docstring states the rule as version-shaped-or-sha-shaped rather than implying provable immutability

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only agent), two independent spawns split by defect pair.
- Requested spawn fields: subagent_type=bounded-reviewer, per-pair scope prompt naming adversarial angles in both directions (over-block and under-block), no host addressing name, session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: Claude Code accepted both `bounded-reviewer` spawns and returned findings inline; `reviewer_boundary_fingerprint.py verify` reported `ok: true` with `drift: []` across window `w-20260727T221606Z-2819378`.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — two bounded read-only reviewers ran in separate agent
contexts. Both flagged that they had no shell and named the exact commands they
needed run; the parent ran every one and reproduced all ten findings by execution
before folding, rather than accepting them on reasoning.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: the release narrative audit, the distinct-channel same-proxy guard, and the current-pointer freshness validator — three independent readers of release state.
- Consumer: `publish_release_cli.run_narrative_audit` and the publish path that treats their verdicts as clearance to create a GitHub release.
- Owning surface: the reader that renders the verdict, not the caller — every defect here was a reader asserting over text it had not established, and per-caller patches would have left the other readers live.
- Verdict: owned-correctly
