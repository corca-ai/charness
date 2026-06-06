# Spec: Pre-Push Gate for Changed-Line Mutation Coverage

Date: 2026-06-06 (refreshed from draft handoff; forced-interrupt carry-forward)
Source: debug #320 (`charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md`),
recurrence #321 (`Mutation test regression on main`, closed per-file 2026-06-06).
Status: **spec — ready for impl** (first slice named below).
Seam class: repeated symptom on one seam (#219 -> #251 -> #260 -> #320 -> #321).

## Problem (Seam, not the single file)

The scheduled mutation gate fails on `main` whenever a newly-changed line in an
eligible mutation-pool Python file lacks test coverage: the changed-line
classifier drops the file before mutation and reports `Blocking signals: FAIL`.
Each instance is resolved per-file by covering the flagged lines (the durable
per-file fix per `skills/public/quality/references/mutation-testing.md`), but the
**seam** keeps producing the same post-merge failure because there is no
pre-push/per-slice gate that forces coverage of newly-added lines/branches in
mutation-pool files. **This is the 5th occurrence** (#321 added 2026-06-06,
signature identical to #320: `Blocking signals: FAIL (changed-line
coverage/selection)`). #251 and #260 already proposed a pre-merge detection
follow-up that was never built — which is why #320 and #321 recurred.

## What Already Exists (most of the build is done — the gap is wiring)

- **`scripts/check_changed_line_mutation_coverage.py` already reproduces the
  blocking changed-line signal** locally over a `base..head` range, reusing the
  gate's own `classify_changed_line_scope_gap`. It already exposes the flags this
  spec needs:
  - `--base-sha` / `--head-sha` (range selection; default `$MUTATION_BASE_SHA` /
    `$MUTATION_HEAD_SHA` else `HEAD`),
  - `--reuse-coverage` ("reuse an existing coverage JSON instead of running the
    slow gate probe") — **the cheap-heuristic path is already implemented**,
  - `--coverage-json` (point at an existing coverage JSON).
  It is faithful but **not wired into any gate**: no `run-quality.sh`,
  `.githooks/`, or `run_slice_closeout.py` invokes it. Its only non-self
  references are the plugin-export copy and an **already-existing unit test**
  `tests/quality_gates/test_changed_line_mutation_coverage.py` (which already
  covers the uncovered / covered / no-pool-change cases — see Acceptance Checks).
- **Subprocess coverage is already captured wholesale.** The gate's
  `run_test_coverage` runs with `COVERAGE_PROCESS_START`, so subprocess-executed
  lines are already measured; `classify_changed_line_scope_gap` only distinguishes
  tracked-and-covered vs not. There is **no** existing subprocess-only-file
  classifier or selective-escalation branch — building one is net-new work, not
  wiring (see Deferred Decisions).
- **`.githooks/pre-push` already computes the exact push range** it needs to
  classify full-vs-docs-only gating: it reads `<remote-sha>..<local-sha>` pairs
  from stdin (`git help githooks` format) and classifies the union diff. That
  push range **is** the `base..head` the changed-line gate wants — no separate
  base-selection machinery to build.
- **`scripts/run-quality.sh` already has a `read-only` mode "(e.g. the pre-push
  hook)"** with a `queue_selected "<name>" <cmd>` + `flush_phase` wiring pattern.
  A new gate is one `queue_selected` line conditioned on mode.

## Sibling Population (cross-codebase scan, from #320)

The class is broad, not isolated — motivation for a standing gate, not a list to
hand-cover:

- **9 `except SurfaceError` handlers** (closest same-family siblings of the #320
  fix), plus the fixed `staged_commit_gate_plan.py:72`.
- **~75 structural degrade-return twins** (`except <Specific>Error:` -> trivial
  `return/pass/continue`) across mutation-pool `scripts/**` and `skills/**`.
  Each is a latent #320 the moment its line is *changed*; only a pre-push gate
  running over the changed range catches them in-slice.

## Current Slice

Wire the **existing** `check_changed_line_mutation_coverage.py` reproducer into
the **pre-push** boundary so a newly-added uncovered changed line in a
mutation-pool file fails locally — with an actionable `path:line` target —
*before* the commits reach `main` and the <=3h cron re-derives the same failure.

## Fixed Decisions (resolved this session)

1. **Phase = pre-push hook** (not per-slice closeout). Rationale: the seam fails
   *post-merge on the cron*; the pre-push boundary is the last local point before
   commits reach `main`, and `.githooks/pre-push` already runs `run-quality.sh`
   read-only there. Per-slice would regress closeout latency for a failure mode
   that only matters at the push boundary.
2. **Base selection = the pre-push hook's already-computed push range**
   (`remote-sha..local-sha`, the union when multiple refs). Outside the hook
   (manual/opt-in invocation), fall back to `$(git merge-base origin/main
   HEAD)..HEAD`. When the hook yields no base (new-ref / zero-sha case, pre-push
   forces the full gate) the changed-line gate stays **non-blocking** (the
   reproducer already exits 0 on no-base), so it never blocks a first push.
   Rationale: charness commits land directly on `main`; the unpushed range is
   exactly what the cron will later diff.
3. **Cost = `--reuse-coverage` cheap default; one coverage probe, reused.** Reuse
   the coverage already produced in the pre-push run for the changed lines (the
   common case: #320 `staged_commit_gate_plan.py:72-73`, #321
   `resolve_adapter.py:49`). Because the reproducer's probe already captures
   subprocess coverage via `COVERAGE_PROCESS_START`, a single faithful probe (or a
   reused coverage JSON) is enough for in-process **and** subprocess-executed
   lines; no per-file escalation engine is in this slice. The residual
   subprocess-only false-positive edge is a **deferred probe**, not a slice-1
   build (see Deferred Decisions). Rationale: near-zero marginal cost at pre-push;
   do not build a classifier the existing probe already obviates.
4. **No threshold/budget relaxation.** Per `mutation-testing.md`, the durable fix
   is *covering the lines*, never lowering a floor. This spec is about detection
   *timing*, not scoring thresholds.

## Probe Questions (answer through the impl slice, not up front)

- **P1 — coverage-JSON source at pre-push.** Does the read-only `run-quality.sh`
  pre-push path already emit a reusable coverage JSON (`--coverage-json`), or must
  the gate produce one? Wire to the existing artifact if present; otherwise the
  slice adds the minimal coverage emission.
- **P2 — failure UX.** Confirm the blocking output prints actionable
  `path:line` targets (the script already targets this) and a one-line "cover
  these lines" pointer to `mutation-testing.md`, not a raw traceback.

## Deferred Decisions (safe to wait)

- **Subprocess-only false-positive escalation engine.** A per-changed-file
  "this file is subprocess-only, the cheap signal is untrustworthy" classifier
  with selective escalation does **not** exist and is net-new work. The existing
  probe already captures subprocess coverage (`COVERAGE_PROCESS_START`), so this
  edge is narrow; build it only if a real false positive surfaces post-wiring.
  Named follow-up slice, not slice 1.
- **Selection/workload-budget drops** (`setup_agent_docs_fresh_eye_lib.py`,
  `setup_commit_discipline_lib.py`): a *distinct* non-coverage signal
  (`follow-up:mutation-selection-budget-setup-libs`). Out of scope — this spec is
  changed-line *coverage*, not selection budget.
- **CI-PR enforcement**: charness runs no push/tag CI (only
  `workflow_dispatch`/path-scoped PR/cron). A future light push/tag CI mirror of
  this gate is a separate decision (handoff `Discuss`).

## Non-Goals

- Not a mutation-score change; no floor/threshold tuning.
- Not a rewrite of the scheduled cron gate; the cron stays the backstop.
- Not hand-covering the ~84 sibling degrade branches; the gate catches each when
  its line is *changed*.

## Deliberately Not Doing (rejected, with reason)

- **Per-slice gate** — rejected: latency cost on every slice for a push-boundary
  failure mode; the cheap win is at pre-push.
- **A net-new subprocess-only escalation engine in slice 1** — rejected: the
  existing probe already captures subprocess coverage (`COVERAGE_PROCESS_START`),
  so a per-file classifier is mostly redundant; deferred to a follow-up slice if a
  real false positive appears.
- **A blanket exempt-list of "known degrade branches"** — rejected: hides
  regressions (`lint-ignore-discipline`); the gate must fail on *any* uncovered
  changed line, not consult an allowlist.
- **Building new base-selection machinery** — rejected: the pre-push hook already
  computes the push range.

## Constraints

- Portable per implementation-discipline: no host-specific path assumptions; the
  gate resolves repo-root and reuses existing run-quality wiring.
- Cost-bounded: the default path must not add a fresh slow coverage probe; it
  reuses already-run coverage.
- `mutate -> sync -> verify -> publish`: the new gate is a *verify*-phase check;
  it must not mutate tracked artifacts in read-only/pre-push mode.

## Success Criteria

1. **(The load-bearing one — the gate, not the script.)** The wired pre-push path
   (`run-quality.sh --read-only` → the new gate) **fails the push** when a
   mutation-pool file has a newly-added uncovered changed line, with an actionable
   `path:line` target, *before* the scheduled cron would re-derive it.
2. The wired gate's default cost is bounded (reuses pre-push coverage; no fresh
   slow probe) and does not regress pre-push latency beyond the chosen budget.
3. A covered changed line, and a non-mutation-pool change, **pass** (no false
   positive at the gate boundary).
4. The read-only pre-push run does **not** mutate tracked artifacts
   (`charness-artifacts/`, generated surfaces).
5. No threshold/budget relaxation introduced.

## Acceptance Checks

**The reproducer's unit behavior is already proven** —
`tests/quality_gates/test_changed_line_mutation_coverage.py` already covers
true-positive (`test_flags_uncovered_changed_lines`), true-negative-covered
(`test_passes_when_changed_lines_are_covered`), and out-of-pool
(`test_passes_when_no_eligible_pool_file_changed`), plus untracked-blocks and
run-probe cases. **The acceptance gap is the wiring**, not the script.

- **AC-WIRE (the missing, load-bearing check — SC1).** Assert the
  `queue_selected "check-changed-line-mutation-coverage"` gate, run via
  `run-quality.sh --read-only` over a push range that reintroduces a #320-class
  uncovered changed line, **fails** (`flush_phase` non-zero) and surfaces the
  `path:line` target. Falsifier: the read-only run passes with the bad line
  present. This is the check SC1 currently lacks.
- **AC-CLEAN (SC4).** Assert the read-only pre-push run leaves `git status`
  clean — no write to `charness-artifacts/` or generated surfaces (mirrors the
  `inventory-sloc` read-only discipline at `run-quality.sh`).
- **AC-COST (SC2).** Assert the wired default invocation passes
  `--reuse-coverage` and triggers no fresh slow probe in the in-process case.
- **AC-PASS (SC3).** Assert a push range with only covered changed lines, and one
  with only non-pool files, pass the wired gate (no false positive).
- Reuse the existing unit tests for reproducer-level proof; add AC-WIRE / AC-CLEAN
  to `tests/quality_gates/` as the new durable, checked-in proof of the wiring.

## Critique

### Forced-interrupt consumption (planner-mandated)

`scripts/plan_risk_interrupt.py --json` returned `status: blocked, required:
true` for this seam. The lines below are the machine-checked interrupt
carry-forward (exact prefixes parsed by
`risk_interrupt_lib.parse_spec_interrupt_resolution`):

- Interrupt Source: issue-320-mutation-changed-line-coverage
- Seam Summary: the scheduled mutation gate keeps failing post-merge because a newly
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the build is wiring an existing faithful reproducer plus AC-WIRE/AC-CLEAN over the existing pre-push push-range; no new detection engine, so ordinary impl can proceed once this spec is committed.
- What Disproving Observation Is Resolved: a 6th post-merge "Mutation test regression on main" of the changed-line class; AC-WIRE (a known #320/#321-class uncovered changed line fails the wired pre-push gate with a path:line target before reaching main) is the falsifiable resolution — until AC-WIRE passes, the seam is not closed.

### Bounded critique (fresh-eye reviewer run — findings folded)

A bounded fresh-eye reviewer (different agent context, read-only) returned
REVISE; all findings are folded into this revision:

- **Over-build trap (folded).** The original draft embedded a net-new
  "subprocess-only escalation" engine inside a "just wiring" thesis. The existing
  probe already captures subprocess coverage (`COVERAGE_PROCESS_START`), so the
  escalation is **deferred** (Deferred Decisions), not slice 1.
- **Overstated acceptance (folded).** AC1–AC3 already exist as unit tests in
  `tests/quality_gates/test_changed_line_mutation_coverage.py`; the Acceptance
  Checks now redirect the bar to the genuinely-missing **AC-WIRE / AC-CLEAN**
  (the gate wiring, not the isolated script).
- **Hidden sequencing (folded + standing).** The selection-budget drops stay an
  explicitly deferred, distinct signal; an implementer must not fold them into
  this coverage gate.
- **Fact corrections (folded).** Fallback range formula fixed to
  `$(git merge-base origin/main HEAD)..HEAD`; "references only itself" corrected
  (an existing unit test already exercises the reproducer). Reviewer confirmed the
  reproducer flags, the pre-push push-range computation, and the `run-quality.sh`
  read-only `queue_selected`/`flush_phase` wiring all exist as the spec claims.

## Fold-In Follow-Ups

- #251 retro: a "tiny repo helper that prints changed-line coverage + blocking
  verdict pre-merge" — satisfied by wiring the existing reproducer.
- #260 retro: "verify a new pool file clears both floors before commit" —
  AC-WIRE / AC-PASS.
- #320: `follow-up:mutation-selection-budget-setup-libs` — confirm whether the
  `setup_*_lib.py` selection-budget drops recur (distinct workload-budget
  question; deferred, not in this slice).

## Canonical Artifact

This file is canonical during implementation. The debug artifact
(`charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md`)
is the root-cause record; `mutation-testing.md` owns the durable per-file fix
doctrine.

## First Implementation Slice

Scope: **cheap wiring only** (no escalation engine). Wire
`check_changed_line_mutation_coverage.py` into `run-quality.sh` read-only
(pre-push) mode as `queue_selected "check-changed-line-mutation-coverage"`,
defaulting to `--reuse-coverage` over the push range, and add **AC-WIRE** and
**AC-CLEAN** to `tests/quality_gates/` (the existing reproducer unit tests stay
as-is). Resolve P1–P2 in-slice. Stop condition: AC-WIRE fails the *wired* gate on
a reintroduced #320-class line, AC-PASS/AC-CLEAN stay green, and the read-only run
leaves the tree clean.

**Explicitly out of slice 1** (named follow-up): the subprocess-only
false-positive escalation engine (Deferred Decisions) and the selection-budget
follow-up. Do not let either expand slice 1.
