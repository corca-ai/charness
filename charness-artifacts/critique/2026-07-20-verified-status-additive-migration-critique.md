# Critique Review
Date: 2026-07-20

## Decision Under Review

The user-approved additive migration for the issue-closeout verifier's
terminal-sounding `verified` status (handoff Discuss item). `verify-closeout`
now emits an additive `confirmation` object — `observer`
(`issue_verify_closeout@<backend-id>`), `channel` (`backend-state-readback` or
`carrier-body-checks`), `scope`, and a pre-rendered `line` whose verb tracks
the scope (`confirmed:` only for the final state-checked verdict,
`carrier-checked:` for pre-publication carrier-only passes, `None` on failure).
Status tokens are unchanged compatibility vocabulary; existing artifacts that
recorded bare statuses are grandfathered, never reinterpreted. The
closeout-discipline reference states the new rendering contract and explicitly
disclaims the line as the verifier's own observer/channel, not the
distinct-observer behavioral confirmation. Mirrors synced; verifier tests
assert the object on all three status branches.

The same slice resolves the sibling Discuss clause by evidence, not code:
pre-commit rollback persistence already shipped (failure records carry
`precommit_rollback` with retention tests), so the handoff entry predating that
implementation was closed as stale.

Cautilus scenario-review decision (ask-before-run preserved, no live eval run):
`evals/cautilus/scenarios.json`'s issue entries cover sibling-search and
representative-contract fixtures untouched by an additive output field, and
`docs/public-skill-dogfood.json` asserts the `carrier_verified`-vs-`verified`
distinction, which the migration preserves — no maintained scenario or dogfood
contract change needed. The reviewer independently sanity-checked and
confirmed this decision.

## Failure Angles

- Correctness: does `confirmation` truthfully describe what the verifier
  observed in every branch (manual-fallback with expect-state, failure shape,
  observer identity across all backend constructions)?
- Contract honesty: does the new paragraph contradict the
  necessary-not-sufficient doctrine or the rung-1/rung-2 split, or suggest the
  line satisfies the distinct-observer mandate?
- Consumer safety: strict-key consumers of the verifier JSON.
- Skill ergonomics/portability: dated incidents, bare anchors, host-specific
  references in new portable-package text.
- Handoff honesty: the already-shipped rollback-persistence claim and the
  RESOLVED wording; the scenario/dogfood no-change decision.

## Counterweight Pass (four-bin triage)

- K1 | act-before-ship (fixed): the reviewer found the `confirmed:` verb also
  rendered on pre-publication paths (draft validator, `carrier_verified`,
  commit-msg hook report) — softly recreating the terminal-sounding claim the
  slice removes. Fixed by making the verb track the scope
  (`carrier-checked:` unless the final state readback ran); tests updated.
- K1 | act-before-ship (fixed): the doc guidance could be read as the
  confirmation line discharging the distinct-observer behavioral-verdict
  obligation. Fixed with an explicit disclaimer sentence pointing at that
  mandate.
- K2 | over-worry (confirmed, no change): no consumer iterates the payload
  keys strictly (commit-msg hook, draft validator, release closeout paths all
  read named keys), so the additive field passes through inertly; `line: None`
  on failure is the right shape (a rendered not-confirmed line would itself
  read as a claim); observer identity matches every backend construction
  (default `gh` in the resolver and all literal callers).
- K3 | bundle-anyway (fixed): the channel label hardcoded `github-` although
  the backend is adapter-owned; renamed to `backend-state-readback` for
  portability while the observer keeps the concrete backend id.
- K4 | valid-but-defer (no action): the draft validator renames `status` to
  `draft_verified` but passes `confirmation` through untouched; after the verb
  fix the draft line reads `carrier-checked:`, which is accurate, so no
  further draft-specific shaping is needed now.

## Recurrence Verdict

The terminal-sounding-status class now has a structural answer: any consumer
rendering closeout prose has a machine-provided line that names observer,
channel, and scope, and the strong verb is unreachable without the state
readback actually running. The same pattern (verb tracks scope) is reusable
for other verifier-style tools; the grandfather rule keeps history stable.

## Boundary Ownership

- Verdict: owned-correctly

The verifier owns its output vocabulary; the closeout-discipline reference owns
the rendering contract; consuming validators were untouched because the field
is additive. The portable package carries no repo-local or host-specific
references in the new text.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer`
  (Read/Grep/Glob) with session-model inheritance per the repo per-host
  subagent contract; no Codex model requested on this host, so the omission is
  contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by
  name; the read-only envelope bound and the rail-1 reviewer-boundary
  fingerprint verified clean (no index/worktree drift) after the reviewer
  returned, so approvals are valid and the reviewer ran on the parent's
  session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — one high-leverage bounded reviewer over the uncommitted
slice (five angles, in-report counterweight); both should-fixes applied and
re-tested before commit; rail-1 reviewer-boundary fingerprint verified clean.
