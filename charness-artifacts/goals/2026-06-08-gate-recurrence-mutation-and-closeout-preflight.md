# Achieve Goal: Harden two recurring harness gate seams: the changed-line mutation gate (#335) + the authoring-preflight closeout-floor surface

Status: active
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-gate-recurrence-mutation-and-closeout-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation with a debug front (Slice 1) — #335 is a
bug-class CI regression, so it gets a causal review before any fix.

## Active Operating Frame

- Current slice: Slice 5 (closeout: broad gate, retro, #335 issue closeout, handoff).
- Next action: broad `run-quality.sh --read-only`; retro; #335 issue closeout
  (carrier + verifier proof); handoff; fill Final Verification + Auto-Retro.
- Timebox: 4h
- Activation time: 2026-06-08
- Closeout reserve: 45m
- Done-early policy: continue_next_improvement (re-point to the next gate-seam
  hardening — e.g. the remaining `--path` adapter-dir resolution, or the next
  mutation-pool blind spot — not a quick unrelated slice).
- Verification cadence: cheap deterministic checks at commit boundaries; the local
  mutation-coverage producer + fresh-eye critique at slice boundaries; broad gate +
  the mutation-test CI verdict at the bundle/closeout boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Close **two recurring harness gate seams** so they stop re-failing or
auto-filing, applying the same "close the loop, don't file the N-th instance"
discipline that the just-shipped v0.28.0 goal used:

1. **#335 — the changed-line mutation-coverage gate's recurrence.** This is the
   next instance of the #219 → #251 → #260 → #320 → #321 seam: the gate's
   *blocking signal* keeps re-firing ("changed lines were left test-uncovered, or
   eligible changed files were dropped by selection/workload budgets, before
   mutation") and auto-filing a fresh issue. Note the mutation *score* PASSES
   (86.7% vs 80%); the FAIL is the changed-line coverage/selection signal
   (survivors clustered in `main` / `build_report`, e.g.
   `skills/public/quality/scripts/inventory_standing_test_economics.py`,
   `scripts/suggest_public_skill_validation.py`). Outcome: a falsifiable
   root-cause (genuinely-uncovered changed lines vs a selection/workload-budget
   drop), the gate restored to green, AND a structural reduction of the
   recurrence — not just covering #335's specific survivors.

2. **Closeout-floor preflight extension.** Extend the v0.28.0 author-time
   shape preflight (`scripts/check_artifact_surface_preflight.py`) to the
   **goal-closeout / coordination-floor** surfaces. The v0.28.0 run discovered the
   closeout line-shapes (Activation-time format, `Issue closeout:`, `Routing:`
   naming the routed skill, the early-close report) by FAILING the complete-flip
   ~4× — the one authoring surface the generalization did not cover, the same
   recurrence class.

Success = #335's gate is green and its recurrence structurally reduced (proven,
not asserted); authoring into a goal-closeout/coordination-floor surface surfaces
the required shape at author time (no flip-by-failure); existing gate verdicts
unchanged; both proven by the relevant gates + a fresh-eye critique; and this
goal's own closeout passes cleanly.

## Non-Goals

- Do NOT just cover #335's specific survivors and call it done — that is the N-th
  point-fix this discipline rejects; the deliverable is a root-cause + a
  recurrence reduction for the class.
- Do NOT weaken the mutation gate to make it pass (lower the score threshold,
  shrink the mutation pool, or relax the changed-line signal). The fix raises
  coverage / fixes selection honesty, never lowers the bar (no Goodhart).
- Do NOT turn the closeout-floor preflight into a new hard gate; the flip-time
  coordination floors already enforce. The preflight only SURFACES the required
  shape at author time (additive, behavior-preserving — the v0.28.0 posture).
- Do NOT build a content classifier in any new floor (carry over the achieve
  guardrail).
- Do NOT take on #184 (product success criteria + metrics) here — it is
  product-level, needs `ideation`/`spec`, and is tracked context only.
- No release/version bump unless the fix warrants a patch; `achieve` does not push.

## Boundaries

- **Bug-class for #335.** Run `debug` (a falsifiable hypothesis + causal review)
  before designing the fix; reproduce locally with the mutation-coverage producer
  (`run_slice_closeout.py --produce-mutation-coverage --verification-lock`) rather
  than guessing from the CI summary.
- **Public-skill + prompt-surface + gate-script scope.** Touches `quality`/mutation
  gate scripts and the `check_artifact_surface_preflight.py` dispatcher (+ maybe
  achieve/quality references) → prompt-behavior-proof + public-skill-dogfood +
  cautilus-on-demand policy applies; deterministic gates own closeout.
- **Behavior-preserving for existing gates.** The closeout-floor preflight is
  additive; the mutation-gate fix must not change any other gate's verdict on
  existing code. Prove with the touched scripts' tests + a before/after check.
- **Export-safe + length-safe.** Mirror sync (`plugins/charness/scripts/`) after
  any `scripts/**` or `skills/**` change.
- Discuss before activation: resolved — (a) **two coupled workstreams** is
  user-directed (the operator chose "#335 + the closeout-floor extension"),
  sequenced #335-first because its CI is red; bounded by the slice plan. (b)
  **broad "structurally reduce recurrence" framing** for #335 is intentional (it
  is the Nth instance of a known seam), bounded to the smallest mechanism that
  stops the class re-filing — not an open-ended rewrite. (c) **#335 verification
  needs the mutation-test CI** for the authoritative verdict; the agent-side proxy
  is the local producer, and the CI re-run is a named external/live proof the
  agent cannot run itself (recorded, not claimed). No irreversible side effect, no
  push/release beyond an optional patch. No consequential default left unresolved.

