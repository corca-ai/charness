# Achieve Goal: Reject invalid prose-only retro dispositions with a form/enum floor (#329)

Status: draft
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-329-disposition-form-floor.md`

This file is the living goal scratchpad, shaped at the end of the
`2026-06-07-330` session (right after #330 closed) at the operator's "다음 청크
어치브로 잡아주세요" request. It becomes active only when the user runs the
activation command; shaping happened, no slices were executed.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-07-329-disposition-form-floor.md`, then re-confirm the primary + the one open scope lever against `## Discuss Before Activation`.
- Mode: spec-light — one small validator + wiring; promote to a `spec` only if the floor needs a shared disposition-grammar surface reused by more than the two call sites.
- Timebox: until #329 is resolved; re-pick the next slice at each boundary.
- Activation time: set by the next session at `/goal`.
- Closeout reserve: keep the last boundary for bundle verify + one bounded fresh-eye critique + retro.
- Done-early policy: continue_next_improvement (if #329 lands early, re-point to #184 with an explicit ideation/spec scope reset, not a quick slice).
- Verification cadence: cheap deterministic checks at commit boundaries; targeted `pytest` + fresh-eye review at slice boundaries; broad `pytest` + one bounded `critique` at the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed files and owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

**Primary: resolve #329 — a narrow presence/enum (form) floor that rejects a
known-invalid retro disposition value and requires a valid one.** For each
emitted disposition, reject the bare `memory` / prose-only form and require one
of:

- `applied: <committed change>` (a gate / hook / validator / test / code change),
- `issue #N`, or
- `none — <reason>` (only when nothing is actionable).

It judges only the disposition **form**, never whether the generalization is
good — that stays the reviewer's/human's job (mirrors
`scripts/check_python_lengths.py`'s "prove it, human judges substance" and the
achieve disposition floor's "never a content classifier"). Build it on the
`scripts/validate_proposal_fields.py` presence/enum shape (the issue's named
template), extending the existing presence/binding gate
(`skills/public/achieve/scripts/goal_artifact_disposition.py`) rather than
forking it. Optionally extend the floor's reach from achieve-goal Auto-Retro to a
standalone **session retro** (which today has no disposition review at all) — the
one real scope lever, surfaced in `## Discuss Before Activation`.

This is the direct dogfood sequel: this very session's #330 retro + goal
Auto-Retro emitted `Disposition: memory ->` lines, exactly the form #329 says the
floor must reject.

## Non-Goals

- Do NOT make the floor a content/semantic classifier. It judges the disposition
  *form/enum value only*; it never decides whether the lesson is worth keeping or
  the generalization is honest (the cardinal rule, repeated verbatim in the
  achieve guardrails).
- Do NOT rewrite or retroactively fail frozen historical retros — that is
  Goodhart's law (the original author never had this floor). Enforce from a date
  forward, mirroring `validate_inventory_consumption.py`'s `ENFORCED_FROM_DATE`.
- Do NOT remove or weaken the existing presence/binding disposition gate; this
  adds a form check beside it.
- #184 (product metrics) is product-level and needs `ideation`/`spec`; it is a
  done-early re-point with an explicit scope reset, not in this goal's scope.

## Boundaries

- External side-effect scope: direct-commit carrier; the push that lands the
  primary closes #329 via the staged close keyword. Approval is phase-scoped and
  does not carry forward — after the approved push lane, done-early test-only
  continuation is local by default (batch remote proof, run the pre-push gate once
  over the final bundled state).
- Reuse the `validate_proposal_fields.py` presence/enum parser shape and extend
  the existing `goal_artifact_disposition.py` gate; do not fork disposition
  parsing. The enforce-from-date grandfathers historical retros.
- Discuss before activation: Resolved (shaped defaults; the operator may re-point
  at `/goal`) — primary is #329; proof is local deterministic plus broad pytest
  with no live/prod/provider proof; #329 closes via a direct-commit staged
  keyword; the historical retro corpus is grandfathered via an enforce-from-date;
  the one open lever (achieve-only vs also-session-retro reach) is recommended as
  BOTH and detailed in `## Discuss Before Activation`.

## User Acceptance

What the user can do to verify completion directly:

- Add a `Disposition: memory` (or otherwise prose-only) line to a goal Auto-Retro
  (and, if the reach is extended, a session retro) → the floor fails; rephrase it
  to `applied: <…>` / `issue #N` / `none — <reason>` → it passes. (Demonstrate the
  negative.)
- Confirm the floor does NOT judge substance: a present-but-vague `applied: tweak`
  still passes (form only), proving it is not a content classifier.
- Confirm a pre-enforce-date historical retro with `Disposition: memory` is NOT
  failed (grandfathered).
- #329 closed (staged close keyword) with the floor landed and tested, and a
  `validate-closeout-draft` proof recorded.

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` for the new disposition-form floor (valid forms pass; bare
  `memory` / prose-only fails; enforce-date grandfathering).
- `ruff`, `check_python_lengths` on touched files at commit boundaries.

### High-Confidence Checks

- Broad `pytest` over the standing targets at the bundle boundary.
- One bounded fresh-eye `critique` (issue-closeout review) before close.

### External Or Live Proof

- None required. Local deterministic + broad-pytest only; the pre-push gate
  (full `run-quality.sh` read-only) is the bundle attestation, run once over the
  final state.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Define the disposition-form contract: valid prefixes (`applied:`, `issue #N`, `none — <reason>`), invalid (bare `memory` / prose-only); decide the parse surface (Auto-Retro `Retro dispositions:` lines + per-line dispositions) + the enforce-from-date + the reach (achieve-only vs +session-retro) | Foundation for #329; the issue names the template and the cardinal "form not substance" rule | a written form spec + the enforce-date + the reach decision | planned |
| S2 | Implement the form/enum check + tests (negative guards: bare `memory ->` fails; the 3 valid forms pass; pre-date grandfathered; vague-but-valid form passes) | The core of #329 | checker + tests; a `Disposition: memory` line fails, `applied:`/`issue #N`/`none — <reason>` pass | planned |
| S3 | Wire the floor into achieve goal closeout (`goal_artifact_disposition`/`check_goal_artifact`) and — per the Discuss reach decision — `validate_retro_artifact` for session retros, with enforce-date grandfathering | Make it a standing gate at the surfaces where invalid dispositions actually shipped | gate runs; appears in closeout + (if extended) session-retro validation | planned |
| S4 | Close #329 + bundle verify + bounded critique + retro | Closeout | staged close; broad pytest; fresh-eye critique; validate-closeout-draft | planned |

## Coordination Cues

Routing deferred to `find-skills` — no hard-coded phase→skill map here. Fill
during the run:

- **Routing** — query `find-skills` per phase; #329 is `impl` + `quality`; record
  the route returned.
- **Gather** — `Gather: n/a — no external source; all context is in-repo issues
  and validators.`
- **Release** — `Release: n/a unless a shipped capability warrants a version
  bump.`
- **Issue closeout** — #329; direct-commit carrier; staged close keyword;
  `validate-closeout-draft` (draft, before commit) then `verify-closeout
  --expect-state CLOSED` proof.

## Slice Log

## Context Sources

A fresh session can reconstruct context from, in order:

- **#329 issue body** (https://github.com/corca-ai/charness/issues/329): the
  observed problem, the named template (`validate_proposal_fields.py` enum shape),
  the cardinal "form not content classifier" rule, and the optional session-retro
  extension.
- **Template:** `skills/public/issue/scripts/validate_proposal_fields.py`
  (presence/enum validator; `_field_value` markdown-tolerant parser).
- **Existing presence/binding gate to extend:**
  `skills/public/achieve/scripts/goal_artifact_disposition.py`,
  `skills/public/achieve/scripts/check_goal_artifact.py`.
- **Session-retro hook (no disposition check today):**
  `scripts/validate_retro_artifact.py` + `scripts/artifact_validator.py`.
- **Enforce-from-date precedent:** `scripts/validate_inventory_consumption.py`
  (`ENFORCED_FROM_DATE`, frozen-retro grandfathering rationale).
- **Dogfood triggering instances:** the #324 retro named in the issue
  (`charness-artifacts/retro/2026-06-07-324-release-325-322-shaping-session.md`)
  and THIS session's `charness-artifacts/retro/2026-06-07-issue-330-metavalidator-gate-hardening.md`
  (`Disposition: memory ->` lines).
- **Recent lessons digest:** `charness-artifacts/retro/recent-lessons.md`;
  **handoff:** `docs/handoff.md`; **open issues:** `gh issue list --state open`.

## Interview Decisions

- **Primary objective:** options = {#329 disposition-form floor, #184 product
  metrics}. Chosen = #329 (bounded, dogfood-motivated, the direct sequel to a gap
  hit twice incl. this session). Rejected: #184 (needs ideation/spec + an explicit
  scope reset, not a quick slice).
