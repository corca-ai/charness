# Reviewer Delivery Seam
Date: 2026-07-25
Source: forced risk interrupt in
[charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md](../debug/2026-07-25-bounded-reviewer-result-delivery.md)
(`Risk Class: external-seam, repeated-symptom`)

## Problem

Reviewer result delivery crosses a seam charness does not own. The parent spawns
a bounded reviewer, the host chooses a delivery channel based on a caller-supplied
parameter, and the findings either arrive in the parent's context or vanish
silently. #454 shipped the immediate fix — spawn unnamed, and record a typed
`Delivery state` at closeout — but that fix is a workaround for an open upstream
defect, proven on exactly one host at one version.

The forced interrupt exists because two things are true at once: the seam is
external (`external-seam`) and this is the third occurrence of the same class
(`repeated-symptom`, recorded 2026-06-20, mis-attributed 2026-07-16 and 07-17).
A fix that holds only on the probed host, plus a lesson-decay mechanism still
live, is what turns a fixed bug into a fourth occurrence.

## Capability Contract

Charness can **influence** the delivery channel (spawn call shape) and **record**
the outcome (`findings-received` / `spawn-accepted-no-delivery <signal>`). It
cannot **guarantee** delivery, because the transport belongs to the host runtime.
Every contract surface must stop at detect-and-report; any wording that implies a
guarantee is a defect.

## Current Slice (shipped in v2.6.0)

- `## Result Delivery` in the shared fresh-eye reference owns the rule.
- Typed `Delivery state` floor in `scripts/critique_reviewer_evidence.py`, kept
  separable from boundary state.
- Availability probe passes only when findings text reaches the caller.
- Pinned by `tests/quality_gates/test_reviewer_result_delivery.py` and
  `tests/quality_gates/test_critique_delivery_state_floor.py`.

## Fixed Decisions

- The rule lives in a contract plus a validator floor, never in a rolling lesson
  digest. Decay is what caused the recurrence.
- Delivery state and boundary state are independent claims. Rail 1 proves only
  the second; a green fingerprint must never read as a received review.
- The unnamed-spawn requirement is a **workaround for a live upstream defect**
  (anthropics/claude-code#71723), not a permanent fact about spawning.
- The invariant "a spawned reviewer is not a received review" survives the
  upstream fix. Only the spawn-shape rule is contingent.

## Probe Questions

1. **Host plurality.** Does the named/unnamed differential exist on Codex
   (`explorer`)? On other Claude Code versions? The current rule is a no-op on any
   host whose spawn surface has no addressing parameter — is that stated clearly
   enough that an operator on such a host does not think they are protected?
2. **Upstream close.** When #71723 closes, re-run the A/B differential. If named
   spawns deliver, does the unnamed rule relax to a preference, and does anything
   in the repo still hard-require it?
3. **Lesson decay (D38).** Can a retro "Next Improvement" that never reaches a
   contract be detected? What distinguishes a lesson that *should* decay from one
   that should not? This is the mechanism behind the five-week recurrence and is
   deliberately unaddressed.
4. **Delivery-state consumption.** The typed states are now required at critique
   closeout. Should `quality`, `release`, and `setup` closeouts require them too,
   or does the critique carrier cover every reviewer-spawning path?

## Deliberately Not Doing

- No artifact-drop fallback channel (reviewers writing findings to a known path).
  The read-only reviewer envelope has no write tool by design, so that shape would
  trade the #428 boundary for delivery. Reconsider only if the unnamed shape stops
  working on a supported host.
- No attempt to guarantee delivery or to detect a named spawn statically. Rail 1
  is git-state only by design, and the closeout field is the intended detector.

## Non-Goals

- Fixing the upstream defect. Charness workarounds it and records the lineage.
- Re-litigating the #428 reviewer boundary rails.

## Constraints

- Portable surfaces stay host-plural and carry no issue anchors (the public-doc
  coupling gate holds `skills/shared/references/` at zero anchors).
- Any new floor keeps the `RULE_DATE = landing_day + 1` grandfather shape and a
  closed legacy allowlist, never a fail-open default.

## Success Criteria

- The named/unnamed differential is either confirmed or refuted on at least one
  non-Claude-Code host, with the result recorded as a live claim rather than
  assumed.
- A reviewer-spawning closeout on any supported host can state delivery honestly,
  including `spawn-accepted-no-delivery <signal>` when the channel drops it.
- No fourth occurrence of the class: either D38 lands, or the next recurrence is
  caught by the delivery floor rather than by a human noticing silence.

## Acceptance Checks

- `python3 -m pytest tests/quality_gates/test_reviewer_result_delivery.py tests/quality_gates/test_critique_delivery_state_floor.py`
- A critique artifact dated on/after 2026-07-26 cannot validate without a typed
  `Delivery state`, and a bolded or backticked `spawn-accepted-no-delivery`
  cannot skip the signal requirement.
- `charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md`
  remains the cited lineage for this seam.

## Critique

Owed on any slice that acts on the probe questions above. The #454 slice itself
carried its own bounded fresh-eye critique
([resolution](../critique/2026-07-25-issue-454-resolution-critique.md),
[release](../critique/2026-07-25-v2-6-0-release-critique.md)); this spec inherits
those and does not re-open them.
