# Achieve Goal: Close the live handoff backlog except the hardware-blocked aarch64 runtime profile: lesson BIND path, mutation regression #457, pytest subprocess-startup speed, and the nose scanner rebaseline

Status: draft
Created: 2026-07-27
Activation: `/goal @charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft awaiting activation.
- Current slice intent: real draft awaiting activation; reshape before activating
  if the acceptance boundary has changed. Once active, this names the
  reviewable-intent unit in progress and the commits it spans; critique and broad
  proof do not re-fire within one unchanged intent.
- Next action: activate with
  `/goal @charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md`
  after confirming the draft is still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost and fresh-eye proof at slice boundaries; broad pytest plus the live
  CI mutation run at closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

Close four of the five live handoff backlog items end-to-end, in an order where
each one lowers risk for the next:

1. **Lesson BIND path** (handoff #1, operator-directed "fix this first"). The
   memory loop's write path is healthy and its bind path is absent. Two halves,
   both in scope:
   - **T-fix (bind at point of use):** artifact validators report ALL violations
     in one pass instead of one rule per run, and any validator with an owning
     `scaffold_*.py` names that command in its first failure. Acceptance: a
     deliberately triple-violating handoff draft yields one message listing three
     violations plus the scaffold command.
   - **Concept identity (make recurrence measurable):** `recent_lessons_lib.normalized_key`
     keys lesson identity on normalized surface text, so re-wording resets the
     count — measured, 1594 of 1596 candidates sit at `independent_source_count == 1`
     and one concept holds 7+ rows across 6 dates without ever winning a digest
     slot. Add an explicit recurrence-class tag to retro Waste/Next-Improvement
     bullets, then re-derive `LESSON_SELECTION_ALPHA_BASE` and the 14-day
     half-life against the live 1596-candidate corpus, with a back-test asserting
     a class recurring 5x over 50 days outranks a 0-day one-off.

2. **Mutation regression #457** (handoff #6). #457's mutation score already passes
   (94.7% vs 80%); the blocking signal is that six changed files went
   test-uncovered before mutation, with 14 named `file:line` proof targets.

3. **Pytest subprocess-startup speed** (handoff #2). Measured: ~25s wall at 16
   workers, ~263s in-test CPU, 6959 spawns/run (4880 `git`, ~1840 `python`) at a
   ~31ms interpreter floor each. The two named levers are ~390 per-test git
   seedings at ~24.5ms and in-process `run_script` conversion via
   `tests/script_main.py`.

4. **Nose scanner rebaseline** (handoff #4). Confirmed live this session: the dup
   gate warns `baseline written under nose 0.19.0, now scanning with nose 0.20.0`
   and lists 4 advisory family reductions. `--restamp-tool-version` refuses while
   the live family set differs, so `--write-baseline --confirm-baseline-delta` on
   the current scanner is the standing fix.

Then push, let CI run the mutation gate, and close #457 on a green run.

## Non-Goals

- **Not the aarch64 runtime profile.** Handoff #3 (`local-linux-aarch64-4cpu`
  never run on aarch64 hardware, missing aggregate bar, the 4-core x86_64
  read-only window's remaining red) is explicitly excluded by operator decision;
  it stays in the handoff for a session with the real box.
- **Not the K-times enforcement layer.** The retro's third improvement — a
  recurrence-class that has bitten K times must carry a mechanism or an explicit
  refusal — is deferred: its data only exists once concept identity lands.
- **Not sibling-scan Tier 1 — already fixed, not debt.** Verified in the live tree
  during shaping: `scripts/record_quality_runtime.py:180` already carries
  `oldest.unlink(missing_ok=True)`, `scripts/mutation_baseline_abort_lib.py:53-55`
  already dropped the exists-then-unlink TOCTOU, and
  `scripts/check_mutation_score.py:283` already compares with `>` so a
  same-second tie keeps the marker authoritative — each with a comment stating
  the audit's own rationale. Commit `092ab996` ("Fix sibling-scan Tier-1
  findings: unlink races and mtime tie direction") landed them after the
  2026-07-20 audit was written. The audit's line numbers no longer resolve
  because the files moved on. This is the second time in two sessions a handoff
  line turned out to be a premise rather than debt.
- **Not sibling-scan Tier 2 or Tier 3.** Finding D (live `.charness/usage-episodes/`
  tree snapshot tests) needs its own design slice per the backlog's own fix
  order; Tier 3 (E–J) is boy-scout only, folded in when a slice already touches
  the line and never as its own work.
- **Not a release.** No plugin version bump expected.
- **Not the #448/#451/#453 siblings.** Verified closed on GitHub this session, so
  the handoff line naming them is stale, not debt.
- Do not absorb adjacent handoff entries beyond the four items above.

## Boundaries

- In scope, lesson BIND path: `scripts/recent_lessons_lib.py` (verified path;
  `LESSON_SELECTION_ALPHA_BASE = 0.35` at :15, `LESSON_SELECTION_HALF_LIFE_DAYS = 14`
  at :17, and `_normalize_lesson_key` truncating to the first 14 words at :136 is
  the surface-text identity to replace), `charness-artifacts/retro/lesson-selection-index.json`,
  `scripts/validate_handoff_artifact.py`, `scripts/artifact_validator.py`, the
  sibling `validate_*_artifact.py` family, `scripts/refresh_recent_lessons.py`,
  retro authoring/validation surfaces, and their tests.
- In scope, #457: `scripts/artifact_validator.py`,
  `scripts/check_changed_line_mutation_coverage.py`,
  `scripts/check_doc_authoring_preflight.py`, `scripts/check_doc_links.py`,
  `scripts/record_quality_runtime.py`, `scripts/validate_debug_artifact.py`,
  `scripts/gate_report_emit.py`,
  `skills/public/critique/scripts/scaffold_critique_artifact.py`,
  `scripts/agent-runtime/contract-versions.mjs`, plus the tests that cover them.
- In scope, speed: `tests/script_main.py`, per-test git-seeding fixtures, and
  `tests/conftest.py`. Explicitly NOT fixture caching, and NOT the deferrals
  already pinned by `tests/quality_gates/test_hot_path_import_weight.py`.
- In scope, baseline: `charness-artifacts/quality/dup-review.json`,
  `skills/public/quality/scripts/check_dup_ratchet.py`,
  `skills/public/quality/scripts/dup_ratchet_rebaseline.py`.
- **Generated mirrors:** several in-scope scripts (including
  `scripts/record_quality_runtime.py`) have `plugins/charness/scripts/` mirrors.
  Mutate canonical source, then sync before validators — this is a hard phase
  barrier, not a cleanup step.
- Portable per implementation-discipline: no host-specific assumption. The issue
  backend stays adapter-resolved through the `issue` skill seam; no hardcoded
  provider literal.
- Stop conditions: name on first discovery, do not guess. Stop if the alpha
  re-derivation would change digest selection in a way that cannot be back-tested
  against the live corpus; stop if the nose rebaseline delta contains a genuine
  new-duplication family rather than only reductions and version skew.

## User Acceptance

- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`
  no longer prints the `nose version skew` warning.
