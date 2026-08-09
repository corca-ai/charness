# re-verify the backlog and retire the unchosen constraint
Date: 2026-08-10
Goal: charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md

## Context

A four-slice goal built from one finding: `#554` had been FIXED before it was last
read, and its own fix quoted its complaint as the reason the fix existed. Nobody
re-read the issue. The goal generalised that — a record treated as a fact because
re-reading it was nobody's step — and set out to retire an unchosen constraint,
make backlog re-verification executable, consolidate on GitHub, and close the
family whose defect reaches consumers.

All four slices ran. v4.2.0 shipped. The backlog went 24 open to 17.

## Evidence Summary

- 11 issues closed: 9 consolidations rendered `NOT_PLANNED`, 2 resolutions
  (`#554`, `#571`) rendered `COMPLETED`. 4 umbrellas filed (`#582`-`#585`), each
  passing the consolidation readback against the live tracker before any close.
- 3 issues filed: `#580`, `#581`, plus a measured refutation recorded on `#546`.
- v4.2.0 published and verified through `gh release view` and `gh api` — a channel
  distinct from the publish helper's own exit code.
- Broad suite 8505 passed at the last full run; every commit gated through
  `run_slice_closeout.py`.
- 6 bounded fresh-eye rounds. Every one changed the design. One returned HOLD.
- Host signals (thread-wide, NOT a per-goal total — no metric window was recorded):
  624 function calls, 70 patch applications, 10 subagent spawns, 0 compactions.
  Proxy activity shape: `check-python-lint.sh` x4, `git push` x8, `git add` x16.

## Waste

- **13 push attempts to land one bundle.** Each ran the ~95s pre-push gate. The
  cause was serial single-blocker discovery: budget, then mutation coverage, then
  ruff, then coverage again. The repo's own implementation discipline names this
  exact trap — "if a commit is rejected by one of these gates, run the aggregate to
  surface ALL of them at once rather than fix-and-retry one rejection at a time" —
  and the PRE-PUSH aggregate has no such affordance, so I rediscovered it by hand.
- **Two full designs built and deleted** (the prose-matching residue scanner, the
  `#546` budget discriminator). Not pure waste — both produced measurements that
  are now the record — but both were built before the cheapest disconfirming probe
  was run. The `#546` probe that killed it took under a minute and could have run
  first.
- **Four length/lint/dup gate rejections mid-slice**, each costing a split or a
  reclassification after the code was written. The advisory hook fires on write and
  I acted on it late.
- Repeated 12-minute broad suites (4 full runs) where a scoped run would have
  answered the question.

## Critical Decisions

- **Deleting all prose matching and every fitted threshold** after the operator
  challenged the hardcoded strings. This was the run's turning point: round 2 had
  measured the design collapsing to 21-of-22 refusals, and the operator's question
  named the deeper reason — a portable skill cannot depend on how one repo phrases
  things, and constants tuned by watching output are fitted to their own test set.
- **Reverting the `#546` repair rather than iterating**, because the review's
  findings said the discriminator was wrong, not buggy.
- **Not routing around three refusals** (the `#514` crosswalk, the consolidated
  close reason, the observer floor) when each blocked my own work.
- **Relevelling the seed-fixture budget by the adapter's own recorded derivation**
  rather than treating it as a floor change requiring the operator — the rule was
  written down, and applying a written rule to current samples is maintenance.

## North Star Alignment

- **P5 held, in the case that mattered.** The premise tool renders a state and
  stops. Run against `#554` — the issue this whole goal was designed from — it
  returned `premise-refuted-clean` and did NOT recommend closing it. The close
  decision stayed a human's, on evidence the tool does not supply.
- **P4 held at every irreversible boundary.** Push and release both got
  distinct-channel hosted readback. Eleven closes each passed the floor before
  mutation, and the three that refused were left refused.
- **P1 held in slice 1** — an unarmed constraint bearing on reversible editorial
  work lost its reach and kept its meaning.
- **The named failure signature this run walked into, repeatedly: a check that
  exists and never runs.** Six instances — the premise-state channels, the
  `consolidated` classification (unreachable on every live carrier), the
  consolidation readbacks (absent from the required carrier), `release_surface_tokens`
  (advertised and dead), and two stale classification vocabularies. Every one was
  found by a bounded round or a probe, never by the tests, because the tests
  exercised direct calls while the wired path never reached the code.

## Expert Counterfactuals

- **The direct lens — "run the cheapest disconfirming probe before building"** —
  would have changed two slices. For the residue scanner: measuring the clean/refuse
  distribution on the real backlog took one command and would have shown the
  prose design collapsing before it was tuned three times. For `#546`: seeding a
  signals file minus one late-recorded label took under a minute and would have
  killed the design before the tests were written.
- **A release engineer's lens** would have asked "what does a consuming repo see on
  its FIRST run after upgrading?" earlier. That question found the `#546` blast
  radius and the `release_triggered` inertness; both were shipped-facing and neither
  was visible from inside this repo's green.

## Sibling Search

- axis: a check that passes its own direct-call test while never firing on the wired path | decision: valid follow-up outside the slice | proof: 6 instances this run, each caught by a bounded round rather than by the suite; the repair applied each time was local (test through the wired surface) with no structural guard added | follow-up: deferred handoff-anchor `wired-path-coverage`

## Next Improvements

- workflow: run the cheapest disconfirming probe BEFORE building a heuristic, not
  after review names it — applied twice this run, both times too late.
- capability: the pre-push aggregate should surface all blockers at once, the way
  the commit-time aggregate already does; 13 push attempts is the measured cost.
- memory: `Premise-residue:` markers must be WRITTEN by records that decline to
  close an issue — the seam now reads them and nothing yet writes them except this
  goal's own one instance.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md
