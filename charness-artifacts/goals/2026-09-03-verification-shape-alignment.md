# Achieve Goal: Remove verification-shape mismatches: hosted mutation, standing release evidence, one layout resolver, ledger budget, awiki echo

Created: 2026-09-03
Planning record: mutable until Goal Binding; the binding freezes these exact bytes.

## Goal
Make every verification channel this repo reads report the same truth in the same shape. The 2026-09-02 and 2026-09-03 retros recorded the `verification-shape-mismatch` class twice in the RCA ledger; five open items from the #765 handoff are instances of it. Concretely: the hosted mutation workflow (#764) runs its coverage baseline green on the post-#770 tree, or the failing tests are named and fixed in the shape CI uses; the `release_only` lane is part of standing evidence so a release-only regression cannot hide for days; the four flat-or-packaged script lookups become one resolver beside `scripts/core/repo_layout.py`; the lesson ledger admits the three recurrence classes hit again this session inside its budget; and the `docs-graph-awiki` phase stops printing a FAIL that no aggregate consumes. Success is a wrong green or a false red losing its path, never a count.

## Starting Truth (2026-09-03 read)

| Surface | Observation |
| --- | --- |
| #764 hosted mutation | Only open issue. Six scheduled runs since 2026-08-31 all failed at `Select mutation sample`; the sampler's coverage-baseline pytest fails before any mutant runs, so `Status: UNMEASURED` every time. The failing set differs per run (two tests on `f8b9cd8af`, 38 on `f0bee64f3`, five on `474b9f514`); the latest run's five are timing-sensitive drain and retry tests (`test_cli_skill_surface.py:709`, `:819` assert one attempt observed against two expected). The last run predates the #770 packaging moves; the workflow already points at `scripts/plugin_export/sync_root_plugin_manifests.py`. The workflow is `schedule` + `workflow_dispatch` only; a dispatch run cannot report recovery (#358 comment in the workflow). |
| release lane | `release_only` and `slow_corpus` are deselected by `run_standing_pytest.py` unless `--include-release-only`. The pre-push hook runs the standing lane. #768's three release-only regressions stayed hidden four days and surfaced only when #772 ran `--release`. Release lane runtime is about 298 s per `.charness/quality/runtime-signals.json`. |
| layout lookups | Three independent flat-or-packaged resolvers written in the #770 session: `scripts/core/scaffold_artifact_lib.py::_repo_script` (glob), `tests/quality_gates/seeding_support.py::_packaged_script` and `_seed_path` (rglob), `skills/public/quality/scripts/public_spec_adapter_policy.py::load_repo_script_module` (glob). The retro also named `scripts/staged_commit_gate_plan_helpers.py::present_gate`, but on read it only chooses between `tools/` and `scripts/` for an already-relative path and does no layout search; it is a consumer candidate, not a duplicate. `scripts/core/repo_layout.py` owns tree-root paths and has no script resolver. The #770 rename sweep was an ad hoc regex; no sweep tool exists in the tree. |
| lesson ledger | 49 active of a 50 budget. 15 active lessons carry `score_total 0, score_count 0`; six of those predate 2026-08-17. Three recurrence classes from the 2026-08-18 to 2026-08-21 retros (`wrong-path-is-premise-failure`, `probe-stimulus-from-model-not-source`, `parallel-coverage-runtime-collision`) recurred in the #770 session and are absent from the ledger. |
| docs-graph-awiki | `scripts/gates/check_docs_graph.py` gates on named metrics, never on awiki's exit code, but `_run_awiki` goes through `run_monitored_phase`, which prints `FAIL [docs-graph-awiki]` whenever awiki exits 1 on lint findings. The `docs-graph` gate is `lane: label-only`; the FAIL line reaches the operator and no aggregate. |

## Non-Goals

- Redesigning the mutation sampler, its seed rotation, or the recovery-candidate contract from #358. #764 closes through the existing distinct-observer path once a scheduled run is green.
- Making `release_only` tests part of the standing pytest selection. The marker stays; what changes is when the release lane runs.
- Moving any further files under `scripts/`. The resolver serves the layout that exists; it does not start another migration.
- Raising `active_lesson_budget` above 50. The budget is the forcing function; admission happens by graduating or archiving.
- A hosted second observer for `release_only` (a `quality-core.yml` job on push to main). The clean-clone push lane is the observer this goal installs; a hosted one is a later decision.
- Making a rename sweep consume the resolver. No sweep tool exists in the tree; the #770 sweep was ad hoc. The resolver is the thing a future sweep would call; building that sweep is not this goal.
- Changing what `check_docs_graph.py` measures or its declared bars.
- Any AGENTS.md or CLAUDE.md edit.