- A deliberately triple-violating handoff draft, run through
  `python3 scripts/validate_handoff_artifact.py --repo-root .`, prints all three
  violations in one message and names the owning scaffold command — not one rule
  per run.
- `python3 -m pytest -q` wall-clock is measurably lower than the recorded ~25s
  baseline at the same worker count, with before/after numbers and spawn counts
  in the Slice Log.
- Issue #457 is closed on GitHub, with the green mutation workflow run linked as
  the closing evidence.
- A back-test in the suite asserts that a lesson class recurring 5x over 50 days
  outranks a 0-day one-off.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/validate_handoff_artifact.py --repo-root .` and the sibling
  artifact validators at every commit boundary.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`
  before and after the rebaseline slice.
- Targeted `pytest` node ids for each slice's own tests.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.

### High-Confidence Checks

- Broad `python3 -m pytest -q` at the verification lock, with wall-clock and
  `spawns/run` recorded so the speed slice's claim is measured, not asserted.
- The lesson-selection back-test run against the real 1596-candidate corpus, not
  a synthetic fixture, so the alpha re-derivation is proven against live data.
- `python3 scripts/check_changed_line_mutation_coverage.py` on this branch's own
  diff, to confirm the #457 fix generalizes to the new changed lines rather than
  only retro-fitting the 14 listed targets.
- Bounded fresh-eye subagent critique at each substantial slice boundary, and a
  resolution critique for #457 per the `issue` contract.

### External Or Live Proof

- **Push to origin, then the real CI mutation workflow run.** This is the only
  proof that closes #457: its blocking signal is computed by the workflow against
  the pushed diff, so no local check can substitute. Approved by the operator
  this session.
- **Close #457 via the `issue` skill**, gated on that run reporting green. If the
  run stays red, the issue stays open and the residual is reported, not narrated
  as fixed.
- Honest limit: local gates can only make #457 *likely* fixed. Any statement that
  #457 is resolved before a green run exists is a false claim and must not be
  made.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Bind lessons at the point of use: one-pass violation reporting across the artifact-validator family, and the owning `scaffold_*.py` named in the first failure | Operator-directed first; every later slice in this run is authored by a session that inherits the improved validator behavior | Triple-violating draft yields one message with three violations plus the scaffold command; regression test pins the one-pass contract | pending |
