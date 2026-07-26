# Achieve Goal: Close the live handoff backlog except the hardware-blocked aarch64 runtime profile: lesson BIND path, mutation regression #457, pytest subprocess-startup speed, and the nose scanner rebaseline

Status: active
Created: 2026-07-27
Activation: `/goal @charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 4 of 6 — cut the standing pytest gate's subprocess-startup cost.
  Slices 1-3 are committed at `ab56e15f`, `ba3b7091`, `75dd5357`.
- Current slice intent: reduce process spawns in the standing suite. Recorded
  baseline: ~25s wall at 16 workers, ~263s in-test CPU, 6959 spawns/run (4880
  `git`, ~1840 `python`) at a ~31ms interpreter floor each. Two named levers:
  per-test git seeding and in-process `run_script` conversion via
  `tests/script_main.py` (`run_loaded_script_main` at :29 is the working runner).
  NOT fixture caching, and NOT the deferrals already pinned by
  `tests/quality_gates/test_hot_path_import_weight.py`.
- Next action: RE-MEASURE before optimizing. The handoff's "~390 per-test git
  seedings at ~24.5ms" figure is unverified — slice 2's reviewer explicitly declined
  to confirm it read-only. Spawn count is the primary acceptance metric because
  wall-clock at 16 workers is noise-dominated.
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

1. **Lesson BIND path** (handoff entry 1, operator-directed "fix this first"). The
   memory loop's write path is healthy and its bind path is absent. Two halves,
   both in scope:
   - **T-fix (bind at point of use) — a WIRING job, not a build.** Fresh-eye review
     refuted the original framing: the shared one-pass path already ships
     (`scripts/artifact_validator.py:358` `run_validation_checks(collect_all=…)`,
     `:44` `scaffold_hint`, `:63` `report_validation_failure`), the scaffold
     registry already maps handoff to its owning
     `skills/public/handoff/scripts/scaffold_handoff_artifact.py`
     (`scripts/check_artifact_surface_preflight.py:176-182`), and
     `scripts/validate_quality_artifact.py:351` already records `--report-all` as
     a deprecated no-op because one-pass is the default there. The real gap is
     three unwired stragglers: `validate_handoff_artifact.py:165-177` still chains
     raising validators and `:196-198` prints the bare exception with no scaffold
     hint, and `scripts/run-quality.sh` passes `--report-all` at `:490`/`:493`/`:513`
     but not at `:489` (handoff), `:514` (ideation), or `:515` (retro). Wire those
     three through the existing path, default-on per the quality precedent, and add
     the artifact-path argument the acceptance check needs.
   - **Concept identity (make recurrence measurable):** `recent_lessons_lib.normalized_key`
     keys lesson identity on normalized surface text, so re-wording resets the
     count — measured, 1594 of 1596 candidates sit at `independent_source_count == 1`
     and one concept holds 7+ rows across 6 dates without ever winning a digest
     slot. Add an explicit recurrence-class tag to retro Waste/Next-Improvement
     bullets, then re-derive `LESSON_SELECTION_ALPHA_BASE` and the 14-day
     half-life against the live 1596-candidate corpus, with a back-test asserting
     a class recurring 5x over 50 days outranks a 0-day one-off.

2. **Mutation regression #457** (the open issue, unioned into the backlog by the
   chunker — not a `## Next Session` entry). #457's mutation score already passes
   (94.7% vs 80%); the blocking signal is that six changed files went
   test-uncovered before mutation, with 14 named `file:line` proof targets.

3. **Pytest subprocess-startup speed** (handoff entry 2). Measured: ~25s wall at 16
   workers, ~263s in-test CPU, 6959 spawns/run (4880 `git`, ~1840 `python`) at a
   ~31ms interpreter floor each. The two named levers are ~390 per-test git
   seedings at ~24.5ms and in-process `run_script` conversion via
   `tests/script_main.py`.

4. **Nose scanner rebaseline** (handoff entry 4). Confirmed live this session: the dup
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
  `scripts/validate_handoff_artifact.py`, `scripts/artifact_validator.py`,
  `scripts/validate_ideation_artifact.py`, `scripts/validate_retro_artifact.py`,
  `scripts/run-quality.sh` (the `--report-all` invocation lines),
  `scripts/refresh_recent_lessons.py`, retro authoring/validation surfaces, and
  their tests.
- **In scope, and easy to miss:** `scripts/build_retro_lesson_selection_index.py`.
  Slice 2 changes lesson identity, which invalidates the checked-in
  `lesson-selection-index.json`, and `scripts/run-quality.sh:492` runs that script
  with `--check` as a gate. Regenerate the index in the same slice or slice 2 fails
  at its own commit boundary.
