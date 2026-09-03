# Goal Run #775 Final Proof

Date: 2026-09-03
Provider: `corca-ai/charness`
Frozen draft SHA-256: `6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898`
Binding SHA-256: `ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0`
Draft: `charness-artifacts/goals/2026-09-03-verification-shape-alignment.md`

## Outcome and boundary

The Goal Run removed the verification-shape mismatches the #765 handoff left
open, in seven Work Items, all operator-approved at activation and none
amended: 776 awiki-phase-echo, 777 layout-resolver, 778
release-lane-standing-evidence, 779 wall-clock-census-and-764, 780
wall-clock-rewrite-remainder, 781 lesson-promotion-and-budget, 782
integrated-closeout. All seven are provider `CLOSED`, each through a
`Closes #N` commit on `origin/main` whose body is the closeout carrier, each
with `verify-closeout` = `verified`, and each carrying an issue-owned closeout
comment whose URL is the evidence identity in `final-close-proof.json`.

Desired-outcome readback against the Goal Draft:

- The hosted sampler's coverage baseline: #779 fixed the five failures read
  from run 33631065064; the next scheduled run (33701977188, after #779)
  failed on one further test whose clock dependency carried no `time.*` call;
  #782 rewrote it. No test in `tests/` now calls `time.sleep`, `time.monotonic`,
  or `time.perf_counter` (record empty, gate at zero over 634 files). The
  hosted read of the tree after #782 belongs to the next scheduled run; #764
  stays open until that observer reads it (see below).
- The pre-push clean-clone lane runs the release lane on every code push
  (#778) and `docs/development.md` says so; it refused three #781 pushes and
  one #780 push in this run, each for a real defect.
- One resolver beside `scripts/core/repo_layout.py` answers script locations
  and a form check refuses another (#777).
- The ledger graduates a proven lesson into its owning `docs/` page (#781):
  ten graduated, four archived, the three recurred classes active, 47 of 50
  active, no budget change; the contract is
  `skills/shared/references/lesson-graduation.md`.
- The docs-graph gate's console output matches its verdict (#776).

Not claimed: a mutation score (the seed rotates per run), #764's closure,
release publication, tag, or installed-host mutation.

## Child closeouts

| child | key | carrier commit | issue-owned comment |
| --- | --- | --- | --- |
| #776 | awiki-phase-echo | `657386b63` | https://github.com/corca-ai/charness/issues/776#issuecomment-5521078361 |
| #777 | layout-resolver | `9e915f281` | https://github.com/corca-ai/charness/issues/777#issuecomment-5521078522 |
| #778 | release-lane-standing-evidence | `0c9f79ab1` | https://github.com/corca-ai/charness/issues/778#issuecomment-5521078704 |
| #779 | wall-clock-census-and-764 | `8d01bae96` | https://github.com/corca-ai/charness/issues/779#issuecomment-5521078915 |
| #780 | wall-clock-rewrite-remainder | `b16999a1f` | https://github.com/corca-ai/charness/issues/780#issuecomment-5521079139 |
| #781 | lesson-promotion-and-budget | `a6b48cb6a` | https://github.com/corca-ai/charness/issues/781#issuecomment-5521079362 |
| #782 | integrated-closeout | `bdddbe93a` | https://github.com/corca-ai/charness/issues/782#issuecomment-5521429134 |

## Whole-system evidence

- Clean-clone lanes: `782-clean-clone-lanes.md` (standing 8750 passed; full
  read-only 82 passed, 5 not run; release 87 passed, 4 not run; the not-run
  list is the skip list, read from the summary line).
- Hosted mutation: the most recent scheduled run on a tree at or after #779 is
  https://github.com/corca-ai/charness/actions/runs/33701977188 on `1e9cb9991`,
  conclusion failure, `Select mutation sample` did not reach `success`: the
  coverage baseline failed on
  `tests/quality_gates/test_cli_skill_surface.py::test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out`
  (1 failed, 8653 passed). That test is rewritten in #782 (`bdddbe93a`). #764
  is therefore NOT closed by this run; the failing set is recorded on #764 as
  the next work, and the recovery-observer path decides after the next
  scheduled run reads the pushed tree.
- Pickup: `/goal #775` returned `ok: true`, `status: selected`, with the
  bounded ledger preview showing `wrong-path-is-premise-failure`,
  `probe-stimulus-from-model-not-source`, and
  `parallel-coverage-runtime-collision` active.
- Lesson review: `781-lesson-dispositions.md` (fifteen settled reasons) and
  `charness-artifacts/retro/2026-09-03-goal-775-closeout-retro.md`.
- Session record: `2026-09-03-session-record.md` (five sessions, each push
  refusal and its repair named).
