# Spec: Pre-Push Gate for Changed-Line Mutation Coverage

Date: 2026-06-06 (refreshed from draft handoff; forced-interrupt carry-forward)
Source: debug #320 (`charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md`),
recurrence #321 (`Mutation test regression on main`, closed per-file 2026-06-06).
Status: **impl — slice 1 (consumer) + slice 2 (producer, lever A+B) delivered**;
gate active pending push-time verification (Slice Status below).
Update (handoff-4, 2026-06-07): the consumer now emits a non-blocking
false-green `warning` (report field + stderr) when the analyzed head resolves to
`HEAD` and an eligible mutation-pool file has uncommitted worktree changes — the
`base..HEAD` range excludes them, so a clean verdict is a false green for those
changes (`false_green_warning` in `check_changed_line_mutation_coverage.py`,
covered by `tests/quality_gates/test_changed_line_mutation_coverage.py`).
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
3. **Cost = producer-at-closeout, consumer-reuses-or-skips (revised in impl —
   see P1).** P1 is resolved: the pre-push `run-quality.sh --read-only` run
   produces **no** reusable coverage JSON (run-quality runs pytest without
   coverage; `reports/mutation/test-coverage.json` is gitignored and written only <!-- reproduction-source -->
   by the mutation pipeline). So the original "reuse the coverage produced in the
   pre-push run" premise was false. The cost model is therefore split:
   - **Consumer (pre-push, this slice):** the wired gate **never** runs the slow
     probe here. It reuses coverage only when it exists AND is **fresh** for the
     current head (`--reuse-coverage --skip-if-no-coverage --require-fresh-coverage`),
     else it skips non-blocking. Cheap and safe by construction.
   - **Producer (closeout, next slice):** a dedicated closeout step runs the
     faithful probe (only when eligible pool files changed) and persists
     `reports/mutation/test-coverage.json` plus a `.head` marker for the consumer <!-- reproduction-source -->
     to trust. The coverage cost lives here, at the boundary the operator chose
     (Option A), not on every push.
   The subprocess-only false-positive edge stays a **deferred probe** (Deferred
   Decisions); the freshness guard already neutralises the broader *stale*-coverage
   false-positive class found in the wiring smoke (a stale JSON would otherwise
   block legitimate pushes).
4. **No threshold/budget relaxation.** Per `mutation-testing.md`, the durable fix
   is *covering the lines*, never lowering a floor. This spec is about detection
   *timing*, not scoring thresholds.

## Probe Questions (answer through the impl slice, not up front)

- **P1 — coverage-JSON source at pre-push. RESOLVED (impl).** The pre-push
  `run-quality.sh --read-only` path emits **no** reusable coverage JSON; pytest
  runs without coverage and `reports/mutation/test-coverage.json` is gitignored, <!-- reproduction-source -->
  written only by the mutation pipeline. → The gate must not rely on a pre-push
  coverage source: the **producer** (closeout, next slice) emits it; the
  **consumer** (this slice) reuses it only when fresh, else skips non-blocking.
  A second fact surfaced in the wiring smoke: reusing a **stale** coverage JSON
  flags recently-changed lines as uncovered (false positives) — answered by the
  `--require-fresh-coverage` `.head`-marker guard.
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
  changed-line *coverage*, not selection budget. **Partial resolution (#341,
  2026-06-09):** the *per-file-workload-cap* sub-case — a changed file dropped
  solely because its own covered-mutable-line count exceeds
  `max_executable_mutants_per_file` (a permanent capacity limit, e.g. the
  module-split `goal_artifact_closeout_loaders.py`/`goal_artifact_disposition_grammar.py`
  at 134/153 mutable lines vs the 80 budget) — is now reclassified from the
  blocking `selection_excluded_changed_files` bucket to the non-blocking advisory
  `changed_files_excluded_by_per_file_budget` bucket
  (`mutation_manifest_lib.split_per_file_budget_exclusions`). Its changed lines are
  still coverage-verified by the changed-line arm, which keeps blocking any
  uncovered changed line; the per-file budget is unchanged. Genuine
  selection-CONTENTION drops (cumulative budget / nodeid budget / no covering test)
  stay blocking and remain the deferred follow-up.
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

## Slice Status

### Slice 1 — consumer wiring (DELIVERED, this session)

The cheap, safe **consumer** half of Option A:

- **Reproducer guards** (`check_changed_line_mutation_coverage.py`):
  `--skip-if-no-coverage` (no coverage source → skip non-blocking, never the slow
  probe) and `--require-fresh-coverage` (a coverage JSON whose `.head` marker does
  not match the analyzed head is stale → skip non-blocking). Skip logic extracted
  to `_coverage_source_skip` (length-gate clean).