- In scope, #457: `scripts/artifact_validator.py`,
  `scripts/check_changed_line_mutation_coverage.py`,
  `scripts/check_doc_authoring_preflight.py`, `scripts/check_doc_links.py`,
  `scripts/record_quality_runtime.py`, `scripts/validate_debug_artifact.py`,
  `scripts/gate_report_emit.py`,
  `skills/public/critique/scripts/scaffold_critique_artifact.py`,
  `scripts/agent-runtime/contract-versions.mjs`, plus the tests that cover them.
- In scope, speed: `tests/script_main.py` (`run_loaded_script_main` at :29 is the
  working in-process runner), per-test git-seeding fixtures, `tests/conftest.py`,
  and `scripts/boundary-bypass-exemptions.txt` — that file pins which tests may
  exercise CLI entrypoints, so converting subprocess calls to in-process ones
  touches its contract. Explicitly NOT fixture caching, and NOT the deferrals
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
- A deliberately triple-violating handoff draft yields ONE message listing all
  three violations plus the owning scaffold command. Runnable without overwriting
  the real `docs/handoff.md`: today `validate_handoff_artifact.py:180-190` accepts
  only `--repo-root` and resolves the path through the adapter, so slice 1 must
  either add an artifact-path argument or the check runs against a temp repo-root.
  Naming the mechanism is part of the acceptance, not an implementation detail.
- **Spawn count is the primary assertion; wall-clock is secondary.** `pytest`
  wall-clock at 16 workers is noise-dominated, so "measurably lower than ~25s" is
  not falsifiable on its own. Acceptance: total subprocess spawns per run drops
  from the recorded 6959 by a stated amount, deterministically, with before/after
  wall-clock reported alongside it in the Slice Log.
- Issue #457 is closed on GitHub, with the green mutation workflow run linked as
  the closing evidence.
- The recurrence back-test runs against the live 1596-candidate corpus and is
  pinned to the re-derived constants, so a synthetic test that fixes its own alpha
  cannot satisfy it while the re-derivation stays untouched: a class recurring 5x
  over 50 days must outrank a 0-day one-off under the shipped
  `LESSON_SELECTION_ALPHA_BASE` and half-life values.

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
| 1 | Wire handoff/ideation/retro validators into the already-shipped one-pass path and scaffold hint, default-on, plus an artifact-path argument | Operator-directed first; every later slice in this run is authored by a session that inherits the improved validator behavior | Triple-violating draft yields one message with three violations plus the scaffold command, run against a temp root; regression test pins the one-pass contract | done (`ab56e15f`) |
| 2 | Give lessons a concept identity: recurrence-class tag on retro bullets, re-derived alpha and half-life, back-test over the live corpus | The count is useless while the weighting cannot act on it; both halves ship together or neither binds | Back-test over the live corpus pinned to the re-derived constants; multiplier distribution moves off 1.0; `build_retro_lesson_selection_index.py --check` regenerated and green | done (`ba3b7091`); multiplier distribution unchanged until retros carry tags — recorded as an honest limit |
| 3 | Cover #457's 14 changed-line proof targets and kill the surviving `gate_report_emit` mutants | Clears the red before the speed slice changes the suite, so slice 4's delta is attributable | done (`75dd5357`) — 36 tests; all 6 mutants hand-verified killed; local coverage PROVISIONAL until slice 6's CI run |
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

- Decision: should `validate_debug_artifact.py` and `validate_critique_artifacts.py`
  flip to one-pass-by-default, matching handoff/retro/ideation after slice 1?
