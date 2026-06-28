# Session Retro
Date: 2026-06-29

## Mode

session

## Context

Reviewing the claim-fidelity fixture correction for the `retro` skill: the first
live capture of the shipped per-skill claim-fidelity sweep (`a7e49790`) and the
planner extraction it drove (`167cad5c`, HEAD).

Arc: the v0.57.0 sweep statically calibrated all 20 public-skill fixtures. Retro's
fixture asserted the floor `requiredCommandFragments: [expert-lens.md]`. The first
*live* capture ran `/charness:retro` for real and the floor **failed** — the run
filled the mandatory `Expert Counterfactuals` section from the SKILL.md-inlined
rule, never opened `expert-lens.md`, and missed the Engelbart system-improving
lens that was the on-the-nose fit. Root cause (git-evidenced): the 6/23-24
planner-first sweep gave 6 skills a planner emitting `required_reads` but left
`retro` and `hitl` planner-absent; the claim-fidelity sweep then calibrated retro
as fidelity-to-current-shape, freezing the gap into a passing fixture. The fix
extracted a real `plan_retro_run.py` (schema `retro.run_plan.v1`), made
`expert-lens.md` an **unconditional** `required_read`, and made SKILL.md
planner-first.

Why it matters: this is the harness's self-review skill failing its own asserted
floor — and the correction is what makes future retros actually consult the lens
catalog instead of regurgitating the inlined rule.

Trustworthy evidence for this retro: git history (`a7e49790`, `167cad5c` with
stat + full message), the captured proof bundle
`charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29/`, the adapter, and
this very run — which exercised the new planner end to end (`strong` for routing
behavior; the formal paid re-capture remains pending, so the floor-flip claim is
`moderate`, see Critical Decisions).

## Evidence Summary

- `git show 167cad5c --stat`: planner extraction, +828/-38 across 5 files
  (`plan_retro_run.py` x2 mirror, SKILL.md x2, `tests/test_retro_plan.py` +7 tests).
- `git show a7e49790`: failed live-capture proof bundle (`PROOF.md`,
  `captured-retro-artifact.md`, `cautilus-report.json`, `observed.v1.json`);
  observation = failed.
- This run's planner output: `lens_brief.fitting_lens` = Engelbart
  (system-improving-itself), `work_class` = system-improving, `expert-lens.md`
  routed as an unconditional `required_read`. I opened it and applied the briefed
  lens — the behavior the fixture asserts now holds in a real run.
- Prepare packet (`changed-files-and-owning-surfaces`): empty — clean tree, work
  already committed. Packet Consumed: yes (empty).

## Waste

- **Static calibration froze a live behavioral gap into a passing fixture
  (`strong`).** The sweep measured fidelity-to-current-shape, so retro's floor
  passed static inspection while the live run never opened `expert-lens.md`. The
  gap only surfaced at the *first live capture* — after v0.57.0 shipped. This is
  not broad-exploration waste; it is a verification-phase gap: the claim-fidelity
  ship asserted a behavioral floor that no live capture had ever exercised.
  Causal root: a passive prose pointer in SKILL.md ("route via expert-lens.md")
  is satisfiable from inlined text, so a capable agent skips the actual read —
  exactly the failure the planner-first family was built to remove, but `retro`
  was left out of that sweep.
- **No double-counting:** the planner-absence itself was correct prior scoping
  (the 6/23-24 sweep was bounded); the waste is specifically that the *later*
  claim-fidelity sweep calibrated against the un-evolved shape instead of
  treating planner-absence as a blocker for asserting the floor.

## Critical Decisions

- **Treat the floor miss as a calibration signal, not a matcher to soften.**
  Per the handoff contract, the live miss re-pinned the skill (extract a planner)
  rather than relaxing `requiredCommandFragments`. Skipped alternative: drop or
  weaken the fixture assertion to make it green. Constraint created: the fix had
  to make the behavior real, which is the more expensive but correct path.
- **Extract a real planner instead of strengthening the prose pointer.** Chosen
  to match the debug/handoff/quality/issue/gather/release family (uniform skill
  structure, planner-anchored floor). Skipped: bolt a louder "MUST READ" note
  onto SKILL.md. Constraint: `hitl` is now the lone planner-absent skill, and the
  methodology spec's "retro has no planner" comment is now stale (deferred to
  task 18).
