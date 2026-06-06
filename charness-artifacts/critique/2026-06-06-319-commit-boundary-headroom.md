# Resolution Critique — #319 commit-boundary SKILL.md core-headroom coverage

- Date: 2026-06-06
- Issue: #319 (SKILL.md `core_nonempty` headroom-buffer test runs only in the
  broad gate, not the commit boundary; generalizes #308/#314)
- Goal: `charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md`
- Target reference: code-critique / issue-resolution critique (recurrence-focused)

## Execution

Fresh bounded subagent reviews (canonical path, not a same-agent pass).

- Fresh-Eye Satisfaction: parent-delegated (bounded subagents).
- Packet Consumed: n/a (no critique-adapter `packet_sections`).

## Change

A changed-file-scoped commit-boundary **ratchet** for the SKILL.md
`core_nonempty` ≥4 headroom buffer (distinct from the hard 160 limit), so
authoring to the 160 limit (0 headroom) no longer passes the per-slice gate and
fails only the broad gate.

- `scripts/check_skill_surface_preflight.py`: shared `CORE_NONEMPTY_HEADROOM_BUFFER`
  constant; `evaluate_core_headroom` ratchet; `scan_changed_skill_md` +
  `--changed-skill-md` mode reading the **staged index blob** (`git show :<rel>`)
  for "new" and `HEAD:<rel>` for "base".
- `scripts/staged_commit_gate_plan.py`: `_skill_core_headroom_gates` appends a
  path-scoped `check-skill-core-headroom (staged)` gate (runs in the literal
  pre-commit hook and in `run_slice_closeout --predict-commit` — the same
  function).
- `docs/conventions/authoring-preflight.md`: #308 preflight reference extension.
- Existing broad-gate achieve headroom test kept, refactored to the shared
  constant (not lowered/removed).

Success line: the buffer is flagged at the commit boundary for changed
public/support SKILL.md before the broad gate, without retroactively breaking the
5 skills already under buffer. Out of scope: the hard ≤160 limit (existing
owner), broad-gate coverage for non-achieve skills, any live/prod/release proof.

## Angles

1. Correctness fresh-eye (pre-fix): found BLOCKER 1 — ratchet read the working
   tree for "new" but HEAD for "base", so a healthy working tree could mask a
   0-headroom staged commit. Re-review after fix: **CLEAR** (index-vs-worktree
   hole closed; fallback keyed on index-presence; staged-deletion safe; mirrors
   byte-identical; no banned vocab; 43 tests pass).
2. Recurrence/prevention: no blockers; one concern — no meta-test detects a
   future "blocking buffer assertion without a commit-boundary equivalent."
   Confirmed **zero** current latent siblings (`check_python_lengths --headroom`
   is advisory; `long_core` 160 ceiling already gates at the boundary; total-200
   has no separate buffer).
3. Completeness/acceptance: **ACCEPTANCE MET** — verified the 5 under-buffer
   skills (issue/release/retro=0, debug/impl=2; none over 160); gate runs in both
   the pre-commit hook and `--predict-commit` (same code path); ~76ms, 2
   `git show` per changed SKILL.md, no gate when no SKILL.md changed; broad gate
   stays achieve-only by design (honest); acceptance repro passes.

## Findings → Counterweight Triage (four bins)

- **Act Before Ship:** BLOCKER 1 (ratchet judged the working tree, not the
  staged index). *Already fixed and re-reviewed CLEAR before this carrier.*
- **Bundle Anyway:** none.
- **Over-Worry / Valid but Defer:** the recurrence "meta-test for the buffer
  class." Counterweight verdict: the class has population = 1 (the #319 surface
  itself, now fixed); a `remaining >= N` regex meta-test is the #305 brittleness
  trap (it would false-positive on the very test it protects) and carries the
  #307/#314 per-commit latency cost; and the concern is essentially the
  already-filed `recent-lessons` line-19 disposition that **#319 itself
  resolves**. Filing a second "meta-test for the class" issue on a size-1 class
  is over-process.

## Deliberately Not Doing

- Not building a meta-test/gate for "blocking buffer assertions must gate at the
  commit boundary": zero current latent instances; speculative gating against a
  hypothetical second buffer; brittle (#305) and adds latency (#307/#314).
- Not filing a fresh follow-up issue for it: the generalization is already
  recorded (`recent-lessons.md` line 19) and #319 is its resolution. Natural,
  non-speculative revisit trigger: a *second* blocking buffer/headroom constant
  is ever introduced.
- Not adding broad-gate buffer tests for non-achieve skills: the commit-boundary
  ratchet is the all-skills enforcement; the broad gate stays achieve-only by
  design (goal Non-Goal).

## Next Move

Ship #319 as-is. Commit with `Close #319`. No further code change, no new gate,
no follow-up issue. Recurrence note recorded as a non-claim here.