- **Wiring** (`run-quality.sh`): `queue_selected "check-changed-line-mutation-coverage"`
  over `git merge-base origin/main HEAD ..HEAD`, with
  `--reuse-coverage --skip-if-no-coverage --require-fresh-coverage` — never runs
  the slow probe in run-quality; non-blocking when no fresh coverage / no base.
- **Tests**: 5 new reproducer unit tests (skip-absent, skip-still-blocks,
  fresh-marker-absent/mismatch/match) + fixture stub
  (`QUALITY_PYTHON_STUBS`) + attention-state declaration
  (`attention-state-visibility.json`, state `skipped`).
- **Verified**: 12/12 reproducer tests; the wiring smoke over the real unpushed
  range safely **skips** (stale coverage, no `.head` marker) — proving the
  freshness guard neutralises the stale-coverage false positives it surfaced
  (it had flagged 3 changed files on the real range before the guard). AC-WIRE
  proven at reproducer level (renamed in Slice 2 to
  `test_require_fresh_coverage_fires_when_marker_matches_fingerprint`);
  AC-CLEAN is additionally enforced by the existing pre-push `git diff --quiet --
  charness-artifacts` hook check.

> **Superseded by Slice 2:** the freshness marker described here as the commit-SHA
> `.head` file is now the content-based `.fingerprint` marker — the SHA identity
> would have made the closeout-piggybacked producer's pre-commit stamp never match
> the consumer's post-commit check. See Slice 2 "Freshness identity changed".

### Slice 2 — producer (DELIVERED via lever A+B, 2026-06-07)

The cheap producer is wired. Lever A+B as decided:

- **Lever A — drop `dynamic_context`.** `run_test_coverage` gained a
  `dynamic_context` flag (default True for the faithful sampler path); the
  producer passes `dynamic_context=False`, which omits the per-test rcfile
  context + `--show-contexts` export. Per-test context was the **~1.34 GB** size
  driver; the changed-line verdict only needs executed-vs-missing lines.
  **Subprocess capture (`COVERAGE_PROCESS_START`) is retained**, so plain `--cov`
  gains no new subprocess blind spot — strictly better than the assumed plain
  `--cov`, while still small.
- **Lever B — piggyback, no double-run.** `run_slice_closeout.py
  --produce-mutation-coverage` (requires `--verification-lock`) instruments the
  **closeout broad pytest itself** under plain coverage (one run), then exports
  `reports/mutation/test-coverage.json` and stamps the freshness marker. New <!-- reproduction-source -->
  module `scripts/mutation_coverage_producer.py` + executor routing
  (`broad_pytest_producer` bypasses proof-reuse so the producing run always
  executes). `reports/mutation/` is gitignored → AC-CLEAN preserved.