| 2 | Give lessons a concept identity: recurrence-class tag on retro bullets, re-derived alpha and half-life, back-test over the live corpus | The count is useless while the weighting cannot act on it; both halves ship together or neither binds | Back-test asserting a 5x/50-day class outranks a 0-day one-off; measured multiplier distribution moves off 1.0 | pending |
| 3 | Cover #457's 14 changed-line proof targets and kill the surviving `gate_report_emit` mutants | Clears the red before the speed slice changes the suite, so slice 4's delta is attributable | New tests for the 6 named files; `check_changed_line_mutation_coverage.py` clean on this branch's diff; `plugins/` mirrors synced | pending |
| 4 | Cut pytest subprocess-startup cost via the two measured levers | Lands after the red is cleared so the before/after delta is attributable to the lever, not a pre-existing failure | Before/after wall-clock and spawn counts at the same worker count; suite still green | pending |
| 5 | Rebaseline the nose scanner with `--write-baseline --confirm-baseline-delta` | Last, because slices 1-4 change files the dup scanner reads; baselining earlier invites a second rewrite | Dup gate runs clean with no version-skew warning; delta reviewed as reductions plus skew only | pending |
| 6 | Push, run CI mutation, close #457 on green | The only proof that closes the issue; bundle boundary | Green workflow run linked on the closing commit and the issue | pending |

**Per-slice proof cost and test-duplication pressure.** Slices 1-3 add tests and
are the ones that could push the broad duplicate/length gate toward threshold —
slice 3 most of all, since covering six scripts invites near-identical test
bodies, and the dup gate already reports 4 advisory family reductions. Each of those slices carries a cheap `--test-pressure` sample in its
slice log entry. Slice 4 removes process spawns rather than adding tests, so its
pressure risk is low but its regression risk is high (fixture semantics change).
Slice 5 adds no tests. If the broad duplicate gate fails at closeout, classify
new-slice-local versus accumulated suite debt before touching the threshold.

## Operator Decision Queue

- Decision: whether sibling-scan Tier 2 finding D (tests snapshotting the live
  `.charness/usage-episodes/` tree) becomes its own slice after this goal.
- Owner: operator.
- Why deferred: it is a latent conditional flake needing design, not a 1-2 line
  fix, and nothing in this goal blocks on it.
- Unblock action: say whether to schedule it next, or leave it in the sibling-scan
  backlog.
- Revisit trigger: the first time that test fails in CI, or this goal's closeout.

## Coordination Cues

Routing chosen from installed skill metadata and model judgment:

- `debug` before the slice-3 fix, because #457 is bug-class: locate why the six
  changed files were left uncovered before mutation rather than patching the 14
  listed lines and calling the class closed.
- `impl` for each slice, with `prove` at its stop gate.
- `quality` for the verification cadence and for the dup-ratchet posture in slice 5.
- `issue` for #457 closeout (`Close #457` on the closing commit) and for any
  off-goal finding surfaced mid-run.
- `critique` for slice-boundary fresh-eye review and the #457 resolution critique.
- `retro` at closeout.
- `Routing:` / `Gather:` / `Release:` / `Issue closeout:` evidence recorded here
  at completion.

Discuss before activation: RESOLVED this session. Four consequential defaults
were surfaced and answered by the operator before saving. (1) *External side
effects:* push to origin and close #457 are both approved, with the close gated on
a green CI mutation run. (2) *Proof-level non-claim:* #457's blocking signal is
CI-computed, so local gates cannot prove it; the artifact records this as a
non-claim rather than letting a local green stand in. (3) *Broad bundled scope:*
five source items in one goal is deliberately wide, accepted because slices stay
independently committable and each has its own proof, and the ranking rationale
for the order is recorded in Interview Decisions. (4) *Scope exclusion:* the
aarch64 profile is dropped by explicit operator decision, not by agent judgment.

## Slice Log

## Context Sources

Follow in this order to reconstruct the originating context:

- [docs/handoff.md](../../docs/handoff.md) `## Next Session` — the backlog this
  goal was chunked from; entries #1, #2, #4, #5 are in scope and #3 is excluded.
- [charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md](../retro/2026-07-26-lesson-recurrence-mechanism.md)
  — owns both halves of the lesson BIND finding, the measured multiplier
  distribution, and the Engelbart/Klein counterfactuals behind the T-fix framing.
- [charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md](../audit/2026-07-20-abstracted-pattern-sibling-scan.md)
  — owns sibling-scan Tier 1 A/B/C with exact file:line and fix, the Tier 2/3
  deferral rationale, and the confirmed-safe list that must not be re-audited.
- GitHub issue #457 (`Mutation test regression on main`) — source of truth for
  the 14 changed-line proof targets, the 6 blocking files, and the surviving
  mutants. Workflow run: https://github.com/corca-ai/charness/actions/runs/30182110672
  (head `aeca200f5d5a42307eff9d53914da6463887fb3e`, base `1c6de037919de23ebca29e05179393129f5ddd44`).
