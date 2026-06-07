# Achieve Goal: Harden the advisory-interpretation contract + close cheap gate-coverage debt

Status: draft
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-330-metavalidator-gate-hardening.md`

This file is the living goal scratchpad, shaped at the end of the
`2026-06-07-issue-328-331` session (after #328 + #331 closed) from the remaining
open-issue list. It becomes active only when the user runs the activation
command; shaping happened, no slices were executed.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-07-330-metavalidator-gate-hardening.md`, then re-confirm the primary against `## Discuss Before Activation` (the operator may re-point to a candidate below).
- Mode: spec-light — small per-check slices; promote to a `spec` only if the meta-validator needs a shared inference-layer surface registry.
- Timebox: until the chosen objective is complete; re-pick the next slice at each boundary.
- Activation time: set by the next session at `/goal`.
- Closeout reserve: keep the last boundary for bundle verify + one bounded fresh-eye critique + retro.
- Done-early policy: continue_next_improvement (if the primary lands early, pick the next candidate below rather than idling).
- Verification cadence: cheap deterministic checks at commit boundaries; targeted `pytest` + fresh-eye review at slice boundaries; broad `pytest` + one bounded `critique` at the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed files and owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

**Primary (recommended): resolve #330 — a meta-validator that enforces the
advisory-interpretation contract across ALL inference-layer surfaces** (the
direct #322 sequel). Enumerate the inference-layer surfaces (the six #322
surfaces plus any added since) and assert each one emits the 4-field
`interpretation` self-declaration (measures / proxy-for / blind-spots /
interpretation-question) AND a paired consumer-must-answer line, while verified
facts are excluded and never carry a declaration. This makes "a new surface
leaks a declaration onto a verified fact, or drops its consumer pairing" a gate
failure instead of a future regression.

Bundled cheap hardening (same gate-coverage theme, carried from #331): a
**surface-idiom lint** — a `validate_surfaces` check that flags any
`<dir>/**/*.X` source pattern lacking a `<dir>/*.X` sibling, so the #331
closeout-matcher footgun (non-recursive fnmatch) cannot return.

## Non-Goals

- Do not re-litigate the #322 per-surface declarations themselves; they are
  shipped — only enforce them.
- Do not make the meta-validator a content/semantic classifier. It is a
  structural presence/pairing check (mirrors the retro disposition-floor
  discipline: prove the declaration exists and is paired; a human/reviewer judges
  whether the wording is honest).
- Do not build a generic recursive-glob matcher for the surface-idiom lint — that
  was #331's rejected Option B (it would narrow fnmatch patterns that rely on `*`
  crossing `/`); the lint only checks the source-pattern sibling, it does not
  change matching semantics.
- #184 (product success criteria / metrics) is product-level and needs
  `ideation`/`spec`, not a quick slice — candidate re-point only, not primary
  scope here.

## Boundaries

- External side-effect scope: direct-commit carrier; the push that lands the
  primary closes #330 via the staged close keyword. Approval is phase-scoped and
  does not carry forward — after the approved push lane, done-early test-only
  continuation is local by default (batch remote proof, run the pre-push gate
  once over the final bundled state).
- Reuse existing checkers and the #322 declaration shape; the meta-validator is a
  new enumerator+asserter, not duplicated per-surface logic. The surface-idiom
  lint extends `validate_surfaces`, it does not fork surface matching.

Discuss before activation: Resolved (shaped defaults; the operator may re-point at `/goal`) — primary is #330; proof is local deterministic plus broad pytest with no live/prod/provider proof (the pre-push full quality gate is the bundle attestation); #330 closes via a direct-commit staged keyword; bundle scope is the named slices with broad pytest and one fresh-eye critique at the bundle boundary. Re-point options are in `## Discuss Before Activation`.

## User Acceptance

What the user can do to verify completion directly:

- Temporarily remove the `interpretation` declaration (or its paired consumer
  line) from one inference-layer surface → the meta-validator fails; restore →
  it passes. (Demonstrate the negative.)
- Reintroduce a `<dir>/**/*.X` source pattern without a `<dir>/*.X` sibling in
  `.agents/surfaces.json` → the surface-idiom lint fails.
