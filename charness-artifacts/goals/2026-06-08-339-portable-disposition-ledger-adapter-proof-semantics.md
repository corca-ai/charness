# Achieve Goal: Portable residual/disposition ledger with adapter-owned proof semantics (#339)

Status: draft
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-339-portable-disposition-ledger-adapter-proof-semantics.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (draft). Open design defaults remain in
  `Discuss before activation:` — resolve them (a–e) before `/goal`.
- Next action: resolve the activation-discussion defaults, then activate with
  `/goal @charness-artifacts/goals/2026-06-08-339-portable-disposition-ledger-adapter-proof-semantics.md`.
- Verification cadence: cheap deterministic checks at commit boundaries; the
  touched scripts' tests + fresh-eye critique at slice boundaries; the broad gate
  + #339 closeout at the bundle boundary. Carry this session's lessons: at a
  bundle boundary with mutation-pool commits run the changed-line coverage
  producer FIRST; cover any new normalization/guard branch IN the introducing
  slice; keep charness-internal `#N` traceability anchors in top-level `scripts/`,
  NOT in skill-package files (the package-level `validate_skill_ergonomics` scan);
  read gate exit codes with `&&`/`||`, never through a pipe; a `Routing:` line
  must name `find-skills` and each routed skill on ONE physical line.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make Charness closeout flows (`achieve` / `retro` / issue closeout) enforce a
portable, **machine-checkable residual/disposition ledger**: every closeout
non-claim, proof gap, deferred improvement, or residual risk must resolve to one
concrete disposition — `issue #N` / `applied: <artifact/change>` /
`accepted-risk: <reason>` / `out-of-scope: <reason>` — so a prose-only `defer`,
`recorded in retro`, or `future work` no longer satisfies closeout.