- [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md) — the
  digest whose selection defect slice 2 fixes.
- [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
  — owns the sync-before-verify barrier the `plugins/` mirrors in slice 3 depend on.

## Interview Decisions

- **Item 1 depth.** Family considered: T-fix half only / both halves / all three
  pieces including K-times enforcement. Chosen: both halves. Rejected T-fix-only
  because the retro's own evidence is that a surfaced lesson still did not bind,
  so measurability and binding are one fix; rejected all-three because the
  enforcement layer's data does not exist until concept identity lands, making it
  unbuildable now rather than merely expensive. `single-point: one repo-local
  memory loop; the lesson corpus is not host- or profile-varying.`
- **Timebox.** Family considered: no timebox / 2h / 4h. Chosen: no timebox, so
  the goal closes on the four items rather than on a clock, and no
  `Timebox:`/`Activation time:`/`Closeout reserve:` fields are recorded.
  `single-point: operator set no work budget for this run.`
- **External scope.** Family considered: local commits only / commit and push /
  push and close #457. Chosen: push and close, with the close gated on a green
  mutation run. Rejected local-only because #457's blocking signal is CI-computed
  and local-only work would leave the goal's headline item unprovable.
  `axis: issue backend` — the close routes through the `issue` skill's
  adapter-resolved backend seam (`gh` by default, host-mediated capability
  otherwise), so this approval is not hardcoded to one provider.
- **Sibling-scan scope (assumed, not asked; then refuted by the tree).** The
  backlog's own next-session pickup names the fix order — Tier 1 first, Tier 2 as
  its own slice, Tier 3 opportunistic — so a strong default settled it without
  spending a question. Checking the three Tier-1 sites before planning work on
  them showed all three already fixed by commit `092ab996`, so the item left the
  Slice Plan entirely and moved to Non-Goals with its evidence. Tier 2 was routed
  to the Operator Decision Queue rather than silently dropped.
  `single-point: one audit artifact with an explicit authored fix order.`
- **Slice ordering (agent judgment, from the chunked-routing rank).** The
  generative-sequence rank put lesson-BIND first (it changes how every later
  session selects work), #457 second (a red gate makes later verification reads
  ambiguous), speed third (measurable only against a green baseline), and the
  rebaseline last (slices 1-4 change files the dup scanner reads).
  `single-point: this run's dependency order, re-derivable from the rank reasoning.`

## Plan Critique Findings

**Premise checks run during shaping (parent agent, source-verified).** Every slice
premise was checked against the live tree before the plan locked, because the
handoff's own `## Discuss` records that two of last session's items were premises
rather than debt.

- **Refuted, folded into Non-Goals:** sibling-scan Tier 1 A/B/C are already fixed
  (commit `092ab996`). Slice 3's sibling half was deleted rather than planned.
- **Confirmed, slice 1 is correctly located:** `validate_handoff_artifact.py:165-177`
  chains seven validators that each `raise ValidationError`, so the run aborts on
  the first violation — the one-rule-per-run behavior the retro blames for
  manufacturing a retry loop is real, and the one-pass fix targets the right code.
- **Confirmed, slice 2 is correctly located:** `scripts/recent_lessons_lib.py:136`
  keys lesson identity on the first 14 normalized words of the bullet text, which
  is the surface-text identity the retro measured. Corrected the plan's original
  path claim (`skills/public/quality/scripts/...`), which did not exist.
- **Confirmed, slice 5 is live work:** the dup gate emits
  `nose version skew: baseline written under nose 0.19.0, now scanning with nose
  0.20.0` plus 4 advisory family reductions, on this tree, today.
- **Confirmed, item 5's issue references are stale:** #448, #451, and #453 are all
  CLOSED on GitHub; #457 is the only open issue.

**Bounded fresh-eye reviewer: NOT PROVEN.** A `bounded-reviewer` subagent was
spawned for the five plan-critique angles (wrong-target risk, slice-order
soundness, acceptance testability, over-anchoring/scope, over-worry counterweight)
and had not returned a report when this draft was saved. The premise checks above
are the parent's own work and do not substitute for fresh-eye review. Before
activation, either collect that report and fold it here, or record the review as
unrun — do not treat this section as complete on the parent's checks alone.

## Off-Goal Findings

- `goal_artifact_discussion.py:13` matches the resolution token with
  `^(?:resolved|confirmed|approved)`, anchored at the literal start of the summary
  text. A summary written as `Discuss before activation: **RESOLVED** ...` — bold,
  the natural markdown emphasis for the token the error message tells you to add —
  fails the match, and the error repeats verbatim with no hint that formatting is
  the cause. Hit once during this shaping session. Same defect class as slice 1
  (the tool knows the fix and does not say it), so route it there or file it via
  `issue` rather than fixing it inline here.

## Final Verification

## User Verification Instructions

## Auto-Retro
