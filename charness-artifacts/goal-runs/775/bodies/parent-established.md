## Situation

The repository reads its own health through several channels that do not report the same truth in the same shape. The RCA ledger recorded the class `verification-shape-mismatch` on 2026-09-02 (39 package-form guard imports invisible under pytest) and again on 2026-09-03 (a bare pytest green from an older tree trusted over the standing runner's 31 failures). The five items left open by the #765 handoff are instances of the same class.

## Experience

A maintainer pushes after a green standing lane and a release-only regression stays hidden for four days, because nothing runs the release lane before the push. The hosted mutation workflow fails six scheduled runs in a row before any mutant runs, on a tree that no longer exists, while the issue it files reads as a mutation regression. Three functions written in one session each answer "where does this script live now" on their own. A session that hit three lesson classes again cannot admit them to the ledger because the budget is full and nothing promotes a proven lesson out. Every lane prints `FAIL [docs-graph-awiki]` that no aggregate reads.

## Evidence

| Surface | Read 2026-09-03 |
| --- | --- |
| #764 | Six scheduled `mutation-tests.yml` runs since 2026-08-31 fail at `Select mutation sample`; the failing baseline set differs per run (2, 38, 5 tests); the latest five are attempt-count claims under a real drain; the last run predates the #770 packaging |
| release lane | `release_only` and `slow_corpus` deselected by `run_standing_pytest.py`; the pre-push hook runs the standing lane only; #768 hid three release-only regressions for four days; the lane takes about 298 s |
| layout lookups | `scaffold_artifact_lib._repo_script`, `seeding_support._packaged_script`/`_seed_path`, `public_spec_adapter_policy.load_repo_script_module` each search flat-or-packaged independently; `scripts/core/repo_layout.py` has no script resolver |
| lesson ledger | 49 active of 50; 15 active lessons with score 0 and no scoring events; three classes recurred in the #770 session and are absent; `SCORE_OUTCOMES` maps `changed-an-action` to `graduate` with no mechanism; `docs/deferred-decisions.md` D38 deferred the promotion gate and its reopen trigger (third recurrence) has fired |
| docs-graph-awiki | `check_docs_graph.py` judges by named metrics, but `run_monitored_phase` prints `FAIL` on awiki lint exit 1; the gate is `lane: label-only` |

Planning record: `charness-artifacts/goals/2026-09-03-verification-shape-alignment.md`.

## Impact

Each mismatch is a path by which a wrong green or a false red reaches a decision. The cost already paid: one hour re-deriving failures a standing run would have listed, four days of hidden release regressions, five sweep repairs found one gate at a time, and a session that could not read the lessons it had already learned.

## Desired outcome

- The hosted mutation sampler's coverage baseline runs green on the current tree; no test in `tests/` claims a wall-clock outcome and a form check refuses the next one.
- The pre-push clean-clone lane runs `run-quality.sh --release` on every push, and `docs/development.md` says so.
- One resolver beside `scripts/core/repo_layout.py` answers script locations; the three private lookups are gone.
- The lesson ledger can graduate a proven lesson into its owning `docs/` page; the three recurred classes are active within the 50 budget, each disposition settled jointly with the operator.
- The docs-graph gate's console output matches its verdict.

Success is a wrong answer's escape path closed, never a count.

## Ownership contract

- Goal Draft owns approved intent, boundaries, and slice design. Goal Binding owns the frozen identity. This parent owns the current-child cursor. Work Item issues own routine implementation state and behavioural proof.
- Verify in the shape production uses; a skipped gate is not a passed gate; a wall-clock-dependent test is rewritten or deleted, never retried, widened, or deselected.
- The awiki fix is local to `check_docs_graph.py`; a diff touching `subprocess_guard.py` fails that child.
- Lesson graduation and archive are settled lesson by lesson between the agent and the operator; no rule, classifier, or after-the-fact commit inspection decides one.
- #764 closes only through its recovery-observer path; the parent closes only through the guarded Goal Run close after exact readback.

## Work sequence

1. awiki-phase-echo
2. layout-resolver
3. release-lane-standing-evidence
4. wall-clock-census-and-764
5. wall-clock-rewrite-remainder
6. lesson-promotion-and-budget
7. integrated-closeout

## Completion criteria

- Every child provider-closed with behavioural evidence.
- Standing, full read-only, and release lanes green in a clean clone with the skip list read.
- The most recent scheduled mutation run read from GitHub and #764's state consistent with it.
- Parent closed only through the guarded Goal Run close path after exact readback.

## Non-claims

- No sampler redesign, no change to the #358 recovery rule, no hosted `release_only` job, no rename-sweep tool, no file moves, no budget increase, no AGENTS.md or CLAUDE.md edit.
- Push, tag, release publish, and installed-host mutation remain separately authorised.

AI provenance: drafted and filed by an AI agent from the operator-approved Goal Draft (sha256 6f2f63ecd8264a45…) and the operator's approval of 2026-09-03; activation is deferred to the next session by the operator.

<!-- charness-goal-run:v1
{
  "amendments": [],
  "binding_path": "charness-artifacts/goals/2026-09-03-verification-shape-alignment.binding.json",
  "binding_schema": "charness.goal-binding/v1",
  "binding_sha256": "ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0",
  "bootstrap_verification": "verified-target-roundtrip",
  "draft_path": "charness-artifacts/goals/2026-09-03-verification-shape-alignment.md",
  "draft_sha256": "6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898",
  "initial_graph_sha256": "6f5b883dd9bc8cb8f0a6721be9f672a6fef06f13f66f1a01124b56b062de4b48",
  "parent_identity": {
    "number": 775,
    "repo": "corca-ai/charness",
    "url": "https://github.com/corca-ai/charness/issues/775"
  },
  "progress": {
    "completed": 0,
    "next": {
      "key": "awiki-phase-echo",
      "number": 776,
      "repo": "corca-ai/charness",
      "state": "OPEN",
      "url": "https://github.com/corca-ai/charness/issues/776"
    },
    "open": 7,
    "revision": 1,
    "schema": "charness.goal-progress/v1",
    "total": 7
  }
}
-->
