# Charness Handoff

## Workflow Trigger

- **A goal is SHAPED and pursue-ready** — activate directly, no activation
  question (the standing approvals in `AGENTS.md` cover it):
  `/goal @charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md`

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back — six times
  measured, and the last is the sharpest.** The repair for a false-POSITIVE hole
  (a blocking gate refusing fenced examples) opened three false-NEGATIVE ones:
  prose-wrapped links, a fence toggle inverting on mismatched `~~~`/backtick
  markers, and live text after a mid-line `-->`. All latent, all caught by round 2.
- **A claims reviewer reads the RECORD and finds what code reviewers cannot.**
  Second outing, three more record blockers — including this goal's own
  measurement artifact still saying axis A2 was NOT ARMED after it had been. That
  table had been ADDED to correct the opposite overclaim, then went stale the
  other way.
- **A completion summary is a proxy; read the OUTPUT.** Two background runs
  reported `exit code 0` over runs carrying 10 and 4 failures.
- **Never sync a generated surface while a background suite reads the tree** —
  four phantom packaging failures, all passing in isolation.
- **Fingerprints rotate three ways**: on a refactor, on removing one unused
  import, and on the commit itself.

## Current State

- `main` is at `ce714872`, pushed, **CI green on every pushed SHA, verified on two
  channels** (`gh api .../check-runs`, `gh run list`). The combined-status API
  says `pending`/`total_count: 0` for every commit here; not a real pending.
- **Three blocking gates now judge references from the CONSUMER's position**, and
  each reports what it SKIPPED on both paths — a green run silent about its skips
  is how this class accumulated three honest zeroes. Anatomy lives in the sweep.
- **The `parents[N]` cancellation is an executable invariant** with a revisit
  trigger in [implementation-discipline.md](./conventions/implementation-discipline.md). If it reddens and the fix is "bump
  the number", the class is recurring and the call sites need a shared helper.
- Still open: the **E-cluster**, D41–D50, `parse_created_date`'s consumers.

## Next Session

1. **#479 is CLOSED.** All four axes armed and repaired: A1 12→0, A2 6→0,
   A3 4→0, A4 ~70→0. Its resolution critique refused an earlier close because
   this repo's own denominator record misstated the arming status — corrected,
   and the three axes with NO ruler are now filed as #482/#483/#484.
2. **The waiting goal owns #481** — the operator's own external-usage report, and
   the class behind it: a generator cannot represent DELIBERATE ABSENCE, and
   destroys the only record of it in the same pass. Read the goal, not this line.
3. **#481 is the operator's own external-usage report, and it is data loss:**
   `bootstrap_adapter.py` silently reverts a customized `quality` adapter to the
   preset on every run — 14 comment lines to 0, and preset defaults resurrected
   pointing at paths that do not exist in that repo.
4. **#482/#483/#484 are the unreachable-file axes with NO ruler**, filed with
   their counts: command carrier (14 sites, the spelling a consumer executes),
   shipped non-markdown (one is a template a consumer copies and runs), and
   `skills/shared/**` being outside the portable rules. #480 and #468 also open.
5. **#475's behavioural half is still an OPEN operator decision.**

## Discuss

- **Both link gates share a staged-`.md` trigger that does NOT scope them** — a
  verdict also flips when the link TARGET is renamed, staging no `.md`. Recorded
  in [validator-timing-layers.md](./conventions/validator-timing-layers.md), compensated by the broad gate and CI, and not
  widened for one gate alone; widening must move both.
- **Issue creation is STANDING, push is standing CONDITIONAL ON THE GATES, issue
  close is standing conditional on the closeout floor** (`AGENTS.md`). PR,
  release, tag, version bump, cautilus stay per-goal.
- **A count that grows when the ruler widens is evidence about the ruler.** A1
  went 11→12 and A2 5→6 once the denominator was stated. Neither means exhausted.
- **A read-only check and an irreversible boundary deserve different teeth** —
  D48 left `drift` alone and refused at publish; still open elsewhere.

## References

- [completed goal](../charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md) · [its retro](../charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md) · [its claims review](../charness-artifacts/critique/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round-claims-review.md) · [the denominator sweep](../charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md)
- [prior goal](../charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md) · [the can-this-rule-fire sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- [deferred decisions](./deferred-decisions.md) (D45–D50) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
