# Achieve Goal: Mutation-gate health — cover #267 host-hook changed-line gap, honest slice closeouts (#266), verify/stage cluster closure

Status: active
Created: 2026-05-31
Activation: `/goal @charness-artifacts/goals/2026-05-31-mutation-gate-health.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation — slices execute once the user runs `/goal`;
inert until then.

## Goal

Restore and protect the scheduled mutation gate on `main`, and make this goal's
own slice closeouts honest. **The plan-critique corrected the original premise**
(B1): the scheduled CI resolves the changed-line base as the *head of the most
recent prior completed run* (`.github/workflows/mutation-tests.yml` ~L141).
During this goal, slice 1 advanced the unpushed HEAD beyond the original
`dad2d01` premise, so the current next run scopes **`6d85aec..0707515`**. That
range contains `scripts/run_cosmic_ray_mutation.py`,
`scripts/run_slice_closeout.py`, and `scripts/staged_commit_gate_plan.py`, and
does **not** contain the two host-hook files #267 originally flagged — they
leave next-run scope on their own.

1. **#266 (slice 1, folded in first):** eliminate the divergence between
   `run_slice_closeout.py` (the "verify before commit" aggregate) and the
   `.githooks/pre-commit` gate set via **one shared staged-path→command
   selection both consume**, so a green aggregate guarantees a green commit.
   Without it, every slice below that stages `.py`/test changes re-hits the
   cluster run's false-green fix-retry waste.
2. **Next-run gate health (slice 2):** verify the *actual* current next-run
   range `6d85aec..0707515` has no uncovered changed lines across its changed
   mutation-pool files; cover any gap so this goal's own fixes do not become the
   next "regression on main." This is the load-bearing recurrence-prevention
   work.
3. **#267 host-hook coverage debt (slice 3):** close the genuine uncovered
   changed-line gap in `scripts/host_hook_codex_toml_lib.py` /
   `scripts/host_hook_find_skills.py` that #267 flagged (B2: the gate uses real
   `coverage.py` missing-lines, so the gap is genuine, not a selection
   artifact). These files leave next-run scope, so this is honest debt closure
   (prevents re-block when they are next touched), **not** the next-run fix.
4. **Cluster closure (After):** verify the unpushed cluster fixes (#262, #219)
   are intact and stage their issue closure; leave #261 open (residual triage
   tracked by #265).

Context: `origin/main` is `6d85aec`; HEAD is 9 unpushed commits ahead
(`0707515`) after slices 1-2.

## Non-Goals

- Not #265 (exhaustive cosmic-ray triage of the #261 coordination-cues
  survivors) — separate ranked chunk; this goal does not re-run the trio.
- Not a full cosmic-ray mutation run (user chose deterministic + targeted-kill
  proof).
- Not re-doing the #262/#261/#219 cluster fixes — they are committed; this goal
  verifies, it does not redo them.
- Not a release: no plugin version bump or install-manifest change.
- No push and no out-of-band `gh` close — `achieve` does not push; closure is
  staged in the commit body for the maintainer.

## Boundaries

- **In scope (#266):** `scripts/run_slice_closeout.py`, `.githooks/pre-commit`
  (**B3: must be refactored to consume the shared selection** so there is one
  implementation, not a parallel replay), `scripts/surfaces_lib.py` /
  `.agents/surfaces.json` (the `repo-python` surface currently omits both
  `check_python_lengths` and `validate_attention_state_visibility`), and the new
  shared staged-path→`(label, argv)` selection module; their tests under
  `tests/`.
- **In scope (slice 2 — next-run health):** `scripts/run_cosmic_ray_mutation.py`,
  `scripts/run_slice_closeout.py`, `scripts/staged_commit_gate_plan.py` (the
  changed mutation-pool files in the real current next-run range
  `6d85aec..0707515`) and any tests needed to cover their uncovered changed
  lines.
- **In scope (#267 debt, slice 3):** `scripts/host_hook_codex_toml_lib.py`,
  `scripts/host_hook_find_skills.py` (`axis: host` — Codex host-adapter
  surfaces; keep host-specific behavior in the hook, no host-hardcoded test
  assumptions), their tests (`tests/test_find_skills_host_hook_reconcile.py` and
  siblings), and the generated `plugins/charness/scripts/` mirror (synced via
  the mirror-drift gate, never hand-edited).
- **Read-only / verify:** `scripts/check_changed_line_mutation_coverage.py` and
  `scripts/mutation_sampling_lib.py` (the gate + coverage mechanism),
  `.github/workflows/mutation-tests.yml` (base resolution), the cluster source
  touched by #262/#219.
- Portable per implementation-discipline: host-specific behavior stays in
  adapters/hooks; no new host assumption baked into shared scripts.
- Stop conditions: name uncovered changed lines on first discovery from the gate
  output over the *exact* range stated per slice — do not guess, and do not
  scope tests to the whole `7a4cbfe` diff (B2). Stop and ask if the #266 design
  turns out to require changing the pre-commit hook's gate *semantics* rather
  than sharing its selection.

## User Acceptance

- The **actual current next-scheduled-run range `6d85aec..0707515`** has no
  uncovered changed lines when the changed-line gate is run locally over that
  exact range (`scripts/run_cosmic_ray_mutation.py`,
  `scripts/run_slice_closeout.py`, `scripts/staged_commit_gate_plan.py`) — so the
  maintainer's push does not produce the next "regression on main." (Corrected
  from the original draft's false claim about the host-hook files, which leave
  next-run scope.)
- `run_slice_closeout.py --predict-commit` (or the aligned aggregate) reproduces
  the **exact** pre-commit gate verdict — a green run guarantees a green commit;
  the two gates the cluster missed (`check_python_lengths` per-function and
  `validate_attention_state_visibility`) are in its set, run with the hook's
  staged-path argv (not whole-repo scope), and the hook and aggregate share one
  selection implementation.
- The genuine host-hook coverage gap #267 flagged (verified over
  `9ee91ff..HEAD`; production host-hook diff is identical to
  `9ee91ff..dad2d01`) is
  closed with scoped tests, each mutation-proven; this prevents re-block when
  those files are next touched.
- #267 is staged to close on the closeout commit; #262 and #219 staged to close;
  #261 left open (→ #265).
- No regression: full `pytest -m 'not release_only'` green; cheap commit-time
  gates green on every commit.

## Agent Verification Plan

- **Low-cost (per slice, deterministic):**
  - #266 (slice 1): a test that a deliberately length-/attention-violating
    staged change is REJECTED by the predict-commit path (RED) and a clean
    change passes (GREEN); ruff + `check_python_lengths` + targeted pytest on
    changed files. Assert the hook and aggregate resolve the **same** command
    plan for a given staged set (one implementation).
  - Slice 2 (next-run health): run the changed-line gate over the **real current
    next-run range** `--base-sha 6d85aec --head-sha HEAD` (HEAD=`0707515`) with
    **freshly generated coverage** (not the stale
    `reports/mutation/test-coverage.json`, B2); expect 0 blocking for
    `scripts/run_cosmic_ray_mutation.py`, `scripts/run_slice_closeout.py`, and
    `scripts/staged_commit_gate_plan.py`. If any changed line is uncovered,
    cover + mutation-prove it.
  - Slice 3 (#267 debt): get the precise per-file `changed_and_missing` line
    list via the gate over `--base-sha 9ee91ff --head-sha HEAD` (the current
    range where the host-hook files show as changed; production host-hook diff
    is identical to `9ee91ff..dad2d01`), then write tests targeting only those
    lines. Hand-verify each new test KILLS its target mutant (write mutant →
    RED; revert → GREEN).
  - Expected proof cost: minutes (no cosmic-ray exec). Expected
    test-duplication pressure: **MODERATE** on slice 3 — scope tests to the
    gate-reported missing lines, not the whole `7a4cbfe` diff, to avoid
    overlapping the 194-line `test_find_skills_host_hook_reconcile.py`; sample
    the duplicate/length gate when adding them.
- **High-confidence (bundle / final):**
  - Full pre-commit gate set on the staged closeout (via the aligned aggregate /
    `--predict-commit`).
  - Full `pytest -m 'not release_only'`.
  - Plugin-mirror sync validated (`check_staged_mirror_drift` /
    `validate_packaging`).
  - Cluster-targeted tests (`validate_rca_ledger`, coordination-cues floors)
    still green (no regression of the #219/#261/#262 work).
- **External / live (NOT RUN — named skipped):** the scheduled
  `workflow_dispatch`/cron mutation gate on `origin/main` requires pushing;
  `achieve` does not push. Live-green proof is the maintainer's post-push step
  (see User Verification Instructions).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #266: introduce a shared staged-path→`(label, argv)` selection module; give `run_slice_closeout` a `--predict-commit` mode that uses it, and refactor `.githooks/pre-commit` to consume the same module (B3) | Folded in first (user): slices 2-3 stage `.py`/test changes that fire the gates the cluster run missed; honest closeout removes the false-green retry tax for the rest of this goal | Synthetic length/attention violation caught pre-commit by predict-commit (RED→fix→GREEN); hook + aggregate provably share one selection (same command plan for a staged set); targeted tests green | completed |
| 2 | Next-run gate health: run the changed-line gate over the real current next-run range `6d85aec..0707515` (fresh coverage); confirm/cover `scripts/run_cosmic_ray_mutation.py`, `scripts/run_slice_closeout.py`, and `scripts/staged_commit_gate_plan.py` | The load-bearing recurrence-prevention work (B1): this is what the next scheduled run actually scopes after slice 1 advanced HEAD; this goal's own new Python surface is also part of the risk | Gate 0-blocking over `6d85aec..0707515`; any uncovered changed line covered + mutation-proven | completed |
| 3 | #267 debt: enumerate the genuine `changed_and_missing` lines over `9ee91ff..HEAD` for the two host-hook files, cover only those, mutation-prove | Honest closure of the gap #267 flagged so it cannot re-block when these files are next touched (they are out of next-run scope, so this is debt, not the next-run fix) | Gate 0-blocking for both files over `9ee91ff..HEAD`; each new test kills its target mutant; no duplication blowup vs the reconcile test | completed |

## Slice Log

### Slice 1: Slice 1 (#266 shared staged commit gate)

- Objective: Eliminate divergence between .githooks/pre-commit and run_slice_closeout by routing staged-path command selection through one shared planner and exposing run_slice_closeout --predict-commit.
- Why this approach: The rest of this goal stages Python/test changes; a green aggregate must predict the commit hook instead of missing check_python_lengths and validate_attention_state_visibility.
- Commits: `86a905d`
- What changed: Added scripts/staged_commit_gate_plan.py and synced plugins/charness/scripts/staged_commit_gate_plan.py; refactored .githooks/pre-commit to delegate to run_slice_closeout --predict-commit; added predict-commit execution in run_slice_closeout; added repo-python surface commands for check_python_lengths and validate_attention_state_visibility; added tests for planner parity, length failure, attention failure, and clean staged Python.
- Alternatives rejected:
- Targeted verification: PASS: pytest -q tests/quality_gates/test_staged_commit_gate_plan.py (5 passed); PASS: real staged python3 scripts/run_slice_closeout.py --repo-root . --predict-commit --json; PASS: python3 scripts/run_slice_closeout.py --repo-root . (packaging, surfaces, integrations, maintainer setup, full ruff, full length gate, attention visibility, broad pytest, agent-browser hygiene).
- Test duplication pressure: Added one focused 119-line quality gate test file. check_python_lengths passes; run_slice_closeout.py is advisory-near-limit at 465/480 and should be trimmed in a later structural cleanup, not expanded further.
- Critique: bounded fresh-eye review executed (`parent-delegated`): no blockers; proof aligned. Follow-up risk addressed in-session by using one captured staged path list for both the plan and payload; remaining non-blocking import-risk note accepted (hook enters through `run_slice_closeout.py`, so future import-time closeout helper failures could affect commit).
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Slice 2 (current next-run changed-line health)

- Objective: Verify and cover the actual current next scheduled mutation range after slice-1 commits: 6d85aec..0707515.
- Why this approach: Slice 1 changed the unpushed head, so current state makes the next scheduled range include run_cosmic_ray_mutation.py, run_slice_closeout.py, and staged_commit_gate_plan.py, not only the old dad2d01 range.
- Commits: `a49db90`, `0707515`
- What changed: Added focused tests for run_cosmic_ray_mutation no-TOML-parser and timeout+dump-failure branches; expanded staged_commit_gate_plan tests for serialization, git error reporting, domain and markdown triggers, CLI JSON/text output, non-json plan-only output, empty-plan no-op, failure output propagation, and success output.
- Alternatives rejected:
- Targeted verification: PASS: ruff check for touched files; PASS: pytest -q tests/quality_gates/test_staged_commit_gate_plan.py tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py (31 passed); PASS: final fresh python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 6d85aec --head-sha HEAD after full coverage pytest (1905 passed, 4 skipped, 57 deselected) with blocking=[] and changed_pool_files=[scripts/run_cosmic_ray_mutation.py, scripts/run_slice_closeout.py, scripts/staged_commit_gate_plan.py].
- Test duplication pressure: Expanded two existing focused quality-gate test files rather than adding a new broad fixture; check_python_lengths passed for touched files.
- Critique: bounded fresh-eye review executed (`parent-delegated`): initial blockers were artifact-only (ahead count and missing commit IDs); fixed before commit. Reviewer independently confirmed reframing from `dad2d01` to current HEAD `0707515` is correct and proof aligns with acceptance.
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Slice 3 (#267 host-hook changed-line debt)

- Objective: Close the genuine host-hook changed-line coverage debt flagged by #267 over the host-hook range.
- Why this approach: The host-hook files are outside the current next-run scope, but the uncovered changed lines are real debt and would re-block when those files are next touched.
- Commits: `a77f49b`
- What changed: Added focused tests for the two gate-reported host-hook lines: Codex TOML matcher returns None for a foreign command with no matching script identity, and Codex JSON find-skills uninstall removes legacy TOML markers from the default config.toml.
- Alternatives rejected:
- Targeted verification: PASS: pytest -q tests/test_find_skills_host_hook_reconcile.py (7 passed); PASS: ruff check tests/test_find_skills_host_hook_reconcile.py; PASS: fresh python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 9ee91ff --head-sha HEAD after full coverage pytest (1907 passed, 4 skipped, 57 deselected) with blocking=[] for host-hook range. Targeted kill proof: mutating host_hook_codex_toml_lib._matching_existing_command final return None -> command made test_codex_toml_matching_existing_command_returns_none_for_foreign_command fail; mutating uninstall_find_skills_codex_hook codex-json legacy cleanup path from config.toml to hooks.json made test_find_skills_codex_json_uninstall_cleans_legacy_toml_markers fail.
- Test duplication pressure: Expanded existing reconcile test file by two scoped tests; no new broad fixture file. check_python_lengths passed for tests/test_find_skills_host_hook_reconcile.py.
- Critique: bounded fresh-eye review executed (`parent-delegated`): no code/test blockers; reviewer confirmed the two new tests target the exact reported lines and proof aligns with acceptance. Artifact hygiene risks (stale `dad2d01` wording, blank commits, pending critique) fixed before amend.
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Off-Goal Findings

## Context Sources

- Issue #267 (the live regression): blocking signal = uncovered changed lines in
  `scripts/host_hook_codex_toml_lib.py` and `scripts/host_hook_find_skills.py`;
  failing range `9ee91ff..6d85aec`; introduced by `7a4cbfe "Clean up duplicate
  Codex find-skills hooks"`. Score (94.2%) passed; the block is changed-line
  coverage, not the score.
