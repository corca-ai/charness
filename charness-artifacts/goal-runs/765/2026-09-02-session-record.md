# Goal Run #765 session record, 2026-09-02

Dated evidence for the first execution session. The provider parent and its
cursor remain the resume state (`/goal #765`); this record exists because the
child closes below are carried in UNPUSHED commits, so the cursor still names
#771 until the operator pushes and the closes land. Run pickup from THIS
checkout's copy (`python3 skills/public/achieve/scripts/goal_run_pickup.py`),
not the installed one under `~/.agents`, which predates #773.

## Integrated locally (closeout carrier in the commit body, `verify-closeout` = carrier_verified)

| Child | Commit subject | Proof that mattered |
| --- | --- | --- |
| #771 rework-instrument | issue/retro: observe consumer rework through the rework label and Causing skill line | packet `charness-artifacts/retro/2026-09-02-771-rework-instrument-packet.md` renders achieve 1, issue 1; `rework` label created and applied to #773 |
| #773 goal-run-binding-simplification | achieve/issue: finish identity-not-content binding for Goal Runs | live `list-children` without identity fields read 8 children; a foreign `binding_sha256` refused by identity (`operations/list-children-773-identity-*.out.yaml`) |
| #766 docs-as-code | docs: retire completed records, verify every page, and make README the user guide | `check-docs.sh` PASS with the new `check-last-verified` component; seeded page turned it red |
| #767 gate-scope-repair | quality: make gate universes recursive, cover shell, and detect unreferenced scripts | `charness-artifacts/quality/2026-09-02-gate-universe-diff.md`; `check_unreferenced_scripts.py --strict` verdict ok; length gate green after splitting two #773 modules |

Each of those four trees passed the full standing pytest (last green: 8554).

## #768 subprocess-retroactive-removal: production done, tests mid-repair

Integrated commits (six lane candidates plus parent fixes, all after #767):

- production: every `subprocess.*` call in `scripts/` and `skills/` now goes
  through `scripts/subprocess_guard.py`; `scripts/check_subprocess_form.py`
  refuses a direct spawn and is green on the live tree (757 files); eval
  runners keep their spawns on `sys.executable`; the guard decodes child
  output with `surrogateescape`.
- tests: lanes T1, T2, T3 migrated most of the 150 spawning test files
  in-process. Three of the six lane commits carry the wrapper's WIP subject
  (`task-run: WIP candidate`); their content was assessed and integrated
  (P2: zero direct spawns left, lint and compile clean; T2 and T3: collect
  parity held). Rewrite those subjects at the #768 closeout.

State of the integrated tree at session end: full standing pytest
`134 failed, 8420 passed`. The failures are the test seam, not production:
tests still patch `module.subprocess.run` on modules that now bind
`run_process`; fakes return bytes; a few assert `CalledProcessError`, which
the guard never raises. `check_subprocess_form.py` is NOT yet queued in
`run-quality.sh` because the runner fixture list (`tests/quality_gates/support.py`)
was inside a repair lane's scope.

## Next session, in order

1. Relaunch the three repair lanes from `briefs/brief-768-repair.md` with the
   batches `briefs/repair-batch-r{0,1,2}.txt` (replace `__SCOPE__` with the
   batch as a bulleted list). They were stopped at wrap-up with almost no
   edits; the worktrees `task-run/subprocess-768-r{0,1,2}` under the charness
   runtime cache may still exist and can be removed. Integrate candidate-first.
2. Launch `briefs/brief-768-ratchet.md` (retires the boundary-bypass ratchet,
   wires `check-subprocess-form` into the runner, fixture list, and
   timing-layers doc, and runs the issue's acceptance greps).
3. Full standing pytest green, then the #768 closeout carrier (feature
   classification; template in the four earlier closeout commits), rewriting
   the three WIP subjects into it or into a squash.
4. #769 quality-boundary-and-run-quality: the parent's design is
   `charness-artifacts/quality/2026-09-02-gate-classification-769.md`,
   reviewed twice by bounded reviewers; both reports were truncated by the
   host, so angles 2 to 4 beyond the recorded rows are unreviewed. The real
   finding: eight `ship` gates need adapter-declared inputs or they are a
   vacuous green in a consumer repo. Then #770, #772.
5. Operator pushes `main`; the `Closes #N` carriers close #771, #773, #766,
   #767; run `issue_tool.py verify-closeout ... --expect-state CLOSED` per
   child and sync the parent cursor through the goal-run operations.

## Lessons this session paid for

- The default `run-quality.sh` lane ran five gates and the full lane ran only
  pytest, so the length gate that flagged two #773 modules was not read until
  #767's lane ran it. Read the skip list before calling a tree green.
- A lane whose brief has five heavy items times out at 60 minutes with a WIP
  candidate; the WIP was salvageable every time. Prefer six small lanes to
  one big one, and launch them in parallel.
- `charness task run` refuses a scope glob that matches nothing; seed the
  directory first. It also refuses a dirty parent, so commit before the next
  launch and do not write files while a launch is sleeping.
- Bounded-reviewer reports are truncated by the host around 4k characters;
  ask for under 60 lines and run two passes with disjoint angles.