- Owner: operator.
- Why deferred: their current stop-at-first default is an EXPLICIT operator
  narrowing recorded in commit `a930cc5f` ("narrowed per operator decision:
  report-all pays off on the two 14-rule validators"). Slice 1's fresh-eye
  reviewer named flipping them as its highest-value change, and the family is now
  split on both default AND flag polarity (`--fail-fast` opt-out vs `--report-all`
  opt-in) — a real trap. But reversing a recorded operator decision is not an
  agent's call, and slice 1's measured evidence covers handoff, not critique/debug.
- Unblock action: say whether to flip both to default-on (making `--report-all` a
  deprecated no-op as in `validate_quality_artifact.py`), or to keep the split.
- Revisit trigger: the next multi-run rework observed on a critique or debug
  artifact; also tracked as the reopen trigger on D28.

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

**Public-skill validation review (slice 1, `quality`): no consumer-contract
change.** Slice 1 touched one `quality` skill file,
`skills/public/quality/scripts/standing_gate_verbosity_lib.py`, and the change is
a pure import-mechanism swap (a hand-rolled `spec_from_file_location` loader
replaced by the in-tree `sys.path` sibling import). Evidence it is behavior-neutral:
the 9 checked-in `test_quality_standing_gate_verbosity.py` tests pass unchanged,
`inventory_standing_gate_verbosity.py` still runs clean, and
`standing_gate_discovery_lib.py` declares only compiled regexes at module level
with no `global` mutation anywhere, so the module now being shared via `sys.modules`
instead of freshly loaded per call cannot change results. The skill's prompt,
routing, adapter requirement, and `charness-artifacts/quality/latest.md` artifact
contract are untouched, so the checked-in `quality` dogfood case in
`docs/public-skill-dogfood.json` still describes current behavior and needs no
re-freeze. Cautilus stayed unrun per repo ask-before-run policy;
`plan_cautilus_proof` reported `run_mode: ask`, `proof_kinds: none`,
`next_action: none`, so no evaluator proof was owed. Acked with
`--ack-cautilus-skill-review`.

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

### Slice 1: Wire the one-pass validator contract into handoff/retro/ideation

- Objective: Bind the repeatedly-violated lesson at the point of use: report every artifact-validator violation in one pass, name the owning scaffold, and let a candidate handoff draft be checked without overwriting the live one
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 89 targeted tests pass; run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review completed; 21 pre-commit gates pass at ab56e15f
- Test duplication pressure: 3 new dup families introduced by the new tests and refactored into shared helpers (validate_each_artifact, run_changed_artifact_validator); 1 residual pre-existing loader family accepted via --accept-family; dup gate now OK with fixable_ceiling=0
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Concept identity for lessons plus the re-derived weighting

- Objective: Make recurrence measurable (authored recurrence-class tag grouping across sections and dates) and make the weighting able to act on it (alpha 0.35->0.6, half-life 14->45), with a back-test pinned to the shipped constants
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 604 tests pass in the lesson/retro/handoff/ideation/artifact_validator selection; proven non-vacuous by reverting the constants (2 tests fail with the arithmetic); selection index regenerated and --check green; run_slice_closeout completed; 21 pre-commit gates pass at ba3b7091
- Test duplication pressure: 10 new tests in test_recent_lessons_recurrence.py plus 2 in test_retro_artifact.py; dup ratchet clean, no new families this slice
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Cover #457's rarely-taken branches and kill the surviving mutants

- Objective: Close the #457 blocking signal at the class level: give every rarely-taken changed-line branch a named behavioral contract, and kill all six surviving mutants
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 28 targeted tests pass; every mutation hand-applied and confirmed killed (ensure_ascii, sort_keys, indent x2, stream swap, keyword-only marker, plus 3 truncation mutants); run_slice_closeout completed; 8 pre-commit gates pass at 75dd5357
- Test duplication pressure: 36 new tests across 3 files (14 degradation-branch, 9 gate_report_emit, 1 critique scaffold, plus rewrites); dup ratchet clean, no new families
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: Git identity from the environment plus global-config isolation

- Objective: Cut subprocess-startup cost in the standing suite by removing per-repo git config spawns, after measuring the real spawn census rather than trusting the handoff figure
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Measured 12527 -> 11756 spawns (git config 764 -> 116) with a sitecustomize Popen probe covering every xdist worker; 5651 tests pass; fixture proven load-bearing (10 failures with identity removed, isolation on); run_slice_closeout completed; 8 pre-commit gates pass at 12bb4ab6. Wall clock NOT claimed - 109/112s after vs 121/107s before, ranges overlap.
- Test duplication pressure: No new tests; 170 lines of redundant git config spawns removed across 38 files via an AST pass; dup ratchet clean
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

Follow in this order to reconstruct the originating context:

- [docs/handoff.md](../../docs/handoff.md) `## Next Session` — the backlog this
  goal was chunked from. Of its five `## Next Session` entries, 1, 2, and 4 are in
  scope; 3 (aarch64) is excluded by operator decision and 5 (sibling scan) was
  refuted as already-fixed. Issue #457 is not a `## Next Session` entry — the
  chunker unioned it in from the live open-issue backlog.
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

**Bounded fresh-eye review: RAN, 8 findings, all dispositioned.** Reviewer
provenance: `bounded-reviewer` typed subagent (read-only: Read/Grep/Glob only, no
Bash/Edit/Write/Agent), five angles — wrong-target risk, slice-order soundness,
acceptance testability, scope/over-anchoring, over-worry counterweight. A first
spawn went idle without delivering a report and its task id no longer resolved, so
the review was re-run against the revised artifact rather than left unproven; the
lost run contributed nothing to this section.

Blockers folded:

- **F1 (wrong-target, BLOCKER) — slice 1 was planning work that mostly exists.**
  The parent independently confirmed the reviewer's evidence: `run_validation_checks(collect_all=)`
  and `scaffold_hint`/`report_validation_failure` already ship in
  `artifact_validator.py`, `validate_quality_artifact.py:351` calls `--report-all` a
  deprecated no-op, and `run-quality.sh` passes it at `:490`/`:493`/`:513` but not
  at `:489`/`:514`/`:515`. Slice 1 was rewritten from a family-wide build to wiring
  the three stragglers. **This is the third premise-vs-debt instance in two
  sessions** — a signal about the handoff/audit surfaces, not about these three
  items.
- **F5 (acceptance, BLOCKER) — acceptance #2 was unrunnable.**
  `validate_handoff_artifact.py:180-190` takes only `--repo-root`, so the
  triple-violating-draft check would have required overwriting the real
  `docs/handoff.md`. The artifact-path argument is now part of slice 1 and named in
  the acceptance line.
- **F6 (acceptance, BLOCKER) — two acceptance items passed without the fix.** The
  recurrence back-test is now pinned to the live corpus AND the re-derived
  constants (a synthetic test fixing its own alpha no longer satisfies it), and the
  speed claim now leads with deterministic spawn count instead of noise-dominated
  wall-clock.

Non-blockers folded:

- **F3** — `build_retro_lesson_selection_index.py` is gated at `run-quality.sh:492`
  with `--check` and slice 2 invalidates the index; added to Boundaries as
  easy-to-miss, and to slice 2's expected evidence.
- **F4** — slice 3's local coverage green is provisional because slice 4 rewrites
  those tests; slice 3's evidence cell now says so.
- **F7** — item numbering was internally inconsistent ("handoff #6" does not
  exist; #457 came from the issue union, not `## Next Session`). Corrected
  throughout.
- **F8** — `scripts/boundary-bypass-exemptions.txt` pins which tests may exercise
  CLI entrypoints, which slice 4's conversion touches; added to speed Boundaries.

Over-worry raised and deliberately NOT folded (do not churn on these): slice 5
last is correct and its stop condition already covers a genuine new-duplication
family; acceptance naming GitHub is fine because #457 lives there and the adapter
seam is preserved in Interview Decisions; the `goal_artifact_discussion.py:13`
finding is correctly routed to Off-Goal rather than fixed inline.

Reviewer non-claim carried forward: the handoff's "~390 per-test git seedings"
figure is **not verifiable read-only** and the reviewer explicitly declined to
confirm it. Slice 4 must re-measure it before relying on it as a lever.

## Off-Goal Findings

- **A recurrence-class slug registry would make slug abuse reviewable.** Slice 2's
  fresh-eye reviewer noted the tag is structurally ungameable in both directions:
  reusing a slug for a DIFFERENT concept inflates that class and hijacks a digest
  slot, while coining a fresh slug every time silently buys nothing. Nothing
  validates semantic sameness, deliberately — a content classifier would rot like
  the surface text it replaced. The proposed cheap guard is an existence check, not
  a classifier: declare each slug once with a one-line definition and have
  `validate_recurrence_class_slugs` fail unregistered slugs, which turns
  slug-churn into a visible diff and reuse into a reviewable change. Not built in
  slice 2 because it adds an authoring surface that should be designed with the
  operator rather than bolted on mid-slice. A cheaper partial: surface
  `independent_source_count` on the digest line so a hijacked slot is visible where
  it is spent.

- **54 files hand-roll a `spec_from_file_location` sibling-module loader** across
  `skills/` and `scripts/`, while `skills/public/quality/scripts/` alone has 19
  scripts using the shared `SKILL_RUNTIME.load_local_skill_module` and
  `check_runtime_budget.py:11-12` shows a simpler `sys.path` pattern for libs.
  Surfaced when slice 1's diff regrouped the clone graph and the dup ratchet
  reported the loader as new duplication; the family rotated to a different
  member each time one was fixed. Slice 1 fixed one instance
  (`standing_gate_verbosity_lib.py`, where the reviewer proved my
  "self-containment" justification factually wrong) and accepted the family into
  the gate baseline with `--accept-family 0c3b7ccb345f8c97` rather than convert 54
  files inside an unrelated slice. Owed: an `issue` filing for the repo-wide
  conversion. Not fixed, not classified intentional — deliberately baselined and
  named here.
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