- Issue #266 (fold-in): `run_slice_closeout` verify set ⊄ pre-commit gate set;
  cluster slice 1 passed the aggregate, then the commit was rejected by
  `check-python-lengths` (per-function 102>100) and
  `validate_attention_state_visibility`.
- Issues #262 (cosmic-ray module-path restore on exit/interrupt) and #219
  (`validate_rca_ledger` survivors): cluster fixes committed locally
  (`6030306`, `d8e310f`), unpushed; verify + stage closure. #261 stays open
  (→ #265).
- Prior goals/retros:
  `charness-artifacts/goals/2026-05-31-262-261-219-mutation-cluster.md`,
  `charness-artifacts/goals/2026-05-31-260-mutation-test-regression-on-main.md`,
  `charness-artifacts/retro/2026-05-31-262-261-219-mutation-cluster.md`,
  `charness-artifacts/retro/recent-lessons.md`.
- CI run referenced by #267: GitHub Actions run 26703573779 (a CI log, not a
  knowledge source to import).

## Interview Decisions

- **#266 inclusion** — family {workaround-only (manual full-gate per commit) |
  fold the fix in}. Chosen: **fold in as slice 1** (user). Rejected
  workaround-only: it leaves the false-green divergence live for every future
  goal. `single-point` — the commit gate set is one repo-owned config, not a
  host-varying axis.
