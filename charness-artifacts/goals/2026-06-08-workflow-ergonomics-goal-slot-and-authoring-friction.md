# Achieve Goal: Workflow-ergonomics hardening: achieve draft must not consume the active goal slot (#336) + critique-scaffold enum validity by-construction + publish_release update_instructions pre-publish stub

Status: active
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slices 1 & 2 DONE (#336 portable fix `cead7949`; critique enum
  legend `a101e716`; both fresh-eye SHIP). Next: Slice 3 (publish_release
  update_instructions pre-publish stub).
- Next action: Slice 3 — emit/surface a target-version `update_instructions`
  stub early (dry-run / `--prep` affordance) so the maintainer fills it before
  the release critique. Then Slice 4 bundle proof + the staged #336 closeout
  (carrier + resolution critique + verify-closeout) + retro.
- Timebox: 4h
- Activation time: 2026-06-08 (active run; flipped from draft at `/goal`)
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

### Slice 1: Slice 1 — #336: achieve draft must not consume the host active-goal slot

- Objective: Add the missing symmetric Before-phase rule: drafting is artifact-only and must not consume the host active-goal slot; the slot is consumed only at /goal pursuit. Settle the portable-vs-host boundary early.
- Why this approach: The lifecycle stated the host-goal-tool boundary only at completion; the Before-phase counterpart was missing — that asymmetry is the #336 root cause. The fix is portable (achieve contract), not a host reimplementation, because slot consumption is agent/operator-driven (upsert_goal.py is pure file I/O), confirmed this session (drafting left the slot empty; only /goal consumed it).
- Commits: cead7949
- What changed: skills/public/achieve/SKILL.md (Before-phase save bullet, +1 core line); references/lifecycle.md (new 'Drafting does not consume the host goal slot' subsection + host-runtime residual non-claim); references/adapter-contract.md (new 'Host Goal-Slot Boundary' section, no adapter knob by design); scripts/public_skill_dogfood_lib.py + docs/public-skill-dogfood.json (3rd achieve acceptance criterion + observed_evidence note, reviewed_on bumped); tests/quality_gates/test_achieve_before_activation.py (new test_drafting_does_not_consume_host_goal_slot); plugin mirror byte-synced.
- Alternatives rejected: Adding a no-op goal_slot.* adapter knob (rejected: would fake portability for a uniform rule). Filing a host-side gap issue now (rejected: no observed host-auto-activation path; recorded as a conditional host-runtime non-claim instead). Building a deterministic content classifier (out of scope; presence/contract-pinning only).
- Targeted verification: py_compile/ruff/check_python_lengths (touched); test_achieve_before_activation.py 9 passed; validate_public_skill_dogfood; validate_skill_ergonomics (all enforced rules incl. portable_package_issue_anchor/dated_incident — package stays anchor/date-free); validate_skills; check-markdown; check_doc_links; check-skill-core-headroom (156/160 = 4 left, ok); 126 related tests; full pre-commit aggregate green at commit.
- Test duplication pressure: check_duplicates.py: No duplicates found at threshold 0.98. The new test is a distinct contract-pinning test (host-slot rule) in an existing module, not a duplicate of the #268 completion-downstream test.
- Critique: Fresh-eye bounded subagent (general-purpose) — verdict SHIP, no blockers/should-fix. Independently confirmed: upsert_goal.py is pure file I/O so drafting cannot consume the slot by construction (determination honest, not a faked/partial fix); the host-runtime residual is correctly a conditional non-claim, so filing a host-side issue now would be premature; SKILL.md<->lifecycle consistent; the test reproduces all 9 assertions and would catch a regression; the dogfood 'UNCHANGED behavior' claim is defensible (documents existing behavior); 0 portability-gate findings. NIT: achieve SKILL.md core is now at the buffer floor (4 left) — next achieve-core addition will need prose moved to references (Slices 2-3 target critique/release, not achieve, so unaffected).
- Off-goal findings:
- Lessons carried forward: achieve SKILL.md core is at the 4-line buffer floor — avoid further achieve-core additions this run. #336 close-keyword carrier + feature-class closeout body (jtbd/boundary/resolution_brief/implementation/prevention) + resolution_critique + verify-closeout are staged for Slice 4 (slice-plan-aligned). Persist the fresh-eye critique as the #336 resolution-critique artifact at Slice 4 (mind the strict critique enums — Slice 2's subject).
- Metrics: 1 fix commit (cead7949); 1 fresh-eye subagent (~58k tokens); no host token/time totals claimed.