- **Floor shape:** options = {content/semantic classifier of disposition quality,
  presence/enum form check}. Chosen = presence/enum form check (reject the named
  invalid `memory`/prose-only value; require `applied:`/`issue #N`/`none —
  <reason>`), mirroring `validate_proposal_fields.py`. Rejected: a classifier
  (the explicit Non-Goal / achieve guardrail).
- **Historical corpus:** options = {retroactively fail all checked-in retros,
  enforce from a date forward}. Chosen = enforce-from-date (grandfather frozen
  retros), mirroring `validate_inventory_consumption.ENFORCED_FROM_DATE`.
- **Reach:** options = {achieve-goal Auto-Retro only, also standalone session
  retros}. Deferred to `## Discuss Before Activation` (the issue's own triggering
  instances include a session-retro line, so the recommendation is BOTH, but it is
  the larger surface and the one real activation lever).

## Plan Critique Findings

Pre-activation shaping notes (the next session runs the real fresh-eye critique):

- Over-worry raised, not folded: the floor might over-reject a `memory ->` line
  that DID result in a committed change (e.g. this session's `memory ->
  recent-lessons refreshed`). Mitigation: that is the intended behavior, not a
  false positive — such a line should be rephrased `applied: recent-lessons
  refreshed`; the floor's whole point is to force the canonical prefix so
  "committed vs prose-only" is unambiguous. S1 must state this explicitly so it is
  not mistaken for over-reach.
- Blocker watch: do not let the form check drift into judging whether the
  disposition's generalization is good (Non-Goal). Keep it prefix/enum only.

## Off-Goal Findings

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` or an explicit
`skipped: <allowed-reason>: <detail>` before flipping to complete.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After completion: emit a `Disposition: memory` line in a goal Auto-Retro (and, if
extended, a session retro) to see the floor fail; rephrase to `applied: <…>` /
`issue #N` / `none — <reason>` to see it pass; confirm a pre-enforce-date retro is
grandfathered; confirm #329 is CLOSED.

## Discuss Before Activation

The activation decision is resolved to shaped defaults in `## Boundaries`
(primary #329; local + broad-pytest proof, no live; direct-commit close;
enforce-from-date grandfathering). One real lever to confirm or re-point at
`/goal` before the first slice:

- **Reach — the one open decision:** enforce the floor at achieve-goal Auto-Retro
  only, OR also at standalone **session retros** (`validate_retro_artifact`).
  **Recommended: BOTH** — the issue's own first triggering instance was a session
  retro with no disposition review at all, so achieve-only would leave the larger
  hole open. The operator may scope to achieve-only if the session-retro surface
  needs its own enforce-date ramp.
- **Candidate re-point (operator may choose instead of #329):** **#184 — product
  success criteria / core metrics** — larger, product-level; needs `ideation`/`spec`
  and an explicit scope reset, not a quick slice.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
