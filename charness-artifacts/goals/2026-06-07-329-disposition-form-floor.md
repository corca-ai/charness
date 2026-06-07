# Achieve Goal: Reject invalid prose-only retro dispositions with a form/enum floor (#329)

Status: complete
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-329-disposition-form-floor.md`

This file is the living goal scratchpad, shaped at the end of the
`2026-06-07-330` session (right after #330 closed) at the operator's "다음 청크
어치브로 잡아주세요" request. It becomes active only when the user runs the
activation command; shaping happened, no slices were executed.

## Active Operating Frame

- Current slice: COMPLETE — S1–S4 done; floor landed, reviewed, closeout evidence bound, `check_goal_artifact` green.
- Next action: commit (staged `Closes #329`) + push (approved lane) + `verify-closeout --expect-state CLOSED`.
- Activated 2026-06-07; reach lever resolved to the recommended **BOTH** (achieve Auto-Retro + session retro) since activation did not re-point. Primary unchanged: #329.
- S1 contract (resolved):
  - **Valid forms** (markdown-tolerant, leading-token enum): `applied …` (leading token `applied`), `issue/issues … #N` (leading `issue(s)`/`#N` AND contains `#\d+`), `none [—–:-] <reason>` (separator + non-empty reason).
  - **Invalid (rejected):** bare `memory` / `memory -> …` / prose-only / unfiled `issue` with no `#N` / bare `none`. Form only — vague-but-valid `applied: tweak` passes (never a content classifier).
  - **Parse surface:** `Disposition:` (per-improvement) + `Retro dispositions:` (aggregate) lines, fence-masked; achieve scopes to `## Auto-Retro`, retro scopes to `## Next Improvements`. Untouched `TODO/<…>` placeholders are skipped (rung 1a owns block-the-blank).
  - **Enforce-from-date = 2026-06-08** (`DISPOSITION_FORM_RULE_DATE`), `observed >= date` enforced, fail-closed on undatable. Set to the day AFTER today so #330 (frozen `complete`, Created 2026-06-07, carries `memory ->`/`fix (folded)`), this #329 goal, and the triggering retros are all grandfathered — honoring the Goodhart Non-Goal. The floor takes effect for next-session artifacts; tests exercise it with synthetic future/past dates.
  - **Home:** shared leaf `scripts/disposition_form.py` (single source of grammar; ships to `plugins/charness/scripts/`); achieve folds it into `apply_disposition_rungs` (wrapper at 348/360 — untouched); retro validator imports it same-root.
- Mode: spec-light — one small validator + wiring; promote to a `spec` only if the floor needs a shared disposition-grammar surface reused by more than the two call sites.
- Timebox: 8h
- Activation time: 2026-06-07
- Closeout reserve: 90m
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
| S1 | Define the disposition-form contract: valid prefixes (`applied:`, `issue #N`, `none — <reason>`), invalid (bare `memory` / prose-only); decide the parse surface (Auto-Retro `Retro dispositions:` lines + per-line dispositions) + the enforce-from-date + the reach (achieve-only vs +session-retro) | Foundation for #329; the issue names the template and the cardinal "form not substance" rule | a written form spec + the enforce-date + the reach decision | done (frame S1 contract) |
| S2 | Implement the form/enum check + tests (negative guards: bare `memory ->` fails; the 3 valid forms pass; pre-date grandfathered; vague-but-valid form passes) | The core of #329 | checker + tests; a `Disposition: memory` line fails, `applied:`/`issue #N`/`none — <reason>` pass | done (`scripts/disposition_form.py` + 18-case test) |
| S3 | Wire the floor into achieve goal closeout (`goal_artifact_disposition`/`check_goal_artifact`) and — per the Discuss reach decision — `validate_retro_artifact` for session retros, with enforce-date grandfathering | Make it a standing gate at the surfaces where invalid dispositions actually shipped | gate runs; appears in closeout + (if extended) session-retro validation | done (BOTH surfaces wired; mirror synced) |
| S4 | Close #329 + bundle verify + bounded critique + retro | Closeout | staged close; broad pytest; fresh-eye critique; validate-closeout-draft | done (broad pytest 2567 passed; SHIP-WITH-NITS critique folded; retro; check_goal_artifact green) |

## Coordination Cues

Routing deferred to `find-skills` — no hard-coded phase→skill map here. Filled
during the run:

- Routing: find-skills routed to achieve = impl + quality + issue (issue-phase = close #329 + file off-goal #332); read-only, local-first, no support/integration/external route returned — the work is in-repo validator + gate wiring.
- Gather: n/a — no external source to fetch; all context is in-repo issues and
  validators (the #329 GitHub issue is the tracked-issue reference, not a gather
  source).
- Release: n/a — no shipped runtime capability warrants a version bump; this is an
  internal validator/closeout-gate change only.
- Issue closeout: #329 — direct-commit carrier; staged `Closes #329`; then
  `verify-closeout --expect-state CLOSED` proof after push.

## Slice Log

- **S1–S3 (impl bundle), 2026-06-07.** Landed the disposition-form floor.
  - New shared leaf `scripts/disposition_form.py` (single source of grammar):
    `evaluate_disposition_form` (markdown-tolerant leading-token enum), `scan_dispositions`
    (fence-masked marker scan of `Disposition:`/`Retro dispositions:`), `invalid_dispositions`,
    `is_form_enforced` (`DISPOSITION_FORM_RULE_DATE = 2026-06-08`, fail-closed). Ships to
    `plugins/charness/scripts/`.
  - Achieve: `goal_artifact_disposition.apply_disposition_form_floor` (rung 1c) loads the shared
    leaf via parent-walk; runs first inside `apply_disposition_rungs` on its own enforce-date;
    scopes `## Auto-Retro`; sets `report["disposition_form"]` + `ok=False`. Wrapper untouched
    (was 348/360).
  - Session retro: `validate_retro_artifact.validate_disposition_forms` scopes `## Next
    Improvements`, keys enforce-date off the retro `Date:` line; raises `ValidationError`.
  - Proof: targeted 18-case test green; existing disposition/retro/goal-artifact suites 102 green;
    ruff/lengths/export-safe/plugin-import-smoke green; mirror synced. Corpus safety: 0 completed
    goals retroactively form-failed (Goodhart Non-Goal honored — all Created ≤ 2026-06-07).

- **S4 (closeout), 2026-06-07.** Bundle verify + fresh-eye critique + retro + close.
  - Broad pytest: 2567 passed, 4 skipped (the only failure — a self-introduced preflight
    regression — was folded; see below).
  - Bounded fresh-eye review (parent-delegated, independent context): SHIP-WITH-NITS;
    both real findings folded before ship — (1) dateless historical retros were
    fail-closed into enforcement → filename-date fallback; (2) `none-actionable`
    compound-word false-accept → separator tightening. Critique:
    `charness-artifacts/critique/2026-06-07-issue-329-disposition-form-floor.md`.
  - Two self-introduced gate regressions surfaced by the broad gate and folded:
    portable-package issue anchors in the achieve leaf (`validate_skill_ergonomics`)
    and a stray `skipped` term (`validate_attention_state_visibility`). Generalized as
    off-goal **#332** (recurring authoring-preflight trap #308/#325/#329) and the retro's
    main waste lesson.
  - Retro `charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md`
    (dogfooded with valid disposition forms). `check_goal_artifact` green.

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

- **#332 — authoring-preflight / commit-boundary structural-sweep is not reliably
  run on new skill-package + script edits (recurring #308/#325/#329).** Filed
  upstream-harness. Surfaced as this session's biggest waste: two self-introduced
  gate regressions (portable-package issue anchor + attention-state `skipped` term)
  caught only at the broad-pytest boundary though both are commit-boundary gates.
  Out of #329 scope (gate automation, not the disposition floor); recorded here per
  the off-goal-findings contract.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` or an explicit
`skipped: <allowed-reason>: <detail>` before flipping to complete.

Retro: charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md
Host log probe: skipped: host-log-not-exposed: no host/runtime behavior is claimed (External Or Live Proof = none); the proof is broad pytest (2567 passed) + the standing deterministic gates, not a host/runtime probe, so there is no host log to probe.
Disposition review: charness-artifacts/critique/2026-06-07-issue-329-disposition-form-floor.md

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

Retro dispositions: applied + issue #332 + none — every surfaced improvement is
dispositioned in `charness-artifacts/retro/2026-06-07-issue-329-disposition-form-floor.md`
`## Next Improvements`; restated per-improvement below (all valid forms, dogfooding
the floor this goal lands):

- Recurring commit-boundary structural-sweep trap (3rd instance #308/#325/#329; two
  self-introduced gate regressions caught only at broad pytest). Disposition: issue #332.
- Enforce-from-date grandfather needs a corpus/identity-aware fallback, not a single
  date-line parse. Disposition: applied: landed the filename-date fallback in
  `validate_retro_artifact._retro_observed_date` + regression tests this run.
- Extend the floor's reach to other disposition emitters. Disposition: none — the two
  surfaces #329 named are gated at source and derived digests inherit it; no third
  surface has shipped an invalid form, so no new teeth are warranted yet.
