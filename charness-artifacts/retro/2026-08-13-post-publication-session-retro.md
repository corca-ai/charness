# Post-publication session retro
Date: 2026-08-13
Goal: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md

## Context

The `5.1.0` release auto-retro
(`charness-artifacts/retro/2026-08-12-v5-1-0-release-auto-retro.md:10-13`)
disclaims session coverage in its own second paragraph and asks for a session
retro. All three existing session retros pre-date publication and say so. This
retro closes that gap: it covers the publication itself and the post-publication
fresh-eye closeout review that followed it.

It also renders the judgment `charness-artifacts/release/latest.md:201-202`
defers to the "release critique/retro reviewers" — the `RECONCILE REQUIRED`
disposition — which nothing had rendered until now.

## Window

`0ac9260d..4aa76a19` (prepared candidate through the handoff reconcile), plus the
post-publication closeout review conducted after `4aa76a19`. The fixed 22-issue
cohort remains OPEN by design; the release closed no issues.

## Evidence Summary

- Publication is real and independently observed: tag `v5.1.0` at `1024e500` on
  `origin`, default head `4aa76a19`, and a **credential-free REST readback**
  returning `draft: false` / `target_commitish: main`
  (`../probe/2026-08-13-v5.1.0-post-publication-observables.md`).
- Hosted Quality Core succeeded on the default branch head (run `31650565315`,
  `Core deterministic gates` and `Changed-line mutation coverage`).
- The post-publication closeout review
  (`../critique/2026-08-13-v5.1.0-post-publication-closeout-review.md`) ran two
  bounded reviewers on distinct angles; both boundary windows verified `clean`.
- Ten findings recorded. Five were stale-record defects in the goal and handoff,
  now repaired. One was resolved during the review. One was escalated to
  [#609](https://github.com/corca-ai/charness/issues/609). One reviewer inference
  was rejected on evidence.

## RECONCILE REQUIRED disposition

**Judged: discharged in substance, receipt now recorded.** `docs/handoff.md` was
reconciled to the published `5.1.0` by commit `4aa76a19`, satisfying the baton
reconcile obligation. But the reconcile *introduced* three of this review's
findings — a misattributed verification channel, a non-claim that had gone stale
within minutes, and a self-falsifying head SHA. So the honest disposition is:
obligation met, quality of the reconcile poor, all three defects now repaired.
This is exactly why the release record defers the judgment to a reviewer instead
of treating the refresh as self-certifying.

## Waste

**The claims-review floor gave a spawn-barred session no honest option.**
`skills/public/release/references/critique-boundary.md:39-40` already prescribes
"publish with the review unproven" when no distinct observer can be obtained. The
validator has no way to express that state, and its distinctness test is
`preparer == reviewer` string inequality. A session documented as unable to spawn
subagents therefore emitted `verdict: pass`, which the helper consumed as
authorization to tag, push, and create the release. Escalated to #609.

**A proof surface confirmed itself.** The release record's "public release
surface verification: verified" is computed from `gh release view` run by the
backend that created the release. The one genuinely distinct channel in the
record honestly states it cannot establish a release exists for a tag. So the
proposition the record's top line asserts had no discharged floor.

**The parent repeated that exact error while trying to fix it.** The evidence
capture written for the reviewers claimed an authenticated `gh release view`
closed that gap. It does not: `release_view_shape` is the command shape this
repo's own guard flags `same-proxy-flagged`. The floor reviewer caught it. Cost
was low because the reviewer caught it before anything depended on it — but the
lesson is that knowing the P4 rule did not prevent me from violating it one step
later, which is the same pattern the north star records at
`docs/design-north-star.md:88-90`.

## Critical Decisions

1. **Escalate the validator defect rather than point-fix it.** A local patch plus
   a passing unit test at `publish_release_claims_review.py` would make the
   ownership question look finished while leaving the fail-open class intact.
2. **Record the claims review as unproven, not fabricated.** Only the publishing
   session's transcript could settle it and it is unavailable. Several signals
   point one way; none is conclusive, and overstating would be its own defect.
3. **Reject the reviewer inference that hosted CI discharges `direct-to-default`.**
   It names a carrier, not a CI lane. Adopting it would have closed eleven cohort
   issues on a readback that never happened.

## Trends vs Last Retro

The final release-boundary retro's lesson was "release evidence packets go stale
after a verdict repair." The recurrence here is adjacent and sharper: **release
evidence goes stale within minutes of being written, and the record that refreshes
it is itself unreviewed.** The handoff reconcile at `4aa76a19` was authored,
committed, and false in three places before the CI run it failed to mention had
finished.

## North Star Alignment

P4 held where a distinct observer and a distinct channel were actually used:
fresh readers found ten defects that local tests and the publishing session did
not, including one inside the parent's own evidence file. P4 failed where the
distinctness was *inferred* — the claims-review floor — which is precisely the
facet's stated failure mode ("a distinct observer that re-reads the same proxy
still rubber-stamps"). The failure signature avoided: a green helper becoming
permission to publish. The failure signature hit: a proof surface whose
distinctness check cannot distinguish an observer from a string.

## Expert Counterfactuals

**Richard Feynman — "the first principle is that you must not fool yourself."**
The claims-review record fools its reader in a structurally specific way: it
reports the *form* of a distinct observation (two different strings) with none of
its *content* (no findings, no reviewer identity, no boundary window). A floor
that accepts form where content is the whole point would have been rejected at
design time by asking "what would this record look like if nobody reviewed
anything?" — the answer is: exactly what is on disk.

**Falsification-first lens applied to my own evidence.** Before presenting a
channel as distinct, ask which repo-owned check would flag it. `same-proxy-flagged`
already existed and already named `release_view_shape`. I did not consult it, and
a reviewer had to. The cheap habit is to run the repo's own guard against your
own evidence before handing it to a reviewer.

## Sibling Search

- same layer: `skills/public/release/scripts/publish_release_post_create.py` distinct-channel confirmation | decision: valid capability follow-up outside this repair | proof: the same-proxy guard exists and names `release_view_shape`, but the record's own `verified` line is computed from that shape without consulting it | follow-up: https://github.com/corca-ai/charness/issues/609
- abstraction up: every proof surface whose floor is "a distinct observer" | decision: same class, escalate | proof: `publication-boundary.md:100-106` makes distinctness a recorded observable for one verdict while the claims lane infers it | follow-up: https://github.com/corca-ai/charness/issues/609
- specialization down: the parent's own evidence capture | decision: fix now | proof: it asserted a same-proxy channel closed a distinct-channel gap, and a bounded reviewer caught it | follow-up: applied in `../probe/2026-08-13-v5.1.0-post-publication-observables.md`

Structural pattern: a distinctness floor that checks form instead of content
fails open silently, and the surface's own author is the least likely to notice.
Triggering instance(s): the v5.1.0 claims review, and the parent's evidence
capture one step later. Destination: https://github.com/corca-ai/charness/issues/609.

## Next Improvements

- workflow: run the repo's own guard against your own evidence before handing it
  to a reviewer, especially when the evidence claims to discharge a P4 floor.
- capability: give the claims-review validator an honest `unproven` state and a
  checkable distinctness observable, per #609.
- memory: retain that `direct-to-default` names a carrier plus
  `verify-closeout --expect-state CLOSED`, not a hosted CI lane; the cohort's
  eleven local-proven rows are still waiting on that carrier.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-post-publication-session-retro.md
