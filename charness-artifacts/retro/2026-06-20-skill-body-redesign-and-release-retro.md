## Mode

session (goal closeout — skill-body-redesign-and-release)

## Context

Goal `2026-06-20-skill-body-redesign-and-release`: diagnose all 20 public
SKILL.md bodies (diagnosis-first), cure where the length-cause warranted, defer
justified-density bodies with cause, then cut a live release exercising the WS-1
non-terminality floors. Outcome: **18 cured, 2 deferred-with-cause** (hotl
justified-density; quality contract-pinned → operator ODQ); **live release
v0.53.0 published** and independently confirmed via channels distinct from
`gh release view`.

## Evidence Summary

- S0 diagnosis workflow (40 agents: 20 diagnose + 20 adversarial verify) →
  `charness-artifacts/spec/2026-06-20-skill-body-diagnosis-disposition.md`.
- Host-log probe (claude scope): `2026-06-20-skill-body-redesign-and-release-host-log.md`
  — 564 token snapshots, 239 function calls, 73 patch applications, 7 subagent
  spawns (thread-wide proxy; no per-goal window was recorded).
- Commits dfb2aa52 (S0) … v0.53.0 publish; broad pytest at the bundle boundary.

## Waste / The Miss

- **The `fail-fast` miss reached the broad release gate.** The S2 achieve
  guardrail collapse dropped the 9-char token `fail-fast` (under the pre-cut
  check's 24-char scan), and my S2 pinned-test sweep ran a *fixed* set of test
  files that did not include `test_achieve_before_activation.py`, so the break
  survived to `run-quality.sh --release`. The cost was a partial-bump abort +
  cleanup. Lesson: for a body cure, run the tests that actually pin THAT skill
  (grep `tests/` for the skill id), not a remembered subset.
- **dup-ratchet accumulates silently.** It runs only at the release boundary, so
  31 new + 29 removed code families had accumulated across the whole unreleased
  range (Phase-4 + this goal) and only surfaced at publish — forcing a re-baseline
  mid-release. Designed behavior, but the late surfacing cost a publish round-trip.

## Critical Decisions

- **Diagnosis-first with adversarial verify was the load-bearing decision.** The
  fan-out diagnosis + a second verifier per body caught that 4 of 20 proposed
  cures (issue/impl/find-skills/retro) would break a pin the diagnosing agent
  missed — and the per-cure pre-cut check + pinned-test sweep caught ~6 more
  during execution. Diagnosis is a hypothesis; the instrument stack is what made
  it safe.
- **Deferred quality with cause instead of forcing a test-breaking cut.** The
  `## Load-Bearing Anchors` catalog is pinned by ~25 `test_quality_skill_docs.py`
  assertions; collapsing it is a contract change, so the cure correctly converted
  to defer-with-cause + operator ODQ. This is the goal's binding constraint 3
  working exactly as designed — and the proof that count was not the metric.
- **Re-baselined dup-ratchet at the release boundary** (the gate's prescribed
  "deliberately accept" path; +31/-29 reviewed churn, predominantly intentional
  per-skill portability boilerplate).

## Expert Counterfactuals

- **Tony Hoare / design-by-contract lens:** the test-pinned literals ARE the
  consumer contract for each skill body; the value of the S0 pre-cut check was
  making that contract *checkable before the cut* instead of at a late gate. A
  contracts-first reviewer would have, from the start, treated "what tests assert
  this body" as the first question of every cure — which is exactly the per-skill
  pinned-test sweep the `fail-fast` miss now mandates.
- **Goodhart counterfactual:** had I optimized line count, I'd have forced the
  quality and hotl cuts (and broken ~25 tests). Leading with the clarity/capability
  delta (the operator's count-is-not-the-metric framing) produced 2 honest defers.

## Next Improvements

- **workflow:** body cures run the skill's *own* pinned tests (derive from
  `grep -rl <skill-id> tests/`), not a fixed sweep. This would have caught
  `fail-fast` at S2 instead of the release gate.
- **capability:** `check_skill_cut_safety.py` could map a changed skill → its
  pinned test files and surface short (<24-char) literals from *those* tests,
  closing the documented blind spot deterministically. Tracked as a follow-up,
  not built this goal (the pinned-test sweep + fresh-eye already backstop it).
- **memory:** "diagnosis is a hypothesis; the deterministic pre-cut check catches
  ≥24-char pins, the skill's pinned tests catch short ones, fresh-eye catches
  losslessness" — the layered stack is the durable lesson.

## Sibling Search

The short-pin (<24-char) blind spot is a transferable pattern in any
prose-pin-diff gate (`check_prose_pin` and everything composed on it). The
backstop (run the surface's own pinned tests + fresh-eye) generalizes. The
dup-ratchet release-only-accumulation is a sibling pattern in any
release-boundary-only gate. Neither warrants a new gate this goal; both are
documented here + in the disposition spec's blind-spot note.

## Persisted

yes — charness-artifacts/retro/2026-06-20-skill-body-redesign-and-release-retro.md