- **#266 design direction** — family {make the aggregate a full superset | add a
  `--predict-commit` affordance}. Leaning **`--predict-commit` sharing one
  gate-selection source of truth** (lowest re-divergence risk; does not bloat
  the default aggregate). Confirm in slice 1 after reading `surfaces_lib.py` and
  the hook. `single-point` (repo gate config).
- **Proof depth** — family {deterministic + targeted kill | + full scoped
  cosmic-ray}. Chosen: **deterministic + targeted kill** (user). Rejected the
  cosmic-ray run as disproportionate for a changed-line coverage gap.
  `single-point` (per-goal verification choice).
- **#265 scope** — excluded (handoff ranked it a separate chunk; the chunk-1-4
  selection excludes it).
- **Host axis** — `scripts/host_hook_*` are `axis: host` (Codex host-adapter
  surfaces); the fix and tests must not hardcode a single-host assumption into
  shared scripts.
- **Push/closeout boundary** — `single-point`: `achieve` does not push; closure
  is staged in the commit body and live-green is the maintainer's post-push
  check.

## Plan Critique Findings

Reviewer provenance: bounded fresh-eye plan critic (general-purpose subagent,
read-only, 29 tool uses), run during the Before-phase. Verdict:
**sound-with-the-listed-blocker-fixes; B1 load-bearing**. The parent
independently re-verified B1's range facts before folding.

