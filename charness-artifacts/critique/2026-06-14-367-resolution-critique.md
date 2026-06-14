# Resolution Critique — #367 (quality CI-recoverability lens + command_timing_log ingest)

Issue: #367 — `quality` invoked cold would not surface the two largest safe local
gate-speed reductions (no CI-recoverability triage lens; `render_runtime_summary`
cannot ingest an existing command-timing log).

This critique probes whether the resolution actually closes the issue's
job-to-be-done, sits at the right boundary, and prevents the class from
recurring — the issue-resolution critique mandate. It synthesizes two fresh-eye
subagent reviews (slice 1; slices 2+3 bundle, both SHIP) and the rung-2
disposition review.

## Does it close the JTBD?

#367's JTBD: when the operator's goal is *gate speed*, `quality` invoked cold
should drive the safe, CI-backstopped reductions instead of leaning on operator
steering. Resolution:

- The CI-recoverability lens (`inventory_ci_recoverable_gates.py`) directly
  surfaces the two reduction types the issue's filing session had to find by hand
  — it dogfoods on this repo to flag `check-markdown` (CI re-runs it) as a
  move-off-local candidate while keeping `check-coverage`/`pytest`/`specdown`
  local. **JTBD met.**
- The `command_timing_log` adapter key closes the second gap: a repo's existing
  timing log now lights up the wall-clock hot-spot ranking with no hand-rolled
  bridge, so "which gate dominates wall-clock" is default skill output. **JTBD met.**

## Is the boundary right?

Yes. Both surfaces are **advisory-only / inert-by-default**, adding no blocking
floor (Floor-Addition Restraint). The lens is the explicit *counterweight* to the
local-proof guardrail, not a replacement: its load-bearing safety gate — never
flag a gate whose proof CI does not fully re-run — was adversarially probed by the
bundle review and confirmed honest-by-construction (false positives bounded to
"CI textually mentions the tool," surfaced with the `if:`/gate-policy and routed
through the interpretation question; the dangerous "move with zero CI match" path
cannot occur). The local-proof discipline is untouched. The ingest is
schema-mapped (portable), fail-loud on misconfig, signals-authoritative.

## Does it prevent recurrence?

Partially, and honestly bounded:

- The dogfood acceptance evidence (`docs/public-skill-dogfood.json` +
  `EVIDENCE_OVERRIDES[quality]`) now asserts the gate-speed behaviors, so a future
  regression of the cold-invocation gap is caught by the dogfood validator.
- The reference + SKILL.md document the lens and the `command_timing_log` key so
  the capability is discoverable, not tribal.
- **Residual / surfaced gap:** the rung-2 disposition review found that the
  meta-gap exposed during this resolution — a cheap structural check
  (inference-interpretation registration) enforced only by broad pytest, not the
  commit-time sweep — is a *recurrence* of the #314/#319/#332 shift-left class
  (same-day sibling #366), not novel. That recurrence is dispositioned to **#368**
  with the lineage cross-linked, to be resolved as recurrence-conversion via the
  established #314 wiring. This critique endorses that disposition: it is out of
  #367's advisory-only scope, and tracking it prevents a fourth recurrence.

## Verdict

**Resolved.** Both #367 gaps are closed, portable, advisory/inert, and the safety
gate holds. Proof: broad pytest green (3033 passed), two SHIP fresh-eye reviews,
rung-2 disposition review (FIX applied: `novel:`→`recurs:` with lineage). The only
open thread is the correctly-deferred meta-gap #368.