## User Acceptance

What the user can do to verify completion directly:

- See a `debug` artifact with a falsifiable root-cause for #335 (uncovered changed
  lines vs selection/workload-budget drop), reproduced locally.
- Confirm the changed-line mutation gate is green locally (the producer) and that
  the mutation-test CI passes on a subsequent run (the authoritative #335 verdict).
- See the recurrence structurally reduced — a named mechanism (e.g. author-time
  changed-line-coverage surfacing or a selection-honesty fix) so the same class
  stops auto-filing — not just #335's survivors covered.
- Author into a goal-closeout / coordination-floor surface and see the required
  shape (Activation-time, `Routing:`/`Issue closeout:` line forms, early-close
  report sections) surfaced at author time, before the complete-flip fails.
- Run the gates and see them green; confirm no existing gate verdict changed;
  mirror byte-synced; #335 closed with verified GitHub state.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched gate/preflight scripts' own pytest modules; a before/after
  verdict-equality check; `check_export_safe_imports` + mirror byte-sync.

### High-Confidence Checks

- The local mutation-coverage producer to reproduce + then clear the changed-line
  blocking signal for #335.
- Dogfood: authoring into the closeout-floor surfaces surfaces the required shape;
  this goal's own closeout passes.
- Broad gate (`run-quality.sh --read-only`) + the full closeout at the bundle
  boundary. Fresh-eye `critique` at the #335 recurrence-mechanism (Slice 3) and the
  preflight (Slice 4) boundaries.

### External Or Live Proof

- The mutation-test CI re-run is the authoritative #335 verdict; the agent cannot
  run CI directly — named here and reported, not claimed as locally satisfied.
- Cautilus only on an explicit log-backed prompt-behavior-proof need (consult
  `plan_cautilus_proof`; deterministic-first). None claimed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `debug` #335: falsifiable root-cause for the recurring changed-line signal (genuinely-uncovered changed lines vs selection/workload-budget drop); local repro via the producer | CI is red; bug-class needs causal review before a fix | a debug artifact with a tested hypothesis + local repro | done |
| 2 | Fix #335: cover the changed lines / fix the selection-drop, restore the gate green WITHOUT weakening thresholds | restore the gate; close the concrete instance | producer green on the changed-line gate; survivors addressed at root | done |
| 3 | Structurally reduce the recurrence: the smallest mechanism that stops THIS class re-filing; fresh-eye critique | the loop's thesis — close the seam, not the instance | a recurrence-reduction mechanism + SHIP critique | done |
| 4 | Extend the author-time preflight to the goal-closeout/coordination-floor surfaces; dogfood; critique | the one uncovered authoring surface from v0.28.0 | authoring surfaces required shape pre-flip; verdicts unchanged | done |
| 5 | Closeout: broad gate, retro, dogfooded disposition, #335 issue closeout, handoff | make it auditable | full gate PASS; retro + disposition; #335 closed + verified | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — planned: Slice 1 → `debug`; Slices 2–3 → `impl` + `quality` +
  `critique`; Slice 4 → `impl` + `critique`; Slice 5 → `quality` + `retro` +
  `issue`. Confirm via `find-skills` and record the returned route at completion.
- **Gather** — n/a — no external URL/Slack/Notion/Docs/Drive source; shaped from
  the in-repo #335 issue body + the v0.28.0 closeout artifacts.
- **Release** — likely n/a or a single patch if the #335 fix warrants it; no
  version bump assumed; `achieve` does not push.
- **Issue closeout** — #335 is a **close-by-this-goal** commitment (a real
  bug-class regression to fix); record the carrier + verifier proof at completion.
  #184 is tracked context only (`Issue closeout: n/a` for it).

