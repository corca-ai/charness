# Fresh-eye closeout review: #585, #596, and #598

Date: 2026-08-12
Reviewer context: bounded fresh-eye reviewer, parent-delegated, read-only
scope. The parent-side boundary receipt was `parent-attributed`: the only
recorded drift was the parent creating the new active-goal artifact while the
reviewer ran; no reviewer mutation is claimed.

## Inputs

- GitHub issue reads, including comments, for #585, #596, and #598.
- Current `main` at `1c1acd90cb45f4e8fa9f7b1159caca82520c3423` and released
  tag `v5.0.0`.
- `27d1c959` / `a52f83e9` and the R6 critique for #585.
- `c553aac9` and the R596 critique for #596.
- `45415116` / `a52f63c7` and the six-rulings record for #598.

## Failure Angles

- Stale-tracker angle: an earlier GitHub comment could be mistaken for the
  current tree, so each claimed commit was checked as an ancestor of current
  `main` and `v5.0.0`.
- Boundary angle: `CLOSED` and a carrier pass prove tracker lifecycle only, so
  every close comment also names a behavior channel and local/hosted limits.

## Counterweight Pass

- The stale "Nothing executed yet" comments are not a blocker: they predate the
  commits and the released tag. The missing #598 release-note detail remains a
  valid communication debt, but not an unmet functional acceptance.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: `27d1c959`, `c553aac9`, `45415116`, `a52f63c7` | action: document | note: close each already-shipped issue with an issue-bound manual carrier and explicit local-only behavior disposition.
- F2 | bin: valid-but-defer | evidence: strong | ref: `charness-artifacts/release/2026-08-12-v5.0.0-notes.md` | action: defer | note: #598's removal is absent from the release notes; keep that communication debt explicit rather than treating it as repaired.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: n/a — the one-shot host spawn inherited the session defaults and returned no applied-tier metadata.
- Host exposure state: host-defaulted
- Application state: n/a — the host returned no provider application metadata.
- Delivery state: findings-received.

## Disposition

### #585 — close as bug

JTBD: avoid false boundary-bypass identity rotation for a pure path move while
keeping content, membership, and multiplicity detection.

`27d1c959` re-keyed the identity to versioned normalized call-site content and
`a52f83e9` repaired the remaining proof gaps. The R6 critique records both
required review rounds and focused payload/validator/ratchet evidence. The
reviewer found no unmet issue acceptance. Distinct behavioral evidence is the
local path/content/membership/multiplicity proof and released `v5.0.0`, not the
tracker state. No hosted CI or consumer-repository observation is established.

### #596 — close as bug

JTBD: remove mutable equality-pin re-record tax while retaining a trustworthy
D47 measurement record.

`c553aac9` records a dated SHA-256 snapshot and changes the pins to provenance,
headline, and invariant checks. The R596 critique records two review rounds.
The reviewer found no unmet issue acceptance. Distinct behavioral evidence is
the local snapshot/provenance/invariant proof and released `v5.0.0`, not the
tracker state. No live-corpus, hosted CI, or consumer observation is claimed.

### #598 — close as feature

JTBD: replace the hand-curated word-preference check without losing detection
of invalid documented Charness CLI commands.

`45415116` added derived documented-subcommand validation and found the real
`charness verify` defect; `a52f63c7` then removed
`domain_language_contract`. The reviewer found the functional acceptance met.
The original framing was refuted: the shipped concern was command form, not a
prose preference. Distinct behavioral evidence is the derived-check test/probe
and released `v5.0.0`, not GitHub state. The v5.0.0 notes do not explicitly name
the removed `domain_language_contract`; that is an unfulfilled communication
debt and is not represented as satisfied by this close.

## Manual carrier decision

All three commits are already ancestors of released `v5.0.0`, but none carried
GitHub close keywords for these issue numbers. Manual fallback is therefore
appropriate with reason `auto-close-failed-after-remote-verification`. The stale
2026-08-11 GitHub comments saying "Nothing executed yet" predate the listed
commits and are superseded by the evidence above.

## Fresh-eye satisfaction

`parent-delegated`. The reviewer returned its findings to the parent. Boundary
fingerprint verification was `parent-attributed` only because the parent wrote
`charness-artifacts/goals/2026-08-12-repair-quality-planner-and-closeout-surface.md`
during the review window; no reviewer-authored change was asserted.

## Boundary Ownership

- Producer: the released implementation commits and their local proof artifacts.
- Consumer: a GitHub issue reader relying on the close comment and tracker state.
- Owning surface: issue manual-fallback closeout carrier.
- Verdict: owned-correctly.