## Boundaries

- **Verify in the shape production uses** (lesson `verification-shape-mismatch`). The #764 slice reproduces the baseline the way the workflow runs it: fresh clone, mirror materialized, `node_modules/.bin` on PATH, `CHARNESS_REQUIRE_MARKDOWNLINT=1`, the sampler's own pytest command. A local `pytest` green is a locate, not a claim.
- **Skipped is not passed** (lesson `skipped-is-not-passed`). Every lane read in this goal states its skip list; a timing-sensitive test is fixed or given a declared reason, never quietly deselected from the baseline.
- **Provider mutation only through the Goal Run and issue workflows.** #764 is closed by the recovery observer path, not by `gh issue close`; lesson ledger lifecycle events go through `record_lesson_lifecycle.py`, never by editing `lesson-ledger.json`.
- **The resolver replaces, it does not add.** Each of the four lookups is deleted when its call sites move; a fifth lookup surviving the slice is a failed slice.
- **The pre-push hook change is tested in a clean clone before it lands**, the way #768's closeout was pushed; the hook reads the parent working tree and lies otherwise.
- **A wall-clock-dependent test must not exist** (operator, 2026-09-03). Its existence is the smell, not its flakiness. Slice 4 does not retry, widen a tolerance, or deselect; it makes the claim deterministic or removes the test, the census covers all of `tests/`, and a standing form check refuses the next one.
- **The awiki fix is local to `check_docs_graph.py`.** `run_monitored_phase` keeps echoing child exit codes for every other phase and `subprocess_guard.py` is not in the slice's scope; `_run_awiki` either passes its own `stream` and renders the lifecycle line from the gate's verdict, or uses `run_process` with the same timeout and emits its own line. A diff touching `subprocess_guard.py` fails the slice.
- **The Goal Run parent is a new issue.** #764 stays the issue slice 4 and slice 6 close; it is not the parent.
- **Lesson graduation and archive are settled jointly, lesson by lesson.** The agent drafts the disposition and the docs edit; the operator and agent discuss each one; nothing is applied by rule, by commit inspection alone, or by automation. The settled reason per lesson is recorded before the event and the docs commit.

## User Acceptance

- The most recent scheduled mutation run on a tree at or after slice 4 has `Select mutation sample: success`; if it is green, #764 is closed through the distinct-observer path, and if not, its failing set is recorded as the next work rather than the goal claiming #764.
- A release-only regression cannot cross a push unnoticed: the pre-push clean-clone procedure runs `run-quality.sh --release` on every push, and `docs/development.md` names it with the measured runtime.
- No test in `tests/` claims a wall-clock outcome; the census list is recorded, every entry is rewritten or deleted, and a form check refuses a seeded new one.
- The ledger has a `graduate` action, and at least one score-0 lesson has been compressed into its owning `docs/` page with the lifecycle event pointing at that commit.
- No `glob`/`rglob` search for a script name under `scripts/` exists outside the resolver module (the form check is the instrument, not a single grep); the three named functions no longer exist; the flat and packaged cases each have a test; the `check-export-safe-imports` and `check-export-self-sufficiency` gates are green.
- `render_lesson_selection_preview.py` shows the three recurred classes as active lessons and the active count at or below 50, with each archive recorded as a lifecycle event.
- A full read-only lane on a tree whose docs graph has lint findings prints no `FAIL [docs-graph-awiki]` line; the gate's own verdict is unchanged.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/gates_support/run_standing_pytest.py --repo-root .` green with the skip list read after every slice.
- `python3 scripts/lessons/check_lesson_ledger.py --repo-root .` and the selection-index `--check` green after the ledger slice.
- Resolver unit tests: flat layout, packaged layout, missing script, and a seeded duplicate lookup refused by a form check.
- Seeded lint finding in a docs fixture: `check_docs_graph.py` still reports the named metric and prints no phase FAIL line.

### High-Confidence Checks

- Sampler baseline reproduced locally in the CI shape (fresh clone, mirror, PATH, env flag) on the current tree, before and after the fix; the before-run reproduces at least one of the five 2026-09-02 failures or the slice records that it could not and says why.
- `./scripts/run-quality.sh --full --read-only` green in a clean clone before each push.
- `./scripts/run-quality.sh --release` green in a clean clone once the hook change lands, and the hook itself refuses a seeded release-only failure.

### External or Live Proof

- One scheduled run of `mutation-tests.yml` on the pushed tree with `Select mutation sample: success` and a mutation result, read from GitHub by `verify-closeout` or the run URL, not asserted from the local baseline.
- `/goal #<parent>` pickup `ok: true` after the ledger slice, showing the bounded ledger preview with the three re-admitted classes.