- **Floor-flip is structurally proven, not yet eval-proven (`moderate`).** This
  run shows the planner briefs Engelbart and routes `expert-lens.md` as
  unconditional, and I consulted it — so the failed→proven flip is demonstrated
  in a real `/charness:retro` run. But this was the slash command, not a
  `cautilus evaluate` capture; the formal paid re-capture (commit's named next
  step) is what converts this to `strong`. I am not claiming the eval passed.

## Expert Counterfactuals

- **Engelbart — system-improving-itself (H + LAM + T as one unit)** (briefed lens,
  on-the-nose for self-improvement work). The sweep evolved the *tooling* (T:
  fixtures + static-calibration method) without co-evolving the *method/language*
  (LAM: planner-first routing) for retro. A fixture (T) asserted a floor the
  skill's routing method (LAM) could not deliver because the planner (also T)
  did not exist — so the measurement tool was calibrated against an un-evolved
  method and dutifully froze the gap. Engelbart's actionable difference:
  planner-first routing should have been a **co-requisite** of asserting any
  per-skill behavioral floor, not something 2 of 20 skills were left out of.
  Co-design the floor and the routing mechanism, and validate against the
  human-in-the-loop live behavior, not the static artifact.
- **Charity Majors — observability / you cannot know behavior without watching it
  run** (divergent domain lens). A static-fragment match is a proxy with a
  construct-validity gap: it measures "does the text mention expert-lens.md," not
  "did the agent consult the lens catalog." Majors' difference: a behavioral
  floor is a production claim — gate the claim-fidelity *ship* on at least one
  live capture per asserted-behavior fixture, the eval equivalent of not shipping
  a code path you never executed. Live capture before assertion, not after.
- Convergent actionable upgrade from both: **live-capture-before-assert** —
  treat the pinned live-capture validation phase as a precondition for keeping
  behavioral floors green, not a follow-on audit.

## Sibling Search

Transferable pattern: *a passive prose pointer in SKILL.md, satisfiable from
inlined text, that a capable agent skips — and a static fixture that freezes the
gap as passing.*

- same layer: `hitl` skill (the other skill left planner-absent by the 6/23-24
  sweep, named in the root cause) | decision: valid follow-up outside the slice |
  proof: `git show a7e49790` root-cause names "retro + hitl were left
  planner-absent" | follow-up: deferred `docs/handoff.md` live-capture validation
  phase (the pinned next task covers per-skill capture; hitl is in scope)
- abstraction up: the claim-fidelity methodology itself — it calibrates
  fidelity-to-current-shape, and the spec `_comment` still asserts "retro has no
  planner" | decision: valid follow-up outside the slice | proof: commit
  `167cad5c` message defers the spec correction to task 18 after re-capture |
  follow-up: deferred `docs/handoff.md` (claim-fidelity methodology change, task 18)
- specialization down: the other 18 public-skill fixtures, all statically
  calibrated and never live-captured | decision: valid follow-up outside the
  slice | proof: `docs/handoff.md` "no live captures have run" | follow-up:
  deferred `docs/handoff.md` live-capture validation phase
- mental-model siblings: any required_read routed by a prose "see X" pointer
  rather than a planner-emitted `required_read` across the non-planner skills |
  decision: same waste, fix now (for retro, fixed by this slice's planner
  extraction) | proof: `167cad5c` makes expert-lens.md an unconditional
  `required_read`; the planner-first family already covers the 6 evolved skills

Structural-follow-up destination: `valid follow-up outside the slice` →
`repo-local guard: docs/handoff.md` live-capture validation phase (already
pinned). No new issue filed: the handoff anchor already owns the de-frozen-floor
follow-ups for hitl, the methodology spec, and the remaining fixtures.

## Next Improvements

- workflow: Make **live-capture-before-assert** the rule for behavioral floors —
  do not ship a `requiredCommandFragments` floor that asserts a *behavior*
  (opening a file, consulting a catalog) until at least one live capture has
  exercised it. Static calibration is allowed for shape, never for asserted
  behavior. (Direct consequence of the Majors lens.)
- capability: The `retro` planner now exists; complete uniformity by giving
  `hitl` the same planner-emitted `required_reads` so no public skill routes a
  mandatory read through a passive prose pointer. Tracked under the pinned
  live-capture phase rather than a new issue.
- memory: This artifact + the recent-lessons digest record the
  static-calibration-freezes-behavioral-gaps trap so the live-capture validation
  phase reads it as a precondition, not a discovery. The methodology spec's stale
  "retro has no planner" comment is the one durable correction still owed
  (task 18, deferred to post-re-capture per `167cad5c`).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-29-session-retro.md
