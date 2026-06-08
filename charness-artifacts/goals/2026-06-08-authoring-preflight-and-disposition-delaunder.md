# Achieve Goal: Generalize author-time shape-preflight + de-launder the disposition escape (break the #308 recurrence loop)

Status: active
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-authoring-preflight-and-disposition-delaunder.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation with a real spec/design front (Slice 1) — the
de-launder mechanism has a hard guardrail constraint, so it is designed +
critiqued before code.

## Active Operating Frame

- Current slice: Slice 3 — sibling scan across the artifact-authoring validator family; extend the registry to the adapter-scoped trio (debug/quality/handoff); coverage report. Slices 1 (design) + 2 (dispatcher + blocking commit-boundary wiring + critique scaffold citation, #334 caught at author time) are DONE.
- Next action: enumerate the artifact-authoring shape family, classify covered/fixed/out-of-class, extend the dispatcher registry to the adapter-scoped surfaces with adapter resolution, write the coverage report; tests + behavior-preservation.
- Timebox: 4h
- Activation time: 2026-06-08 (activated via `/goal`)
- Closeout reserve: 45m
- Done-early policy: continue_next_improvement (re-point to the next recurrence-
  loop hardening, e.g. the remaining uncovered artifact-validator surfaces, not a
  quick unrelated slice).
- Verification cadence: cheap deterministic checks at commit boundaries
  (py_compile / ruff / check_python_lengths / the touched validators' own tests +
  a behavior-preservation check that existing gate VERDICTS are unchanged); a
  fresh-eye critique at the Slice-1 design boundary AND at the de-launder boundary;
  broad gate + dogfood (this goal's own closeout must pass under the new rules) at
  the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Structurally close the recurring **"authoring-preflight skip"** loop
(#284 → #308 → #325 → #329 → #332 → #334) instead of filing its N-th narrow
instance. Three coupled outcomes, all in one goal:

1. **Generalize the author-time shape-preflight.** Today `check_skill_surface_preflight.py`
   (#284/#308/#328) covers only public/support *skill-surface* edits. The
   ~30 artifact-shape validators (`validate_critique_artifacts`,
   `check_goal_artifact` closeout-evidence, `validate_retro_artifact`,
   `validate_debug_artifact`, `validate_ideation_artifact`,
   `validate_quality_artifact`, `validate_handoff_artifact`, …) are NOT covered —
   so an author of a critique artifact or a goal closeout-evidence block discovers
   the required shape only by FAILING the gate. Make the preflight, given a target
   artifact path/type, surface (or stub) the owning validator's required shape
   (sections/fields/enums) at AUTHOR time, **non-discretionarily** — because #332
   already proved discoverable docs + memory do not stop this; only auto-run at the
   right boundary does. The critique-artifact + goal-closeout-evidence surfaces
   (the #334 instance) are the proving instances.

2. **De-launder the disposition escape.** The `applied:` / `issue #N` disposition
   gate makes `issue #N` the cheapest path, so every recurrence becomes a new
   narrow issue that gets closed (feels resolved) while the GENERAL fix never
   lands — the loop's engine. Modify the skill(s) so a disposition that re-files a
   finding matching an already-recurring class cannot silently launder as a fresh
   narrow issue: require a recurrence-lineage assertion and route the
   *is-this-actually-recurring?* judgment to the rung-2 fresh-eye disposition
   reviewer (which is allowed to judge substance) — **without** turning the
   deterministic floor into a content classifier (achieve's own guardrail).

3. **Sibling scan + fix.** Enumerate the artifact-authoring validator family,
   classify which fail-at-gate-only with no author-time shape help, and fix the
   in-class ones — with a coverage report so "we generalized it" is provable, not
   asserted.

Success = the loop is structurally closed: the preflight emits/asserts required
shape for the #334 surfaces at author time (proven by authoring into them without
a gate-time surprise); a sibling-coverage report; a de-launder mechanism that is
presence-only + reviewer-judged (never a classifier); and this goal's OWN closeout
passes under the new rules (dogfood).

## Non-Goals

- Do NOT turn the deterministic disposition floor into a content classifier or a
  prose word-list. Achieve's own guardrail: "the deterministic floor proves a
  review ran; the reviewer/human judges substance." The de-launder is presence-
  only (a required recurrence-lineage field) + rung-2 reviewer judgment.
- Do NOT add another *discoverable doc / reference* as the primary fix for
  workstream 1. #332 already proved that class ineffective. The fix is
  non-discretionary author-time behavior; a doc may accompany it but is not it.
- Do NOT change what any artifact MEANS or alter any existing gate VERDICT. This
  changes WHEN/HOW an author learns the required shape, not the gates' judgments.
- Do NOT broaden the sibling scan to non-authoring infra validators (packaging,
  supply-chain, integrations, adapters, profiles, presets, mirror-drift). Scope is
  the hand-authored-artifact-shape family only.
- Do NOT rewrite the validators; the preflight READS their required shape (or a
  declared spec of it) — validators stay the single source of truth.
- Do NOT file yet another narrow per-surface issue as the deliverable; the
  deliverable is the general mechanism + coverage proof. #334 is folded in as a
  proving instance, not closed by side effect without a decision.
- No release / version bump / install-manifest edit; `achieve` does not push.

## Boundaries

- **Public-skill + prompt-surface scope.** This modifies public-skill SKILL.md /
  references (achieve, critique, and likely retro/issue) and validator/preflight
  scripts → the repo's prompt-behavior-proof + public-skill-dogfood +
  cautilus-on-demand policy applies. Deterministic gates own closeout; consult
  `plan_cautilus_proof` / `scripts/run_cautilus_eval.py` and only run
  `cautilus evaluate fixture` on an explicit log-backed behavior-proof need.
- **Behavior-preserving for existing gates.** Every existing validator's verdict
  on existing artifacts stays identical; the preflight is additive. Prove with the
  touched validators' own test modules + a before/after verdict check.
- **Dogfood is mandatory.** The de-launder change must let THIS goal's own
  closeout (its Auto-Retro dispositions + disposition review) pass under the new
  rule — if it can't, the rule is wrong.
- **Export-safe + length-safe.** Mirror sync (`plugins/charness/scripts/`); watch
  `check_goal_artifact.py` / `goal_artifact_closeout_evidence.py` single-file
  length gates if they grow.
- Discuss before activation: resolved — (a) broad scope (3 coupled workstreams)
  is intentional and user-requested, bounded by the slice plan and sequenced
  lowest-risk-first with the delicate disposition-gate change last and critiqued;
  (b) the disposition-gate / public-skill prompt-surface modification is
  user-directed (the user explicitly asked to modify the skill so the laundering
  cannot escape), not an agent-chosen consequential default, and the
  content-classifier guardrail is folded into Non-Goals as the hard constraint;
  (c) no live/prod/provider proof, no irreversible side effect, no push/release.
  The one genuinely open design axis — the exact de-launder mechanism
  (presence-only lineage field vs rung-2 reviewer strengthening vs
  issue-filing-time recurrence check, or a combination) — is a Slice-1 design
  decision (recorded as an anti-anchoring axis), not an activation blocker. No
  consequential default remains unresolved.

## User Acceptance

What the user can do to verify completion directly:

- Author a fresh critique artifact (or a goal closeout-evidence block) via the
  documented path and see the required shape surfaced/stubbed at AUTHOR time —
  before any gate run — rather than discovering `Reviewer Tier Evidence` /
  closeout-evidence requirements by failing the gate. Demonstrated on the #334
  surfaces.
- Read a sibling-coverage report enumerating the artifact-authoring validator
  family with, per surface: covered-by-author-time-preflight (yes/no before),
  fixed (yes/no), or out-of-class with reason.
- See a contrived "re-file of a known recurring class as a fresh narrow issue"
  get caught — by a required recurrence-lineage field and/or the rung-2 reviewer —
  with the deterministic floor provably NOT classifying content.
- Confirm this goal's own closeout passed under the new de-launder rule (dogfood).
- Run the existing gates and the touched validators' tests and see them green;
  confirm no existing gate verdict changed; mirror byte-synced.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched validators' / preflight's own pytest modules; a before/after
  verdict-equality check on a corpus of existing artifacts (behavior-preserving).
- `check_export_safe_imports` + mirror byte-sync after any `scripts/**` change.

### High-Confidence Checks

- Dogfood: this goal's own `check_goal_artifact.py` closeout passes under the new
  de-launder rule.
- Broad gate (`run-quality.sh --read-only`, and the full closeout) at the bundle
  boundary.
- Fresh-eye `critique` at the Slice-1 design boundary (does the de-launder design
  avoid the content-classifier trap? is the preflight generalization actually
  non-discretionary, not another doc?) and again at the de-launder code boundary.

### External Or Live Proof

- Cautilus only on an explicit log-backed behavior-proof need for a prompt-surface
  change (consult `plan_cautilus_proof`; deterministic-first). No live/prod/provider
  proof; none claimed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Spec the de-launder mechanism + the preflight-generalization shape; decide the design axes; fresh-eye critique | The de-launder has a hard guardrail (no content classifier); design before code, lowest-regret first | a short contract/spec + SHIP critique resolving the content-classifier constraint and the "non-discretionary, not a doc" constraint | planned |
| 2 | Generalize the author-time preflight to the critique-artifact + goal-closeout-evidence surfaces (#334 instance), wired non-discretionarily at the author boundary | The #334 surfaces are the proving instances; closes the concrete gap that bit this session | authoring into those surfaces surfaces/stubs required shape pre-gate; existing verdicts unchanged; tests green | planned |
| 3 | Sibling scan + fix across the artifact-authoring validator family; coverage report | Generalization must be proven across the class, not just #334's two surfaces | coverage report; in-class gaps fixed; out-of-class entries justified | planned |
| 4 | De-launder the disposition escape (presence-only lineage field + rung-2 reviewer), dogfood on this goal, critique | The delicate, contract-touching change goes last with the most proof | contrived laundering caught; floor not a classifier; this goal's closeout passes under the new rule; SHIP critique | planned |
| 5 | Closeout: full gate, retro, dogfooded disposition, doc/handoff sync | Make it auditable and prove the loop is closed | full gate PASS; retro + disposition-review; coverage report linked from handoff | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — planned: Slice 1 → `spec` + `critique`; Slice 2–3 → `impl` +
  `quality`; Slice 4 → `impl` + `critique`; Slice 5 → `quality` + `retro`. Confirm
  via `find-skills` and record the returned route at completion.
- **Gather** — n/a — no external URL/Slack/Notion/Docs/Drive source; shaped from
  this session's retro + the in-repo recurrence lineage only.
- **Release** — n/a — harness-internal change; no version bump or install-manifest
  edit; `achieve` does not push.
- **Issue closeout** — #284/#308/#325/#329/#332 (closed lineage) and #334 (open,
  the latest instance) are tracked CONTEXT, not a close-by-this-goal commitment.
  Whether #334 is folded/closed/reframed as "this generalization supersedes it" is
  a Slice decision, recorded at completion; default `Issue closeout: n/a — context
  only` unless a slice deliberately closes one.

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1._

### Slice 1: Slice 1 — Design spec + fresh-eye critique

- Objective: Spec the de-launder mechanism + the preflight-generalization shape; decide the design axes; resolve the content-classifier + non-discretionary guardrails before any code.
- Why this approach: The de-launder has a hard guardrail (no content classifier in the deterministic floor); design + fresh-eye critique lowest-regret first.
- Commits:
- What changed: charness-artifacts/spec/authoring-preflight-generalization-and-disposition-delaunder.md (new design contract).
- Alternatives rejected: De-launder via filing-time dedup in issue (rejected as primary: heavier, needs a recurrence index, and 'matches a recurring class' at filing time is a substance call better left to rung-2). A3 exit-0 advisory tier (rejected after critique: doc-equivalent = the G2 trap; replaced with a blocking structural-sweep member + scaffold-by-construction).
- Targeted verification: check-markdown (0 errors), check_doc_links (clean). Fresh-eye design critique (different agent context, read-only): SHIP-WITH-CHANGES; all must-fix findings folded into the spec.
- Test duplication pressure:
- Critique: Fresh-eye SHIP-WITH-CHANGES. Real findings folded: A3 tier was doc-equivalent (now blocking structural-sweep + scaffold-by-construction); goal-closeout has no scaffold (registry now marks it validator-constants+template); G3 restated as verdict-relocation; lineage floor value honestly attributed to rung-2 (floor is presence-only forcing function). Verified-safe: critique scaffold round-trips, retro isolation holds by construction, validators not at commit boundary today (relocation is genuine new value).
- Off-goal findings: None.
- Lessons carried forward: Design axes locked: (A) general dispatcher + family registry reading shape from scaffolds/validator-constants, wired as a BLOCKING commit-boundary structural-sweep member + scaffold-by-construction; (B) de-launder = presence-only recurrence-lineage marker (rung 1d in goal_artifact_disposition, grammar in shared disposition_form) on issue-form Auto-Retro dispositions + rung-2 reviewer falsifies novel:. Enforce-from-date 2026-06-08 so THIS goal dogfoods. Standalone-retro extension deferred (named open escape).
- Metrics:

### Slice 2: Slice 2 — General artifact-surface preflight + blocking commit-boundary wiring (#334 proving instance)

- Objective: Build the general dispatcher + family registry; wire it as a BLOCKING commit-boundary structural-sweep member; connect the critique scaffold (Arm 2). Prove on the critique-artifact + goal-closeout surfaces.
- Why this approach: The #334 surfaces are the proving instances; the blocking arm (not an advisory) is what makes the fix non-discretionary per the Slice-1 critique.
- Commits: pending (this slice commit)
- What changed: NEW scripts/check_artifact_surface_preflight.py (registry + describe/--emit-stub/--changed-artifacts). scripts/staged_commit_gate_plan.py: _artifact_shape_gates + check-artifact-shape (staged) in STRUCTURAL_SWEEP_LABELS. skills/public/critique/references/counterweight-triage.md: cite the scaffold (Arm 2). docs/conventions/authoring-preflight.md: artifact-shape preflight section. tests/quality_gates/test_check_artifact_surface_preflight.py (NEW) + 2 cases in test_staged_commit_gate_plan.py. Plugin mirror synced.
- Alternatives rejected: Exit-0 advisory tier (rejected per Slice-1 critique SC-1: doc-equivalent = G2 trap). Re-declaring shape in the dispatcher (rejected: drift; it reads scaffold/template/validator-constants instead). Importing the heavy goal-closeout module for constants (rejected: read the goal template's Final Verification block instead — lighter, single source).
- Targeted verification: py_compile + ruff clean; 39/39 pytest (dispatcher unit + grouping/blocking logic + gate-plan wiring + scaffold round-trip). Proving test: a parent-delegated critique missing Reviewer Tier Evidence is BLOCKED at the commit boundary (the #334 catch), a scaffold round-trip PASSES. Behavior preservation: validate_critique_artifacts/ideation/retro --all still green (255/0/156); validators untouched. Mirror byte-synced (no staged drift); export-safe imports (444 files); doc-links + markdown clean.
- Test duplication pressure: New tests target a new module (check_artifact_surface_preflight) + new gate-plan branch; no duplication of existing suites — they exercise the registry/grouping and the structural-sweep wiring not covered elsewhere.
- Critique: Slice-1 fresh-eye findings applied in-build: blocking tier (not advisory); registry marks goal-closeout as no-scaffold; G3-precise (relocation, not new requirement) proven by behavior-preservation check.
- Off-goal findings: None.
- Lessons carried forward: Dispatcher registry now holds critique/ideation/retro (prefix-mapped, commit-boundary) + goal-closeout (shape-only). Slice 3 extends to adapter-scoped debug/quality/handoff + the coverage report.
- Metrics:

## Context Sources

Follow these in order to reconstruct the goal from a cold start:

1. **The recurrence lineage (the whole point).** Issues #284, #308, #325, #329,
   #332 (closed) and #334 (open). #332's body is the key: "Memory-only reminders
   have not stopped this from recurring … the tooling already exists; the gap is
   that running it is discretionary, so it is forgotten." Its fix made the
   *structural sweep* non-discretionary but did NOT cover the artifact-shape
   validators — which is exactly the remaining gap.
2. **This session's retro + the laundering finding:**
   `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`
   (the #334 trigger and the disposition-laundering observation).
3. **Prior goals that touched the same areas (evidence the fix never generalized):**
   `2026-06-08-preflight-gate-phase-coverage.md` (#328),
   `2026-06-04-291-292-284-activation-index-and-skill-preflight.md` (#284),
   `2026-05-30-253-improvement-disposition-gate.md` (the disposition gate),
   `2026-06-02-workflow-review-efficiency-and-generalization.md`.
4. **The existing preflight to generalize:**
   `scripts/check_skill_surface_preflight.py`, `docs/conventions/authoring-preflight.md`.
5. **The disposition gate to de-launder (respect its guardrail):**
   `skills/.../achieve/scripts/goal_artifact_disposition.py`,
   `goal_artifact_closeout_evidence.py`, and the rung-2 fresh-eye reviewer flow.
6. **The artifact-validator family to scan:** `scripts/validate_critique_artifacts.py`,
   `scripts/check_goal_artifact.py`, `scripts/validate_retro_artifact.py`,
   `scripts/validate_debug_artifact.py`, `scripts/validate_ideation_artifact.py`,
   `scripts/validate_quality_artifact.py`, `scripts/validate_handoff_artifact.py`.

## Interview Decisions

- **How to break the loop (asked 2026-06-08).** Family: {generalize the
  non-discretionary preflight (real application), fix the disposition-laundering
  process, just correct #334, diagnose-only}. Chosen by the user: *generalize the
  preflight (real application)* AND, in the follow-up, *also modify the skill to
  prevent the laundering escape* AND *scan + fix sibling skills in the same goal*.
  Rejected: "just correct #334" (would be the N-th narrow point-fix — the exact
  anti-pattern); "diagnose-only" (user wants the fix shaped now).
- **De-launder mechanism (NOT pre-committed; Slice-1 axis).** Family: {presence-
  only recurrence-lineage field on issue-routed dispositions; strengthen the rung-2
  fresh-eye reviewer to check "is this a re-file of a known recurring class?";
  recurrence-index/dedup check at issue-filing time in `issue`; a combination}.
  Hard constraint: the deterministic floor must NOT become a content classifier
  (achieve guardrail). Recorded as anti-anchoring axis: `axis: where the
  recurrence judgment lives (deterministic-presence vs fresh-eye-substance vs
  filing-time-dedup)`.
- **Sibling-scan breadth (strong default).** Family: {artifact-authoring shape
  validators only; all ~35 required-shape validators; everything}. Default:
  *artifact-authoring shape validators only* (the true siblings of #334's class);
  infra validators (packaging/supply-chain/adapters/…) are out of class.
- **Mode (not asked; strong default).** implementation-continuation with a spec
  front for Slice 1 — concrete harness change, but the de-launder needs design +
  critique before code.

## Plan Critique Findings

Self-critique (Before-phase). Fresh-eye critiques run at the Slice-1 design
boundary and the Slice-4 de-launder boundary per the verification plan.

- **The goal could itself become a narrow point-fix (the central risk).** Folded:
  success is defined as a GENERAL mechanism + a sibling-coverage report, with
  #334's two surfaces only as proving instances; "just patch #334" is an explicit
  Non-Goal.
- **The de-launder could violate achieve's own "no content classifier in the
  deterministic floor" guardrail.** Folded: Non-Goals + a dedicated Slice-1 spec +
  critique; the design splits deterministic-presence from fresh-eye-substance.
- **A "discoverable doc" relapse for workstream 1.** Folded: Non-Goals explicitly
  forbid a doc as the primary fix; the proof is non-discretionary author-time
  behavior, echoing #332's own conclusion.
- **Modifying public-skill prompt surfaces without proof.** Folded into Boundaries
  (prompt-behavior-proof + dogfood + cautilus-on-demand) and the mandatory
  this-goal-dogfoods-its-own-closeout requirement.
- **Broad scope / 3 workstreams.** Folded: sliced and sequenced lowest-risk-first,
  de-launder last with critique; done-early policy points at remaining uncovered
  surfaces, not unrelated work.
- **Over-worry, not folded.** Rewriting all ~35 validators, or covering infra
  validators — out of class; the validators stay the source of truth.

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here — and, per this goal's own thesis, check the recurrence lineage before
filing a fresh narrow issue._

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

1. Author into a critique artifact / goal closeout-evidence block and confirm the
   required shape is surfaced/stubbed at author time (no gate-time surprise).
2. Read the sibling-coverage report; confirm in-class gaps were fixed.
3. Confirm a contrived recurring-class re-file is caught and the deterministic
   floor is not a content classifier.
4. `./scripts/run-quality.sh --read-only` + the touched validators' tests green;
   no existing gate verdict changed; mirror synced; this goal's own closeout
   passed under the new rule.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
