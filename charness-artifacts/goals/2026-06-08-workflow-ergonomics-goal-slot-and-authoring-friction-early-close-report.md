# Early Close Report — Workflow-ergonomics bundle (#336 + critique-enum + update_instructions)

Goal: `charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`
Date: 2026-06-08
Timebox: 4h (240m); closeout reserve 30m; activation 2026-06-08T07:19:58Z.
Elapsed at close: ~92m of 240m (closed before the 210m closeout window).

## Why early closeout was chosen

The operator-approved macro scope was the three-fix workflow-ergonomics bundle.
All three shipped by construction, each behavior-preserving, each with a SHIP
fresh-eye slice critique, and the whole bundle passed the broad gate (73/73
phases, 0 failed) with `ok:true` changed-line mutation coverage:

1. #336 — `achieve` Before-phase must not consume the host active-goal slot
   (`cead7949`).
2. critique-scaffold enum validity by-construction (`a101e716`).
3. publish_release `--prep-update-instructions` pre-publish stub (`138366c1`;
   coverage backfill `297d52ab`).

The goal's `Done-early policy: continue_next_improvement` names two continuation
candidates: (a) the installed-vs-repo drift detector — but that is an explicit
**Non-Goal** in this same artifact (different theme, kept deferred to respect the
prior-goal focus lesson), so continuing into it would contradict the goal's own
scope; (b) "the next agent/operator-tripping workflow surface" — which is
unscoped discovery: finding, shaping, and implementing a *new* ergonomics fix is
a fresh goal's worth of work that the operator has not scoped, and starting it
mid-goal without operator input is the scope-creep the focus lesson exists to
prevent. Therefore **no safe in-scope next slice remains**: the in-scope work is
complete, and every continuation candidate is either a Non-Goal or unscoped new
work. Closing at the approved macro target (with the #336 closeout) is the honest
stop.

## What user decisions are needed

- **Whether to spend the remaining ~118m on a new ergonomics surface.** If the
  operator wants the done-early budget used, re-point me at a *specific* next
  workflow/ergonomics or release-hardening surface (or explicitly re-scope the
  deferred drift detector in, lifting its Non-Goal status) and I will continue.
  Absent that scoping, I closed at the approved bundle.
- **#336 GitHub closure.** The closeout is staged via a direct-commit
  close-keyword carrier (`Close #336`); default no-push means #336 stays OPEN
  until the maintainer pushes, at which point GitHub auto-closes it. Push is the
  operator's call.

## What waste / retro findings explain the gap

Per the session retro
(`charness-artifacts/retro/2026-06-08-workflow-ergonomics-bundle-336-goal-slot.md`):

- The Slice-3 prep affordance shipped input-normalization branches and defensive
  guards uncovered; the bundle-boundary mutation producer flagged 6 changed lines,
  costing a cover-then-re-run-producer cycle (each producer run is multi-minute).
  Running the producer first (per the carried guardrail) surfaced this early; the
  durable lesson is to cover normalization/guard branches in the introducing
  slice. This is the main reducible waste and the gap between "implementation
  done" and "closeout proven."
- Minor: a SKILL.md core-headroom re-tighten (Slice 1) and a first-miss
  invalid-adapter test (Slice 4) — both single edit cycles, anticipated.

The early close is not driven by a blocker — the bundle is complete and proven —
but by the honest absence of a safe in-scope continuation within the operator's
approved scope.