## Slice Plan

Ordered smallest-first so the runner's output is trustworthy before the larger reads depend on it, then the resolver before any lane relies on script paths, then the two evidence-cadence items, then the ledger, then closeout.

| Slice | Objective | Why Now | Dependencies |
| --- | --- | --- | --- |
| 1 awiki-phase-echo | Stop `run_monitored_phase` (or `_run_awiki`) from printing `FAIL [docs-graph-awiki]` for awiki's lint exit 1 while keeping NOT-RUN on timeout; seeded-finding test. | Smallest item; every later lane read stops carrying a false red. | none |
| 2 layout-resolver | Add a script resolver beside `scripts/core/repo_layout.py` answering flat and packaged locations; fold the three lookups onto it and delete them; `present_gate` calls it for existence; form check refusing a new `glob`/`rglob` script search under `scripts/` outside the resolver. | Retro `layout-oracle-duplication`; the next path change would otherwise sweep with a regex again. | 1 |
| 3 release-lane-standing-evidence | Put `run-quality.sh --release` into the documented pre-push clean-clone procedure (cadence per Interview Decisions), state it in `docs/development.md`, prove the hook refuses a seeded release-only failure. | #768's three regressions hid four days; the gate exists, only the cadence is missing. | 1 |
| 4a wall-clock-census-and-764 | Record the census of every wall-clock-dependent test in `tests/` with its count (rough read today: `time.sleep` in 21 files, `time.monotonic` in 10, `timeout=` 77 sites; the claim set is smaller and the census names it); land the form check that refuses a new wall-clock claim; rewrite or delete the union of tests that failed in the six #764 runs; reproduce the sampler baseline in the CI shape before and after; push. No waiting on the schedule. |
| 4b wall-clock-rewrite-remainder | Rewrite or delete every remaining census entry (controlled clock, controlled child, or an observation the test itself forces); done means the census list is empty, not a batch count. | Six failed runs; the only open issue; the tree changed under it with #768/#770. | 2, 3 |
| 5 lesson-promotion-and-budget | Add the missing promotion path: a `graduate` action with a new `graduated` state, a three-site change (`LIFECYCLE_TRANSITIONS` and `_replay_lifecycle` in `lesson_ledger_lib.py`, `_materialize` and the argparse choices in `record_lesson_lifecycle.py`, the literal in `tests/test_lesson_lifecycle_refusals.py`), requiring a decision ref to the docs commit where the lesson was compressed into its owning standing page (D38 reopened; the score outcome `changed-an-action` already maps to `graduate` with no mechanism). Then, in one slice, a joint review with the operator: for each of the 15 score-0 candidates the agent drafts a disposition (helped, contradicted, did not help, never consulted, in the same vocabulary as the ledger's score outcomes) with the evidence behind it, and for a graduate candidate the exact `docs/` edit (what is added, what the page loses); the operator and agent settle each lesson in conversation, and the settled reason is recorded per lesson before any event or docs commit; seed `wrong-path-is-premise-failure`, `probe-stimulus-from-model-not-source`, `parallel-coverage-runtime-collision` as active lessons; ledger check and `check-docs.sh` green. Neither half alone closes the slice. | The three classes recurred this session and the next session cannot read them. | none |
| 6 integrated-closeout | Standing and release lanes green in a clean clone; the most recent scheduled mutation run read from GitHub; #764 closed through the recovery observer if that run is green, otherwise the run's failing set recorded as the next work; parent closed through the guarded close. | Proves the composition once. | 1–5 including 4a and 4b |

## Discuss Before Activation

- Discuss before activation: none — all ten interview decisions were resolved with the operator on 2026-09-03; the sibling interview record reads `interview-complete`.

## Context Sources

- `charness-artifacts/retro/2026-09-03-session-retro.md` — the resolver item, `verification-shape-mismatch` recurrence, sweep overreach.
- `charness-artifacts/retro/2026-09-02-session-retro.md` — first `verification-shape-mismatch` instance.
- `charness-artifacts/metrics/rca-ledger.jsonl` — two entries with `class_key: verification-shape-mismatch` (2026-09-02, 2026-09-03).
- `charness-artifacts/goal-runs/765/2026-09-02-session-record.md` — the #765 handoff; step 4 of the third session's list names the resolver as a follow-up.
- GitHub #764 and its comments; `mutation-tests.yml` runs 33346505915 to 33631065064; `.github/workflows/mutation-tests.yml` lines 75 to 100 (mirror and PATH preconditions) and 460 to 472 (recovery-candidate rule).
- `scripts/gates_support/run_standing_pytest.py` marker selection; `pyproject.toml` `release_only` marker; `.charness/quality/runtime-signals.json`.
- `scripts/core/repo_layout.py`; the four lookup sites named in Starting Truth.
- `charness-artifacts/retro/lesson-ledger.json` (`active_lesson_budget: 50`); `charness-artifacts/retro/lesson-selection-index.json` for the three absent classes.
- `scripts/gates/check_docs_graph.py` `_run_awiki`; `scripts/core/subprocess_guard.py::run_monitored_phase`; `.agents/quality-gates.yaml` `docs-graph` (`lane: label-only`).
- Lesson ledger seed `goal-verification-shape`: `green-test-is-not-covered-line`, `layout-oracle-duplication`, `goal-closeout-evidence-binding`, `verification-shape-mismatch`, `lane-brief-omits-parent-owned-surfaces`.

## Interview Decisions

- 2026-09-03, operator: items 1 to 5 of the #765 handoff form one goal under the "verification-shape mismatch" class; item 6 (the new goal itself) is this record.
- 2026-09-03, operator: the release lane runs in the pre-push clean-clone lane on every push. Alternatives: session start only (rejected: a regression made mid-session hides until the next session); a hosted `quality-core.yml` release job (rejected as the first observer: it reads after the push, past the boundary; it may still be added later as a second observer). Reason: the clean-clone push lane is the last local read before an irreversible boundary and already exists.
- 2026-09-03, operator: nondeterministic timing-sensitive tests should not exist at all. This sharpens the agent's recommendation (fix the tests) into a boundary: slice 4 rewrites each failing test to a deterministic claim or deletes it, and never deselects it from the sampler baseline. Alternatives rejected: dispatch-only observation (cannot report recovery per #358); deselecting the tests (skipped-is-not-passed).
- 2026-09-03, operator: the ledger slice presents candidates for the operator to pick, and it must do both exclusion and promotion in the same slice. Alternative rejected: archive by an age rule now (the operator signs each lifecycle event); dropping the item (the three classes recurred this session).
- 2026-09-03, operator: wall-clock-dependent tests existing at all is the smell; the slice censuses all of `tests/`, not only the #764 failing set, and adds a form check. Alternative rejected: fix only the failing union (leaves the class in place).
- 2026-09-03, operator: graduation is not decided by the operator reading a commit nor by automation; the agent drafts a per-lesson disposition (helped, contradicted, did not help, like the ledger's score outcomes) and the docs edit, and the two settle each lesson together in conversation. Slice 5 is written as that joint review.
- 2026-09-03, operator: promotion means compressing a proven lesson into the owning standing `docs/` page, removing from that page what it no longer needs. The agent's finding: no such mechanism exists; `SCORE_OUTCOMES` maps `changed-an-action` to `graduate` with nothing behind it and `docs/deferred-decisions.md` D38 deferred the promotion gate. This session's third recurrence is D38's reopen trigger, so slice 5 builds the `graduate` action. Alternative rejected: seed-only promotion (leaves the ledger as the only memory).
- 2026-09-03, operator: slice 4 does not wait on the 12-hour schedule; the next cycle is read when it has happened. Alternative rejected: changing the #358 rule so a push-triggered run reports recovery (changes a proof-surface rule for a convenience).
- 2026-09-03, operator: resolver only, no rename-sweep tool. The operator first asked what the question meant; after the explanation (the #770 sweep was an ad hoc regex that rewrote five non-repo strings because it had no resolver to ask) the operator approved the recommendation. Rejected: a repo-owned sweep tool that consumes the resolver (no planned migration would use it).
- 2026-09-03, operator: one observer, the pre-push clean-clone lane; no hosted `release_only` job. The operator first asked what the question meant; after the explanation (a `quality-core.yml` job reads after the push, survives hook bypass, but inherits the mirror/PATH/env preconditions that broke the mutation baseline) the operator approved the recommendation. Rejected: local and hosted (decide after slice 4 makes the CI baseline green).
- 2026-09-03, operator: the awiki fix is local to `check_docs_graph.py`; the Goal Run parent is a new issue.
- 2026-09-03, operator: the achieve skill gap (SKILL.md silent on `interview_contract.py` and the pre-approval sequence) is fixed immediately, outside this goal; landed as the commit that precedes this draft.

## Plan Critique Findings

- Risk: the #764 failures are CI-runner timing, not a code defect, and a local reproduction never fails. Mitigation: the census does not depend on reproduction; a wall-clock claim is rewritten because it exists, and the CI-shape reproduction is the before-and-after evidence, not the trigger.
- Risk: the census is large and the slice stalls (fresh-eye count: `time.sleep` 49 sites in 21 files, `time.monotonic` 34 in 10, `timeout=` 77, `attempt` in 54 files). Mitigation: split into 4a (census recorded, form check landed, the #764 union rewritten, CI-shape baseline) and 4b (the remainder, done when the census list is empty); the form check stops the class growing while 4b runs.
- Fresh-eye finding, accepted: the five items are coupled by the RCA class, not by code; four of five dependency edges are order-only. Disposition: the operator chose the bundling on 2026-09-03 with the RCA ledger as the reason; the order-only edges are labelled as such in the child bodies so a stalled slice does not block an independent one.
- Fresh-eye finding, accepted: `present_gate` is not a layout search; removed from the duplicate list, kept as a resolver consumer.
- Fresh-eye finding, accepted: the acceptance grep missed the `rglob` lookups and named a retired script (`check_export_safe_imports.py`, migrated to the native `export-safe` gate in `f4ecbe438`); acceptance now names the form check and the live gate labels.
- Fresh-eye finding, accepted: the native export-safe gate forbids only `skills.public` imports, so the real question for the exported quality skill is whether `scripts/core` ships in the same install unit. It does (the #769 boundary: everything under `scripts/` ships); the resolver lives there.
- Fresh-eye finding, accepted: `graduate` is a three-site change with a state decision; recorded in slice 5 and its body.
- Fresh-eye finding, accepted: the awiki boundary was unenforced; the body now names the mechanism and fails on a `subprocess_guard.py` diff.
- Risk: a `graduate` action without a contract for what the docs compression must contain reproduces D38's deferral reason. Mitigation: the action requires a decision ref to a commit touching a `docs/` page, `check-docs.sh` must be green at that commit, and the content of the compression is settled per lesson in the joint review, not by a classifier and not by commit inspection after the fact.
- Risk: the resolver becomes a fifth lookup because a caller keeps its own fallback. Mitigation: the four functions are deleted, not wrapped, and the form check refuses the glob pattern outside the resolver.
- Risk: adding `--release` to the pre-push lane doubles push latency and the operator starts skipping the hook. Mitigation: the cadence decision is recorded before activation; runtime is measured in the slice and written to `docs/development.md`.
- Risk: archiving a score-0 lesson removes one that was read but never cited (lesson `positive-effect-cannot-be-cited`). Mitigation: the candidate table shows `outcome_counts`, and the operator picks; the slice does not archive by rule.
- Risk: silencing the awiki FAIL line hides a real awiki crash. Mitigation: only exit 1 (lint findings) is downgraded; timeout and unknown exit codes keep their NOT-RUN and UNESTABLISHED paths, and a test seeds each.

## Briefing

- **Purpose.** Every verification channel this repo reads reports the same truth in the same shape. The RCA ledger recorded `verification-shape-mismatch` twice in two days; the five handoff items are instances: a hosted baseline that never runs on the tree it judges, a release lane nobody runs before pushing, four private answers to one layout question, a memory that cannot admit what recurred, and a FAIL line nobody consumes.
- **Target structure.** One script resolver in `scripts/core`; one push procedure that runs both lanes from a clean clone; a test suite with no wall-clock claims and a form check that keeps it so; a ledger with a promotion path into `docs/` beside its archive path; a docs-graph gate whose console output matches its verdict.
- **Execution order.** awiki echo, resolver, release cadence, wall-clock census with the #764 baseline, wall-clock remainder, ledger promotion and budget, integrated closeout. Smallest first so lane output is trustworthy before larger reads depend on it; the resolver before any lane relies on script paths; the census after the release lane exists so its clean-clone proof is available; the ledger anytime; closeout last.
- **Proof.** Low cost: standing runner and ledger check after each slice. High confidence: CI-shape baseline before and after; full read-only and release lanes in a clean clone before each push; seeded refusals for the form check, the hook, and the awiki paths. Live: the most recent scheduled mutation run read from GitHub; `/goal #N` pickup; guarded parent close after readback.
- **Child bodies.** `charness-artifacts/goal-runs/pending-verification-shape-alignment/bodies/` (seven, one per slice, moved under the parent number after establishment).
- **Fresh-eye critique.** One distinct-observer pass (sonnet, read-only) on 2026-09-03 returned ten findings; seven changed the draft, recorded under Plan Critique Findings.
- **Interview.** `charness-artifacts/goals/2026-09-03-verification-shape-alignment.interview.json`, ten questions, validated by `interview_contract.py`.
