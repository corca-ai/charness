# Achieve Goal: Workflow-ergonomics hardening: achieve draft must not consume the active goal slot (#336) + critique-scaffold enum validity by-construction + publish_release update_instructions pre-publish stub

Status: draft
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`.
- Timebox: 4h
- Activation time: TBD (set at `/goal`)
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement (re-point to the next workflow/
  ergonomics or release-hardening surface — e.g. the deferred installed-vs-repo
  drift detector, or the next agent/operator-tripping workflow surface — not an
  unrelated slice).
- Verification cadence: cheap deterministic checks at commit boundaries; the
  touched scripts' tests + fresh-eye critique at slice boundaries; the broad gate
  + #336 closeout at the bundle/closeout boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Bundle three workflow-ergonomics fixes that this session (and a fresh issue)
exposed — each a surface where the achieve/release workflow itself trips the
operator or agent. Remove them by construction, not by prose ritual:

1. **#336 — achieve draft must not consume the active goal slot.** Drafting an
   achieve goal artifact (Before-phase) is planning/shaping and must leave the
   host active-goal slot EMPTY; only `/goal @artifact` starts host-level pursuit.
   Observed friction (Ceal, 2026-06-08): after drafting a goal, the next goal
   creation fails with "a goal is still active" until the operator manually
   clears the slot, blurring "drafted artifact" vs "active pursued goal".
2. **critique-scaffold enum validity by-construction.** `scaffold_critique_artifact.py`
   / the artifact-surface preflight surfaces the validator's allowed enums
   (Structured Findings `bin`/`action`, Reviewer Tier `Host exposure state` + the
   `applied` <-> `Application state: host-confirmed:` coupling) at author time, so
   an author substituting a value cannot silently pick an invalid one. (This
   session's Slice-2 critique cost 3 validate->fix round-trips from invented enum
   values — a sibling of the documented critique-authoring trap.)
3. **publish_release update_instructions pre-publish stub.** `publish_release.py`
   surfaces/emits a stub target-version `update_instructions` entry early (a
   dry-run affordance or a `--prep-update-instructions` mode) so the maintainer
   fills it BEFORE the release critique, pre-empting the staleness-guard HOLD.
   (This session's release critique round-1 HOLD.)

Theme: stop the workflow surfaces from tripping the operator/agent; each fix is
small and structural.

## Non-Goals

- Do NOT build the installed-vs-repo drift detector / `--release` gate check — the
  prior goal's named done-early candidate; a different theme (release/version-skew
  hardening), kept deferred (a done-early candidate here, not in primary scope).
- Do NOT take on product-metrics #184 — product-level; needs `ideation`/`spec`.
- Do NOT manually close #335 — it rides on the next scheduled mutation cron after
  the prior session's push (its authoritative verdict).
- Do NOT cut a real release/push by default — standard `achieve` no-push; ship the
  ergonomics behind the normal gates unless a slice's release-surface change
  warrants a bump (scope that approval explicitly at the time).
- Do NOT turn the critique-enum surface into a content classifier; it is
  presence/enum surfacing only.

## Boundaries

- **#336 touches HOST integration.** The active-goal slot is a host-level feature
  (Claude `/goal` Stop-hook; the Codex equivalent). Keep portable: host-specific
  behavior in adapters/integration manifests; the `achieve` skill states the
  Before-phase(artifact-only) / pursuit(`/goal`) boundary. Determine EARLY (Slice
  1) what charness can portably change versus a host-runtime limitation; if the
  slot is host-owned and not portably changeable, document the limitation, ship
  the portable partial (achieve guidance + adapter + a clear draft-vs-active
  distinction), and file the host-side gap rather than faking a fix.
- **Public-skill + prompt-surface scope.** Touches `achieve`, the `critique`
  scaffold, and `release` → mirror-sync (`plugins/charness/...`), public-skill
  dogfood, and prompt-behavior-proof apply; deterministic gates own closeout.
- **Behavior-preserving.** Existing active-goal completion for real pursued goals
  stays unchanged; the enum surfacing and the update_instructions stub are
  additive — no existing validator verdict changes on existing artifacts.
- External side-effect scope: default no-push. If a slice changes a release
  surface enough to warrant a version bump, scope that approval to that bundle
  explicitly at the time — it does not carry forward, and after an approved lane
  done-early continuation is local by default.
- Discuss before activation: RESOLVED at shaping. (a) **#336 host-runtime
  boundary** — scope the portable fix (achieve guidance + adapter + Before/pursuit
  boundary); if the slot mechanism is host-owned, document the limitation and file
  the host-side gap rather than faking a fix; settle this EARLY in Slice 1 (a
  design question, not an activation blocker). (b) **#336 closure** — close on the
  fix landing via a direct-commit close-keyword carrier (standard issue closeout);
  the issue is repo-owned. (c) **Scope** = the #336 + workflow-ergonomics bundle
  (operator chose it 2026-06-08). No unresolved consequential default remains.

## User Acceptance

What the user can do to verify completion directly.

- Draft an achieve goal artifact and confirm the host active-goal slot stays
  EMPTY (no "goal still active" friction on the next goal creation); confirm
  `/goal @artifact` is where pursuit / host-tracking starts; confirm #336 closed.
- Author a `critique` artifact and confirm the scaffold/preflight surfaces the
  allowed `bin` / `action` / `Host exposure state` enums (so an invalid
  substitution is caught at author time, not by a validate->fix round-trip).
- Run the release publish dry-run / prep and confirm it emits/surfaces the
  target-version `update_instructions` stub before the critique gate.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched scripts' own pytest modules; a before/after verdict-equality check;
  `check_export_safe_imports` + mirror byte-sync.

### High-Confidence Checks

- Dogfood: drafting a goal leaves the slot empty; authoring a critique surfaces
  the allowed enums; the publish dry-run emits the update_instructions stub; the
  touched gates stay green.
- Broad gate (`run-quality.sh --read-only`) at the bundle boundary. Fresh-eye
  `critique` at each slice boundary per the slice plan.

### External Or Live Proof

- **#336 closeout** via a direct-commit close-keyword carrier, verified with
  `gh issue view 336` (and `issue_tool.py verify-closeout`).
- **Host-runtime verification for #336** if the slot mechanism is host-owned: a
  real-host check that drafting leaves the slot empty, OR a documented host
  limitation + the portable partial-fix. Recorded as executed proof or a named
  limitation.
- No real release by default; if a release-surface bump is warranted, record the
  `Release:` proof, else `Release: n/a — <reason>`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #336: achieve draft != active goal slot — Before-phase is artifact-only, `/goal` starts pursuit; settle the portable-vs-host-runtime boundary early | the newly-opened operations issue, in the exact workflow used to shape THIS goal | drafting leaves the slot empty; `/goal` activates; error messages distinguish draft-exists vs slot-occupied; #336 closed; SHIP critique | planned |
| 2 | critique-scaffold enum validity by-construction: surface allowed `bin`/`action`/host-exposure enums at author time | this session's Slice-2 3-round-trip waste; the documented critique-authoring trap's sibling | scaffold/preflight surfaces the allowed enums; an invalid substitution is caught at author time; verdicts unchanged; SHIP critique | planned |
| 3 | publish_release update_instructions pre-publish stub emitter (dry-run / `--prep-update-instructions`) | this session's release critique round-1 HOLD (Gawande lens) | publish dry-run / prep emits the target-version stub before the critique gate; verdicts unchanged; SHIP critique | planned |
| 4 | bundle proof + closeout: broad gate; #336 closeout; retro | the operator-requested next-to-do closeout | broad gate PASS; #336 verified closed; retro + dispositions | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — planned: Slice 1 → `issue` + `impl` (+ `create-skill` for the
  achieve/host-integration boundary); Slice 2 → `impl` + `critique`; Slice 3 →
  `release`/`impl` + `critique`; Slice 4 → `quality` + `issue` + `retro`. Confirm
  via `find-skills` and record the returned route at completion (or
  `Routing: n/a — <reason>`).
- **Gather step** — likely n/a — #336 is a GitHub issue read via `gh`, not an
  external URL/Slack/Notion/Docs/Drive source; confirm at completion
  (`Gather: n/a — <reason>` if so).
- **Release step** — likely n/a by default (no real release); if Slice 3 changes
  the release surface enough to bump, record the `Release:` proof, else
  `Release: n/a — <reason>`.
- **Issue closeout step** — #336 is the in-scope tracked issue: close on the fix
  landing via a direct-commit close-keyword carrier; record the `Issue closeout:`
  line (numbers + carrier + `issue_tool.py verify-closeout` proof) at completion.
  #335 (cron-closing) and #184 (product) are tracked context only.

Operating guardrails carried from this session's retro
(`charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`):
at a bundle boundary that added mutation-pool commits, run the changed-line
coverage producer FIRST; anticipate the no-increase ratchets (core-headroom /
boundary-bypass) on additive work; keep the critique scaffold's example enum
tokens / check the allowed enums before substituting (also Slice 2's subject).

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The fresh issue:** #336 "Do not consume active goal slot when drafting
   achieve goal artifacts" (`gh issue view 336`; label `operations`; observed in
   the Ceal repo, requested via Codex).
2. **This session's lessons:** the goal retro
   `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`
   (the critique-enum + update_instructions + coverage-first lessons) and
   `charness-artifacts/retro/recent-lessons.md`.
3. **The shipped version-skew goal:**
   `charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`
   (the deferred drift-detector candidate; the critique-enum/update_instructions
   lessons in its Auto-Retro + early-close report).
4. **Owning surfaces:** the `achieve` skill + the host `/goal` integration
   (Stop-hook wiring / adapter); `skills/public/critique/scripts/scaffold_critique_artifact.py`
   + `scripts/validate_critique_artifacts.py` + `scripts/check_artifact_surface_preflight.py`;
   `skills/public/release/scripts/publish_release.py` +
   `publish_release_preflight.py` (the `update_instructions_version_blocker`).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- **Scope (asked 2026-06-08).** Family: {#336 only; #336 + workflow-ergonomics
  bundle; #336 + version-skew drift detector}. Chosen: **#336 + workflow-ergonomics
  bundle** (critique-enum by-construction + update_instructions pre-publish stub).
  Rejected: #336-only (under-uses the session lessons the operator asked to
  include); +drift-detector (different theme — release/version-skew hardening,
  over-broad; kept as a named deferred/done-early candidate).
- **#336 host-runtime boundary (to settle early in Slice 1, not at activation).**
  Family: {fully portable fix; portable partial + documented host limitation +
  host-gap issue}. Chosen direction: determine in Slice 1; default to the portable
  partial + documented limitation if the slot is host-owned.

## Plan Critique Findings

Self-critique (Before-phase). Fresh-eye critiques run at each slice boundary per
the verification plan.

- **#336's fix may be partly host-owned.** The active-goal slot is a host-runtime
  feature charness may not fully control. Folded: Boundaries scope a portable fix
  + a documented-limitation + host-gap-issue fallback; Slice 1 settles this early.
- **Over-bundle risk (3 surfaces in one goal).** Counterweight: all three are ONE
  theme (workflow surfaces that trip the operator/agent), each small and
  structural; the prior-goal focus lesson is respected by keeping the drift
  detector OUT (deferred). Folded into Non-Goals.
- **Over-worry, not folded:** rebuilding the host `/goal` machinery wholesale, or
  adding broad CI for goal-slot state — out of class; the portable partial +
  documented limitation is the honest boundary.

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

1. Draft an achieve goal artifact and confirm the host active-goal slot stays
   empty (the next goal creation does not fail with "a goal is still active").
2. Confirm `/goal @artifact` is the point where host-level pursuit starts.
3. Author a `critique` artifact and confirm the allowed `bin`/`action`/host-
   exposure enums are surfaced at author time.
4. Run the release publish dry-run and confirm it emits the target-version
   `update_instructions` stub before the critique gate.
5. Confirm #336 is CLOSED on GitHub via the close-keyword carrier.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