The portable layer stays **presence/form-enum-only** (the fixed #337/#329/#253
doctrine: never a content classifier); the **adapter owns the domain proof
semantics** — proof levels and their ordering/incomparability, which proof levels
satisfy which acceptance classes, verifier/artifact references, and whether a gap
is acceptable / out-of-scope / needs an issue. Detect **proof-mismatch**
generically: when acceptance names a stronger behavior class than the proof
actually reached (per the adapter's map), the mismatch must be recorded and
dispositioned — without Charness learning any domain concept (no Slack
`app_mention`, `#ceal-dev`, receipt-intake, or Workspace-cleanup semantics).

This is the adapter-boundary successor to #337's structural-follow-up destination
floor: #337 added the per-transferable-waste destination; #339 generalizes to a
full residual ledger whose *proof semantics* the adapter declares.

## Non-Goals

- Do NOT encode domain semantics in portable Charness. No consumer-repo concept
  (Slack/Workspace/receipt/channel) enters core; the adapter declares proof
  levels and the acceptance→proof map. Slice 2 dogfoods with a *synthetic* adapter
  to prove no domain concept is needed in core.
- Do NOT make the ledger floor a content classifier (the #337/#329 trap). It
  checks presence + disposition FORM/enum only; the reviewer/human + the adapter
  map judge substance. A vague-but-valid `accepted-risk: <reason>` passes.
- Do NOT change the existing disposition forms (`applied`/`issue #N`/`none —`) or
  the #337 structural-follow-up destination / rung-1e behavior. `accepted-risk:` /
  `out-of-scope:` are ADDITIVE forms on the shared grammar.
- Do NOT take on #338 (gather X/Twitter — gather-provider theme) or #184 (product
  metrics — needs ideation/spec); different themes, tracked separately.
- Do NOT cut a real release/push by default — standard `achieve` no-push.

## Boundaries

- **Presence/form-enum-only, grandfathered.** New ledger forms/floors fire only
  for in-scope artifacts, grandfathered by `Created`/`Date` (landing-day + 1, the
  established precedent, so every existing artifact is grandfathered and the broad
  gate stays green); missing/malformed date fails closed; clone-safe (in-file
  content, not mtime).
- **Behavior-preserving.** The shared grammar `scripts/disposition_form.py` is
  EXTENDED, not forked: `accepted-risk:`/`out-of-scope:` are new enum arms with
  their own enforce-from dates; existing `evaluate_disposition_form` /
  `evaluate_destination_form` verdicts are unchanged (a before/after verdict-
  equality check on the live corpus is a required low-cost proof).
- **Adapter boundary.** Charness asks; the adapter answers. The adapter schema is
  declared once (alongside the existing achieve/issue/retro adapters) and resolved
  via the existing adapter-resolution path. Missing adapter → the portable
  presence/form floor still fires (degraded, not absent); proof-mismatch detection
  degrades to "no domain map available → require a ledger disposition" rather than
  silently passing.
- **Public-skill + adapter-schema + prompt-surface scope.** Touches the achieve /
  issue / retro closeout surfaces + `disposition_form.py` + the adapter contract →
  mirror-sync (`plugins/charness/...`), public-skill dogfood, and prompt-behavior-
  proof apply; deterministic gates own closeout.
- External side-effect scope: default no-push. Any approved publish/push/CI is
  scoped to the bundle that requested it and does not carry forward.
- Discuss before activation: **UNRESOLVED — resolve (a)–(e) below before `/goal`.**
  (a) **Ledger surface** — a NEW machine-checkable ledger section/artifact, or
  EXTEND the existing #337 disposition gate (Auto-Retro + disposition review) with
  residual/proof-gap rows. Lean: extend (one disposition system, not two), but
  confirm the residual/non-claim rows fit the Auto-Retro surface vs need their own
  `## Residual Ledger` block. (b) **Adapter schema shape** — exact fields (proof
  levels + ordering/incomparability; acceptance-class→satisfying-proof-level map;
  verifier/artifact refs; gap acceptability) and the missing-adapter fallback.
  (c) **Scope across 3 surfaces** — one goal (achieve+retro+issue) or split into a
  second goal if Slice 2–3 prove too large; decide the split trigger up front.
  (d) **New forms' enforce dates** — `accepted-risk:`/`out-of-scope:` grandfather
  dates (landing-day + 1). (e) **Proof-mismatch detection** — confirm it is
  adapter-map lookup + presence only (Charness never judges proof *strength*),
  matching the gate-and-intelligence doctrine. These are consequential design
  defaults (proof-level non-claims + architectural surface); `--pursue-ready` stays
  false until they are resolved in-transcript.

## User Acceptance

What the user can do to verify completion directly.

- Run a closeout (achieve or issue) whose residual / non-claim / proof-gap is left
  as prose-only `defer` / `recorded in retro` / `future work`, and confirm it is
  REFUSED; confirm it is accepted once each ledger item carries `issue #N` /
  `applied: <artifact>` / `accepted-risk: <reason>` / `out-of-scope: <reason>`.
- Declare a synthetic adapter with proof levels + an acceptance-class→proof-level
  map, and confirm a closeout whose reached proof level does NOT satisfy the named
  acceptance class is refused without a recorded mismatch disposition.
- Confirm NO domain concept appears in portable Charness; the adapter owns proof
  semantics; a repo with no adapter still gets the portable presence/form floor
  (degraded, not absent).
- Confirm an existing (pre-rule) goal / retro / issue closeout completes unchanged
  (grandfathered) and that a closeout with no residuals is not forced to add a
  ledger row (no over-fire).
- Confirm #339 is CLOSED on GitHub via the close-keyword carrier.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched scripts' own pytest modules; a before/after verdict-equality check
  on the live goal/retro/issue-closeout corpus (behavior-preserving for existing
  forms); `check_export_safe_imports` + mirror byte-sync.
- At a bundle boundary with mutation-pool commits, run the changed-line coverage
  producer FIRST and cover any new normalization/guard branch in-slice.

### High-Confidence Checks

- Dogfood: a prose-only residual is refused, a dispositioned ledger accepted; a
  synthetic adapter drives proof-mismatch detection; a missing-adapter repo
  degrades to the portable floor (no domain concept needed in core); pre-rule
  artifacts and no-residual closeouts are unaffected; touched gates stay green.
- Broad gate (`run-quality.sh --read-only`) at the bundle boundary. Fresh-eye
  `critique` at each slice boundary.

### External Or Live Proof

- **#339 closeout** via a direct-commit close-keyword carrier, verified with
  `gh issue view 339` + `issue_tool.py verify-closeout` (+ resolution critique).
- No real release by default; record `Release:` proof or `Release: n/a — <reason>`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add `accepted-risk:` / `out-of-scope:` forms to `disposition_form.py` (the shared grammar) + the residual/disposition LEDGER presence/form floor; grandfathered, behavior-preserving | the shared grammar is the one source #337/#329 built; the new enum arms land first | prose-only residual refused, dispositioned ledger accepted; existing-form verdicts unchanged (corpus equality); SHIP critique | planned |
| 2 | The adapter boundary: schema for proof levels + acceptance-class→proof-level map + verifier refs + gap acceptability; resolution + missing-adapter degradation | Charness must ask adapters, not encode domain semantics | a synthetic adapter drives behavior; missing adapter degrades to the portable floor; NO domain concept in core; SHIP critique | planned |
| 3 | Proof-mismatch detection (acceptance class vs proof reached, via the adapter map) wired into achieve/issue closeout | the generic mismatch check is the core of #339 | a closeout whose proof < the named acceptance class is refused without a mismatch disposition; SHIP critique | planned |
| 4 | Wire retro + dogfood + #339 closeout: broad gate; #339 carrier; retro | the operator-requested closeout | broad gate PASS; #339 verified closed; retro + ledger dispositions | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns (name `find-skills` and each routed
  skill on ONE physical line). At completion, recorded implementation / debug /
  quality / issue work needs this `Routing:` evidence or a `Routing: n/a — <reason>`
  opt-out.
