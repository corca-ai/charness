# Resolution Critique #305 — release publish-flow resilience

Date: 2026-06-05
Issue: #305
Classification: bug
Reviewer: bounded fresh-eye subagent (general-purpose, read-only, shared parent
worktree) + operator self-critique.

## Slice under review

Three-gap bug-class fix on the release publish helper: (1) a `--resume` flag that
detects an existing local release commit+tag partial state, re-validates, then
continues push/create/verify idempotently; (2) a layout-tolerant retro import so
the helper runs from the installed plugin cache; (3) an unconditional check that
blocks when adapter `update_instructions` are stale relative to the target.

## Verdict: SHIP — no blockers

The fresh-eye reviewer confirmed all three gaps correctly and safely addressed
(YES each), genuine regression guards (new tests fail against pre-fix code), and
byte-identical mirrors. The B3 double-publish hazard is closed: `assert_resumable`
refuses when already fully published or when there is no consistent partial
state, and all re-validation gates run before the push.

## Adversarial findings folded in-slice

The reviewer's review was non-blocking but surfaced real edges; all folded:

- **Staleness regex edges (C).** The original `\b\d+\.\d+\.\d+\b` scan had a
  false negative on `v`-prefixed versions and a possible false positive on dotted
  dates. Replaced with precise previous-vs-target substring containment: flags
  only when the previous version is present and the target is absent. No date
  false positive, `v`-prefix matched transparently, no version-agnostic false
  positive. New unit cases pin all four edges.
- **Resume re-validation honesty (B).** Added `preflight_release_issues` to the
  resume re-validation (so resume-with-`--close-issue` keeps pre-mutation issue
  verification) and documented that resume re-runs the push-time-flaky gates, not
  the one-time file-delta adapter/real-host preflights the original attempt
  already passed on the unchanged worktree.
- **Import fallback breadth (D).** The `skills.public.X -> skills.X` fallback now
  tolerates only a `skills(.public)` layout miss and re-raises a genuine missing
  dependency inside the target module instead of relabeling it.
- **Weak test (E).** `test_resume_requires_publish_current` now asserts the
  specific `--resume requires --publish-current` message rather than any usage
  line that happens to contain the flag name, so it stays a discriminating guard.

## Residual / non-claims (accepted)

No real `git push` / `gh release create`: resume and idempotency are proven with
a simulated failed-push partial state, a fake git, and a fake gh. No new charness
version / no marketplace bump — this hardens the helper only. The public `release`
consumer contract is unchanged (routing, `charness-artifacts/release/latest.md`
artifact, acceptance evidence); recorded as additive dogfood evidence.

## Prevention

Resume idempotency, the exported-layout import, and the staleness block are each
locked by a regression test; the dogfood evidence entry freezes the unchanged
consumer contract so a future edit that regresses any of them fails a test or the
public-skill validation gate.