**Freshness identity changed from commit-SHA → content fingerprint (supersedes
slice 1's `.head` marker).** Closeout runs **pre-commit** (verify → commit), so a
closeout-piggybacked producer stamps the *parent* SHA while the pre-push consumer
checks the *committed tip* SHA — with the slice-1 SHA marker the gate would
silently skip on **every** push (a permanent false-negative, defeating the seam
fix). The marker is now `<coverage-json>.fingerprint` = a content hash of the
changed eligible pool files over `base→worktree`
(`mutation_changed_files_lib.changed_pool_fingerprint`), which is identical at the
producer's pre-commit run and the consumer's post-commit (clean-tree) check of the
same code. Consumer (`--require-fresh-coverage`) recomputes and compares; producer
(`--write-fresh-marker` / the closeout producer) stamps it. Content-based is also
more correct than SHA: a no-op recommit/rebase that does not touch the pool no
longer needlessly invalidates fresh coverage. Operator-confirmed direction
("우리 목적에 맞으려면 뭐가 최선?" → content fingerprint, 2026-06-07).

**Verification strategy = via the push (operator):** the expensive faithful-probe
local run is NOT re-run; the producer slice is proven by the real push — run the
producer on the committed tip (so the marker matches the pushed HEAD), then the
pre-push consumer gate fires against fresh, matching coverage, with the scheduled
cron as backstop. Accepted trade-off: a false positive blocks the push (safe — fix
and retry), a false negative is caught by the cron post-merge (no worse than
today). Bundle the push + release.

The cosmic-ray test set (full `tests`) and the closeout broad set
(`tests/quality_gates tests/control_plane tests/test_*.py`) differ: a changed line
covered only by an excluded test (e.g. `tests/charness_cli`) reads as uncovered in
the piggybacked coverage → a possible false positive. This is the accepted
"false-positive blocks the push (fix+retry)" trade-off, not a silent gap. The
subprocess-only escalation engine stays deferred (Deferred Decisions).

**Tests:** producer + executor routing + guard + fingerprint freshness
(`tests/quality_gates/test_mutation_coverage_producer.py`,
`test_changed_line_mutation_coverage.py`). A manual fallback remains:
`check_changed_line_mutation_coverage.py --write-fresh-marker` runs a plain
(no-`dynamic_context`) full-suite probe + stamps the same fingerprint marker.

**Portability classification (closeout checkpoint):** the producer module + wiring
are **host-local** (charness `run_slice_closeout.py` / broad-pytest shape /
`reports/mutation/` paths). The transferable *doctrine* (content-fingerprint
freshness, drop-`dynamic_context` producer-cost lesson) belongs in
`skills/public/quality/references/mutation-testing.md` — that promotion is the
separate handoff "Skill portability" follow-up, not this slice.

### Skill portability (follow-up — surfaced by operator 2026-06-07)

This gate is currently a **charness-repo-local** capability: the logic lives in
repo-root `scripts/check_changed_line_mutation_coverage.py` (mirrored into the
plugin export but NOT presented as a `quality`-skill capability), and the wiring
is charness-host-specific (`run-quality.sh` / pre-push). Per "keep the harness
portable", the **lessons** should benefit any repo adopting the `quality` skill:
- **Doctrine (cheap, high-value):** add to
  `skills/public/quality/references/mutation-testing.md` the pre-merge
  changed-line-coverage teeth pattern, the **stale-coverage freshness-guard**
  rule (never trust coverage not stamped for the analyzed head), and the
  **producer-cost lesson** (faithful full-suite `dynamic_context` coverage is the
  wrong cost model for routine teeth — drop `dynamic_context` / piggyback).
- **Capability (larger):** offer the gate as a `quality`-skill script + an adapter
  wiring contract so adopting repos can enable it, instead of only shipping a
  repo-root script. This needs the mutation libs (`mutation_changed_files_lib`,
  `mutation_sampling_lib`, `sample_mutation_files`) reachable from the skill —
  a packaging decision, not just a move.
Route through `create-skill`/`quality` next session; the doctrine update is the
minimum that lets other repos benefit.

**Explicitly out of all slices** (named follow-ups): the subprocess-only
false-positive escalation engine (Deferred Decisions) and the selection-budget
follow-up.

### Slice 3 — recurrence reduction: surface the silent skip (#335, 2026-06-08)

**Root cause of the recurrence (debug
`2026-06-08-issue-335-changed-line-mutation-recurrence.md`).** The seam recurs
because the gate's protection is *silently absent* exactly when it matters. The
cheap consumer (`run-quality.sh` pre-push, `--skip-if-no-coverage
--require-fresh-coverage`) **skips non-blocking (exit 0)** when coverage was not
freshly produced — and that skip path is only reached when eligible mutation-pool
files actually changed in the range (the empty case returns earlier). So an
unverified skip reads *identically* to a clean pass: the author's pre-push
attestation goes green, uncovered changed lines land on `main`, and only the
scheduled cron (base = the previous run's head, so it accumulates everything since)
flags them post-merge and auto-files. #335 was the #332 lines; the same run also
had 85 uncovered v0.28.0 lines queued behind it — the class, not the instance.

**The mechanism (smallest, additive, behavior-preserving).** Convert the silent
skip into a LOUD author-time obligation. `check_changed_line_mutation_coverage.py`
now, whenever it skips with changed eligible files present, writes a non-blocking
stderr `WARNING (changed-line mutation gate): … N eligible mutation-pool file(s)
changed but their changed lines were NOT verified for coverage … Run
run_slice_closeout.py --produce-mutation-coverage --verification-lock …` and
records `coverage_not_verified: true` + `changed_eligible_files` in the JSON. The
verdict (exit 0) is unchanged — no gate's verdict changes on existing code — so
this mirrors the v0.28.0 author-time *surfacing* posture, not a new hard gate.
It directly removes the false-confidence (`skipped` indistinguishable from
`passed`) that let the debt accumulate, parallel to the existing
`false_green_warning` tripwire on the same script.

**Why not a new hard gate / auto-produce.** Blocking the cheap pre-push tier when
coverage is absent would change its verdict (every script-touching push without a
slow coverage run would fail) and is the "new hard gate" the goal forbids;
auto-producing coverage in every closeout is a larger cost/scope change. Both are
**deferred follow-ups** — the surfacing is the minimum that makes the recurrence
driver visible. Doctrine carried to
`skills/public/quality/references/mutation-testing.md` so adopting repos inherit
the "an unverified skip must not read as a pass" rule.