- **Gather step** — `## Context Sources` cites #339 via `gh` and repo paths, not an
  external URL/Slack/Notion/Docs/Drive asset; likely `Gather: n/a — <reason>`.
  Confirm at completion.
- **Release step** — likely n/a by default (no real release); record
  `Release: n/a — <reason>` unless a release-surface bump is taken.
- **Issue closeout step** — #339 is the in-scope tracked issue: close on the fix
  landing via a direct-commit close-keyword carrier; record the `Issue closeout:`
  line (numbers + carrier + `issue_tool.py validate-closeout-draft`/`verify-closeout`
  proof) at completion. #338, #335, #184 are tracked context only.

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1
after the activation-discussion defaults are resolved._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The fresh issue:** #339 "Separate portable disposition gates from
   adapter-owned proof semantics" (`gh issue view 339`; filed from a `corca-ai/ceal`
   Slack reliability closeout where follow-up was left as prose-only disposition).
2. **The #337 work this extends (same area, this session):** the goal
   `charness-artifacts/goals/2026-06-08-retro-disposition-structural-followup-classification.md`,
   the shared grammar `scripts/disposition_form.py`, the rung-1e floor
   `skills/public/achieve/scripts/goal_artifact_disposition.py`, and the shared
   reference `skills/shared/references/retro-issue-destination-split.md`.
3. **The doctrine (presence/form-enum-only, never a content classifier; the
   gate-and-intelligence split):** `docs/prescribed-skill-closeout-contract.md`
   (#253/#329 two-rung gate + form floor) and achieve `references/lifecycle.md`.
4. **The adapter-resolution path:** `scripts/resolve_adapter.py` and the existing
   achieve/issue/retro adapters under `.agents/*.yaml` (the boundary #339 extends).
5. **Recent-lessons:** `charness-artifacts/retro/recent-lessons.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Scope (chosen by the user at shaping 2026-06-08).** Family: {#339 only; #339 +
  #338 gather; #339 + the `charness update` release-closeout step}. Chosen:
  **#339 only** — the operator selected it; it continues this session's #337
  disposition-gate theme and reuses the warm context. Rejected: +#338 (gather
  provider / source-identity theme, different area); +release-update (release-
  contract theme, tracked in handoff). `axis: issue-theme` — bundling across
  themes is the over-anchoring to avoid.
- **Ledger surface (DEFERRED to activation, default (a)).** Family: {new ledger
  artifact/section; extend the existing #337 disposition gate}. Lean: **extend**
  (one disposition system, not two drifting copies), confirm at activation whether
  residual/non-claim rows fit Auto-Retro or need a `## Residual Ledger` block.
- **Floor design (assumed; fixed doctrine).** Family: {presence/form-enum-only +
  adapter-owned proof semantics; deterministic content/proof classifier}. Chosen:
  **presence/form-enum-only** — the #337/#329 doctrine that a prose word-list
  over-fires or passes pure narration is fixed; the adapter + reviewer own
  substance. `single-point: the gate-and-intelligence split is fixed repo doctrine`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique. (Shaping-phase
self-critique; a fresh-eye plan critique is part of the activation discussion.)

- **Over-tightening into a content/proof-strength classifier** (the #337 trap one
  level up). Folded: Non-Goals + Boundaries scope it presence/form-enum-only; the
  adapter map + reviewer own substance; proof-mismatch is an adapter-map lookup,
  not Charness judging proof strength.
- **Domain leakage into portable core.** Folded: Non-Goals forbid domain concepts;
  Slice 2 dogfoods with a *synthetic* adapter to prove core needs no domain term;
  missing-adapter degradation is specified (portable floor still fires).
- **Over-fire on closeouts with no residuals.** Folded: the floor fires only on a
  named residual/non-claim/proof-gap row, grandfathered by date.
- **Over-broad scope (3 surfaces in one goal).** Raised, NOT yet folded — surfaced
  as Discuss-before-activation (c) with an explicit split trigger to decide at
  activation rather than mid-run.

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here — and check the seam lineage before filing a fresh narrow issue._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. A closeout that leaves a residual as prose-only `defer`/`recorded in retro`/
   `future work` is refused; dispositioning each ledger item
   (`issue #N`/`applied:`/`accepted-risk:`/`out-of-scope:`) accepts it.
2. A synthetic adapter's acceptance→proof-level map drives proof-mismatch
   detection; a missing-adapter repo still gets the portable floor.
3. No domain concept appears in portable Charness core.
4. A pre-rule artifact and a no-residual closeout both complete unchanged.
5. #339 is CLOSED on GitHub via the close-keyword carrier.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <change>` / `issue #N (recurs:|novel:)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