- #330 closed (staged close keyword) with the meta-validator landed and tested,
  and a `validate-closeout-draft` proof recorded.

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` for the new meta-validator + surface-idiom lint.
- `ruff`, `check_python_lengths`, `validate_attention_state_visibility`,
  `validate_surfaces` on touched files at commit boundaries.

### High-Confidence Checks

- Broad `pytest` over the standing targets at the bundle boundary.
- One bounded fresh-eye `critique` (issue-closeout review) before close.

### External Or Live Proof

- None required. This goal is local deterministic + broad-pytest only; no
  live/prod/provider proof is claimed. The pre-push gate (full `run-quality.sh`
  read-only) is the bundle attestation, run once over the final state.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Enumerate the inference-layer surfaces + define the contract the meta-validator asserts (decide: scan vs a small registry) | Foundation for #330; the #322 rollout left this as a noted deferred capability | a list of surfaces + the assert spec (declaration 4 fields + paired consumer line; verified-fact exclusions) | planned |
| S2 | Build the meta-validator (enumerate -> assert declaration + consumer pairing; exclude verified facts) + tests incl. negative guards | The core of #330 | checker + tests; removing a declaration/consumer fails it | planned |
| S3 | Wire the meta-validator into run-quality.sh (and slice closeout if cheap) | Make it a standing gate, not a one-off | gate runs green; appears in the quality run | planned |
| S4 | Surface-idiom lint in validate_surfaces + test (the #331 deferred hardening, anchor surface-idiom-lint) | Same gate-coverage family; cheap; prevents the fnmatch footgun returning | lint + test; a reintroduced bare `**/*.X` source pattern fails | planned |
| S5 | Close #330 + bundle verify + bounded critique + retro | Closeout | staged close; broad pytest; fresh-eye critique; validate-closeout-draft | planned |

## Coordination Cues

Routing deferred to `find-skills` (its `--recommend-for-task` /
`--recommendation-role --next-skill-id` engine) — no hard-coded phase→skill map
here. Fill during the run:

- **Routing** — query `find-skills` per phase; #330 + surface-idiom-lint are
  `impl` + `quality`; record the route returned.
- **Gather** — `Gather: n/a — no external source; all context is in-repo issues
  and artifacts.`
- **Release** — `Release: n/a unless a shipped capability warrants a version
  bump.`
- **Issue closeout** — #330 (and surface-idiom-lint folds into the same carrier
  if landed together); direct-commit carrier; staged close keyword;
  `validate-closeout-draft` (draft, before commit) then `verify-closeout
  --expect-state CLOSED` proof.

## Slice Log

## Context Sources

A fresh session can reconstruct context from, in order:

- **#330 issue body** (https://github.com/corca-ai/charness/issues/330): the
  meta-validator scope (enumerate inference-layer surfaces; assert the 4-field
  declaration + paired consumer line; exclude verified facts).
- **#322 closeout** (the contract being enforced):
  `charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md`,
  `charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md`.
- **Consumer references** that pair each declaration:
  `skills/public/quality/references/automation-promotion.md`,
  `skills/public/find-skills/references/discovery-order.md`,
  `skills/public/quality/references/gate-classification.md`.
- **#331 retro** (the surface-idiom-lint candidate, anchor surface-idiom-lint):
  `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`.
- **Recent lessons digest:** `charness-artifacts/retro/recent-lessons.md`;
  **handoff:** `docs/handoff.md`; **open issues:** `gh issue list --state open`.

## Discuss Before Activation

The activation decision is resolved to shaped defaults in `## Boundaries`
(primary #330; local + broad-pytest proof, no live proof; direct-commit close).
Re-point or confirm at `/goal` before the first slice:

- **Candidate re-points (operator may choose instead of #330):**
  - **surface-idiom-lint only** — the smallest, cleanest slice if a quick win is
    preferred over #330; it is S4 here and can stand alone.
  - **#329 — retro disposition floor** does not reject invalid (prose-only
    "memory") dispositions; small retro-tooling hardening. (Hit this session: the
    floor accepted dispositions it should have scrutinized.)
  - **#184 — product success criteria / core metrics** — larger, product-level;
    needs `ideation`/`spec`, not a quick slice. Only take with an explicit scope
    reset.

## Interview Decisions

- **Primary objective:** options = {#330 meta-validator, surface-idiom-lint,
  #329, #184}. Chosen = #330 (direct #322 sequel, bounded, clean). Rejected:
  surface-idiom-lint alone (smaller than a session warrants; folded as S4); #329
  (small; candidate re-point); #184 (needs ideation/spec, not a slice).
- **Meta-validator shape:** options = {content/semantic classifier, structural
  presence+pairing check}. Chosen = structural (presence of the 4 fields + a
  paired consumer line; verified-fact exclusion list), mirroring the
  disposition-floor "prove it ran, human judges substance" discipline. Rejected:
  a semantic classifier (brittle, over-reaching).
- **Enumeration source:** options = {scan inference-layer files for the
  declaration, a small explicit registry of inference-layer surfaces}. Deferred
  to S1 — decide there based on how reliably the surfaces can be discovered.

## Plan Critique Findings

Pre-activation shaping notes (the next session runs the real fresh-eye critique):

- Over-worry raised, not folded: the meta-validator could over-fit the current
  six surfaces. Mitigation lives in S1 (enumeration source decision) — prefer a
  discovery that fails closed when a new inference-layer surface appears without a
  declaration, rather than a hard-coded list of six.
- Blocker watch: do not let the meta-validator become a content classifier
  (Non-Goals) — keep it structural so it does not fight honest per-surface
  wording.

## Off-Goal Findings

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` or an explicit
`skipped: <allowed-reason>: <detail>` before flipping to complete.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After completion: run the meta-validator, remove one surface's declaration to see
it fail, restore it; reintroduce a bare `<dir>/**/*.X` source pattern to see the
surface-idiom lint fail; confirm #330 is CLOSED.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
