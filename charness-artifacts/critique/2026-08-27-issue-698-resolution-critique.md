# Issue #698 Resolution Critique

Date: 2026-08-27 Asia/Seoul

## Decision Under Review

Close #698 after the superseded lifecycle now preserves its successor handoff
and applies the existing Auto-Retro disposition floor when a bound retro
surfaces improvements.

## JTBD and Resolution

The issue asks Charness to prevent a superseded transition from silently
dropping surfaced retro improvements. The repaired checker and status writer
share the smaller superseded-specific floor; an undispositioned improving retro
is refused before the status transition is written. Complete-only host,
evaluator, coordination, and other After-phase requirements remain out of scope.

## Counterweight Pass

The independent reviewer found no remaining local implementation blocker. The
counterweight retained one operational condition: a local proof and a comment
do not establish the external issue state. The close must use the exact target
provider, validate the carrier before mutation, and read the final state back
after the comment and close. This condition was handled by the provider
preflight and the final `verify-closeout --expect-state CLOSED` readback.

## Verdict

Conditionally closable: the local JTBD proof is sufficient for the claimed
local-only behavior, and the close is approved only after the provider carrier
and final state checks pass. No hosted or installed behavior is inferred.

## Non-Claims

- No remote CI, installed export, release, push, consumer migration, or
  end-to-end hosted behavior is claimed.
- The close does not claim that complete-only lifecycle floors apply to
  `superseded`.
- This critique does not authorize parent #724 closure or cursor advancement
  until the issue close readback is complete.

## Reviewer Tier Evidence

- Requested tier: host-defaulted bounded reviewer; no tier override was exposed.
- Requested spawn fields: n/a — the host spawn surface exposed no typed tier
  fields.
- Host exposure state: host-defaulted
- Application state: host-defaulted — no separate envelope-application signal
  was exposed.
- Delivery state: findings-received
- Execution mode: typed-subagent
- Execution: one unnamed independent bounded reviewer context returned findings
  to the parent.
- Boundary: the untyped reviewer shared the parent worktree; window
  `issue698-closeout-review-2` was fingerprint-verified immediately after the
  result with `verdict: clean` and empty drift before findings were consumed.
- Reviewer disposition: conditional approval, with exact-target preflight and
  post-mutation readback required at the external boundary.

## Fresh-Eye Satisfaction

parent-delegated — the resolution was read in a separate reviewer context and
the returned condition was incorporated into this closeout contract.

## Reviewed Input Identity

<!-- No prepare packet was consumed for this direct issue-resolution review. -->

## Local Review Scope

- Issue: #698 in `corca-ai/charness`.
- Implementation contract:
  `charness-artifacts/impl/2026-08-27-issue-698-superseded-floor.md`.
- Local implementation/proof commits: `9255a238f`, `0c0e5bd3e`, and
  `673a76c78`.
- Reviewed implementation state: the named implementation contract, focused
  proof, and closeout carrier for this issue.

## Boundary Ownership

- Producer: the superseded checker and status writer.
- Consumer: the issue closeout carrier and provider state readback.
- Owning surface: Charness's superseded lifecycle and its local proof; hosted
  issue state remains provider-owned.
- Verdict: owned-correctly.
