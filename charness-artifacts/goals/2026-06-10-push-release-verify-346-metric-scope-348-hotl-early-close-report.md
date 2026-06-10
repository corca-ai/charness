# Early Close Report — 2026-06-10-push-release-verify-346-metric-scope-348-hotl

## Why early closeout was chosen

The goal closed ~80 minutes before the 4-hour timebox's reserve window
because the in-scope queue genuinely emptied with verified proof, not because
work was deferred: slice 1's lane verification completed INCLUDING the
scheduled mutation run over the pushed HEAD (run 27270609532 fired 10:40Z
inside the timebox and went green, so the pre-resolved cron-skip fallback was
never needed); slice 2 (#346) landed with the corrected root cause, two
folded fresh-eye cycles, a 0-uncovered consumer confirm, and a live dogfood
of the new Claude-scoped metrics on this very goal's closeout; slice 3
(#348) landed the `hotl` package with all gates green and a SHIP-WITH-NITS
port review. The done-early policy (`continue_next_improvement`) was honored
by filing the surfaced improvement as issue 349 rather than absorbing it:
the reciprocal hitl boundary line requires trimming a reviewed, at-cap
frozen contract — its own deliberate lane, exactly the kind of edit the
slice 3 critique disposition said must not happen under closeout time
pressure. The other open item (#184) is excluded by this goal's Non-Goals
(fifth consecutive deliberate exclusion). No safe in-scope slice remains.

## What user decisions are needed

1. **Push lane:** local `main` is ahead of `origin/main` with the slice and
   closeout commits, including the staged `Closes #346` / `Closes #348`
   carriers (both `draft_verified`). Pushing is the operator-authorized
   lane this goal deliberately did not execute; after the push, verify both
   issues flipped CLOSED (`issue_tool.py verify-closeout`).
2. **#349 (hitl/hotl reciprocal boundary):** decide whether it joins the
   next goal queue as a small bounded frozen-contract slice.
3. **ceal-side consumption of `hotl`:** the consuming repo's follow-up
   (adapter wiring + retiring its repo-local skill) — operator decides
   when that repo picks it up.
4. **#184 (product success metrics):** fifth consecutive deliberate
   exclusion; needs an operator `ideation` session shaped into its own
   goal if it should happen next.

## Waste and retro

Retro: charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md.
Headline waste: one redundant instrumented broad-pytest producer run per
mutating slice (~7 min each, twice) because the locked producer ran before
the fresh-eye critique / late branch-coverage tests — now a contract line in
docs/conventions/implementation-discipline.md (run the slice critique BEFORE
the locked producer). Second, a fold-then-revert cycle on the at-cap hitl
core (became issue 349). The probe-attribution capability gap that wasted
the two PRIOR goals' closeouts is closed and was dogfooded by this goal's
own scoped metrics block (776 of 1027 session records in the goal window).