### Slice 2: Slice 2 — critique-scaffold enum validity by-construction

- Objective: Surface the critique validator's allowed enums (Structured Findings bin/evidence/action; Reviewer Tier Host exposure state + the applied<->host-confirmed coupling) at scaffold author time, so substituting a value picks from the valid set instead of hitting a validate->fix round-trip.
- Why this approach: The scaffold emitted only example values; an author substituting one could silently pick an invalid enum (documented trap: a prior Slice-2 critique cost 3 round-trips). Surfacing the legend in the scaffold template auto-covers the artifact-surface preflight too (it renders the scaffold as the required shape). Chose a drift-pinning test over a runtime validator import to keep the scaffold portable to exported/consumer layouts (no validator-path coupling).
- Commits: a101e716
- What changed: skills/public/critique/scripts/scaffold_critique_artifact.py (ALLOWED_* constants + allowed_enums() + HTML-comment legend under both schema sections + allowed_enums in JSON payload); tests/test_critique_scaffold.py (legend assertions + new bidirectional drift test test_scaffold_surfaced_enums_match_validator_frozensets); plugin mirror byte-synced.
- Alternatives rejected: Runtime import of the validator frozensets into the scaffold (rejected: couples the portable scaffold to a source-repo-only validator path, would break the exported-consumer scaffold test). Visible prose legend (rejected: HTML comment keeps the final record clean and is ignored by both validator parsers + markdownlint). Pinning the couplings prose to validator error strings (rejected as brittle; the enforced frozensets are what's pinned).
- Targeted verification: tests/test_critique_scaffold.py + test_critique_skill.py 24 passed; scaffolded template still validates (Validated 1 critique artifact); preflight --path surfaces both legend lines in stub + shape-preview; ruff clean; check_python_lengths ok; structural sweep pass; pre-commit aggregate green at commit.
- Test duplication pressure: Added 1 drift test + extended 1 existing test in tests/test_critique_scaffold.py (24 passed total in the critique scaffold+skill modules). The drift test is distinct (single-source-of-truth pin), not a duplicate of the validator's own enum-rejection tests in test_critique_skill.py which assert the validator REJECTS bad values; this asserts the scaffold SURFACES the same valid set.
- Critique: Fresh-eye bounded subagent (general-purpose) — verdict SHIP, no blockers/should-fix. Independently confirmed via the real parsers that the HTML-comment legend can never be parsed as a Structured Finding (_structured_findings_lines) or Reviewer Tier field (_section_field_map) — both gate on the '- ' prefix the legend lacks; the drift test catches divergence in BOTH directions (simulated); the portable drift-test design is correct (a runtime import would break the exported-consumer scaffold test); the legend wording matches is_valid_followup_tail and the applied->host-confirmed coupling exactly; no markdown/MD033 issue (legend has zero backticks, MD013 off). NITs/over-worries only.
- Off-goal findings:
- Lessons carried forward: The artifact-surface preflight renders the owning scaffold as the required shape, so surfacing author-time guidance in the scaffold template covers the preflight surface for free. For Slice 3 (publish_release update_instructions stub): same 'emit the author-time affordance from the owning helper' shape may apply.
- Metrics: 1 fix commit (a101e716); 1 fresh-eye subagent (~37k tokens); no host token/time totals claimed.

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
