# Achieve Goal: Aggregate author-time preflight for general doc/markdown surfaces (resolve #362)

Status: draft
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-general-doc-authoring-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (pursue-ready draft).
- Current slice intent: before activation. The reviewable-intent unit in progress
  and the commits it spans; critique and broad proof do not re-fire within one
  unchanged intent — update it when the intent changes, not per commit
  (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-14-general-doc-authoring-preflight.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve [#362](https://github.com/corca-ai/charness/issues/362): give general
doc/markdown surfaces (`docs/handoff.md`, `docs/*.md`) an **aggregate author-time
preflight** that surfaces, in one pass before the commit gate, the constraints an
author currently discovers by failing one gate at a time — markdownlint rules
(wrapped inline-code-span, `MD004` list-marker style, etc.), `check_doc_links`
pathy-ref/link form, and the length/cap floors (`validate_handoff_artifact`'s
70-line cap, doc length). This is the **describe-first absorption** pattern A2
just brought to goal-closeout and `check_skill_surface_preflight.py` (#284)
brought to SKILL.md, extended to general docs — closing the Problem-1
authoring-churn residual on the one surface class that still lacks it.

## Non-Goals

- **Not a new blocking floor/gate.** Per the Floor-Addition Restraint checklist,
  this is a describe-first affordance that *absorbs* the existing gates' shape up
  front, not a new serial gate. The existing gates stay the enforcement.
- **Not re-implementing the gates.** The preflight forecasts/aggregates the SAME
  constraints the existing validators enforce (shell out to / reuse markdownlint,
  `check_doc_links`, `check-markdown`, the handoff cap) — it must not fork their
  logic and drift, mirroring how A2 reused `check_complete_evidence`.
- **Not skill surfaces.** `check_skill_surface_preflight.py` already owns
  `SKILL.md` / `references/**`; this is the *general docs* gap it does not cover.
- No cross-repo work; no prompt-behavior change requiring live Cautilus.

## Boundaries

- charness-internal only. A new repo-root authoring tool (likely
  `scripts/*.py`) — run the portability classification at closeout
  (host-local authoring helper vs a generalizable capability that a consuming
  repo's docs would also want), since adding a repo-root `scripts/*.py` is a
  `follow-up:portability-classification-tripwire` trigger.
- Stay a non-blocking affordance — a goal/doc must still commit without running
  it (guards against a future hand converting the affordance into a precondition).
- This goal **resolves tracked issue #362**; the issue-closeout floor applies
  (stage the close through `issue`).
- External side-effect scope: none beyond a normal local closeout; any push is
  operator-approved at the bundle boundary, not per slice.
- Discuss before activation: resolved: the two consequential signals are settled by
  the goal's design and need no operator decision before activation — (1) issue
  closeout (#362) is the goal's explicit purpose (the close is staged through `issue`
  at the goal's own closeout, not a surprise side effect); (2) the proof non-claim
  (no live Cautilus / no release coupling in the goal) is the correct default for
  additive charness-internal tooling. No cross-repo work, no floor removal, no
  irreversible side effect.

## User Acceptance

- Running the new preflight on a doc that violates several constraints (a
  deliberately-broken `docs/*.md` fixture: a wrapped inline-code-span + an
  `MD004` `+`-bullet + a backticked pathy ref + over the length cap) emits **all
  of them in one call**, not one per failed commit — hand-runnable.
- A real `docs/handoff.md` edit drafted from the preflight output passes the
  commit gate on the **first** attempt (zero serial-rejection rounds on the
  constraints the preflight surfaces).

## Agent Verification Plan

### Low-Cost Checks

- Unit tests: a fixture doc carrying each violation class → the preflight surfaces
  each; a clean doc → silent. Forecast matches the real gate verdict (no drift).
- `validate_skills` / length / `check_doc_links` / `check-markdown` pass for the
  new tool and any doc edits.

### High-Confidence Checks

- A handoff/doc edit built from the preflight output passes `check-markdown.sh`,
  `check_doc_links.py`, and `validate_handoff_artifact.py` first try.
- `run_slice_closeout.py` bundle boundary green; `plugins/` mirror synced if a
  packaged surface is touched.

### External Or Live Proof

- None required; explicit non-claim — no live Cautilus / no release coupling in
  the goal itself (release is a separate operator-approved step).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Build the aggregate doc-surface preflight: given a target `docs/*.md`/handoff path, forecast the markdownlint + doc-link + length/cap constraints in one report (reusing the real validators, not forking them) | the Problem-1 residual the session's handoff churn exposed (5+ serial rejections) | broken-fixture unit test (all violation classes surfaced) + clean-fixture silence; no-drift vs the real gates | planned |
| S2 | Wire it into the authoring flow (implementation-discipline "before authoring into a gated surface" guidance; optionally a slice-closeout advisory) and stage the #362 closeout | makes the affordance discoverable at the point of edit; closes the tracked issue | grep wiring; first-try clean handoff edit; `issue_tool.py validate-closeout-draft`/`verify-closeout` for #362 | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [#362](https://github.com/corca-ai/charness/issues/362) — the tracked issue this
  goal resolves (observed churn + the precedent shape of a fix).
- `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md` —
  the `## Waste` evidence (the concrete handoff rejection sequence) the issue cites.
- `skills/public/achieve/scripts/describe_goal_closeout_shape.py` — the A2
  goal-closeout describe-first precedent to mirror (reuse the real check, no drift).
- `scripts/check_skill_surface_preflight.py` — the #284 skill-surface preflight
  precedent (the SKILL.md-only coverage this goal extends to general docs).

## Interview Decisions

- **Shape of the fix:** chose an *aggregate describe-first preflight that reuses
  the real validators*, over (a) a new blocking gate (rejected — the Floor-Addition
  Restraint reflex) and (b) re-implementing the lint/link/length checks (rejected —
  drift risk; A2's lesson is reuse the live check). The fix absorbs existing gates
  up front; it does not add or fork enforcement.
- **Surface scope:** general docs (`docs/*.md`, `docs/handoff.md`) only — SKILL.md
  surfaces are already covered by `check_skill_surface_preflight.py` (#284), so
  this is the residual gap, not a re-do.

## Plan Critique Findings

Pre-activation premortem light (additive, charness-internal). Worth stressing when
it runs: (a) **no-drift** — the preflight must forecast by invoking/reusing the
real validators (markdownlint, `check_doc_links`, the handoff cap), never a hand
copy that drifts from what the gate enforces; (b) **stays an affordance** — a doc
must still commit without it, asserted by a test (the C5-style non-blocking guard);
(c) **portability** — classify the new repo-root script host-local vs
skill-capability before closeout (the portability-classification tripwire).

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