**Blockers folded into the plan:**

- **B1 (load-bearing) — original premise false; reframed Goal + User Acceptance
  + Slice Plan.** The scheduled CI base = head of the most recent prior
  *completed* run (`.github/workflows/mutation-tests.yml` ~L141), so the next run
  after pushing `dad2d01` scopes `6d85aec..dad2d01`, which contains **only**
  `scripts/run_cosmic_ray_mutation.py` (the #262 +160-line growth) and **not**
  the host-hook files. Re-verified: `git diff --name-only 6d85aec..dad2d01 --
  'scripts/*.py'` → only `run_cosmic_ray_mutation.py`. Folded: slice 2 now
  verifies the real next-run range; slice 3 re-justified as host-hook *debt*
  closure; the false "host-hook block clears next run" acceptance was removed.
- **B3 — #266 design tightened.** A `--predict-commit` that re-derives the
  hook's selection in Python is a second implementation that re-diverges; and
  "align the aggregate to a superset" cannot reproduce the hook's staged-only
  `--paths` semantics (it would over-report on pre-existing over-limit files the
  commit would not touch). Evidence: `.githooks/pre-commit:25` runs
  `check_python_lengths --paths "$STAGED_PY"`, `run-quality.sh:415` runs it with
  `--require-git-file-listing` (whole-repo), and `.agents/surfaces.json`
  `repo-python` omits both gates. Folded: slice 1 now requires a shared
  staged-path→argv module that **`.githooks/pre-commit` is refactored to
  consume** (one implementation).
- **B2 — scope tests to gate-reported lines, fresh coverage.** The gate uses
  real `coverage.py` missing-lines (`mutation_sampling_lib.py:190`), so the gap
  is genuine, not a selection artifact; most of `7a4cbfe`'s diff is already
  covered by the 194-line reconcile test — the residual is specific branches
  (likely `uninstall_find_skills_codex_hook` codex-json,
  `host_hook_find_skills.py:~118-126`). Folded: slice 3 enumerates
  `changed_and_missing` with fresh coverage and targets only those lines.

**Over-worries (raised, not folded):**

- Stale-premise (did cluster commits change the host-hook range?) — refuted; the
  `9ee91ff..6d85aec` line set is intact at HEAD, but that is irrelevant given B1.
- Slice ordering — #266-first confirmed correct: slice 2/3 commits stage
  `scripts/*.py`+tests that the hook routes through `check_python_lengths
  --paths` and `validate_attention_state_visibility`, so they do fire the gates
  #266 fixes.
- Length-gate panic / host-axis over-anchoring — both low risk; the existing
  fixtures (`fake_home`/`fake_repo`) satisfy the no-host-hardcoding boundary.

## Final Verification

## User Verification Instructions

## Auto-Retro

## Coordination Cues

Phase→skill routing defers to `find-skills` (`--recommend-for-task` /
`--recommendation-role <runtime|validation> --next-skill-id <skill>`); no inline
map is baked here. Expected boundaries: `issue` for staging #267/#262/#219
closure; `quality` for the final gate cadence; `critique` for slice-level and
closeout fresh-eye reviews; `retro` at closeout. `debug` root-cause is already
done inline for #267/#266 (cause named in Context Sources), so no separate debug
slice is planned.

- Gather: n/a — all context is in-repo (issues #267/#266/#262/#219, prior
  goals/retros); the only external URL is a CI run log, not a knowledge source
  to import via `gather`.
- Release: n/a — no version bump or install-manifest edit; the `plugins/` mirror
  is a generated sync (mirror-drift gate), not a release surface.