## Slice Log

### Slice 1 — debug #335 (done, 2026-06-08)

- Root cause (falsifiable, confirmed): **genuinely-uncovered changed lines**, NOT
  a selection/workload-budget drop (per-line `changed_and_missing` evidence; files
  in the eligible set; fresh same-worktree probe rules out stale coverage).
- Reproduction: one instrumented coverage run via the gate's own probe, classified
  over two ranges. Over the ACTUAL next-run base `858c9eab..HEAD`: **85 uncovered
  changed lines / 3 files** — `check_artifact_surface_preflight.py` (33),
  `slice_closeout_reporting.py` (47), `check_goal_artifact.py` (5). The #335
  survivors (#332 lines in `check_python_lengths.py` + `staged_commit_gate_plan.py`)
  are now in the next run's BASE — so covering only them would let the next run
  fail on the v0.28.0 lines and auto-file a fresh issue (the recurrence proven).
- Structural root cause: the local gate runs `merge-base origin/main HEAD` (≠ the
  scheduled `prev-run-head..HEAD`) AND skips silently when coverage was not freshly
  produced (opt-in `--produce-mutation-coverage`). → host-disproves-local seam;
  next step routed to `spec` (the premerge-gate spec) for the Slice-3 mechanism.
- Artifact: `charness-artifacts/debug/2026-06-08-issue-335-changed-line-mutation-recurrence.md`
  (validates; seam-risk-index synced).

### Slice 2 — restore the gate green (done, 2026-06-08)

- Covered the genuinely-uncovered changed lines across all 5 files with focused
  tests (no threshold/pool/signal change): `check_python_lengths.py` (function
  warn/headroom guards), `staged_commit_gate_plan.py` (failing-stream echo),
  `check_goal_artifact.py` (`_evidence_missing_bits`),
  `check_artifact_surface_preflight.py` (resolve/shape/emit/describe failure arms,
  `_format_changed`, full `main` dispatch + `__main__` via runpy; removed one
  unreachable post-`parser.error` `return 2`), `slice_closeout_reporting.py`
  (`print_text` → every `_print_*` helper). Plugin mirror synced.
- Proof: re-produced coverage (gate's own probe, with the new tests) → the
  changed-line gate is GREEN over BOTH `858c9eab..HEAD` (the actual next-run
  range) and `7f0231e3..HEAD` (inclusive): `ok: True, blocking: []`. 129 touched
  tests pass; ruff/length/export-safe/mirror-drift clean.
- Note: the CI re-run is the authoritative #335 verdict (agent cannot run it) —
  the local producer over the next-run range is the recorded proxy.

### Slice 3 — structural recurrence reduction (done, 2026-06-08)

- Mechanism: the changed-line gate's SILENT skip (the recurrence driver — an
  unverified skip reads identically to a clean pass) now emits a loud non-blocking
  stderr WARNING + `coverage_not_verified`/`changed_eligible_files` in the JSON
  whenever it skips with changed eligible files present. Additive,
  behavior-preserving (exit 0 unchanged) — the v0.28.0 surfacing posture, NOT a
  new hard gate (hard-gate/auto-produce deferred by design, no Goodhart).
- Surfaces: `check_changed_line_mutation_coverage.py` (+ mirror); spec Slice 3
  entry; `quality/mutation-testing.md` "unverified-skip trap" doctrine (portable);
  helper unit test + skip-test surfacing asserts.
- Fresh-eye critique: SHIP, zero blockers — and the reviewer independently traced
  the WARNING through `run-quality.sh:296` attention-output to confirm it reaches
  the operator at the green pre-push moment (efficacy, not just code). One nit
  folded (stale-skip tests now assert surfacing). Artifact:
  `charness-artifacts/critique/2026-06-08-issue-335-changed-line-recurrence-surfacing.md`.
- RCA ledger: appended one converted `repeated_correction` (durable_kind=gate,
  class `changed-line-mutation-silent-skip-recurrence`, ref #335).

### Slice 4 — closeout-floor preflight extension (done, 2026-06-08)

- Added two author-time preflight surfaces (additive, behavior-preserving;
  `commit_boundary=False`, owned at the achieve complete flip — no validator
  verdict changes): `goal-coordination` (template `## Coordination Cues` →
  Routing:/Gather:/Release:/Issue closeout:) and `goal-early-close` (the
  early-close floor module is now itself the scaffold — `report_stub()` + CLI —
  single-source with its validator, pinned by a round-trip + cross-validator
  emit-stub test).
- Dogfood: `--type goal-coordination` / `--type goal-early-close` surface the
  required shape at author time (verified); `--emit-stub` for goal-early-close
  passes the floor validator.
- Fresh-eye critique: SHIP, zero blockers (reviewer verified invariants by
  execution — drift-binding, `changed_artifacts` checked:[], byte-unchanged
  validators). Artifact:
  `charness-artifacts/critique/2026-06-08-issue-335-closeout-floor-preflight.md`.
- Deferred follow-up: `goal-activation-preflight-surface` (the Activation: preamble
  line — enforced at activation-readiness, needs preamble extraction). Recorded in
  `charness-artifacts/spec/artifact-shape-preflight-coverage.md` + Off-Goal Findings.

## Context Sources

Follow these in order to reconstruct the goal from a cold start:

1. **#335** (Mutation test regression on main) — the failing CI summary: score
   PASS (86.7%), blocking signal FAIL (changed-line coverage/selection), survivors
   in `inventory_standing_test_economics.py` / `suggest_public_skill_validation.py`.
2. **The changed-line mutation gate + its recurrence lineage:**
   `skills/public/quality/references/mutation-testing.md`,
   `scripts/check_changed_line_mutation_coverage.py`,
   `run_slice_closeout.py --produce-mutation-coverage`; the seam history
   #219 → #251 → #260 → #320 → #321 (carried in prior release update_instructions).
3. **The closeout-floor preflight to extend:**
   `scripts/check_artifact_surface_preflight.py` (the v0.28.0 dispatcher + registry),
   the achieve closeout floors `goal_artifact_phase_routing.py` /
   `goal_artifact_coordination_floors.py` / `goal_artifact_timebox.py` /
   `goal_artifact_early_close_report.py`.
4. **The originating lesson:** the v0.28.0 goal's early-close report
   `charness-artifacts/goals/2026-06-08-authoring-preflight-and-disposition-delaunder-early-close-report.md`
   (the closeout-floor extension is its recorded primary follow-on) and its retro.

## Interview Decisions

- **Next-goal focus (asked 2026-06-08).** Family: {#335 mutation regression; the
  closeout-floor preflight extension; #184 product metrics}. Chosen by the user:
  *#335 + the closeout-floor extension* (both). Rejected: #184 (product-level,
  needs `ideation`/`spec`, a different mode) — kept as tracked context.
- **Mode (strong default, not asked).** implementation-continuation with a `debug`
  front for #335, because #335 is a bug-class CI regression.
- **#335 framing (strong default).** Structurally reduce the recurrence (the
  seam's Nth instance), not a survivor-only point-fix — mirrors the just-shipped
  goal's thesis; bounded to the smallest mechanism that stops the class re-filing.

## Plan Critique Findings

Self-critique (Before-phase). Fresh-eye critiques run at the Slice-3 recurrence-
mechanism boundary and the Slice-4 preflight boundary per the verification plan.

- **The two workstreams are loosely coupled.** Folded: sequenced #335-first
  (CI red), unified by the "recurring gate seam" thesis; each is independently
  shippable and the slice plan keeps them separable.
- **#335 could become a narrow survivor-only point-fix (the central risk).**
  Folded: Slice 3 requires a structural recurrence reduction; Non-Goals forbid
  survivor-only closure.
- **The fix could weaken the gate to pass (Goodhart).** Folded into Non-Goals: no
  threshold/pool/signal relaxation; coverage goes up or selection honesty improves.
- **#335's authoritative verdict needs CI the agent can't run.** Folded into
  Boundaries + the verification plan as a named external/live proof (local
  producer is the proxy; CI re-run is reported, not claimed).
- **Over-worry, not folded:** rewriting the mutation engine, or covering #184 —
  out of class.

## Off-Goal Findings

- **`goal-activation-preflight-surface` (deferred, Slice 4).** The preflight does
  not yet surface the `Activation:` preamble line shape (it covers the
  closeout/coordination floors). Not filed as a fresh narrow issue (recurrence
  discipline): it is enforced at activation-readiness, needs preamble extraction
  (not the `## Heading` template-section source), and is recorded in
  `charness-artifacts/spec/artifact-shape-preflight-coverage.md` for a future slice.

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

1. Read the #335 debug artifact's root-cause; confirm the local producer shows the
   changed-line gate green and the mutation-test CI passes on a later run.
2. Confirm the recurrence is structurally reduced (the class stops auto-filing),
   not just #335's survivors covered.
3. Author into a goal-closeout / coordination-floor surface and confirm the shape
   is surfaced at author time (no flip-by-failure).
4. `./scripts/run-quality.sh --read-only` green; no existing gate verdict changed;
   mirror synced; #335 closed with verified GitHub state.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
